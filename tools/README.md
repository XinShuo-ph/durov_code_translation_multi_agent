# Technical Approach Documentation - M1

## Chosen Approach: LaTeX with XeLaTeX

### Decision Rationale

After exploration, **LaTeX with xeCJK** is the optimal approach for this multilingual book project.

**Why LaTeX won:**
1. **Superior typography**: Professional typesetting, especially for mixed scripts
2. **CJK support**: xeCJK package handles Chinese/Japanese beautifully
3. **Color management**: Easy color-coding per language
4. **Font flexibility**: fontspec allows any OpenType/TrueType fonts
5. **Proven technology**: Decades of academic publishing
6. **Scriptable**: Can be automated via Python wrapper

**Why NOT Python (reportlab/fpdf2):**
- CJK support problematic
- Manual layout calculations complex
- Typography quality lower
- More code to maintain

### Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Compiler** | XeLaTeX | Unicode-aware LaTeX compiler |
| **CJK Package** | xeCJK | Chinese/Japanese support |
| **Font Mgmt** | fontspec | Modern font loading |
| **Colors** | xcolor | Language color-coding |
| **Fonts** | Noto family | Universal Unicode coverage |
| **Wrapper** | Python 3 | Automation and JSON→LaTeX |

### Installation Requirements

```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-lang-chinese texlive-lang-japanese \
    fonts-noto-core fonts-noto-cjk

# Python packages (already in requirements.txt)
pip install pdfplumber PyPDF2
```

### Workflow Pipeline

```
1. PDF → Text Extraction
   durov_code_book.pdf → examples/page_XXX_original.txt
   Tool: tools/extract_text.py (pdfplumber)

2. Text → Translation
   page_XXX_original.txt → manual translation → translations/raw/page_XXX.json
   Format: {"page": N, "sentences": [{"ru": "", "en": "", "zh": "", "ja": ""}]}

3. JSON → PDF Compilation
   page_XXX.json → output/page_XXX_translated.pdf
   Tool: tools/compile_pages.py (generates LaTeX, runs xelatex)

4. Quality Review
   - Visual check of PDF
   - Verify all 4 languages render
   - Check colors, fonts, spacing
   - Iterate if needed

5. Final Assembly
   - Merge all page PDFs
   - Add table of contents
   - Generate complete book
```

### File Formats

#### Translation JSON Schema
```json
{
  "page": 13,
  "chapter": 1,
  "chapter_title_ru": "Ботанический сад",
  "chapter_title_en": "Botanical Garden",
  "chapter_title_zh": "植物园",
  "chapter_title_ja": "植物園",
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "中文翻译...",
      "ja": "日本語の翻訳..."
    }
  ],
  "translator_notes": ["Note 1", "Note 2"],
  "research_used": ["Source 1", "Source 2"]
}
```

### LaTeX Template Structure

```latex
% Header: Package loading, font setup, colors
\documentclass[12pt,a4paper]{article}
\usepackage{xeCJK}
\usepackage{fontspec}
\usepackage{color}

% Define colors
\definecolor{russiancolor}{RGB}{0,0,0}    % Black
\definecolor{englishcolor}{RGB}{0,68,153} % Blue
\definecolor{chinesecolor}{RGB}{204,0,0}  % Red
\definecolor{japanesecolor}{RGB}{0,128,0} % Green

% Commands for each language
\newcommand{\ru}[1]{\textcolor{russiancolor}{#1}}
\newcommand{\en}[1]{\textcolor{englishcolor}{#1}}
\newcommand{\zh}[1]{\textcolor{chinesecolor}{#1}}
\newcommand{\ja}[1]{\textcolor{japanesecolor}{#1}}

% Body: Sentence blocks
\ru{Russian sentence}
\en{English sentence}
\zh{中文句子}
\ja{日本語の文}
```

### Demo Results

✓ **Page 13 Demo**: 53KB PDF, 3 sentences, all languages rendered
✓ **Page 43 Demo**: 50KB PDF, 3 sentences, all languages rendered

Both demos successfully demonstrate:
- Color-coded languages
- CJK character rendering
- Translator notes section
- Professional layout

### Performance Metrics

| Metric | Value |
|--------|-------|
| Compilation time | ~3-5 seconds per page |
| PDF size | ~50-60KB per page (text-based) |
| Render quality | Professional, publication-ready |
| Font coverage | 100% (Noto covers all needed characters) |

### Known Limitations & Solutions

1. **LaTeX special characters**: 
   - Problem: `&`, `%`, `$`, `#`, `_`, `{`, `}` break compilation
   - Solution: Python escape function in compile_pages.py

2. **Long compilation**:
   - Problem: 99 pages × 5 seconds = 8+ minutes total
   - Solution: Parallel compilation possible, batch processing

3. **Memory for full book**:
   - Problem: Single LaTeX file for 99 pages might be large
   - Solution: Compile individually, merge PDFs at end

### Verification Checklist

For M1 completion, each worker should verify:
- [ ] XeLaTeX installed and working
- [ ] Can compile demo templates
- [ ] All 4 languages render correctly
- [ ] Colors display as specified
- [ ] Fonts load (Noto family)
- [ ] compile_pages.py script works
- [ ] JSON→PDF pipeline functional

### M1 Exit Criteria Met

✓ M1.1: LaTeX approach explored and working
✓ M1.2: Python alternative considered (rejected for CJK issues)
✓ M1.3: Color/font scheme designed and documented
✓ M1.4: Demo template created (format_demo.tex + compile_pages.py)
✓ M1.5: Page 13 demo translated and compiled
✓ M1.6: Page 43 demo translated and compiled
✓ M1.7: Technical approach documented (this file)

### Consensus Vote

**format_approach = latex_xecjk**

Rationale: Best balance of typography quality, CJK support, automation potential, and proven reliability.

### Next Steps (M2)

With M1 complete, workers can proceed to M2:
1. Claim pages dynamically (lowest available)
2. Research context for assigned page
3. Translate sentence-by-sentence (all 4 languages)
4. Review 3 times
5. Compile to PDF using tools/compile_pages.py
6. Commit to repository
7. Claim next page

---

**Document Hash**: For cross-verification
**Generated**: 2026-01-01
**Status**: M1 Complete, Ready for M2
