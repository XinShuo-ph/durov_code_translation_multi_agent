#!/usr/bin/env python3
"""
Lightweight team sync helper (no daemon).

Commands:
  - status: fetch + list active workers
  - check-page N: show who claims/completed N
  - next-page: print lowest available page number

This tool is intentionally conservative: it trusts WORKER_STATE.md as the
coordination source-of-truth and avoids scanning translation files across
branches (expensive).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Iterable


def _run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output.strip() or f"git failed: {' '.join(args)}") from e


def git_fetch() -> None:
    _run_git(["git", "fetch", "origin", "--prune"])


def list_origin_cursor_branches() -> list[str]:
    out = _run_git(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/cursor/"]
    )
    branches = [line.strip() for line in out.splitlines() if line.strip()]
    # Keep stable order for humans
    return sorted(branches)


def try_read_worker_state(branch: str) -> str | None:
    try:
        return _run_git(["git", "show", f"{branch}:WORKER_STATE.md"])
    except Exception:
        return None


_RE_HEARTBEAT = re.compile(r"\*\*Heartbeat\*\*:\s*([0-9]+)")
_RE_STATUS = re.compile(r"\*\*Status\*\*:\s*([A-Za-z_]+)")
_RE_CLAIMED = re.compile(r"\*\*Claimed Page\*\*:\s*([0-9]+|none)", re.IGNORECASE)
_RE_STARTED = re.compile(r"\*\*Started At\*\*:\s*([0-9]+|-)")


def _parse_completed_pages(md: str) -> set[int]:
    pages: set[int] = set()
    in_table = False
    for line in md.splitlines():
        if line.strip().lower() == "## completed pages":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table:
            continue
        # Table lines like: | 13   | 1735688400   | a8f3b2c1 |
        m = re.match(r"^\|\s*([0-9]{1,3})\s*\|", line)
        if m:
            pages.add(int(m.group(1)))
    return pages


def _parse_ready_for_review_pages(md: str) -> set[int]:
    pages: set[int] = set()
    in_table = False
    for line in md.splitlines():
        if line.strip().lower() == "## ready for review":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table:
            continue
        m = re.match(r"^\|\s*([0-9]{1,3})\s*\|", line)
        if m:
            pages.add(int(m.group(1)))
    return pages


def short_id_from_branch(branch: str) -> str:
    # branch like: origin/cursor/book-translation-multi-agent-14ce
    leaf = branch.split("/")[-1]
    tail = leaf.split("-")[-1]
    return (tail[-4:] if len(tail) >= 4 else tail).lower()


@dataclass(frozen=True)
class Worker:
    branch: str
    short_id: str
    heartbeat: int | None
    status: str | None
    claimed_page: int | None
    started_at: int | None
    completed_pages: set[int]
    ready_for_review_pages: set[int]

    def heartbeat_age(self, now: int) -> int | None:
        if self.heartbeat is None:
            return None
        return now - self.heartbeat


def parse_worker(branch: str, md: str) -> Worker:
    hb = None
    m = _RE_HEARTBEAT.search(md)
    if m:
        hb = int(m.group(1))

    st = None
    m = _RE_STATUS.search(md)
    if m:
        st = m.group(1).strip()

    claimed = None
    m = _RE_CLAIMED.search(md)
    if m:
        v = m.group(1).strip().lower()
        claimed = int(v) if v.isdigit() else None

    started_at = None
    m = _RE_STARTED.search(md)
    if m:
        v = m.group(1).strip()
        started_at = int(v) if v.isdigit() else None

    return Worker(
        branch=branch,
        short_id=short_id_from_branch(branch),
        heartbeat=hb,
        status=st,
        claimed_page=claimed,
        started_at=started_at,
        completed_pages=_parse_completed_pages(md),
        ready_for_review_pages=_parse_ready_for_review_pages(md),
    )


def load_workers() -> list[Worker]:
    workers: list[Worker] = []
    for br in list_origin_cursor_branches():
        md = try_read_worker_state(br)
        if not md:
            continue
        workers.append(parse_worker(br, md))
    return workers


def is_online(w: Worker, now: int, offline_seconds: int) -> bool:
    age = w.heartbeat_age(now)
    if age is None:
        return False
    return age < offline_seconds


def print_status(workers: Iterable[Worker], offline_seconds: int) -> int:
    now = int(time.time())
    rows = []
    for w in workers:
        age = w.heartbeat_age(now)
        online = is_online(w, now, offline_seconds)
        rows.append(
            (
                "ONLINE" if online else "OFFLINE",
                w.short_id,
                w.status or "-",
                str(w.claimed_page) if w.claimed_page is not None else "-",
                f"{age}s" if age is not None else "-",
                w.branch,
            )
        )

    if not rows:
        print("No workers found (no origin/cursor/* branches with WORKER_STATE.md).")
        return 1

    print("STATE     ID    STATUS            CLAIM  HEARTBEAT_AGE  BRANCH")
    for r in rows:
        print(f"{r[0]:<9} {r[1]:<5} {r[2]:<17} {r[3]:<5} {r[4]:<13} {r[5]}")
    return 0


def check_page(workers: Iterable[Worker], page: int, offline_seconds: int) -> int:
    now = int(time.time())
    claimed_by = []
    completed_by = []
    ready_by = []

    for w in workers:
        online = is_online(w, now, offline_seconds)
        if online and w.claimed_page == page:
            claimed_by.append(w)
        if page in w.completed_pages:
            completed_by.append(w)
        if page in w.ready_for_review_pages:
            ready_by.append(w)

    if not claimed_by and not completed_by and not ready_by:
        print(f"page {page}: AVAILABLE (no online claim, no completed record)")
        return 0

    if claimed_by:
        for w in claimed_by:
            print(f"page {page}: CLAIMED by {w.short_id} ({w.branch})")
    if ready_by:
        for w in ready_by:
            print(f"page {page}: READY_FOR_REVIEW on {w.short_id} ({w.branch})")
    if completed_by:
        for w in completed_by:
            print(f"page {page}: COMPLETED on {w.short_id} ({w.branch})")
    return 0


def next_page(workers: Iterable[Worker], total_pages: int, offline_seconds: int) -> int:
    now = int(time.time())
    completed: set[int] = set()
    claimed: set[int] = set()

    for w in workers:
        completed |= w.completed_pages
        if is_online(w, now, offline_seconds) and w.claimed_page is not None:
            claimed.add(w.claimed_page)

    for p in range(1, total_pages + 1):
        if p in completed:
            continue
        if p in claimed:
            continue
        print(p)
        return 0

    print("NO_AVAILABLE_PAGES")
    return 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="team.py")
    ap.add_argument("--no-fetch", action="store_true", help="Skip git fetch origin --prune")
    ap.add_argument("--offline-seconds", type=int, default=600, help="Heartbeat age threshold")
    ap.add_argument(
        "--branch-regex",
        type=str,
        default=".*",
        help="Only consider origin/cursor branches matching this regex",
    )

    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="List workers and claims")

    p_check = sub.add_parser("check-page", help="Check a page claim/completion")
    p_check.add_argument("page", type=int)

    p_next = sub.add_parser("next-page", help="Print lowest available page number")
    p_next.add_argument("--total-pages", type=int, default=99)

    ns = ap.parse_args(argv)

    if not ns.no_fetch:
        git_fetch()

    try:
        br_re = re.compile(ns.branch_regex)
    except re.error as e:
        ap.error(f"invalid --branch-regex: {e}")
        return 2

    workers = [w for w in load_workers() if br_re.search(w.branch)]

    if ns.cmd == "status":
        return print_status(workers, ns.offline_seconds)
    if ns.cmd == "check-page":
        return check_page(workers, ns.page, ns.offline_seconds)
    if ns.cmd == "next-page":
        return next_page(workers, ns.total_pages, ns.offline_seconds)

    ap.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

