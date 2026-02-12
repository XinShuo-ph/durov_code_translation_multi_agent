#!/usr/bin/env python3
"""Coordination helper for multi-agent page translation.

Commands:
  - status: show workers, coverage, duplicates, and skew.
  - next: compute the next page for a worker with fairness gating.
  - stale: list reclaimable claims from stale/offline workers.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


PAGE_FILE_RE = re.compile(r"translations/(?:raw/)?page_(\d+)\.json$")


def git(args: List[str], allow_fail: bool = False) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except subprocess.CalledProcessError:
        if allow_fail:
            return ""
        raise


def fetch_if_requested(do_fetch: bool) -> None:
    if do_fetch:
        subprocess.check_call(["git", "fetch", "origin", "--prune"])


def parse_short_id(branch: str) -> str:
    # Example: origin/cursor/book-translation-multi-agent-c68e -> c68e
    return branch.rsplit("-", 1)[-1].lower()


def parse_heartbeat(worker_state: str) -> Optional[int]:
    if not worker_state:
        return None

    patterns = [
        r"(?im)^\s*Heartbeat:\s*(\d+)\s*$",
        r"(?im)\*\*Heartbeat\*\*:\s*(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, worker_state)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def parse_claimed_page(worker_state: str) -> Optional[int]:
    if not worker_state:
        return None

    # Canonical v3 field
    direct_patterns = [
        r"(?im)^\s*Claimed-Page:\s*([^\n]+)\s*$",
        r"(?im)\*\*Claimed Page\*\*:\s*([^\n]+)",
    ]
    for pattern in direct_patterns:
        match = re.search(pattern, worker_state)
        if not match:
            continue
        raw = (
            match.group(1)
            .strip()
            .strip("`")
            .strip("*")
            .strip()
            .lower()
        )
        if raw in {"none", "-", "n/a", "null", ""}:
            return None
        num = re.search(r"\d+", raw)
        if num:
            return int(num.group(0))

    # Legacy milestone table row: | 37 | translating | ... |
    for match in re.finditer(r"(?im)^\|\s*(\d+)\s*\|\s*([^\|]+)\|", worker_state):
        page = int(match.group(1))
        status = match.group(2).strip().lower()
        if any(key in status for key in ("translating", "claimed", "in_progress", "working")):
            if "done" not in status and "complete" not in status:
                return page

    return None


def list_remote_branches(ref_glob: str) -> List[str]:
    output = git(["for-each-ref", "--format=%(refname:short)", ref_glob], allow_fail=True)
    branches = [line.strip() for line in output.splitlines() if line.strip()]
    return sorted(branches)


def read_branch_file(branch: str, path: str) -> str:
    return git(["show", f"{branch}:{path}"], allow_fail=True)


def last_commit_timestamp(branch: str) -> Optional[int]:
    ts = git(["log", "-1", "--format=%ct", branch], allow_fail=True)
    if not ts:
        return None
    try:
        return int(ts.strip())
    except ValueError:
        return None


def list_completed_pages(branch: str) -> Set[int]:
    tree = git(["ls-tree", "-r", "--name-only", branch], allow_fail=True)
    pages: Set[int] = set()
    for path in tree.splitlines():
        match = PAGE_FILE_RE.search(path.strip())
        if match:
            pages.add(int(match.group(1)))
    return pages


@dataclass
class Worker:
    branch: str
    short_id: str
    heartbeat: Optional[int]
    heartbeat_age_s: Optional[int]
    last_commit: Optional[int]
    online: bool
    claimed_page: Optional[int]
    completed_pages: List[int]


@dataclass
class Snapshot:
    total_pages: int
    now: int
    workers: List[Worker]
    online_ids: List[str]
    completed_union: List[int]
    duplicate_pages: Dict[int, List[str]]
    claimed_pages_online: List[int]
    available_pages: List[int]
    stale_claims: List[Dict[str, object]]


def build_snapshot(
    ref_glob: str,
    total_pages: int,
    heartbeat_timeout_s: int,
    reclaim_timeout_s: int,
) -> Snapshot:
    now = int(time.time())
    branches = list_remote_branches(ref_glob)

    workers: List[Worker] = []
    page_to_workers: Dict[int, List[str]] = {}
    stale_claims: List[Dict[str, object]] = []

    for branch in branches:
        short_id = parse_short_id(branch)
        worker_state = read_branch_file(branch, "WORKER_STATE.md")
        heartbeat = parse_heartbeat(worker_state)
        claimed_page = parse_claimed_page(worker_state)
        completed_pages = sorted(list_completed_pages(branch))
        last_commit = last_commit_timestamp(branch)

        heartbeat_age: Optional[int] = None
        if heartbeat is not None:
            heartbeat_age = max(0, now - heartbeat)

        # Primary online signal is heartbeat; fallback to commit recency if missing.
        if heartbeat_age is not None:
            online = heartbeat_age <= heartbeat_timeout_s
        elif last_commit is not None:
            online = (now - last_commit) <= heartbeat_timeout_s
        else:
            online = False

        worker = Worker(
            branch=branch,
            short_id=short_id,
            heartbeat=heartbeat,
            heartbeat_age_s=heartbeat_age,
            last_commit=last_commit,
            online=online,
            claimed_page=claimed_page,
            completed_pages=completed_pages,
        )
        workers.append(worker)

        for page in completed_pages:
            page_to_workers.setdefault(page, []).append(short_id)

        if (
            not online
            and claimed_page is not None
            and heartbeat_age is not None
            and heartbeat_age >= reclaim_timeout_s
        ):
            stale_claims.append(
                {
                    "worker": short_id,
                    "branch": branch,
                    "claimed_page": claimed_page,
                    "stale_age_s": heartbeat_age,
                }
            )

    online_ids = sorted([worker.short_id for worker in workers if worker.online])
    completed_union = sorted(page_to_workers.keys())
    duplicate_pages = {
        page: sorted(ids)
        for page, ids in page_to_workers.items()
        if len(ids) > 1
    }

    claimed_pages_online = sorted(
        {
            worker.claimed_page
            for worker in workers
            if worker.online and worker.claimed_page is not None
        }
    )

    all_pages = set(range(1, total_pages + 1))
    available_pages = sorted(all_pages - set(completed_union) - set(claimed_pages_online))

    return Snapshot(
        total_pages=total_pages,
        now=now,
        workers=sorted(workers, key=lambda worker: worker.short_id),
        online_ids=online_ids,
        completed_union=completed_union,
        duplicate_pages=duplicate_pages,
        claimed_pages_online=claimed_pages_online,
        available_pages=available_pages,
        stale_claims=sorted(stale_claims, key=lambda row: int(row["claimed_page"])),
    )


def snapshot_to_json(snapshot: Snapshot) -> str:
    payload = {
        "total_pages": snapshot.total_pages,
        "now": snapshot.now,
        "online_ids": snapshot.online_ids,
        "completed_union": snapshot.completed_union,
        "duplicate_pages": snapshot.duplicate_pages,
        "claimed_pages_online": snapshot.claimed_pages_online,
        "available_pages": snapshot.available_pages,
        "stale_claims": snapshot.stale_claims,
        "workers": [
            {
                "branch": worker.branch,
                "short_id": worker.short_id,
                "heartbeat": worker.heartbeat,
                "heartbeat_age_s": worker.heartbeat_age_s,
                "last_commit": worker.last_commit,
                "online": worker.online,
                "claimed_page": worker.claimed_page,
                "completed_pages": worker.completed_pages,
            }
            for worker in snapshot.workers
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def command_status(args: argparse.Namespace) -> int:
    fetch_if_requested(args.fetch)
    snapshot = build_snapshot(
        ref_glob=args.ref_glob,
        total_pages=args.total_pages,
        heartbeat_timeout_s=args.heartbeat_timeout_s,
        reclaim_timeout_s=args.reclaim_timeout_s,
    )

    if args.json:
        print(snapshot_to_json(snapshot))
        return 0

    total_artifacts = sum(len(worker.completed_pages) for worker in snapshot.workers)
    unique_pages = len(snapshot.completed_union)
    duplicate_artifacts = total_artifacts - unique_pages
    duplicate_pct = (100.0 * duplicate_artifacts / total_artifacts) if total_artifacts else 0.0

    print(f"TOTAL_WORKERS={len(snapshot.workers)}")
    print(f"ONLINE_WORKERS={len(snapshot.online_ids)} [{','.join(snapshot.online_ids) or '-'}]")
    print(f"COVERAGE={unique_pages}/{snapshot.total_pages}")
    print(
        "DUPLICATE_PAGES="
        f"{len(snapshot.duplicate_pages)} "
        f"DUPLICATE_ARTIFACTS={duplicate_artifacts}/{total_artifacts} ({duplicate_pct:.1f}%)"
    )
    print(f"CLAIMED_ONLINE={snapshot.claimed_pages_online or '-'}")
    print(f"AVAILABLE_COUNT={len(snapshot.available_pages)}")

    print("\nWORKER_LEADERBOARD")
    print("id\tonline\tdone\tclaimed\theartbeat_age_s")
    for worker in sorted(
        snapshot.workers,
        key=lambda item: (len(item.completed_pages), item.short_id),
        reverse=True,
    ):
        print(
            f"{worker.short_id}\t{str(worker.online).lower()}\t{len(worker.completed_pages)}\t"
            f"{worker.claimed_page if worker.claimed_page is not None else '-'}\t"
            f"{worker.heartbeat_age_s if worker.heartbeat_age_s is not None else '-'}"
        )

    if snapshot.stale_claims:
        print("\nRECLAIMABLE_STALE_CLAIMS")
        for stale in snapshot.stale_claims:
            print(
                f"page={stale['claimed_page']} "
                f"worker={stale['worker']} stale_age_s={stale['stale_age_s']}"
            )

    return 0


def choose_next_page(
    snapshot: Snapshot,
    worker_id: str,
    max_lead: int,
    fairness_min_online: int,
) -> Tuple[Optional[int], str]:
    if not snapshot.available_pages:
        return None, "all_pages_done_or_claimed"

    online_pool = list(snapshot.online_ids)
    if worker_id not in online_pool:
        online_pool.append(worker_id)
        online_pool = sorted(set(online_pool))

    # Fairness gate: with enough active workers, prevent one worker from running far ahead.
    online_done = {
        worker.short_id: len(worker.completed_pages)
        for worker in snapshot.workers
        if worker.online
    }
    if worker_id not in online_done:
        online_done[worker_id] = 0

    if len(snapshot.online_ids) >= fairness_min_online and online_done:
        my_done = online_done.get(worker_id, 0)
        min_done = min(online_done.values())
        if my_done - min_done > max_lead:
            return (
                None,
                (
                    f"hold_lead_cap_exceeded my_done={my_done} "
                    f"min_done={min_done} max_lead={max_lead}"
                ),
            )

    index = online_pool.index(worker_id)
    shard_pages = [
        page
        for page in snapshot.available_pages
        if (page - 1) % len(online_pool) == index
    ]
    if shard_pages:
        return shard_pages[0], f"shard_assignment pool={','.join(online_pool)}"

    return snapshot.available_pages[0], "fallback_lowest_available"


def command_next(args: argparse.Namespace) -> int:
    fetch_if_requested(args.fetch)
    snapshot = build_snapshot(
        ref_glob=args.ref_glob,
        total_pages=args.total_pages,
        heartbeat_timeout_s=args.heartbeat_timeout_s,
        reclaim_timeout_s=args.reclaim_timeout_s,
    )

    worker_id = args.worker_id.strip().lower()
    if not worker_id:
        print("ERROR=worker_id_required", file=sys.stderr)
        return 2

    page, reason = choose_next_page(
        snapshot=snapshot,
        worker_id=worker_id,
        max_lead=args.max_lead,
        fairness_min_online=args.fairness_min_online,
    )

    if page is None and reason.startswith("hold_lead_cap_exceeded"):
        print("HOLD=lead_cap")
        print(f"DETAIL={reason}")
        print("ACTION=review_peer_output_or_wait_for_team_catchup")
        return 0

    if page is None:
        print("NEXT_PAGE=none")
        print(f"REASON={reason}")
        return 0

    print(f"NEXT_PAGE={page}")
    print(f"REASON={reason}")
    print(f"ONLINE_WORKERS={len(snapshot.online_ids)}")
    print(f"AVAILABLE_COUNT={len(snapshot.available_pages)}")
    if snapshot.stale_claims:
        first = snapshot.stale_claims[0]
        print(
            "STALE_RECLAIM_HINT="
            f"page_{first['claimed_page']}_from_{first['worker']}"
        )
    return 0


def command_stale(args: argparse.Namespace) -> int:
    fetch_if_requested(args.fetch)
    snapshot = build_snapshot(
        ref_glob=args.ref_glob,
        total_pages=args.total_pages,
        heartbeat_timeout_s=args.heartbeat_timeout_s,
        reclaim_timeout_s=args.reclaim_timeout_s,
    )

    if args.json:
        print(json.dumps(snapshot.stale_claims, indent=2, sort_keys=True))
        return 0

    if not snapshot.stale_claims:
        print("STALE_CLAIMS=none")
        return 0

    print(f"STALE_CLAIMS={len(snapshot.stale_claims)}")
    for stale in snapshot.stale_claims:
        print(
            f"page={stale['claimed_page']} "
            f"worker={stale['worker']} "
            f"stale_age_s={stale['stale_age_s']}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    def add_common_options(target: argparse.ArgumentParser) -> None:
        target.add_argument(
            "--ref-glob",
            default="refs/remotes/origin/cursor/book-translation-multi-agent-*",
            help="Git ref glob for worker branches",
        )
        target.add_argument(
            "--total-pages",
            type=int,
            default=99,
            help="Total pages in book/project",
        )
        target.add_argument(
            "--heartbeat-timeout-s",
            type=int,
            default=600,
            help="Heartbeat age threshold to consider worker online",
        )
        target.add_argument(
            "--reclaim-timeout-s",
            type=int,
            default=900,
            help="Heartbeat age threshold to reclaim stale claims",
        )
        target.add_argument(
            "--fetch",
            action="store_true",
            help="Run git fetch origin --prune before evaluation",
        )

    parser = argparse.ArgumentParser(
        description="Coordination helper for multi-agent translation."
    )
    add_common_options(parser)

    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show team status and skew")
    add_common_options(status)
    status.add_argument("--json", action="store_true", help="Emit JSON output")
    status.set_defaults(func=command_status)

    next_cmd = subparsers.add_parser("next", help="Compute next page for worker")
    add_common_options(next_cmd)
    next_cmd.add_argument(
        "--worker-id",
        required=True,
        help="Worker short id (e.g. c68e)",
    )
    next_cmd.add_argument(
        "--max-lead",
        type=int,
        default=2,
        help="Max page lead over slowest online worker before hold",
    )
    next_cmd.add_argument(
        "--fairness-min-online",
        type=int,
        default=4,
        help="Enforce lead cap only when online worker count reaches this threshold",
    )
    next_cmd.set_defaults(func=command_next)

    stale = subparsers.add_parser("stale", help="List reclaimable stale claims")
    add_common_options(stale)
    stale.add_argument("--json", action="store_true", help="Emit JSON output")
    stale.set_defaults(func=command_stale)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
