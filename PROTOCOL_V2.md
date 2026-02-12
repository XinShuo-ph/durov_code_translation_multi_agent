# Collaborative Translation Protocol (v2: Parallel + Executable)

This protocol is optimized for **16+ agents translating in parallel** without duplication and without “one agent going solo”.

If you follow only one rule: **never claim a page without using the sync service**.

## Work unit + canonical output

- **Work unit**: 1 page (from `extracted/pages/page_XXX.txt`)
- **Output**: `translations/page_XXX.json` (one page per file)
- **Definition of “done”**: the JSON exists and passes validation (see below)

## Non‑negotiables (these prevent the known failures)

- **Prefix isolation**: only coordinate with workers from the **same experiment batch** (same branch prefix).
- **Executable sync**: run `tools/sync_service.py` before claiming pages.
- **Continuous integration**: publish your completed pages in a way other agents can consume immediately (PR or shared integration branch).
- **Machine-checkable output**: validate JSON before pushing.

## Quick start (copy/paste)

### 0) Register as a worker (once per branch)

```bash
cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
# edit WORKER_STATE.md: fill Branch, Short ID, Heartbeat, Status
git add WORKER_STATE.md
git commit -m "[${MY_SHORT_ID}] SYNC: Registering as active worker
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### 1) Sync + find a page

```bash
python3 tools/sync_service.py status
PAGE=$(python3 tools/sync_service.py next-page)
echo "Claiming page: $PAGE"
python3 tools/sync_service.py check-page "$PAGE"
```

### 2) Claim (1 page only) and broadcast immediately

Edit `WORKER_STATE.md`:
- set `Heartbeat` to `$(date +%s)`
- set `Status` to `translating`
- set `Claimed Page` to `$PAGE`
- set `Started At` to `$(date +%s)`

Then:

```bash
git add WORKER_STATE.md
git commit -m "[${MY_SHORT_ID}] CLAIM: Starting page ${PAGE}
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### 3) Translate → validate → publish

Create `translations/page_$(printf '%03d' "$PAGE").json`, then:

```bash
python3 tools/validate_translation_json.py "translations/page_$(printf '%03d' "$PAGE").json"
git add "translations/page_$(printf '%03d' "$PAGE").json" WORKER_STATE.md
git commit -m "[${MY_SHORT_ID}] DONE: Completed page ${PAGE}
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### 4) Integrate so nobody has to redo your pages

One of these must be true (pick the one your run uses):

- **Preferred**: open/keep a PR from your worker branch into the integration branch (often `main`).
- **Alternative**: if all workers are allowed to push to a shared branch, publish there directly (requires `git pull --rebase` discipline).

Minimal PR flow:

```bash
gh pr create --fill --base main
```

### 5) Repeat (don’t stop early)

Loop: sync → claim → translate → validate → publish → integrate.

## Coordination rules

### 1) Worker discovery MUST be prefix-filtered

The earlier experiments failed because agents “discovered” stale branches from older runs.

`tools/sync_service.py` already filters peers using:

- my branch: `cursor/<prefix>-<id>`
- peers: `origin/cursor/<prefix>-*`

### 2) Completion is file-based, not “someone said so”

A page is done if a committed file exists:

- `translations/page_XXX.json` (canonical)

Legacy paths are still recognized by the sync service for compatibility:

- `translations/raw/page_XXX.json`
- `translations/final/page_XXX.json`

### 3) Claim leases are short

- **Claim exactly 1 page**
- If you can’t complete it quickly, **release it** (set `Claimed Page: none`, `Status: idle`) and push.

## What this fixes (from the 16-branch experiment)

- **Mass duplication**: prevented by mandatory prefix-filtered sync (`tools/sync_service.py next-page`)
- **Only 3/16 agents translating**: reduced by removing “consensus/setup tasks” from worker flow; workers translate immediately
- **One agent translating the whole book**: prevented by mandatory integration (PRs or shared integration branch) so pages accumulate centrally

## Reference docs

- `SYNC_SERVICE.md`: details of `tools/sync_service.py`
- `instructions.md`: translation format and quality requirements

