# Durov Code Book Translation Project

## Objective
Deliver a multilingual edition of "Код Дурова" (Durov Code) by Nikolai Kononov, translated into English, 中文 (Chinese), and 日本語 (Japanese). The final output presents each original Russian sentence followed by its translations in all four languages.

---

## LESSONS LEARNED FROM PREVIOUS RUN

The first multi-agent run had 16 workers but produced suboptimal results. Key failures identified:

### Critical Failures Fixed in This Version

| Failure | Root Cause | Fix |
|---------|-----------|-----|
| **Consensus Deadlock** | Workers waited forever for 50% vote on format | No consensus required - each worker proceeds independently |
| **Technical Approach Split** | Workers voted LaTeX vs Python, couldn't agree | Output format is JSON only - workers use any tool that works |
| **Session Ended Early** | Workers exhausted context on setup tasks | Pre-extracted text provided - jump straight to translation |
| **Redundant M0 Work** | 16 workers all extracted PDF, wrote research docs | All setup pre-done - workers only translate |
| **Communication Failure** | Workers couldn't discover each other reliably | Simplified protocol - no git sync required to proceed |
| **Lost Workers** | Protocol assumed 16 workers present | Protocol works for 1-N workers, no minimum required |
| **Missing Content** | JSON translations skipped sentences | Explicit: translate EVERY sentence, no skipping |
| **Poor Formatting** | Inconsistent JSON structure | Strict JSON schema with examples |

---

## Execution Model: INDEPENDENT WORKERS

**Each worker operates independently on their assigned pages.**

- No git synchronization required to proceed
- No consensus voting needed
- No waiting for other workers
- Workers translate at their own pace
- Works correctly with any number of workers (1 to N)

### Worker Philosophy
Think of yourself as a **freelance translator** with an assigned section:
1. You have pre-extracted Russian text files ready
2. You translate your pages from Russian → {English, Chinese, Japanese}
3. You save translations as JSON in a standard format
4. You optionally generate PDF output
5. You commit and push your work

**You do NOT need to:**
- Wait for other workers to start
- Vote on technical approaches
- Reach consensus on anything
- Sync with other workers to claim pages
- Do any setup (dependencies, PDF extraction, research)

---

## Reader Context

**Target Reader Profile:**
- Chinese-born graduate student at Stanford University (computational physics)
- Active Telegram user, programmer since high school
- Interested in Pavel Durov's worldview on technology, code, and life philosophy
- Reads Russian (original), English, Chinese, and Japanese

**Cultural Bridge Goals:**
- Make Russian tech/startup culture accessible to international readers
- Preserve Durov's distinctive voice and unconventional philosophy
- Localize references for English/Chinese/Japanese netizen audiences

---

## Pre-Provided Resources

All setup work is done. You have:

### 1. Extracted Text Files
```
extracted/pages/page_001.txt through page_099.txt
```
**Use these directly.** Read the `.txt` file, parse sentences yourself, translate.

### 2. Full Text (for context)
```
extracted/full.txt
```
Complete book text for understanding narrative context.

### 3. Research Documents (Reference Only)
```
research/
├── durov_bio.md         # Pavel Durov biography
├── vk_history.md        # VKontakte company history  
├── russia_context.md    # Russian cultural context
├── chapter_summaries.md # Chapter-by-chapter summaries
├── glossary.md          # Terminology consistency guide
└── chapter_structure.md # Page ranges for each chapter
```

### 4. Example Translations (Reference)
```
examples/
├── page_013_translation.json  # Example output format
└── page_043_translation.json  # Another example
```

---

## File Structure

```
workspace/
├── instructions.md           # This file (read-only)
├── PROTOCOL.md               # Multi-agent protocol (read-only)
├── durov_code_book.pdf       # Original PDF (for reference only)
│
├── extracted/                # PRE-EXTRACTED - USE THESE
│   ├── full.txt              # Complete book text
│   └── pages/                
│       ├── page_001.txt
│       ├── page_002.txt
│       └── ... (all 99 pages)
│
├── research/                 # PRE-WRITTEN - USE FOR CONTEXT
│   ├── durov_bio.md
│   ├── vk_history.md
│   ├── russia_context.md
│   ├── chapter_structure.md
│   ├── chapter_summaries.md
│   └── glossary.md
│
├── translations/             # YOUR OUTPUT GOES HERE
│   ├── page_001.json
│   ├── page_002.json
│   └── ...
│
├── output/                   # OPTIONAL: Generated PDFs
│   ├── page_001.pdf
│   └── ...
│
└── WORKER_STATE.md           # Your status (optional but recommended)
```

---

## Your Only Task: TRANSLATE

### Step 1: Identify Your Pages
When you start, you should know your assigned page range.
If not explicitly assigned, use the **lowest-numbered-first** strategy:
1. Check `translations/` for existing page_XXX.json files
2. Find the lowest page number that doesn't have a translation yet
3. Start translating from there

### Step 2: Read the Extracted Text
```bash
# Read the Russian text for your page
cat extracted/pages/page_013.txt
```

### Step 3: Parse Sentences
You (the agent) parse the Russian text into sentences yourself. 
- Use your judgment on sentence boundaries
- Keep paragraph structure if helpful
- Include ALL text - nothing should be skipped

### Step 4: Translate Each Sentence
For each Russian sentence, produce:
- **English translation**: Natural, accessible American English
- **Chinese translation**: Simplified Chinese (简体中文), modern internet register
- **Japanese translation**: Standard Japanese, appropriate register

### Step 5: Save as JSON
Save to `translations/page_XXX.json` using the **exact format below**.

---

## JSON Output Format (MANDATORY)

Every page translation MUST follow this exact structure:

```json
{
  "page": 13,
  "chapter": 1,
  "chapter_title": "Ботанический сад (Botanical Garden)",
  "sentences": [
    {
      "id": 1,
      "ru": "Мальчик с томом Сервантеса выходит из подъезда, огибает автомобиль, который какой-то негодяй поставил так, что пешеходы еле протискиваются мимо, и сворачивает за угол.",
      "en": "A boy with a volume of Cervantes exits the building entrance, skirts around a car that some scoundrel parked so badly that pedestrians can barely squeeze past, and turns the corner.",
      "zh": "一个手捧塞万提斯著作的男孩走出公寓楼门口，绕过一辆被某个混蛋停得让行人几乎无法通过的汽车，然后拐过街角。",
      "ja": "セルバンテスの本を抱えた少年が建物の入り口から出てきて、誰かの非常識な駐車で歩行者がかろうじて通れるような車を迂回し、角を曲がる。"
    },
    {
      "id": 2,
      "ru": "Перед ним пустынные кварталы, поля и высоковольтные вышки, а в физиономию дует ветер – как везде в Петербурге, но в этом районе особенно.",
      "en": "Before him stretch deserted blocks, fields, and high-voltage towers, while the wind blows in his face—as it does everywhere in St. Petersburg, but especially in this district.",
      "zh": "他面前是荒凉的街区、田野和高压输电塔，风吹在他脸上——这在彼得堡随处可见，但这个区域尤其明显。",
      "ja": "目の前には荒涼とした街区、野原、高圧鉄塔が広がり、風が彼の顔に吹き付ける――サンクトペテルブルクではどこでもそうだが、この地区では特に強い。"
    }
  ],
  "translator_notes": [
    "Chapter 1 opens with young Pavel Durov's childhood neighborhood in Primorsky district",
    "The 'boy with Cervantes' is young Pavel - Don Quixote was his favorite book",
    "Setting is near Gulf of Finland, explaining the constant wind"
  ],
  "total_sentences": 2,
  "page_type": "narrative"
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (1-99) |
| `chapter` | int | Chapter number (0 for front matter, 1-7 for chapters) |
| `chapter_title` | string | Russian title with English translation |
| `sentences` | array | Array of sentence objects |
| `sentences[].id` | int | Sequential sentence ID within page |
| `sentences[].ru` | string | Original Russian text |
| `sentences[].en` | string | English translation |
| `sentences[].zh` | string | Chinese translation (Simplified) |
| `sentences[].ja` | string | Japanese translation |
| `translator_notes` | array | Context, cultural notes, translation decisions |
| `total_sentences` | int | Count of sentences (for verification) |
| `page_type` | string | "front_matter", "narrative", "dialogue", "about_author" |

### JSON Quality Rules

1. **Every sentence has all 4 languages** - no null/empty values
2. **Valid JSON** - escape quotes properly, no trailing commas
3. **UTF-8 encoding** - Chinese/Japanese characters must be valid
4. **No skipped content** - every paragraph must be represented
5. **Sentence IDs are sequential** - 1, 2, 3, ... (no gaps)

---

## Chapter Reference

| Chapter | Pages | Title | Content |
|---------|-------|-------|---------|
| 0 | 1-4 | Front Matter | Title, copyright, table of contents |
| 0 | 5-6 | Предисловие (Preface) | Yuri Saprykin's introduction |
| 0 | 7-12 | Пролог (Prologue) | VK office scene, tone-setting |
| 1 | 13-22 | Ботанический сад (Botanical Garden) | Durov's childhood |
| 2 | 23-37 | Chapter 2 | University years |
| 3 | 38-50 | Chapter 3 | VKontakte founding |
| 4 | 51-64 | Chapter 4 | Scaling and growth |
| 5 | 65-78 | Chapter 5 | Business conflicts |
| 6 | 79-91 | Chapter 6 | Philosophy and maturity |
| 7 | 92-98 | Chapter 7 | Future outlook |
| - | 99 | Об авторе (About Author) | Author biography |

---

## Translation Quality Guidelines

### Voice Preservation
Pavel Durov's voice in this book is:
- **Sharp and direct**: Short sentences, confident assertions
- **Intellectually provocative**: References to philosophy, unconventional thinking
- **Anti-establishment**: Skepticism toward traditional business, authority
- **Technical precision**: Accurate when discussing code, systems

### Cultural Localization

**For English:**
- American English spelling (Stanford context)
- Tech industry idioms where appropriate
- Informal tech register, avoid British-isms

**For 中文:**
- Simplified Chinese (简体中文)
- Internet slang where appropriate (程序员 culture)
- Preserve Russian names in pinyin with characters: 杜罗夫 (Durov), 圣彼得堡 (St. Petersburg)

**For 日本語:**
- Appropriate formal-informal balance (match original register)
- Katakana for foreign names: ドゥーロフ (Durov)
- Japanese tech/startup culture parallels where helpful

### Common Terms (Use Consistently)

| Russian | English | Chinese | Japanese |
|---------|---------|---------|----------|
| ВКонтакте | VKontakte | VKontakte (VK) | VKontakte |
| Дуров | Durov | 杜罗夫 | ドゥーロフ |
| Санкт-Петербург | St. Petersburg | 圣彼得堡 | サンクトペテルブルク |
| нёрд/ботаник | nerd/geek | 极客/书呆子 | オタク/ギーク |
| хакер | hacker | 黑客 | ハッカー |
| стартап | startup | 创业公司 | スタートアップ |

---

## Workflow Summary

```
1. CHECK: What pages need translation?
   → ls translations/  # See what exists
   
2. READ: Get the Russian text
   → cat extracted/pages/page_XXX.txt
   
3. CONTEXT: Understand the chapter
   → cat research/chapter_summaries.md (relevant section)
   
4. TRANSLATE: Create translations
   → Parse sentences, translate each to EN/ZH/JA
   
5. SAVE: Output JSON file
   → Write to translations/page_XXX.json
   
6. COMMIT: Save your work
   → git add translations/page_XXX.json
   → git commit -m "[SHORT_ID] Translated page XXX"
   → git push
   
7. NEXT: Move to next page
   → Repeat for next page in your range
```

---

## What NOT To Do (Anti-Patterns)

### Translation Anti-Patterns
- ❌ **Skipping sentences** - Translate EVERYTHING on the page
- ❌ **Machine translation without review** - Review your output for naturalness
- ❌ **Literal translation of idioms** - Adapt idioms for target culture
- ❌ **Inconsistent terminology** - Use the glossary
- ❌ **Missing languages** - All 4 languages required for every sentence
- ❌ **Empty/null values** - No empty strings or null in JSON

### Workflow Anti-Patterns
- ❌ **Waiting for consensus** - Just start translating
- ❌ **Re-extracting PDF** - Use provided extracted/ files
- ❌ **Writing research docs** - They're already provided
- ❌ **Syncing before working** - Work first, sync is optional
- ❌ **Starting M0/M1 tasks** - Go directly to translation

---

## Commit Message Format

Simple and descriptive:
```
[SHORT_ID] Translated page XXX - Chapter Y

Brief note about content (optional)
```

Example:
```
[c68e] Translated page 23 - Chapter 2

University years, first programming projects
```

---

## Context Efficiency Tips

- Don't re-read entire chapters repeatedly; use chapter summaries
- Use the glossary for consistent terminology
- If stuck on a sentence > 5 minutes, add a translator note and move on
- Batch similar pages (e.g., do all of one chapter)
- Use previous page translations for context and consistency

---

## Page Type Guidelines

### Front Matter (Pages 1-4)
- Minimal text, mostly titles and metadata
- Keep formatting simple
- JSON should still have proper structure

### Preface (Pages 5-6)
- Formal tone, introduction by editor
- Preserve the journalistic style

### Prologue (Pages 7-12)
- Sets the tone for the entire book
- VK office scene, dynamic and cinematic
- Extra attention to atmosphere and mood

### Narrative Chapters (Pages 13-98)
- Main content, mixed dialogue and narration
- Preserve Durov's distinctive voice
- Add translator notes for cultural references

### About Author (Page 99)
- Brief biographical text
- Simple and factual

---

## Success Criteria

Your page translation is complete when:
1. ✅ JSON file exists: `translations/page_XXX.json`
2. ✅ All sentences from the page are included
3. ✅ Every sentence has ru, en, zh, ja fields (non-empty)
4. ✅ JSON is valid (no syntax errors)
5. ✅ Translations are natural and readable
6. ✅ Committed and pushed to your branch

---

## Quick Reference: Key Book Context

### Pavel Durov
- Born October 10, 1984, in Leningrad (St. Petersburg)
- Founded VKontakte in 2006 at age 22
- Known for libertarian views, anti-censorship stance
- Left Russia in 2014, founded Telegram

### VKontakte (VK)
- Founded: October 10, 2006
- "Russian Facebook" - largest social network in Russia/CIS
- Key events: founding, rapid growth, investor conflicts

### Book Context
- Written by Nikolai Kononov, journalist
- Published 2012-2013 (before Durov left VK)
- Covers 2006-2012 period primarily

---

## Start Translating Now!

If you're reading this, you have everything you need:
1. The extracted text files are in `extracted/pages/`
2. The output format is documented above
3. Research is in `research/` for context
4. Just pick a page and start translating

**Don't wait. Don't ask for permission. Don't sync with others first. TRANSLATE.**

---

*This document provides all context needed. There is no M0/M1 phase. There is no consensus. There is only translation.*
