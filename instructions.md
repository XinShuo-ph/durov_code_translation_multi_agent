# Durov Code Book Translation Project

## Objective

Deliver a multilingual edition of "Код Дурова" (Durov Code) by Nikolai Kononov, translated into English, 中文 (Chinese), and 日本語 (Japanese). The final PDF presents each original Russian sentence followed by translations in all four languages, color-coded for visual distinction.

---

## Multi-Agent Parallel Execution

You are one of multiple agents translating this book in parallel. Each agent works on a separate git branch.

**Follow `PROTOCOL.md` for coordination.** The key idea: your branch name determines your starting page. You work forward from there, push after each page, and periodically sync to skip pages others have already done.

### Agent Startup (< 60 seconds)

```bash
# 1. Get your start page
MY_BRANCH=$(git branch --show-current)
SUFFIX=$(echo "$MY_BRANCH" | grep -oE '[^-]+$')
START=$(python3 -c "print(int('$SUFFIX', 16) % 99 + 1)")
echo "Starting at page $START"

# 2. Initial sync — see what's already translated
git fetch origin --prune
PREFIX=$(echo "$MY_BRANCH" | sed 's/-[^-]*$//')
for branch in $(git branch -r | grep "origin/cursor/$PREFIX" | tr -d ' '); do
    git ls-tree -r --name-only "$branch" -- translations/ 2>/dev/null
done | sort -u

# 3. Start translating immediately from your start page
```

**Your first commit must be a completed page translation. Not a state file.**

---

## Your Task: TRANSLATE

### Workflow Per Page

```
1. READ: Get the Russian text from extracted/pages/page_NNN.txt
2. PARSE: Split into sentences
3. TRANSLATE: Russian → English, Chinese, Japanese
4. SAVE: Write translations/page_NNN.json
5. PUSH: git add + commit + push
6. ADVANCE: Move to next page (skip if already done by another agent)
```

### Reading Source Text

```bash
cat extracted/pages/page_013.txt
```

All 99 pages are pre-extracted. No PDF parsing needed.

---

## JSON Output Format (MANDATORY)

Every page translation MUST follow this structure:

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
  "translator_notes": [
    "Chapter 1 opens with young Pavel Durov's childhood neighborhood"
  ],
  "total_sentences": 1,
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
| `sentences[].id` | int | Sequential ID (1, 2, 3, ...) |
| `sentences[].ru` | string | Original Russian text |
| `sentences[].en` | string | English translation |
| `sentences[].zh` | string | Chinese translation (Simplified) |
| `sentences[].ja` | string | Japanese translation |
| `translator_notes` | array | Context, cultural notes |
| `total_sentences` | int | Count of sentences |
| `page_type` | string | "front_matter", "narrative", "dialogue", "about_author" |

### Quality Rules

1. **Every sentence has all 4 languages** — no null/empty values
2. **Valid JSON** — escape special characters properly
3. **UTF-8 encoding** — Chinese/Japanese must render correctly
4. **No skipped content** — include EVERY sentence from the page
5. **Sequential IDs** — 1, 2, 3, ... (no gaps)

---

## Chapter Reference

| Chapter | Pages | Title | Content |
|---------|-------|-------|---------|
| 0 | 1-4 | Front Matter | Title, copyright, contents |
| 0 | 5-6 | Предисловие (Preface) | Yuri Saprykin's introduction |
| 0 | 7-12 | Пролог (Prologue) | VK office scene |
| 1 | 13-22 | Ботанический сад | Durov's childhood |
| 2 | 23-37 | Chapter 2 | University years |
| 3 | 38-50 | Chapter 3 | VKontakte founding |
| 4 | 51-64 | Chapter 4 | Scaling and growth |
| 5 | 65-78 | Chapter 5 | Business conflicts |
| 6 | 79-91 | Chapter 6 | Philosophy and maturity |
| 7 | 92-98 | Chapter 7 | Future outlook |
| - | 99 | Об авторе | About the author |

---

## Pre-Provided Resources

**All setup work is already done.** Do not redo it.

### Extracted Text (Ready to Use)
```
extracted/
├── full.txt              # Complete book text
└── pages/
    ├── page_001.txt      # Page-by-page extraction
    └── ... (all 99 pages)
```

### Research Documents (For Context — READ, don't recreate)
```
research/
├── durov_bio.md          # Pavel Durov biography
├── vk_history.md         # VKontakte company history
├── russia_context.md     # Russian cultural context
├── chapter_summaries.md  # Chapter-by-chapter summaries
└── glossary.md           # Terminology consistency guide
```

### Example Translations (Format Reference Only — don't retranslate these)
```
examples/
├── page_013_translation.json   # Example JSON format
└── page_043_translation.json   # Another example
```

### PDF Generation Tools
```
tools/
├── compile_pages.py      # Generates PDF from JSON
└── README.md             # Tool documentation
```

---

## Translation Quality Guidelines

### Voice Preservation
Pavel Durov's voice is:
- **Sharp and direct**: Short sentences, confident assertions
- **Intellectually provocative**: Philosophy, unconventional thinking
- **Anti-establishment**: Skepticism toward authority
- **Technical precision**: Accurate when discussing code/systems

### Cultural Localization

**For English:**
- American English spelling
- Tech industry idioms where appropriate
- Informal tech register

**For 中文:**
- Simplified Chinese (简体中文)
- Internet slang where appropriate (程序员 culture)
- Russian names in pinyin: 杜罗夫 (Durov), 圣彼得堡 (St. Petersburg)

**For 日本語:**
- Appropriate formal-informal balance
- Katakana for foreign names: ドゥーロフ (Durov)
- Japanese tech culture parallels where helpful

### Common Terms (from research/glossary.md)

| Russian | English | Chinese | Japanese |
|---------|---------|---------|----------|
| ВКонтакте | VKontakte | VKontakte (VK) | VKontakte |
| Дуров | Durov | 杜罗夫 | ドゥーロフ |
| Санкт-Петербург | St. Petersburg | 圣彼得堡 | サンクトペテルブルク |
| ботаник | nerd/geek | 书呆子 | オタク |
| стартап | startup | 创业公司 | スタートアップ |

---

## Reader Context

**Target Reader Profile:**
- Chinese-born graduate student at Stanford University (computational physics)
- Active Telegram user, programmer since high school
- Interested in Pavel Durov's worldview on technology, code, and life philosophy
- Reads Russian, English, Chinese, and Japanese

---

## Output Location

```
translations/         # JSON translations (one per page)
├── page_001.json
├── page_002.json
└── ...

output/               # Generated PDFs (optional)
├── page_001.pdf
└── ...
```

---

## Continuous Execution Rules

**Do NOT pause** between pages to ask for confirmation. Keep working:

1. Complete page → push → advance to next → repeat
2. Sync every ~5 pages to check what others have done
3. Continue until:
   - All 99 pages are translated, OR
   - A blocking error requires help, OR
   - Context limit is approaching

---

## Protocol Configuration for This Project

```
TOTAL_UNITS    = 99
OUTPUT_DIR     = translations
UNIT_FILENAME  = page_%03d.json
BRANCH_FILTER  = <your task prefix>
```

See `PROTOCOL.md` for the full coordination protocol.

---

## Anti-Patterns

### Translation
- Do not skip sentences — include EVERYTHING
- Do not translate idioms literally — adapt appropriately
- Do not use inconsistent terminology — check the glossary
- Do not lose Durov's voice — keep it sharp and provocative
- Do not commit invalid JSON — validate before committing

### Coordination
- Do not claim pages via state files — use your hash-assigned start position
- Do not build helper tools or scripts — translate pages
- Do not do research that already exists — read the research/ directory
- Do not stop after a few pages — keep going
- Do not start at page 1 unless that's your hash-assigned start
