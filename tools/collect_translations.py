#!/usr/bin/env python3
"""
collect_translations.py - collect translations from multiple remote branches.

This script is meant for an "Integrator" role:
- scan remote branches matching an experiment prefix
- find candidate translation JSON files per page
- pick a best candidate using simple heuristics (valid JSON + more sentences)
- write a unified translations/page_XXX.json set into the working tree

It does NOT push/commit for you; it just prepares the working tree.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


PAGE_JSON_RE = re.compile(r"^translations/(?:raw/|final/)?page_(\d{3})\.json$")


def _run_git(args: List[str], *, check: bool = True) -> str:
    p = subprocess.run(["git", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def list_remote_branches(prefix: str) -> List[str]:
    out = _run_git(["for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/cursor/"], check=True)
    branches = [line.strip() for line in out.splitlines() if line.strip()]
    return [b for b in branches if b.startswith(prefix)]


def list_candidate_paths(branch: str) -> List[str]:
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


def git_show(branch: str, path: str) -> Optional[str]:
    p = subprocess.run(["git", "show", f"{branch}:{path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        return None
    return p.stdout


def safe_json_loads(s: str) -> Optional[dict]:
    try:
        data = json.loads(s)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def score_translation(data: dict) -> Tuple[int, int]:
    """
    Returns (primary_score, sentence_count) where higher is better.
    """
    sentences = data.get("sentences")
    if not isinstance(sentences, list) or not sentences:
        return (0, 0)
    # Basic field presence check
    ok = 1
    for s in sentences:
        if not isinstance(s, dict):
            ok = 0
            break
        for k in ("ru", "en", "zh", "ja"):
            v = s.get(k)
            if not isinstance(v, str) or not v.strip():
                ok = 0
                break
        if ok == 0:
            break
    if ok == 0:
        return (100, len(sentences))  # parsed but incomplete
    return (10_000, len(sentences))


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_file(path: str, content: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def collect(prefix: str, total_pages: int) -> Tuple[Dict[int, dict], Dict[int, List[dict]]]:
    branches = list_remote_branches(prefix)
    page_candidates: Dict[int, List[dict]] = {p: [] for p in range(1, total_pages + 1)}

    for b in branches:
        for path in list_candidate_paths(b):
            m = PAGE_JSON_RE.match(path)
            if not m:
                continue
            page = int(m.group(1))
            raw = git_show(b, path)
            if raw is None:
                continue
            data = safe_json_loads(raw)
            if data is None:
                page_candidates[page].append(
                    {"branch": b, "path": path, "valid_json": False, "score": 0, "sentence_count": 0}
                )
                continue
            score, scount = score_translation(data)
            page_candidates[page].append(
                {
                    "branch": b,
                    "path": path,
                    "valid_json": True,
                    "score": score,
                    "sentence_count": scount,
                    "page_field": data.get("page"),
                    "raw": raw,
                }
            )

    winners: Dict[int, dict] = {}
    for page, cands in page_candidates.items():
        if not cands:
            continue
        # pick by score, then sentence_count, then stable branch name
        def key(c: dict) -> Tuple[int, int, str]:
            return (int(c.get("score", 0)), int(c.get("sentence_count", 0)), str(c.get("branch", "")))

        best = sorted(cands, key=key, reverse=True)[0]
        winners[page] = best

    return winners, page_candidates


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Collect translation JSONs from remote worker branches.")
    ap.add_argument(
        "--prefix",
        required=True,
        help="Remote branch prefix to scan, e.g. origin/cursor/exp-005-",
    )
    ap.add_argument("--total-pages", type=int, default=99)
    ap.add_argument("--out-dir", default="translations", help="Output directory (default: translations)")
    ap.add_argument("--no-fetch", action="store_true", help="Do not run git fetch origin --prune")
    ap.add_argument("--dry-run", action="store_true", help="Do not write files, only print summary")
    ap.add_argument("--manifest", default=None, help="Write manifest JSON to this path")
    args = ap.parse_args(list(argv))

    if not args.no_fetch:
        _run_git(["fetch", "origin", "--prune"], check=True)

    winners, candidates = collect(args.prefix, args.total_pages)

    missing = [p for p in range(1, args.total_pages + 1) if p not in winners]
    duplicates = [p for p, c in candidates.items() if len(c) > 1]

    print(f"Prefix: {args.prefix}")
    print(f"Winners: {len(winners)}/{args.total_pages}")
    print(f"Missing pages: {len(missing)}")
    print(f"Pages with duplicates: {len(duplicates)}")

    manifest = {
        "prefix": args.prefix,
        "total_pages": args.total_pages,
        "winners": {},
        "missing_pages": missing,
        "duplicate_pages": duplicates,
    }

    for p in sorted(winners.keys()):
        w = winners[p]
        manifest["winners"][str(p)] = {
            "branch": w.get("branch"),
            "path": w.get("path"),
            "valid_json": bool(w.get("valid_json")),
            "score": int(w.get("score", 0)),
            "sentence_count": int(w.get("sentence_count", 0)),
        }

    if args.manifest:
        if not args.dry_run:
            write_file(args.manifest, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        else:
            print(f"(dry-run) Would write manifest to {args.manifest}")

    if args.dry_run:
        return 0

    ensure_dir(args.out_dir)
    for page, w in winners.items():
        raw = w.get("raw")
        if not isinstance(raw, str):
            continue
        out_path = os.path.join(args.out_dir, f"page_{page:03d}.json")
        write_file(out_path, raw)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

