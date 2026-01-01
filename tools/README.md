# Translation Tools

## Overview
This directory contains tools for extracting text from the source PDF and compiling translated pages into multilingual PDFs.

## Dependencies
- Python 3
- `reportlab`
- `pdfminer.six` (for extraction, or `pdftotext`)
- `PyPDF2`
- Fonts: `DroidSansFallbackFull.ttf` (usually found in `fonts-droid-fallback` package) or similar CJK-supporting font.

## Scripts

### `extract_text.py`
Extracts full text from `durov_code_book.pdf` to `durov_code_book.txt`.
Usage: `python3 tools/extract_text.py`

### `compile_pages.py`
Compiles a JSON translation file into a PDF.
Usage: `python3 tools/compile_pages.py <input_json> <output_pdf>`

## JSON Format
The input JSON for `compile_pages.py` should follow this structure:
```json
{
  "page": 13,
  "chapter": 1,
  "sentences": [
    {
      "id": 1,
      "ru": "Original Russian text...",
      "en": "English translation...",
      "zh": "Chinese translation...",
      "ja": "Japanese translation..."
    }
  ],
  "translator_notes": ["Notes..."],
  "research_used": ["Sources..."]
}
```

## Approach
We use Python's `reportlab` library to generate PDFs programmatically. This allows precise control over layout and font handling, which is crucial for mixing Cyrillic, Latin, and CJK characters. We use `DroidSansFallbackFull.ttf` as a universal font that covers all required scripts.
