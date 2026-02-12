#!/usr/bin/env python3
"""
validate_translation.py — Validate translation JSON files.

Checks:
  - Valid JSON
  - Required top-level fields (page, chapter, sentences, etc.)
  - All 4 languages present and non-empty for every sentence
  - Sequential sentence IDs (no gaps)
  - total_sentences matches actual count
  - Page number in filename matches JSON

Synthesized from validation tools across branches 28aa, 64eb, a0cf, c510, e6ed.

Usage:
  python3 tools/validate_translation.py translations/page_013.json
  python3 tools/validate_translation.py translations/*.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Sequence


PAGE_FILE_RE = re.compile(r"page_(\d{3})\.json$")
REQUIRED_LANGS = ("ru", "en", "zh", "ja")
REQUIRED_TOP_FIELDS = ("page", "sentences")
OPTIONAL_TOP_FIELDS = ("chapter", "chapter_title", "translator_notes", "total_sentences", "page_type")


def is_nonempty_str(x: Any) -> bool:
    return isinstance(x, str) and x.strip() != ""


def validate(path: str) -> List[str]:
    """Validate a translation JSON file. Returns list of errors (empty = valid)."""
    errors: List[str] = []

    # Load JSON
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    except Exception as e:
        return [f"cannot read file: {e}"]

    if not isinstance(data, dict):
        return ["top-level JSON must be an object"]

    # Page field
    page = data.get("page")
    if not isinstance(page, int) or page < 1:
        errors.append("field 'page' must be a positive integer")

    # Filename consistency
    m = PAGE_FILE_RE.search(os.path.basename(path))
    if m and isinstance(page, int):
        file_page = int(m.group(1))
        if file_page != page:
            errors.append(f"page mismatch: filename says {file_page}, JSON says {page}")

    # Chapter field (optional but validated if present)
    chapter = data.get("chapter")
    if chapter is not None and (not isinstance(chapter, int) or chapter < 0):
        errors.append("field 'chapter' must be int >= 0 (if present)")

    # Chapter title (optional)
    title = data.get("chapter_title")
    if title is not None and not is_nonempty_str(title):
        errors.append("field 'chapter_title' must be a non-empty string (if present)")

    # Page type (optional)
    ptype = data.get("page_type")
    if ptype is not None and not is_nonempty_str(ptype):
        errors.append("field 'page_type' must be a non-empty string (if present)")

    # Translator notes (optional)
    notes = data.get("translator_notes")
    if notes is not None:
        if not isinstance(notes, list):
            errors.append("field 'translator_notes' must be a list (if present)")
        elif any(not isinstance(x, str) for x in notes):
            errors.append("field 'translator_notes' must contain only strings")

    # Sentences
    sentences = data.get("sentences")
    if not isinstance(sentences, list) or len(sentences) == 0:
        errors.append("field 'sentences' must be a non-empty array")
        return errors

    # total_sentences consistency
    total = data.get("total_sentences")
    if total is not None:
        if not isinstance(total, int):
            errors.append("field 'total_sentences' must be an integer (if present)")
        elif total != len(sentences):
            errors.append(f"total_sentences={total} != actual count={len(sentences)}")

    # Validate each sentence
    expected_id = 1
    for i, s in enumerate(sentences, start=1):
        if not isinstance(s, dict):
            errors.append(f"sentences[{i}] must be an object")
            continue

        # ID check
        sid = s.get("id")
        if isinstance(sid, int):
            if sid != expected_id:
                errors.append(f"sentences[{i}].id = {sid}, expected {expected_id}")
            expected_id = sid + 1
        else:
            errors.append(f"sentences[{i}].id must be an integer")

        # Language checks
        for lang in REQUIRED_LANGS:
            val = s.get(lang)
            if val is None:
                errors.append(f"sentences[{i}] missing field: {lang}")
            elif not is_nonempty_str(val):
                errors.append(f"sentences[{i}].{lang} must be a non-empty string")

    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate translation JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("paths", nargs="+", help="One or more JSON files to validate.")
    ap.add_argument("--strict", action="store_true",
                    help="Require all optional fields (chapter, chapter_title, etc.)")
    args = ap.parse_args(argv)

    ok = True
    for p in args.paths:
        if not os.path.isfile(p):
            print(f"[SKIP] {p} (not a file)", file=sys.stderr)
            continue

        errs = validate(p)

        if args.strict:
            # Check optional fields are present
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for field in OPTIONAL_TOP_FIELDS:
                    if field not in data:
                        errs.append(f"strict mode: missing optional field '{field}'")
            except Exception:
                pass

        if errs:
            ok = False
            print(f"[FAIL] {p}", file=sys.stderr)
            for err in errs:
                print(f"  - {err}", file=sys.stderr)
        else:
            print(f"[OK] {p}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
