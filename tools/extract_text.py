#!/usr/bin/env python3
"""
PDF text extraction helper.

Primary strategy: call `pdftotext` (Poppler) for deterministic extraction.
This avoids PDF parsing variability across Python libraries.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_pdftotext(pdf_path: Path, out_path: Path, encoding: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftotext", "-enc", encoding, str(pdf_path), str(out_path)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text from a PDF using pdftotext.")
    parser.add_argument("--pdf", type=Path, default=Path("durov_code_book.pdf"))
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("tools/extracted/durov_code_book.txt"),
        help="Output .txt path",
    )
    parser.add_argument("--encoding", default="UTF-8")
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    run_pdftotext(args.pdf, args.out, args.encoding)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

