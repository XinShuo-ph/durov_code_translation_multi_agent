#!/usr/bin/env python3
"""
PDF Text Extraction Script for Durov Code Book
Extracts text from each page of the PDF for translation.
"""

import subprocess
import os
import json
import hashlib

def extract_page(pdf_path, page_num, output_dir="translations/raw"):
    """Extract text from a single page using pdftotext."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"page_{page_num:03d}_ru.txt")
    
    # Use pdftotext with -f and -l for first and last page
    cmd = [
        "pdftotext",
        "-f", str(page_num),
        "-l", str(page_num),
        "-layout",
        pdf_path,
        output_file
    ]
    
    subprocess.run(cmd, check=True)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    return text

def extract_all_pages(pdf_path, num_pages=99, output_dir="translations/raw"):
    """Extract text from all pages."""
    os.makedirs(output_dir, exist_ok=True)
    
    for page_num in range(1, num_pages + 1):
        print(f"Extracting page {page_num}...")
        extract_page(pdf_path, page_num, output_dir)
    
    print(f"Extracted {num_pages} pages to {output_dir}")

def get_text_hash(text):
    """Get SHA256 hash of text (first 8 chars)."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:8]

if __name__ == "__main__":
    import sys
    
    pdf_path = "/workspace/durov_code_book.pdf"
    output_dir = "/workspace/translations/raw"
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            extract_all_pages(pdf_path, 99, output_dir)
        else:
            page_num = int(sys.argv[1])
            text = extract_page(pdf_path, page_num, output_dir)
            print(f"Page {page_num} extracted ({len(text)} chars)")
            print(f"Hash: {get_text_hash(text)}")
    else:
        print("Usage: python extract_text.py [page_num | --all]")
        print("  page_num: Extract single page")
        print("  --all: Extract all 99 pages")
