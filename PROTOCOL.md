# Parallel Translation Protocol (v2)

This protocol is designed for **real parallel execution** by many agents (e.g., 16 workers).
It replaces milestone-heavy behavior with a translation-first loop and machine-checked claiming.

---

## Why v2 Exists (Evidence From 16 `book-translation-multi-agent-*` Branches)

Investigation summary:

- 16 total worker branches were active.
- Only **8/16** reached M2 translation (`M0: 4`, `M1: 4`, `M2: 8`).
- Translation commits were highly concentrated: top 3 branches produced **78.79%** of all translation commits.
- We observed **19 duplicate pages** claimed/completed across branches.
- Timeline collapsed from multi-worker activity to one long-tail worker:
  - early peak: 7 branches active in the same 10-minute bucket
  - final 40+ minutes: only one branch remained active

Root causes:

1. Workers repeated M0/M1 setup instead of translating.
2. Consensus waiting states blocked M2 start.
3. Manual claim workflow allowed races/duplication.
4. Worker-state formats drifted and became hard to parse reliably.

---

## Non-Negotiable Rules

1. **Translation-first**: no per-worker M0/M1 gating before page work.
2. **Machine-checked claims only**: run coordinator command before every claim.
3. **One live page lease per worker** (no multi-claim hoarding).
4. **Push immediately** after CLAIM and DONE.
5. **Heartbeat <= 5 min** cadence while active.
6. **Reclaim stale leases** after offline + timeout.

---

## Required Files

- `WORKER_STATE.md` (strict template format)
- `translations/page_XXX.json` (one page per file)
- `tools/parallel_coord.py` (claim gate + scheduler)

---

## Timeouts

| Item | Threshold |
|---|---|
| Heartbeat stale (offline) | 10 min |
| Lease timeout (reclaim eligible) | 15 min |
| Recommended heartbeat update | <= 5 min |
| Sync cadence | Every page (mandatory) |

---

## Scheduling Strategy (How We Keep 16 Workers Busy)

Default assignment is **shard-first with fallback**:

1. Build online worker list sorted by `short_id`.
2. If you are rank `i` among `N` workers, your preferred pages satisfy:
   - `(page - 1) % N == i`
3. Pick the lowest available page in your shard.
4. If shard is empty, steal the lowest global available page.

This keeps workers spread out while still finishing tail pages quickly.

The scheduler is implemented by:

```bash
python3 tools/parallel_coord.py next-page
```

---

## Startup (Per Worker)

```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=${MY_BRANCH##*-}
NOW=$(date +%s)

if [ ! -f WORKER_STATE.md ]; then
  cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
fi
```

Fill `WORKER_STATE.md` identity fields once, then register:

```bash
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: worker online
HEARTBEAT: $NOW"
git push origin HEAD
```

---

## Mandatory Claim Gate (Borrowed and Adapted From StoneRecords)

Before claiming any page, run:

```bash
git fetch origin --prune
python3 tools/parallel_coord.py snapshot
NEXT_PAGE=$(python3 tools/parallel_coord.py next-page --plain)
python3 tools/parallel_coord.py check-page "$NEXT_PAGE"
```

If `check-page` is not `status=available`, do not claim it. Re-run `next-page`.

---

## Claim Procedure (One Page Only)

1. Compute and verify `NEXT_PAGE` with the mandatory gate.
2. Update `WORKER_STATE.md`:
   - `Heartbeat = now`
   - `Status = translating`
   - `Claimed Page = NEXT_PAGE`
   - `Lease Expires At = now + 900`
   - `Started At = now`
3. Commit + push immediately.

Commit format:

```text
[SHORT_ID] CLAIM: page XXX
HEARTBEAT: <unix_ts>
LEASE_EXPIRES_AT: <unix_ts>
```

---

## Completion Procedure

1. Save result to `translations/page_XXX.json`.
2. Update `WORKER_STATE.md`:
   - Append page row to `Completed Pages`.
   - Clear current claim (`Claimed Page: none`, `Lease Expires At: -`, `Started At: -`).
   - `Status = online` (or `idle` if pausing).
   - `Heartbeat = now`.
3. Commit + push immediately.

Commit format:

```text
[SHORT_ID] DONE: page XXX
HASH: <sha256_8chars>
HEARTBEAT: <unix_ts>
```

---

## Conflict and Reclaim Rules

### Claim Collision

If two workers claim the same page:

- earlier commit timestamp wins,
- later worker releases claim immediately and reruns claim gate.

### Reclaim Stale Work

A page may be reclaimed when both are true:

1. owner heartbeat is stale (>10 min), and
2. lease has expired (>15 min since claim / lease expiry).

Use commit action `RECLAIM`.

---

## Continuous Execution Loop (Per Page)

Repeat this loop until no pages remain:

1. `git fetch origin --prune`
2. `NEXT_PAGE=$(python3 tools/parallel_coord.py next-page --plain)`
3. `python3 tools/parallel_coord.py check-page "$NEXT_PAGE"`
4. CLAIM (update state, commit, push)
5. Translate page JSON
6. DONE (update state, commit, push)

Do not wait for additional consensus unless there is a true blocker.

---

## Anti-Stall Guardrails

1. **No consensus barrier** for entering translation.
2. Workers still in M0/M1-style states must switch to translation immediately.
3. Any worker with no DONE for >20 min while online should either:
   - release/refresh lease, or
   - move to an unclaimed page after sync.
4. If duplicate claims are detected, resolve before new claims.

---

## Health Check Commands

Snapshot:

```bash
python3 tools/parallel_coord.py snapshot
```

Single page availability:

```bash
python3 tools/parallel_coord.py check-page 37
```

Session audit (distribution, duplicates, milestones):

```bash
python3 tools/parallel_coord.py audit
```

---

## Minimal Commit Actions

| Action | Meaning |
|---|---|
| `SYNC` | Worker registration / heartbeat update |
| `CLAIM` | Acquired page lease |
| `DONE` | Completed page translation |
| `RECLAIM` | Took over stale page lease |
| `SESSION_END` | Graceful stop with released claim |

---

Protocol goal: **high-quality translation and sustained parallel throughput**, not isolated hero runs.
