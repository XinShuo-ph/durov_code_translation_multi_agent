#!/usr/bin/env python3
"""
Extract text from Durov Code PDF book.
Extracts both full text and per-page text for translation workflow.
"""

import sys
import pdfplumber
from pathlib import Path

def extract_full_text(pdf_path, output_path):
    """Extract all text from PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = []
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                full_text.append(f"=== PAGE {i} ===\n{text}\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(full_text))
        
        return len(pdf.pages)

def extract_page_text(pdf_path, page_num, output_dir):
    """Extract text from specific page"""
    with pdfplumber.open(pdf_path) as pdf:
        if 1 <= page_num <= len(pdf.pages):
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            
            output_file = Path(output_dir) / f"page_{page_num:03d}_original.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text if text else "")
            
            return True
    return False

def extract_all_pages(pdf_path, output_dir):
    """Extract text from all pages individually"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            output_file = Path(output_dir) / f"page_{i:03d}_original.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text if text else "")
        
        return len(pdf.pages)

if __name__ == '__main__':
    pdf_path = 'durov_code_book.pdf'
    
    print(f"Extracting text from {pdf_path}...")
    
    # Extract full text
    num_pages = extract_full_text(pdf_path, 'durov_code_full_text.txt')
    print(f"✓ Extracted full text: {num_pages} pages")
    
    # Extract individual pages
    pages_extracted = extract_all_pages(pdf_path, 'examples')
    print(f"✓ Extracted individual pages: {pages_extracted} files")
    
    print("Done!")
