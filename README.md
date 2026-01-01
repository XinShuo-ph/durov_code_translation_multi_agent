# Durov Code Book Translation Project

**Multi-Agent Collaborative Translation System**

## Overview

This project translates "Код Дурова" (Durov Code) by Nikolai Kononov into a multilingual edition featuring Russian, English, Chinese, and Japanese in parallel.

## Multi-Agent Architecture

This project uses **multiple AI agents working collaboratively**, each on their own git branch.

### Key Design Principles

1. **Collaborative, not isolated**: Workers know who else is online and what they're doing
2. **Simple workload distribution**: Claim lowest available page
3. **Robust against disconnection**: Pages can be reclaimed from offline workers
4. **Easy reconnection**: Returning workers sync and continue

### Communication Method

Agents communicate via **git commits, pushes, and pulls**—using git as a message-passing interface.

### Worker Identity

- **Branch Name**: Full branch name (e.g., `cursor/translation-task-a1b2`)
- **Short ID**: Last 4 characters (e.g., `a1b2`) - used in commit messages
- **Registration**: Creating `WORKER_STATE.md` on your branch registers you as active

### Checking Who's Online

```bash
git fetch origin --prune
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null 2>&1; then
    short_id=$(echo "$branch" | grep -oE '[^-]+$' | tail -c 5)
    echo "Active: $short_id ($branch)"
  fi
done
```

## Quick Start for Workers

1. **Identify yourself**:
   ```bash
   MY_BRANCH=$(git branch --show-current)
   MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
   ```

2. **Create WORKER_STATE.md**: Copy from template, fill in your info

3. **Push to register**: This makes you visible to other workers

4. **Sync and discover**: Fetch other workers' states

5. **Claim a page**: Lowest available page number

6. **Translate and push**: Save JSON, push, claim next

## Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | Communication protocol |
| `instructions.md` | Detailed task instructions |
| `STATE.md` | Global project state |
| `WORKER_STATE.md` | Your worker state (create this!) |
| `WORKER_STATE_TEMPLATE.md` | Template for new workers |

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

1. **Sync regularly**: Every 2-3 minutes
2. **Claim one page at a time**: Lowest available
3. **Push immediately**: After claiming, after completing
4. **Heartbeat**: Update at least every 5 minutes
5. **Handle disconnection**: Reclaim pages from offline workers (>15 min)

---

*See `PROTOCOL.md` for detailed communication rules and `instructions.md` for complete task details.*
