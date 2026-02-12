# Durov Code Book Translation Project

**Multi-Agent Parallel Translation System**

## Overview

This project translates "Код Дурова" (Durov Code) by Nikolai Kononov into a multilingual edition featuring Russian, English, Chinese, and Japanese in parallel.

## Multi-Agent Architecture

This project uses **multiple AI agents working in parallel**, each on their own git branch. Agents communicate via git commits, pushes, and fetches.

### How It Works

The protocol has two phases:

1. **Phase 1 — STRIPE**: Each agent receives a deterministic, non-overlapping set of pages computed from their sorted position among peers. No runtime coordination needed.
2. **Phase 2 — SCAVENGE**: After completing their stripe, agents use `tools/coord.py` to find and fill remaining gaps.
3. **Balance Gate**: When a fast worker gets too far ahead, they must review a peer's page before claiming more — tying quality review to work distribution.

### Key Design Principles

1. **Produce output immediately** — all setup is pre-done, no consensus/voting
2. **Deterministic page assignment** — eliminates thundering herd on page 1
3. **Quality enforced** — mandatory validation, automatic review triggers
4. **Batch-scoped discovery** — only see peers from the same experiment run

## Quick Start for Workers

1. **Identify yourself**:
   ```bash
   MY_BRANCH=$(git branch --show-current)
   MY_ID=${MY_BRANCH##*-}
   ```

2. **Discover peers and compute stripe**:
   ```bash
   git fetch origin --prune
   python3 tools/coord.py --fetch status
   ```

3. **Initialize state and register**:
   ```bash
   cp WORKER_STATE_TEMPLATE.json WORKER_STATE.json
   # Fill in worker_id, branch, batch_prefix, heartbeat
   git add WORKER_STATE.json
   git commit -m "[$MY_ID] START: registered"
   git push -u origin HEAD
   ```

4. **Translate your stripe pages**: One at a time, validate, push after each.

5. **After stripe**: Use `tools/coord.py --fetch next --worker "$MY_ID"` to scavenge remaining pages.

## Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | Parallel work protocol |
| `instructions.md` | Detailed task instructions |
| `STATE.md` | Global project state |
| `WORKER_STATE.json` | Your worker state (create from template) |
| `WORKER_STATE_TEMPLATE.json` | Template for new workers |

## Tools

| Tool | Purpose |
|------|---------|
| `tools/coord.py` | Coordination: status, next page, claims, review queue, collection |
| `tools/validate_translation.py` | Validate translation JSON before pushing |
| `tools/compile_pages.py` | Generate PDF from translation JSON |

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
├── page_013_translation.json
├── page_043_translation.json
└── format_demo.tex
```

**Note**: Example JSONs show format only, not complete translations.

## Translation Output

Workers save translations to:
```
translations/page_XXX.json
```

## Target Output Format

Each page becomes a JSON file with sentences in 4 languages:

```json
{
  "page": 13,
  "chapter": 1,
  "chapter_title": "Ботанический сад (Botanical Garden)",
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "Chinese translation...",
      "ja": "Japanese translation..."
    }
  ],
  "translator_notes": ["Context notes"],
  "total_sentences": 1,
  "page_type": "narrative"
}
```

## Color Scheme (for PDF)

| Language | Color |
|----------|-------|
| Russian | Black |
| English | Dark Blue |
| Chinese | Dark Red |
| Japanese | Dark Green |

---

*See `PROTOCOL.md` for the parallel work protocol and `instructions.md` for complete task details.*
