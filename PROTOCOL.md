# Multi-Agent Parallel Work Protocol v3

## Failure Analysis: Why Previous Protocols Failed

Two experiments with 16 agents each produced nearly identical failures:

| Metric | Experiment 1 | Experiment 2 |
|--------|-------------|-------------|
| Agents that translated >5 pages | 3/16 | 4/16 |
| Pages translated by top 1 agent | 29/99 | 99/99 |
| Page 2 translated by N agents | ~3 | 11 |
| Time wasted on setup per agent | 10+ min | 5+ min |
| Agents dead within 10 min | 8/16 | 6/16 |

**Root causes identified:**

1. **Redundant setup**: Every agent independently extracted text, wrote research docs, explored tools. This consumed 10+ minutes and significant context per agent before any real work began.
2. **Phase gates**: M0→M1→M2 phases meant agents couldn't translate until they finished setup. Many died during setup.
3. **Consensus deadlocks**: Agents waited for "50% vote" on format approach. With agents dying, quorum was never reached.
4. **No work spreading**: "Claim lowest available page" + no shared filesystem = every agent starts at page 1. Pages 1-5 got translated 6-11 times.
5. **Unreliable sync**: Reading all other branches via `git show` is slow, complex, and error-prone. Most agents never successfully synced.
6. **Protocol too long**: 377 lines of protocol + 468 lines of instructions = agents burning context on coordination instead of work.

---

## Design Principles

1. **Zero setup**: All prep work is pre-done and committed to `main`. Workers start producing output immediately.
2. **Deterministic assignment**: Workers compute their page range from their sorted position. No claiming, no races, no conflicts.
3. **One sync, then independence**: Workers discover peers once at startup, then work autonomously.
4. **No consensus, no voting, no phases**: One format, pre-decided. No gates.
5. **Concise**: This entire protocol fits in ~150 lines. Agents should spend context on work, not coordination.

---

## Protocol

### Step 0: Prerequisites (done BEFORE agents launch)

The repository `main` branch must contain all pre-processed inputs before agents start. Agents must NEVER regenerate these. The task instructions file (e.g., `instructions.md`) must tell agents explicitly: "All resources are pre-provided. Do NOT regenerate them."

### Step 1: Discover Peers (max 60 seconds)

```bash
MY_BRANCH=$(git branch --show-current)
MY_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$')

git fetch origin --prune 2>/dev/null

# Find all sibling worker branches (same task prefix)
TASK_PREFIX=$(echo "$MY_BRANCH" | sed 's/-[^-]*$//')
WORKERS=($(git branch -r | grep "origin/${TASK_PREFIX}-" | sed 's|.*origin/||' | sort))
TOTAL=${#WORKERS[@]}

# Find my 0-based index in sorted worker list
MY_INDEX=0
for i in "${!WORKERS[@]}"; do
  if [[ "${WORKERS[$i]}" == "$MY_BRANCH" ]]; then
    MY_INDEX=$i
    break
  fi
done
```

### Step 2: Compute Assignment

Pages are interleaved across workers to maximize spread:

```
TOTAL_PAGES=<from task config>

Worker 0 gets pages: 1, 1+N, 1+2N, ...
Worker 1 gets pages: 2, 2+N, 2+2N, ...
Worker k gets pages: k+1, k+1+N, k+1+2N, ...

Where N = number of workers
```

```bash
MY_PAGES=()
PAGE=$((MY_INDEX + 1))
while [ $PAGE -le $TOTAL_PAGES ]; do
  MY_PAGES+=($PAGE)
  PAGE=$((PAGE + TOTAL))
done
echo "I am worker $MY_INDEX of $TOTAL. My pages: ${MY_PAGES[*]}"
```

**Why interleaved, not contiguous blocks?** If worker 3 dies after 5 minutes, only pages `{4, 20, 36, 52, 68, 84}` are orphaned (spread across the book) rather than pages `{19-24}` (a contiguous hole). Surviving workers filling gaps produce more even coverage.

### Step 3: Work

For each page in your assignment:

1. Read the source input
2. Produce the output
3. Save to the designated output path
4. `git add . && git commit -m "[ID] Done page X" && git push origin HEAD`

**Rules:**
- Translate/process pages **in your assigned order**. Do not skip ahead.
- Commit and push after **every completed page** (or every 2-3 pages for fast tasks).
- Do **not** sync with other workers during this phase.
- Do **not** create worker state files, heartbeat files, or status updates.
- If a push fails, retry up to 3 times. If it still fails, continue working and batch-push later.

### Step 4: Fill Gaps (after primary assignment is done)

After completing all your assigned pages:

```bash
git fetch origin --prune 2>/dev/null

# Check which pages exist across ALL sibling branches
DONE_PAGES=()
for branch in "${WORKERS[@]}"; do
  for f in $(git ls-tree --name-only -r "origin/$branch" -- <output_dir>/ 2>/dev/null); do
    PAGE_NUM=$(echo "$f" | grep -oP '[0-9]+')
    DONE_PAGES+=($PAGE_NUM)
  done
done

# Find missing pages
MISSING=()
for p in $(seq 1 $TOTAL_PAGES); do
  if ! echo "${DONE_PAGES[@]}" | grep -qw "$p"; then
    MISSING+=($p)
  fi
done

echo "Missing pages: ${MISSING[*]}"
# Translate missing pages, commit, push
```

---

## Handling Edge Cases

### Fewer workers than expected
Works fine. Each worker gets more pages. Even 1 worker gets all pages.

### Worker dies mid-task
Its completed pages are preserved on its branch. Orphaned pages are picked up in Step 4 by surviving workers.

### Worker can't discover peers (fetch fails)
Fall back to `TOTAL=1, MY_INDEX=0`. The worker takes all pages. Other workers will naturally avoid duplication through their own assignments.

### Two workers compute different peer counts (staggered start)
Possible if workers start at very different times. Interleaving minimizes overlap: even with off-by-one peer counts, at most 1-2 pages may overlap per worker pair, not dozens.

### Git push conflicts
Should not happen—each branch is single-writer. If it does, `git pull --rebase origin HEAD && git push origin HEAD`.

---

## What This Protocol Does NOT Include (by design)

| Removed Feature | Why |
|----------------|-----|
| WORKER_STATE.md | Agents wasted 20%+ of context maintaining state files nobody read |
| Heartbeat system | Required constant commits for no benefit; dying agents can't send heartbeats anyway |
| Consensus/voting | Blocked all agents; top workers succeeded by ignoring it |
| Phase gates (M0/M1/M2) | Prevented early translation; most agents died during setup phases |
| Sync loop every 2-3 min | Complex bash loops that failed silently; agents that synced less were more productive |
| Conflict resolution protocol | Deterministic assignment eliminates conflicts; Step 4 handles residual gaps |
| Page claiming broadcasts | The entire concept of "claiming" is replaced by deterministic assignment |
| Known Workers table | Agents synced once at startup; stale tables caused more confusion than clarity |

---

## Adapting This Protocol

To use this protocol for a new task:

1. **Prepare inputs on `main`**: Ensure all source material, tools, and configs exist before launching agents.
2. **Set `TOTAL_PAGES`**: Replace with your total work unit count.
3. **Set `TASK_PREFIX`**: The common branch name prefix that identifies sibling workers.
4. **Set `<output_dir>`**: The directory where completed work goes.
5. **Write concise task instructions**: Tell agents WHAT to produce, not HOW to coordinate. Keep under 200 lines. Reference this protocol for coordination.

### Task Instructions Template

```markdown
# Task: [description]

## You are one of N parallel agents. Follow PROTOCOL.md for coordination.

## Your Job
[One paragraph: what to do with each work unit]

## Input
[Where to find source material — already on main, do NOT regenerate]

## Output Format
[Exact format specification]

## Quality Rules
[5-10 bullet points max]

## Reference Material
[List of pre-provided resources — do NOT recreate these]
```

---

## Summary

```
START ──► Discover peers (1 min) ──► Compute pages ──► Translate assigned pages ──► Fill gaps ──► DONE
              │                           │                     │                        │
              │  git fetch, sort,         │  Interleaved       │  Independent,          │  Fetch all
              │  find my index            │  assignment         │  no sync needed        │  branches,
              │                           │                     │                        │  find holes
              ▼                           ▼                     ▼                        ▼
          60 sec max                  10 sec               90% of session           remaining time
```

The protocol is: **discover, divide, work, fill**. Everything else is a distraction.
