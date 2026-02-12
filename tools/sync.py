#!/usr/bin/env python3
"""
sync.py — lightweight, executable coordination for multi-agent translation.

Design goals:
- No long-lived daemon required (safe in ephemeral agent environments)
- Derive global state by scanning remote branches (git = message bus)
- Provide deterministic sharding for 16-agent parallelism + work stealing

Typical usage:
  python3 tools/sync.py refresh
  python3 tools/sync.py status
  python3 tools/sync.py next --mode shard
  python3 tools/sync.py next --mode steal
  python3 tools/sync.py review-queue
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


TOTAL_PAGES_DEFAULT = 99
DEFAULT_SLOTS = 16

CACHE_DIR = ".sync"
CACHE_PATH = os.path.join(CACHE_DIR, "cache.json")


PAGE_JSON_RE = re.compile(r"translations/(?:final/)?page_(\d{3})\.json$")
REVIEW_RE = re.compile(r"reviews/page_(\d{3})\.[^/]+\.md$")


def run(cmd: List[str], *, check: bool = True) -> str:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{res.stderr.strip()}")
    return res.stdout


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check)


def now_ts() -> int:
    return int(time.time())


def current_branch() -> str:
    return git("branch", "--show-current").strip()


def short_id_from_branch(branch: str) -> str:
    # Convention: last token after '-' (e.g., cursor/task-14ce -> 14ce)
    token = branch.split("-")[-1]
    return token[-4:]


def slot_from_short_id(short_id: str, slots: int) -> int:
    """
    Map a short id to a stable slot in [0, slots-1].
    If short_id is hex, interpret as hex; else hash.
    """
    s = short_id.strip()
    if re.fullmatch(r"[0-9a-fA-F]{4}", s):
        return int(s, 16) % slots
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16) % slots


def ensure_cache_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


@dataclass(frozen=True)
class WorkerInfo:
    branch: str  # origin/cursor/...
    short_id: str
    heartbeat: Optional[int]
    claimed_page: Optional[int]

    @property
    def online(self) -> bool:
        if self.heartbeat is None:
            return False
        return (now_ts() - self.heartbeat) < 600


def list_remote_cursor_branches() -> List[str]:
    out = git("branch", "-r")
    branches = []
    for line in out.splitlines():
        b = line.strip()
        if b.startswith("origin/cursor/"):
            branches.append(b)
    return sorted(branches)


def try_git_show(branch: str, path: str) -> Optional[str]:
    try:
        return git("show", f"{branch}:{path}", check=True)
    except Exception:
        return None


def parse_worker_state(md: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Best-effort parsing for multiple WORKER_STATE.md formats used historically.
    Returns (heartbeat, claimed_page).
    """
    heartbeat = None
    claimed = None

    # Heartbeat patterns
    for pat in [
        r"\bHeartbeat\b[^0-9]*([0-9]{9,})",
    ]:
        m = re.search(pat, md, flags=re.IGNORECASE)
        if m:
            try:
                heartbeat = int(m.group(1))
            except ValueError:
                pass
            break

    # Claimed page patterns (new template)
    m = re.search(r"Claimed Page\b[^0-9]*(\d{1,3})", md, flags=re.IGNORECASE)
    if m:
        try:
            claimed = int(m.group(1))
        except ValueError:
            claimed = None

    # Old milestone table formats may include "claiming" row; don't attempt to infer if ambiguous.
    return heartbeat, claimed


def scan_branch_done_pages(branch: str) -> Set[int]:
    out = git("ls-tree", "-r", "--name-only", branch, "--", "translations", check=True)
    pages: Set[int] = set()
    for p in out.splitlines():
        p = p.strip()
        m = PAGE_JSON_RE.match(p)
        if not m:
            continue
        pages.add(int(m.group(1)))
    return pages


def scan_branch_reviewed_pages(branch: str) -> Set[int]:
    out = git("ls-tree", "-r", "--name-only", branch, "--", "reviews", check=False)
    if not out:
        return set()
    pages: Set[int] = set()
    for p in out.splitlines():
        p = p.strip()
        m = REVIEW_RE.match(p)
        if not m:
            continue
        pages.add(int(m.group(1)))
    return pages


def build_state(total_pages: int) -> Dict:
    """
    Global state is derived from remote branches:
    - done pages: any branch containing translations/page_XXX.json (or legacy translations/final/page_XXX.json)
    - reviewed pages: any branch containing reviews/page_XXX.<id>.md
    - claimed pages: best-effort from WORKER_STATE.md
    """
    branches = list_remote_cursor_branches()

    done_by_page: Dict[int, List[str]] = {i: [] for i in range(1, total_pages + 1)}
    reviewed_by_page: Dict[int, List[str]] = {i: [] for i in range(1, total_pages + 1)}
    claimed_by_page: Dict[int, List[str]] = {i: [] for i in range(1, total_pages + 1)}
    workers: List[WorkerInfo] = []

    for b in branches:
        ws = try_git_show(b, "WORKER_STATE.md")
        short_id = short_id_from_branch(b.replace("origin/", ""))  # stable even without state file
        heartbeat = None
        claimed = None
        if ws:
            heartbeat, claimed = parse_worker_state(ws)
        workers.append(WorkerInfo(branch=b, short_id=short_id, heartbeat=heartbeat, claimed_page=claimed))

        for p in scan_branch_done_pages(b):
            if 1 <= p <= total_pages:
                done_by_page[p].append(b)

        for p in scan_branch_reviewed_pages(b):
            if 1 <= p <= total_pages:
                reviewed_by_page[p].append(b)

        if claimed is not None and 1 <= claimed <= total_pages:
            claimed_by_page[claimed].append(b)

    done_pages = sorted([p for p, bs in done_by_page.items() if bs])
    reviewed_pages = sorted([p for p, bs in reviewed_by_page.items() if bs])
    claimed_pages = sorted([p for p, bs in claimed_by_page.items() if bs])

    online_workers = [w for w in workers if w.online]

    return {
        "generated_at": now_ts(),
        "total_pages": total_pages,
        "branches": branches,
        "workers": [
            {
                "branch": w.branch,
                "short_id": w.short_id,
                "heartbeat": w.heartbeat,
                "online": w.online,
                "claimed_page": w.claimed_page,
            }
            for w in workers
        ],
        "online_workers": len(online_workers),
        "done_pages": done_pages,
        "reviewed_pages": reviewed_pages,
        "claimed_pages": claimed_pages,
        "done_by_page": done_by_page,
        "reviewed_by_page": reviewed_by_page,
        "claimed_by_page": claimed_by_page,
    }


def load_cache(max_age_s: int = 60) -> Optional[Dict]:
    if not os.path.exists(CACHE_PATH):
        return None
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        age = now_ts() - int(data.get("generated_at", 0))
        if age <= max_age_s:
            return data
        return None
    except Exception:
        return None


def save_cache(state: Dict) -> None:
    ensure_cache_dir()
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def refresh_state(total_pages: int, *, force: bool) -> Dict:
    cached = None if force else load_cache()
    if cached is not None and cached.get("total_pages") == total_pages:
        return cached
    git("fetch", "origin", "--prune")
    state = build_state(total_pages)
    save_cache(state)
    return state


def shard_pages(slot: int, slots: int, total_pages: int) -> List[int]:
    # Pages are 1-indexed; shard by (page-1) mod slots
    return [p for p in range(1, total_pages + 1) if ((p - 1) % slots) == slot]


def choose_next_page(
    *,
    state: Dict,
    total_pages: int,
    slot: int,
    slots: int,
    mode: str,
) -> Optional[int]:
    done = set(state["done_pages"])
    claimed = set(state["claimed_pages"])

    if mode == "shard":
        candidates = shard_pages(slot, slots, total_pages)
    elif mode == "steal":
        candidates = list(range(1, total_pages + 1))
    else:
        raise ValueError(f"Unknown mode: {mode}")

    for p in candidates:
        if p in done:
            continue
        if p in claimed:
            continue
        return p
    return None


def cmd_refresh(args: argparse.Namespace) -> int:
    state = refresh_state(args.total_pages, force=True)
    print(json.dumps({"generated_at": state["generated_at"], "done": len(state["done_pages"]), "claimed": len(state["claimed_pages"]), "reviewed": len(state["reviewed_pages"]), "online_workers": state["online_workers"]}))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state = refresh_state(args.total_pages, force=args.force)
    total = args.total_pages
    done = len(state["done_pages"])
    reviewed = len(state["reviewed_pages"])
    claimed = len(state["claimed_pages"])
    online = state["online_workers"]

    print(f"Total pages: {total}")
    print(f"Done pages: {done}")
    print(f"Reviewed pages: {reviewed}")
    print(f"Claimed pages: {claimed}")
    print(f"Online workers (heartbeat <10m): {online}")

    if args.workers:
        print("")
        for w in state["workers"]:
            hb = w.get("heartbeat")
            age = None
            if hb:
                age = now_ts() - int(hb)
            status = "ONLINE" if w.get("online") else "offline"
            claim = w.get("claimed_page")
            claim_s = "-" if claim is None else str(claim)
            age_s = "-" if age is None else f"{age}s"
            print(f"{w['short_id']} {status:6} claim={claim_s:>3} hb_age={age_s:>6} {w['branch']}")

    return 0


def cmd_next(args: argparse.Namespace) -> int:
    branch = current_branch()
    short_id = args.short_id or short_id_from_branch(branch)
    slot = args.slot if args.slot is not None else slot_from_short_id(short_id, args.slots)
    state = refresh_state(args.total_pages, force=args.force)
    p = choose_next_page(state=state, total_pages=args.total_pages, slot=slot, slots=args.slots, mode=args.mode)
    if p is None:
        return 2
    print(p)
    return 0


def cmd_shard(args: argparse.Namespace) -> int:
    branch = current_branch()
    short_id = args.short_id or short_id_from_branch(branch)
    slot = args.slot if args.slot is not None else slot_from_short_id(short_id, args.slots)
    pages = shard_pages(slot, args.slots, args.total_pages)
    for p in pages:
        print(p)
    return 0


def cmd_where(args: argparse.Namespace) -> int:
    state = refresh_state(args.total_pages, force=args.force)
    p = args.page
    branches = state["done_by_page"].get(p) or []
    if not branches:
        return 2
    for b in branches:
        print(b)
    return 0


def cmd_review_queue(args: argparse.Namespace) -> int:
    """
    Deterministic pairing: reviewer(slot) reviews pages from previous slot.
    """
    branch = current_branch()
    short_id = args.short_id or short_id_from_branch(branch)
    my_slot = args.slot if args.slot is not None else slot_from_short_id(short_id, args.slots)
    target_slot = (my_slot - 1) % args.slots

    state = refresh_state(args.total_pages, force=args.force)
    done = set(state["done_pages"])
    reviewed = set(state["reviewed_pages"])

    targets = [p for p in shard_pages(target_slot, args.slots, args.total_pages) if p in done and p not in reviewed]
    for p in targets:
        src = (state["done_by_page"].get(p) or ["?"])[0]
        print(f"{p}\t{src}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Multi-agent sync helper (no daemon).")
    p.add_argument("--total-pages", type=int, default=TOTAL_PAGES_DEFAULT, help="Total pages in project (default: 99).")
    p.add_argument("--slots", type=int, default=DEFAULT_SLOTS, help="Shard slots (default: 16).")
    p.add_argument("--force", action="store_true", help="Force refresh (ignore local cache).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("refresh", help="Fetch + rebuild local cache.")
    sp.set_defaults(func=cmd_refresh)

    sp = sub.add_parser("status", help="Print global status summary.")
    sp.add_argument("--workers", action="store_true", help="List discovered workers.")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("next", help="Print next page number to work on.")
    sp.add_argument("--mode", choices=["shard", "steal"], default="shard")
    sp.add_argument("--short-id", default=None)
    sp.add_argument("--slot", type=int, default=None, help="Override computed slot (0..slots-1).")
    sp.set_defaults(func=cmd_next)

    sp = sub.add_parser("shard", help="Print all page numbers in your shard.")
    sp.add_argument("--short-id", default=None)
    sp.add_argument("--slot", type=int, default=None)
    sp.set_defaults(func=cmd_shard)

    sp = sub.add_parser("where", help="Print branch(es) that contain a given page translation.")
    sp.add_argument("page", type=int)
    sp.set_defaults(func=cmd_where)

    sp = sub.add_parser("review-queue", help="List pages you should review (page<TAB>source-branch).")
    sp.add_argument("--short-id", default=None)
    sp.add_argument("--slot", type=int, default=None)
    sp.set_defaults(func=cmd_review_queue)

    return p


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

