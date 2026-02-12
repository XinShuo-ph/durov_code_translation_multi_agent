#!/usr/bin/env python3
"""
Parallel coordination helper for multi-agent translation workers.

This tool makes the protocol executable by providing:
1) live worker snapshot,
2) machine-checked page availability,
3) deterministic next-page selection (shard-first),
4) branch-level audit metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


PAGE_FILE_RE = re.compile(r"^translations/(?:.*/)?page_(\d{3})\.json$")
INT_RE = re.compile(r"\d+")


@dataclass
class WorkerState:
    canonical_branch: str
    display_branch: str
    short_id: str
    heartbeat: Optional[int]
    status: str
    milestone: Optional[str]
    claimed_page: Optional[int]
    lease_expires_at: Optional[int]
    completed_pages: Set[int] = field(default_factory=set)
    translated_pages: Set[int] = field(default_factory=set)
    online: bool = False
    heartbeat_age: Optional[int] = None


def run_git(args: List[str], check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        text=True,
        capture_output=True,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def git_show(ref: str, path: str) -> Optional[str]:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def canonical_branch_name(branch: str) -> str:
    if branch.startswith("origin/"):
        return branch[len("origin/") :]
    return branch


def branch_to_short_id(branch: str) -> str:
    token = canonical_branch_name(branch).split("/")[-1].split("-")[-1]
    return token[-4:]


def parse_int(value: str) -> Optional[int]:
    if value is None:
        return None
    m = INT_RE.search(value)
    return int(m.group(0)) if m else None


def parse_worker_state(markdown: str, branch: str) -> WorkerState:
    short_id = branch_to_short_id(branch)
    short_match = re.search(r"\*\*Short ID\*\*:\s*([^\n]+)", markdown)
    if short_match:
        candidate = short_match.group(1).strip()
        if candidate and "[" not in candidate:
            short_id = candidate

    heartbeat = parse_int(
        re.search(r"\*\*Heartbeat\*\*:\s*([^\n]+)", markdown).group(1)
        if re.search(r"\*\*Heartbeat\*\*:\s*([^\n]+)", markdown)
        else None
    )
    status = (
        re.search(r"\*\*Status\*\*:\s*([^\n]+)", markdown).group(1).strip().lower()
        if re.search(r"\*\*Status\*\*:\s*([^\n]+)", markdown)
        else "unknown"
    )
    milestone = (
        re.search(r"\*\*Milestone\*\*:\s*([^\n]+)", markdown).group(1).strip()
        if re.search(r"\*\*Milestone\*\*:\s*([^\n]+)", markdown)
        else None
    )
    claimed_page = parse_int(
        re.search(r"\*\*Claimed Page\*\*:\s*([^\n]+)", markdown).group(1)
        if re.search(r"\*\*Claimed Page\*\*:\s*([^\n]+)", markdown)
        else None
    )
    lease_expires_at = parse_int(
        re.search(r"\*\*Lease Expires At\*\*:\s*([^\n]+)", markdown).group(1)
        if re.search(r"\*\*Lease Expires At\*\*:\s*([^\n]+)", markdown)
        else None
    )

    completed_pages: Set[int] = set()
    inferred_claimed_page: Optional[int] = None
    section = ""
    for line in markdown.splitlines():
        if line.startswith("## "):
            section = line.strip().lower()
            continue
        if section.startswith("## completed pages"):
            match = re.match(r"\|\s*(\d+)\s*\|", line)
            if match:
                completed_pages.add(int(match.group(1)))
        elif section.startswith("## m2 page claims"):
            row_match = re.match(r"\|\s*(\d+)\s*\|(.+)\|", line)
            if not row_match:
                continue
            page = int(row_match.group(1))
            parts = [part.strip().lower() for part in line.split("|")]
            status_col = parts[2] if len(parts) > 2 else ""
            if "done" in status_col or "complete" in status_col:
                completed_pages.add(page)
            elif "translating" in status_col or "claimed" in status_col:
                inferred_claimed_page = page

    if claimed_page is None and inferred_claimed_page is not None:
        claimed_page = inferred_claimed_page

    canonical = canonical_branch_name(branch)
    return WorkerState(
        canonical_branch=canonical,
        display_branch=branch,
        short_id=short_id,
        heartbeat=heartbeat,
        status=status,
        milestone=milestone,
        claimed_page=claimed_page,
        lease_expires_at=lease_expires_at,
        completed_pages=completed_pages,
    )


def remote_refs(ref_glob: str) -> List[str]:
    out = run_git(["for-each-ref", "--format=%(refname:short)", ref_glob], check=False)
    if not out:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def translated_pages_for_ref(ref: str) -> Set[int]:
    out = run_git(["ls-tree", "-r", "--name-only", ref, "translations"], check=False)
    if not out:
        return set()
    pages = set()
    for path in out.splitlines():
        match = PAGE_FILE_RE.match(path.strip())
        if match:
            pages.add(int(match.group(1)))
    return pages


def translated_pages_local() -> Set[int]:
    pages = set()
    root = Path("translations")
    if not root.exists():
        return pages
    for path in root.rglob("page_*.json"):
        match = re.match(r"page_(\d{3})\.json$", path.name)
        if match:
            pages.add(int(match.group(1)))
    return pages


def load_states(
    ref_glob: str,
    offline_seconds: int,
) -> Dict[str, WorkerState]:
    now = int(time.time())
    states: Dict[str, WorkerState] = {}

    for ref in remote_refs(ref_glob):
        content = git_show(ref, "WORKER_STATE.md")
        if content is None:
            continue
        state = parse_worker_state(content, ref)
        state.translated_pages = translated_pages_for_ref(ref)
        states[state.canonical_branch] = state

    # Local branch overrides remote state for the same branch, if present.
    local_branch = run_git(["branch", "--show-current"], check=False).strip()
    local_state_path = Path("WORKER_STATE.md")
    if local_branch and local_state_path.exists():
        content = local_state_path.read_text(encoding="utf-8")
        local_state = parse_worker_state(content, local_branch)
        local_state.translated_pages = translated_pages_local()
        states[local_state.canonical_branch] = local_state

    for state in states.values():
        if state.heartbeat is not None:
            age = max(0, now - state.heartbeat)
            state.heartbeat_age = age
            state.online = age <= offline_seconds
        else:
            state.heartbeat_age = None
            state.online = False
    return states


def active_claims(states: Iterable[WorkerState], now: Optional[int] = None) -> Dict[int, List[WorkerState]]:
    now = now if now is not None else int(time.time())
    claims: Dict[int, List[WorkerState]] = {}
    for state in states:
        if not state.online:
            continue
        if state.claimed_page is None:
            continue
        if state.lease_expires_at is not None and state.lease_expires_at < now:
            continue
        if "idle" in state.status or "offline" in state.status:
            continue
        claims.setdefault(state.claimed_page, []).append(state)
    return claims


def completed_pages(states: Iterable[WorkerState]) -> Dict[int, List[WorkerState]]:
    completed: Dict[int, List[WorkerState]] = {}
    for state in states:
        for page in state.completed_pages | state.translated_pages:
            completed.setdefault(page, []).append(state)
    return completed


def available_pages(
    states: Iterable[WorkerState],
    total_pages: int,
) -> List[int]:
    claim_map = active_claims(states)
    done_map = completed_pages(states)
    return [
        page
        for page in range(1, total_pages + 1)
        if page not in claim_map and page not in done_map
    ]


def current_branch_short_id(states: Dict[str, WorkerState]) -> Tuple[Optional[str], Optional[str]]:
    local_branch = run_git(["branch", "--show-current"], check=False).strip()
    if not local_branch:
        return None, None
    canonical = canonical_branch_name(local_branch)
    if canonical in states:
        return canonical, states[canonical].short_id
    return canonical, branch_to_short_id(local_branch)


def cmd_snapshot(args: argparse.Namespace) -> int:
    states = load_states(args.ref_glob, args.offline_seconds)
    workers = list(states.values())
    claim_map = active_claims(workers)
    done_map = completed_pages(workers)
    online = [w for w in workers if w.online]

    print(f"workers_total={len(workers)} online={len(online)} offline={len(workers)-len(online)}")
    print(f"pages_completed={len(done_map)} pages_claimed={len(claim_map)}")
    print("")
    print("short_id  online  claim  completed  hb_age_s  branch")
    print("--------  ------  -----  ---------  --------  ------")
    for state in sorted(workers, key=lambda s: s.short_id):
        claim_text = str(state.claimed_page) if state.claimed_page is not None else "-"
        done_count = len(state.completed_pages | state.translated_pages)
        age_text = str(state.heartbeat_age) if state.heartbeat_age is not None else "-"
        online_text = "yes" if state.online else "no"
        print(
            f"{state.short_id:8}  {online_text:6}  {claim_text:5}  {done_count:9}  {age_text:8}  {state.canonical_branch}"
        )

    dup_claims = {page: owners for page, owners in claim_map.items() if len(owners) > 1}
    if dup_claims:
        print("")
        print("duplicate_claims:")
        for page in sorted(dup_claims):
            owners = ",".join(sorted(o.short_id for o in dup_claims[page]))
            print(f"  page_{page:03d}: {owners}")
    return 0


def cmd_check_page(args: argparse.Namespace) -> int:
    states = load_states(args.ref_glob, args.offline_seconds)
    workers = list(states.values())
    claim_map = active_claims(workers)
    done_map = completed_pages(workers)
    page = args.page

    completed_by = sorted({w.short_id for w in done_map.get(page, [])})
    claimed_by = sorted({w.short_id for w in claim_map.get(page, [])})

    if completed_by:
        print(f"page={page} status=completed by={','.join(completed_by)}")
        return 0
    if claimed_by:
        print(f"page={page} status=claimed by={','.join(claimed_by)}")
        return 2
    print(f"page={page} status=available")
    return 0


def cmd_next_page(args: argparse.Namespace) -> int:
    states = load_states(args.ref_glob, args.offline_seconds)
    workers = list(states.values())
    available = available_pages(workers, args.total_pages)

    self_branch, self_short = current_branch_short_id(states)
    if self_branch is None or self_short is None:
        print("Unable to determine current branch identity.", file=sys.stderr)
        return 1

    # If this worker already has a live claim, keep it.
    self_state = states.get(self_branch)
    if self_state and self_state.online:
        current_claims = active_claims([self_state])
        if self_state.claimed_page in current_claims:
            page = self_state.claimed_page
            if args.plain:
                print(page)
            else:
                print(f"next_page={page} reason=existing_live_claim worker={self_short}")
            return 0

    if not available:
        if args.plain:
            print("")
        else:
            print("No pages available.")
        return 1

    online_ids = sorted({w.short_id for w in workers if w.online})
    if self_short not in online_ids:
        online_ids.append(self_short)
        online_ids.sort()

    selected = None
    reason = "global_lowest"

    if args.strategy == "shard" and online_ids:
        idx = online_ids.index(self_short)
        n = len(online_ids)
        shard_pages = [p for p in available if (p - 1) % n == idx]
        if shard_pages:
            selected = shard_pages[0]
            reason = f"shard rank={idx+1}/{n}"

    if selected is None:
        selected = available[0]

    if args.plain:
        print(selected)
    else:
        print(
            f"next_page={selected} reason={reason} "
            f"online_workers={len(online_ids)} available={len(available)} worker={self_short}"
        )
    return 0


def unique_translation_commits(base_ref: str, branch_ref: str) -> int:
    out = run_git(
        ["log", "--pretty=format:%H", f"{base_ref}..{branch_ref}", "--", "translations"],
        check=False,
    )
    return len([line for line in out.splitlines() if line.strip()]) if out else 0


def cmd_audit(args: argparse.Namespace) -> int:
    states = load_states(args.ref_glob, args.offline_seconds)
    workers = list(states.values())
    refs = remote_refs(args.ref_glob)

    per_branch = []
    total_translation_commits = 0
    for ref in refs:
        canonical = canonical_branch_name(ref)
        count = unique_translation_commits(args.base_ref, ref)
        total_translation_commits += count
        state = states.get(canonical)
        m2_rows = len(state.completed_pages) if state else 0
        per_branch.append(
            {
                "branch": canonical,
                "short_id": branch_to_short_id(canonical),
                "translation_commits": count,
                "completed_pages": m2_rows,
                "milestone": state.milestone if state else None,
                "status": state.status if state else None,
            }
        )

    per_branch.sort(key=lambda item: item["translation_commits"], reverse=True)
    top3 = sum(item["translation_commits"] for item in per_branch[:3])
    share_top3 = (100.0 * top3 / total_translation_commits) if total_translation_commits else 0.0

    milestones: Dict[str, int] = {}
    for state in workers:
        key = state.milestone or "unknown"
        milestones[key] = milestones.get(key, 0) + 1

    claims = active_claims(workers)
    duplicate_claims = {
        page: sorted(worker.short_id for worker in owners)
        for page, owners in claims.items()
        if len(owners) > 1
    }

    payload = {
        "branch_count": len(refs),
        "workers_observed": len(workers),
        "milestone_counts": milestones,
        "translation_commit_total": total_translation_commits,
        "top3_translation_commit_share_pct": round(share_top3, 2),
        "duplicate_claim_count": len(duplicate_claims),
        "duplicate_claims": duplicate_claims,
        "per_branch": per_branch,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"branch_count={payload['branch_count']} workers_observed={payload['workers_observed']}")
    print(f"milestone_counts={payload['milestone_counts']}")
    print(
        "translation_commits_total="
        f"{payload['translation_commit_total']} top3_share_pct={payload['top3_translation_commit_share_pct']}"
    )
    print(f"duplicate_active_claims={payload['duplicate_claim_count']}")
    if duplicate_claims:
        for page in sorted(duplicate_claims):
            print(f"  page_{page:03d}: {','.join(duplicate_claims[page])}")
    print("")
    print("top_branches_by_translation_commits:")
    for item in per_branch[:8]:
        print(
            f"  {item['short_id']} commits={item['translation_commits']} "
            f"completed_pages={item['completed_pages']} milestone={item['milestone']}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parallel multi-agent coordination helper")
    parser.add_argument(
        "--ref-glob",
        default="refs/remotes/origin/cursor/book-translation-multi-agent-*",
        help="git ref glob used to discover worker branches",
    )
    parser.add_argument(
        "--offline-seconds",
        type=int,
        default=600,
        help="heartbeat age threshold for online workers",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    snapshot = sub.add_parser("snapshot", help="show workers, claims, and coverage")
    snapshot.set_defaults(func=cmd_snapshot)

    check_page = sub.add_parser("check-page", help="check whether a page is available")
    check_page.add_argument("page", type=int)
    check_page.set_defaults(func=cmd_check_page)

    next_page = sub.add_parser("next-page", help="select next page using protocol strategy")
    next_page.add_argument("--total-pages", type=int, default=99)
    next_page.add_argument("--plain", action="store_true", help="print only the page number")
    next_page.add_argument(
        "--strategy",
        choices=["shard", "lowest"],
        default="shard",
        help="shard: modulo assignment among online workers, lowest: global lowest page",
    )
    next_page.set_defaults(func=cmd_next_page)

    audit = sub.add_parser("audit", help="summarize branch-level parallelism health")
    audit.add_argument("--base-ref", default="origin/main")
    audit.add_argument("--json", action="store_true")
    audit.set_defaults(func=cmd_audit)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
