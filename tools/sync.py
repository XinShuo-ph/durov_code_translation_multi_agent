#!/usr/bin/env python3
"""
sync.py - lightweight cross-branch sync helper.

This script is intentionally dependency-free (stdlib only). It helps a worker:
- list relevant remote branches (filtered by an experiment prefix)
- compute which pages are already translated across those branches
- pick a "next" page using a deterministic stagger (to reduce everyone starting on page 1)

It is designed to address the main failure mode observed in past runs:
workers discovering *all* cursor/* branches (including stale experiments), causing massive duplication.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple


PAGE_JSON_RE = re.compile(r"^translations/(?:raw/|final/)?page_(\d{3})\.json$")


def _run_git(args: List[str], *, check: bool = True) -> str:
    p = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def get_current_branch() -> str:
    return _run_git(["branch", "--show-current"]).strip()


def infer_short_id(branch: str) -> str:
    """
    Best-effort short id:
    - prefer a trailing 4-hex token (matches many Cursor branches)
    - otherwise: last 4 alnum characters
    """
    m = re.search(r"([0-9a-fA-F]{4})$", branch)
    if m:
        return m.group(1).lower()
    tail = re.sub(r"[^0-9A-Za-z]+", "", branch)[-4:]
    return (tail or "0000").lower()


def infer_experiment_prefix(branch: str) -> Optional[str]:
    """
    If branch name contains exp-<id>, infer remote prefix origin/cursor/exp-<id>- .
    Example: cursor/exp-005-translate-c68e -> origin/cursor/exp-005-
    """
    m = re.search(r"(exp-[0-9A-Za-z]+)", branch)
    if not m:
        return None
    return f"origin/cursor/{m.group(1)}-"


def list_remote_branches(prefix: str) -> List[str]:
    """
    prefix is a *remote short ref prefix*, e.g.:
    - origin/cursor/exp-005-
    - origin/cursor/book-translation-multi-agent-
    """
    out = _run_git(["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/cursor/"], check=True)
    branches = [line.strip() for line in out.splitlines() if line.strip()]
    return [b for b in branches if b.startswith(prefix)]


def list_translation_paths(branch: str) -> List[str]:
    try:
        out = _run_git(["ls-tree", "-r", "--name-only", branch], check=True)
    except RuntimeError:
        return []
    paths = []
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("translations/") or not line.endswith(".json"):
            continue
        if PAGE_JSON_RE.match(line):
            paths.append(line)
    return paths


def scan_translated_pages(branches: Iterable[str]) -> Tuple[Dict[int, List[Tuple[str, str]]], Dict[str, Set[int]]]:
    """
    Returns:
    - page_to_sources: {page_num: [(branch, path), ...]}
    - branch_to_pages: {branch: {page_num, ...}}
    """
    page_to_sources: Dict[int, List[Tuple[str, str]]] = {}
    branch_to_pages: Dict[str, Set[int]] = {}
    for b in branches:
        pages: Set[int] = set()
        for path in list_translation_paths(b):
            m = PAGE_JSON_RE.match(path)
            if not m:
                continue
            page = int(m.group(1))
            pages.add(page)
            page_to_sources.setdefault(page, []).append((b, path))
        branch_to_pages[b] = pages
    return page_to_sources, branch_to_pages


def deterministic_start_page(short_id: str, total_pages: int) -> int:
    """
    Deterministically spread workers across pages using short_id.
    """
    try:
        n = int(short_id, 16)
    except ValueError:
        n = sum(ord(c) for c in short_id)
    return 1 + (n % total_pages)


def pick_next_page(
    *,
    translated: Set[int],
    start_page: int,
    total_pages: int,
) -> Optional[int]:
    for i in range(total_pages):
        p = ((start_page - 1 + i) % total_pages) + 1
        if p not in translated:
            return p
    return None


def cmd_status(args: argparse.Namespace) -> int:
    if not args.no_fetch:
        _run_git(["fetch", "origin", "--prune"], check=True)

    branches = list_remote_branches(args.prefix)
    page_to_sources, branch_to_pages = scan_translated_pages(branches)

    translated = sorted(page_to_sources.keys())
    summary = {
        "prefix": args.prefix,
        "branches": len(branches),
        "translated_pages": len(translated),
        "total_pages": args.total_pages,
        "coverage": (len(translated) / args.total_pages) if args.total_pages else 0.0,
    }

    if args.json:
        payload = {
            "summary": summary,
            "per_branch": {b: sorted(list(p)) for b, p in branch_to_pages.items() if p},
            "duplicates": {str(p): len(srcs) for p, srcs in page_to_sources.items() if len(srcs) > 1},
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"Prefix: {args.prefix}")
    print(f"Remote branches matched: {len(branches)}")
    print(f"Translated pages found: {len(translated)}/{args.total_pages}")
    if translated:
        print(f"Lowest translated page: {min(translated)}")
        print(f"Highest translated page: {max(translated)}")
    dups = sorted([p for p, srcs in page_to_sources.items() if len(srcs) > 1])
    if dups:
        print(f"Duplicate pages (multiple sources): {len(dups)}")
        if args.verbose:
            for p in dups[:30]:
                srcs = page_to_sources[p]
                print(f"  page {p:03d}: {len(srcs)} sources")
    else:
        print("Duplicate pages: 0")

    if args.verbose:
        per = sorted(((b, len(p)) for b, p in branch_to_pages.items()), key=lambda x: (-x[1], x[0]))
        for b, n in per:
            if n:
                print(f"  {b}: {n} pages")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    if not args.no_fetch:
        _run_git(["fetch", "origin", "--prune"], check=True)

    branches = list_remote_branches(args.prefix)
    page_to_sources, _ = scan_translated_pages(branches)
    translated = set(page_to_sources.keys())

    branch = get_current_branch()
    short_id = args.short_id or infer_short_id(branch)
    start_page = args.start_page or deterministic_start_page(short_id, args.total_pages)
    nxt = pick_next_page(translated=translated, start_page=start_page, total_pages=args.total_pages)

    if args.json:
        print(
            json.dumps(
                {
                    "prefix": args.prefix,
                    "current_branch": branch,
                    "short_id": short_id,
                    "start_page": start_page,
                    "next_page": nxt,
                    "translated_pages": len(translated),
                },
                ensure_ascii=False,
            )
        )
        return 0

    if nxt is None:
        print("All pages appear translated across matched branches.")
        return 0

    print(nxt)
    return 0


def cmd_suggest_start(args: argparse.Namespace) -> int:
    branch = get_current_branch()
    short_id = args.short_id or infer_short_id(branch)
    start_page = deterministic_start_page(short_id, args.total_pages)
    if args.json:
        print(json.dumps({"current_branch": branch, "short_id": short_id, "start_page": start_page}, ensure_ascii=False))
        return 0
    print(start_page)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Cross-branch sync helper for multi-agent translation runs.")
    p.add_argument(
        "--prefix",
        default=None,
        help="Remote branch prefix to scan, e.g. origin/cursor/exp-005- . If omitted, inferred from current branch (exp-<id>).",
    )
    p.add_argument("--total-pages", type=int, default=99, help="Total pages in project (default: 99)")
    p.add_argument("--no-fetch", action="store_true", help="Do not run git fetch origin --prune")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("status", help="Show translation coverage across remote branches.")
    ps.add_argument("--json", action="store_true", help="JSON output")
    ps.add_argument("--verbose", action="store_true", help="Show per-branch counts / duplicates")
    ps.set_defaults(func=cmd_status)

    pn = sub.add_parser("next", help="Print next page number to translate (staggered).")
    pn.add_argument("--short-id", default=None, help="Override short id used for staggering.")
    pn.add_argument("--start-page", type=int, default=None, help="Override start page.")
    pn.add_argument("--json", action="store_true", help="JSON output")
    pn.set_defaults(func=cmd_next)

    pss = sub.add_parser("suggest-start", help="Suggest a deterministic start page for this worker.")
    pss.add_argument("--short-id", default=None, help="Override short id used for staggering.")
    pss.add_argument("--json", action="store_true", help="JSON output")
    pss.set_defaults(func=cmd_suggest_start)

    return p


def main(argv: List[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.prefix is None:
        inferred = infer_experiment_prefix(get_current_branch())
        if inferred is None:
            parser.error("--prefix is required unless your branch name contains exp-<id> (e.g. cursor/exp-005-translate-abcd)")
        args.prefix = inferred

    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

