# Multi-Agent Parallel Protocol (v2)

Goal: make **16 agents** reliably produce **non-overlapping, reviewable, mergeable** work—without requiring perfect “everyone constantly syncs”.

This protocol is designed from failures observed in the `cursor/book-translation-multi-agent-*` runs:
- too many agents duplicated “bootstrap” work (setup/research/tools) instead of translating
- agents waited for consensus or went idle
- some agents didn’t (or thought they couldn’t) commit/push, so their work never entered the shared picture
- manual syncing was brittle

---

## Non‑Negotiables (what prevents collapse)

1. **Push‑proof in 2 minutes**
   - Immediately create and push `WORKER_STATE.md`.
   - If you cannot push, **do not translate** (you’ll create invisible work and the swarm will collapse). Switch to “review notes only” and report in your state.

2. **No duplicated bootstrap**
   - Setup, extraction, research, tooling are already on `main` (`extracted/`, `research/`, `tools/`).
   - **Do not redo** M0/M1‑style work unless explicitly assigned as Tooling/Infra.

3. **Deterministic sharding first; work stealing second**
   - Default work allocation is a deterministic 16‑way shard so agents can start immediately without collisions.
   - If your shard is empty (or agents went missing), switch to work stealing.

4. **Two‑pass pipeline**
   - A page is “done” only after it has:
     - **translation JSON**
     - **a review note** by a different agent

---

## Work Units + Artifacts

- **Work unit**: one PDF page → one JSON file
- **Translation output**: `translations/page_XXX.json`
- **Review output**: `reviews/page_XXX.<reviewer_short_id>.md`
- **Worker presence**: `WORKER_STATE.md` (on your branch)

---

## The One Command You Must Use

Read `SYNC_SERVICE.md`. Use the executable sync helper:

```bash
python3 tools/sync.py refresh
python3 tools/sync.py status --workers
python3 tools/sync.py next --mode shard
python3 tools/sync.py next --mode steal
python3 tools/sync.py review-queue
```

Why: it removes “I forgot to sync” and makes parallelism work even when agents are short‑lived.

### Run scoping (do this once per swarm)

This repo may contain historical worker branches. Before starting a new 16‑agent run:

1. Pick a unique run prefix, e.g. `book-translation-run-2026-02-12`
2. Update `RUN_CONFIG.json`:
   - set `run_id`
   - set `branch_prefixes` to `origin/cursor/<your-run-prefix>-`
3. Ensure all worker branches are created with that prefix.

---

## Startup (every agent)

### 1) Register (push‑proof)

```bash
cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
# Fill it in (branch, short id, heartbeat, status)
git add WORKER_STATE.md
git commit -m "[<id>] SYNC: register\nHEARTBEAT: $(date +%s)"
git push origin HEAD
```

### 2) Sync once (fast)

```bash
python3 tools/sync.py refresh
python3 tools/sync.py status
```

---

## Translation Loop (default role: Translator)

### 1) Pick next page (shard mode)

```bash
PAGE=$(python3 tools/sync.py next --mode shard) || PAGE=$(python3 tools/sync.py next --mode steal)
echo "Working page: $PAGE"
```

### 2) Claim (lightweight, best‑effort)

Update your `WORKER_STATE.md`:
- set **Status** = translating
- set **Claimed Page** = \(PAGE\)
- set **Heartbeat** = current timestamp

Commit + push immediately (this is how others avoid stepping on your work):

```bash
git add WORKER_STATE.md
git commit -m "[<id>] CLAIM: page $PAGE\nHEARTBEAT: $(date +%s)"
git push origin HEAD
```

### 3) Translate + save

- Source text: `extracted/pages/page_$(printf '%03d' $PAGE).txt`
- Output: `translations/page_$(printf '%03d' $PAGE).json`
- Follow the JSON schema in `instructions.md`

Validate before broadcasting:

```bash
python3 tools/validate_translation.py "translations/page_$(printf '%03d' $PAGE).json"
```

### 4) Broadcast completion

```bash
git add "translations/page_$(printf '%03d' $PAGE).json" WORKER_STATE.md
git commit -m "[<id>] DONE: page $PAGE\nHEARTBEAT: $(date +%s)"
git push origin HEAD
```

Then immediately pick the next page and repeat.

---

## Review Loop (default role: Reviewer)

Deterministic pairing (“buddy system”):
- each shard slot reviews the **previous slot’s** pages
- this yields even review load without coordination chat

### 1) Get your review queue

```bash
python3 tools/sync.py refresh
python3 tools/sync.py review-queue
```

This prints lines like:

```
15    origin/cursor/some-worker-14ce
```

### 2) Write a review note

Create:
- `reviews/page_015.<your_id>.md`

Keep it short and actionable:
- **terminology consistency** (glossary)
- **meaning/omissions**
- **tone/voice**
- **JSON issues** (missing fields, empty strings, id gaps)

Commit + push:

```bash
git add "reviews/page_015.<your_id>.md" WORKER_STATE.md
git commit -m "[<id>] REVIEW: page 15\nHEARTBEAT: $(date +%s)"
git push origin HEAD
```

---

## Integration (prevents “one agent at the end”)

Any idle agent can act as an integrator (no special authority required):

1. Collect the best available page JSONs from all worker branches:

```bash
python3 tools/collect_translations.py --fetch --output translations
```

2. Validate locally (spot check or batch):

```bash
python3 tools/validate_translation.py translations/page_*.json
```

3. Commit on your branch and push (so it can be merged via PR):

```bash
git add translations/
git commit -m "chore: collect translations from worker branches"
git push origin HEAD
```

This turns integration into a **repeatable task** that multiple agents can do, instead of a single heroic final agent.

---

## Timeouts + Reclaiming

- **Online**: heartbeat < 10 minutes old
- **Reclaim**: if a page is claimed by an offline worker for > 15 minutes, treat it as available
- The sync helper uses both:
  - “done anywhere” = don’t redo it
  - “claimed anywhere” = avoid collisions

---

## Commit Message Contract (machine-readable)

Use:

```
[<id>] <ACTION>: <details>
HEARTBEAT: <unix_ts>
```

Actions:
- `SYNC` (register / resync)
- `CLAIM` (starting a page)
- `DONE` (page JSON saved)
- `REVIEW` (review note written)
- `INTEGRATE` (collection/merge work)

