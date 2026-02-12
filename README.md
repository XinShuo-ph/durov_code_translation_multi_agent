# Durov Code Book Translation Project

**Multi-Agent Collaborative Translation System**

## Overview

This project translates "Код Дурова" (Durov Code) by Nikolai Kononov into a multilingual edition featuring Russian, English, Chinese, and Japanese in parallel.

## Multi-Agent Architecture

This project uses **multiple AI agents working collaboratively**, each on their own git branch.

### Key Design Principles

1. **Parallel by default**: Many translators work at once on disjoint pages
2. **Experiment-scoped discovery**: Workers only sync against branches in the current experiment (prevents stale-branch duplication)
3. **Integrate continuously**: An integrator regularly collects and merges page outputs so work never gets stranded on worker branches

### Communication Method

Agents communicate via **git commits, pushes, and pulls**—using git as a message-passing interface.

### Worker Identity

- **Experiment branch naming (mandatory)**: `cursor/exp-<ID>-<role>-<xxxx>`
  - Example: `cursor/exp-005-translate-c68e`
- **Short ID**: Usually the last 4 characters (e.g., `c68e`) - used in commit messages

### Syncing Without Stale-Branch Duplication

Use the helper (scans only `origin/cursor/exp-<ID>-*`):

```bash
python3 tools/sync.py status
python3 tools/sync.py next
```

## Quick Start for Workers

1. **Get next page**:
   ```bash
   NEXT_PAGE=$(python3 tools/sync.py next)
   ```
2. **Translate** `extracted/pages/page_XXX.txt` → `translations/page_XXX.json`
3. **Validate + push**:
   ```bash
   python3 tools/validate_translation.py "translations/page_$(printf '%03d' "$NEXT_PAGE").json"
   git add "translations/page_$(printf '%03d' "$NEXT_PAGE").json"
   MY_SHORT_ID=$(git branch --show-current | grep -oE '[0-9a-fA-F]{4}$' || echo xxxx)
   git commit -m "[${MY_SHORT_ID}] page ${NEXT_PAGE}: translate"
   git push origin HEAD
   ```

## Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | Communication protocol |
| `instructions.md` | Detailed task instructions |
| `STATE.md` | Global project state |
| `tools/sync.py` | Experiment-scoped sync + next-page selection |
| `tools/collect_translations.py` | Integrator: collect best pages across worker branches |
| `tools/validate_translation.py` | Validate JSON before pushing |

## Resources Available

### Pre-Extracted Text
```
extracted/
├── full.txt           # Complete book
└── pages/             # Page-by-page (page_001.txt - page_099.txt)
```

### Research Documents
```
research/
├── durov_bio.md       # Pavel Durov biography
├── vk_history.md      # VKontakte history
├── russia_context.md  # Cultural context
├── chapter_summaries.md
├── chapter_structure.md
└── glossary.md        # Terminology guide
```

### Example Translations (Format Reference)
```
examples/
├── page_013_translation.json   # Example format
├── page_043_translation.json   # Another example
└── format_demo.tex             # LaTeX template
```

**Note**: Example JSONs show format only, not complete translations.

### PDF Generation Tools
```
tools/
├── compile_pages.py   # JSON → PDF compiler
├── README.md          # Tool docs
└── requirements.txt   # Dependencies
```

## Translation Output

Workers save translations to:
```
translations/page_XXX.json
```

Optional PDF output:
```
output/page_XXX.pdf
```

## Target Output Format

Each page becomes a JSON file with sentences in 4 languages:

```json
{
  "page": 13,
  "chapter": 1,
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "Chinese translation...",
      "ja": "Japanese translation..."
    }
  ]
}
```

## Color Scheme (for PDF)

| Language | Color |
|----------|-------|
| Russian | Black |
| English | Dark Blue |
| Chinese | Dark Red |
| Japanese | Dark Green |

## Protocol Summary

1. **Use experiment-scoped prefixes** (`cursor/exp-<ID>-*`) to avoid stale-branch duplication
2. **Pick pages with** `tools/sync.py next` (staggered starts reduce collisions)
3. **Validate every page** with `tools/validate_translation.py`
4. **Integrate continuously** using `tools/collect_translations.py`

---

*See `PROTOCOL.md` for detailed communication rules and `instructions.md` for complete task details.*
