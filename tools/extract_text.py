#!/usr/bin/env python3
"""
PDF Text Extraction Script for Durov Code Translation Project

This script extracts text from the PDF for translation purposes.
It can extract full text or per-page text.
"""

import subprocess
import os
import sys
import hashlib

def extract_full_text(pdf_path: str, output_path: str) -> str:
    """Extract full text from PDF using pdftotext."""
    cmd = ['pdftotext', '-layout', pdf_path, output_path]
    subprocess.run(cmd, check=True)
    
    with open(output_path, 'rb') as f:
        content = f.read()
    return hashlib.sha256(content).hexdigest()[:8]

def extract_page(pdf_path: str, page_num: int, output_dir: str) -> str:
    """Extract a single page from PDF."""
    output_path = os.path.join(output_dir, f'page_{page_num:03d}_ru.txt')
    cmd = ['pdftotext', '-f', str(page_num), '-l', str(page_num), 
           '-layout', pdf_path, output_path]
    subprocess.run(cmd, check=True)
    
    with open(output_path, 'rb') as f:
        content = f.read()
    return hashlib.sha256(content).hexdigest()[:8]

def extract_all_pages(pdf_path: str, output_dir: str, total_pages: int = 99):
    """Extract all pages from PDF."""
    os.makedirs(output_dir, exist_ok=True)
    hashes = {}
    for i in range(1, total_pages + 1):
        h = extract_page(pdf_path, i, output_dir)
        hashes[i] = h
        print(f"Page {i:03d}: {h}")
    return hashes

if __name__ == '__main__':
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(workspace, 'durov_code_book.pdf')
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Extract all pages
        output_dir = os.path.join(workspace, 'translations', 'raw')
        hashes = extract_all_pages(pdf_path, output_dir)
        print(f"\nExtracted {len(hashes)} pages")
    else:
        # Extract full text
        output_path = os.path.join(workspace, 'tools', 'full_text.txt')
        h = extract_full_text(pdf_path, output_path)
        print(f"Full text extracted to {output_path}")
        print(f"Hash: {h}")
