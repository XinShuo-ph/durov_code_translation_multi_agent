# Technical Approach

## Format Selection
We have selected **XeLaTeX** (with `xeCJK` package) as the primary typesetting engine.
- **Reasoning**: Superior handling of multilingual typography (mixing Cyrillic, Latin, Chinese, Japanese) and high-quality PDF output.

## Fonts
- **Main Font (Cyrillic/Latin)**: `Noto Serif`
- **Chinese Font**: `Noto Serif CJK SC`
- **Japanese Font**: `Noto Serif CJK JP`

## Color Scheme
To visually distinguish languages in parallel text:
- **Russian (RU)**: Black (#000000) - Original text
- **English (EN)**: Dark Blue (#00008B)
- **Chinese (ZH)**: Dark Red (#8B0000)
- **Japanese (JA)**: Dark Green (#006400)

## Compilation Pipeline
1. **Translation**: Translation data is stored in JSON files (`translations/raw/page_XXX.json`).
2. **Compilation**: A Python script (`tools/compile_pages.py`) reads the JSON and generates a `.tex` file using the standard template.
3. **Rendering**: `xelatex` compiles the `.tex` file to PDF.

## Usage
```bash
python3 tools/compile_pages.py translations/raw/page_XXX.json output_directory
```

## Dependencies
- `python3`
- `xelatex` (part of `texlive-xetex`)
- `xeCJK` (part of `texlive-lang-chinese`)
- `Noto` fonts
