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

## Multi-Agent Coordination Helper

`tools/coord.py` provides machine-checkable coordination for parallel translation.

### Commands

```bash
# Team health, skew, duplicates
python3 tools/coord.py status --total-pages 99

# Next page recommendation with fairness gate
python3 tools/coord.py next --worker-id YOUR_ID --total-pages 99

# Reclaimable stale claims
python3 tools/coord.py stale --total-pages 99
```

### Notes

- `next` may return `HOLD=lead_cap` when a worker is too far ahead while peers are online.
- Tool scans `translations/raw/page_XXX.json` and `translations/page_XXX.json`.
- Worker-state parsing depends on the v3 `WORKER_STATE_TEMPLATE.md` field names.
