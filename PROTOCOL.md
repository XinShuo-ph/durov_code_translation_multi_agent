# Multi-Agent Parallel Work Protocol

Agents spread across work units deterministically using their branch name, work forward, push after each unit, and skip what others completed. Near-linear speedup, near-zero coordination.

**No claiming. No voting. No phases. No state files. Just output.**

---

## TL;DR

```
1. start = hash(branch_suffix) % total_units + 1
2. Initial sync: fetch branches, note which units are already done
3. Work forward from start, skip done units (wrap around after max)
4. Push after every unit completed
5. Re-sync every ~5 units: fetch, update done set, skip newly-done units
6. Stop when all units are done or you cannot continue
```

---

## Why This Design

Two previous 16-agent experiments on this codebase produced hard data on what fails:

| Failure Pattern | Cause | Measured Impact |
|----------------|-------|-----------------|
| **Thundering herd** | All agents claim "lowest available" simultaneously | Pages 2-3 each translated by **11 of 16 agents**. 77% total waste. |
| **Startup death** | Complex multi-phase protocols (research → voting → work) | **31%** of agents made 1 commit and stopped forever. |
| **Solo completion** | Consensus bottleneck + early dropout | **1 of 16** agents did most of the work alone. |
| **Meta-work trap** | Agents build "helper tools" instead of producing output | Entire sessions spent on scripts, zero pages translated. |

This protocol eliminates all four by replacing coordination with determinism. See `ANALYSIS.md` for full data.

---

## The Algorithm

### Step 0: Configuration

These values must be defined in the project's task instructions (not in this protocol):

```
TOTAL_UNITS    = <number>         # e.g. 99 pages, 120 chapters
OUTPUT_DIR     = <path>           # e.g. translations/
UNIT_FILENAME  = <pattern>        # e.g. page_%03d.json (printf-style)
BRANCH_FILTER  = <prefix>         # e.g. book-translation-multi-agent
```

### Step 1: Compute Your Start Position

```bash
MY_BRANCH=$(git branch --show-current)
SUFFIX=$(echo "$MY_BRANCH" | grep -oE '[^-]+$')
START=$(python3 -c "print(int('$SUFFIX', 16) % $TOTAL_UNITS + 1)")
```

Each agent gets a different-ish start position derived from its branch name. With 16 agents and 99 units, expected collisions: ~1.3 (acceptable).

### Step 2: Initial Sync

Before starting, fetch once to see what's already done:

```bash
git fetch origin --prune

PREFIX=$(echo "$MY_BRANCH" | sed 's/-[^-]*$//')

DONE_UNITS=""
for branch in $(git branch -r | grep "origin/cursor/$PREFIX" | tr -d ' '); do
    DONE_UNITS="$DONE_UNITS $(git ls-tree -r --name-only "$branch" -- "$OUTPUT_DIR/" 2>/dev/null)"
done
# Parse unit numbers from filenames, store as a set
```

### Step 3: Work Loop

```
current = START

loop forever:
    if current is not in done_set:
        produce output for unit current
        save to OUTPUT_DIR/unit_NNN.ext
        git add . && git commit && git push

    current = (current % TOTAL_UNITS) + 1

    every 5 completed units (or 10 minutes):
        re-run sync (Step 2) to refresh done_set

    if done_set covers all units:
        break    # project complete

    if current == START and no progress since last wrap:
        break    # nothing left to do
```

### Step 4: Assembly (optional, run once at end)

Collect all output from all branches into one place:

```bash
git fetch origin --prune
mkdir -p assembled/
for branch in $(git branch -r | grep "origin/cursor/$PREFIX" | tr -d ' '); do
    for file in $(git ls-tree -r --name-only "$branch" -- "$OUTPUT_DIR/" 2>/dev/null); do
        name=$(basename "$file")
        if [ ! -f "assembled/$name" ]; then
            git show "${branch}:${file}" > "assembled/$name"
        fi
    done
done
echo "Assembled $(ls assembled/ | wc -l) units"
```

---

## Rules

1. **Your first commit must be a completed work unit.** Not a state file. Not a research document. Output.
2. **Your start position comes from your branch name.** Don't override it, don't pick page 1.
3. **Work forward, wrapping around.** Unit after TOTAL is unit 1.
4. **Push after every completed unit.** Don't batch. Other agents need to see your work.
5. **Sync every ~5 units or ~10 minutes.** Skip units others completed.
6. **Never stop voluntarily.** Keep producing until everything is done or you cannot continue.
7. **No meta-work.** Don't build scripts, templates, helpers, or documentation.
8. **One output file per unit.** Predictable path. Consistent format.
9. **Tolerate rare duplication.** Two agents doing the same unit occasionally is fine.
10. **If stuck on a unit for >5 minutes, skip it.** Come back on your next wrap-around.

---

## Commit Messages

Minimal. No heartbeats, no state machine codes, no verbose metadata.

```
[SUFFIX] DONE unit NNN: brief description
```

Examples:

```
[c68e] DONE unit 044: Chapter 4, VK office confrontation
[14ce] DONE unit 080: Chapter 6, philosophy and ethics
[c3ab] DONE unit 012: Prologue ending
```

---

## What NOT to Do

| Don't | Why |
|-------|-----|
| Claim pages via a state file | Race conditions. All agents claim the same page. |
| Wait for consensus or voting | Serialization bottleneck. One agent ends up solo. |
| Build "helper tools" before working | Meta-work trap. Zero output produced. |
| Run research/setup phases | All N agents do identical work. N times the waste. |
| Sync before every single unit | Sync overhead dominates. Work-to-sync ratio collapses. |
| Stop after a few units "to check in" | Keep going. Context remaining = output remaining. |
| Create WORKER_STATE.md or status files | Nobody reads them. Output files are the only state that matters. |
| Start at page 1 | Everyone else does too. Use your hash-assigned start. |
| Batch multiple units before pushing | Others can't see your work. Increases duplication. |

---

## Performance Model

```
Effective speedup ≈ N × (1 - N/(2T)) × (1 - sync_overhead)

  N = number of agents
  T = total work units
  sync_overhead ≈ 0.05 (5% of time on sync)
```

| Agents | Units | Expected Duplicates | Waste  | Effective Speedup |
|--------|-------|---------------------|--------|-------------------|
| 4      | 99    | ~0.08               | <1%    | ~3.8x             |
| 8      | 99    | ~0.32               | <1%    | ~7.5x             |
| 16     | 99    | ~1.3                | ~2%    | ~14.9x            |
| 16     | 400   | ~0.32               | <1%    | ~15.2x            |

Compare previous experiments on this codebase:
- book-translation-multi-agent: 16 agents achieved ~**1.5x** speedup
- collaborative-translation-initiation: 16 agents achieved ~**3x** speedup (77% waste)

---

## Adapting to Your Workload

This protocol works for any embarrassingly parallel task:

| Workload | Units | Output |
|----------|-------|--------|
| Book translation | Pages or chapters | `translations/page_NNN.json` |
| Code generation | Modules or files | `generated/module_NNN.py` |
| Data processing | Shards | `processed/shard_NNN.parquet` |
| Test execution | Test suites | `results/suite_NNN.xml` |
| Document review | Sections | `reviewed/section_NNN.md` |

**Requirements:**
- Work can be divided into numbered, independent units
- Output is one file per unit with a predictable name
- Git is available for communication

**For workloads with dependencies** (unit 5 needs unit 3's output):

```
if dependencies_of(current) are not all in done_set:
    skip current, advance to next
```

---

## Quick Reference

### Agent Startup Script

```bash
#!/usr/bin/env bash
set -e

# --- CONFIGURE THESE ---
TOTAL_UNITS=99
OUTPUT_DIR="translations"
BRANCH_FILTER="your-task-prefix"
# -----------------------

MY_BRANCH=$(git branch --show-current)
SUFFIX=$(echo "$MY_BRANCH" | grep -oE '[^-]+$')
PREFIX=$(echo "$MY_BRANCH" | sed 's/-[^-]*$//')
START=$(python3 -c "print(int('$SUFFIX', 16) % $TOTAL_UNITS + 1)")

echo "=== Agent $SUFFIX ==="
echo "Start unit: $START"
echo "Total units: $TOTAL_UNITS"
echo "Output dir: $OUTPUT_DIR"
echo "Branch prefix: $PREFIX"
echo ""

# Initial sync
git fetch origin --prune
echo "Discovered branches:"
git branch -r | grep "origin/cursor/$PREFIX" | wc -l

# List done units
for branch in $(git branch -r | grep "origin/cursor/$PREFIX" | tr -d ' '); do
    git ls-tree -r --name-only "$branch" -- "$OUTPUT_DIR/" 2>/dev/null
done | sort -u
```

### Progress Check (run from any branch)

```bash
git fetch origin --prune

PREFIX="your-task-prefix"
TOTAL=99

done=0
for branch in $(git branch -r | grep "origin/cursor/$PREFIX" | tr -d ' '); do
    done=$((done + $(git ls-tree -r --name-only "$branch" -- translations/ 2>/dev/null | wc -l)))
done

# Note: this over-counts if pages are duplicated
echo "Total translations across all branches: $done"
echo "Target: $TOTAL"
```
