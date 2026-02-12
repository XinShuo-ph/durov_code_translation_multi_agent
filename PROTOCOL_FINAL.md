# Multi-Agent Parallel Work Protocol (Final — Synthesized from 16 Branches)

> Distilled from 16 independent protocol designs that each analyzed the same 32-agent experiment data.
> This protocol preserves **translation quality** while maximizing **parallel throughput**.

---

## Design Principles

1. **Produce output from minute one.** No setup, no research, no voting. All prep is pre-done.
2. **Deterministic first, adaptive second.** Phase 1 needs zero coordination. Phase 2 adapts to reality.
3. **Quality is enforced, not hoped for.** Validation is mandatory. Review is triggered automatically.
4. **Protocol must fit in an agent's context.** Under 200 lines of rules. One tool. One validator.

---

## Two Phases

### Phase 1 — STRIPE (Zero Coordination)

Each agent gets a **deterministic, non-overlapping page set** computed from its sorted position among peers.

```bash
# Discover peers (once, <30 seconds)
MY_BRANCH=$(git branch --show-current)
MY_ID=${MY_BRANCH##*-}
BATCH_PREFIX=$(echo "$MY_BRANCH" | sed 's/-[^-]*$//')

git fetch origin --prune
PEERS=($(git branch -r | grep "origin/${BATCH_PREFIX}-" | sed 's|.*origin/||;s|.*-||' | sort -u))
N=${#PEERS[@]}
MY_POS=0
for i in "${!PEERS[@]}"; do [[ "${PEERS[$i]}" == "$MY_ID" ]] && MY_POS=$i && break; done

# Your stripe: pages MY_POS+1, MY_POS+1+N, MY_POS+1+2N, ...
echo "Worker $MY_POS of $N. Stripe:"
for ((p=MY_POS+1; p<=TOTAL_PAGES; p+=N)); do echo "  Page $p"; done
```

**Why interleaved**: If worker 5 of 16 dies, orphaned pages are spread evenly (`{6,22,38,54,70,86}`) rather than clustered. Surviving workers fill gaps with better coverage.

**During Phase 1**: No sync needed. Just translate your stripe pages sequentially, validate, push after each.

### Phase 2 — SCAVENGE (Lightweight Coordination)

After completing your stripe, scan all peer branches for gaps and fill them:

```bash
python3 tools/coord.py --fetch next --worker "$MY_ID" --total-pages $TOTAL_PAGES
```

Before each scavenge claim, the tool:
1. Fetches all peer branches (scoped to batch prefix)
2. Scans for completed translation files (the source of truth)
3. Checks active claims from peer WORKER_STATE.json files
4. Returns the lowest uncompleted, unclaimed page — or `HOLD` if you're too far ahead

---

## Hard Rules

1. **Run `tools/coord.py` before every scavenge claim.** Stripe claims need no tool.
2. **One page at a time.** Finish, push, then claim next.
3. **Push immediately after completing each page.** Your commit is how others see it.
4. **Validate before pushing.** `python3 tools/validate_translation.py <file>`
5. **Use batch-scoped discovery only.** Never scan branches outside your batch prefix.
6. **Never stop voluntarily.** Keep translating until all pages are done or context is exhausted.

---

## Balance Gate (Prevents Monopoly, Triggers Review)

When >= 4 workers are online, if your completed count exceeds the slowest online worker by more than 2:

- The `coord.py next` command returns `HOLD` instead of a page number
- During HOLD, you **must review** another worker's recent page (see Review Protocol below)
- After submitting one review, the balance gate rechecks automatically

This ties quality review directly to work distribution — faster workers produce reviews, maintaining both balance and quality.

---

## Review Protocol (Lightweight, Triggered by Balance Gate)

When HOLD is active:

1. Run `python3 tools/coord.py --fetch review-queue --worker "$MY_ID"`
2. Pick a page from the queue (buddy system: review the worker whose sorted position precedes yours)
3. Spot-check:
   - All 4 languages present and non-empty for every sentence
   - Terminology matches `research/glossary.md`
   - No skipped content
   - Valid JSON structure
4. Commit a brief review note to `reviews/page_XXX.<your_id>.md`
5. Push and return to the work loop

Reviews are 2-5 minutes, not full editorial passes. The goal is catch obvious omissions and term inconsistencies.

---

## State Management

### Worker State: `WORKER_STATE.json` (one per worker)

```json
{
  "worker_id": "c68e",
  "branch": "cursor/exp-005-translate-c68e",
  "batch_prefix": "cursor/exp-005-translate",
  "heartbeat": 1767254400,
  "status": "translating",
  "claimed_page": 42,
  "claimed_at": 1767254300,
  "completed_pages": [3, 19, 35],
  "phase": "stripe"
}
```

JSON, not Markdown — machine-parseable without regex.

### Completion Detection: Output Files (Source of Truth)

A page is done if `translations/page_XXX.json` exists on **any** peer branch. Output files don't lie. State files can be stale.

### Timeouts

| Event | Threshold |
|-------|-----------|
| Worker offline | Heartbeat > 10 min stale |
| Claim reclaimable | Heartbeat > 15 min stale |
| Sync frequency (Phase 2) | Before each claim |
| Push after completion | Immediate |

---

## Agent Lifecycle

```
STARTUP (< 90 seconds)
├── 1. Compute identity (MY_ID from branch name)
├── 2. git fetch (discover peers, scoped to batch prefix)
├── 3. Compute stripe pages (deterministic, zero coordination)
├── 4. Initialize WORKER_STATE.json, commit + push
│
PHASE 1: STRIPE (bulk of session)
│   ┌─── For each stripe page: ─────────────────┐
│   │  1. Read extracted/pages/page_XXX.txt      │
│   │  2. Translate → translations/page_XXX.json │
│   │  3. Validate: tools/validate_translation.py│
│   │  4. Update WORKER_STATE.json               │
│   │  5. git add + commit + push                │
│   └─── Next stripe page ──────────────────────┘
│
PHASE 2: SCAVENGE (after stripe done)
│   ┌─── Until all pages done: ─────────────────┐
│   │  1. tools/coord.py next (fetch + scan)     │
│   │  2. If HOLD → review a peer's page, push   │
│   │  3. If page N → translate, validate, push  │
│   │  4. If NONE → all done, exit               │
│   └─── Repeat ────────────────────────────────┘
│
SHUTDOWN
├── Update WORKER_STATE.json (status: done)
├── Commit + push final state
└── Done
```

---

## Commit Messages

```
[SHORT_ID] DONE: page NNN
HEARTBEAT: <unix_timestamp>
```

Actions: `START`, `DONE`, `REVIEW`, `END`. Keep it minimal. No verbose metadata.

---

## Handling Edge Cases

| Situation | Resolution |
|-----------|------------|
| Can't discover peers at startup | Assume N=1, take all pages as stripe |
| Stripe page already done by someone else | Skip it, move to next stripe page |
| Git push fails | Retry 3x with 5s gaps. Keep translating locally if still failing. |
| Git fetch fails | Work offline on stripe pages (they're deterministic). Try fetch before Phase 2. |
| Running low on context | Push everything immediately. Update state to `done`. |
| Duplicate translation discovered | Acceptable (<5%). Final assembly picks first-encountered. |
| All pages claimed but book not done | Check for stale claims (>15 min offline). Reclaim or wait. |

---

## Anti-Patterns (Proven Failures from 32 Agent Sessions)

| Don't | Why |
|-------|-----|
| Run setup/install before translating | Wastes 10-20 min; setup is pre-done on `main` |
| Wait for consensus or votes | Deadlocks when agents die; top performers ignored consensus |
| Start at page 1 | Everyone else does too; use your stripe |
| Create research/analysis docs | You're here to translate, not write reports |
| Build custom helper tools | Use what's provided; tool-building is a meta-work trap |
| Track other agents' heartbeats in your state file | Scan output files instead; they're the truth |
| Batch multiple pages before pushing | Others can't see your work; increases duplication risk |
| Skip validation before pushing | Invalid JSON wastes the page and requires re-translation |
| Claim multiple pages simultaneously | Finish one, push, then claim next |

---

## Final Assembly (Post-Run)

Any agent (or a post-run process) can collect all results:

```bash
git fetch origin --prune
mkdir -p assembled/translations

for branch in $(git branch -r | grep "origin/${BATCH_PREFIX}-" | tr -d ' '); do
  for file in $(git ls-tree --name-only -r "$branch" -- translations/ 2>/dev/null); do
    name=$(basename "$file")
    [ ! -f "assembled/translations/$name" ] && \
      git show "${branch}:${file}" > "assembled/translations/$name" 2>/dev/null
  done
done

echo "Collected $(ls assembled/translations/ | wc -l) / $TOTAL_PAGES pages"
```

For pages with multiple versions (from duplication), prefer the version from the worker with more total completions.

---

## Performance Model

```
Expected speedup ≈ N × (1 - N/(2T)) × (1 - overhead)

  N = active agents, T = total work units
  overhead ≈ 0.03 (Phase 1) to 0.08 (Phase 2)
```

| Agents | Pages | Phase 1 Duplication | Phase 2 Duplication | Total Waste | Effective Speedup |
|--------|-------|---------------------|---------------------|-------------|-------------------|
| 4 | 99 | 0% | <1% | <1% | ~3.9x |
| 8 | 99 | 0% | <2% | <2% | ~7.6x |
| 16 | 99 | 0% | <3% | <3% | ~14.7x |

Compare prior experiments: 16 agents achieved ~1.5x (Exp 1) and ~3x (Exp 2) speedup.

---

## Adapting This Protocol

Replace these variables for any embarrassingly parallel task:

| Variable | Translation Project | Your Project |
|----------|-------------------|--------------|
| `TOTAL_PAGES` | 99 | Your unit count |
| `BATCH_PREFIX` | `cursor/exp-NNN-translate` | Your branch naming pattern |
| Output directory | `translations/` | Your output path |
| Output filename | `page_XXX.json` | Your file pattern |
| Validation tool | `validate_translation.py` | Your validator |
| Input source | `extracted/pages/page_XXX.txt` | Your source data path |

---

## Protocol Summary (Pocket Reference)

```
1. Compute stripe from sorted peer position → translate stripe pages → push each
2. After stripe: coord.py next → if HOLD, review a peer's page → push
3. If page number → translate, validate, push → repeat
4. If NONE → all done
5. Never wait. Never stop. Push after every page. Validate before pushing.
```
