# Multi-Agent Parallel Work Protocol

> **Version**: 2.0 — Redesigned after analyzing 32 agent sessions across 2 experiments.
> Previous protocol produced **76% wasted effort** (duplicate work) and left **56% of agents idle**.
> This protocol eliminates those failures.

---

## Post-Mortem: Why Previous Sessions Failed

| Failure | Data | Root Cause |
|---------|------|------------|
| 76% duplicate work | Pages 2-3 translated 11x each | All agents race for page 1, no deconfliction |
| 56% of agents idle | 9/16 agents produced zero output | Multi-phase setup (M0→M1→M2) consumed entire sessions |
| One agent does everything | 1 agent translated all 99 pages alone | Other agents dead before reaching translation phase |
| Consensus deadlock | 4/16 agents stuck voting on format | Voting requires simultaneous presence; agents arrive/leave asynchronously |
| Stale branch confusion | Agents discovered old experiment branches | No scoping of peer discovery |

---

## Five Rules (Non-Negotiable)

1. **Translate from minute zero.** No research phase. No format exploration. No voting. All setup is pre-done.
2. **Use your stripe.** Your starting pages are deterministic — computed from your ID. No coordination needed.
3. **Push after every page.** Your commit is how others know the page is done.
4. **Sync between pages, not during.** One fetch per page cycle. Don't interrupt translation to sync.
5. **Never stop voluntarily.** Translate until all work is done, or you run out of context/session.

---

## How It Works: Two Phases

### Phase 1 — STRIPE (first ~6 pages per agent)

Each agent gets a **deterministic, non-overlapping set of pages** based on its ID. No coordination needed.

```
Agent 0:  pages  1, 17, 33, 49, 65, 81, 97
Agent 1:  pages  2, 18, 34, 50, 66, 82, 98
Agent 2:  pages  3, 19, 35, 51, 67, 83, 99
...
Agent 15: pages 16, 32, 48, 64, 80, 96
```

**How to compute your stripe:**

```bash
# 1. Get your short ID (last 4 hex chars of branch name)
MY_ID=$(git branch --show-current | grep -oE '[0-9a-f]{4}$')

# 2. Discover your peers (one-time, <30 seconds)
git fetch origin --prune
MY_PREFIX=$(git branch --show-current | sed 's/-[^-]*$//')
PEERS=($(git branch -r | grep "origin/cursor/${MY_PREFIX}-" | sed 's|.*-||' | sort))

# 3. Find your position in the sorted peer list
NUM_WORKERS=${#PEERS[@]}
MY_POS=0
for i in "${!PEERS[@]}"; do
  if [[ "${PEERS[$i]}" == "$MY_ID" ]]; then MY_POS=$i; break; fi
done

# 4. Your stripe: pages MY_POS+1, MY_POS+1+N, MY_POS+1+2N, ...
echo "I am position $MY_POS of $NUM_WORKERS workers"
echo "My stripe pages:"
for ((p=MY_POS+1; p<=TOTAL_PAGES; p+=NUM_WORKERS)); do echo "  Page $p"; done
```

**Why this works:** With 16 agents and 99 pages, each agent gets ~6 pages. All agents work in parallel on different pages. Zero race conditions. Zero wasted work.

### Phase 2 — SCAVENGE (after stripe is done)

Once you finish your stripe pages, **scan all peer branches** for gaps:

```bash
# Find pages that have NO translation file on ANY peer branch
git fetch origin --prune
for branch in $(git branch -r | grep "origin/cursor/${MY_PREFIX}-"); do
  git ls-tree --name-only "${branch}" -- translations/ 2>/dev/null
done | sort -u > /tmp/all_done.txt

# Find gaps
for p in $(seq 1 $TOTAL_PAGES); do
  FILE=$(printf "translations/page_%03d.json" $p)
  if ! grep -q "$FILE" /tmp/all_done.txt; then
    echo "UNCLAIMED: page $p"
  fi
done
```

Claim the **lowest unclaimed page** and translate it. Push. Repeat.

In scavenge phase, **sync before each claim** to avoid duplicates.

---

## Complete Agent Lifecycle

```
STARTUP (< 2 minutes)
│
├── 1. Compute identity (MY_ID, MY_POS)
├── 2. git fetch (discover peers)
├── 3. Compute stripe pages
├── 4. Create WORKER_STATE.md (from template)
├── 5. Push registration commit
│
▼
STRIPE PHASE (bulk of your session)
│
│   ┌─── For each page in my stripe: ───┐
│   │                                    │
│   │  1. Read source text               │
│   │  2. Translate (the actual work)    │
│   │  3. Save output file               │
│   │  4. git add + commit + push        │
│   │  5. (optional) quick git fetch     │
│   │                                    │
│   └──── Next stripe page ─────────────┘
│
▼
SCAVENGE PHASE (after stripe is complete)
│
│   ┌─── Loop until all pages done: ────┐
│   │                                    │
│   │  1. git fetch (full sync)          │
│   │  2. Scan all branches for gaps     │
│   │  3. Claim lowest unclaimed page    │
│   │  4. Translate + save + push        │
│   │                                    │
│   └──── Repeat ───────────────────────┘
│
▼
SESSION END
│
├── Push final state
└── Update WORKER_STATE.md
```

---

## Commit Convention

Every commit message follows this format:

```
[XXXX] ACTION: page NNN - brief description
```

Where `XXXX` is your 4-char ID, ACTION is one of:

| Action | When |
|--------|------|
| `START` | First commit (registration) |
| `DONE` | Completed a page translation |
| `SCAN` | Synced and found gaps |
| `END` | Session ending |

Examples:
```bash
git commit -m "[c68e] START: registered, stripe pages 3,19,35,51,67,83,99"
git commit -m "[c68e] DONE: page 003 - prologue, VK office scene"
git commit -m "[c68e] DONE: page 019 - chapter 1, Durov childhood"
git commit -m "[c68e] SCAN: switching to scavenge, 12 pages remaining"
git commit -m "[c68e] DONE: page 045 - scavenged, chapter 3"
git commit -m "[c68e] END: translated 9 pages total (3,19,35,51,67,83,99,45,52)"
```

---

## WORKER_STATE.md (Minimal)

Keep it short. The file's only purpose is to show you're alive and what you've done.

```markdown
# Worker: XXXX
- Branch: cursor/project-name-XXXX
- Status: translating | scavenging | done
- Stripe: [3, 19, 35, 51, 67, 83, 99]
- Completed: [3, 19, 35]
- Current: 51
- Last push: [unix timestamp]
```

Do NOT maintain "Known Workers" tables. Do NOT track other agents' heartbeats. That complexity is what killed the previous protocol. If you need to know what others have done, **scan their branches for output files** — that's the source of truth.

---

## Handling Edge Cases

### "I can't compute my stripe (peer discovery failed)"
Fall back to scavenge-only mode: scan all branches, claim lowest unclaimed page, translate, push, repeat. This is less efficient but still works.

### "My stripe page is already done (someone else did it)"
Skip it. Move to your next stripe page. This happens when a faster agent scavenged your page — it's fine, no work is lost.

### "Git push fails"
Retry 3 times with 5-second gaps. If still failing, **keep translating locally**. Push a batch later. Never block translation on push failures.

### "Git fetch fails"  
Work offline on your stripe pages. They're deterministic — you don't need fetch to know them. Try fetching again before scavenge phase.

### "I'm running low on context/session time"
Push everything immediately. Update WORKER_STATE.md with your final status. Don't start a new page you can't finish.

### "Another agent and I both translated the same page"
This is acceptable. Duplicates are merged during aggregation (keep the higher-quality version). The protocol minimizes this but doesn't guarantee zero overlap. A small amount of redundancy (< 5%) is fine.

---

## Aggregation (Post-Run)

After all agents finish, collect results from all branches:

```bash
mkdir -p aggregated/
git fetch origin --prune

for branch in $(git branch -r | grep "origin/cursor/${PREFIX}-"); do
  for file in $(git ls-tree --name-only "${branch}" -- translations/ 2>/dev/null); do
    page=$(echo "$file" | grep -oP '\d+')
    if [ ! -f "aggregated/$file" ]; then
      git show "${branch}:${file}" > "aggregated/$file" 2>/dev/null
      echo "Collected page $page from ${branch}"
    fi
  done
done

echo "Total unique pages collected: $(ls aggregated/translations/ | wc -l)"
```

---

## Why This Protocol Works

| Problem | Old Protocol | This Protocol |
|---------|-------------|---------------|
| Thundering herd on page 1 | All agents race for lowest page | Stripe assignment — each agent starts on different page |
| Setup phase kills agents | M0 (research) → M1 (format) → M2 (translate) | No phases. Translate immediately. |
| Consensus deadlock | Agents vote and wait for agreement | No voting. All decisions pre-made. |
| 76% duplicate work | Manual sync + lowest-available claiming | Deterministic stripes + file-existence scanning |
| Protocol too long to absorb | 378 lines, complex state machines | ~200 lines, two phases, simple loop |
| Agents track each other's heartbeats | Complex WORKER_STATE.md tables | Don't track others. Scan output files instead. |

### Expected Performance

With 16 agents on 99 pages:
- **Stripe phase**: Each agent gets ~6 pages. Zero coordination overhead. All 16 work in parallel.
- **Scavenge phase**: ~3 pages remain unclaimed (from dead agents). Active agents fill gaps.
- **Expected waste**: < 5% (vs 76% previously)
- **Expected coverage**: 100% of pages translated (vs dependent on single agent previously)
- **Time to completion**: ~6 pages per agent at ~15 min/page = ~90 min for full book (vs one agent doing 99 pages in ~500 min)

---

## Quick Reference

```
┌────────────────────────────────────────────────┐
│          AGENT DECISION FLOWCHART              │
│                                                │
│  Am I just starting?                           │
│  └─ YES → Compute stripe → Start translating   │
│                                                │
│  Do I have stripe pages left?                  │
│  └─ YES → Translate next stripe page → Push    │
│                                                │
│  Is my stripe done?                            │
│  └─ YES → Fetch → Scan for gaps → Scavenge    │
│                                                │
│  Are all pages done?                           │
│  └─ YES → Push final state → END              │
│                                                │
│  Am I running out of context?                  │
│  └─ YES → Push everything → END               │
│                                                │
│  Did something fail?                           │
│  └─ Keep translating. Push later.              │
└────────────────────────────────────────────────┘
```
