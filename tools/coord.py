#!/usr/bin/env python3
"""
coord.py — Unified coordinator for multi-agent parallel work.

Synthesized from 16 protocol branch designs. Combines:
  - Deterministic stripe assignment (from branches 37be, e163, d038)
  - Batch-scoped peer discovery (from branches 28aa, a0cf, 943d)
  - Balance gate with HOLD (from branches 9d18, d249, fcb3)
  - Buddy review queue (from branches a0cf, 64eb)
  - Output-file-based completion detection (from branches 943d, d038, e163)

Commands:
  status         Show team status, coverage, and worker states
  next           Get next page to work on (or HOLD if balance gate active)
  check          Check availability of a specific page
  claim          Mark a page as claimed in local WORKER_STATE.json
  done           Validate translation + mark page complete in local state
  review-queue   Show pages available for review (buddy system)
  heartbeat      Update heartbeat in WORKER_STATE.json
  collect        Collect all translations from all peer branches

Usage:
  python3 tools/coord.py [--fetch] [--total-pages N] <command> [options]

All commands are stateless per invocation: each run scans git state fresh.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple


# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------

TOTAL_PAGES_DEFAULT = 99
ONLINE_TIMEOUT_S = 600        # 10 minutes
RECLAIM_TIMEOUT_S = 900       # 15 minutes
BALANCE_SLACK = 2             # max pages ahead of slowest before HOLD
MIN_WORKERS_FOR_BALANCE = 4   # balance gate only active with >=4 online

WORKER_STATE_FILE = "WORKER_STATE.json"
TRANSLATION_DIRS = ("translations",)
PAGE_JSON_RE = re.compile(r"(?:^|/)page_(\d{3})\.json$")


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

class GitError(RuntimeError):
    pass


def _git(args: Sequence[str], check: bool = True) -> str:
    try:
        p = subprocess.run(
            ["git", *args],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        raise GitError("git not found on PATH")
    if check and p.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def current_branch() -> str:
    return _git(["branch", "--show-current"]).strip()


def short_id_from_branch(branch: str) -> str:
    tail = branch.split("/")[-1]
    return tail.rsplit("-", 1)[-1] if "-" in tail else tail


def batch_prefix(branch: str) -> str:
    """Remove the final -XXXX worker suffix to get the batch prefix."""
    if "-" not in branch:
        return branch
    return branch.rsplit("-", 1)[0]


def fetch_origin() -> None:
    _git(["fetch", "origin", "--prune"])


def list_peer_branches(my_branch: str) -> List[str]:
    """Return remote branches sharing the same batch prefix."""
    prefix = batch_prefix(my_branch)
    want = f"origin/{prefix}-"
    out = _git(["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/"])
    branches = [ln.strip() for ln in out.splitlines() if ln.strip()]
    # Also check cursor/ prefix format
    if not any(b.startswith(want) for b in branches):
        want_alt = f"origin/cursor/{prefix.split('/')[-1]}-" if "/" in prefix else want
        return sorted(b for b in branches if b.startswith(want) or b.startswith(want_alt))
    return sorted(b for b in branches if b.startswith(want))


# ---------------------------------------------------------------------------
# Worker state
# ---------------------------------------------------------------------------

@dataclass
class WorkerInfo:
    branch: str
    worker_id: str
    heartbeat: int = 0
    status: str = "unknown"
    claimed_page: Optional[int] = None
    claimed_at: Optional[int] = None
    completed_pages: List[int] = field(default_factory=list)
    phase: str = "unknown"

    @property
    def is_online(self) -> bool:
        return self.heartbeat > 0 and (time.time() - self.heartbeat) < ONLINE_TIMEOUT_S

    @property
    def is_reclaimable(self) -> bool:
        return self.heartbeat > 0 and (time.time() - self.heartbeat) >= RECLAIM_TIMEOUT_S

    @property
    def done_count(self) -> int:
        return len(self.completed_pages)


def read_worker_state_json(remote_branch: str) -> Optional[WorkerInfo]:
    """Read WORKER_STATE.json from a remote branch."""
    try:
        raw = _git(["show", f"{remote_branch}:{WORKER_STATE_FILE}"], check=True)
    except GitError:
        return None
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return WorkerInfo(
        branch=remote_branch,
        worker_id=data.get("worker_id", short_id_from_branch(remote_branch.replace("origin/", ""))),
        heartbeat=int(data.get("heartbeat", 0)),
        status=data.get("status", "unknown"),
        claimed_page=data.get("claimed_page"),
        claimed_at=data.get("claimed_at"),
        completed_pages=list(data.get("completed_pages", [])),
        phase=data.get("phase", "unknown"),
    )


def read_worker_state_md(remote_branch: str) -> Optional[WorkerInfo]:
    """Fallback: read WORKER_STATE.md from a remote branch (regex-based)."""
    try:
        raw = _git(["show", f"{remote_branch}:WORKER_STATE.md"], check=True)
    except GitError:
        return None

    hb_m = re.search(r"\*\*Heartbeat\*\*:\s*([0-9]+)", raw)
    st_m = re.search(r"\*\*Status\*\*:\s*([^\n]+)", raw)
    cl_m = re.search(r"\*\*Claimed(?:\s+|-)Page\*\*:\s*([0-9]+|none|-)", raw, re.IGNORECASE)

    heartbeat = int(hb_m.group(1)) if hb_m else 0
    status = st_m.group(1).strip() if st_m else "unknown"
    claimed_raw = cl_m.group(1).strip() if cl_m else None
    claimed = int(claimed_raw) if claimed_raw and claimed_raw.isdigit() else None

    # Parse completed pages from table
    completed: List[int] = []
    for m in re.finditer(r"^\|\s*(\d{1,3})\s*\|", raw, re.MULTILINE):
        completed.append(int(m.group(1)))

    return WorkerInfo(
        branch=remote_branch,
        worker_id=short_id_from_branch(remote_branch.replace("origin/", "")),
        heartbeat=heartbeat,
        status=status,
        claimed_page=claimed,
        completed_pages=completed,
    )


def read_worker_state(remote_branch: str) -> Optional[WorkerInfo]:
    """Try JSON first, then fall back to Markdown."""
    w = read_worker_state_json(remote_branch)
    if w is not None:
        return w
    return read_worker_state_md(remote_branch)


# ---------------------------------------------------------------------------
# Output file scanning (source of truth)
# ---------------------------------------------------------------------------

def list_completed_pages_on_branch(remote_branch: str) -> Set[int]:
    """Scan for translation JSON files on a remote branch."""
    pages: Set[int] = set()
    for tdir in TRANSLATION_DIRS:
        try:
            out = _git(["ls-tree", "-r", "--name-only", remote_branch, "--", tdir])
        except GitError:
            continue
        for line in out.splitlines():
            line = line.strip()
            m = PAGE_JSON_RE.search(line)
            if m:
                pages.add(int(m.group(1)))
    return pages


# ---------------------------------------------------------------------------
# Global scan
# ---------------------------------------------------------------------------

@dataclass
class GlobalState:
    my_branch: str
    my_id: str
    batch_prefix: str
    peers: List[str]
    workers: List[WorkerInfo]
    online_workers: List[WorkerInfo]
    completed_pages: Set[int]           # union across all branches (from files)
    claimed_pages_online: Dict[int, str]  # page -> worker_id (online only)
    total_pages: int
    now: int

    @property
    def available_pages(self) -> List[int]:
        taken = self.completed_pages | set(self.claimed_pages_online.keys())
        return sorted(set(range(1, self.total_pages + 1)) - taken)


def scan(my_branch: str, total_pages: int, do_fetch: bool) -> GlobalState:
    if do_fetch:
        fetch_origin()

    peers = list_peer_branches(my_branch)
    now = int(time.time())

    workers: List[WorkerInfo] = []
    completed: Set[int] = set()
    claimed_online: Dict[int, str] = {}

    for b in peers:
        # Completion from output files (source of truth)
        completed |= list_completed_pages_on_branch(b)

        # Worker state for claims
        w = read_worker_state(b)
        if w is not None:
            workers.append(w)
            if w.is_online and w.claimed_page is not None and not w.is_reclaimable:
                claimed_online[w.claimed_page] = w.worker_id

    online = [w for w in workers if w.is_online]

    return GlobalState(
        my_branch=my_branch,
        my_id=short_id_from_branch(my_branch),
        batch_prefix=batch_prefix(my_branch),
        peers=peers,
        workers=sorted(workers, key=lambda w: (not w.is_online, w.worker_id)),
        online_workers=sorted(online, key=lambda w: w.worker_id),
        completed_pages=completed,
        claimed_pages_online=claimed_online,
        total_pages=total_pages,
        now=now,
    )


# ---------------------------------------------------------------------------
# Stripe computation
# ---------------------------------------------------------------------------

def compute_stripe(worker_id: str, peer_ids: List[str], total_pages: int) -> List[int]:
    """Compute deterministic interleaved page assignment."""
    sorted_ids = sorted(set(peer_ids))
    n = len(sorted_ids)
    if n == 0:
        return list(range(1, total_pages + 1))
    try:
        my_pos = sorted_ids.index(worker_id)
    except ValueError:
        # Fallback: hash-based position
        my_pos = int(worker_id, 16) % n if all(c in "0123456789abcdef" for c in worker_id.lower()) else 0
    pages = []
    p = my_pos + 1
    while p <= total_pages:
        pages.append(p)
        p += n
    return pages


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(gs: GlobalState) -> int:
    online = gs.online_workers
    offline = [w for w in gs.workers if not w.is_online]

    print(f"Batch prefix: {gs.batch_prefix}")
    print(f"Peers: {len(gs.peers)} branches")
    print(f"Workers: {len(online)} online, {len(offline)} offline")
    print(f"Completed pages: {len(gs.completed_pages)}/{gs.total_pages}")
    avail = gs.available_pages
    print(f"Available pages: {len(avail)}")
    claimed_count = len(gs.claimed_pages_online)
    print(f"Claimed (online): {claimed_count}")

    if online:
        print("\nOnline workers:")
        for w in online:
            age = gs.now - w.heartbeat
            cl = str(w.claimed_page) if w.claimed_page is not None else "-"
            print(f"  {w.worker_id:6s}  done={w.done_count:3d}  claimed={cl:4s}  "
                  f"hb={age}s ago  phase={w.phase}")
    if offline:
        print("\nOffline workers:")
        for w in offline:
            age = gs.now - w.heartbeat if w.heartbeat else "?"
            print(f"  {w.worker_id:6s}  done={w.done_count:3d}  hb={age}s ago")

    return 0


def cmd_next(gs: GlobalState, worker_id: str, force: bool) -> int:
    """Compute next page for this worker (or HOLD)."""
    me = None
    for w in gs.workers:
        if w.worker_id == worker_id:
            me = w
            break

    my_done = me.done_count if me else 0

    # Balance gate check
    online = gs.online_workers
    if not force and len(online) >= MIN_WORKERS_FOR_BALANCE:
        min_done = min(w.done_count for w in online) if online else 0
        if my_done > min_done + BALANCE_SLACK:
            print(f"HOLD=lead_cap (you={my_done}, slowest={min_done}, slack={BALANCE_SLACK})")
            print("  Allowed HOLD tasks: review a peer's page, update glossary, check stale claims")
            return 0

    available = gs.available_pages
    if not available:
        print("NONE")
        return 0

    # Striping preference: prefer pages where (page-1) % N == my_sorted_pos
    peer_ids = [w.worker_id for w in online] if online else [worker_id]
    sorted_ids = sorted(set(peer_ids))
    n = len(sorted_ids)
    try:
        my_pos = sorted_ids.index(worker_id)
    except ValueError:
        my_pos = 0

    # Prefer stripe pages, then any available
    preferred = [p for p in available if (p - 1) % n == my_pos]
    if preferred:
        print(preferred[0])
    else:
        print(available[0])
    return 0


def cmd_check(gs: GlobalState, page: int) -> int:
    if page in gs.completed_pages:
        print(f"page {page}: COMPLETED")
        return 1
    if page in gs.claimed_pages_online:
        owner = gs.claimed_pages_online[page]
        print(f"page {page}: CLAIMED by {owner}")
        return 1
    print(f"page {page}: AVAILABLE")
    return 0


def cmd_claim(gs: GlobalState, worker_id: str, page: int) -> int:
    """Update local WORKER_STATE.json with a claim."""
    state_path = WORKER_STATE_FILE
    now = int(time.time())

    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    data["worker_id"] = worker_id
    data["heartbeat"] = now
    data["status"] = "translating"
    data["claimed_page"] = page
    data["claimed_at"] = now

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Claimed page {page} in {state_path}")
    return 0


def cmd_done(gs: GlobalState, worker_id: str, filepath: str) -> int:
    """Validate translation file and mark page complete in local state."""
    # Validate file exists
    if not os.path.isfile(filepath):
        print(f"ERROR: file not found: {filepath}", file=sys.stderr)
        return 2

    # Validate JSON
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 2

    # Basic validation
    errors = _validate_translation(data, filepath)
    if errors:
        for err in errors:
            print(f"  VALIDATION ERROR: {err}", file=sys.stderr)
        return 2

    # Extract page number
    m = PAGE_JSON_RE.search(os.path.basename(filepath))
    page_num = int(m.group(1)) if m else data.get("page", 0)

    # Update local state
    state_path = WORKER_STATE_FILE
    now = int(time.time())

    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    completed = list(state.get("completed_pages", []))
    if page_num not in completed:
        completed.append(page_num)
    completed.sort()

    state["worker_id"] = worker_id
    state["heartbeat"] = now
    state["status"] = "idle"
    state["claimed_page"] = None
    state["claimed_at"] = None
    state["completed_pages"] = completed

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"OK: page {page_num} validated and marked complete ({len(completed)} total)")
    return 0


def _validate_translation(data: dict, filepath: str) -> List[str]:
    """Quick validation of translation JSON structure."""
    errors: List[str] = []

    if not isinstance(data, dict):
        return ["top-level JSON must be an object"]

    page = data.get("page")
    if not isinstance(page, int) or page < 1:
        errors.append("missing/invalid field: page (must be int >= 1)")

    sentences = data.get("sentences")
    if not isinstance(sentences, list) or len(sentences) == 0:
        errors.append("missing/invalid field: sentences (must be non-empty array)")
        return errors

    for i, s in enumerate(sentences, start=1):
        if not isinstance(s, dict):
            errors.append(f"sentences[{i}] must be an object")
            continue
        for lang in ("ru", "en", "zh", "ja"):
            val = s.get(lang)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"sentences[{i}].{lang} must be non-empty string")

    total = data.get("total_sentences")
    if total is not None and isinstance(total, int) and isinstance(sentences, list):
        if total != len(sentences):
            errors.append(f"total_sentences={total} != len(sentences)={len(sentences)}")

    return errors


def cmd_review_queue(gs: GlobalState, worker_id: str) -> int:
    """Show pages available for review (buddy system)."""
    online_ids = sorted(w.worker_id for w in gs.online_workers)
    if not online_ids:
        print("No online workers found.")
        return 0

    # Buddy: review pages from the worker whose sorted position precedes yours
    try:
        my_pos = online_ids.index(worker_id)
    except ValueError:
        my_pos = 0

    buddy_pos = (my_pos - 1) % len(online_ids)
    buddy_id = online_ids[buddy_pos]

    # Find buddy's completed pages that don't have a review
    buddy_worker = None
    for w in gs.workers:
        if w.worker_id == buddy_id:
            buddy_worker = w
            break

    if buddy_worker is None:
        print("No buddy worker found for review.")
        return 0

    # Get buddy's completed pages from file scanning
    buddy_pages = set()
    for b in gs.peers:
        if short_id_from_branch(b.replace("origin/", "")) == buddy_id:
            buddy_pages |= list_completed_pages_on_branch(b)

    if not buddy_pages:
        print(f"Buddy {buddy_id} has no completed pages yet.")
        return 0

    # Check which pages already have review files
    reviewed: Set[int] = set()
    for b in gs.peers:
        try:
            out = _git(["ls-tree", "-r", "--name-only", b, "--", "reviews/"], check=False)
            for line in out.splitlines():
                rm = re.search(r"page_(\d{3})", line)
                if rm:
                    reviewed.add(int(rm.group(1)))
        except GitError:
            pass

    reviewable = sorted(buddy_pages - reviewed)
    if not reviewable:
        # Fall back to any unreviewed completed pages
        all_completed = sorted(gs.completed_pages - reviewed)
        if all_completed:
            print(f"No buddy pages to review. Other unreviewed pages: {all_completed[:5]}")
        else:
            print("All completed pages have been reviewed.")
        return 0

    print(f"Review queue (buddy={buddy_id}):")
    for p in reviewable[:5]:
        print(f"  page {p}")
    return 0


def cmd_heartbeat(worker_id: str, status: str) -> int:
    """Update heartbeat in local WORKER_STATE.json."""
    state_path = WORKER_STATE_FILE
    now = int(time.time())

    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    data["worker_id"] = worker_id
    data["heartbeat"] = now
    if status:
        data["status"] = status

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Heartbeat updated: {now}")
    return 0


def cmd_collect(gs: GlobalState, out_dir: str) -> int:
    """Collect all translations from all peer branches."""
    os.makedirs(out_dir, exist_ok=True)
    collected = 0
    skipped = 0

    for b in gs.peers:
        pages = list_completed_pages_on_branch(b)
        for p in sorted(pages):
            fname = f"page_{p:03d}.json"
            out_path = os.path.join(out_dir, fname)
            if os.path.exists(out_path):
                skipped += 1
                continue
            # Try canonical path first, then alternatives
            for tdir in TRANSLATION_DIRS:
                src = f"{tdir}/{fname}"
                try:
                    content = _git(["show", f"{b}:{src}"], check=True)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    collected += 1
                    print(f"  Collected page {p} from {b}")
                    break
                except GitError:
                    continue

    total_files = len([f for f in os.listdir(out_dir) if f.endswith(".json")])
    print(f"\nCollected {collected} new, skipped {skipped} existing. "
          f"Total: {total_files}/{gs.total_pages} pages in {out_dir}/")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Unified coordinator for multi-agent parallel work.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--fetch", action="store_true",
                        help="Run git fetch origin --prune before scanning.")
    parser.add_argument("--total-pages", type=int, default=TOTAL_PAGES_DEFAULT)
    parser.add_argument("--branch", help="Override current branch detection.")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # status
    sub.add_parser("status", help="Show team status and coverage.")

    # next
    p_next = sub.add_parser("next", help="Get next page (or HOLD).")
    p_next.add_argument("--worker", required=True, help="Your worker short ID.")
    p_next.add_argument("--force", action="store_true",
                        help="Override balance gate.")

    # check
    p_check = sub.add_parser("check", help="Check page availability.")
    p_check.add_argument("--page", type=int, required=True)

    # claim
    p_claim = sub.add_parser("claim", help="Claim a page in local state.")
    p_claim.add_argument("--worker", required=True)
    p_claim.add_argument("--page", type=int, required=True)

    # done
    p_done = sub.add_parser("done", help="Validate and mark page done.")
    p_done.add_argument("--worker", required=True)
    p_done.add_argument("--file", required=True, help="Path to translation JSON.")

    # review-queue
    p_rq = sub.add_parser("review-queue", help="Show pages to review.")
    p_rq.add_argument("--worker", required=True)

    # heartbeat
    p_hb = sub.add_parser("heartbeat", help="Update heartbeat.")
    p_hb.add_argument("--worker", required=True)
    p_hb.add_argument("--status", default="", help="Optional status update.")

    # collect
    p_col = sub.add_parser("collect", help="Collect translations from all branches.")
    p_col.add_argument("--output", default="assembled/translations",
                        help="Output directory.")

    args = parser.parse_args(argv)

    my_branch = args.branch or current_branch()
    if not my_branch:
        print("ERROR: cannot determine current branch (use --branch).", file=sys.stderr)
        return 2

    gs = scan(my_branch, args.total_pages, do_fetch=args.fetch)

    if args.cmd == "status":
        return cmd_status(gs)
    elif args.cmd == "next":
        return cmd_next(gs, args.worker, args.force)
    elif args.cmd == "check":
        return cmd_check(gs, args.page)
    elif args.cmd == "claim":
        return cmd_claim(gs, args.worker, args.page)
    elif args.cmd == "done":
        return cmd_done(gs, args.worker, args.file)
    elif args.cmd == "review-queue":
        return cmd_review_queue(gs, args.worker)
    elif args.cmd == "heartbeat":
        return cmd_heartbeat(args.worker, args.status)
    elif args.cmd == "collect":
        return cmd_collect(gs, args.output)
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
