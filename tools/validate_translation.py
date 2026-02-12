#!/usr/bin/env python3
"""
validate_translation.py — basic schema + consistency checks for page JSONs.

Usage:
  python3 tools/validate_translation.py translations/page_013.json
  python3 tools/validate_translation.py translations/page_*.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Sequence, Tuple


PAGE_FROM_FILENAME_RE = re.compile(r"page_(\d{3})\.json$")


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"WARN: {msg}", file=sys.stderr)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def validate_sentence(sentence: Dict[str, Any], idx: int) -> None:
    require(isinstance(sentence, dict), f"sentences[{idx}] must be an object")
    for k in ["id", "ru", "en", "zh", "ja"]:
        require(k in sentence, f"sentences[{idx}] missing key '{k}'")
    require(isinstance(sentence["id"], int), f"sentences[{idx}].id must be int")
    for k in ["ru", "en", "zh", "ja"]:
        require(isinstance(sentence[k], str), f"sentences[{idx}].{k} must be string")
        require(sentence[k].strip() != "", f"sentences[{idx}].{k} must be non-empty")


def validate_page(path: str, data: Dict[str, Any]) -> None:
    require("page" in data and isinstance(data["page"], int), f"{path}: missing/int 'page'")
    require("sentences" in data and isinstance(data["sentences"], list), f"{path}: missing/list 'sentences'")

    m = PAGE_FROM_FILENAME_RE.search(os.path.basename(path))
    if m:
        fn_page = int(m.group(1))
        require(data["page"] == fn_page, f"{path}: page={data['page']} does not match filename page_{fn_page:03d}.json")
    else:
        warn(f"{path}: filename does not match page_XXX.json; skipping filename-page check")

    sentences: List[Dict[str, Any]] = data["sentences"]
    for i, s in enumerate(sentences):
        validate_sentence(s, i)

    # IDs should be 1..N sequential
    ids = [s["id"] for s in sentences]
    require(ids == list(range(1, len(sentences) + 1)), f"{path}: sentence ids must be 1..N sequential (got {ids[:10]}...)")

    if "total_sentences" in data:
        require(isinstance(data["total_sentences"], int), f"{path}: total_sentences must be int")
        require(data["total_sentences"] == len(sentences), f"{path}: total_sentences={data['total_sentences']} != len(sentences)={len(sentences)}")
    else:
        warn(f"{path}: missing total_sentences (recommended)")

    # Optional fields type checks
    if "translator_notes" in data:
        require(isinstance(data["translator_notes"], list), f"{path}: translator_notes must be list")


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate translation JSON files.")
    ap.add_argument("paths", nargs="+", help="One or more JSON paths.")
    args = ap.parse_args(list(argv))

    ok = True
    for path in args.paths:
        try:
            data = load_json(path)
            validate_page(path, data)
        except Exception as e:
            ok = False
            err(f"{path}: {e}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

