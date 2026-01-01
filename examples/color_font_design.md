# Color and Font Design Scheme

## Color Palette (Language Coding)

| Language | Color | RGB | Hex | Rationale |
|----------|-------|-----|-----|-----------|
| Russian (Русский) | Black | 0,0,0 | #000000 | Default, authoritative, original text |
| English | Blue | 0,68,153 | #004499 | Professional, clear, readable |
| Chinese (中文) | Red | 204,0,0 | #CC0000 | Traditional Chinese cultural association, high visibility |
| Japanese (日本語) | Green | 0,128,0 | #008000 | Distinct from other colors, good contrast |

## Font Choices

### Latin Characters (Russian, English)
- **Primary**: Noto Serif
- **Rationale**: Free, excellent Unicode support, professional appearance
- **Alternative**: Liberation Serif (if Noto unavailable)

### CJK Characters (Chinese, Japanese)
- **Primary**: Noto Sans CJK SC (Simplified Chinese)
- **Japanese**: Noto Sans CJK JP
- **Rationale**: 
  - Comprehensive coverage
  - Good readability at various sizes
  - Open source, freely distributable
  - Consistent with Google's Material Design

## Typography Specifications

### Sentence Display
- **Base font size**: 12pt
- **Line spacing**: 1.5 (within sentence block)
- **Paragraph spacing**: 0.8em between sentences
- **Margins**: 2.5cm all sides on A4

### Hierarchy
1. **Title**: Multilingual, 24pt+
2. **Chapter headings**: 18pt, bold
3. **Body text**: 12pt, color-coded by language
4. **Notes**: 10pt, gray

## Accessibility Considerations

### Color Blindness
- Black/Blue/Red/Green palette works for most common color blindness types
- Red-green colorblind readers can still distinguish via position
- Blue-black distinction clear for deuteranopia

### Contrast Ratios
- Black on white: AAA (perfect)
- Blue on white: AA+ (readable)
- Red on white: AA+ (readable)  
- Green on white: AA (acceptable)

## Layout Strategy

### Sentence-by-Sentence Approach
Each original Russian sentence followed immediately by three translations:

```
[Russian sentence in black]
[English translation in blue]
[Chinese translation in red]
[Japanese translation in green]
[blank line]
[Next Russian sentence...]
```

### Advantages
1. Easy comparison across languages
2. Clear structure
3. Preserves narrative flow
4. Allows spot-checking specific passages

### Page Management
- Original page number referenced
- Translations may span 1-2 pages per original
- Footer indicates continuation

## Alternative Designs Considered

### Table Format (Rejected)
| RU | EN | ZH | JA |
- **Pro**: Side-by-side comparison
- **Con**: Hard to read long sentences, breaks at page boundaries

### Parallel Columns (Rejected)
- **Pro**: Space efficient
- **Con**: Eye tracking difficult, CJK needs more width

### Toggle/Overlay (Not applicable for print)
- Could work for digital edition

## Implementation Notes

### LaTeX (Chosen)
- **Package**: xeCJK for CJK support
- **Compiler**: XeLaTeX (Unicode support)
- **Color**: xcolor package
- **Fonts**: fontspec for font management

### Python Alternative (Considered)
- **reportlab**: Could work but complex CJK
- **fpdf2**: Limited CJK support
- **Verdict**: LaTeX superior for multilingual typography

## Sample Output Quality

Test compilation shows:
- ✓ All 4 languages render correctly
- ✓ Colors distinct and readable
- ✓ CJK characters display properly
- ✓ Professional appearance
- ✓ 62KB PDF size for demo (efficient)

## Recommendations

1. **Proceed with LaTeX + xeCJK approach**
2. Use Noto font family throughout
3. Color-code as specified
4. Sentence-by-sentence layout
5. Include format explanation page at start

## Hash
Design document for M1.3
