# Translation Tools Documentation

## Overview
This directory contains tools for the Durov Code multilingual translation project.

---

## Technical Approach

### Primary Method: LaTeX/XeLaTeX
We use XeLaTeX with xeCJK for generating multilingual PDFs.

**Advantages:**
- Professional typographic quality
- Excellent CJK (Chinese/Japanese/Korean) support
- Color and font control
- Consistent page layout
- PDF/A compatibility

**Requirements:**
- texlive-xetex
- texlive-lang-cjk
- texlive-lang-cyrillic
- texlive-fonts-extra

### Fallback Method: Python (fpdf2/reportlab)
Python-based PDF generation for environments without LaTeX.

**Advantages:**
- No LaTeX installation needed
- Simpler deployment
- Programmatic control

**Limitations:**
- Less typographic quality
- CJK font handling more complex

---

## Color Scheme

| Language | Color | RGB | Hex |
|----------|-------|-----|-----|
| Russian (Original) | Black | (0, 0, 0) | #000000 |
| English | Blue | (0, 82, 147) | #005293 |
| Chinese | Brown | (139, 69, 19) | #8B4513 |
| Japanese | Green | (0, 100, 0) | #006400 |

---

## File Structure

```
tools/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── extract_text.py     # PDF text extraction
├── compile_pages.py    # Page compilation to PDF
└── full_text.txt       # Extracted full text (generated)

examples/
├── format_demo.tex     # LaTeX template
└── format_demo.pdf     # Compiled demo

translations/
├── raw/                # First-pass translations
│   ├── page_NNN.json   # Translation data
│   └── page_NNN_ru.txt # Extracted Russian text
├── reviewed/           # After proofreading
└── final/              # After 3x review cycles
```

---

## Translation JSON Format

Each translated page is stored as JSON:

```json
{
  "page": 13,
  "chapter": 1,
  "chapter_title": {
    "ru": "Ботанический сад",
    "en": "Botanical Garden",
    "zh": "植物园",
    "ja": "植物園"
  },
  "sentences": [
    {
      "id": 1,
      "ru": "Russian original text...",
      "en": "English translation...",
      "zh": "Chinese translation...",
      "ja": "Japanese translation..."
    }
  ],
  "translator_notes": [
    "Cultural note 1",
    "Term explanation 2"
  ],
  "research_used": [
    "Research topic 1"
  ]
}
```

---

## Usage

### Extract Text from PDF
```bash
# Extract full text
python tools/extract_text.py

# Extract all pages individually
python tools/extract_text.py --all
```

### Compile Pages to PDF
```bash
# Compile single page
python tools/compile_pages.py --page 13

# Compile all available pages
python tools/compile_pages.py --all

# Force specific method
python tools/compile_pages.py --page 13 --method latex
python tools/compile_pages.py --page 13 --method python
```

### Compile LaTeX Demo Directly
```bash
cd examples
xelatex format_demo.tex
```

---

## Font Requirements

### System Fonts Needed
- DejaVu Serif/Sans/Mono (Latin/Cyrillic)
- Noto Serif CJK SC (Chinese Simplified)
- Noto Serif CJK JP (Japanese)

### Installing Fonts (Ubuntu/Debian)
```bash
sudo apt-get install fonts-dejavu fonts-noto-cjk
```

---

## Quality Checklist

Before marking a page as complete:

1. **Text Accuracy**
   - [ ] All sentences translated
   - [ ] No sentences skipped or merged incorrectly
   - [ ] Russian original matches PDF extraction

2. **Translation Quality**
   - [ ] Natural flow in target language
   - [ ] Durov's voice preserved (sharp, provocative)
   - [ ] Cultural references adapted appropriately

3. **Technical Quality**
   - [ ] PDF compiles without errors
   - [ ] All languages display correctly
   - [ ] Fonts render properly

4. **Consistency**
   - [ ] Terminology matches glossary
   - [ ] Names transliterated consistently
   - [ ] Format matches template

---

## Consensus Decision: LaTeX Approach

**Decision**: Use LaTeX/XeLaTeX as primary compilation method.

**Rationale**:
1. Superior CJK handling with xeCJK package
2. Professional typographic quality
3. Better control over multilingual layout
4. Widely available on Linux systems

**Fallback**: Python fpdf2 for emergency use only.

---

## Hashes for Verification

| File | SHA256 (first 8) |
|------|------------------|
| format_demo.pdf | 809cef5e |
| format_demo.tex | (compute at verification) |

---

*Last updated: 2026-01-01*
*Part of Durov Code Translation Project*
