# Task: Translate "Код Дурова" (Durov Code)

## You are one of N parallel agents. Follow PROTOCOL.md for coordination.

## Your Job

Translate each assigned page of the Russian book "Код Дурова" by Nikolai Kononov into English, Chinese (Simplified), and Japanese. One page = one JSON file.

## Startup

Follow `PROTOCOL.md` Steps 1-2 to discover your peers and compute your assigned pages. Then immediately start translating — all resources are pre-provided on `main`. Do **NOT** regenerate extracted text, research docs, or tools.

## Workflow Per Page

1. Read `extracted/pages/page_XXX.txt` (pre-extracted Russian text)
2. Parse into sentences
3. Translate each sentence to EN, ZH, JA
4. Save to `translations/page_XXX.json`
5. Commit and push

## JSON Output Format (mandatory)

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
  "translator_notes": ["Context notes for the reader"],
  "total_sentences": 1,
  "page_type": "narrative"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (1-99) |
| `chapter` | int | 0 for front matter, 1-7 for chapters |
| `chapter_title` | string | Russian title (English in parentheses) |
| `sentences` | array | All sentences on the page |
| `sentences[].id` | int | Sequential: 1, 2, 3, ... |
| `sentences[].ru` | string | Original Russian |
| `sentences[].en` | string | English translation |
| `sentences[].zh` | string | Simplified Chinese translation |
| `sentences[].ja` | string | Japanese translation |
| `translator_notes` | array | Cultural/context notes |
| `total_sentences` | int | Count of sentences |
| `page_type` | string | `front_matter`, `narrative`, `dialogue`, or `about_author` |

### Quality Rules

1. Every sentence must have all 4 languages — no null/empty values
2. Valid JSON with proper UTF-8 encoding
3. Include EVERY sentence from the page — no skipping
4. Sequential IDs with no gaps
5. Escape special characters properly

## Chapter Structure

| Chapter | Pages | Title |
|---------|-------|-------|
| 0 | 1-4 | Front Matter (title, contents) |
| 0 | 5-6 | Предисловие (Preface) |
| 0 | 7-12 | Пролог (Prologue) |
| 1 | 13-22 | Ботанический сад (Botanical Garden) |
| 2 | 23-37 | University years |
| 3 | 38-50 | VKontakte founding |
| 4 | 51-64 | Growth and scaling |
| 5 | 65-78 | Business conflicts |
| 6 | 79-91 | Philosophy and maturity |
| 7 | 92-98 | Future outlook |
| - | 99 | About the Author |

Total: 99 pages.

## Translation Style

**Voice**: Pavel Durov's voice is sharp, direct, intellectually provocative, anti-establishment.

| Language | Guidelines |
|----------|-----------|
| English | American English, tech industry register, informal |
| 中文 | Simplified Chinese (简体中文), internet culture where appropriate |
| 日本語 | Katakana for foreign names, formal-informal balance |

### Key Terms (use consistently)

| Russian | English | Chinese | Japanese |
|---------|---------|---------|----------|
| ВКонтакте | VKontakte | VKontakte (VK) | VKontakte |
| Дуров | Durov | 杜罗夫 | ドゥーロフ |
| Санкт-Петербург | St. Petersburg | 圣彼得堡 | サンクトペテルブルク |

See `research/glossary.md` for the complete terminology guide.

## Pre-Provided Resources (do NOT recreate)

```
extracted/pages/page_001.txt - page_099.txt   # Source text (already extracted)
research/glossary.md                           # Terminology guide
research/chapter_summaries.md                  # Chapter summaries
research/durov_bio.md                          # Background: Durov
research/vk_history.md                         # Background: VKontakte
research/russia_context.md                     # Background: cultural context
examples/page_013_translation.json             # Format reference
examples/page_043_translation.json             # Format reference
```

## Output Location

```
translations/page_001.json
translations/page_002.json
...
translations/page_099.json
```

## Rules

- Start translating immediately after computing your page assignment
- Commit and push after every completed page
- Do NOT create WORKER_STATE.md, heartbeat files, or status updates
- Do NOT regenerate extracted text, research docs, or tools
- Do NOT wait for other agents or any form of consensus
- If stuck on a sentence for >5 minutes, add a translator note and move on
- Continue translating until all your assigned pages are done, then fill gaps per PROTOCOL.md Step 4
