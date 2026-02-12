# Multi-Agent Parallel Work Protocol v3

## Purpose

This protocol enables N agents (each on its own git branch) to divide a set of work units (e.g., pages, files, tasks) and complete them **in parallel with minimal duplication and zero blocking**.

It is designed to be **generic** (not tied to translation), **concise** (an agent can absorb it in under 2 minutes), and **battle-tested** against real failure modes observed across 32+ agent runs.

---

## Lessons From Prior Runs

| Failure mode | Observed frequency | Root cause |
|---|---|---|
| Agents stuck in setup phases (M0/M1/M2) | 13 of 16 agents | Phased pipeline + consensus gates |
| All agents claim work unit 1 | 11 of 16 agents translated page 2 | No starting-offset strategy |
| Agents die after 1 commit | 4-6 of 16 agents | No continuous-execution enforcement |
| Agents discover wrong-experiment branches | Most agents | No experiment-ID filtering |
| Agents wait for consensus votes | 8 of 16 agents | Voting/quorum requirements |
| One agent does all the work | 1 agent translated 99/99 pages | Others dead from above failures |
| 83% wasted effort from duplication | Measured across round 2 | Poor sync + same starting page |

**The single biggest cause of failure: agents spending their limited context on non-productive work (setup, research, format exploration, consensus) instead of the actual task.**

---

## Core Rules (memorize these)

```
1. START PRODUCING IMMEDIATELY. No setup, no research, no exploration.
2. YOUR STARTING UNIT = (hash(branch_id) mod N_units) + 1. NOT unit 1.
3. SYNC BEFORE EACH NEW UNIT. Check what others have done. Takes 30 seconds.
4. NEVER WAIT for another agent. No votes. No consensus. No phases.
5. PUSH AFTER EVERY COMPLETED UNIT. Make your work visible.
6. DO NOT STOP until you run out of units or hit a hard context limit.
```

---

## Agent Lifecycle

```
STARTUP (< 60 seconds)
  │
  ├─ 1. Read PROTOCOL.md (this file) and TASK.md
  ├─ 2. Identify yourself: MY_ID = last 4 chars of branch name
  ├─ 3. Compute your starting unit (see "Work Distribution")
  ├─ 4. Create AGENT_STATE.md, commit + push
  │
  ▼
WORK LOOP (repeat until done)
  │
  ├─ 1. SYNC: git fetch, scan for completed units across all branches
  ├─ 2. PICK: Choose the lowest UNCLAIMED and UNCOMPLETED unit
  ├─ 3. CLAIM: Write unit ID to AGENT_STATE.md, commit + push
  ├─ 4. EXECUTE: Do the actual work. Produce the output file.
  ├─ 5. COMPLETE: Commit output + updated AGENT_STATE.md, push
  ├─ 6. GOTO 1
  │
  ▼
SHUTDOWN (when no units remain or context limit approaching)
  │
  ├─ 1. Update AGENT_STATE.md with final status
  ├─ 2. Commit + push
  └─ 3. Done
```

**Time budget per unit**: All overhead (sync + claim + push) should be < 10% of the unit's execution time. If a unit takes 3 minutes to execute, spend < 20 seconds on coordination.

---

## Work Distribution

### The Starting-Offset Problem

If all agents start from unit 1, they all race for the same units and produce massive duplication. Prior experiments showed 11/16 agents translating the same page.

### Solution: Deterministic Scattering

Each agent computes a **starting offset** from its branch ID so agents naturally spread across the work space:

```bash
MY_BRANCH=$(git branch --show-current)
MY_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$')

# Convert hex ID to a number, mod by total units
OFFSET=$(printf '%d' "0x${MY_ID}" 2>/dev/null || echo "0")
TOTAL_UNITS=99  # <-- set this to your project's unit count
START_UNIT=$(( (OFFSET % TOTAL_UNITS) + 1 ))

echo "I am $MY_ID, starting at unit $START_UNIT"
```

After completing the starting unit, the agent scans for the **lowest uncompleted unit** (wrapping around). This ensures:
- Agents start spread across the work space
- They converge naturally toward filling gaps
- No coordination is needed to achieve this distribution

### Finding the Next Unit

```bash
# Fetch all branches in this experiment
git fetch origin --prune 2>/dev/null

# Collect completed units from all branches
COMPLETED=""
BRANCH_PREFIX="cursor/YOUR-EXPERIMENT-PREFIX"  # <-- set this

for branch in $(git branch -r | grep "origin/${BRANCH_PREFIX}" | tr -d ' '); do
  # Check which output files exist on each branch
  FILES=$(git ls-tree --name-only -r "$branch" -- output/ 2>/dev/null)
  COMPLETED="$COMPLETED $FILES"
done

# Also check local filesystem
LOCAL=$(ls output/*.json 2>/dev/null)
COMPLETED="$COMPLETED $LOCAL"

# Find lowest available unit not in COMPLETED
# (implementation depends on your file naming scheme)
```

**Key**: Check **actual output files**, not state files. Files don't lie.

---

## Sync Protocol

### What to Sync

| Check | How | Why |
|---|---|---|
| Completed units | `git ls-tree` output files on each branch | Avoid duplicating done work |
| Claimed units | Read AGENT_STATE.md from active branches | Avoid duplicating in-progress work |
| Active agents | Presence of AGENT_STATE.md + recent commit | Know team size |

### How to Sync (30-second version)

```bash
git fetch origin --prune 2>/dev/null

CLAIMED=""
COMPLETED=""

for branch in $(git branch -r | grep "origin/${BRANCH_PREFIX}" | tr -d ' '); do
  # Get completed outputs
  DONE=$(git ls-tree --name-only "$branch" -- output/ 2>/dev/null)
  COMPLETED="$COMPLETED $DONE"

  # Get current claim (only from recently active agents)
  STATE=$(git show "${branch}:AGENT_STATE.md" 2>/dev/null)
  if [ -n "$STATE" ]; then
    CLAIM=$(echo "$STATE" | grep -oP 'Current Unit: \K[0-9]+' | head -1)
    HEARTBEAT=$(echo "$STATE" | grep -oP 'Heartbeat: \K[0-9]+' | head -1)
    NOW=$(date +%s)
    AGE=$(( NOW - ${HEARTBEAT:-0} ))
    if [ "$AGE" -lt 600 ]; then  # Active in last 10 min
      CLAIMED="$CLAIMED $CLAIM"
    fi
  fi
done
```

### When to Sync

- **Before each new unit** (mandatory)
- **NOT during unit execution** (don't interrupt productive work)
- **After pushing** (verify your work is visible)

### Experiment Isolation

Only discover branches matching your experiment's prefix. This prevents confusion with old experiments:

```bash
# GOOD: Only find branches from this experiment
BRANCH_PREFIX="cursor/book-translation-multi-agent"
git branch -r | grep "origin/${BRANCH_PREFIX}"

# BAD: Find ALL cursor branches (includes old experiments)
git branch -r | grep "origin/cursor/"
```

---

## AGENT_STATE.md Format

Each agent maintains a minimal state file. **Keep it simple** -- the state file is a courtesy to other agents, not a requirement.

```markdown
# Agent: XXXX

- **Branch**: cursor/experiment-prefix-XXXX
- **Heartbeat**: 1735689600
- **Current Unit**: 15
- **Status**: working

## Completed
1, 5, 8, 12, 13, 14

## Log
- [timestamp] Started at unit 42 (computed offset)
- [timestamp] Completed unit 42, synced, claiming unit 1
- [timestamp] Completed unit 1, synced, claiming unit 5
```

**Update frequency**: After every unit completion + claim. This naturally provides heartbeats.

---

## Conflict Resolution

### Two Agents Produce the Same Unit

This will happen occasionally. It is **acceptable**.

- Both agents keep their output on their respective branches
- During final assembly, one version is chosen (e.g., the one from the agent with more total completions, or the earlier timestamp)
- **Do not** waste time trying to prevent this. Some duplication (< 10%) is cheaper than coordination overhead

### Git Push Conflicts

Agents work on separate branches, so git push conflicts should not occur. If they do:

```bash
git pull --rebase origin HEAD 2>/dev/null
git push -u origin HEAD
```

### Claiming Conflicts

If you sync and see another agent claimed the same unit you're about to claim:
1. Skip it
2. Pick the next available unit
3. Move on

Do not negotiate. Do not wait. Just pick a different unit.

---

## What NOT to Do

These are real failure patterns from 32 agents across 2 experiments:

| Anti-pattern | Why it kills parallelism |
|---|---|
| Run setup/install before producing output | Wastes 10-20 min of context on work that's already done |
| Wait for format/approach consensus | Deadlocks when agents die or disagree |
| Implement phased execution (M0 → M1 → M2) | Forces sequential bottlenecks |
| Start from unit 1 alongside all other agents | Creates N-way duplication on early units |
| Skip syncing before claiming | Duplicate work without knowing it |
| Create research/analysis docs | You're here to produce output, not write reports |
| Update state file without producing output | Activity theater -- push output, not status |
| Stop after one unit to "check in" | Break your flow; keep producing |
| Build custom tools or scripts | Use what's provided; tool-building is a trap |
| Explore multiple approaches before committing | Pick one approach and go |

---

## Continuous Execution

**This is the single most important behavioral instruction.**

Prior experiments showed that most agents produced 1-5 units and then stopped. The agents that completed the project were the ones that kept going without pausing.

```
DO NOT STOP after completing one unit.
DO NOT STOP to ask for confirmation.
DO NOT STOP to write analysis.
DO NOT STOP to wait for other agents.
DO NOT STOP to restructure your approach.

Produce output → push → sync → produce output → push → sync → ...

Continue until ALL units are done or you are genuinely unable to continue.
```

An agent that translates 10 pages in 30 minutes is 10x more valuable than an agent that spends 30 minutes on perfect setup and translates 0 pages.

---

## Timeouts

| Event | Threshold |
|---|---|
| Agent considered offline | 10 min since last commit |
| Claimed unit becomes reclaimable | 10 min after agent goes offline |
| Sync before claiming | Mandatory, but < 30 seconds |
| Push after completing | Immediate |

No other timeouts. No waiting periods. No cooldowns.

---

## Final Assembly

When all units are complete (or the deadline is reached):

1. Any agent (or a separate assembly process) collects all output files from all branches
2. For duplicates, pick the best version (or first encountered)
3. Combine into final deliverable
4. No special coordination needed -- this is a post-hoc step

```bash
# Collect all outputs from all experiment branches
for branch in $(git branch -r | grep "origin/${BRANCH_PREFIX}" | tr -d ' '); do
  for unit in $(seq 1 $TOTAL_UNITS); do
    FILE="output/unit_$(printf '%03d' $unit).json"
    if [ ! -f "$FILE" ]; then  # Only if we don't have it yet
      git show "${branch}:${FILE}" > "$FILE" 2>/dev/null && echo "Got unit $unit from $branch"
    fi
  done
done
```

---

## Protocol Fitness Checklist

Before deploying this protocol for a new project, verify:

- [ ] All setup/research/tooling is **pre-completed** and committed to main
- [ ] `TASK.md` describes exactly what each unit of work requires (input, output format, quality bar)
- [ ] Output directory and file naming scheme are defined
- [ ] Example output file exists for reference
- [ ] Branch naming prefix is defined for experiment isolation
- [ ] Total unit count is known and specified
- [ ] No phase gates or consensus requirements exist in the instructions
- [ ] Instructions contain explicit "do not stop" continuous-execution language
- [ ] Starting-offset formula is included

---

## Adapting This Protocol

This protocol is generic. To use it for a specific task:

1. **Replace "unit"** with your work unit (page, file, chapter, function, etc.)
2. **Set `TOTAL_UNITS`** to your project's count
3. **Set `BRANCH_PREFIX`** to your experiment's branch naming pattern
4. **Set `output/`** to your output directory path
5. **Write `TASK.md`** describing exactly what producing one unit entails
6. **Pre-complete all setup** so agents can start producing immediately

### Example: Book Translation

```
Unit = one page of the book
TOTAL_UNITS = 99
BRANCH_PREFIX = "cursor/book-translation-v3"
Output directory = translations/
Output file = translations/page_XXX.json
TASK.md = describes how to translate one page (input format, output JSON schema, quality rules)
```

### Example: Codebase Migration

```
Unit = one source file to migrate
TOTAL_UNITS = 250
BRANCH_PREFIX = "cursor/migration-batch-1"
Output directory = migrated/
Output file = migrated/module_XXX.py
TASK.md = describes how to migrate one file (old API → new API mapping, test requirements)
```

### Example: Test Generation

```
Unit = one module to test
TOTAL_UNITS = 80
BRANCH_PREFIX = "cursor/test-gen"
Output directory = tests/
Output file = tests/test_module_XXX.py
TASK.md = describes coverage requirements, test style, mocking strategy
```

---

## Protocol Summary (Pocket Reference)

```
1. Read TASK.md. Start producing output within 60 seconds.
2. Compute starting unit from branch ID hash. Don't start at unit 1.
3. Sync (30s): fetch branches, check output files + claims.
4. Claim: update AGENT_STATE.md, push.
5. Execute: produce the output file for this unit.
6. Complete: commit output + state, push.
7. Loop to step 3 until all units are done.
8. Never wait. Never block. Never stop. Just produce.
```
