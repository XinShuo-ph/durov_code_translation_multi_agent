# Experiment Analysis: Multi-Agent Parallel Translation

## Experiment 1: `book-translation-multi-agent-*` (16 agents)

### Duration and Activity

| Agent | Commits | Duration | Pages Translated | Outcome |
|-------|---------|----------|-----------------|---------|
| c68e  | 33      | 1h 37m   | 29 (pages 6-36) | **Top performer**. Translated steadily for 97 min. |
| 14ce  | 22      | 55m      | 12 (pages 8-22) | Second best. 8 pages overlap with c68e. |
| c3ab  | 12      | 33m      | 6 (pages 7-12)  | All 6 pages overlap with c68e. |
| 991c  | 16      | 16m      | 4 (pages 1-4)   | Died after completing front matter. |
| f6c8  | 13      | 17m      | 2 (pages 5-6)   | Died after 2 pages. Page 6 conflict with c68e. |
| 6d12  | 12      | 16m      | 0               | Spent all time on setup (M0+M1), claimed page 1, never translated. |
| e5f7  | 10      | 14m      | 2 (pages 2-3)   | Spent 12 min on setup, translated 2 pages, died. |
| 655c  | 7       | 12m      | 0               | Created "helper scripts" and "verification tools" instead of translating. |
| 7ae4  | 6       | 12m      | 0               | Explored LaTeX, then Python, then voted. Never translated. |
| 4e64  | 6       | 9m       | 0               | Explored fpdf2, voted, waited for consensus. Never translated. |
| 81f0  | 4       | 7m       | 0               | Completed M0, explored M1, improved template. Never translated. |
| 19b6  | 1       | -        | 0               | Single commit adding initial files. Died immediately. |
| 49ab  | 1       | -        | 0               | Single commit adding initial files. Died immediately. |
| 8e97  | 1       | -        | 0               | Single commit adding initial files. Died immediately. |
| de92  | 1       | -        | 0               | Single commit adding initial files. Died immediately. |
| e545  | 1       | -        | 0               | Single commit adding initial files. Died immediately. |

### Time Breakdown (estimated, across all agents)

| Activity | Agent-Minutes | % of Total |
|----------|--------------|------------|
| M0: Install deps, extract text, write research | ~100 min | 35% |
| M1: Explore formats, create demos, vote | ~60 min | 21% |
| M2: Actually translating pages | ~100 min | 35% |
| Syncing, state updates, waiting | ~25 min | 9% |

**Only 35% of total effort went to the actual task.**

### Page Coverage

- **Pages actually translated**: 1-36 (36 pages)
- **Pages translated ONLY by c68e**: 14-36 (23 pages)
- **Pages translated by 3+ agents**: 8, 10, 11, 12
- **Pages never translated**: 37-99 (63 pages)

---

## Experiment 2: `collaborative-translation-initiation-*` (16 agents)

### Duration and Activity

| Agent | Commits | Duration | Pages |
|-------|---------|----------|-------|
| f4a6  | 88      | 3h 50m   | 85    |
| ba2f  | 18      | 4h 27m   | 99    |
| b9fb  | 64      | 1h 45m   | 62    |
| d536  | 51      | 2h 20m   | 49    |
| 8fb2  | 39      | 1h 47m   | 38    |
| 7030  | 26      | 22m      | 11    |
| 4900  | 24      | 15m      | 12    |
| 5aa9  | 21      | 19m      | 10    |
| 02bd  | 19      | 14m      | 9     |
| a361  | 16      | 10m      | 7     |
| 056e  | 12      | 11m      | 5     |
| 37cb  | 8       | 3m       | 3     |
| 6050  | 1       | -        | 3     |
| 723f  | 1       | -        | 4     |
| 7e4a  | 1       | -        | 1     |
| 82a5  | 1       | -        | 5     |

### Page Overlap (pages translated by N agents)

| Overlap Count | Pages |
|--------------|-------|
| 11 agents | Pages 2, 3 |
| 10 agents | Page 4 |
| 8 agents  | Page 5 |
| 7 agents  | Page 6 |
| 6 agents  | Pages 1, 38 |
| 5 agents  | Pages 7, 8, 9, 13, 39 |
| 4 agents  | Pages 10, 40 |
| 3 agents  | Pages 11, 12, 16, 23-27, 30-35, 37, 39 |
| 2 agents  | Pages 14, 15, 17-22, 28-29, 36, 41-80 |

**Approximately 40-60% of total agent effort was wasted on duplicate translations.**

---

## Root Cause Analysis

### 1. Redundant Setup Work

Every agent independently performed identical tasks:
- Installed dependencies (poppler, texlive, fonts)
- Extracted text from PDF
- Wrote research documents (Durov bio, VK history, Russia context)
- Created chapter structure
- Explored PDF generation approaches
- Created demo translations

This consumed 10+ minutes per agent. With 16 agents, that's 160+ minutes of redundant work.

**Fix**: Pre-do all setup on `main` before launching agents.

### 2. Phase Gates Killed Agents

The M0→M1→M2→M3 progression meant:
- Agents spent their first 10 min on M0 (setup)
- Then 5-10 min on M1 (format exploration + consensus)
- Many agents died before reaching M2 (translation)
- Of 16 agents in Exp 1, 7 never translated a single page

**Fix**: No phases. Agents start producing output immediately.

### 3. Consensus Was a Trap

M1 required workers to "vote" on format approach (LaTeX vs ReportLab vs fpdf2). Workers waited for 50% consensus that never materialized because workers kept dying.

- 655c spent all its time building "verification tools" and waiting for consensus
- 7ae4 voted twice (different options) trying to reach quorum
- 4e64 declared its own consensus and still couldn't proceed

**Fix**: All tooling decisions pre-made. No voting.

### 4. "Lowest Available" = Everyone Starts at Page 1

Without shared filesystem access, every agent independently concluded page 1 was available. The sync mechanism (reading all branches via `git show`) was too complex and slow for most agents to execute correctly.

In Experiment 2, page 2 was translated 11 times.

**Fix**: Deterministic interleaved assignment based on sorted worker index.

### 5. Protocol Length Consumed Agent Context

The original protocol (377 lines) + instructions (468 lines) + README (160 lines) = ~1000 lines of coordination text that agents read before starting work. This left less context for actual translation.

The most productive agents (c68e, f4a6) effectively ignored most of the protocol.

**Fix**: Protocol under 150 lines. Task instructions under 200 lines.

---

## What Worked

1. **Simple sequential page translation** — c68e just translated page after page, ignoring sync
2. **Pre-extracted text** — agents that found `extracted/pages/` could start faster
3. **JSON output format** — simple, clear, well-defined
4. **Individual branches** — no merge conflicts during work

## What the v2 Improvement Branch Got Right

The `multi-agent-translation-improvement-7967` branch correctly identified:
- "Simpler is better"
- "Workers that ignored the complex consensus protocol were the most productive"
- "No consensus, no voting, no phases"
- "The protocol is: there is no protocol. Translate pages."

But it went too far toward "no coordination at all," which still leads to massive overlap.

## The v3 Solution

The new PROTOCOL.md combines:
- **v2's insight**: eliminate all blocking coordination
- **Deterministic assignment**: mathematically eliminate overlap
- **One sync at startup**: minimal coordination overhead
- **Gap-fill phase**: resilience against worker death

Expected improvement with 16 agents:
- Setup time per agent: **0 minutes** (vs 10+ minutes)
- Page overlap: **0-2 pages** (vs 50+ pages)
- Agents that translate at least 1 page: **16/16** (vs 3-4/16)
- Total pages translated: **99** (vs 36 in Exp 1)
