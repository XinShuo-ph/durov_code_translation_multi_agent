# Multi-Agent Parallel Protocol v3 (Concise + Executable)

This protocol is designed from the 16 `book-translation-multi-agent-*` branches.

## Postmortem Signals (Why v3)

- 16 workers started, but active workers dropped to 1 near the end.
- Only 37 unique pages were produced across all 16 branches.
- Demo pages were over-translated (`page_013` and `page_043` appeared in 7 branches each).
- Most branches spent time on setup/consensus instead of sustained translation.

v3 fixes this with **immediate translation**, **batch-local discovery**, **machine-readable state**, and an **executable coordinator**.

---

## Core Rules (Non-Negotiable)

1. **No M0/M1/M2 phase gates**. Start translating immediately.
2. **Only coordinate with your batch peers** (same branch prefix, excluding the last `-xxxx` worker ID).
3. **Use `WORKER_STATE.json`** (not free-form markdown) as source of truth.
4. **Claim via tool before translating**:
   - `python3 tools/parallel_coord.py claim ...`
5. **One live claim per worker**.
6. **Balance guard enabled**: if you are too far ahead of active peers, claim is throttled unless forced.
7. **Heartbeat freshness**:
   - worker offline after 10 minutes stale heartbeat
   - claim reclaimable after 15 minutes stale claim

---

## Required File Conventions

- Worker state: `WORKER_STATE.json`
- Output file: `translations/page_XXX.json` (three-digit page number)

Use `WORKER_STATE_TEMPLATE.json` to initialize local state.

---

## Coordinator Tool (Executable Protocol)

All coordination commands are implemented in:

```bash
python3 tools/parallel_coord.py <command> [flags]
```

### Commands

- `status` - online workers, live claims, completed coverage, duplicates
- `next` - recommended next page for this worker
- `check` - availability for one page
- `claim` - atomically claim a page in local `WORKER_STATE.json`
- `done` - validate page JSON + mark page complete in local state
- `heartbeat` - keep worker online while reviewing/debugging

---

## 3-Minute Startup

```bash
# 1) Identity
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | awk -F- '{print $NF}')

# 2) Init state once
test -f WORKER_STATE.json || cp WORKER_STATE_TEMPLATE.json WORKER_STATE.json

# 3) Sync view
python3 tools/parallel_coord.py --fetch status

# 4) Pick page
NEXT_PAGE=$(python3 tools/parallel_coord.py --fetch next --worker "$MY_SHORT_ID")

# 5) Claim and broadcast
python3 tools/parallel_coord.py --fetch claim --worker "$MY_SHORT_ID" --page "$NEXT_PAGE"
git add WORKER_STATE.json
git commit -m "[$MY_SHORT_ID] CLAIM: page $NEXT_PAGE
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

---

## Main Work Loop

Repeat until no pages are left:

1. **Find next page**
   ```bash
   NEXT_PAGE=$(python3 tools/parallel_coord.py --fetch next --worker "$MY_SHORT_ID")
   test "$NEXT_PAGE" = "NONE" && echo "All pages done" && break
   ```
2. **Claim**
   ```bash
   python3 tools/parallel_coord.py --fetch claim --worker "$MY_SHORT_ID" --page "$NEXT_PAGE"
   git add WORKER_STATE.json
   git commit -m "[$MY_SHORT_ID] CLAIM: page $NEXT_PAGE
   HEARTBEAT: $(date +%s)"
   git push origin HEAD
   ```
3. **Translate** to `translations/page_XXX.json`
4. **Mark done + validate JSON**
   ```bash
   FILE="translations/page_$(printf '%03d' "$NEXT_PAGE").json"
   python3 tools/parallel_coord.py done --worker "$MY_SHORT_ID" --file "$FILE"
   git add "$FILE" WORKER_STATE.json
   git commit -m "[$MY_SHORT_ID] DONE: page $NEXT_PAGE
   HASH: $(sha256sum "$FILE" | cut -c1-8)
   HEARTBEAT: $(date +%s)"
   git push origin HEAD
   ```

If you are temporarily not translating, run:

```bash
python3 tools/parallel_coord.py heartbeat --worker "$MY_SHORT_ID" --status reviewing
git add WORKER_STATE.json && git commit -m "[$MY_SHORT_ID] HEARTBEAT" && git push origin HEAD
```

---

## Scheduling Semantics (What `next` Does)

For pages `1..99`, a page is available iff it is:

- not already completed anywhere in the batch
- not claimed by an online worker with a fresh claim

Then the coordinator applies:

1. **Striping preference**: pages are striped by sorted online worker IDs (`(page-1) % N`) to spread workers.
2. **Balance guard**: if a worker is more than `balance_slack` (default: 2 pages) ahead of the slowest online peer, new claims are throttled unless `--force`.

This keeps parallelism broad while still allowing progress if peers disappear.

---

## Failure Handling

### Claim conflict
- Earlier pushed claim wins.
- Losing worker runs `next` again and claims a different page.

### Worker disappears
- Offline after 10 minutes stale heartbeat.
- Their claim becomes reclaimable after 15 minutes.

### Reconnect after interruption
1. `python3 tools/parallel_coord.py --fetch status`
2. verify old claim with `check --page X`
3. if already done/claimed, pick new page with `next`

### Force override (exception path)
Use `--force` only when:
- balance guard is blocking and peers are clearly inactive
- human supervisor requests override

---

## Commit Message Contract

Use parseable commit messages:

```text
[SHORT_ID] CLAIM: page 23
HEARTBEAT: 1767254400
```

```text
[SHORT_ID] DONE: page 23
HASH: a1b2c3d4
HEARTBEAT: 1767254700
```

---

## Anti-Patterns (Do Not Repeat)

- Do not wait for global format/tool consensus.
- Do not do heavy shared setup on every worker.
- Do not discover unrelated old experiment branches.
- Do not keep coordination state only in free-form markdown.
- Do not hold multiple active page claims.
- Do not continue claiming indefinitely while active peers are far behind.

---

## Minimal Definition of Done

A worker session is valid only if all are true:

1. Every claimed page is pushed promptly.
2. Every completed page has valid JSON and is committed.
3. `WORKER_STATE.json` heartbeat is fresh during active work.
4. Claims and completions are made via `tools/parallel_coord.py`.

