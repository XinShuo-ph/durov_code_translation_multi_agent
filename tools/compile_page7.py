#!/usr/bin/env python3
"""Compile page 7 translation to PDF."""

import json
import sys
sys.path.insert(0, '/workspace/tools')
from compile_pages import create_page_pdf
from pathlib import Path

def main():
    json_path = Path("/workspace/translations/raw/page_007.json")
    output_path = Path("/workspace/output/page_007_translated.pdf")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        page_data = json.load(f)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    create_page_pdf(page_data, output_path)
    print(f"Compiled: {output_path}")
    
    # Calculate hash
    import hashlib
    with open(output_path, 'rb') as f:
        pdf_hash = hashlib.sha256(f.read()).hexdigest()[:8]
    print(f"PDF Hash: {pdf_hash}")
    
    with open(json_path, 'rb') as f:
        json_hash = hashlib.sha256(f.read()).hexdigest()[:8]
    print(f"JSON Hash: {json_hash}")

if __name__ == "__main__":
    main()
