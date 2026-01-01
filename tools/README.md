# Technical Pipeline Documentation

## M1 Decision: LaTeX with XeLaTeX Approach

### Rationale
After exploring both LaTeX and Python approaches, **LaTeX with XeLaTeX** is the recommended solution for this project.

### Advantages of LaTeX/XeLaTeX

1. **Professional Typography**: LaTeX produces publication-quality typography automatically
2. **Multilingual Support**: XeLaTeX with xeCJK handles Russian, English, Chinese, and Japanese seamlessly
3. **Font Management**: Easy integration with system fonts (Noto CJK for Asian languages)
4. **Color Support**: Built-in xcolor package for language differentiation
5. **Mature Ecosystem**: Well-tested, stable, widely-used in academic publishing
6. **Batch Processing**: Easy to template and automate for 99 pages
7. **PDF Quality**: Native PDF generation with excellent rendering

### Python PDF Libraries (Explored but Not Recommended)

**Tested**: reportlab, fpdf2

**Limitations**:
- Complex multilingual text rendering requires significant manual work
- CJK font management is more complicated
- Line breaking and text flow less sophisticated
- Color and layout require more manual coding
- Less professional output compared to LaTeX

**Verdict**: Python libraries are powerful for programmatic PDF generation but overkill and more error-prone for our text-heavy, typography-focused use case.

## Chosen Stack

### Core Tools
- **XeLaTeX**: LaTeX compiler with Unicode and font support
- **xeCJK**: Package for Chinese, Japanese, Korean text
- **fontspec**: Advanced font selection
- **xcolor**: Color management
- **babel**: Multilingual support with Russian and English

### Fonts
- **DejaVu Serif**: Main Latin and Cyrillic font
- **Noto Sans CJK SC**: Simplified Chinese
- **Noto Sans CJK JP**: Japanese

### Color Scheme
- **Russian**: Black (RGB: 0,0,0) - Original text, neutral
- **English**: Blue (RGB: 0,51,153) - Professional, readable
- **Chinese**: Red (RGB: 204,0,0) - Traditional color association
- **Japanese**: Dark Green (RGB: 0,102,51) - Distinguishable, readable

## Template Structure

### Document Layout
- Paper: A4
- Font size: 12pt base
- Margins: 2.5cm all sides
- Paragraph spacing: parskip package (no indentation)

### Sentence Display Format
Each sentence appears in a `mlsentence` environment (quote-based):
1. Russian (black)
2. English (blue) 
3. Chinese (red)
4. Japanese (green)

Slight indentation and smaller font for readability.

### Custom Commands
- `\ru{text}` - Russian text in black
- `\en{text}` - English text in blue
- `\zh{text}` - Chinese text in red
- `\ja{text}` - Japanese text in green

## Workflow for M2 Translation

### Per Page Process

1. **Extract Russian text** from original PDF (pdftotext)
2. **Translate** to English, Chinese, Japanese
3. **Create JSON** with sentence-by-sentence translations
4. **Generate LaTeX** from JSON template
5. **Compile** with XeLaTeX to produce PDF
6. **Verify** output quality

### Automation Script Structure

```python
# tools/compile_pages.py (to be created)

def json_to_latex(page_number, json_data):
    """Convert translation JSON to LaTeX source"""
    # Load template
    # Insert sentences
    # Return LaTeX string

def compile_latex(tex_file, output_dir):
    """Compile LaTeX to PDF using xelatex"""
    # Run xelatex
    # Handle errors
    # Return PDF path

def process_page(page_number):
    """Complete workflow for one page"""
    # Load translation JSON
    # Generate LaTeX
    # Compile PDF
    # Verify output
```

## Installation Requirements

### System Packages (Ubuntu/Debian)
```bash
sudo apt-get install texlive-xetex texlive-fonts-extra \
    texlive-lang-cyrillic texlive-lang-chinese \
    texlive-lang-japanese fonts-noto-cjk poppler-utils
```

### Python Packages
```bash
pip3 install PyPDF2 pyyaml
```

## Quality Assurance

### Checks for Each Page
1. **Compilation success**: No LaTeX errors
2. **Font rendering**: All characters display correctly
3. **Color accuracy**: Each language in correct color
4. **Layout consistency**: Uniform spacing and alignment
5. **No overflows**: Text fits within margins
6. **PDF readability**: Legible on screen and print

### Common Issues & Solutions

**Issue**: CJK characters not rendering
**Solution**: Ensure fonts-noto-cjk installed, check font names in template

**Issue**: Overfull hbox warnings
**Solution**: Adjust margins or break long sentences

**Issue**: Slow compilation
**Solution**: Use xelatex -interaction=nonstopmode for batch processing

## Performance Estimates

- **Per page compilation time**: 3-5 seconds
- **Total for 99 pages**: ~8 minutes (sequential)
- **With parallel processing**: ~2 minutes (4 workers)

## File Organization

```
examples/format_demo.tex          # Template demonstration
tools/compile_pages.py            # Automation script
tools/latex_template.tex          # Base template
translations/raw/page_XXX.json    # Translation data
output/page_XXX_translated.pdf    # Compiled pages
```

## M1 Vote

**format_approach**: latex_xecjk
**color_scheme**: ru_black_en_blue_zh_red_ja_green
**font_choice**: noto_cjk

## Next Steps for M2

1. Create `compile_pages.py` automation script
2. Establish JSON format for translations
3. Test full workflow with demo pages 13 and 43
4. Distribute page assignments among workers
5. Begin parallel translation

---

**Status**: M1 technical exploration complete
**Recommendation**: Proceed with LaTeX/XeLaTeX approach
**Ready for M2**: Yes, pending cross-verification with other workers
