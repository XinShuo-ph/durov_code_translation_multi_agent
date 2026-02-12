#!/usr/bin/env python3
"""
validate_translation.py - validate a single translations/page_XXX.json file.

This is a pragmatic validator used as a guardrail for multi-agent work.
It checks:
- JSON parses
- required top-level fields exist
- sentences are a list of objects containing ru/en/zh/ja strings (non-empty after strip)
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List


REQUIRED_SENTENCE_FIELDS = ("ru", "en", "zh", "ja")


def _err(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)


def validate(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        _err(f"File not found: {path}")
        return 2
    except json.JSONDecodeError as e:
        _err(f"Invalid JSON: {e}")
        return 3

    if not isinstance(data, dict):
        _err("Top-level JSON must be an object")
        return 4

    page = data.get("page")
    if not isinstance(page, int) or page < 1:
        _err("Field `page` must be a positive integer")
        return 5

    sentences = data.get("sentences")
    if not isinstance(sentences, list) or not sentences:
        _err("Field `sentences` must be a non-empty list")
        return 6

    for idx, s in enumerate(sentences, start=1):
        if not isinstance(s, dict):
            _err(f"sentences[{idx}] must be an object")
            return 7
        for k in REQUIRED_SENTENCE_FIELDS:
            v = s.get(k)
            if not isinstance(v, str) or not v.strip():
                _err(f"sentences[{idx}].{k} must be a non-empty string")
                return 8

    total_sentences = data.get("total_sentences")
    if total_sentences is not None:
        if not isinstance(total_sentences, int) or total_sentences != len(sentences):
            _err("Field `total_sentences`, if present, must equal len(sentences)")
            return 9

    return 0


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate a translation JSON file.")
    ap.add_argument("path", help="Path to translations/page_XXX.json")
    args = ap.parse_args(argv)
    rc = validate(args.path)
    if rc == 0:
        print("OK")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

