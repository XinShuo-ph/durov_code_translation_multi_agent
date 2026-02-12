#!/usr/bin/env python3
"""Executable coordinator for parallel translation workers.

This tool makes the multi-agent protocol executable:
- discovers peers in the same experiment batch
- computes live claims and completed pages
- recommends next page using striping + balance guard
- updates local WORKER_STATE.json on claim/done/heartbeat
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


TOTAL_PAGES_DEFAULT = 99
ONLINE_TIMEOUT_DEFAULT = 600
CLAIM_TIMEOUT_DEFAULT = 900
BALANCE_SLACK_DEFAULT = 2

STATE_FILE_DEFAULT = Path("WORKER_STATE.json")
PAGE_FILE_RE = re.compile(r"^translations/(?:[^/]+/)*page_(\d{3})\.json$")
BRANCH_SUFFIX_RE = re.compile(r"^(?P<prefix>.+)-(?P<worker>[a-z0-9]{4})$")
MD_HEARTBEAT_RE = re.compile(r"\*\*Heartbeat\*\*:\s*([0-9]+)")
MD_STATUS_RE = re.compile(r"\*\*Status\*\*:\s*([^\n]+)")
MD_CLAIM_RE = re.compile(r"\*\*Claimed Page\*\*:\s*([^\n]+)")
MD_WORKER_RE = re.compile(r"^#\s*Worker(?:\s+State)?\s*:\s*([^\n]+)", re.MULTILINE)
ROW_PAGE_RE = re.compile(r"^\|\s*([0-9]{1,3})\s*\|")


def run_git(args: List[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args], check=False, capture_output=True, text=True
    )
    if check and proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or "git command failed"
        raise RuntimeError(f"git {' '.join(args)}: {msg}")
    return proc


def current_branch() -> str:
    branch = run_git(["branch", "--show-current"]).stdout.strip()
    if not branch:
        raise RuntimeError("Unable to detect current branch.")
    return branch


def infer_batch_prefix(branch: str) -> str:
    match = BRANCH_SUFFIX_RE.match(branch)
    return match.group("prefix") if match else branch


def infer_worker_id(branch: str) -> str:
    match = BRANCH_SUFFIX_RE.match(branch)
    if match:
        return match.group("worker")
    tail = branch.rsplit("-", 1)[-1]
    return tail[-4:].lower()


def parse_int(value: object) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"", "none", "-", "null"}:
            return None
        if v.isdigit():
            return int(v)
    return None


def normalize_pages(values: object) -> Set[int]:
    out: Set[int] = set()
    if not isinstance(values, list):
        return out
    for value in values:
        parsed = parse_int(value)
        if parsed is not None and parsed > 0:
            out.add(parsed)
    return out


@dataclass
class WorkerState:
    branch: str
    worker_id: str
    heartbeat: int = 0
    status: str = "unknown"
    claimed_page: Optional[int] = None
    claimed_at: Optional[int] = None
    completed_pages: Set[int] = field(default_factory=set)
    source: str = "unknown"

    def is_online(self, now: int, timeout: int) -> bool:
        return self.heartbeat > 0 and (now - self.heartbeat) <= timeout

    def claim_is_live(self, now: int, claim_timeout: int) -> bool:
        if self.claimed_page is None:
            return False
        base = self.claimed_at if self.claimed_at is not None else self.heartbeat
        return base > 0 and (now - base) <= claim_timeout


def remote_file(branch: str, path: str) -> Optional[str]:
    proc = run_git(["show", f"origin/{branch}:{path}"], check=False)
    if proc.returncode != 0:
        return None
    return proc.stdout


def parse_state_json(raw: str, branch: str) -> WorkerState:
    data = json.loads(raw)
    worker_id = str(data.get("worker_id") or infer_worker_id(branch)).lower()
    heartbeat = parse_int(data.get("heartbeat")) or 0
    claimed_page = parse_int(data.get("claimed_page"))
    claimed_at = parse_int(data.get("claimed_at"))
    completed_pages = normalize_pages(data.get("completed_pages"))
    status = str(data.get("status") or "unknown")
    return WorkerState(
        branch=branch,
        worker_id=worker_id,
        heartbeat=heartbeat,
        status=status,
        claimed_page=claimed_page,
        claimed_at=claimed_at,
        completed_pages=completed_pages,
        source="WORKER_STATE.json",
    )


def parse_state_md(raw: str, branch: str) -> WorkerState:
    worker_match = MD_WORKER_RE.search(raw)
    worker_id = (
        worker_match.group(1).strip().split()[0].lower()
        if worker_match
        else infer_worker_id(branch)
    )
    heartbeat_match = MD_HEARTBEAT_RE.search(raw)
    heartbeat = int(heartbeat_match.group(1)) if heartbeat_match else 0
    status_match = MD_STATUS_RE.search(raw)
    status = status_match.group(1).strip() if status_match else "unknown"
    claim_match = MD_CLAIM_RE.search(raw)
    claimed_page = parse_int(claim_match.group(1).strip()) if claim_match else None

    completed_pages: Set[int] = set()
    for line in raw.splitlines():
        row = ROW_PAGE_RE.match(line)
        if not row:
            continue
        page = int(row.group(1))
        lowered = line.lower()
        if "done" in lowered or "completed" in lowered:
            completed_pages.add(page)

    return WorkerState(
        branch=branch,
        worker_id=worker_id,
        heartbeat=heartbeat,
        status=status,
        claimed_page=claimed_page,
        claimed_at=None,
        completed_pages=completed_pages,
        source="WORKER_STATE.md",
    )


def list_remote_batch_branches(prefix: str) -> List[str]:
    refs = run_git(
        ["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"]
    ).stdout.splitlines()
    out = []
    needle = f"{prefix}-"
    for ref in refs:
        if not ref.startswith("origin/"):
            continue
        branch = ref[len("origin/") :]
        if branch.startswith(needle):
            out.append(branch)
    return sorted(set(out))


def pages_from_remote_branch(branch: str) -> Set[int]:
    proc = run_git(
        ["ls-tree", "-r", "--name-only", f"origin/{branch}", "--", "translations"],
        check=False,
    )
    if proc.returncode != 0:
        return set()
    out: Set[int] = set()
    for line in proc.stdout.splitlines():
        match = PAGE_FILE_RE.match(line.strip())
        if match:
            out.add(int(match.group(1)))
    return out


def pages_from_local_worktree() -> Set[int]:
    root = Path("translations")
    if not root.exists():
        return set()
    out: Set[int] = set()
    for path in root.rglob("page_*.json"):
        rel = path.as_posix()
        match = PAGE_FILE_RE.match(rel)
        if match:
            out.add(int(match.group(1)))
    return out


def merge_states(base: WorkerState, override: WorkerState) -> WorkerState:
    merged = WorkerState(
        branch=base.branch,
        worker_id=override.worker_id or base.worker_id,
        heartbeat=max(base.heartbeat, override.heartbeat),
        status=base.status,
        claimed_page=base.claimed_page,
        claimed_at=base.claimed_at,
        completed_pages=set(base.completed_pages) | set(override.completed_pages),
        source=f"{base.source}+{override.source}",
    )
    base_ts = base.claimed_at or base.heartbeat
    over_ts = override.claimed_at or override.heartbeat
    if over_ts >= base_ts:
        merged.status = override.status
        merged.claimed_page = override.claimed_page
        merged.claimed_at = override.claimed_at
    return merged


def load_local_state(path: Path, branch: str) -> WorkerState:
    if path.exists():
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        state = parse_state_json(json.dumps(data), branch)
        state.source = str(path)
        return state
    md_path = Path("WORKER_STATE.md")
    if md_path.exists():
        raw = md_path.read_text(encoding="utf-8")
        state = parse_state_md(raw, branch)
        state.source = "WORKER_STATE.md(local)"
        return state
    return WorkerState(branch=branch, worker_id=infer_worker_id(branch), source="local-default")


def save_state_document(path: Path, doc: Dict[str, object]) -> None:
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass
class Snapshot:
    prefix: str
    workers: Dict[str, WorkerState]
    page_owners: Dict[int, Set[str]]
    now: int

    @property
    def completed_pages(self) -> Set[int]:
        return set(self.page_owners.keys())

    def live_claims(self, online_timeout: int, claim_timeout: int) -> Dict[int, str]:
        claims: Dict[int, str] = {}
        for state in self.workers.values():
            if not state.is_online(self.now, online_timeout):
                continue
            if not state.claim_is_live(self.now, claim_timeout):
                continue
            assert state.claimed_page is not None
            existing_worker = claims.get(state.claimed_page)
            if existing_worker is None:
                claims[state.claimed_page] = state.worker_id
                continue
            existing = next(
                (w for w in self.workers.values() if w.worker_id == existing_worker), None
            )
            existing_ts = (existing.claimed_at if existing else 0) or (existing.heartbeat if existing else 0)
            this_ts = state.claimed_at or state.heartbeat
            if this_ts > existing_ts:
                claims[state.claimed_page] = state.worker_id
        return claims

    def worker_completed_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for state in self.workers.values():
            counts[state.worker_id] = max(counts.get(state.worker_id, 0), len(state.completed_pages))
        return counts


def build_snapshot(prefix: str, fetch: bool, state_file: Path) -> Snapshot:
    if fetch:
        run_git(["fetch", "origin", "--prune"])

    workers: Dict[str, WorkerState] = {}
    page_owners: Dict[int, Set[str]] = {}

    for branch in list_remote_batch_branches(prefix):
        json_raw = remote_file(branch, "WORKER_STATE.json")
        md_raw = remote_file(branch, "WORKER_STATE.md") if json_raw is None else None
        completed = pages_from_remote_branch(branch)
        if json_raw is None and md_raw is None and not completed:
            continue

        if json_raw is not None:
            state = parse_state_json(json_raw, branch)
        elif md_raw is not None:
            state = parse_state_md(md_raw, branch)
        else:
            state = WorkerState(branch=branch, worker_id=infer_worker_id(branch), source="translations-only")

        state.completed_pages |= completed
        workers[branch] = state
        for page in completed:
            page_owners.setdefault(page, set()).add(state.worker_id)

    local_branch = current_branch()
    if infer_batch_prefix(local_branch) == prefix:
        local_state = load_local_state(state_file, local_branch)
        local_completed = pages_from_local_worktree()
        local_state.completed_pages |= local_completed
        if local_branch in workers:
            workers[local_branch] = merge_states(workers[local_branch], local_state)
        else:
            workers[local_branch] = local_state
        for page in local_completed:
            page_owners.setdefault(page, set()).add(local_state.worker_id)

    return Snapshot(prefix=prefix, workers=workers, page_owners=page_owners, now=int(time.time()))


def choose_next_page(
    snapshot: Snapshot,
    worker_id: str,
    max_page: int,
    online_timeout: int,
    claim_timeout: int,
    balance_slack: int,
) -> Dict[str, object]:
    completed = {p for p in snapshot.completed_pages if 1 <= p <= max_page}
    claims = snapshot.live_claims(online_timeout, claim_timeout)
    available = [p for p in range(1, max_page + 1) if p not in completed and p not in claims]

    online_workers = sorted(
        {
            state.worker_id
            for state in snapshot.workers.values()
            if state.is_online(snapshot.now, online_timeout)
        }
    )
    if worker_id not in online_workers:
        online_workers.append(worker_id)
        online_workers.sort()

    counts = snapshot.worker_completed_counts()
    for online in online_workers:
        counts.setdefault(online, 0)

    my_count = counts.get(worker_id, 0)
    min_count = min((counts[w] for w in online_workers), default=my_count)
    throttled = len(online_workers) > 1 and my_count > (min_count + balance_slack)

    recommended = None
    striped_count = 0
    if available:
        lane_size = len(online_workers)
        lane_index = online_workers.index(worker_id)
        striped = [p for p in available if ((p - 1) % lane_size) == lane_index]
        striped_count = len(striped)
        recommended = striped[0] if striped else available[0]

    return {
        "recommended": recommended,
        "available_count": len(available),
        "striped_candidates": striped_count,
        "throttled": throttled,
        "my_count": my_count,
        "min_count": min_count,
        "online_workers": online_workers,
        "claims": claims,
        "completed_count": len(completed),
    }


def cmd_status(args: argparse.Namespace) -> int:
    branch = current_branch()
    prefix = args.prefix or infer_batch_prefix(branch)
    snapshot = build_snapshot(prefix, fetch=args.fetch, state_file=Path(args.state_file))
    claims = snapshot.live_claims(args.online_timeout, args.claim_timeout)
    duplicates = {p: sorted(v) for p, v in snapshot.page_owners.items() if len(v) > 1}

    if args.json:
        payload = {
            "batch_prefix": prefix,
            "generated_at": snapshot.now,
            "worker_count": len(snapshot.workers),
            "online_workers": [
                {
                    "worker_id": state.worker_id,
                    "branch": state.branch,
                    "heartbeat": state.heartbeat,
                    "status": state.status,
                    "claimed_page": state.claimed_page,
                    "completed_pages": len(state.completed_pages),
                    "source": state.source,
                }
                for state in sorted(snapshot.workers.values(), key=lambda s: s.worker_id)
                if state.is_online(snapshot.now, args.online_timeout)
            ],
            "completed_pages": sorted(snapshot.completed_pages),
            "completed_count": len(snapshot.completed_pages),
            "live_claims": [{"page": p, "worker_id": wid} for p, wid in sorted(claims.items())],
            "duplicate_pages": [{"page": p, "workers": w} for p, w in sorted(duplicates.items())],
        }
        print(json.dumps(payload, indent=2))
        return 0

    online = [
        state for state in snapshot.workers.values() if state.is_online(snapshot.now, args.online_timeout)
    ]
    print(f"Batch prefix: {prefix}")
    print(
        f"Workers: total={len(snapshot.workers)} online={len(online)} "
        f"completed_pages={len(snapshot.completed_pages)}"
    )
    print("Online workers:")
    for state in sorted(online, key=lambda s: s.worker_id):
        age = snapshot.now - state.heartbeat
        claim = state.claimed_page if state.claimed_page is not None else "-"
        print(
            f"  - {state.worker_id}  done={len(state.completed_pages):>2}  "
            f"claim={claim}  hb_age={age:>4}s  status={state.status}"
        )

    if claims:
        print("Live claims:")
        for page, worker_id in sorted(claims.items()):
            print(f"  - page {page:03d} -> {worker_id}")
    else:
        print("Live claims: none")

    if duplicates:
        sample = ", ".join(f"{p:03d}" for p in sorted(duplicates)[:10])
        print(f"Duplicate pages: {len(duplicates)} (sample: {sample})")
    else:
        print("Duplicate pages: 0")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    branch = current_branch()
    prefix = args.prefix or infer_batch_prefix(branch)
    worker_id = (args.worker or infer_worker_id(branch)).lower()
    snapshot = build_snapshot(prefix, fetch=args.fetch, state_file=Path(args.state_file))
    pick = choose_next_page(
        snapshot=snapshot,
        worker_id=worker_id,
        max_page=args.max_page,
        online_timeout=args.online_timeout,
        claim_timeout=args.claim_timeout,
        balance_slack=args.balance_slack,
    )

    if pick["recommended"] is None:
        print("NONE")
        return 0

    if pick["throttled"] and not args.force:
        print(
            "THROTTLED: you are ahead of active workers. "
            "Use --force to override after review/assist work.",
            file=sys.stderr,
        )
        print(
            f"my_done={pick['my_count']} min_done={pick['min_count']} "
            f"recommended={pick['recommended']}",
            file=sys.stderr,
        )
        return 3

    if args.verbose:
        print(
            f"recommended={pick['recommended']} available={pick['available_count']} "
            f"striped_candidates={pick['striped_candidates']} online={len(pick['online_workers'])}"
        )
    else:
        print(pick["recommended"])
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    branch = current_branch()
    prefix = args.prefix or infer_batch_prefix(branch)
    snapshot = build_snapshot(prefix, fetch=args.fetch, state_file=Path(args.state_file))
    claims = snapshot.live_claims(args.online_timeout, args.claim_timeout)
    page = args.page

    owners = sorted(snapshot.page_owners.get(page, set()))
    claimant = claims.get(page)
    if owners:
        print(f"page {page:03d}: DONE by {', '.join(owners)}")
        return 0
    if claimant:
        print(f"page {page:03d}: CLAIMED by {claimant}")
        return 0
    print(f"page {page:03d}: AVAILABLE")
    return 0


def load_or_init_state_doc(path: Path, branch: str, worker_id: str, prefix: str) -> Dict[str, object]:
    if path.exists():
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError(f"{path} must contain a JSON object.")
    else:
        doc = {}
    base = {
        "schema_version": 1,
        "worker_id": worker_id,
        "branch": branch,
        "batch_prefix": prefix,
        "heartbeat": 0,
        "status": "idle",
        "claimed_page": None,
        "claimed_at": None,
        "completed_pages": [],
        "last_sync_at": 0,
        "notes": "",
    }
    base.update(doc)
    base["worker_id"] = worker_id
    base["branch"] = branch
    base["batch_prefix"] = prefix
    base["completed_pages"] = sorted(normalize_pages(base.get("completed_pages")))
    return base


def cmd_claim(args: argparse.Namespace) -> int:
    branch = current_branch()
    prefix = args.prefix or infer_batch_prefix(branch)
    worker_id = (args.worker or infer_worker_id(branch)).lower()
    state_path = Path(args.state_file)
    snapshot = build_snapshot(prefix, fetch=args.fetch, state_file=state_path)
    pick = choose_next_page(
        snapshot=snapshot,
        worker_id=worker_id,
        max_page=args.max_page,
        online_timeout=args.online_timeout,
        claim_timeout=args.claim_timeout,
        balance_slack=args.balance_slack,
    )
    page = args.page
    claims = pick["claims"]
    completed = snapshot.completed_pages

    if page in completed and not args.force:
        print(f"Cannot claim page {page:03d}: already completed.", file=sys.stderr)
        return 2
    claimant = claims.get(page)
    if claimant and claimant != worker_id and not args.force:
        print(f"Cannot claim page {page:03d}: currently claimed by {claimant}.", file=sys.stderr)
        return 2
    if pick["throttled"] and not args.force:
        print(
            "Cannot claim: balance guard active (you are ahead). "
            "Use --force to override.",
            file=sys.stderr,
        )
        return 3

    now = int(time.time())
    doc = load_or_init_state_doc(state_path, branch, worker_id, prefix)
    doc["heartbeat"] = now
    doc["last_sync_at"] = now
    doc["status"] = "translating"
    doc["claimed_page"] = page
    doc["claimed_at"] = now
    save_state_document(state_path, doc)

    print(f"Claimed page {page:03d} in {state_path}")
    print("Next: git add WORKER_STATE.json && git commit && git push")
    return 0


def extract_page_from_path(path: Path) -> Optional[int]:
    match = PAGE_FILE_RE.match(path.as_posix())
    if match:
        return int(match.group(1))
    fallback = re.search(r"page_(\d{3})\.json$", path.as_posix())
    if fallback:
        return int(fallback.group(1))
    return None


def cmd_done(args: argparse.Namespace) -> int:
    branch = current_branch()
    prefix = args.prefix or infer_batch_prefix(branch)
    worker_id = (args.worker or infer_worker_id(branch)).lower()
    state_path = Path(args.state_file)
    translation_file = Path(args.file)
    if not translation_file.exists():
        print(f"Missing translation file: {translation_file}", file=sys.stderr)
        return 2

    raw = translation_file.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    page_from_file = extract_page_from_path(translation_file)
    page = args.page if args.page is not None else page_from_file
    if page is None:
        print(
            "Could not infer page from filename; pass --page explicitly.",
            file=sys.stderr,
        )
        return 2
    doc_page = parse_int(parsed.get("page")) if isinstance(parsed, dict) else None
    if doc_page is not None and doc_page != page:
        print(
            f"Page mismatch: filename says {page:03d}, JSON field says {doc_page:03d}.",
            file=sys.stderr,
        )
        return 2

    file_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
    now = int(time.time())

    doc = load_or_init_state_doc(state_path, branch, worker_id, prefix)
    completed = sorted(normalize_pages(doc.get("completed_pages")) | {page})
    doc["completed_pages"] = completed
    doc["heartbeat"] = now
    doc["last_sync_at"] = now
    doc["status"] = "online"
    doc["claimed_page"] = None
    doc["claimed_at"] = None
    save_state_document(state_path, doc)

    print(f"Marked page {page:03d} done (hash={file_hash}) in {state_path}")
    print("Next: git add translations/page_XXX.json WORKER_STATE.json && git commit && git push")
    return 0


def cmd_heartbeat(args: argparse.Namespace) -> int:
    branch = current_branch()
    prefix = args.prefix or infer_batch_prefix(branch)
    worker_id = (args.worker or infer_worker_id(branch)).lower()
    state_path = Path(args.state_file)
    doc = load_or_init_state_doc(state_path, branch, worker_id, prefix)
    now = int(time.time())
    doc["heartbeat"] = now
    doc["last_sync_at"] = now
    if args.status:
        doc["status"] = args.status
    save_state_document(state_path, doc)
    print(f"Heartbeat updated in {state_path} ({now})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Coordinator utility for multi-agent parallel translation."
    )
    parser.add_argument("--prefix", help="Batch prefix override (defaults to current branch prefix).")
    parser.add_argument(
        "--state-file",
        default=str(STATE_FILE_DEFAULT),
        help="Local worker state JSON path (default: WORKER_STATE.json).",
    )
    parser.add_argument("--fetch", action="store_true", help="Run git fetch origin --prune before computing.")
    parser.add_argument("--json", action="store_true", help="JSON output (status only).")
    parser.add_argument(
        "--online-timeout",
        type=int,
        default=ONLINE_TIMEOUT_DEFAULT,
        help=f"Seconds before worker is offline (default: {ONLINE_TIMEOUT_DEFAULT}).",
    )
    parser.add_argument(
        "--claim-timeout",
        type=int,
        default=CLAIM_TIMEOUT_DEFAULT,
        help=f"Seconds before claim is stale (default: {CLAIM_TIMEOUT_DEFAULT}).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show online workers, live claims, and coverage.")
    p_status.set_defaults(func=cmd_status)

    p_next = sub.add_parser("next", help="Recommend next page for a worker.")
    p_next.add_argument("--worker", help="Worker short ID override.")
    p_next.add_argument("--max-page", type=int, default=TOTAL_PAGES_DEFAULT, help="Total pages.")
    p_next.add_argument(
        "--balance-slack",
        type=int,
        default=BALANCE_SLACK_DEFAULT,
        help=f"Allow this many pages ahead before throttle (default: {BALANCE_SLACK_DEFAULT}).",
    )
    p_next.add_argument("--force", action="store_true", help="Ignore balance throttle.")
    p_next.add_argument("--verbose", action="store_true", help="Verbose output.")
    p_next.set_defaults(func=cmd_next)

    p_check = sub.add_parser("check", help="Check whether a page is available, claimed, or done.")
    p_check.add_argument("--page", type=int, required=True, help="Page number to inspect.")
    p_check.set_defaults(func=cmd_check)

    p_claim = sub.add_parser("claim", help="Claim a page and update WORKER_STATE.json.")
    p_claim.add_argument("--worker", help="Worker short ID override.")
    p_claim.add_argument("--page", type=int, required=True, help="Page number to claim.")
    p_claim.add_argument("--max-page", type=int, default=TOTAL_PAGES_DEFAULT, help="Total pages.")
    p_claim.add_argument(
        "--balance-slack",
        type=int,
        default=BALANCE_SLACK_DEFAULT,
        help=f"Allow this many pages ahead before throttle (default: {BALANCE_SLACK_DEFAULT}).",
    )
    p_claim.add_argument("--force", action="store_true", help="Force claim despite guardrails.")
    p_claim.set_defaults(func=cmd_claim)

    p_done = sub.add_parser("done", help="Mark a page done after validating JSON.")
    p_done.add_argument("--worker", help="Worker short ID override.")
    p_done.add_argument("--file", required=True, help="Path to page JSON file.")
    p_done.add_argument("--page", type=int, help="Page number (optional; inferred from filename).")
    p_done.set_defaults(func=cmd_done)

    p_hb = sub.add_parser("heartbeat", help="Update heartbeat in local state.")
    p_hb.add_argument("--worker", help="Worker short ID override.")
    p_hb.add_argument("--status", help="Optional status update.")
    p_hb.set_defaults(func=cmd_heartbeat)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except json.JSONDecodeError as exc:
        print(f"JSON parse error: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
