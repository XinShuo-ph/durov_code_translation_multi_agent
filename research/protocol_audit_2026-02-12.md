# Multi-Agent Protocol Audit (2026-02-12)

Scope: 16 branches matching `origin/cursor/book-translation-multi-agent-*`.

## Key findings

1. **Sustained participation was low**
   - Branches active >=30 minutes: **3/16**
   - Long-running branches:
     - `c68e`: 97.2 min, 33 unique commits
     - `14ce`: 54.8 min, 22 unique commits
     - `c3ab`: 32.6 min, 12 unique commits

2. **Work concentration**
   - Unique non-demo pages found: **35**
   - `c68e` contributed **29/35 (~83%)**

3. **Duplication / collision**
   - Pages translated at least once: **37**
   - Duplicated pages: **19**
   - `page_013` duplicated across **7** branches
   - `page_043` duplicated across **7** branches

4. **Root protocol gaps**
   - "Lowest available page" allowed races and duplicate picking.
   - No fairness gate, so one fast worker could outpace all peers.
   - No mandatory review/handoff requirement, so collaboration degraded.
   - Demo page behavior leaked into production translation paths.

## Changes introduced

- Added executable coordinator: `tools/sync_daemon.py`
  - global snapshot
  - deterministic lane allocation
  - claim validity / reclaim windows
  - fairness gate (`review` when too far ahead)
  - page-level status checks
- Rewrote `PROTOCOL.md` as concise v2 command protocol.
- Updated `WORKER_STATE_TEMPLATE.md` to track peer review.
- Updated `README.md` to reference coordinator-driven workflow.
