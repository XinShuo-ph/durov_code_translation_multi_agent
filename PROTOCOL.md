# Parallel Translation Protocol v3

This protocol is optimized for **real parallelism** (not just eventual completion).
It is short, executable, and machine-checkable.

## Why this replaces the old protocol

From the 16 `book-translation-multi-agent-*` branches:

- Only **3/16** workers sustained translation work.
- Final stage collapsed to **1 active worker**.
- Roughly **48%** of produced page artifacts were duplicates.

v3 addresses this with command-level gating, strict worker state, and fairness limits.

---

## Hard Rules (non-negotiable)

1. **Run `tools/coord.py next` before every claim.**
2. **Use the exact `WORKER_STATE.md` schema from `WORKER_STATE_TEMPLATE.md`.**
3. **One claimed page per worker at a time.**
4. **Push immediately after claim and after done.**
5. **Heartbeat must be refreshed at least every 5 minutes.**
6. **Reclaim stale claims only via `tools/coord.py stale`.**

If a command says `HOLD`, do not claim a new page.

---

## Required Files

- `WORKER_STATE.md` (your live state; machine-parseable)
- `translations/raw/page_XXX.json` (preferred) or `translations/page_XXX.json`

---

## 60-Second Startup

```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | rg -o '[^-]+$')
NOW=$(date +%s)

cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
# Fill Branch, Short-ID, Heartbeat, Last-Sync

git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: worker online
HEARTBEAT: $NOW"
git push origin HEAD
```

---

## Execution Loop (repeat continuously)

### Step 1) Sync + observe team health

```bash
git fetch origin --prune
python3 tools/coord.py status --total-pages 99
```

### Step 2) Ask coordinator for the next page

```bash
python3 tools/coord.py next --worker-id "$MY_SHORT_ID" --total-pages 99
```

Possible outputs:

- `NEXT_PAGE=K` -> claim page `K`
- `HOLD=lead_cap` -> you are too far ahead; do review/help tasks
- `NEXT_PAGE=none` -> no claimable pages left

### Step 3) Claim (only when `NEXT_PAGE` is returned)

Update `WORKER_STATE.md`:

- `Heartbeat: <now>`
- `Status: translating`
- `Claimed-Page: <K>`
- `Claimed-At: <now>`
- `Last-Sync: <now>`

Then:

```bash
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] CLAIM: page K
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Step 4) Translate + save

Save:

- `translations/raw/page_$(printf '%03d' K).json` (preferred), or
- `translations/page_$(printf '%03d' K).json`

### Step 5) Complete + broadcast

Update `WORKER_STATE.md`:

- `Heartbeat: <now>`
- `Status: idle` (or `reviewing`)
- `Claimed-Page: none`
- append `K` to `Completed-Pages`
- `Last-Sync: <now>`

Then:

```bash
git add "translations/raw/page_$(printf '%03d' K).json" WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] DONE: page K
HASH: $(sha256sum "translations/raw/page_$(printf '%03d' K).json" | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

If you used `translations/page_XXX.json`, keep commit paths consistent.

---

## Fairness / Anti-Monopoly Rules

`tools/coord.py next` enforces:

1. **Sharded assignment**: available pages are distributed by worker-id shard.
2. **Lead cap**: if at least 4 workers are online, a worker cannot exceed the
   slowest online worker by more than 2 completed pages.

When lead cap is hit, the worker receives `HOLD=lead_cap`.

Allowed HOLD tasks:

- review another worker’s recent page for obvious omissions
- update glossary/notes
- check for stale claims (`tools/coord.py stale`)

---

## Stale Worker / Reclaim Rules

Timeouts:

- Online timeout: heartbeat older than **600s** (10 min) -> offline
- Reclaim timeout: heartbeat older than **900s** (15 min) and page still claimed

Check reclaimable claims:

```bash
python3 tools/coord.py stale --total-pages 99
```

If stale claim exists, reclaim with commit message:

```bash
[$MY_SHORT_ID] RECLAIM: page K from <worker>
HEARTBEAT: <unix_ts>
```

---

## Recovery Modes

### Many workers online (>=4)
- Full fairness enabled (lead cap + sharding)

### Small active team (1-3 online)
- Lead cap is relaxed automatically
- Sharding still applies when possible

### Returning after disconnect
1. `git fetch origin --prune`
2. `python3 tools/coord.py status --total-pages 99`
3. if old claim was reclaimed, request fresh page via `next`

---

## Commit Message Contract

Use machine-readable actions:

- `SYNC`
- `CLAIM`
- `DONE`
- `RECLAIM`
- `REVIEW`

Format:

```text
[short_id] ACTION: short description
HEARTBEAT: unix_timestamp
```

---

## What to Avoid

- claiming without running `coord.py next`
- custom worker-state formats
- claiming multiple pages
- working with stale heartbeat
- waiting for consensus on tooling

---

## One-Page Checklist

1. Sync (`git fetch`)
2. Status (`coord.py status`)
3. Next (`coord.py next`)
4. Claim + push
5. Translate
6. Done + push
7. Repeat

If blocked, publish it in `WORKER_STATE.md` (`Status: blocked`, `Notes: ...`) and push.

