# Durov Code Book Translation Project

## Objective
Deliver a multilingual edition of "Код Дурова" (Durov Code) by Nikolai Kononov, translated into English, 中文 (Chinese), and 日本語 (Japanese). The final PDF presents each original Russian page followed by 1-2 pages of translated text, where each sentence appears in all four languages in parallel, visually distinguished by color/font.

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

## Execution Mode

**CONTINUOUS EXECUTION:** Do NOT pause between tasks or pages to ask for confirmation. Complete all tasks sequentially until:
- All pages are translated, OR
- A blocking error requires user input, OR
- Context limit (~10k tokens remaining)

When a page is complete, immediately proceed to the next page.

---

## File Structure

```
workspace/
├── instructions.md          # This file (read-only reference)
├── STATE.md                  # CRITICAL: Current progress, next action, blockers
├── durov_code_book.pdf       # Original Russian book (99 pages)
├── README.md                 # Project overview
│
├── research/                 # Background research notes
│   ├── durov_bio.md          # Pavel Durov biography & key events
│   ├── vk_history.md         # VKontakte company history
│   ├── telegram_history.md   # Telegram history (for context)
│   ├── russia_context.md     # Russian cultural/political context
│   └── chapter_summaries.md  # Brief summary of each chapter
│
├── tools/                    # Technical implementation
│   ├── extract_text.py       # PDF text extraction script
│   ├── compile_pages.py      # LaTeX/PDF compilation script
│   ├── screenshot_verify.py  # Screenshot verification helper
│   └── requirements.txt      # Python dependencies
│
├── examples/                 # Demo pages (M1 deliverables)
│   ├── page_13_original.txt  # Extracted Russian text
│   ├── page_13_translated.pdf
│   ├── page_43_original.txt
│   ├── page_43_translated.pdf
│   └── format_demo.tex       # LaTeX template for 4-language display
│
├── translations/             # Main translation work
│   ├── raw/                  # First-pass translations
│   │   ├── page_001.json     # {ru, en, zh, ja} per sentence
│   │   ├── page_002.json
│   │   └── ...
│   ├── reviewed/             # After proofreading
│   │   ├── page_001.json
│   │   └── ...
│   └── final/                # After 3x review cycles
│       ├── page_001.json
│       └── ...
│
├── output/                   # Compiled PDF pages
│   ├── page_001_translated.pdf
│   ├── page_002_translated.pdf
│   └── ...
│
└── final/                    # Complete book
    └── durov_code_multilingual.pdf
```

---

## State Management Protocol

### On Session Start
1. **Read `STATE.md` first** - understand current progress
2. Read the current milestone's status
3. Resume from the documented next action
4. **Keep working until blocked or context exhausted**

### On Session End (or ~10k tokens remaining)
1. Update `STATE.md` with:
   - Current milestone and page number
   - Exact next action (be specific: page, sentence, issue)
   - Any blockers or failed attempts
   - Research findings that affect translation
2. Save all work in progress
3. **Do NOT start new pages with <15k tokens remaining**

### STATE.md Template
```markdown
# Current State
- **Milestone**: M1/M2/M3
- **Current Page**: [page number]
- **Status**: in_progress | blocked | ready_for_next

## Next Action
[Exactly what to do next. Be specific: page number, sentence, task.]

## Blockers (if any)
[What's preventing progress, what was tried]

## Research Notes for Current Page
[Key context needed for translation: names, places, cultural references]

## Session Log
- [date/session]: [pages completed, key decisions made]
```

---

## Milestones

### M0: Project Setup & Research Foundation
**Goal**: Establish tools, understand book structure, build knowledge base
**Duration**: 1 session

**Tasks:**
- [ ] Install dependencies (pdftotext, LaTeX, Python packages)
- [ ] Extract full text from PDF, verify extraction quality
- [ ] Create chapter structure document with page ranges
- [ ] Research and document:
  - Pavel Durov biography (key dates, events, philosophy)
  - VKontakte history (founding, growth, conflicts, sale)
  - Russian tech scene context (2006-2013 era)
  - Key people mentioned in book
- [ ] Read through entire book to understand narrative arc
- [ ] Create `research/chapter_summaries.md` with 2-3 sentence summaries

**Exit Criteria:**
- All research documents created
- Book structure fully mapped
- Ready to start format exploration

---

### M1: Format Exploration & Demo Pages
**Goal**: Determine optimal technical approach, create demo pages 13 and 43
**Duration**: 1-2 sessions

**Tasks:**
- [ ] Explore format options:
  - LaTeX with CJK support (xelatex + xeCJK)
  - Python + reportlab/fpdf2 with multilingual fonts
  - Pandoc + custom templates
- [ ] Design 4-language parallel display format:
  - Color coding: Russian (black), English (blue), 中文 (red), 日本語 (green)
  - OR: Font variation (serif vs sans-serif)
  - Sentence numbering for alignment
- [ ] Create LaTeX template `tools/format_demo.tex`
- [ ] Extract page 13 (Chapter 1 opening) text
- [ ] Quick-translate page 13 (focus on format, not polish)
- [ ] Compile page 13 demo PDF
- [ ] Screenshot and verify rendering
- [ ] Repeat for page 43 (mid-chapter narrative)
- [ ] Document chosen approach in `tools/README.md`

**Exit Criteria:**
- `examples/page_13_translated.pdf` exists and renders correctly
- `examples/page_43_translated.pdf` exists and renders correctly
- User has reviewed and approved format
- Technical pipeline documented

---

### M2: Professional Translation (99 Iterations)
**Goal**: Translate all 99 pages with professional, localized quality
**Duration**: 50-100 sessions (depending on page complexity)

**Per-Page Workflow (One Iteration):**

#### Phase 1: Context Gathering (per page)
1. **Read current chapter context**
   - Skim 5 pages before and after current page
   - Note narrative arc, key themes, character dynamics
   
2. **Research page-specific references**
   - Names: Who is mentioned? Their background, role
   - Places: St. Petersburg locations, Russian geography
   - Events: Historical/tech events referenced
   - Terminology: Tech terms, Russian internet slang
   - Cultural references: Soviet/Russian culture, memes

3. **Online research (minimum 3 searches per page)**
   - Search: "Pavel Durov [specific topic from page]"
   - Search: "VKontakte [specific event/person from page]"
   - Search: "[Russian term] meaning cultural context"
   - Document findings in translation notes

#### Phase 2: Translation
4. **Sentence-by-sentence translation**
   - Preserve sentence structure for parallel display
   - Russian → English: Prioritize clarity, natural flow
   - Russian → 中文: Consider mainland Chinese internet culture, 网络用语
   - Russian → 日本語: Consider Japanese netizen culture, ネット用語
   
5. **Localization considerations**
   - Adapt idioms appropriately (don't translate literally)
   - Add translator notes for culture-specific references
   - Maintain Durov's voice: sharp, confident, unconventional

#### Phase 3: Quality Assurance
6. **First review pass**
   - Read all 4 versions aloud
   - Check for awkward phrasing, grammatical errors
   - Verify terminology consistency with previous pages

7. **Second review pass (different perspective)**
   - Read as target audience (Stanford grad student)
   - Check: Does the humor land? Is the personality preserved?
   - Check: Are Russian references accessible?

8. **Third review pass (final polish)**
   - Cross-check with original Russian
   - Verify no sentences skipped or merged incorrectly
   - Confirm formatting will work in LaTeX

#### Phase 4: Compilation
9. **Save translation JSON**
   ```json
   {
     "page": 13,
     "chapter": 1,
     "sentences": [
       {
         "id": 1,
         "ru": "Мальчик с томом Сервантеса выходит из подъезда...",
         "en": "A boy with a volume of Cervantes exits the building entrance...",
         "zh": "一个手捧塞万提斯著作的男孩走出公寓楼...",
         "ja": "セルバンテスの本を持った少年が建物の入り口を出る..."
       }
     ],
     "translator_notes": ["Reference to Don Quixote - Durov's favorite book"],
     "research_used": ["Durov childhood in St. Petersburg", "Soviet panel housing"]
   }
   ```

10. **Compile to PDF**
    - Run LaTeX compilation
    - Verify output renders correctly
    - Save to `output/page_XXX_translated.pdf`

11. **Update STATE.md and commit**

**Page Groups (for progress tracking):**
- Pages 1-4: Title, copyright, contents (minimal translation)
- Pages 5-6: Preface (set the tone)
- Pages 7-12: Prologue (critical - introduces narrative style)
- Pages 13-22: Chapter 1 - Childhood/background
- Pages 23-37: Chapter 2 - University years
- Pages 38-50: Chapter 3 - VKontakte founding
- Pages 51-64: Chapter 4 - Growth and challenges
- Pages 65-78: Chapter 5 - Business conflicts
- Pages 79-91: Chapter 6 - Maturity and philosophy
- Pages 92-98: Chapter 7 - Future outlook
- Page 99: About the author

**Exit Criteria per page:**
- Translation JSON saved to `translations/final/page_XXX.json`
- PDF rendered and saved to `output/page_XXX_translated.pdf`
- No awkward phrasing (passed 3 review cycles)
- STATE.md updated with page completion

---

### M3: Final Assembly
**Goal**: Compile complete multilingual book
**Duration**: 1-2 sessions

**Tasks:**
- [ ] Merge all individual PDFs in correct order
- [ ] Add table of contents (multilingual)
- [ ] Add translator's note (explaining format, approach)
- [ ] Create cover page (multilingual title)
- [ ] Final quality check: spot-check 10 random pages
- [ ] Export to `final/durov_code_multilingual.pdf`

**Exit Criteria:**
- Complete PDF exists
- All 99 original pages + translations included
- File opens correctly, all fonts render

---

## Translation Quality Guidelines

### Voice Preservation
Pavel Durov's voice in this book is:
- **Sharp and direct**: Short sentences, confident assertions
- **Intellectually provocative**: References to philosophy, unconventional thinking
- **Anti-establishment**: Skepticism toward traditional business, authority
- **Technical precision**: Accurate when discussing code, systems

### Cultural Localization Rules

**For English:**
- American English spelling (Stanford context)
- Tech industry idioms where appropriate
- Avoid British-isms, maintain informal tech register

**For 中文:**
- Mainland Simplified Chinese
- Internet slang where appropriate (but not overused)
- Consider 程序员 culture references
- Preserve Russian proper nouns in pinyin with characters: 杜罗夫 (Durov), 圣彼得堡 (St. Petersburg)

**For 日本語:**
- Formal-informal balance (match original register)
- Katakana for foreign names: ドゥーロフ (Durov)
- Consider Japanese tech/startup culture parallels
- Appropriate use of honorifics based on context

### Terminology Consistency

Maintain a glossary (`research/glossary.md`) for:
- Character names (Russian → transliteration + meaning)
- Company names (VKontakte, Mail.ru, etc.)
- Technical terms (backend, frontend, server, etc.)
- Russian cultural terms (гопник, ботаник, etc.)

---

## Research Protocol

### Before Each Chapter
1. Skim entire chapter (10-15 pages)
2. Identify major themes, new characters, key events
3. Create chapter research notes

### Before Each Page (minimum)
1. **Context search**: What is happening in the narrative?
2. **Person search**: Any new names → research background
3. **Term search**: Any unfamiliar Russian terms → meaning + cultural context
4. **Event search**: Any historical events → verify facts, find additional context

### Research Sources Priority
1. Wikipedia (en, ru, zh, ja) - for facts
2. News archives (for VKontakte/Durov coverage)
3. Tech blogs/forums (for terminology)
4. Cultural forums (for slang/idiom context)

---

## Anti-Patterns (Avoid These)

- ❌ **Skipping research**: Every page needs context research
- ❌ **Literal translation**: Idioms must be adapted, not translated word-for-word
- ❌ **Inconsistent terminology**: Use glossary, don't reinvent translations
- ❌ **Starting new page with <15k tokens**: Finish current page or save state
- ❌ **Ignoring cultural context**: Russian references need explanation/adaptation
- ❌ **Machine translation without review**: All output must be human-reviewed 3x
- ❌ **Losing Durov's voice**: Sharp, provocative, unconventional - preserve this
- ❌ **Overlong sessions without saves**: Update STATE.md every 5 pages minimum

---

## Context Efficiency Tips

- Don't re-read entire chapters repeatedly; use chapter summaries
- Build and reuse glossary for common terms
- Keep research notes minimal but precise
- If stuck on a sentence > 10 minutes, mark for review and continue
- Batch similar research (e.g., all names in a chapter)
- Use previous page translations for context and consistency

---

## Token Budget Guidelines

| Phase | Budget | Activities |
|-------|--------|------------|
| Orientation | ~3k | Read STATE.md, understand where we are |
| Research | ~5k | Online searches, context gathering for current pages |
| Translation | ~15k per page | 4 languages × sentence count |
| Review | ~5k per page | 3 review passes |
| Handoff | ~5k | Update STATE.md, commit, verify saves |

**Per-session target**: 3-5 pages completed (depending on density)

**If blocked for >10 minutes on same issue:**
1. Document the issue in translator notes
2. Mark sentence with [REVIEW NEEDED]
3. Continue to next sentence/page
4. Return in future session with fresh perspective

---

## Key Context: Pavel Durov & VKontakte

### Pavel Durov
- Born October 10, 1984, in Leningrad (St. Petersburg), Russia
- Father: Valery Durov, professor of philology
- Brother: Nikolai Durov, mathematician and key VK developer
- Founded VKontakte in 2006 at age 22
- Known for libertarian views, anti-censorship stance
- Left Russia in 2014, founded Telegram
- As of 2024: CEO of Telegram, estimated net worth ~$15 billion

### VKontakte (VK)
- Founded: October 10, 2006
- "Russian Facebook" - largest social network in Russia/CIS
- By 2012: 100+ million users
- 2014: Durov lost control, sold to Mail.ru Group
- Key events covered in book: founding, rapid growth, investor conflicts

### Book Context
- Written by Nikolai Kononov, journalist
- Published 2012-2013 (before Durov left VK)
- Covers 2006-2012 period primarily
- Mix of biography, tech history, and Russian business culture

---

## Git Workflow

### After Every Completed Page
```bash
cd /workspace
git add -A
git commit -m "Translate page XX: [brief content note]"
```

### After Every Session
```bash
git add -A
git commit -m "Session end: completed pages XX-YY, next: ZZ"
```

### Commit Message Format
- `M0: Setup research foundation and tools`
- `M1: Demo page 13 format complete`
- `M1: Demo page 43 format complete`
- `M2 Page 15: Chapter 1 childhood narrative`
- `M2 Pages 20-25: Chapter 1 complete`
- `M3: Final assembly complete`

---

## Quick Reference: Book Structure

| Pages | Section | Content |
|-------|---------|---------|
| 1-4 | Front Matter | Title, ISBN, Contents |
| 5-6 | Предисловие (Preface) | Yuri Saprykin's introduction |
| 7-12 | Пролог (Prologue) | VK office scene, sets tone |
| 13-22 | Глава 1 (Chapter 1) | Durov's childhood, family, St. Petersburg |
| 23-37 | Глава 2 (Chapter 2) | University years, early projects |
| 38-50 | Глава 3 (Chapter 3) | VKontakte founding, early growth |
| 51-64 | Глава 4 (Chapter 4) | Scaling challenges, team building |
| 65-78 | Глава 5 (Chapter 5) | Business conflicts, investor relations |
| 79-91 | Глава 6 (Chapter 6) | Philosophy, worldview, maturity |
| 92-98 | Глава 7 (Chapter 7) | Future, legacy |
| 99 | Об авторе | About the author |

---

## Starting the Project

To begin, create `STATE.md`:

```markdown
# Current State
- **Milestone**: M0
- **Task**: Project setup
- **Status**: ready_to_start

## Next Action
1. Install dependencies (pdftotext, texlive, python packages)
2. Extract full book text
3. Create research documents

## Blockers
None

## Session Log
- [date]: Project initiated
```

Then execute M0 tasks in order.

---

*This document should be treated as read-only during execution. Update only STATE.md and task-specific files.*
