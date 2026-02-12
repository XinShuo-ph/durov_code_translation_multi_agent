# Parallel Translation Protocol (v2)

This is the execution protocol for **16 parallel translation agents**.
It is designed to be concise, executable, and resilient when workers join/leave.

---

## Why this revision exists

Audit of the 16 `book-translation-multi-agent-*` branches showed:

- Only **3/16** branches stayed active for 30+ minutes.
- One branch (`c68e`) produced **29/35 non-demo pages (~83%)**.
- **19 pages** were duplicated across branches.
- `page_013` and `page_043` were each translated on **7 branches**.

The old "lowest available page" protocol was not enough to enforce true collaboration.

---

## Non-negotiable rules

1. **No manual page picking.** Use `tools/sync_daemon.py` for allocation.
2. **One open claim per worker.** Never hold multiple claimed pages.
3. **Push claim before translating.** Claim is not valid until pushed.
4. **Heartbeat every <= 5 minutes.**
5. **Offline threshold:** heartbeat age > 10 min.
6. **Reclaim threshold:** claim can be reclaimed at heartbeat age > 15 min.
7. **Fairness gate (when >= 4 workers online):**
   - If your completed pages are more than `min_online_done + 1`,
     you must do a **REVIEW** action before taking another page.
8. **Peer review requirement (when >= 2 workers online):**
   - Every `DONE` page should receive one `REVIEW` from a different worker.
9. **Production output path:** `translations/raw/page_XXX.json`.
   - Do not place demo/warmup pages in production output.

---

## Mandatory coordinator tool

Use `tools/sync_daemon.py` as the single source of truth.

### Core commands

```bash
# Optional, but recommended before each loop
python3 tools/sync_daemon.py --snapshot --fetch

# Recommended next step for this worker
python3 tools/sync_daemon.py --next-action --worker "$MY_BRANCH" --fetch

# Page number only (for scripts)
python3 tools/sync_daemon.py --next-page --worker "$MY_BRANCH" --fetch

# Inspect one page
python3 tools/sync_daemon.py --check-page --page 24 --fetch
```

### Scope branches for one run

Always scope the coordinator to the run's branch family:

```bash
export SYNC_BRANCH_GLOB="origin/cursor/book-translation-multi-agent-*"
```

If you do not set this, the tool defaults to the same pattern above.

---

## Allocation model (implemented in `sync_daemon.py`)

For online workers sorted by `short_id`:

- Worker at index `i` in `N` online workers gets **lane pages** where:
  - `(page - 1) % N == i`
- If lane has no available pages, tool may assign **spillover**.
- Fairness gate can force `REVIEW` instead of new claim when a worker is too far ahead.

This keeps all agents active and reduces page collisions.

---

## 90-second execution loop (mandatory)

Repeat until all pages are done:

1. **Sync snapshot**
   ```bash
   python3 tools/sync_daemon.py --snapshot --fetch
   ```
2. **Get action**
   ```bash
   python3 tools/sync_daemon.py --next-action --worker "$MY_BRANCH" --fetch
   ```
3. **Execute action**
   - `action=continue`: continue current page.
   - `action=claim`: claim suggested page immediately (commit + push), then translate.
   - `action=review`: review another worker's recent page and push REVIEW commit.
   - `action=idle`: heartbeat commit and wait 60-90s.

4. **After each page completion**
   - Update `WORKER_STATE.md`
   - Commit `DONE`
   - Push immediately
   - Re-enter loop

---

## Commit contract (machine-readable)

Use consistent action keywords in commit subject:

- `SYNC`
- `CLAIM`
- `PROGRESS`
- `DONE`
- `REVIEW`
- `RECLAIM`
- `HEARTBEAT`

### Commit examples

```bash
git commit -m "[c68e] CLAIM: page 024
HEARTBEAT: $(date +%s)"

git commit -m "[c68e] DONE: page 024
HASH: $(sha256sum translations/raw/page_024.json | cut -c1-8)
HEARTBEAT: $(date +%s)"

git commit -m "[c68e] REVIEW: page 024 from 14ce
RESULT: approved_with_minor_edits
HEARTBEAT: $(date +%s)"
```

---

## Required `WORKER_STATE.md` fields

Each worker state file must always have:

- `Heartbeat`
- `Status`
- `Claimed Page`
- `Started At`
- `Completed Pages` table
- `Known Workers` table

Recommended:

- `Peer Reviews` section/table (pages reviewed and result)

---

## Conflict and reclaim behavior

### Duplicate claims

- Earlier claim timestamp wins.
- Losing worker switches to tool-assigned next action.

### Worker disconnect

- Heartbeat stale > 10 min: worker marked offline.
- Heartbeat stale > 15 min: claim becomes reclaimable.
- Reclaimer adds `RECLAIM` commit and note in `WORKER_STATE.md`.

### Returning worker

- Must sync first.
- If page was reclaimed, claim a new page via tool.

---

## Fast startup (copy/paste)

```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | awk -F- '{print $NF}' | tail -c 5)
export SYNC_BRANCH_GLOB="origin/cursor/book-translation-multi-agent-*"

# Register worker state first (if not already registered)
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: register worker
HEARTBEAT: $(date +%s)"
git push origin HEAD

# Start loop
python3 tools/sync_daemon.py --snapshot --fetch
python3 tools/sync_daemon.py --next-action --worker "$MY_BRANCH" --fetch
```

---

## Expected outcomes

If followed, this protocol should:

- Keep most of 16 workers active for longer.
- Prevent "single-worker takeover" while peers are online.
- Reduce duplicate translation work.
- Keep progress continuous when workers disconnect/reconnect.
