# Multi-Agent Experiment Analysis

Raw data from two 16-agent parallel translation experiments on this codebase.

---

## Experiment 1: `book-translation-multi-agent` (16 branches)

**Duration**: 2026-01-01 04:29 - 06:07 UTC (1h38m)

### Per-Agent Activity

| Agent  | Commits | Active Duration | Pages Translated | Outcome              |
|--------|---------|-----------------|------------------|----------------------|
| c68e   | 33      | 1h37m           | 6-36 (31 pages)  | Solo workhorse       |
| 14ce   | 22      | 55m             | 13-22 (10 pages) | Good contributor     |
| c3ab   | 12      | 33m             | 7-12 (6 pages)   | Decent contributor   |
| 991c   | 16      | 16m             | 2-4 (3 pages)    | Short-lived          |
| f6c8   | 13      | 17m             | 5-6 (2 pages)    | Short-lived          |
| 6d12   | 12      | 16m             | 1 (claimed only)  | Setup then stalled   |
| e5f7   | 10      | 14m             | 2-4 (3 pages)    | Short-lived, overlap |
| 655c   | 7       | 12m             | 0 pages           | Built scripts only   |
| 4e64   | 6       | 9m              | 0 pages           | Stuck in M1 phase    |
| 7ae4   | 6       | 12m             | 0 pages           | Stuck in M1 phase    |
| 81f0   | 4       | 7m              | 0 pages           | Stuck in M1 phase    |
| 19b6   | 1       | 0m              | 0 pages           | Startup death        |
| 49ab   | 1       | 0m              | 0 pages           | Startup death        |
| 8e97   | 1       | 0m              | 0 pages           | Startup death        |
| de92   | 1       | 0m              | 0 pages           | Startup death        |
| e545   | 1       | 0m              | 0 pages           | Startup death        |

### Timeline

```
04:29  ████████████████  All 16 agents start M0 (research)
04:42  ████████████      11 agents reach M1 (format exploration + voting)
04:45  ████████          8 agents voting on PDF approach
04:50  ██████            6 agents enter M2 (translation)
04:55  ███               3 agents still translating
05:25  ██                2 agents remain
05:30  █                 c68e alone
06:07  ·                 c68e finishes
```

### Failure Breakdown

- **5 agents (31%)**: Startup death — 1 commit, never progressed
- **4 agents (25%)**: Stuck in M1 — voted on format, never translated
- **1 agent (6%)**: Meta-work trap — built scripts instead of translating
- **3 agents (19%)**: Short-lived translators — produced 2-4 pages each
- **3 agents (19%)**: Productive — translated 6-31 pages each

### Key Observation

The M0 (research) and M1 (format exploration) phases caused all 16 agents to do identical redundant work. By the time agents reached actual translation (M2), most had exhausted their context or stalled. The three productive agents all began translating by ~04:50. Agent c68e produced 31 of the ~45 unique translated pages.

---

## Experiment 2: `collaborative-translation-initiation` (16 branches)

**Duration**: 2026-01-01 07:16 - 11:43 UTC (4h27m)

### Per-Agent Activity

| Agent  | Commits | Active Duration | Pages Range       | Outcome            |
|--------|---------|-----------------|-------------------|--------------------|
| f4a6   | 88      | 3h50m           | 2-99 (~88 pages)  | Near-complete solo |
| b9fb   | 64      | 1h45m           | 38-99 (~62 pages) | Overlapped heavily |
| d536   | 51      | 2h20m           | 1-99 (~50 pages)  | Overlapped heavily |
| ba2f   | 18      | 4h27m           | 1-40 (sporadic)   | Long but sparse    |
| 8fb2   | 39      | 1h47m           | 1-60 (~39 pages)  | Overlapped heavily |
| 7030   | 26      | 22m             | 2-30 (~25 pages)  | Moderate overlap   |
| 5aa9   | 21      | 19m             | 2-20 (~15 pages)  | Early pages only   |
| 4900   | 24      | 15m             | 1-30 (~22 pages)  | Overlapped heavily |
| 02bd   | 19      | 14m             | 2-20 (~17 pages)  | Early pages only   |
| a361   | 16      | 10m             | 2-14 (~13 pages)  | Early pages only   |
| 056e   | 12      | 11m             | 2-12 (~10 pages)  | Early pages only   |
| 37cb   | 8       | 3m              | 2-8 (~6 pages)    | Very short          |
| 6050   | 1       | 0m              | 1-3               | Startup death      |
| 723f   | 1       | 0m              | 1-4               | Startup death      |
| 7e4a   | 1       | 0m              | 38                | Startup death      |
| 82a5   | 1       | 0m              | 1-4               | Startup death      |

### Page Duplication

| Pages   | Agents Translating Each | Waste |
|---------|------------------------|-------|
| 1       | 6                      | 5x    |
| 2-3     | 11                     | 10x   |
| 4       | 10                     | 9x    |
| 5       | 8                      | 7x    |
| 6-8     | 5-7                    | 4-6x  |
| 9-30    | 4-5                    | 3-4x  |
| 31-99   | 3-4                    | 2-3x  |

**Total**: 426 page-translations for 99 unique pages. **327 wasted (77%).**

### Root Cause: Thundering Herd

All 16 agents used the same algorithm: "claim the lowest available page." They all started simultaneously. Before any agent could push its claim, all 16 had already decided to translate page 1 (or 2, or 3). The git-based "claim and push" mechanism has multi-second latency — plenty of time for all agents to race for the same work.

---

## Cross-Experiment Root Causes

### 1. Redundant Startup Phases

Both experiments required agents to perform setup/research before productive work. This non-parallelizable overhead consumed 10-20 minutes per agent for identical output. With 16 agents, that's 160-320 agent-minutes wasted.

### 2. Thundering Herd on Work Assignment

"Claim the lowest available" is the worst possible strategy when N agents start simultaneously. It guarantees maximum collision on the lowest-numbered units.

### 3. Meta-Work Trap

Multiple agents spent entire sessions building "helper scripts," "verification tools," and "workflow templates" rather than producing output. The verbose protocol encouraged this by describing complex state management.

### 4. Protocol Complexity Causes Startup Death

Both experiments had ~25-31% of agents die after a single commit. The complex multi-phase protocol (read instructions, create state file, sync, discover workers, vote, etc.) overwhelmed agents before they could produce any output.

### 5. No Deterministic Work Distribution

Without deterministic assignment, agents independently executed identical algorithms and reached identical conclusions about what to work on. This is the fundamental cause of both duplication and consensus bottlenecks.

---

## Comparison with StoneRecords Project

The [StoneRecords translation project](https://github.com/XinShuo-ph/StoneRecords_translation_multi_agent/blob/cursor/hong-lou-meng-translation-843e/PROTOCOL.md) attempted to fix these issues with a "sync daemon" — a background Python process that automatically fetches branches and tracks state. Their protocol acknowledges "83% wasted effort" from manual syncing.

**What they got right:**
- Recognized the duplication problem explicitly
- Automated sync via daemon (reduces human/agent error)
- Mandatory pre-claim checks

**What still failed:**
- Still used "claim lowest available" (thundering herd not solved)
- Added tool complexity (agents must run a background daemon correctly)
- Protocol remained verbose (~400 lines)

---

## Derived Requirements for New Protocol

1. **Deterministic work assignment** — eliminate claiming entirely
2. **Minimal protocol** — under 200 lines, fits in one read
3. **Zero startup overhead** — first commit must be productive output
4. **No consensus/voting** — each agent acts independently
5. **Collision-tolerant** — some duplication is acceptable if rare
6. **No state files** — output files ARE the state
7. **No meta-work** — explicitly forbidden in protocol rules
