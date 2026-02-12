#!/usr/bin/env python3
"""
Validate a page translation JSON for required structure and completeness.

Usage:
  python3 tools/validate_translation.py translations/raw/page_013.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def fail(msg: str) -> int:
    print(f"VALIDATION_FAILED: {msg}", file=sys.stderr)
    return 2


def validate(path: Path) -> int:
    if not path.exists():
        return fail(f"file does not exist: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return fail(f"invalid JSON: {e}")

    if not isinstance(data, dict):
        return fail("top-level JSON must be an object")

    required_top = ["page", "chapter", "chapter_title", "sentences", "translator_notes", "total_sentences", "page_type"]
    for k in required_top:
        if k not in data:
            return fail(f"missing required field: {k}")

    if not isinstance(data["page"], int) or data["page"] <= 0:
        return fail("field 'page' must be a positive int")

    if not isinstance(data["chapter"], int) or data["chapter"] < 0:
        return fail("field 'chapter' must be an int >= 0")

    if not isinstance(data["chapter_title"], str) or not data["chapter_title"].strip():
        return fail("field 'chapter_title' must be a non-empty string")

    if not isinstance(data["page_type"], str) or not data["page_type"].strip():
        return fail("field 'page_type' must be a non-empty string")

    if not isinstance(data["translator_notes"], list):
        return fail("field 'translator_notes' must be a list (can be empty)")
    if any(not isinstance(x, str) for x in data["translator_notes"]):
        return fail("field 'translator_notes' must contain only strings")

    sentences = data["sentences"]
    if not isinstance(sentences, list) or not sentences:
        return fail("field 'sentences' must be a non-empty list")

    if not isinstance(data["total_sentences"], int):
        return fail("field 'total_sentences' must be an int")
    if data["total_sentences"] != len(sentences):
        return fail(f"'total_sentences'={data['total_sentences']} does not match len(sentences)={len(sentences)}")

    expected_id = 1
    for i, s in enumerate(sentences, start=1):
        if not isinstance(s, dict):
            return fail(f"sentence[{i}] must be an object")

        for k in ["id", "ru", "en", "zh", "ja"]:
            if k not in s:
                return fail(f"sentence[{i}] missing field: {k}")

        if s["id"] != expected_id:
            return fail(f"sentence[{i}] id must be {expected_id}, got {s['id']!r}")
        expected_id += 1

        for lang in ["ru", "en", "zh", "ja"]:
            v = s.get(lang)
            if not isinstance(v, str) or not v.strip():
                return fail(f"sentence[{i}] '{lang}' must be a non-empty string")

    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="validate_translation.py")
    ap.add_argument("json_path", type=Path)
    ns = ap.parse_args(argv)
    rc = validate(ns.json_path)
    if rc == 0:
        print("OK")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

