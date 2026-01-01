#!/usr/bin/env python3
"""
Extract text from durov_code_book.pdf using poppler's pdftotext.

Outputs a UTF-8 text file suitable for downstream per-page splitting and translation.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_pdftotext(pdf_path: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "pdftotext",
            "-layout",
            "-enc",
            "UTF-8",
            str(pdf_path),
            str(out_path),
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path("durov_code_book.pdf"),
        help="Input PDF path (default: durov_code_book.pdf)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("research/durov_code_book_ru.txt"),
        help="Output text path (default: research/durov_code_book_ru.txt)",
    )
    args = parser.parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"PDF not found: {args.pdf}")

    run_pdftotext(args.pdf, args.out)
    digest = sha256_file(args.out)
    print(f"Wrote: {args.out}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

