# Translation Tools Documentation

## Chosen Approach: Python + fpdf2

We are using Python with the `fpdf2` library to generate PDFs. This approach was chosen because:
1. It is lightweight and easy to install via pip.
2. It supports TrueType/OpenType fonts (essential for CJK).
3. It allows precise control over positioning and colors.
4. It avoids the complexity of installing a full TeX distribution (XeLaTeX) in restricted environments.

## Dependencies

- Python 3.x
- `fpdf2`
- `pdfminer.six` (for extraction)
- See `requirements.txt`

## Fonts

We use the Google Noto font family to ensure coverage for all 4 languages:
- **Russian/English**: `NotoSans-Regular.ttf` (or system installed)
- **Chinese**: `NotoSansCJKsc-Regular.otf` (downloaded)
- **Japanese**: `NotoSansCJKjp-Regular.otf` (downloaded)

Fonts are expected to be in `/workspace/tools/fonts/` or `/usr/share/fonts/truetype/noto/`.

## Color Scheme

| Language | Color | RGB |
|----------|-------|-----|
| Russian  | Black | 0, 0, 0 |
| English  | Blue  | 0, 0, 255 |
| Chinese  | Red   | 255, 0, 0 |
| Japanese | Green | 0, 128, 0 |

## Usage

### Extract Text
```bash
python3 tools/extract_text.py
```

### Generate PDF Page
```bash
python3 tools/generate_page.py path/to/translation.json path/to/output.pdf
```
