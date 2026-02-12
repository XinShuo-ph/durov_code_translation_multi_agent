# Investigation Report: 16 Agent-Collaboration-Protocol Branches

## Overview

This report summarizes a thorough investigation of 16 `cursor/agent-collaboration-protocol-*` branches. Each branch independently attempted to solve the same problem: how to maintain translation quality while enabling parallel collaborative work across 16+ AI agents.

All branches analyzed data from two prior failed experiments:
- **Experiment 1** (`book-translation-multi-agent-*`): 16 agents, only 3/16 did meaningful work, 1 agent translated 29/35 pages alone
- **Experiment 2** (`collaborative-translation-initiation-*`): 16 agents, 40-60% duplicate work, pages 2-3 translated 11 times each

---

## Branch-by-Branch Summary

### 1. `28aa` — Executable Sync Service + V2 Protocol

**Strategy**: Prefix-filtered sync service (`tools/sync_service.py`) that treats git as a message bus. Workers claim one page at a time via a CLI tool.

**Quality Approach**: JSON validation tool (`validate_translation_json.py`), WORKER_STATE.md heartbeats, prefix-filtered peer discovery.

**Key Innovation**: Practical executable tooling with `sync_service.py` providing `status`, `next-page`, `check-page`, `scan`, and `daemon` commands. Prefix filtering prevents cross-experiment confusion.

**Strengths**: Well-engineered Python tooling (448 lines), daemon mode, file-based completion detection, legacy path support. Comprehensive but not bloated instructions.

**Weaknesses**: Still relies on claim-based lowest-available approach (thundering herd possible). No deterministic page assignment. No fairness/balance enforcement.

---

### 2. `37be` — Deterministic Interleaved Assignment (V3)

**Strategy**: **Zero-coordination deterministic assignment**. Workers discover peers once, compute interleaved page ranges, then work independently.

**Quality Approach**: Pre-decided format, concise instructions (<200 lines), gap-fill phase after primary assignment. No WORKER_STATE files.

**Key Innovation**: Completely eliminates claiming/races via math: Worker `k` of `N` gets pages `{k+1, k+1+N, k+1+2N, ...}`. Includes detailed `EXPERIMENT_ANALYSIS.md` with hard data.

**Strengths**: Most radical simplification. Zero sync during work. Near-zero coordination overhead. Excellent failure analysis with concrete metrics. Protocol fits in ~150 lines. Performance model included.

**Weaknesses**: No quality review mechanism. No runtime coordination means no adaptation to worker death until gap-fill phase. No validation tooling. Assumes all workers discover each other at startup.

---

### 3. `64eb` — Roles Pipeline (Conductor/Translator/Reviewer/Integrator)

**Strategy**: Explicit role assignment with dedicated Conductor, Integrator, Reviewers, and Translators. Two-pass pipeline: raw translation then review.

**Quality Approach**: Mandatory review via `reviews/page_XXX.<id>.md`. Integrator merges reviewed pages from `translations/raw/` to `translations/final/`. Validation tool included.

**Key Innovation**: Only branch with explicit **review pipeline** and quality gate before integration. Separate `raw` and `final` translation directories.

**Strengths**: Strongest quality assurance. Pipeline mindset (translate → review → integrate runs in parallel). Clear role definitions prevent coordination overhead by limiting who does what.

**Weaknesses**: Role assignment overhead. Requires a minimum team size. Conductor role is a single point of coordination. Workers still claim lowest-available (no deterministic assignment). Higher protocol complexity.

---

### 4. `7aa1` — Mandatory Sync Daemon + Workload Balancing

**Strategy**: Background sync daemon (mandatory, running every 60s) with workload balancing. First-in-first-done setup (no consensus).

**Quality Approach**: Heartbeat monitoring, workload balance checks every 3 pages, aggressive stalled worker reclaiming (15 min timeout).

**Key Innovation**: Explicit **workload balancing rules** (check every 3 pages, slow down if ahead 3x). `--balance`, `--reclaimable`, `--team-stats` daemon commands. Most comprehensive worker state tracking.

**Strengths**: Rich daemon with many query commands. Balance monitoring prevents single-agent takeover. Very detailed protocol (757 lines) covering every edge case.

**Weaknesses**: Protocol is too long (757 lines) — risks burning agent context. Balance checking adds overhead. Daemon-based approach may be fragile if daemon crashes. Still uses claim-based assignment.

---

### 5. `7d12` — Complete V2 with Migration Guide

**Strategy**: Mandatory sync daemon + atomic page claiming with verification + work stealing from stale workers. Includes migration guide from V1.

**Quality Approach**: Heartbeat enforcement, atomic claim sequence (claim → push → re-fetch → verify), separate `claim_page.py`, `complete_page.py`, `heartbeat.py` tools.

**Key Innovation**: Most complete implementation — separate tools for each action. `MIGRATION_GUIDE.md` for transitioning from V1. Largest codebase (3,965 lines added).

**Strengths**: Well-organized tool suite. Atomic claiming is robust. Comprehensive documentation with migration path. Analysis and summary documents.

**Weaknesses**: Massive scope (3,965 lines, 10 new files) — too much for an agent to absorb. No deterministic assignment. No review/quality process. Over-engineered for the problem.

---

### 6. `943d` — Generic Protocol with Hash-Based Scattering

**Strategy**: Generic multi-agent parallel work protocol (not translation-specific). Uses `hash(branch_id) % total_units + 1` as starting offset to scatter agents.

**Quality Approach**: "Check actual output files, not state files. Files don't lie." Minimal AGENT_STATE.md. Emphasis on continuous execution.

**Key Innovation**: **Generic protocol** adaptable to any parallelizable task (translation, migration, test generation). Hash-based starting offset instead of sorted-index interleaving. Strongest anti-pattern documentation. Explicit "protocol fitness checklist."

**Strengths**: Most reusable/generic design. Strong continuous-execution language. Excellent anti-pattern list. Concise yet comprehensive. Pocket reference at the end.

**Weaknesses**: No review mechanism. Hash scattering has more collision risk than sorted interleaving. No validation tooling. Relies on "tolerate rare duplication" rather than preventing it.

---

### 7. `9d18` — Lane-Based Allocation with Fairness Gate + Peer Review

**Strategy**: Lane-based sharding (`(page-1) % N == worker_index`) with spillover. Fairness gate forces REVIEW action when a worker gets too far ahead.

**Quality Approach**: **Peer review requirement** (when >=2 workers online, every DONE page should get one REVIEW). Fairness gate prevents monopoly.

**Key Innovation**: Combines sharding with a **fairness gate** (if completed > min_online_done + 1, must review before claiming). First branch to link quality review to work distribution. Stateless coordinator tool (no daemon).

**Strengths**: Elegant fairness mechanism tied to review. Stateless tool (each invocation is fresh scan). `--next-action` command returns `claim`, `review`, `continue`, or `idle`. Compact protocol.

**Weaknesses**: Fairness gate could stall productive workers. Review quality depends on agent capability. Still requires WORKER_STATE.md parsing.

---

### 8. `a0cf` — Deterministic Sharding + Two-Pass Pipeline + Run Scoping

**Strategy**: Deterministic 16-way shard first, work stealing second. Two-pass pipeline (translation + review). Run scoping via `RUN_CONFIG.json`.

**Quality Approach**: Review required (buddy system: each shard reviews previous shard's pages). `collect_translations.py` for integration. Validation tool.

**Key Innovation**: **`RUN_CONFIG.json`** for explicit run scoping (prevents stale branch confusion). **Buddy review system** (deterministic reviewer pairing). `collect_translations.py` for any-agent integration.

**Strengths**: Clean separation of concerns. Run scoping is elegant. Buddy review is zero-coordination. Collection tool makes integration repeatable. Good sync tool with `--mode shard` and `--mode steal`.

**Weaknesses**: Shard assignment not fully detailed in code. `RUN_CONFIG.json` must be pre-configured. More complex than pure deterministic approaches.

---

### 9. `c510` — Shard-First with Fallback + Lease Timeout

**Strategy**: Shard-first scheduling (sorted worker index modulo) with global fallback. Explicit lease timeout and expiry.

**Quality Approach**: Mandatory validation before broadcast. Machine-checked claiming via `parallel_coord.py`. Lease-based claims with expiry timestamps.

**Key Innovation**: **Explicit lease expiry** in WORKER_STATE.md (`Lease Expires At` field). `audit` command for session-wide distribution/duplicate/milestone analysis.

**Strengths**: Lease expiry is more explicit than heartbeat-only timeout. Audit command useful for monitoring. Comprehensive scheduling with shard + fallback.

**Weaknesses**: No review mechanism. Lease concept adds state management complexity. Protocol is clear but not the most concise.

---

### 10. `c94a` — Quota Enforcement + Gap-First Claiming + Metrics Dashboard

**Strategy**: Load balancing via enforced quotas (max fair_share + 25%). Gap-first claiming priority. Comprehensive metrics monitoring.

**Quality Approach**: Work quotas prevent monopoly. Gap-first claiming ensures continuous coverage. Metrics dashboard tracks load distribution, gap count, duplicate rate.

**Key Innovation**: **Quota enforcement** with `check_quota.py` (blocks claiming if >25% over fair share). **Gap-first priority** (claim gaps before lowest-available). **Health metrics** with defined thresholds (load std dev <15%, gap count <5%).

**Strengths**: Most sophisticated load balancing. Concrete success criteria with numeric thresholds. Six separate tools (sync_daemon, claim_page, check_quota, metrics, monitor_load, update_worker_state). Migration guide from V1.

**Weaknesses**: Most tools of any branch (6 separate scripts). Very heavy tooling overhead. Quota pausing could waste productive agent time. No quality review mechanism. 786-line protocol.

---

### 11. `d005` — Experiment ID + Explicit Roles + Integration Focus

**Strategy**: Mandatory experiment ID in branch names (`exp-<ID>-*`). Explicit roles (Coordinator, Translators, Reviewers, Integrator). Strong integration focus.

**Quality Approach**: Reviewers spot-check pages. Integrator runs continuous collection. `validate_translation.py` before push. Reviewer fixes applied as targeted commits.

**Key Innovation**: **Experiment ID as branch namespace** (e.g., `cursor/exp-005-translate-c68e`). `collect_translations.py` with `--manifest` output. **No mandatory heartbeat** — protocol doesn't rely on heartbeats for correctness.

**Strengths**: Clean namespace design. Strongest integration workflow (any idle agent can integrate). Lightweight reviewer role. Optional WORKER_STATE.md (protocol works without it).

**Weaknesses**: Requires pre-coordination to assign experiment ID. Role assignment overhead. No deterministic page assignment (still uses sync-and-claim). Less tooling than other branches.

---

### 12. `d038` — Hash-Partitioned Deterministic Assignment (Purist)

**Strategy**: **Purest deterministic approach**. Hash-assigned start position, work forward, push after every unit, re-sync every ~5 units. No claiming, no voting, no phases, no state files.

**Quality Approach**: "Just output." First commit must be a completed work unit. Tolerate rare duplication (<2%) rather than coordinate. Performance model with expected speedup formulas.

**Key Innovation**: **No state files at all** — output files are the only state. **Mathematical performance model** (`speedup ≈ N × (1 - N/(2T)) × (1 - sync_overhead)`). Most extreme anti-coordination stance. Comprehensive "What NOT to Do" section.

**Strengths**: Simplest possible protocol. Lowest cognitive load for agents. Excellent performance model. Adapts to any embarrassingly parallel task. 10 explicit rules, no ambiguity.

**Weaknesses**: No quality review. Tolerates duplication rather than preventing it. No fairness mechanism. Hash collisions more likely than index-based sharding. No tools provided.

---

### 13. `d249` — Coordinator Tool with Lead Cap + Striping

**Strategy**: Executable coordinator (`tools/coord.py`) with sharded assignment, lead-cap fairness, and stale claim reclaiming.

**Quality Approach**: Mandatory tool gating (`coord.py next` before every claim). Balance guard (lead cap of +2 pages over slowest peer). HOLD mechanism forces review/help when ahead.

**Key Innovation**: **HOLD mechanism** — coordinator returns `HOLD=lead_cap` instead of a page number, with explicit allowed HOLD tasks (review, glossary, stale-check). Concise yet complete protocol. Clear recovery modes (many/few/returning workers).

**Strengths**: Elegant HOLD mechanism ties balance to quality work. Clear recovery modes for different team sizes. Compact protocol. Well-structured `coord.py` (528 lines).

**Weaknesses**: Lead cap could frustrate fast workers. Review during HOLD is not enforced (just suggested). Shard-based assignment still requires peer discovery.

---

### 14. `e163` — Stripe Protocol (Two-Phase: Stripe + Scavenge)

**Strategy**: Two-phase approach: **Stripe** (deterministic non-overlapping pages from sorted peer index), then **Scavenge** (scan for gaps after stripe done).

**Quality Approach**: Minimal WORKER_STATE.md (don't track others, scan output files instead). Push after every page. Five non-negotiable rules.

**Key Innovation**: **Clearest two-phase articulation** — Phase 1 (Stripe) needs zero coordination, Phase 2 (Scavenge) uses file-existence scanning. `compute_stripe.py` helper. Detailed decision flowchart. Performance estimates.

**Strengths**: Very clean phase separation. Excellent expected performance analysis (16 agents, ~6 pages each, <5% waste). Decision flowchart is immediately actionable. "Don't track others" philosophy reduces state overhead.

**Weaknesses**: No quality review. Staggered starts could cause stripe miscalculation. No validation tool. Scavenge phase still risks duplication without careful sync.

---

### 15. `e6ed` — Full Automation: JSON State + Init + Sync + Validate + Worker Loop

**Strategy**: Maximum automation. Global `STATE.json`, individual `worker-states/*.json` files. Automated sync service (30s intervals). Atomic claiming with immediate conflict detection.

**Quality Approach**: `validate_state.py` for state file validation. `worker_loop.py` for automated work cycle. `init_project.py` for one-time setup. Most tooling of any branch.

**Key Innovation**: **JSON-based state management** (not Markdown). `STATE.json` as single canonical global state. `init_project.py` automates project setup. Most extensive tooling suite (4 Python tools, 3,984 lines added). Automated conflict detection within 2 seconds.

**Strengths**: Most "production-ready" implementation. JSON state is machine-parseable without regex. Comprehensive tool suite. Well-documented with multiple README files.

**Weaknesses**: Most complex overall (3,984 lines, 14 files). STATE.json is a central bottleneck. Multiple agents updating STATE.json creates merge conflicts. No deterministic assignment (still lowest-available). No quality review process.

---

### 16. `fcb3` — Executable Coordinator with JSON State + Balance Guard

**Strategy**: Executable coordinator (`parallel_coord.py`, 758 lines) with JSON-based worker state. Striping preference + balance guard. Batch-local discovery.

**Quality Approach**: Balance guard (no more than 2 pages ahead of slowest peer). Machine-readable `WORKER_STATE.json`. Validation included in `done` command.

**Key Innovation**: **`WORKER_STATE_TEMPLATE.json`** (JSON over Markdown for state — machine-parseable). Single coordinator tool with `status`, `next`, `check`, `claim`, `done`, `heartbeat` commands. Built-in validation in `done` command.

**Strengths**: Clean JSON state. Well-structured single tool. Balance guard is practical. Compact protocol with clear anti-patterns. Good startup script.

**Weaknesses**: Large single tool file (758 lines). No review mechanism. Balance guard could slow productive workers. Still requires peer discovery at startup.

---

## Comparative Analysis

### Strategy Categories

| Category | Branches | Approach |
|----------|----------|----------|
| **Deterministic Assignment** | 37be, d038, e163, (943d) | Hash/index-based page assignment, minimal runtime coordination |
| **Claim-Based with Sync** | 28aa, 7aa1, 7d12, c510, d249, fcb3 | Sync service + claim protocol, runtime coordination |
| **Role-Based Pipeline** | 64eb, a0cf, d005 | Explicit roles (translator/reviewer/integrator) |
| **Quota/Balance Enforced** | c94a, 9d18, d249, fcb3 | Work limits prevent monopoly |
| **Full Automation** | e6ed | Maximum tooling, JSON state, automated everything |

### Quality Assurance Mechanisms

| Mechanism | Branches |
|-----------|----------|
| **Peer review pipeline** | 64eb, 9d18, a0cf, d005 |
| **JSON validation tool** | 28aa, 64eb, a0cf, d005, c510, e6ed, fcb3 |
| **Fairness/quota gate** | 9d18, c94a, d249, fcb3 |
| **Glossary consistency** | Referenced by most, enforced by 64eb, a0cf |
| **No quality mechanism** | 37be, d038, 7aa1, 7d12, e163, 943d |

### Complexity vs. Effectiveness

| Metric | Lowest Complexity | Highest Complexity |
|--------|-------------------|--------------------|
| Lines of protocol | d038 (~200) | c94a (~786), e6ed (~966) |
| Files added | d038 (6 changed) | e6ed (14 new), c94a (12 new) |
| Tools provided | d038, 37be (none) | e6ed (4 tools), c94a (6 tools) |
| Agent cognitive load | d038, 37be, e163 | e6ed, c94a, 7d12 |

### Scoring Matrix (1-5, higher is better)

| Branch | Simplicity | Quality Controls | Parallelism | Fault Tolerance | Tooling | Reusability | **Total** |
|--------|-----------|-----------------|-------------|-----------------|---------|-------------|-----------|
| 28aa | 3 | 3 | 3 | 4 | 4 | 3 | **20** |
| **37be** | **5** | 1 | **5** | 3 | 1 | **5** | **20** |
| 64eb | 3 | **5** | 3 | 3 | 3 | 3 | **20** |
| 7aa1 | 1 | 2 | 3 | 4 | 3 | 2 | **15** |
| 7d12 | 1 | 2 | 3 | 4 | 4 | 2 | **16** |
| **943d** | **5** | 1 | 4 | 3 | 1 | **5** | **19** |
| **9d18** | 3 | **4** | **4** | 4 | 3 | 3 | **21** |
| **a0cf** | 3 | **4** | **4** | 4 | **4** | **4** | **23** |
| c510 | 3 | 2 | 4 | 4 | 3 | 3 | **19** |
| c94a | 1 | 3 | 3 | 4 | 4 | 2 | **17** |
| d005 | 3 | 3 | 3 | 3 | 3 | 4 | **19** |
| **d038** | **5** | 1 | **5** | 3 | 1 | **5** | **20** |
| d249 | 3 | 3 | 4 | 4 | 4 | 3 | **21** |
| **e163** | **4** | 1 | **5** | 3 | 2 | **4** | **19** |
| e6ed | 1 | 3 | 3 | 4 | 5 | 2 | **18** |
| fcb3 | 3 | 3 | 4 | 4 | 4 | 3 | **21** |

### Top Ranked Branches

1. **a0cf (23)** — Best overall balance of all factors
2. **9d18 (21)** — Elegant fairness + review integration
3. **d249 (21)** — Practical HOLD mechanism
4. **fcb3 (21)** — Clean JSON state + balance guard
5. **37be (20)** — Purest deterministic, best for simplicity
6. **28aa (20)** — Solid sync tooling
7. **64eb (20)** — Best quality pipeline
8. **d038 (20)** — Simplest protocol, best for low-context agents

---

## Key Insights Across All Branches

### Universal Agreements (All 16 branches agree on these)

1. **Eliminate phase gates** (M0/M1/M2) — agents must translate immediately
2. **Pre-complete all setup** on `main` before launching agents
3. **No consensus/voting** — pre-decide format, tools, approach
4. **Push after every completed unit** — make work visible
5. **Experiment/batch scoping** — only discover peers from the same run
6. **Continuous execution** — never stop voluntarily

### Contentious Design Decisions

1. **Deterministic vs. Claim-Based**: 37be, 943d, d038, e163 favor deterministic; others favor claim-based. Deterministic is simpler and faster but less adaptive.

2. **State Files (MD vs. JSON vs. None)**: d038 says no state files; e6ed says JSON; most use Markdown. JSON is most parseable; Markdown is most human-readable.

3. **Sync Daemon vs. On-Demand Sync**: 7aa1, 7d12, c94a, e6ed run continuous daemons; others do on-demand sync. Daemons are more reliable but add complexity.

4. **Quality Review**: 64eb, 9d18, a0cf, d005 include review; others don't. Review improves quality but reduces throughput.

5. **Fairness/Quotas**: 9d18, c94a, d249, fcb3 enforce balance; others don't. Balance prevents monopoly but may slow fast workers.

---

## Recommendation: Best Composite Protocol

The ideal protocol combines:

- **From 37be/e163**: Deterministic stripe assignment (Phase 1) — zero coordination overhead
- **From 943d/d038**: Generic, reusable design — not tied to translation
- **From a0cf**: Run scoping + buddy review system + integration tooling
- **From 9d18/d249**: Fairness gate tied to review (HOLD → must review)
- **From 28aa/fcb3**: Practical executable tooling with JSON state
- **From 64eb**: Two-pass quality pipeline (raw → reviewed → final)

The resulting protocol should be:
- Under 200 lines of protocol text
- Include one executable tool (~500 lines)
- Include one validation tool (~100 lines)
- Support deterministic assignment + claim-based scavenging
- Include lightweight review during balance-gate HOLD periods
- Use JSON for machine-parseable state
