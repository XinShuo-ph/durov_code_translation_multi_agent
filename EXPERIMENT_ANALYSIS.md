# Multi-Agent Experiment Analysis

Analysis of two multi-agent parallel translation experiments, each with 16 AI agents.

---

## Experiment 1: `book-translation-multi-agent-*` (16 agents)

### Per-Agent Activity

| Agent ID | Unique Commits | Duration (min) | Pages Translated | Status |
|----------|---------------|-----------------|------------------|--------|
| c68e | 28 | 217 | 30+ (pages 6-36) | **Workhorse** — translated most of the book alone |
| 14ce | 17 | 174 | 10 (pages 13-22) | Completed Chapter 1 |
| c3ab | 7 | 152 | 6 (pages 7-12) | Completed Prologue |
| 991c | 11 | 134 | 3 (pages 2-4) | Some translation work |
| f6c8 | 8 | 136 | 2 (pages 5-6) | Some translation work |
| 6d12 | 7 | 135 | 1 (page 1) | Minimal translation |
| e5f7 | 5 | 133 | 3 (pages 2-4) | Duplicated 991c's work |
| 4e64 | 1 | 128 | 0 | Stuck in M1 voting |
| 655c | 2 | 131 | 0 | Stuck in M1 consensus |
| 7ae4 | 1 | 131 | 0 | Stuck in M1 voting |
| 81f0 | -1 | 125 | 0 | Stuck in M1 |
| 19b6 | -4 | 134 | 0 | Dead after M0 setup |
| 49ab | -4 | 129 | 0 | Dead after M0 setup |
| 8e97 | -4 | 128 | 0 | Dead after M0 setup |
| de92 | -4 | 129 | 0 | Dead after M0 setup |
| e545 | -4 | 143 | 0 | Dead after M0 setup |

### Findings

- **5/16 (31%)** agents never got past initial setup (M0 phase)
- **4/16 (25%)** agents got stuck in format exploration and voting (M1 phase)
- **Only 7/16 (44%)** agents actually translated any pages
- **Only 3/16 (19%)** did significant translation work
- **1 agent (c68e)** translated more pages than all other agents combined

### Root Causes

1. **Milestone bloat**: M0 (7 research tasks) and M1 (7 format tasks) were redundant — all 16 agents independently re-did pre-completed setup work
2. **Consensus deadlock**: M1 required agents to vote on format approach (LaTeX vs Python). Agents voted differently and then waited for consensus that never reached quorum
3. **Sequential milestone gates**: Agents couldn't start translating (M2) until completing M0 and M1, which consumed 60-120 minutes of each agent's session

---

## Experiment 2: `collaborative-translation-initiation-*` (16 agents)

### Per-Agent Activity

| Agent ID | Unique Commits | Duration (min) | Pages Translated | Status |
|----------|---------------|-----------------|------------------|--------|
| f4a6 | 88 | 517 | 85 | **Workhorse** — nearly the whole book |
| ba2f | 18 | 553 | 99 | Translated ALL pages (aggregated from others?) |
| b9fb | 64 | 390 | 62 (pages 38-99) | Heavy contributor |
| d536 | 51 | 426 | 49 | Heavy contributor |
| 8fb2 | 39 | 394 | 38 (pages 37-77) | Significant work |
| 7030 | 26 | 308 | 11 | Moderate work |
| 4900 | 24 | 301 | 12 (pages 1-12) | Moderate work |
| 5aa9 | 21 | 306 | 10 | Moderate work |
| 02bd | 19 | 300 | 9 (pages 2-10) | Some work |
| ba2f | 18 | 553 | 99 | See above |
| a361 | 16 | 297 | 7 (pages 2-8) | Some work |
| 056e | 12 | 298 | 5 | Some work |
| 37cb | 8 | 288 | 3 (pages 2-4) | Minimal |
| 82a5 | 1 | 291 | 5 (pages 1-5) | Minimal unique contribution |
| 723f | 1 | 290 | 4 (pages 1-4) | Minimal unique contribution |
| 7e4a | 1 | 289 | 1 (page 38) | Minimal |
| 6050 | 1 | 289 | 3 (pages 1-3) | Minimal |

### Duplication Analysis

| Metric | Value |
|--------|-------|
| **Total page-translations produced** | 406 |
| **Unique pages needed** | 99 |
| **Duplicate translations** | 307 (**76% waste**) |
| **Most-duplicated page** | Page 2 — translated **11 times** |
| **Second most-duplicated** | Page 3 — translated **11 times** |
| **Pages translated only once** | **0** (every page had at least 2 translations) |

### Top 10 Most-Duplicated Pages

| Page | Times Translated | Notes |
|------|-----------------|-------|
| 2 | 11 | Front matter — every agent's "first page" |
| 3 | 11 | Front matter |
| 4 | 10 | Front matter |
| 5 | 8 | Front matter |
| 6 | 7 | Preface |
| 38 | 6 | Chapter 3 start — second wave of agents |
| 45 | 6 | Chapter 3 |
| 1 | 6 | Title page |
| 7 | 5 | Prologue start |
| 8 | 5 | Prologue |

### Root Causes

1. **Thundering herd**: All agents race for the lowest-numbered page (page 1, 2, 3...). Without deterministic assignment, early pages get massively over-translated
2. **Sync failure**: Despite "sync every 2-3 minutes" instructions, agents didn't reliably check other branches before claiming pages
3. **No deconfliction mechanism**: The "claim lowest available" strategy requires perfect real-time coordination that git-based communication can't provide
4. **Long-lived agents dominate**: Agents with longer sessions (f4a6, b9fb, d536) naturally took over as shorter-lived agents died

---

## Cross-Experiment Comparison

| Metric | Experiment 1 (multi-agent) | Experiment 2 (collaborative) |
|--------|---------------------------|------------------------------|
| Agents producing output | 7/16 (44%) | 12/16 (75%) |
| Pages by top agent | 30+ (c68e) | 99 (ba2f) |
| Duplication rate | Moderate (different file locations) | 76% (307/406) |
| Primary failure mode | Setup phase bloat | Duplicate work |
| Protocol complexity | High (3 milestones, voting) | Medium (sync + claim) |
| Effective throughput | ~36 unique pages | 99 pages (but 76% waste) |

---

## Key Lessons

### 1. Eliminate All Setup Phases
Every minute an agent spends on setup is a minute not spent on the actual task. In Experiment 1, 9/16 agents never reached the translation phase because M0 + M1 consumed their entire sessions.

**Rule**: All research, format decisions, and tooling must be complete before agents start. Agents translate from minute zero.

### 2. Deterministic Work Assignment
The "claim lowest available" strategy causes thundering herd. With 16 agents, pages 1-5 get claimed by nearly everyone in the first sync window.

**Rule**: Use stripe-based assignment. Agent position determines starting pages. No coordination needed for initial work distribution.

### 3. Never Use Consensus Mechanisms
Voting requires simultaneous agent presence, which doesn't happen in async distributed systems. In Experiment 1, 4 agents were permanently stuck waiting for consensus.

**Rule**: All decisions are pre-made. No voting, no consensus, no waiting for agreement.

### 4. File Existence > State Parsing
Scanning for output files (`translations/page_XXX.json` exists?) is more reliable than parsing `WORKER_STATE.md` tables. Files either exist or they don't — no heartbeat interpretation, no table parsing, no stale state.

**Rule**: Use output file existence as the source of truth for what work is done.

### 5. Keep the Protocol Under 200 Lines
A 378-line protocol document exceeds what agents can reliably absorb in their context window. Critical rules get lost in verbosity.

**Rule**: The protocol must fit in one screen. Every line must earn its place.

### 6. Push After Every Unit of Work
Agents that batched their pushes (or forgot to push) became invisible to others, causing duplicate work.

**Rule**: Push immediately after completing each page. Your commit is your broadcast.

---

## Protocol v2.0 Design (See PROTOCOL.md)

Based on these lessons, the new protocol implements:

1. **Stripe-based assignment**: Agents get deterministic, non-overlapping page sets
2. **Two-phase execution**: STRIPE (parallel, zero coordination) → SCAVENGE (fill gaps)
3. **Zero setup time**: No M0, M1, voting, or consensus
4. **Minimal state**: 6-line WORKER_STATE.md instead of complex tables
5. **Helper tooling**: `tools/compute_stripe.py` handles stripe computation and progress scanning

Expected improvement: **< 5% waste** (vs 76%) with **> 90% agent utilization** (vs 44%).
