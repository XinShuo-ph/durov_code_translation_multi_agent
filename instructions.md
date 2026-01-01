# Durov Code Book Translation Project

## Objective

Deliver a multilingual edition of "Код Дурова" (Durov Code) by Nikolai Kononov, translated into English, 中文 (Chinese), and 日本語 (Japanese). The final PDF presents each original Russian sentence followed by translations in all four languages, color-coded for visual distinction.

---

## Multi-Agent Collaborative Execution

**THIS PROJECT USES MULTIPLE AI AGENTS WORKING COLLABORATIVELY**

You are part of a team of workers translating this book in parallel. You will:
1. **Discover** other workers and know who's online
2. **Claim** pages to translate (one at a time)
3. **Sync** regularly to stay coordinated
4. **Share** your translations via git

See `PROTOCOL.md` for the complete communication protocol.

### Key Principles

- **Collaborative, not isolated**: You know who else is working and what they're doing
- **Simple workload**: Each worker claims pages (lowest available first)
- **Robust**: If workers disconnect, others can reclaim their pages
- **Sync regularly**: Fetch other workers' states every 2-3 minutes

---

## Quick Start (Agent Startup Sequence)

### Step 1: Identify Yourself
```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_SHORT_ID on $MY_BRANCH"
```

### Step 2: Create WORKER_STATE.md
Copy from `WORKER_STATE_TEMPLATE.md` and fill in your details. This **registers you as an active worker**.

### Step 3: Sync & Discover Other Workers
```bash
git fetch origin --prune

# Find all active workers
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null 2>&1; then
    short_id=$(echo "$branch" | grep -oE '[^-]+$' | tail -c 5)
    echo "Active worker: $short_id ($branch)"
  fi
done
```

### Step 4: Register Yourself
```bash
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: Registering as active worker
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Step 5: Claim a Page and Start Translating
1. Find the lowest page number not claimed or completed
2. Update WORKER_STATE.md with your claim
3. Push immediately
4. Start translating!

---

## Pre-Provided Resources

**All setup work is already done.** You have:

### 1. Extracted Text (Ready to Use)
```
extracted/
├── full.txt              # Complete book text
└── pages/
    ├── page_001.txt      # Page-by-page extraction
    ├── page_002.txt
    └── ... (all 99 pages)
```

### 2. Research Documents (For Context)
```
research/
├── durov_bio.md          # Pavel Durov biography
├── vk_history.md         # VKontakte company history
├── russia_context.md     # Russian cultural context
├── chapter_structure.md  # Page ranges for each chapter
├── chapter_summaries.md  # Chapter-by-chapter summaries
└── glossary.md           # Terminology consistency guide
```

### 3. Example Translations (Format Reference Only)
```
examples/
├── page_013_translation.json   # Example JSON format
├── page_043_translation.json   # Another example
└── format_demo.tex             # LaTeX template for PDF
```

**⚠️ NOTE**: The example JSON files show only a few sentences for format reference. They are NOT complete page translations. Your translations must include ALL sentences from each page.

### 4. PDF Generation Tools
```
tools/
├── compile_pages.py      # Generates PDF from JSON
├── README.md             # Tool documentation
└── requirements.txt      # Python dependencies
```

---

## File Structure

```
workspace/
├── instructions.md           # This file (read-only)
├── PROTOCOL.md               # Communication protocol (read-only)
├── STATE.md                  # Global project state
├── WORKER_STATE.md           # YOUR worker state (update frequently!)
├── WORKER_STATE_TEMPLATE.md  # Template for new workers
├── durov_code_book.pdf       # Original Russian PDF
│
├── extracted/                # PRE-EXTRACTED TEXT
│   ├── full.txt
│   └── pages/page_XXX.txt
│
├── research/                 # BACKGROUND RESEARCH
│   └── [various .md files]
│
├── examples/                 # FORMAT EXAMPLES
│   ├── page_013_translation.json
│   ├── page_043_translation.json
│   └── format_demo.tex
│
├── tools/                    # PDF GENERATION
│   ├── compile_pages.py
│   └── README.md
│
├── translations/             # YOUR OUTPUT (translations go here)
│   ├── page_001.json
│   ├── page_002.json
│   └── ...
│
└── output/                   # GENERATED PDFs (optional)
    ├── page_001.pdf
    └── ...
```

---

## Your Task: TRANSLATE

### The Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. SYNC: Fetch all branches, see who's online              │
│  2. CLAIM: Take the lowest available page                   │
│  3. READ: Get the Russian text from extracted/pages/        │
│  4. TRANSLATE: Russian → English, Chinese, Japanese         │
│  5. SAVE: Write translations/page_XXX.json                  │
│  6. BROADCAST: Commit & push, update WORKER_STATE.md        │
│  7. REPEAT: Claim next page                                 │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step for Each Page

#### 1. Read the Extracted Text
```bash
cat extracted/pages/page_013.txt
```

#### 2. Parse Into Sentences
You parse the Russian text into sentences. Use your judgment on sentence boundaries.

#### 3. Translate Each Sentence
For each Russian sentence, produce:
- **English**: Natural, accessible American English
- **Chinese**: Simplified Chinese (简体中文)
- **Japanese**: Standard Japanese

#### 4. Save as JSON
Save to `translations/page_XXX.json` using the exact format below.

#### 5. (Optional) Generate PDF
```bash
python3 tools/compile_pages.py translations/page_013.json output/
```

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
    },
    {
      "id": 2,
      "ru": "Перед ним пустынные кварталы...",
      "en": "Before him stretch deserted blocks...",
      "zh": "他面前是荒凉的街区...",
      "ja": "目の前には荒涼とした街区..."
    }
  ],
  "translator_notes": [
    "Chapter 1 opens with young Pavel Durov's childhood neighborhood",
    "The 'boy with Cervantes' is young Pavel - Don Quixote was his favorite book"
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
| `sentences[].id` | int | Sequential ID (1, 2, 3, ...) |
| `sentences[].ru` | string | Original Russian text |
| `sentences[].en` | string | English translation |
| `sentences[].zh` | string | Chinese translation (Simplified) |
| `sentences[].ja` | string | Japanese translation |
| `translator_notes` | array | Context, cultural notes |
| `total_sentences` | int | Count of sentences |
| `page_type` | string | "front_matter", "narrative", "dialogue", "about_author" |

### Quality Rules

1. **Every sentence has all 4 languages** - no null/empty values
2. **Valid JSON** - escape special characters properly
3. **UTF-8 encoding** - Chinese/Japanese must render correctly
4. **No skipped content** - include EVERY sentence from the page
5. **Sequential IDs** - 1, 2, 3, ... (no gaps)

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

## Reader Context

**Target Reader Profile:**
- Chinese-born graduate student at Stanford University (computational physics)
- Active Telegram user, programmer since high school
- Interested in Pavel Durov's worldview on technology, code, and life philosophy
- Reads Russian, English, Chinese, and Japanese

**Cultural Bridge Goals:**
- Make Russian tech/startup culture accessible to international readers
- Preserve Durov's distinctive voice and unconventional philosophy
- Localize references for global audiences

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

See `research/glossary.md` for the complete terminology guide.

---

## Collaboration Protocol Summary

### Regular Sync (Every 2-3 Minutes)
```bash
git fetch origin --prune
# Read other workers' WORKER_STATE.md files
# Update your "Known Workers" table
```

### Page Claiming
1. Sync first (always!)
2. Find lowest available page
3. Update WORKER_STATE.md with claim
4. Push immediately
5. Start translating

### Completing a Page
```bash
git add translations/page_XXX.json WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] DONE: Completed page XXX
HASH: $(sha256sum translations/page_XXX.json | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Handling Offline Workers
- Workers with heartbeats >10 min old are considered offline
- After 15 min, their claimed pages can be reclaimed
- Note in your WORKER_STATE.md when reclaiming

### If You Reconnect After Disconnect
1. Sync first (fetch all branches)
2. Check if your old page was reclaimed
3. If yes: claim next available page
4. If no: continue where you left off
5. Push immediately to show you're back

---

## PDF Generation

### Using the Compilation Tool
```bash
# Generate PDF for a single page
python3 tools/compile_pages.py translations/page_013.json output/

# This creates output/page_013.pdf
```

### Requirements
- XeLaTeX (texlive-xetex)
- xeCJK package (texlive-lang-chinese)
- Noto fonts (noto-fonts, noto-fonts-cjk)

### Color Scheme
| Language | Color |
|----------|-------|
| Russian | Black |
| English | Dark Blue |
| Chinese | Dark Red |
| Japanese | Dark Green |

---

## Anti-Patterns to Avoid

### Translation
- ❌ Skipping sentences - include EVERYTHING
- ❌ Literal translation of idioms - adapt appropriately
- ❌ Inconsistent terminology - use the glossary
- ❌ Losing Durov's voice - keep it sharp and provocative
- ❌ Invalid JSON - validate before committing

### Collaboration
- ❌ Claiming without syncing first
- ❌ Claiming multiple pages at once
- ❌ Forgetting to push claims immediately
- ❌ Letting heartbeat go stale (>5 min)
- ❌ Working in isolation - sync every 2-3 min

---

## Context Efficiency

- Use `research/chapter_summaries.md` instead of re-reading entire chapters
- Use `research/glossary.md` for consistent terminology
- If stuck on a sentence > 5 minutes, add a translator note and continue
- Each page should take roughly 10-20 minutes depending on density

---

## Continuous Execution Rules

**Do NOT pause** between pages to ask for confirmation. Keep working:

1. Complete page → Push → Claim next → Repeat
2. Sync every 2-3 minutes between pages
3. Continue until:
   - All pages are translated, OR
   - A blocking error requires help, OR
   - Context limit (~10k tokens remaining)

---

## Session End Protocol

When ending your session (or running low on context):

1. **Complete current page** if possible
2. **Update WORKER_STATE.md** with final status
3. **Push everything**:
   ```bash
   git add .
   git commit -m "[$MY_SHORT_ID] SESSION_END: Completed pages X-Y
   STATUS: [summary]
   HEARTBEAT: $(date +%s)"
   git push origin HEAD
   ```

If you can't complete your current page:
1. Update WORKER_STATE.md to release the claim
2. Push so others know the page is available

---

## Key Files Reference

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `WORKER_STATE.md` | Your status (claims, completions) | Every action |
| `PROTOCOL.md` | Communication rules | Read-only |
| `instructions.md` | Task instructions | Read-only |
| `translations/page_XXX.json` | Your output | Per page |
| `research/glossary.md` | Term consistency | Reference |

---

*Start translating! Sync regularly, push often, and coordinate with your team.*
