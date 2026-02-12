#!/usr/bin/env python3
"""
collect_translations.py — collect page translations from remote worker branches
into the local working tree (for an integrator branch / PR).

This does NOT commit or push; it only writes files.

Usage:
  python3 tools/collect_translations.py --output translations
  python3 tools/collect_translations.py --output translations --total-pages 99
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional, Sequence, Tuple


PAGE_JSON_RE = re.compile(r"translations/(?:final/)?page_(\d{3})\.json$")


def run(cmd: List[str], *, check: bool = True) -> str:
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{res.stderr.strip()}")
    return res.stdout


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check)


def list_remote_cursor_branches() -> List[str]:
    out = git("branch", "-r")
    branches = []
    for line in out.splitlines():
        b = line.strip()
        if b.startswith("origin/cursor/"):
            branches.append(b)
    return sorted(branches)


def branch_translation_paths(branch: str) -> List[str]:
    out = git("ls-tree", "-r", "--name-only", branch, "--", "translations", check=True)
    return [l.strip() for l in out.splitlines() if l.strip()]


def branch_has_path(branch: str, path: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{branch}:{path}"]).returncode == 0


def read_remote_file(branch: str, path: str) -> str:
    return git("show", f"{branch}:{path}", check=True)


def file_last_touch_ts(branch: str, path: str) -> int:
    """
    Timestamp (unix) for last commit that touched a path in a branch.
    If unavailable, fallback to branch HEAD timestamp.
    """
    try:
        out = git("log", "-1", "--format=%ct", branch, "--", path, check=True).strip()
        if out:
            return int(out)
    except Exception:
        pass
    out = git("log", "-1", "--format=%ct", branch, check=True).strip()
    return int(out) if out else 0


def best_source_for_page(page: int, candidates: List[Tuple[str, str]]) -> Optional[Tuple[str, str]]:
    """
    candidates: [(branch, path)]
    Choose by latest touch timestamp.
    """
    best = None
    best_ts = -1
    for branch, path in candidates:
        ts = file_last_touch_ts(branch, path)
        if ts > best_ts:
            best_ts = ts
            best = (branch, path)
    return best


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Collect translations from remote worker branches into local directory.")
    ap.add_argument("--output", default="translations", help="Local output dir (default: translations).")
    ap.add_argument("--total-pages", type=int, default=99, help="Total pages (default: 99).")
    ap.add_argument("--fetch", action="store_true", help="Fetch origin before collecting.")
    args = ap.parse_args(list(argv))

    if args.fetch:
        git("fetch", "origin", "--prune")

    branches = list_remote_cursor_branches()
    page_sources: Dict[int, List[Tuple[str, str]]] = {p: [] for p in range(1, args.total_pages + 1)}

    for b in branches:
        for p in branch_translation_paths(b):
            m = PAGE_JSON_RE.match(p)
            if not m:
                continue
            page = int(m.group(1))
            if 1 <= page <= args.total_pages:
                page_sources[page].append((b, p))

    os.makedirs(args.output, exist_ok=True)

    written = 0
    missing = 0
    for page in range(1, args.total_pages + 1):
        candidates = page_sources.get(page) or []
        if not candidates:
            missing += 1
            continue

        best = best_source_for_page(page, candidates)
        if best is None:
            missing += 1
            continue
        branch, src_path = best
        content = read_remote_file(branch, src_path)

        out_path = os.path.join(args.output, f"page_{page:03d}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        written += 1
        print(f"WROTE page_{page:03d}.json  <-  {branch}:{src_path}")

    print(f"\nCollected: {written} pages. Missing: {missing} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

