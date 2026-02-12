# Multi-Agent Parallel Protocol (v3)

This protocol is optimized for **sustained parallel work** (16+ agents) and prevents the common collapse mode: *a few agents do work, then one agent finishes the entire book alone*.

It is based on failures observed in the `book-translation-multi-agent-*` and `collaborative-translation-initiation-*` runs:
- **Wrong peer discovery** (agents scanned all `cursor/*` branches, including stale experiments) → massive duplication
- **Phase gates / consensus** → most agents never reached translation
- **No integration lane** → finished work stayed stranded on worker branches, so a single agent re-did everything in one place

---

## Non-negotiables

### 1) Experiment ID (branch filtering) is mandatory

All worker branches for an experiment MUST share a prefix and include an experiment id:

- `cursor/exp-<ID>-translate-<xxxx>`
- `cursor/exp-<ID>-review-<xxxx>`
- `cursor/exp-<ID>-integrate-<xxxx>`

**Rule**: Workers only sync against `origin/cursor/exp-<ID>-*`. Do **not** scan all `origin/cursor/*`.

### 2) One page = one deliverable file

The only required work product is:

- `translations/page_XXX.json`

(If you used `translations/raw/` or `translations/final/` in older runs, the integrator will still be able to collect it, but new work should use the canonical path.)

### 3) Always validate before you push

Run:

```bash
python3 tools/validate_translation.py translations/page_XXX.json
```

---

## Roles (run in parallel)

### Coordinator (1 agent)
- Picks `exp-<ID>` and announces it.
- Spawns agents with correct branch naming.
- Monitors progress (coverage, missing pages, duplication hotspots).

### Translators (most agents)
- Produce page JSONs only.
- Never block on consensus or toolchain debates.

### Reviewers (2–4 agents)
- Sample-check pages for completeness, tone, and terminology.
- File small fix commits (or report pages to re-translate).

### Integrator (1–2 agents)
- Collects the best available page JSON for each page across worker branches.
- Merges into the integration branch (or `main`) on a cadence.

---

## Translator workflow (executable)

### Step 0: Ensure your branch name is correct

Example:

- `cursor/exp-005-translate-c68e`

### Step 1: Sync status (scan only your experiment)

```bash
python3 tools/sync.py status
```

If your branch name does not include `exp-<ID>`, pass the prefix explicitly:

```bash
python3 tools/sync.py --prefix origin/cursor/exp-005- status
```

### Step 2: Pick your next page (staggered start, reduces duplication)

```bash
NEXT_PAGE=$(python3 tools/sync.py next)
echo "$NEXT_PAGE"
```

This uses a deterministic start page derived from your short id (to avoid 10+ agents starting on page 1).

### Step 3: Translate the page

Input:
- `extracted/pages/page_XXX.txt`

Output:
- `translations/page_XXX.json`

### Step 4: Validate, commit, push

```bash
python3 tools/validate_translation.py "translations/page_$(printf '%03d' "$NEXT_PAGE").json"
MY_SHORT_ID=$(git branch --show-current | grep -oE '[0-9a-fA-F]{4}$' || echo xxxx)
git add "translations/page_$(printf '%03d' "$NEXT_PAGE").json"
git commit -m "[${MY_SHORT_ID}] page ${NEXT_PAGE}: translate"
git push origin HEAD
```

### Step 5: Repeat (no waiting)

---

## Integrator workflow (executable)

The integrator’s job is what prevents “stranded work” and single-agent re-translation.

### Collect best-per-page from all worker branches

```bash
python3 tools/collect_translations.py \
  --prefix origin/cursor/exp-005- \
  --out-dir translations \
  --manifest collected_manifest.json
```

Then validate a subset (or all pages) and commit/merge as usual.

---

## Reviewer workflow (lightweight)

Reviewers keep overall quality high without blocking translators.

- Pick 3–5 recently added pages (from the manifest or branch diffs)
- Run validation:
  - `python3 tools/validate_translation.py translations/page_XXX.json`
- Spot-check:
  - no missing/empty `ru/en/zh/ja`
  - terminology consistent with `research/glossary.md`
  - sentence segmentation is reasonable (not one giant paragraph)

If you can make a small fix safely, commit it as a targeted change; otherwise, report the page number to be re-translated.

---

## Collaboration rules that keep agents active

### No phase gates
- **Never** require “M0/M1/M2” completion, voting, or consensus before translating.
- Tooling/design debates happen in parallel; translation continues regardless.

### “Push-visible progress” cadence
- Translators push **every page** (or every 2 pages max).
- Reviewers push small, targeted fixes; do not batch 30+ pages of edits.
- Integrator merges on a cadence (e.g., every 30–60 minutes).

### Duplication policy
- Duplication is acceptable, but **avoidable duplication is not**.
- Always run `tools/sync.py next` before starting a new page.

---

## Anti-patterns (things that caused prior runs to collapse)

- Scanning all `origin/cursor/*` branches (stale peer discovery)
- Waiting for votes/consensus before doing translation
- Spending most time on “status files” instead of page outputs
- No integrator role (work never gets assembled, so a single agent redoes it)

---

## Optional: WORKER_STATE.md

If you want a human-readable status file, keep it minimal and update only at session start/end.
The protocol does **not** rely on heartbeats for correctness.

