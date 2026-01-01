#!/usr/bin/env python3
"""
Extract per-page and fulltext from the source PDF.

Preferred backend: `pdftotext` (poppler-utils) for stable, layout-preserving output.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def get_page_count(pdf_path: Path) -> int:
    # Prefer pdfinfo if present (part of poppler-utils).
    try:
        out = subprocess.check_output(["pdfinfo", str(pdf_path)], text=True)
        for line in out.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    # Fallback: project-known page count
    return 99


def extract_page(pdf_path: Path, page: int, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "pdftotext",
            "-f",
            str(page),
            "-l",
            str(page),
            "-layout",
            "-enc",
            "UTF-8",
            str(pdf_path),
            str(out_path),
        ]
    )

def extract_full_consensus(pdf_path: Path, out_path: Path) -> str:
    """
    Consensus (cross-worker) extraction format:
    `pdftotext -layout <pdf> <out>`

    This matches the hash most workers are using for M0.2.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _run(["pdftotext", "-layout", str(pdf_path), str(out_path)])
    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path("durov_code_book.pdf"),
        help="Path to the source PDF",
    )
    parser.add_argument(
        "--consensus-out",
        type=Path,
        default=Path("durov_code_book_extracted.txt"),
        help="Path for consensus full-text extraction (M0.2)",
    )
    parser.add_argument(
        "--also-per-page",
        action="store_true",
        help="Additionally extract per-page text and a concatenated file with page separators",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("extracted/pages"),
        help="Directory for per-page text outputs",
    )
    parser.add_argument(
        "--full-out",
        type=Path,
        default=Path("extracted/durov_code_book_full.txt"),
        help="Path for concatenated full text output",
    )
    args = parser.parse_args()

    pdf_path = args.pdf
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    consensus_hash = extract_full_consensus(pdf_path, args.consensus_out)
    print("Consensus extraction (M0.2):")
    print(f"- Output: {args.consensus_out}")
    print(f"- SHA256: {consensus_hash}")

    if args.also_per_page:
        pages = get_page_count(pdf_path)

        # Extract per-page
        per_page_paths: list[Path] = []
        for page in range(1, pages + 1):
            out_path = args.out_dir / f"page_{page:03d}.txt"
            extract_page(pdf_path, page, out_path)
            per_page_paths.append(out_path)

        # Concatenate into one file with stable separators (helpful for later parsing)
        args.full_out.parent.mkdir(parents=True, exist_ok=True)
        with args.full_out.open("w", encoding="utf-8") as f:
            for page, p in enumerate(per_page_paths, start=1):
                f.write(f"\n\n===== PAGE {page:03d} =====\n\n")
                f.write(p.read_text(encoding="utf-8", errors="replace"))

        print(f"\nExtra outputs (optional):")
        print(f"- Per-page: {args.out_dir}")
        print(f"- Fulltext with page separators: {args.full_out}")


if __name__ == "__main__":
    main()

