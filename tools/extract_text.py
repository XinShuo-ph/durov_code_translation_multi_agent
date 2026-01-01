#!/usr/bin/env python3
"""
Extract text from PDF page by page.
Uses pdfplumber for better Russian text extraction.
"""

import sys
import pdfplumber
import json
from pathlib import Path

def extract_pdf_text(pdf_path, output_dir):
    """Extract text from each page of the PDF."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pages_data = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")
        
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                pages_data[i] = text.strip()
                
                # Save individual page
                page_file = output_dir / f"page_{i:03d}_original.txt"
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(text.strip())
                
                print(f"Extracted page {i}/{total_pages}")
            else:
                print(f"Warning: No text found on page {i}")
    
    # Save complete extraction as JSON
    full_json = output_dir / "full_text_extraction.json"
    with open(full_json, 'w', encoding='utf-8') as f:
        json.dump(pages_data, f, ensure_ascii=False, indent=2)
    
    return pages_data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 extract_text.py <pdf_path> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    pages = extract_pdf_text(pdf_path, output_dir)
    print(f"\nExtraction complete: {len(pages)} pages extracted")
