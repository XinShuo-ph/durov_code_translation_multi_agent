# Technical Approach Documentation

## M1 Decision: LaTeX with XeTeX and xeCJK

### Chosen Approach: **LaTeX (xelatex + xeCJK)**

After exploration, we have selected **LaTeX with XeTeX and xeCJK** as the technical approach for generating multilingual PDFs.

## Rationale

### Why LaTeX?
1. **Professional Typography**: LaTeX provides superior typography for academic/book publishing
2. **CJK Support**: xeCJK package handles Chinese, Japanese, Korean characters excellently
3. **Color Management**: Easy to define and apply colors for different languages
4. **Scalability**: Can generate 99 pages consistently with same formatting
5. **Version Control**: Source `.tex` files are plain text, git-friendly

### Why NOT Python (reportlab/fpdf2)?
- More complex to achieve professional typography
- CJK font handling more difficult
- Would require more custom code for layout
- LaTeX is industry standard for this type of work

## Technical Stack

### Core Components
- **XeTeX**: Modern TeX engine with Unicode and OpenType font support
- **xeCJK**: CJK (Chinese-Japanese-Korean) extension for XeLaTeX
- **fontspec**: Advanced font selection in XeLaTeX
- **xcolor**: Color management

### Fonts
- **Russian/English**: DejaVu Serif (excellent Cyrillic support)
- **Chinese**: Noto Serif CJK SC (Simplified Chinese)
- **Japanese**: Noto Sans CJK JP

### Color Scheme
- **Russian**: Black (RGB: 0,0,0) - Neutral, authoritative
- **English**: Blue (RGB: 0,102,204) - Distinct but readable
- **Chinese**: Red (RGB: 204,0,0) - Traditional Chinese association
- **Japanese**: Green (RGB: 0,153,76) - Distinct from other languages

## File Structure

### Per-Page Workflow

```
1. Extract Russian text from PDF → page_NNN.txt
2. Translate to all languages → page_NNN.json
3. Generate LaTeX source → page_NNN.tex
4. Compile to PDF → page_NNN.pdf
```

### JSON Format

```json
{
  "page": 13,
  "chapter": 1,
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "中文翻译...",
      "ja": "日本語翻訳..."
    }
  ],
  "translator_notes": [],
  "cultural_notes": []
}
```

### LaTeX Template

See `examples/format_demo.tex` and `examples/page_13_demo.tex` for working templates.

Key LaTeX commands:
```latex
\ru{Russian text}  % Black
\en{English text}  % Blue
\zh{中文文本}      % Red
\ja{日本語テキスト} % Green
```

## Compilation Process

### Single Page
```bash
xelatex -interaction=nonstopmode page_NNN.tex
```

### All Pages (M3 assembly)
```bash
# Compile all individual pages
for i in {001..099}; do
    xelatex -interaction=nonstopmode page_$i.tex
done

# Merge PDFs using pdftk or similar
pdftk page_*.pdf cat output durov_code_multilingual.pdf
```

## Dependencies

### Ubuntu/Debian
```bash
sudo apt-get install texlive-xetex texlive-lang-chinese \
  texlive-lang-japanese fonts-noto-cjk fonts-noto-cjk-extra
```

### Python (for helper scripts)
```bash
pip install PyPDF2 # For PDF manipulation if needed
```

## Verified Demos

### Page 13 Demo
- **File**: `examples/page_13_demo.pdf`
- **Hash**: e44df771
- **Content**: Chapter 1 opening, describes Pavel's childhood
- **Quality**: ✓ All 4 languages render correctly
- **Colors**: ✓ Distinct and readable

### Page 43 Demo
- **File**: `examples/page_43_demo.pdf`
- **Hash**: e5ace50d
- **Content**: Chapter 3, forum posts about early VK
- **Quality**: ✓ All 4 languages render correctly
- **Colors**: ✓ Distinct and readable

## Advantages of This Approach

1. **Professional Quality**: LaTeX is publishing industry standard
2. **Consistency**: Same template applies to all 99 pages
3. **Maintainability**: Plain text source files
4. **Flexibility**: Easy to adjust spacing, fonts, colors
5. **Proven**: Both demo pages compiled successfully

## Potential Issues & Solutions

### Issue 1: Font Availability
- **Problem**: Some systems may not have Noto fonts
- **Solution**: Install via package manager or bundle fonts

### Issue 2: Compilation Time
- **Problem**: XeLaTeX can be slow for 99 pages
- **Solution**: Parallel compilation, cache intermediate files

### Issue 3: CJK Line Breaking
- **Problem**: Chinese/Japanese text may break awkwardly
- **Solution**: xeCJK handles this automatically; manual `\\` if needed

## Recommendation for M2

**Proceed with LaTeX approach** for all 99 pages. The infrastructure is proven and scalable.

### M2 Translation Pipeline

1. Worker claims page N
2. Worker extracts text: `examples/page_NNN.txt`
3. Worker researches context (names, places, references)
4. Worker translates to EN, ZH, JA
5. Worker creates `translations/raw/page_NNN.json`
6. Worker generates `page_NNN.tex` from template
7. Worker compiles to `output/page_NNN.pdf`
8. Worker commits with hash
9. Repeat for next page

---

**Decision**: ✅ **APPROVE LaTeX (xelatex + xeCJK) approach**

**Worker**: f6c8
**Date**: 2026-01-01
**Demo Hashes**: 
- Page 13: e44df771
- Page 43: e5ace50d
