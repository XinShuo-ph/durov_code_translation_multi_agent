# Durov Code Book Translation Project

## Objective
Deliver a multilingual edition of "Код Дурова" (Durov Code) by Nikolai Kononov, translated into English, 中文 (Chinese), and 日本語 (Japanese). The final PDF presents each original Russian page followed by 1-2 pages of translated text, where each sentence appears in all four languages in parallel, visually distinguished by color/font.

---

## Multi-Agent Parallel Execution

**THIS PROJECT USES MULTIPLE AI AGENTS WORKING IN PARALLEL**

See `PROTOCOL.md` for the complete communication protocol. Key points:

### Agent Identity
- Each agent operates on its own `cursor/*` branch (names are random, created by Cursor)
- **FIRST ACTION**: Identify your branch and derive your Short ID (last 4 chars)
- Maintain `WORKER_STATE.md` as your state broadcast AND registration file
- **A branch with WORKER_STATE.md = An active worker**

### Identifying Yourself
```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
# Example: cursor/multi-agent-parallel-translation-cca9 → cca9
```

### Discovering Other Workers
```bash
git fetch origin --all --prune
# Find all cursor/* branches with WORKER_STATE.md
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||'); do
  git show "origin/${branch}:WORKER_STATE.md" &>/dev/null && echo "Active: $branch"
done
```

### Communication via Git
- **Commit = Broadcast** your state to other agents
- **Push = Send** your message to the network
- **Pull = Receive** messages from other agents
- **PULL EVERY 60-120 SECONDS** - this is mandatory

### Commit Message Format
```
[SHORT_ID] [MILESTONE] [ACTION]: [description]
STATE: [milestone].[task] = [status]
PAGES: [relevant pages]
HEARTBEAT: [unix timestamp]
```

### Parallel Execution Philosophy
This is like MPI (Message Passing Interface) for AI agents:
- No shared memory - only message passing via git
- Time unit is ~60 seconds (push/pull + thinking)
- Frequent commits prevent work duplication
- Consensus before critical transitions
- Quorum = >50% of **active workers** (those with WORKER_STATE.md)

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

**PARALLEL MULTI-AGENT EXECUTION WITH CONTINUOUS PROGRESS**

### Agent Startup Sequence (MANDATORY)
```
1. IDENTIFY YOURSELF
   MY_BRANCH=$(git branch --show-current)
   MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
   # Example: cursor/multi-agent-parallel-translation-cca9 → cca9

2. CREATE/UPDATE WORKER_STATE.md
   # Copy from WORKER_STATE_TEMPLATE.md if first time
   # Fill in your branch name and short ID
   # This file REGISTERS you as an active worker!

3. DISCOVER OTHER WORKERS
   git fetch origin --all --prune
   # Find all cursor/* branches with WORKER_STATE.md
   # Read their states, build global picture

4. BROADCAST YOUR STATUS
   git add WORKER_STATE.md
   git commit -m "[SHORT_ID] SYNC: Starting session
   HEARTBEAT: $(date +%s)"
   git push origin HEAD

5. BEGIN WORK BASED ON GLOBAL STATE
```

### Continuous Execution Rules
- **Do NOT pause** between tasks to ask for confirmation
- **Commit and push** after every significant action
- **Pull from all workers** every 60-120 seconds
- Continue until:
  - All pages are translated, OR
  - A blocking error requires coordination, OR
  - Context limit (~10k tokens remaining)

### Communication Cadence
| Action | Frequency |
|--------|-----------|
| Pull all worker branches | Every 60-120 seconds |
| Push state updates | After every task completion |
| Heartbeat commit | Every 5 minutes if idle |

---

## File Structure

```
workspace/
├── instructions.md           # Task instructions (read-only)
├── PROTOCOL.md               # Multi-agent communication protocol (read-only)
├── STATE.md                  # Global project state (shared)
├── WORKER_STATE.md           # YOUR worker state (update frequently!)
├── WORKER_STATE_TEMPLATE.md  # Template for new workers
├── durov_code_book.pdf       # Original Russian book (99 pages)
├── README.md                 # Project overview
│
├── research/                 # Background research notes
│   ├── durov_bio.md          # Pavel Durov biography & key events
│   ├── vk_history.md         # VKontakte company history
│   ├── telegram_history.md   # Telegram history (for context)
│   ├── russia_context.md     # Russian cultural/political context
│   ├── glossary.md           # Terminology consistency
│   └── chapter_summaries.md  # Brief summary of each chapter
│
├── tools/                    # Technical implementation
│   ├── extract_text.py       # PDF text extraction script
│   ├── compile_pages.py      # LaTeX/PDF compilation script
│   ├── verify_sync.py        # Multi-worker sync verification
│   ├── claim_page.sh         # Page claiming helper script
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

### Multi-Agent File Ownership
| File | Ownership | Update By |
|------|-----------|-----------|
| `instructions.md` | Read-only | Never |
| `PROTOCOL.md` | Read-only | Never |
| `STATE.md` | Shared | Periodic consensus updates |
| `WORKER_STATE.md` | Per-worker | Frequently (each worker their own) |
| `research/*` | Shared | After M0 consensus |
| `translations/raw/*` | Per-page | Claiming worker |
| `translations/final/*` | Per-page | After verification |
| `output/*` | Per-page | Claiming worker |

---

## State Management Protocol (Multi-Agent)

### On Session Start
1. **IDENTIFY** your worker ID from branch name
2. **CREATE/UPDATE** `WORKER_STATE.md` with your status
3. **SYNC** - Fetch all worker branches, read their states
4. **BROADCAST** - Commit and push your initial state
5. **ORIENT** - Determine next action based on global state
6. **EXECUTE** - Work on next task, committing frequently

### During Session
1. **SYNC every 60-120 seconds** - Pull all worker branches
2. **COMMIT after every significant action** - Don't batch
3. **PUSH immediately** - Your state must be visible
4. **CHECK for conflicts** - Re-pull after claiming resources
5. **UPDATE HEARTBEAT** - In every commit

### On Session End (or ~10k tokens remaining)
1. **Complete current task** if possible (don't leave mid-page)
2. **Release claims** - If you can't finish, un-claim the page
3. **Update WORKER_STATE.md** with final status
4. **Commit and push** with descriptive message:
   ```
   [WORKER-XX] SESSION END: [summary]
   COMPLETED: [list of completed items]
   IN_PROGRESS: [anything left unfinished]
   HEARTBEAT: [timestamp]
   ```

### WORKER_STATE.md Template
```markdown
# Worker [ID] State

## Identity
- **Worker ID**: [01-16]
- **Branch**: worker/[ID]/durov-translation
- **Last Updated**: [ISO 8601 timestamp]
- **Heartbeat**: [Unix timestamp]

## Current Milestone
- **Milestone**: M0 | M1 | M2 | M3
- **Status**: working | waiting | blocked | completed

## M0/M1 Task Status
[Table of tasks with status and hashes]

## M2 Page Claims
[Table of claimed/completed pages]

## Consensus Votes
[Table of votes cast]

## Observed Workers
[Table of other workers' last seen states]

## Messages
[Any messages for other workers]

## Blockers
[Any issues preventing progress]
```

---

## Milestones

### M0: Project Setup & Research Foundation (PARALLEL - ALL WORKERS)
**Goal**: Establish tools, understand book structure, build knowledge base
**Execution**: All 16 workers execute independently, then verify consensus

**Tasks (each worker completes independently):**

| Task ID | Description | Verification |
|---------|-------------|--------------|
| M0.1 | Install dependencies (pdftotext, LaTeX, Python) | Command success check |
| M0.2 | Extract full text from PDF | Hash of extracted text |
| M0.3 | Create chapter structure document | Hash of chapter_structure.md |
| M0.4 | Research: Pavel Durov biography | Hash of durov_bio.md |
| M0.5 | Research: VKontakte history | Hash of vk_history.md |
| M0.6 | Research: Russian tech context | Hash of russia_context.md |
| M0.7 | Read entire book, create chapter summaries | Hash of chapter_summaries.md |

**Parallel Execution Protocol:**
1. Each worker completes all tasks independently
2. After each task, broadcast status:
   ```
   [WORKER-XX] M0 COMPLETE: [Task ID] done
   STATE: M0.[task_id] = done
   HASH: [output hash first 8 chars]
   HEARTBEAT: [timestamp]
   ```
3. Pull other workers' states every 60 seconds
4. When a task is done multiple ways, vote on best solution
5. After all tasks done, run cross-verification

**Consensus Protocol for M0:**
- If outputs have different hashes, workers vote
- >50% of **active workers** agreement adopts that version
- Losing workers adopt winning version
- All active workers must have identical hashes before M1

**Exit Criteria:**
- All active workers report all tasks DONE
- All output hashes match across workers
- Verification commits from all active workers

---

### M1: Format Exploration & Demo Pages (PARALLEL - ALL WORKERS)
**Goal**: Determine optimal technical approach, create demo pages 13 and 43
**Execution**: All 16 workers explore, vote on approach, then verify

**Tasks (each worker explores independently):**

| Task ID | Description | Deliverable |
|---------|-------------|-------------|
| M1.1 | Explore LaTeX (xelatex + xeCJK) approach | Working template or failure report |
| M1.2 | Explore Python (reportlab/fpdf2) approach | Working template or failure report |
| M1.3 | Design color/font scheme | Proposal document |
| M1.4 | Create demo template | Template file |
| M1.5 | Translate page 13 (quick pass) | page_13_demo.pdf |
| M1.6 | Translate page 43 (quick pass) | page_43_demo.pdf |
| M1.7 | Document chosen approach | tools/README.md |

**Parallel Execution Protocol:**
1. Workers may specialize (e.g., Workers 1-8 try LaTeX, 9-16 try Python)
2. Broadcast exploration results:
   ```
   [WORKER-XX] M1 RESULT: [approach] = [success/fail]
   DETAILS: [brief findings]
   HEARTBEAT: [timestamp]
   ```
3. Vote on final approach when multiple solutions exist
4. All workers must produce identical demo PDFs

**Consensus Voting:**
```
[WORKER-XX] VOTE: format_approach = latex_xecjk
REASON: [brief justification]
HEARTBEAT: [timestamp]
```

**Cross-Verification Before M2:**
Each worker MUST verify:
1. My test scripts produce same output with other workers' code
2. Other workers' test scripts produce same output with my code
3. All active worker branches produce byte-identical demo PDFs

**Verification Commit:**
```
[SHORT_ID] VERIFY: M1 cross-check passed
VERIFIED_WITH: [list of short IDs of all active workers]
DEMO_13_HASH: [hash]
DEMO_43_HASH: [hash]
READY_FOR_M2: true
HEARTBEAT: [timestamp]
```

**Exit Criteria:**
- All active workers report READY_FOR_M2: true
- All verification hashes match
- Technical pipeline documented and agreed upon

---

### M2: Professional Translation (PARALLEL - PAGE DISTRIBUTION)
**Goal**: Translate all 99 pages with professional, localized quality
**Execution**: 16 workers translate in parallel, each claiming pages dynamically

**Initial Page Assignment:**
No fixed assignment. Each worker claims the **lowest available page** dynamically.

When M2 begins:
- All workers sync and see pages 1-99 available
- Each worker claims the lowest unclaimed page
- Natural distribution happens as workers claim in parallel

**Dynamic Page Claiming Protocol:**
Each worker claims the next available page:

```python
def get_next_page(worker_id, global_state):
    """
    1. Pull all worker states
    2. Identify pages: claimed, completed, available
    3. Claim lowest available page number
    """
    all_pages = set(range(1, 100))  # Pages 1-99
    claimed = global_state.claimed_pages()
    completed = global_state.completed_pages()
    available = sorted(all_pages - claimed - completed)
    
    if available:
        return available[0]  # Lowest available
    return None  # All done!
```

**Page Claim Commit:**
```
[SHORT_ID] M2 CLAIM: Starting page YY
STATE: M2.translating
PAGES: YY
HEARTBEAT: [timestamp]
```
**⚠️ PUSH IMMEDIATELY AFTER CLAIMING** - Prevents duplicate work

**Page Completion Commit:**
```
[SHORT_ID] M2 DONE: Completed page YY
STATE: M2.page_done
PAGES: YY
TRANSLATION_HASH: [sha256 first 8 chars of JSON]
PDF_HASH: [sha256 first 8 chars of PDF]
HEARTBEAT: [timestamp]
```

**Conflict Resolution (Race Conditions):**
If two workers claim the same page:
1. Earlier commit timestamp wins
2. If same second, lexicographically earlier branch name wins
3. Losing worker re-syncs and claims next available page

**Progress Tracking in WORKER_STATE.md:**
```markdown
## M2 Page Status
| Page | Status | Started | Completed | Hash |
|------|--------|---------|-----------|------|
| 7 | done | 10:00:00 | 10:25:00 | a8b3c2d1 |
| 23 | done | 10:26:00 | 10:48:00 | f4e5d6c7 |
| 39 | translating | 10:49:00 | - | - |
```

**Per-Page Workflow (One Iteration):**

#### Phase 0: Claim and Broadcast
1. **Pull** all worker branches (MANDATORY before claiming)
2. **Identify** next available page
3. **Commit and push claim** immediately
4. **Verify** no conflict (re-pull after push)

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

### M3: Final Assembly (COORDINATED - LEADER ELECTION)
**Goal**: Compile complete multilingual book
**Execution**: One worker leads assembly, others verify

**Leader Election:**
1. First worker to complete their last M2 page becomes assembly leader
2. Leader broadcasts:
   ```
   [SHORT_ID] M3 LEADER: Taking assembly responsibility
   HEARTBEAT: [timestamp]
   ```
3. Other workers enter verification mode

**Leader Tasks:**
- [ ] Collect all page translations from all active worker branches
- [ ] Verify all 99 pages are complete
- [ ] Merge all individual PDFs in correct order
- [ ] Add table of contents (multilingual)
- [ ] Add translator's note (explaining format, approach)
- [ ] Create cover page (multilingual title)
- [ ] Export to `final/durov_code_multilingual.pdf`
- [ ] Broadcast final hash

**Verifier Tasks (other workers):**
- [ ] Pull leader's final assembly
- [ ] Verify PDF contains all pages
- [ ] Spot-check random pages (distribute evenly among verifiers)
- [ ] Report verification:
  ```
  [SHORT_ID] M3 VERIFY: Final assembly verified
  FINAL_HASH: [hash]
  PAGES_CHECKED: [list]
  STATUS: pass
  ```

**Exit Criteria:**
- Complete PDF exists
- All 99 original pages + translations included
- File opens correctly, all fonts render
- All active workers report verification passed

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

## Deadlock Prevention

### Timeout Rules
| Situation | Timeout | Action |
|-----------|---------|--------|
| Page claimed, no progress | 30 min | Page becomes available |
| Worker no heartbeat | 15 min | Consider worker stalled |
| Waiting for consensus | 20 min | Proceed with majority |
| Verification timeout | 30 min | Re-run verification |

### Heartbeat Protocol
- Update HEARTBEAT in every commit
- If no commits for 5 min while working, push a heartbeat-only commit
- Stale workers (>15 min old heartbeat) can be worked around

### Stall Recovery
If you detect you're stalled:
1. Commit an ALERT message explaining the issue
2. Release any claimed resources (pages)
3. Other workers will work around you

### Livelock Prevention
To prevent workers from endlessly conflicting:
- Always claim the LOWEST available page number
- Lower worker ID wins ties
- If you lose a conflict, wait 10 seconds before re-claiming

---

## Multi-Agent Coordination Rules

### 1. Never Work in Isolation
- Pull other workers' branches every 60-120 seconds
- Your work is invisible until you push
- Push early, push often

### 2. Claim Before Work
- Never start on a page without claiming it first
- Push the claim before starting translation
- Re-verify your claim after push (check for conflicts)

### 3. Trust But Verify
- Other workers may make mistakes
- Cross-verify outputs when required (M0, M1, M3)
- Report discrepancies via ALERT messages

### 4. Majority Rules
- For decisions, >50% agreement wins
- Minority workers must adopt majority decision
- Document your disagreement but comply

### 5. Help Stalled Workers
- If a worker appears stalled, flag their claimed resources
- Don't immediately take over—wait for timeout
- Communicate via ALERT before reclaiming

### 6. Maintain Global Awareness
Always know:
- Which pages are claimed/done
- Which workers are active
- What the current consensus is
- Whether verification has passed

---

## Anti-Patterns (Avoid These)

### Translation Anti-Patterns
- ❌ **Skipping research**: Every page needs context research
- ❌ **Literal translation**: Idioms must be adapted, not translated word-for-word
- ❌ **Inconsistent terminology**: Use glossary, don't reinvent translations
- ❌ **Starting new page with <15k tokens**: Finish current page or save state
- ❌ **Ignoring cultural context**: Russian references need explanation/adaptation
- ❌ **Machine translation without review**: All output must be human-reviewed 3x
- ❌ **Losing Durov's voice**: Sharp, provocative, unconventional - preserve this
- ❌ **Overlong sessions without saves**: Update STATE.md every 5 pages minimum

### Multi-Agent Anti-Patterns
- ❌ **Working without claiming**: Always claim pages before translating
- ❌ **Infrequent pushes**: Push after every significant action
- ❌ **Ignoring other workers**: Pull every 60-120 seconds
- ❌ **Claiming multiple pages**: Claim one page at a time
- ❌ **Skipping verification**: M0/M1/M3 require cross-verification
- ❌ **Ignoring conflicts**: Resolve conflicts immediately, don't proceed
- ❌ **Stale heartbeats**: Update HEARTBEAT in every commit
- ❌ **Unilateral decisions**: Vote on format/approach decisions
- ❌ **Proceeding without consensus**: Wait for active workers before M2
- ❌ **Assuming fixed worker count**: Quorum is >50% of active workers, not fixed 16
- ❌ **Forgetting to create WORKER_STATE.md**: This file REGISTERS you!

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

## Git Workflow (Multi-Agent)

### Critical: Push Frequency
**PUSH IMMEDIATELY** after any of these events:
- Starting a new task
- Completing a task
- Claiming a page
- Completing a page
- Any error or blocker
- Voting on a decision

### Sync Protocol (Every 60-120 seconds)
```bash
# Fetch all remote branches
git fetch origin --all --prune

# Discover and read active workers' states
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
    echo "=== $branch ==="
    git show "origin/${branch}:WORKER_STATE.md" | head -20
  fi
done
```

### Commit Message Format (MANDATORY)
All commits MUST follow this format for machine parsing:

```
[SHORT_ID] [MILESTONE] [ACTION]: [description]
STATE: [state info]
HEARTBEAT: [unix timestamp]
```

Where `SHORT_ID` = last 4 characters of your branch name.

### Examples
```bash
# Get your short ID first
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)

# M0 task complete
git commit -m "[$MY_SHORT_ID] M0 COMPLETE: Dependency installation
STATE: M0.1 = done
HEARTBEAT: $(date +%s)"

# M2 page claim
git commit -m "[$MY_SHORT_ID] M2 CLAIM: Starting page 23
PAGES: 23
HEARTBEAT: $(date +%s)"

# M2 page done
git commit -m "[$MY_SHORT_ID] M2 DONE: Completed page 23
PAGES: 23
TRANSLATION_HASH: a8b3c2d1
HEARTBEAT: $(date +%s)"

# Vote
git commit -m "[$MY_SHORT_ID] VOTE: format_approach = latex
HEARTBEAT: $(date +%s)"
```

### Conflict Resolution
If `git push` fails:
```bash
git pull --rebase origin HEAD
# Resolve any conflicts
git push origin HEAD
```

If conflicts persist, commit an ALERT:
```
[SHORT_ID] ALERT: Push conflict unresolved
DETAILS: [description]
HEARTBEAT: [timestamp]
```

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

## Starting the Project (Multi-Agent)

### STEP 1: Identify Yourself
```bash
# Get your branch name and short ID
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "Branch: $MY_BRANCH"
echo "Short ID: $MY_SHORT_ID"
# Example: cursor/multi-agent-parallel-translation-cca9 → cca9
```

### STEP 2: Create WORKER_STATE.md
Copy from `WORKER_STATE_TEMPLATE.md` and fill in your info:

```markdown
# Worker State: [YOUR_SHORT_ID]

## Identity
- **Branch**: [your full branch name]
- **Short ID**: [last 4 chars, e.g., cca9]
- **Last Updated**: [ISO 8601 timestamp]
- **Heartbeat**: [Unix timestamp]

## Current Milestone
- **Milestone**: M0
- **Status**: starting

## M0 Task Status
| Task ID | Description | Status | Result Hash |
|---------|-------------|--------|-------------|
| M0.1 | Install dependencies | pending | - |
| M0.2 | Extract PDF text | pending | - |
| M0.3 | Create chapter structure | pending | - |
| M0.4 | Research: Durov bio | pending | - |
| M0.5 | Research: VK history | pending | - |
| M0.6 | Research: Russia context | pending | - |
| M0.7 | Create chapter summaries | pending | - |

## M2 Page Claims
| Page | Status | Started | Completed |
|------|--------|---------|-----------|

## Consensus Votes
| Topic | My Vote | Timestamp |
|-------|---------|-----------|

## Known Workers
[Will be populated after first sync]

## Messages
Ready to begin.

## Blockers
None
```

### STEP 3: Initial Sync and Broadcast
```bash
# Fetch all remote branches
git fetch origin --all --prune

# Commit and push your initial state (this REGISTERS you as a worker!)
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] M0 START: Beginning session
STATE: M0 = starting
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### STEP 4: Discover Other Workers
```bash
# Find all active workers (branches with WORKER_STATE.md)
git fetch origin --all --prune
echo "Active workers:"
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
    short_id=$(echo "$branch" | grep -oE '[^-]+$' | tail -c 5)
    echo "  - $branch ($short_id)"
  fi
done
```

### STEP 5: Begin M0 Tasks
Execute M0 tasks, committing and pushing after each one.

---

## Quick Reference Card

### Get Your Short ID
```bash
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_SHORT_ID"
```

### Communication Commands
```bash
# Sync with all workers
git fetch origin --all --prune

# Discover active workers
for b in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||'); do
  git show "origin/${b}:WORKER_STATE.md" &>/dev/null && echo "Active: $b"
done

# Read a specific worker's state
git show origin/[branch-name]:WORKER_STATE.md

# Push your state
git add WORKER_STATE.md && git commit -m "[$MY_SHORT_ID] ..." && git push

# Check global page progress
git log --remotes --oneline --grep="M2 DONE"
```

### Commit Prefixes
- `[SHORT_ID] M0 COMPLETE:` - M0 task done
- `[SHORT_ID] M1 RESULT:` - M1 exploration result
- `[SHORT_ID] VOTE:` - Consensus vote
- `[SHORT_ID] VERIFY:` - Verification result
- `[SHORT_ID] M2 CLAIM:` - Page claimed
- `[SHORT_ID] M2 DONE:` - Page completed
- `[SHORT_ID] ALERT:` - Important notice
- `[SHORT_ID] SYNC:` - Sync/heartbeat

### Files to Track
- `WORKER_STATE.md` - Your state (update frequently, THIS REGISTERS YOU!)
- `PROTOCOL.md` - Communication rules (read-only)
- `instructions.md` - Task instructions (read-only)
- `STATE.md` - Shared project state (update with consensus)

---

*This document and PROTOCOL.md should be treated as read-only during execution. Update WORKER_STATE.md frequently. Commit and push often!*
