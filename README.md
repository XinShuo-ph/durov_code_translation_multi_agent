# Durov Code Book Translation Project

**Multi-Agent Parallel Translation System v2.0**

## Overview

This project translates "Код Дурова" (Durov Code) by Nikolai Kononov into a multilingual edition featuring Russian, English, Chinese, and Japanese.

## v2.0 Improvements

This is version 2.0, redesigned after analyzing the failure modes of the first 16-agent run:

| Problem in v1.0 | Solution in v2.0 |
|-----------------|------------------|
| Consensus deadlock | No consensus required |
| Complex M0→M1→M2→M3 phases | Single phase: translate |
| Workers waiting for sync | Independent operation |
| Re-extracting PDF 16 times | Pre-extracted text provided |
| Protocol too complex | Minimal protocol |

## Quick Start for Workers

### 1. You Already Have Everything

- **Extracted text**: `extracted/pages/page_XXX.txt`
- **Research docs**: `research/` directory
- **Output format**: JSON (see instructions.md)

### 2. Your Only Task

Translate pages from Russian to English, Chinese, and Japanese.

### 3. Simple Workflow

```bash
# 1. Find next untranslated page
ls translations/

# 2. Read the Russian text
cat extracted/pages/page_013.txt

# 3. Translate (in your agent memory)
# ... translate each sentence to en, zh, ja ...

# 4. Save as JSON
# ... write to translations/page_013.json ...

# 5. Commit and push
git add translations/page_013.json
git commit -m "[YOUR_ID] Translated page 013"
git push origin HEAD
```

### 4. No Waiting Required

- No consensus voting
- No synchronization with other workers
- No setup tasks (already done)
- Just translate and save

## Files

| File | Purpose |
|------|---------|
| `instructions.md` | Detailed translation instructions |
| `PROTOCOL.md` | Multi-agent coordination (minimal) |
| `extracted/pages/` | Pre-extracted Russian text |
| `research/` | Context and reference materials |
| `translations/` | Your output JSON files |

## Output Format

Each page produces a JSON file:

```json
{
  "page": 13,
  "chapter": 1,
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text...",
      "en": "English translation...",
      "zh": "中文翻译...",
      "ja": "日本語訳..."
    }
  ]
}
```

## Target Output

A multilingual document where each original Russian sentence is followed by translations in all four languages.

## Project Status

See `STATE.md` for current progress tracking.

---

*Read `instructions.md` for complete details. Then start translating!*
