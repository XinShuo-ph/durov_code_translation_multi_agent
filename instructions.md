# Durov Code Book Translation Project

## Objective

Deliver a multilingual edition of "Код Дурова" (Durov Code) by Nikolai Kononov, translated into English, 中文 (Chinese), and 日本語 (Japanese). The final PDF presents each original Russian sentence followed by translations in all four languages, color-coded for visual distinction.

---

## Multi-Agent Parallel Execution

**THIS PROJECT USES MULTIPLE AI AGENTS WORKING IN PARALLEL**

You are one of N parallel agents. Follow `PROTOCOL.md` for coordination.

### How It Works

1. **Phase 1 — STRIPE**: You receive a deterministic set of pages based on your sorted position among peers. No coordination needed. Just translate and push.
2. **Phase 2 — SCAVENGE**: After your stripe is done, use `tools/coord.py` to find remaining gaps and fill them.
3. **Balance Gate**: If you get too far ahead, you'll be asked to review a peer's work before claiming more pages.

### Key Principles

- **Produce output from minute one** — all setup is pre-done, start translating immediately
- **Deterministic page assignment** — no racing for the same page
- **Validate before pushing** — use `tools/validate_translation.py`
- **Push after every page** — make your work visible to peers
- **Never stop voluntarily** — keep translating until done or out of context

---

## Quick Start (< 90 Seconds to First Page)

### Step 1: Identify Yourself
```bash
MY_BRANCH=$(git branch --show-current)
MY_ID=${MY_BRANCH##*-}
BATCH_PREFIX=$(echo "$MY_BRANCH" | sed 's/-[^-]*$//')
echo "I am: $MY_ID on $MY_BRANCH"
```

### Step 2: Discover Peers and Compute Your Stripe
```bash
git fetch origin --prune
PEERS=($(git branch -r | grep "origin/${BATCH_PREFIX}-" | sed 's|.*origin/||;s|.*-||' | sort -u))
N=${#PEERS[@]}
MY_POS=0
for i in "${!PEERS[@]}"; do [[ "${PEERS[$i]}" == "$MY_ID" ]] && MY_POS=$i && break; done

TOTAL_PAGES=99
echo "Worker $MY_POS of $N. My stripe pages:"
for ((p=MY_POS+1; p<=TOTAL_PAGES; p+=N)); do echo "  Page $p"; done
```

### Step 3: Initialize State and Register
```bash
cp WORKER_STATE_TEMPLATE.json WORKER_STATE.json
# Update worker_id, branch, batch_prefix, heartbeat in the JSON
git add WORKER_STATE.json
git commit -m "[$MY_ID] START: registered, stripe computed
HEARTBEAT: $(date +%s)"
git push -u origin HEAD
```

### Step 4: Start Translating Your Stripe Pages
Translate each page in your stripe sequentially. No sync needed during Phase 1.

---

## Pre-Provided Resources

**All setup work is already done.** Do NOT regenerate any of these. Do NOT run setup/install phases.

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

**NOTE**: The example JSON files show only a few sentences for format reference. They are NOT complete page translations. Your translations must include ALL sentences from each page.

### 4. Coordination & Validation Tools
```
tools/
├── coord.py                  # Coordination tool (Phase 2 scavenging)
├── validate_translation.py   # JSON validation (mandatory before push)
├── compile_pages.py          # Generates PDF from JSON (optional)
├── README.md                 # Tool documentation
└── requirements.txt          # Python dependencies
```

---

## File Structure

```
workspace/
├── instructions.md              # This file (read-only)
├── PROTOCOL.md                  # Parallel work protocol (read-only)
├── STATE.md                     # Global project state
├── WORKER_STATE.json            # YOUR worker state (update per page)
├── WORKER_STATE_TEMPLATE.json   # Template for new workers
├── durov_code_book.pdf          # Original Russian PDF
│
├── extracted/                   # PRE-EXTRACTED TEXT
│   ├── full.txt
│   └── pages/page_XXX.txt
│
├── research/                    # BACKGROUND RESEARCH
│   └── [various .md files]
│
├── examples/                    # FORMAT EXAMPLES
│   └── [example JSONs + LaTeX]
│
├── tools/                       # COORDINATION + VALIDATION + PDF
│   ├── coord.py
│   ├── validate_translation.py
│   └── compile_pages.py
│
├── translations/                # YOUR OUTPUT (translations go here)
│   └── page_XXX.json
│
├── reviews/                     # REVIEW NOTES (during balance gate HOLD)
│   └── page_XXX.<worker_id>.md
│
└── output/                      # GENERATED PDFs (optional)
    └── page_XXX.pdf
```

---

## Workflow Per Page

```
┌──────────────────────────────────────────────────────────────┐
│  1. READ: Get the Russian text from extracted/pages/         │
│  2. TRANSLATE: Russian → English, Chinese, Japanese          │
│  3. SAVE: Write translations/page_XXX.json                   │
│  4. VALIDATE: python3 tools/validate_translation.py <file>   │
│  5. PUSH: git add + commit + push                            │
│  6. REPEAT: Next stripe page (Phase 1) or coord.py (Phase 2)│
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step for Each Page

#### 1. Read the Extracted Text
```bash
cat extracted/pages/page_013.txt
```

#### 2. Parse Into Sentences
Parse the Russian text into sentences. Use your judgment on sentence boundaries.

#### 3. Translate Each Sentence
For each Russian sentence, produce:
- **English**: Natural, accessible American English
- **Chinese**: Simplified Chinese (简体中文)
- **Japanese**: Standard Japanese

#### 4. Save as JSON
Save to `translations/page_XXX.json` using the format below.

#### 5. Validate
```bash
python3 tools/validate_translation.py translations/page_XXX.json
```

#### 6. Commit and Push
```bash
git add translations/page_XXX.json WORKER_STATE.json
git commit -m "[$MY_ID] DONE: page XXX
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

#### 7. (Optional) Generate PDF
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

1. **Every sentence has all 4 languages** — no null/empty values
2. **Valid JSON** — escape special characters properly
3. **UTF-8 encoding** — Chinese/Japanese must render correctly
4. **No skipped content** — include EVERY sentence from the page
5. **Sequential IDs** — 1, 2, 3, ... (no gaps)
6. **Validate before pushing** — `python3 tools/validate_translation.py <file>`

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

## Anti-Patterns to Avoid

### Translation
- Do not skip sentences — include EVERYTHING
- Do not literally translate idioms — adapt appropriately
- Do not use inconsistent terminology — use the glossary
- Do not lose Durov's voice — keep it sharp and provocative
- Do not push invalid JSON — validate before committing

### Collaboration
- Do not run setup/install phases — everything is pre-done
- Do not wait for consensus or votes — start translating immediately
- Do not start at page 1 — use your stripe
- Do not build custom tools — use what's provided
- Do not claim multiple pages at once — one at a time
- Do not batch pages before pushing — push after every page

---

## Context Efficiency

- Use `research/chapter_summaries.md` instead of re-reading entire chapters
- Use `research/glossary.md` for consistent terminology
- If stuck on a sentence > 5 minutes, add a translator note and continue
- Each page should take roughly 10-20 minutes depending on density

---

## Continuous Execution Rules

**Do NOT pause** between pages to ask for confirmation. Keep working:

1. Complete page → Validate → Push → Next stripe page → Repeat
2. After stripe is done, switch to Phase 2 (scavenge via `tools/coord.py`)
3. Continue until:
   - All pages are translated, OR
   - A blocking error requires help, OR
   - Context limit approaching

---

## Session End Protocol

When ending your session (or running low on context):

1. **Complete current page** if possible
2. **Validate and push** the completed page
3. **Update WORKER_STATE.json** — set status to `done`, clear claimed_page
4. **Push everything**:
   ```bash
   git add .
   git commit -m "[$MY_ID] END: session complete
   HEARTBEAT: $(date +%s)"
   git push origin HEAD
   ```

If you can't complete your current page:
1. Update WORKER_STATE.json to release the claim (set claimed_page to null)
2. Push so others know the page is available

---

## PDF Generation

### Using the Compilation Tool
```bash
python3 tools/compile_pages.py translations/page_013.json output/
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

## Key Files Reference

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `WORKER_STATE.json` | Your status (claims, completions) | Every page |
| `PROTOCOL.md` | Parallel work protocol | Read-only |
| `instructions.md` | Task instructions | Read-only |
| `translations/page_XXX.json` | Your output | Per page |
| `research/glossary.md` | Term consistency | Reference |

---

*Start translating your stripe immediately. Validate before pushing. Never stop.*
