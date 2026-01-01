#!/usr/bin/env python3
"""
Extract text from PDF pages for the Durov Code translation project.
"""

import sys
import subprocess
from pathlib import Path

def extract_pdf_text(pdf_path, output_dir):
    """Extract text from PDF using pdftotext."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract all text to a single file
    full_text_path = output_dir / "full_text.txt"
    subprocess.run(
        ["pdftotext", "-enc", "UTF-8", str(pdf_path), str(full_text_path)],
        check=True
    )
    
    # Extract text page by page
    for page_num in range(1, 100):  # 99 pages
        page_path = output_dir / f"page_{page_num:03d}.txt"
        subprocess.run(
            ["pdftotext", "-f", str(page_num), "-l", str(page_num), 
             "-enc", "UTF-8", str(pdf_path), str(page_path)],
            check=True
        )
    
    print(f"Extracted text from {pdf_path.name}")
    print(f"Full text: {full_text_path}")
    print(f"Individual pages: {output_dir}/page_*.txt")
    
    return full_text_path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <pdf_path> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    extract_pdf_text(pdf_path, output_dir)
