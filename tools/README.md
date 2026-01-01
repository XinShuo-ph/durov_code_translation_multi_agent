# Translation Tools Documentation

## Overview
This directory contains tools for the Durov Code Book translation project.
The chosen approach is **Python with PyMuPDF** for PDF generation.

## Format Decision

### Evaluated Options
1. **LaTeX (xelatex + xeCJK)** - Not available in this environment
2. **Python (fpdf2)** - Issues with CJK font handling
3. **Python (PyMuPDF/fitz)** - ✅ **Selected** - Best CJK support, built-in fonts

### Why PyMuPDF?
- Built-in CJK font support (`china-s`, `japan` font families)
- No external font installation required
- Good text positioning and layout control
- Reliable multi-page document handling
- Fast compilation

## Tools

### extract_text.py
Extracts Russian text from the source PDF.

```bash
# Extract single page
python3 tools/extract_text.py 13

# Extract all pages
python3 tools/extract_text.py --all
```

**Output**: `translations/raw/page_XXX_ru.txt`

### compile_pages.py
Compiles multilingual translations to PDF.

```bash
# Test with sample sentences
python3 tools/compile_pages.py --test

# Compile a specific page (requires JSON)
python3 tools/compile_pages.py 13
```

**Input**: `translations/raw/page_XXX.json` or `translations/final/page_XXX.json`
**Output**: `output/page_XXX_translated.pdf`

## Color Scheme

| Language | Color | RGB |
|----------|-------|-----|
| Russian (original) | Black | (0, 0, 0) |
| English | Blue | (0, 102, 204) |
| Chinese | Green | (0, 153, 51) |
| Japanese | Purple | (153, 0, 153) |

## Translation JSON Format

```json
{
  "page": 13,
  "chapter": "Глава 1 - Ботанический сад",
  "sentences": [
    {
      "id": 1,
      "ru": "Russian original text...",
      "en": "English translation...",
      "zh": "Chinese translation...",
      "ja": "Japanese translation..."
    }
  ],
  "translator_notes": ["Note about cultural reference..."],
  "research_used": ["Source 1", "Source 2"]
}
```

## Page Layout

Each translated page contains:
1. **Header**: Book title and page number
2. **Chapter title**: If applicable
3. **Sentences**: Each sentence in 4 languages with color-coded labels
4. **Separator lines**: Between sentence blocks
5. **Footer**: Color legend

## Dependencies

Install with:
```bash
pip install -r requirements.txt
```

Required packages:
- PyMuPDF (fitz)
- pdfminer.six (for text extraction)

## Multi-Agent Workflow

1. **Claim a page** (M2 protocol)
2. **Extract Russian text**: Already done for all pages in `translations/raw/`
3. **Translate**: Create JSON with all 4 languages
4. **Compile**: Run `compile_pages.py` to generate PDF
5. **Verify**: Check output renders correctly
6. **Commit**: Push translation JSON and PDF

## Demo Files

- `examples/page_013_demo.pdf` - Chapter 1 opening (childhood scene)
- `examples/page_043_demo.pdf` - Chapter 3 (VK vs moifakultet controversy)

## Verification

To verify a translation compiles correctly:
```bash
python3 tools/compile_pages.py --test
ls -la examples/
```

---
*Created by worker e545 during M1 phase*
*Last updated: 2026-01-01*
