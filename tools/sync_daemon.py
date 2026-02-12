#!/usr/bin/env python3
"""
Coordinator utility for multi-agent translation runs.

This script is intentionally stateless: each invocation pulls the current git
state and computes a fresh snapshot from remote branches.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


HEARTBEAT_RE = re.compile(r"\*\*Heartbeat\*\*:\s*([0-9]+)", re.IGNORECASE)
STATUS_RE = re.compile(r"\*\*Status\*\*:\s*([^\n\r]+)", re.IGNORECASE)
CLAIMED_PAGE_RE = re.compile(
    r"\*\*Claimed Page\*\*:\s*([0-9]+|none|-)", re.IGNORECASE
)
STARTED_AT_RE = re.compile(r"\*\*Started At\*\*:\s*([0-9]+)", re.IGNORECASE)
COMPLETED_ROW_RE = re.compile(r"^\|\s*([0-9]+)\s*\|", re.MULTILINE)
PAGE_FILE_PATTERNS = (
    re.compile(r"translations/raw/page_(\d{3})\.json$"),
    re.compile(r"translations/page_(\d{3})\.json$"),
)


@dataclass
class WorkerState:
    branch: str
    short_id: str
    heartbeat: Optional[int] = None
    heartbeat_age: Optional[int] = None
    status: str = "unknown"
    claimed_page: Optional[int] = None
    claim_started_at: Optional[int] = None
    done_pages: Set[int] = field(default_factory=set)

    @property
    def done_count(self) -> int:
        return len(self.done_pages)


@dataclass
class Snapshot:
    now: int
    branch_glob: str
    workers: List[WorkerState]
    online_workers: List[WorkerState]
    done_pages: Set[int]
    done_sources: Dict[int, List[str]]
    valid_claims: Dict[int, List[str]]


def run_git(args: Sequence[str], check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def default_branch_glob() -> str:
    env_glob = os.environ.get("SYNC_BRANCH_GLOB")
    if env_glob:
        return env_glob
    return "origin/cursor/book-translation-multi-agent-*"


def parse_excluded_pages(raw: str) -> Set[int]:
    raw = raw.strip()
    if not raw:
        return set()
    values: Set[int] = set()
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.add(int(item))
    return values


def short_id_from_branch(branch: str) -> str:
    tail = branch.split("/")[-1]
    if "-" in tail:
        return tail.rsplit("-", 1)[-1][-4:]
    return tail[-4:]


def normalize_worker_ref(worker_ref: str, workers: Iterable[WorkerState]) -> str:
    worker_ref = worker_ref.strip()
    if not worker_ref:
        return worker_ref

    by_short: Dict[str, List[str]] = defaultdict(list)
    for worker in workers:
        by_short[worker.short_id].append(worker.branch)

    if "/" not in worker_ref and len(worker_ref) <= 8:
        matches = by_short.get(worker_ref, [])
        if len(matches) == 1:
            return matches[0]

    if worker_ref.startswith("origin/"):
        return worker_ref
    if worker_ref.startswith("cursor/"):
        return f"origin/{worker_ref}"
    return worker_ref


def list_candidate_branches(branch_glob: str) -> List[str]:
    text = run_git(["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"])
    branches = [line.strip() for line in text.splitlines() if line.strip()]
    return sorted(branch for branch in branches if fnmatch.fnmatch(branch, branch_glob))


def read_file_from_branch(branch: str, path: str) -> Optional[str]:
    proc = subprocess.run(
        ["git", "show", f"{branch}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def list_translation_pages(branch: str) -> Set[int]:
    proc = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", branch, "translations"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return set()

    pages: Set[int] = set()
    for path in proc.stdout.splitlines():
        for pattern in PAGE_FILE_PATTERNS:
            match = pattern.match(path.strip())
            if match:
                pages.add(int(match.group(1)))
                break
    return pages


def parse_worker_state_markdown(markdown: str) -> Tuple[Optional[int], str, Optional[int], Optional[int], Set[int]]:
    heartbeat: Optional[int] = None
    status = "unknown"
    claimed_page: Optional[int] = None
    started_at: Optional[int] = None
    done_pages: Set[int] = set()

    heartbeat_match = HEARTBEAT_RE.search(markdown)
    if heartbeat_match:
        heartbeat = int(heartbeat_match.group(1))

    status_match = STATUS_RE.search(markdown)
    if status_match:
        status = status_match.group(1).strip().lower()

    claimed_match = CLAIMED_PAGE_RE.search(markdown)
    if claimed_match:
        raw = claimed_match.group(1).strip().lower()
        if raw.isdigit():
            claimed_page = int(raw)

    started_match = STARTED_AT_RE.search(markdown)
    if started_match:
        started_at = int(started_match.group(1))

    for completed_match in COMPLETED_ROW_RE.finditer(markdown):
        done_pages.add(int(completed_match.group(1)))

    return heartbeat, status, claimed_page, started_at, done_pages


def build_snapshot(args: argparse.Namespace) -> Snapshot:
    if args.fetch:
        run_git(["fetch", "origin", "--prune"])

    now = int(time.time())
    branches = list_candidate_branches(args.branch_glob)

    workers: List[WorkerState] = []
    done_sources: Dict[int, Set[str]] = defaultdict(set)
    claim_sources: Dict[int, List[str]] = defaultdict(list)

    for branch in branches:
        state_text = read_file_from_branch(branch, "WORKER_STATE.md")
        translated_pages = list_translation_pages(branch)

        if state_text is None and not translated_pages:
            continue

        worker = WorkerState(branch=branch, short_id=short_id_from_branch(branch))
        if state_text is not None:
            (
                worker.heartbeat,
                worker.status,
                worker.claimed_page,
                worker.claim_started_at,
                state_done_pages,
            ) = parse_worker_state_markdown(state_text)
            worker.done_pages.update(state_done_pages)

        worker.done_pages.update(translated_pages)

        if worker.heartbeat is not None:
            worker.heartbeat_age = max(now - worker.heartbeat, 0)

        workers.append(worker)

        for page in worker.done_pages:
            done_sources[page].add(branch)

    online_workers: List[WorkerState] = []
    for worker in workers:
        if worker.heartbeat is None or worker.heartbeat_age is None:
            continue
        if worker.heartbeat_age <= args.offline_seconds:
            online_workers.append(worker)

        if worker.claimed_page is None:
            continue
        if worker.heartbeat_age <= args.reclaim_seconds:
            claim_sources[worker.claimed_page].append(worker.branch)

    ordered_online = sorted(online_workers, key=lambda w: (w.short_id, w.branch))
    serializable_done_sources = {p: sorted(v) for p, v in done_sources.items()}
    serializable_claims = {p: sorted(v) for p, v in claim_sources.items()}

    return Snapshot(
        now=now,
        branch_glob=args.branch_glob,
        workers=sorted(workers, key=lambda w: (w.short_id, w.branch)),
        online_workers=ordered_online,
        done_pages=set(serializable_done_sources.keys()),
        done_sources=serializable_done_sources,
        valid_claims=serializable_claims,
    )


def resolve_worker(snapshot: Snapshot, requested_worker: str) -> WorkerState:
    if not requested_worker:
        local = run_git(["branch", "--show-current"], check=False).strip()
        requested_worker = local
    normalized = normalize_worker_ref(requested_worker, snapshot.workers)
    by_branch = {worker.branch: worker for worker in snapshot.workers}
    if normalized in by_branch:
        return by_branch[normalized]

    # Worker may not have pushed state yet; create a local placeholder.
    inferred_branch = normalized
    if inferred_branch.startswith("cursor/"):
        inferred_branch = f"origin/{inferred_branch}"
    short_id = short_id_from_branch(inferred_branch)
    return WorkerState(branch=inferred_branch, short_id=short_id)


def available_pages(
    snapshot: Snapshot,
    total_pages: int,
    excluded_pages: Set[int],
) -> List[int]:
    universe = set(range(1, total_pages + 1))
    claimed = set(snapshot.valid_claims.keys())
    return sorted(universe - excluded_pages - snapshot.done_pages - claimed)


def fairness_hold(
    worker: WorkerState,
    online_workers: List[WorkerState],
    min_online: int,
    fairness_gap: int,
) -> bool:
    if len(online_workers) < min_online:
        return False
    done_counts = [w.done_count for w in online_workers]
    if not done_counts:
        return False
    min_done = min(done_counts)
    return worker.done_count > (min_done + fairness_gap)


def pick_review_target(worker: WorkerState, online_workers: List[WorkerState]) -> Optional[WorkerState]:
    candidates = [w for w in online_workers if w.branch != worker.branch]
    if not candidates:
        return None
    return min(candidates, key=lambda w: (w.done_count, w.short_id, w.branch))


def next_action(
    snapshot: Snapshot,
    worker: WorkerState,
    args: argparse.Namespace,
) -> Dict[str, object]:
    online_workers = list(snapshot.online_workers)
    online_branches = {w.branch for w in online_workers}
    if worker.branch not in online_branches:
        online_workers.append(worker)
        online_workers.sort(key=lambda w: (w.short_id, w.branch))

    if worker.claimed_page is not None:
        claim_holders = snapshot.valid_claims.get(worker.claimed_page, [])
        if worker.branch in claim_holders and worker.claimed_page not in snapshot.done_pages:
            return {
                "action": "continue",
                "page": worker.claimed_page,
                "reason": "worker already owns an active claim",
            }

    if fairness_hold(worker, online_workers, args.fairness_min_online, args.fairness_gap):
        review_target = pick_review_target(worker, online_workers)
        return {
            "action": "review",
            "page": None,
            "reason": (
                "fairness gate active: worker is ahead of the slowest online peer by "
                f"more than {args.fairness_gap} page(s)"
            ),
            "review_target": review_target.branch if review_target else None,
            "review_target_short_id": review_target.short_id if review_target else None,
        }

    available = available_pages(snapshot, args.total_pages, args.excluded_pages)
    if not available:
        return {
            "action": "idle",
            "page": None,
            "reason": "no pages available",
        }

    n_workers = max(len(online_workers), 1)
    lane_index = 0
    for idx, lane_worker in enumerate(online_workers):
        if lane_worker.branch == worker.branch:
            lane_index = idx
            break

    lane_pages = [p for p in available if ((p - 1) % n_workers) == lane_index]
    if lane_pages:
        return {
            "action": "claim",
            "page": lane_pages[0],
            "reason": f"lane allocation ({lane_index + 1}/{n_workers})",
            "lane_index": lane_index,
            "lane_workers": n_workers,
        }

    return {
        "action": "claim",
        "page": available[0],
        "reason": "spillover allocation (lane empty)",
        "lane_index": lane_index,
        "lane_workers": n_workers,
    }


def page_status(snapshot: Snapshot, page: int, args: argparse.Namespace) -> Dict[str, object]:
    done_by = snapshot.done_sources.get(page, [])
    claimed_by = snapshot.valid_claims.get(page, [])
    online_workers = list(snapshot.online_workers)
    owner = None
    if online_workers:
        owner = online_workers[(page - 1) % len(online_workers)]

    if done_by:
        state = "done"
    elif claimed_by:
        state = "claimed"
    elif page in args.excluded_pages:
        state = "excluded"
    elif 1 <= page <= args.total_pages:
        state = "available"
    else:
        state = "out_of_range"

    return {
        "page": page,
        "state": state,
        "done_by": done_by,
        "claimed_by": claimed_by,
        "lane_owner": owner.branch if owner else None,
        "lane_owner_short_id": owner.short_id if owner else None,
    }


def serialize_snapshot(snapshot: Snapshot, args: argparse.Namespace) -> Dict[str, object]:
    duplicates = {
        page: branches
        for page, branches in snapshot.done_sources.items()
        if len(branches) > 1
    }
    avail = available_pages(snapshot, args.total_pages, args.excluded_pages)

    return {
        "timestamp": snapshot.now,
        "branch_glob": snapshot.branch_glob,
        "total_workers": len(snapshot.workers),
        "online_workers": len(snapshot.online_workers),
        "done_pages": sorted(snapshot.done_pages),
        "done_count": len(snapshot.done_pages),
        "valid_claims": {str(page): branches for page, branches in sorted(snapshot.valid_claims.items())},
        "duplicate_done_pages": {str(page): branches for page, branches in sorted(duplicates.items())},
        "available_count": len(avail),
        "available_preview": avail[:20],
        "workers": [
            {
                "branch": worker.branch,
                "short_id": worker.short_id,
                "status": worker.status,
                "heartbeat": worker.heartbeat,
                "heartbeat_age": worker.heartbeat_age,
                "claimed_page": worker.claimed_page,
                "done_count": worker.done_count,
                "done_preview": sorted(worker.done_pages)[:20],
            }
            for worker in snapshot.workers
        ],
    }


def print_human_snapshot(snapshot: Snapshot, args: argparse.Namespace) -> None:
    data = serialize_snapshot(snapshot, args)
    print(f"branch_glob={data['branch_glob']}")
    print(
        f"workers={data['total_workers']} online={data['online_workers']} "
        f"done={data['done_count']}/{args.total_pages} available={data['available_count']}"
    )
    duplicate_count = len(data["duplicate_done_pages"])
    print(f"duplicate_done_pages={duplicate_count}")
    if duplicate_count:
        sample = sorted(int(p) for p in data["duplicate_done_pages"].keys())[:10]
        pretty = ", ".join(f"{p:03d}" for p in sample)
        print(f"duplicate_sample={pretty}")

    print("online_workers:")
    if not snapshot.online_workers:
        print("  (none)")
    for worker in snapshot.online_workers:
        age = worker.heartbeat_age if worker.heartbeat_age is not None else -1
        claim = worker.claimed_page if worker.claimed_page is not None else "-"
        print(
            f"  - {worker.short_id} branch={worker.branch} "
            f"done={worker.done_count} claim={claim} heartbeat_age={age}s"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute coordination state for parallel translation workers."
    )
    parser.add_argument(
        "--branch-glob",
        default=default_branch_glob(),
        help=(
            "Remote branch glob to include, e.g. "
            "'origin/cursor/book-translation-multi-agent-*'"
        ),
    )
    parser.add_argument(
        "--total-pages",
        type=int,
        default=99,
        help="Total number of production pages.",
    )
    parser.add_argument(
        "--excluded-pages",
        type=parse_excluded_pages,
        default=set(),
        help="Comma-separated pages to ignore in allocation (example: 13,43).",
    )
    parser.add_argument(
        "--offline-seconds",
        type=int,
        default=600,
        help="Heartbeat age threshold for online workers.",
    )
    parser.add_argument(
        "--reclaim-seconds",
        type=int,
        default=900,
        help="Claim becomes reclaimable when heartbeat is older than this value.",
    )
    parser.add_argument(
        "--fairness-min-online",
        type=int,
        default=4,
        help="Enable fairness gating only at or above this many online workers.",
    )
    parser.add_argument(
        "--fairness-gap",
        type=int,
        default=1,
        help="Max allowed lead over the slowest online worker before REVIEW is required.",
    )
    parser.add_argument(
        "--worker",
        default="",
        help="Worker reference: short id, local branch, or remote branch.",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=0,
        help="Page number for --check-page.",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Run git fetch origin --prune before computing.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--snapshot", action="store_true", help="Print current global snapshot.")
    mode.add_argument("--next-page", action="store_true", help="Print only the next page to claim.")
    mode.add_argument(
        "--next-action",
        action="store_true",
        help="Print recommended action: claim, continue, review, or idle.",
    )
    mode.add_argument("--check-page", action="store_true", help="Show status for one page.")

    args = parser.parse_args()
    if args.check_page and args.page <= 0:
        parser.error("--check-page requires --page N with N > 0")
    return args


def main() -> int:
    args = parse_args()
    try:
        snapshot = build_snapshot(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.snapshot:
        if args.json:
            print(json.dumps(serialize_snapshot(snapshot, args), ensure_ascii=False, indent=2))
        else:
            print_human_snapshot(snapshot, args)
        return 0

    if args.check_page:
        payload = page_status(snapshot, args.page, args)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"page={payload['page']} state={payload['state']}")
            print(f"done_by={','.join(payload['done_by']) or '-'}")
            print(f"claimed_by={','.join(payload['claimed_by']) or '-'}")
            print(
                "lane_owner="
                f"{payload['lane_owner_short_id'] or '-'} "
                f"({payload['lane_owner'] or '-'})"
            )
        return 0

    worker = resolve_worker(snapshot, args.worker)
    action = next_action(snapshot, worker, args)

    if args.next_page:
        if action["action"] in {"claim", "continue"} and action["page"] is not None:
            print(action["page"])
            return 0
        print("")
        return 1

    # args.next_action
    if args.json:
        print(json.dumps(action, ensure_ascii=False, indent=2))
    else:
        print(f"action={action['action']}")
        print(f"page={action.get('page') or '-'}")
        print(f"reason={action['reason']}")
        if action.get("review_target_short_id"):
            print(
                "review_target="
                f"{action['review_target_short_id']} ({action['review_target']})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
