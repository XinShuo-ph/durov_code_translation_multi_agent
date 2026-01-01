# Python PDF approach (ReportLab/etc.) — quick exploration notes

Status: **not chosen** (LaTeX/XeLaTeX looks simpler + more deterministic for multi-script typography).

## Summary

Generating the multilingual pages directly via Python (e.g., ReportLab) is possible in principle, but in practice it introduces extra complexity around:

- **CJK font embedding/selection** (Noto CJK fonts are often TTC/OTF collections; tooling support varies)
- **Line breaking** for Chinese/Japanese (needs script-aware shaping + wrapping)
- **Consistent layout** across environments (font availability/metrics differences)

## Recommendation

Use **XeLaTeX + xeCJK** as the default pipeline for M1/M2:

- Better typography for mixed scripts out of the box
- Easier “what you see is what you get” reproducibility across workers
- Straightforward color styling per-language

