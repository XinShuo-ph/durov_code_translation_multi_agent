# Technical Approach Documentation - M1

## Decision: Python-based PDF Generation

### Rationale
- **XeLaTeX unavailable**: No sudo access to install texlive-xetex
- **Python readily available**: reportlab library successfully installed
- **Cross-platform**: Works without system dependencies
- **Flexible**: Easy to customize layouts, colors, fonts

## Implementation: reportlab + Custom Styling

### Core Libraries
- `reportlab`: PDF generation engine
- `json`: Translation data storage format
- Standard Python libraries for file handling

### Font Strategy
- **Primary**: DejaVu Sans (widely available, good Unicode support)
- **Fallback**: reportlab default fonts if DejaVu not found
- **CJK Support**: DejaVu Sans includes basic CJK characters
- **Future enhancement**: Can add dedicated CJK fonts (Noto Sans CJK)

### Color Scheme
Based on target readability and cultural associations:

| Language | Color | Rationale |
|----------|-------|-----------|
| Russian (ru) | Black | Original text, primary/authoritative |
| English (en) | Blue | Common for secondary text, good contrast |
| Chinese (zh) | Red | Culturally significant color in China |
| Japanese (ja) | Dark Green | Distinctive, good readability |

### Page Layout
- **Page Size**: A4 (international standard)
- **Margins**: 0.75-1 inch (readable, professional)
- **Font Sizes**: 
  - Russian: 11pt (primary language)
  - Other languages: 10pt (secondary)
- **Spacing**: 1.3x leading (line height) for readability

### Translation Data Format (JSON)
```json
{
  "page": [page_number],
  "chapter": [chapter_number],
  "sentences": [
    {
      "id": [sentence_id],
      "ru": "[Russian text]",
      "en": "[English translation]",
      "zh": "[Chinese translation]",
      "ja": "[Japanese translation]"
    }
  ],
  "translator_notes": ["note1", "note2"],
  "research_used": ["source1", "source2"]
}
```

## Workflow

### Per-Page Translation Process
1. **Extract Russian text**: Use pdfplumber on original PDF
2. **Segment sentences**: Split into translatable units
3. **Research context**: Chapter summaries, glossary, cultural notes
4. **Translate**: Russian → English, Chinese, Japanese
5. **Review**: 3-pass quality check
6. **Generate JSON**: Save to translations/raw/page_XXX.json
7. **Compile PDF**: Run compile_pages.py
8. **Verify output**: Check rendering, fonts, colors
9. **Save**: Store in output/page_XXX_translated.pdf

### Quality Assurance
- Sentence alignment across all 4 languages
- Consistent terminology (use glossary)
- Cultural localization (not literal translation)
- Translator notes for complex references
- Color-coding correct in output

## Demo Pages

### Page 13 - Chapter 1 Opening
- **Theme**: Childhood, intellectual background
- **Key elements**: Don Quixote reference, panel housing, St. Petersburg
- **Translation challenges**: Cultural references, architectural terms
- **Status**: ✓ Demo completed

### Page 43 - Chapter 3 Scene
- **Theme**: VKontakte development
- **Key elements**: Informal work culture, team dynamics
- **Translation challenges**: Names (Pasha = Pavel), tech culture
- **Status**: ✓ Demo completed

## Advantages of This Approach

### Pros
1. **No system dependencies**: Works on any Python environment
2. **Maintainable**: Pure Python, easy to debug
3. **Flexible**: Easy layout/color customization
4. **Portable**: Generated PDFs work everywhere
5. **Scriptable**: Easy to automate for 99 pages

### Cons
1. **Font limitations**: Need to install/bundle CJK fonts for best results
2. **Less typographic control**: vs. LaTeX
3. **Manual layout**: No automatic page breaking for complex text

## Future Enhancements
1. **Better CJK fonts**: Install Noto Sans CJK for improved Chinese/Japanese
2. **Page breaking**: Smart sentence wrapping across pages
3. **Headers/footers**: Page numbers, chapter titles
4. **Table of contents**: Generate from all pages
5. **Final assembly**: Merge all individual pages into single PDF

## Cross-Worker Verification
- Other workers can run: `python3 compile_pages.py examples/page_13_demo.json test_output.pdf`
- Compare output PDFs via hash or visual inspection
- JSON format allows easy diff between translations

## M1 Task Completion Status

| Task | Status | Notes |
|------|--------|-------|
| M1.1 | N/A | LaTeX not available (no sudo) |
| M1.2 | ✓ Done | Python/reportlab approach implemented |
| M1.3 | ✓ Done | Color scheme: Black/Blue/Red/Green |
| M1.4 | ✓ Done | compile_pages.py template created |
| M1.5 | ✓ Done | Page 13 demo generated |
| M1.6 | ✓ Done | Page 43 demo generated |
| M1.7 | ✓ Done | This document |

## Hashes for Verification

```bash
# Demo translation JSON files
sha256sum examples/page_13_demo.json
sha256sum examples/page_43_demo.json

# Demo PDF outputs
sha256sum examples/page_13_demo.pdf
sha256sum examples/page_43_demo.pdf

# Compilation script
sha256sum tools/compile_pages.py
```

## Consensus Vote
**My vote**: `format_approach = python_reportlab`

**Reasoning**:
- Works immediately without system dependencies
- Sufficient quality for multilingual parallel text
- Easier for other workers to reproduce/verify
- Can enhance with better fonts later if needed
