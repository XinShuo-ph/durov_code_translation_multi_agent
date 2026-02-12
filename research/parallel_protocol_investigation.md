# Parallel Protocol Investigation (16-Branch Review)

Date: 2026-02-12  
Scope: `origin/cursor/book-translation-multi-agent-*` (16 branches)

---

## 1) What We Measured

We inspected:

- worker milestones and M2 page tables from `WORKER_STATE.md`,
- translation commit counts per branch (`origin/main..branch`, path `translations`),
- translation activity timeline in 10-minute buckets,
- duplicate page coverage across worker states.

---

## 2) Key Findings

### A. Participation collapsed early

- Milestone distribution:
  - `M0`: 4 branches
  - `M1`: 4 branches
  - `M2`: 8 branches
- So only half the workers reached sustained translation mode.

### B. Throughput was concentrated in a few workers

- Total translation commits: **66**
- Top-3 branches share: **78.79%**
  - `c68e`: 30
  - `14ce`: 14
  - `c3ab`: 8

### C. Parallelism decayed into a solo long tail

10-minute bucket activity (branches with translation commits):

- `1767242400`: 7 active branches
- `1767243000`: 4
- `1767243600`: 3
- `1767244200`: 2
- `1767244800`: 2
- `1767245400` onward: **1** (`c68e` only)

### D. Duplicate work was significant

- Duplicate pages in M2 claims table: **19**
- Examples:
  - page 8: `14ce,c3ab,c68e,e545`
  - pages 10-12: `14ce,c3ab,c68e`
  - pages 14-22: `14ce,c68e`

---

## 3) Root Causes

1. **Per-worker M0/M1 repetition** consumed many workers before M2.
2. **Consensus waiting states** (`waiting_consensus`) blocked translators from starting.
3. **Manual claim flow** produced races and overlapping page ownership.
4. **State format drift** reduced machine-parseability and reliable coordination.

---

## 4) Borrowed Idea From StoneRecords

Reference:  
`https://github.com/XinShuo-ph/StoneRecords_translation_multi_agent/blob/cursor/hong-lou-meng-translation-843e/PROTOCOL.md`

Useful idea adopted:

- **Mandatory machine-checked pre-claim step** (a sync gate before any new claim).

Adaptation in this repo:

- Implemented as `tools/parallel_coord.py` command workflow (no long-running daemon required).

---

## 5) Protocol v2 Decisions

Implemented in `PROTOCOL.md`:

1. Translation-first loop (remove M0/M1 gating from execution path).
2. Mandatory claim gate via `tools/parallel_coord.py`.
3. Deterministic shard-first assignment + global fallback.
4. One active lease per worker, strict heartbeat/timeout rules.
5. Minimal, strict `WORKER_STATE.md` schema (`WORKER_STATE_TEMPLATE.md`).

Expected effect:

- keep a larger fraction of workers in active translation,
- reduce duplicate pages,
- avoid “single hero worker” endgame when workers are actually available.
