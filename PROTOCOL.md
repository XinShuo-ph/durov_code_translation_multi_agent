# Multi-Agent Parallel Translation Protocol (v2)

This protocol is optimized for **real parallelism** (many agents doing useful work for a long time) and **high quality** (review + integration), using git branches as the communication bus.

It replaces the “everyone does setup + lowest-page claiming” pattern that caused most agents to stall after bootstrap and left final integration to a single agent.

---

## Goals

- **Sustain parallel throughput**: keep most agents translating most of the time.
- **Prevent wasted work**: minimize duplicated pages and “waiting for consensus”.
- **Ship quality**: every page passes a validator and gets at least one review before final integration.
- **Be executable**: concrete commands + file paths; minimal ceremony.

## Non-goals

- Perfect real-time coordination (git is eventual-consistency).
- Heavy long-running daemons (optional tools exist, but protocol should work without them).

---

## Roles (must be assigned at run start)

You want **at least 70%** of agents as translators at all times.

- **Conductor (1)**: starts the run, assigns roles + page ranges, monitors utilization, resolves disputes.
- **Integrator (1)**: continuously pulls finished pages into `main`, updates progress, enforces quality gates.
- **Reviewers (2–4)**: review pages and request fixes.
- **Terminology/Tools (0–1)**: only if needed; maintains glossary + validator, otherwise translate.
- **Translators (everyone else)**: translate pages (raw), respond to reviews.

If there is no explicit Conductor, the Integrator acts as Conductor.

---

## Canonical paths (single source of truth)

- **Input**: `extracted/pages/page_XXX.txt`
- **Worker output (raw)**: `translations/raw/page_XXX.json`
- **Integrated output (final)**: `translations/final/page_XXX.json`
- **Reviews**: `reviews/page_XXX.<reviewerShortId>.md`

PDF generation is optional and **should not block** translation throughput.

---

## Bootstrap rule (prevents the “everyone did M0/M1 then stopped” failure mode)

**Default**: assume the repo is already bootstrapped. Start translating immediately.

Only run bootstrap tasks if the Conductor explicitly announces “BOOTSTRAP REQUIRED”.

If bootstrap is required:
- **Max 10 minutes**.
- **Max 2 agents** on tools/format verification.
- Everyone else translates pages using the existing pipeline; do **not** wait for consensus.

---

## Allocation: page ranges first, then work-stealing

### Primary allocation (preferred): page ranges from the Conductor

At run start, Conductor publishes a simple mapping (in their first commit + in their `WORKER_STATE.md` notes):

- Each translator gets a **contiguous page range** (e.g. `23–28`).
- Translators work **only inside their range** until it’s complete.

This keeps agents from colliding on the same “lowest available” pages and keeps everyone busy.

### Work-stealing (mandatory when you finish your range)

When you finish your assigned range:
- Pick the **lowest unfinished page in any range owned by an offline worker**, or
- Pick the **lowest unfinished page globally**.

Never stay idle because “my range is done”.

---

## Coordination: use the lightweight sync helper (recommended)

Before claiming a page, run:

```bash
python3 tools/team.py status
# Optional: filter to just the current run's branches
python3 tools/team.py --branch-regex 'book-translation-multi-agent' status
python3 tools/team.py check-page 17
python3 tools/team.py next-page
```

If you don’t use the helper, you must still:
- `git fetch origin --prune`
- inspect other workers’ `WORKER_STATE.md`
- avoid claiming pages that are claimed by online workers

---

## The production loop (what every translator does)

### 0) Register (once per session)

Create `WORKER_STATE.md` from the template, commit, push.

### 1) Claim exactly one page

Update `WORKER_STATE.md`:
- **Status**: `translating`
- **Claimed Page**: `N`
- **Started At**: timestamp

Push immediately.

### 2) Translate (raw)

Read:
- `extracted/pages/page_XXX.txt`

Write:
- `translations/raw/page_XXX.json`

Rules:
- Don’t skip content.
- Keep glossary terms consistent (`research/glossary.md`).
- If stuck \(>5 minutes on one sentence\), add a brief `translator_notes` entry and continue.

### 3) Self-check (mandatory)

```bash
python3 tools/validate_translation.py translations/raw/page_XXX.json
```

### 4) Publish “READY_FOR_REVIEW”

Commit + push:
- `translations/raw/page_XXX.json`
- `WORKER_STATE.md` (mark page done + set status to `ready_for_review`)

### 5) Immediately claim your next page

Don’t wait for review to start the next page. The system is a pipeline.

---

## Review loop (what reviewers do)

Pick pages marked `READY_FOR_REVIEW` (or the lowest pages not yet reviewed on `main` once integration starts).

Create a review file on **your branch**:
- `reviews/page_XXX.<yourShortId>.md`

The review must include:
- **Verdict**: `LGTM` | `NEEDS_FIXES` | `MAJOR_REWRITE`
- **Issues**: bullet list with sentence ids where possible
- **Glossary**: any term inconsistencies

Commit + push the review file.

Reviewers should target **fast, actionable feedback** (timebox: ~5–10 minutes per page).

---

## Integration loop (what the Integrator does)

The Integrator’s job is to prevent the “endgame becomes one agent translating everything” collapse by merging continuously.

Continuously:
- Pull `translations/raw/page_XXX.json` from worker branches (prefer pages with `LGTM` review).
- Run validator.
- Promote into `translations/final/page_XXX.json` on `main`.
- Update a progress note (optional): `STATE.md` or a dedicated progress table.

Integration gates:
- Must pass `tools/validate_translation.py`.
- If review says `NEEDS_FIXES`, either request fixes or apply minimal edits directly (don’t block the pipeline).

---

## Heartbeats, timeouts, reclaiming

- **Heartbeat**: every meaningful commit includes `HEARTBEAT: <unix>` in the message and updates `WORKER_STATE.md`.
- **Online**: heartbeat age < 10 minutes.
- **Reclaim**: if worker heartbeat age ≥ 15 minutes, their claimed page may be reclaimed.

When reclaiming:
- Note it in your `WORKER_STATE.md` (“Reclaimed page X from <worker>”).
- Prefer reclaiming **stalled** pages over starting brand-new ones.

---

## Commit message format (machine-readable)

```
[<shortId>] <ACTION>: <what>
PAGE: <N or ->
STATE: <translating|ready_for_review|reviewing|integrating|idle>
HEARTBEAT: <unix>
```

Actions:
- `SYNC`, `CLAIM`, `PROGRESS`, `READY_FOR_REVIEW`, `REVIEW`, `INTEGRATE`, `RECLAIM`, `SESSION_END`

---

## Rules that keep agents working (anti-stall)

- **No waiting**: if you’re not translating, you’re reviewing or integrating.
- **No redundant bootstrap**: don’t redo “setup/format exploration” unless explicitly assigned.
- **One page at a time**: claim 1, ship it, claim next.
- **Pipeline mindset**: translation continues while reviews happen in parallel.

---

## If you only read one thing

1) Claim a page, translate it to `translations/raw/page_XXX.json`, validate, push, repeat.  
2) Reviewers produce `reviews/page_XXX.<id>.md`.  
3) Integrator merges continuously into `translations/final/` on `main`.

