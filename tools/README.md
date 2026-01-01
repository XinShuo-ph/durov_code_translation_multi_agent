# Translation Tools

## PDF Generation Approach

This project uses **XeLaTeX with xeCJK** for generating multilingual PDFs. This approach was chosen because:

1. **Full CJK Support**: xeCJK provides excellent Chinese, Japanese, and Korean typesetting
2. **Unicode Support**: XeLaTeX handles Unicode natively
3. **Font Flexibility**: Can use system fonts including Noto CJK fonts
4. **Quality Output**: Professional-quality typesetting for the book

### Alternative Approaches Tested

| Approach | Status | Notes |
|----------|--------|-------|
| XeLaTeX + xeCJK | **CHOSEN** | Best quality, full CJK support |
| Python fpdf2 | Works | Simpler, but font registration more complex |
| Python reportlab | Works | Good fallback, but CJK setup requires extra fonts |

## Color Scheme

| Language | Color | RGB | Hex |
|----------|-------|-----|-----|
| Russian | Black | (0, 0, 0) | #000000 |
| English | Blue | (0, 0, 200) | #0000C8 |
| Chinese | Red | (180, 0, 0) | #B40000 |
| Japanese | Green | (0, 128, 0) | #008000 |

## Dependencies

### System Packages
```bash
# Ubuntu/Debian
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-fonts-extra
sudo apt-get install texlive-lang-cjk fonts-noto-cjk fonts-noto
```

### Python Packages
```bash
pip install -r requirements.txt
```

## Usage

### Generate a Single Page PDF

```bash
python3 tools/generate_page_latex.py translations/raw/page_013.json output/page_013_translated.pdf
```

### Translation JSON Format

```json
{
  "page": 13,
  "chapter": 1,
  "chapter_title_ru": "Ботанический сад",
  "chapter_title_en": "The Botanical Garden",
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "中文翻译...",
      "ja": "日本語訳..."
    }
  ],
  "translator_notes": ["Note 1", "Note 2"],
  "research_used": ["Source 1", "Source 2"]
}
```

## File Structure

```
tools/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── generate_page_latex.py    # XeLaTeX-based PDF generator
└── fonts/                    # Additional fonts (if needed)
```

## Workflow

1. Extract text from PDF page (already done in `translations/raw/page_XXX.txt`)
2. Create translation JSON with all 4 languages
3. Run PDF generator
4. Verify output quality
5. Commit to repository

## Quality Guidelines

- Each sentence should appear in all 4 languages
- Colors must be consistent (Russian=Black, English=Blue, Chinese=Red, Japanese=Green)
- PDF should be readable on screen and print
- CJK characters must render correctly

---

*Documentation by Worker 14ce*
