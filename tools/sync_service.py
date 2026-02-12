#!/usr/bin/env python3
"""
sync_service.py

Purpose:
  Make the multi-agent protocol *executable* by providing one command that:
  - Fetches remote peer branches from the SAME experiment batch (prefix filtered)
  - Reads peer WORKER_STATE.md (simple template format) for claimed pages + heartbeat
  - Scans peer branches for completed translations (translations/page_XXX.json)
  - Computes next available page to work on

This is intentionally stdlib-only.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
import time
from typing import Iterable, List, Optional, Sequence, Set, Tuple


TOTAL_PAGES_DEFAULT = 99
ONLINE_MAX_AGE_SECONDS_DEFAULT = 10 * 60  # 10 minutes


class GitError(RuntimeError):
    pass


def _run(cmd: Sequence[str], *, check: bool = True, cwd: Optional[str] = None) -> str:
    try:
        p = subprocess.run(
            list(cmd),
            cwd=cwd,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise GitError(e.stderr.strip() or str(e)) from e
    return p.stdout


def repo_root() -> str:
    return _run(["git", "rev-parse", "--show-toplevel"]).strip()


def current_branch() -> str:
    return _run(["git", "branch", "--show-current"]).strip()


def branch_short_id(branch: str) -> str:
    # Expect branches like cursor/something-1a2b ; short id is last 4 chars of last dash segment.
    last = branch.split("/")[-1]
    seg = last.split("-")[-1]
    return seg[-4:] if len(seg) >= 4 else seg


def experiment_prefix(branch: str) -> str:
    """
    Prefix = branch name with last '-<suffix>' removed.
    Example: cursor/collaborative-translation-initiation-ba2f -> cursor/collaborative-translation-initiation
    """
    # Remove only the final "-token" if present.
    if "-" not in branch:
        return branch
    return branch.rsplit("-", 1)[0]


def fetch_origin(*, prune: bool = True) -> None:
    cmd = ["git", "fetch", "origin"]
    if prune:
        cmd.append("--prune")
    _run(cmd)


def list_origin_cursor_branches() -> List[str]:
    """
    Return remote branches like: origin/cursor/foo-bar-1234
    """
    out = _run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/cursor/"]
    )
    branches = [ln.strip() for ln in out.splitlines() if ln.strip()]
    return branches


def peer_branches(my_branch: str) -> Tuple[str, List[str]]:
    """
    Identify peers by matching the SAME experiment prefix as my_branch.
    """
    prefix = experiment_prefix(my_branch)  # e.g. cursor/book-translation-multi-agent
    want = f"origin/{prefix}-"
    peers = [b for b in list_origin_cursor_branches() if b.startswith(want)]
    return prefix, sorted(set(peers))


WORKER_STATE_PATH = "WORKER_STATE.md"

_RE_HEARTBEAT = re.compile(r"^\s*-\s+\*\*Heartbeat\*\*:\s*([0-9]+)\s*$", re.MULTILINE)
_RE_STATUS = re.compile(r"^\s*-\s+\*\*Status\*\*:\s*([^\n]+?)\s*$", re.MULTILINE)
_RE_CLAIMED = re.compile(r"^\s*-\s+\*\*Claimed Page\*\*:\s*([0-9]+|none)\s*$", re.MULTILINE)


@dataclasses.dataclass(frozen=True)
class Worker:
    branch: str  # origin/...
    short_id: str
    heartbeat: Optional[int]
    status: Optional[str]
    claimed_page: Optional[int]  # None means none/unknown
    online: bool


def read_worker_state(remote_branch: str, *, now: int, online_max_age_s: int) -> Optional[Worker]:
    """
    Read WORKER_STATE.md from a remote branch. Returns None if not present.
    """
    try:
        txt = _run(["git", "show", f"{remote_branch}:{WORKER_STATE_PATH}"], check=True)
    except GitError:
        return None

    hb_m = _RE_HEARTBEAT.search(txt)
    st_m = _RE_STATUS.search(txt)
    cl_m = _RE_CLAIMED.search(txt)

    hb = int(hb_m.group(1)) if hb_m else None
    status = st_m.group(1).strip() if st_m else None
    claimed_raw = cl_m.group(1).strip() if cl_m else None
    claimed = int(claimed_raw) if claimed_raw and claimed_raw.isdigit() else None

    online = False
    if hb is not None:
        online = (now - hb) <= online_max_age_s

    return Worker(
        branch=remote_branch,
        short_id=branch_short_id(remote_branch.replace("origin/", "", 1)),
        heartbeat=hb,
        status=status,
        claimed_page=claimed,
        online=online,
    )


_RE_PAGE_JSON = re.compile(
    r"^translations/(?:raw/|final/)?page_(\d{3})\.json$"
)


def list_completed_pages(remote_branch: str) -> Set[int]:
    """
    Completed pages are inferred from committed JSON translation files.

    We accept both:
      - translations/page_XXX.json  (canonical)
      - translations/raw/page_XXX.json (legacy)
      - translations/final/page_XXX.json (legacy)
    """
    try:
        out = _run(["git", "ls-tree", "-r", "--name-only", remote_branch, "--", "translations"])
    except GitError:
        return set()
    pages: Set[int] = set()
    for p in out.splitlines():
        p = p.strip()
        if not p:
            continue
        m = _RE_PAGE_JSON.match(p)
        if m:
            pages.add(int(m.group(1)))
    return pages


@dataclasses.dataclass(frozen=True)
class ScanResult:
    my_branch: str
    prefix: str
    peers: List[str]
    now: int
    online_max_age_s: int
    total_pages: int
    workers: List[Worker]
    completed_pages: List[int]
    claimed_pages_online: List[int]
    next_page: Optional[int]


def scan(
    *,
    my_branch: str,
    total_pages: int,
    online_max_age_s: int,
    do_fetch: bool,
) -> ScanResult:
    if do_fetch:
        fetch_origin(prune=True)

    prefix, peers = peer_branches(my_branch)
    now = int(time.time())

    workers: List[Worker] = []
    completed: Set[int] = set()
    claimed_online: Set[int] = set()

    for b in peers:
        w = read_worker_state(b, now=now, online_max_age_s=online_max_age_s)
        if w is not None:
            workers.append(w)
            if w.online and w.claimed_page is not None:
                claimed_online.add(w.claimed_page)
        completed |= list_completed_pages(b)

    all_pages = set(range(1, total_pages + 1))
    available = sorted(all_pages - completed - claimed_online)
    next_page = available[0] if available else None

    return ScanResult(
        my_branch=my_branch,
        prefix=prefix,
        peers=peers,
        now=now,
        online_max_age_s=online_max_age_s,
        total_pages=total_pages,
        workers=sorted(workers, key=lambda w: (not w.online, w.short_id)),
        completed_pages=sorted(completed),
        claimed_pages_online=sorted(claimed_online),
        next_page=next_page,
    )


def to_jsonable(res: ScanResult) -> dict:
    return {
        "my_branch": res.my_branch,
        "prefix": res.prefix,
        "peers": res.peers,
        "now": res.now,
        "online_max_age_s": res.online_max_age_s,
        "total_pages": res.total_pages,
        "workers": [
            {
                "branch": w.branch,
                "short_id": w.short_id,
                "heartbeat": w.heartbeat,
                "status": w.status,
                "claimed_page": w.claimed_page,
                "online": w.online,
            }
            for w in res.workers
        ],
        "completed_pages": res.completed_pages,
        "claimed_pages_online": res.claimed_pages_online,
        "next_page": res.next_page,
    }


def print_status(res: ScanResult) -> None:
    online = [w for w in res.workers if w.online]
    offline = [w for w in res.workers if not w.online]

    def fmt_worker(w: Worker) -> str:
        hb = str(w.heartbeat) if w.heartbeat is not None else "?"
        cl = str(w.claimed_page) if w.claimed_page is not None else "none"
        st = w.status or "?"
        return f"{w.short_id}\t{'ONLINE' if w.online else 'OFFLINE'}\tclaimed={cl}\thb={hb}\t{w.branch}\tstatus={st}"

    print(f"prefix: {res.prefix}")
    print(f"peers: {len(res.peers)} remote branches matched")
    print(f"online: {len(online)}  offline: {len(offline)}  (online_max_age_s={res.online_max_age_s})")
    print(f"completed_pages: {len(res.completed_pages)}/{res.total_pages}")
    if res.next_page is not None:
        print(f"next_page: {res.next_page}")
    else:
        print("next_page: none (all pages completed or currently claimed)")

    if online:
        print("\nONLINE WORKERS")
        for w in online:
            print(fmt_worker(w))
    if offline:
        print("\nOFFLINE/UNKNOWN WORKERS")
        for w in offline:
            print(fmt_worker(w))


def _cache_path(root: str) -> str:
    d = os.path.join(root, ".sync")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "state.json")


def cmd_scan(args: argparse.Namespace) -> int:
    my_branch = args.branch or current_branch()
    if not my_branch:
        print("ERROR: could not determine current branch (use --branch).", file=sys.stderr)
        return 2

    res = scan(
        my_branch=my_branch,
        total_pages=args.total_pages,
        online_max_age_s=args.online_max_age_s,
        do_fetch=not args.no_fetch,
    )
    root = repo_root()
    path = _cache_path(root)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_jsonable(res), f, ensure_ascii=False, indent=2)
        f.write("\n")

    if args.quiet:
        return 0

    print(json.dumps(to_jsonable(res), ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    my_branch = args.branch or current_branch()
    if not my_branch:
        print("ERROR: could not determine current branch (use --branch).", file=sys.stderr)
        return 2
    res = scan(
        my_branch=my_branch,
        total_pages=args.total_pages,
        online_max_age_s=args.online_max_age_s,
        do_fetch=not args.no_fetch,
    )
    print_status(res)
    return 0


def cmd_next_page(args: argparse.Namespace) -> int:
    my_branch = args.branch or current_branch()
    if not my_branch:
        print("ERROR: could not determine current branch (use --branch).", file=sys.stderr)
        return 2
    res = scan(
        my_branch=my_branch,
        total_pages=args.total_pages,
        online_max_age_s=args.online_max_age_s,
        do_fetch=not args.no_fetch,
    )
    if res.next_page is None:
        return 1
    print(res.next_page)
    return 0


def cmd_check_page(args: argparse.Namespace) -> int:
    my_branch = args.branch or current_branch()
    if not my_branch:
        print("ERROR: could not determine current branch (use --branch).", file=sys.stderr)
        return 2
    res = scan(
        my_branch=my_branch,
        total_pages=args.total_pages,
        online_max_age_s=args.online_max_age_s,
        do_fetch=not args.no_fetch,
    )
    page = args.page
    is_completed = page in set(res.completed_pages)
    is_claimed = page in set(res.claimed_pages_online)
    if args.json:
        print(
            json.dumps(
                {"page": page, "available": (not is_completed and not is_claimed), "completed": is_completed, "claimed_online": is_claimed},
                ensure_ascii=False,
            )
        )
    else:
        if is_completed:
            print(f"page {page}: NOT available (already completed)")
        elif is_claimed:
            print(f"page {page}: NOT available (claimed by an online worker)")
        else:
            print(f"page {page}: available")
    return 0 if (not is_completed and not is_claimed) else 1


def cmd_daemon(args: argparse.Namespace) -> int:
    my_branch = args.branch or current_branch()
    if not my_branch:
        print("ERROR: could not determine current branch (use --branch).", file=sys.stderr)
        return 2

    root = repo_root()
    path = _cache_path(root)
    interval = args.interval_s
    print(f"sync daemon started (interval={interval}s). writing: {path}", file=sys.stderr)
    while True:
        try:
            res = scan(
                my_branch=my_branch,
                total_pages=args.total_pages,
                online_max_age_s=args.online_max_age_s,
                do_fetch=True,
            )
            with open(path, "w", encoding="utf-8") as f:
                json.dump(to_jsonable(res), f, ensure_ascii=False, indent=2)
                f.write("\n")
        except Exception as e:
            print(f"[daemon] error: {e}", file=sys.stderr)
        time.sleep(interval)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Executable sync/claim helper for multi-agent translation.")
    parser.add_argument("--branch", help="Local branch name (defaults to current).")
    parser.add_argument("--total-pages", type=int, default=TOTAL_PAGES_DEFAULT)
    parser.add_argument("--online-max-age-s", type=int, default=ONLINE_MAX_AGE_SECONDS_DEFAULT)
    parser.add_argument("--no-fetch", action="store_true", help="Do not run 'git fetch origin --prune'.")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Scan peers and write .sync/state.json (also prints JSON).")
    p_scan.add_argument("--quiet", action="store_true", help="Do not print JSON to stdout.")
    p_scan.set_defaults(func=cmd_scan)

    p_status = sub.add_parser("status", help="Human-readable status summary.")
    p_status.set_defaults(func=cmd_status)

    p_next = sub.add_parser("next-page", help="Print next available page number (exit 1 if none).")
    p_next.set_defaults(func=cmd_next_page)

    p_check = sub.add_parser("check-page", help="Check if a page is available (exit 0 yes, 1 no).")
    p_check.add_argument("page", type=int)
    p_check.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    p_check.set_defaults(func=cmd_check_page)

    p_daemon = sub.add_parser("daemon", help="Run a background scanner (writes .sync/state.json).")
    p_daemon.add_argument("--interval-s", type=int, default=60)
    p_daemon.set_defaults(func=cmd_daemon)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

