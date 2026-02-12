# Durov Code Book Translation — Agent Instructions

## Your Job

Translate pages of "Код Дурова" (Durov Code) from Russian into English, Chinese, and Japanese.

**You are one of ~16 agents working in parallel.** Read `PROTOCOL.md` for the coordination protocol. This file covers the translation task itself.

---

## Step 1: Compute Your Stripe (< 2 min)

```bash
# Get your assigned pages
python3 tools/compute_stripe.py

# Or just get the next page to translate
python3 tools/compute_stripe.py --next
```

This gives you a deterministic set of pages. Start with the first one.

---

## Step 2: Translate Pages (The Actual Work)

For each page in your stripe:

### 2a. Read the source text

The Russian text is pre-extracted at `extracted/pages/page_XXX.txt`.

### 2b. Parse into sentences

Split the Russian text into sentences. Use your judgment on boundaries.

### 2c. Translate each sentence into 3 languages

| Language | Style |
|----------|-------|
| **English** | Natural American English. Sharp, direct (match Durov's voice). Tech-savvy register. |
| **Chinese** (简体中文) | Simplified Chinese. 杜罗夫 for Durov, 圣彼得堡 for St. Petersburg. |
| **Japanese** | Standard Japanese. ドゥーロフ for Durov, サンクトペテルブルク for St. Petersburg. |

### 2d. Save as JSON

Save to `translations/page_XXX.json` using this exact format:

```json
{
  "page": 13,
  "chapter": 1,
  "chapter_title": "Ботанический сад (Botanical Garden)",
  "sentences": [
    {
      "id": 1,
      "ru": "Мальчик с томом Сервантеса выходит из подъезда...",
      "en": "A boy with a volume of Cervantes exits the building entrance...",
      "zh": "一个手捧塞万提斯著作的男孩走出公寓楼门口...",
      "ja": "セルバンテスの本を抱えた少年が建物の入り口から出てきて..."
    }
  ],
  "translator_notes": ["Brief context notes if useful"],
  "total_sentences": 1,
  "page_type": "narrative"
}
```

### 2e. Push immediately

```bash
git add translations/page_XXX.json WORKER_STATE.md
git commit -m "[YOUR_ID] DONE: page XXX - brief description"
git push origin HEAD
```

### 2f. Move to next page

Repeat from 2a with your next stripe page.

---

## Step 3: Scavenge (After Stripe Is Done)

```bash
# Find pages not yet translated by any agent
python3 tools/compute_stripe.py --scan

# Or just get the next unclaimed page
python3 tools/compute_stripe.py --next
```

Claim and translate unclaimed pages until everything is done.

---

## Required JSON Fields

| Field | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (1-99) |
| `chapter` | int | Chapter number (0 = front matter, 1-7 = chapters) |
| `chapter_title` | string | Russian title (English translation) |
| `sentences` | array | Array of sentence objects |
| `sentences[].id` | int | Sequential: 1, 2, 3... |
| `sentences[].ru` | string | Original Russian |
| `sentences[].en` | string | English translation |
| `sentences[].zh` | string | Chinese translation (Simplified) |
| `sentences[].ja` | string | Japanese translation |
| `translator_notes` | array | Context notes (brief) |
| `total_sentences` | int | Sentence count |
| `page_type` | string | `front_matter`, `narrative`, `dialogue`, `about_author` |

**Quality rules:**
1. Every sentence has all 4 languages — no null/empty values
2. Valid JSON — escape special characters
3. UTF-8 encoding
4. No skipped content — include EVERY sentence from the page
5. Sequential IDs — 1, 2, 3... (no gaps)

---

## Chapter Reference

| Ch | Pages | Title | Content |
|----|-------|-------|---------|
| 0 | 1-4 | Front Matter | Title, copyright, contents |
| 0 | 5-6 | Предисловие | Yuri Saprykin's introduction |
| 0 | 7-12 | Пролог | VK office scene |
| 1 | 13-22 | Ботанический сад | Durov's childhood |
| 2 | 23-37 | Ch 2 | University years |
| 3 | 38-50 | Ch 3 | VKontakte founding |
| 4 | 51-64 | Ch 4 | Scaling and growth |
| 5 | 65-78 | Ch 5 | Business conflicts |
| 6 | 79-91 | Ch 6 | Philosophy and maturity |
| 7 | 92-98 | Ch 7 | Future outlook |
| - | 99 | Об авторе | About the author |

---

## Translation Voice Guide

Pavel Durov's voice is:
- **Sharp and direct**: Short sentences, confident assertions
- **Intellectually provocative**: Philosophy, unconventional thinking
- **Anti-establishment**: Skepticism toward authority
- **Technical precision**: Accurate on code/systems

### Common Terms (use consistently)

| Russian | English | Chinese | Japanese |
|---------|---------|---------|----------|
| ВКонтакте | VKontakte | VKontakte (VK) | VKontakte |
| Дуров | Durov | 杜罗夫 | ドゥーロフ |
| Санкт-Петербург | St. Petersburg | 圣彼得堡 | サンクトペテルブルク |
| ботаник | nerd/geek | 书呆子 | オタク |
| стартап | startup | 创业公司 | スタートアップ |

See `research/glossary.md` for the full terminology guide.

---

## Available Resources (Pre-Done — Do NOT Redo)

All setup is complete. These are for **reference only** — do not spend time recreating them:

```
extracted/pages/page_001.txt - page_099.txt   # Source text (read these)
research/glossary.md                           # Terminology consistency
research/chapter_summaries.md                  # Chapter context
research/durov_bio.md                          # Durov background
examples/page_013_translation.json             # Output format example
tools/compile_pages.py                         # Optional PDF generation
tools/compute_stripe.py                        # YOUR PAGE ASSIGNMENTS
```

---

## Execution Rules

1. **Never stop between pages** to ask for confirmation. Translate → push → next → repeat.
2. **Sync between pages** (quick `git fetch`), not during translation.
3. **If stuck on a sentence > 5 min**, add a translator note and move on.
4. **Each page should take ~10-20 min** depending on density.
5. **Continue until**: all your stripe pages are done AND all scavenge pages are done, OR you run out of context.
6. **If running low on context**: push everything, update WORKER_STATE.md, stop cleanly.

---

## Session End

```bash
git add .
git commit -m "[YOUR_ID] END: translated pages [list] — session complete"
git push origin HEAD
```
