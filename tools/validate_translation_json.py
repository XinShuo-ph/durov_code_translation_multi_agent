#!/usr/bin/env python3
"""
validate_translation_json.py

Quick validator for translation JSON files.

Goal: prevent the most common failure modes:
  - invalid JSON
  - missing required fields
  - empty translations for en/zh/ja
  - total_sentences mismatch
  - filename page number mismatch
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Sequence


PAGE_FILE_RE = re.compile(r"page_(\d{3})\.json$")


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_nonempty_str(x: Any) -> bool:
    return isinstance(x, str) and x.strip() != ""


def validate(path: str) -> List[str]:
    errors: List[str] = []
    try:
        data = load_json(path)
    except Exception as ex:
        return [f"invalid JSON: {ex}"]

    if not isinstance(data, dict):
        return ["top-level JSON must be an object"]

    # page
    page = data.get("page")
    if not isinstance(page, int) or page < 1:
        errors.append("missing/invalid field: page (must be int >= 1)")

    # filename consistency
    m = PAGE_FILE_RE.search(os.path.basename(path))
    if m and isinstance(page, int):
        file_page = int(m.group(1))
        if file_page != page:
            errors.append(f"page mismatch: filename says {file_page}, JSON says {page}")

    # sentences
    sentences = data.get("sentences")
    if not isinstance(sentences, list) or len(sentences) == 0:
        errors.append("missing/invalid field: sentences (must be non-empty array)")
        return errors

    # validate each sentence
    required_lang_keys = ("ru", "en", "zh", "ja")
    for i, s in enumerate(sentences, start=1):
        if not isinstance(s, dict):
            errors.append(f"sentences[{i}] must be an object")
            continue
        sid = s.get("id")
        if not isinstance(sid, int) or sid < 1:
            errors.append(f"sentences[{i}].id must be int >= 1")
        for k in required_lang_keys:
            if k not in s:
                errors.append(f"sentences[{i}] missing key: {k}")
                continue
            if not is_nonempty_str(s.get(k)):
                errors.append(f"sentences[{i}].{k} must be non-empty string")

    # total_sentences consistency (if present)
    total_sentences = data.get("total_sentences")
    if total_sentences is not None:
        if not isinstance(total_sentences, int) or total_sentences < 0:
            errors.append("total_sentences must be int >= 0 (if present)")
        elif isinstance(sentences, list) and total_sentences != len(sentences):
            errors.append(f"total_sentences mismatch: {total_sentences} != len(sentences) {len(sentences)}")

    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Validate translation JSON files.")
    ap.add_argument("paths", nargs="+", help="One or more JSON files to validate.")
    args = ap.parse_args(argv)

    ok = True
    for p in args.paths:
        errs = validate(p)
        if errs:
            ok = False
            eprint(f"[FAIL] {p}")
            for er in errs:
                eprint(f"  - {er}")
        else:
            print(f"[OK] {p}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

