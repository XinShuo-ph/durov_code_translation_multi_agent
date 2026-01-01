# Technical Pipeline: LaTeX + XeCJK

We use **XeLaTeX** for PDF generation because it handles Unicode and system fonts natively, which is essential for mixing Cyrillic, Latin, Chinese, and Japanese scripts.

## Dependencies
- `texlive-xetex`
- `texlive-lang-chinese`, `texlive-lang-japanese`
- `texlive-latex-extra` (for paracol)
- Fonts: `DejaVu Serif` (Ru/En), `AR PL UMing CN` (Zh), `IPAexMincho` (Ja)

## File Format
We use `.tex` files with the `paracol` package for parallel columns.

## Structure
```latex
\documentclass{article}
\usepackage{xeCJK}
\usepackage{paracol}
\setmainfont{DejaVu Serif}
\setCJKmainfont{AR PL UMing CN}
...
\begin{paracol}{4}
Russian \switchcolumn English \switchcolumn Chinese \switchcolumn Japanese
\end{paracol}
```

## Compilation
Run:
```bash
xelatex -output-directory=output translation.tex
```

## Why this approach?
- **Typography**: LaTeX provides superior typesetting quality compared to ReportLab/fpdf2.
- **Multilingual**: XeTeX was designed for this specific mixed-script use case.
- **Stability**: Standard LaTeX packages are robust.
