# Tools (draft)

This folder contains the scripts/templates used to extract text from `durov_code_book.pdf` and to compile multilingual demo pages.

## Text extraction

- **Full book text (RU)**:

```bash
python3 tools/extract_text.py --pdf durov_code_book.pdf --out research/durov_code_book_ru.txt
```

- **Single-page extraction (RU)** (uses poppler directly):

```bash
pdftotext -layout -enc UTF-8 -f 13 -l 13 durov_code_book.pdf examples/page_013_original.txt
pdftotext -layout -enc UTF-8 -f 43 -l 43 durov_code_book.pdf examples/page_043_original.txt
```

## LaTeX demo compilation (XeLaTeX)

```bash
xelatex -interaction=nonstopmode -output-directory examples examples/format_demo.tex
```

If font names differ on a system, edit the font lines in `examples/format_demo.tex`:

- `\setmainfont{...}` for Latin/Cyrillic
- `\setCJKmainfont{...}` for Chinese
- `\newCJKfontfamily\CJKjp{...}` for Japanese

