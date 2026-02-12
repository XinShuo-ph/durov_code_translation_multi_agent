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

---

## Multi-Agent Helpers

These scripts support the Protocol v3 workflow:

- `tools/sync.py`: scan experiment-scoped branches and pick a next page
  - `python3 tools/sync.py status`
  - `python3 tools/sync.py next`
- `tools/validate_translation.py`: validate a page JSON before pushing
  - `python3 tools/validate_translation.py translations/page_013.json`
- `tools/collect_translations.py`: integrator utility to collect best-per-page across branches
  - `python3 tools/collect_translations.py --prefix origin/cursor/exp-005- --out-dir translations`
