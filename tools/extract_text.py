#!/usr/bin/env python3
"""
Extract text from the source PDF into:
- extracted/full.txt
- extracted/pages/page_XXX.txt (one file per page)

Uses Poppler's `pdftotext` + `pdfinfo` for reproducible, tool-based extraction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ExtractionResult:
    pdf_path: str
    pages: int
    full_text_path: str
    full_text_sha256: str
    page_dir: str
    page_sha256: dict[str, str]
    tool_versions: dict[str, str]
    commands: dict[str, list[str]]
    created_utc: str


def _run(cmd: list[str], *, combine_stderr: bool = False) -> str:
    """
    Run a command and return its stdout (optionally with stderr merged into stdout).
    Poppler tools (`pdfinfo`, `pdftotext`) often print version info to stderr.
    """
    stderr = subprocess.STDOUT if combine_stderr else subprocess.PIPE
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=stderr, text=True)
    return p.stdout or ""


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _get_pages(pdf_path: Path) -> int:
    out = _run(["pdfinfo", str(pdf_path)])
    m = re.search(r"^Pages:\s+(\d+)\s*$", out, flags=re.MULTILINE)
    if not m:
        raise RuntimeError("Could not determine page count from pdfinfo output.")
    return int(m.group(1))


def _get_version(binary: str) -> str:
    out = ""
    for args in ([binary, "--version"], [binary, "-v"]):
        try:
            out = _run(args, combine_stderr=True).strip()
        except subprocess.CalledProcessError:
            continue
        if out:
            break
    if not out:
        return "unknown"
    return out.splitlines()[0].strip()


def extract(pdf_path: Path, out_dir: Path, *, layout: bool = True) -> ExtractionResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    page_dir = out_dir / "pages"
    page_dir.mkdir(parents=True, exist_ok=True)

    pages = _get_pages(pdf_path)

    full_txt = out_dir / "full.txt"
    base_cmd = ["pdftotext", "-enc", "UTF-8"]
    if layout:
        base_cmd += ["-layout"]

    cmd_full = base_cmd + [str(pdf_path), str(full_txt)]
    subprocess.run(cmd_full, check=True)

    page_hashes: dict[str, str] = {}
    for i in range(1, pages + 1):
        page_txt = page_dir / f"page_{i:03d}.txt"
        cmd_page = base_cmd + ["-f", str(i), "-l", str(i), "-nopgbrk", str(pdf_path), str(page_txt)]
        subprocess.run(cmd_page, check=True)
        page_hashes[f"{i:03d}"] = _sha256_file(page_txt)

    res = ExtractionResult(
        pdf_path=str(pdf_path),
        pages=pages,
        full_text_path=str(full_txt),
        full_text_sha256=_sha256_file(full_txt),
        page_dir=str(page_dir),
        page_sha256=page_hashes,
        tool_versions={
            "pdfinfo": _get_version("pdfinfo"),
            "pdftotext": _get_version("pdftotext"),
            "python": sys.version.split()[0],
        },
        commands={
            "full": cmd_full,
            "per_page_template": base_cmd
            + ["-f", "<n>", "-l", "<n>", "-nopgbrk", str(pdf_path), str(page_dir / "page_<n>.txt")],
        },
        created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract PDF text into extracted/ folder.")
    ap.add_argument("--pdf", default=str(Path(__file__).resolve().parents[1] / "durov_code_book.pdf"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "extracted"))
    ap.add_argument("--no-layout", action="store_true", help="Disable pdftotext -layout.")
    args = ap.parse_args()

    pdf_path = Path(args.pdf).resolve()
    out_dir = Path(args.out).resolve()

    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    res = extract(pdf_path, out_dir, layout=not args.no_layout)
    manifest_path = out_dir / "extraction_manifest.json"
    manifest_path.write_text(json.dumps(asdict(res), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Pages: {res.pages}")
    print(f"Full text: {res.full_text_path}")
    print(f"Full SHA256: {res.full_text_sha256}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

