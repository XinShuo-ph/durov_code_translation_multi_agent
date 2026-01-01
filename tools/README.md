# Translation Tools

## Overview
This directory contains tools for the Durov Code Book translation project. We use Python with reportlab for PDF generation, as it provides reliable CJK (Chinese, Japanese, Korean) font support.

## Approach Decision
After evaluation by multiple workers, the consensus is to use **Python/reportlab** for PDF generation:
- LaTeX/xelatex works but requires more complex font configuration
- reportlab provides simpler, more portable solution
- DroidSansFallbackFull font covers all required scripts (Cyrillic, Latin, CJK)

## Color Scheme
- **Russian (RU)**: Black
- **English (EN)**: Dark Blue
- **Chinese (ZH)**: Dark Red
- **Japanese (JA)**: Dark Green

## Dependencies
Install with: `pip install reportlab`

System fonts needed:
- `fonts-droid-fallback` package (Ubuntu/Debian)
- Or any CJK-supporting font like Noto Sans CJK

## Scripts

### `compile_pages.py`
Compiles a JSON translation file into a multilingual PDF.

**Usage:**
```bash
python3 tools/compile_pages.py <input_json> <output_pdf>
```

**Example:**
```bash
python3 tools/compile_pages.py translations/raw/page_013.json examples/page_13_translated.pdf
```

### `extract_text.py`
Extracts text from the source PDF (alternative to pdftotext).

**Usage:**
```bash
python3 tools/extract_text.py
```

## JSON Translation Format
Each page translation should be a JSON file with this structure:

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
  "translator_notes": ["Notes about cultural context, word choices, etc."],
  "research_used": ["Sources consulted for this page"]
}
```

## Workflow
1. Extract Russian text from PDF page
2. Create JSON file with sentence-by-sentence translations
3. Review translations (3 passes as per instructions)
4. Run `compile_pages.py` to generate PDF
5. Verify PDF renders correctly with all languages

## Quality Checklist
- [ ] All sentences translated to 4 languages
- [ ] Cultural references explained in translator_notes
- [ ] Terminology consistent with glossary.md
- [ ] PDF renders correctly with proper fonts
- [ ] No awkward phrasing (3 review passes complete)

## File Locations
- Input JSONs: `translations/raw/page_XXX.json`
- Reviewed JSONs: `translations/reviewed/page_XXX.json`
- Final JSONs: `translations/final/page_XXX.json`
- Output PDFs: `output/page_XXX_translated.pdf`

---
*Last updated: 2026-01-01 by worker c68e*
