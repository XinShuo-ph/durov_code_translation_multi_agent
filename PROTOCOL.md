# Multi-Agent Communication Protocol

## Overview

This protocol enables 16 AI agents to work in parallel on the Durov Code translation project. Each agent operates on its own git branch and uses git commit/push/pull as the primary communication mechanism—analogous to MPI (Message Passing Interface) for distributed computing, but with git as the transport layer and time measured in seconds/minutes rather than nanoseconds.

---

## Core Principles

### 1. Git as Message Passing Interface
- **Branch = Worker Identity**: Each worker's branch is their unique identifier
- **Commit = State Broadcast**: Every commit broadcasts state to other workers
- **Push = Send Message**: Pushing makes your state visible to others
- **Pull = Receive Messages**: Pulling retrieves other workers' states

### 2. High-Frequency Communication
Unlike traditional MPI where communication is near-instant, our "clock cycle" is 30-120 seconds (time for push/pull + agent thinking). Therefore:
- **Commit early, commit often**: Don't batch large changes
- **Push immediately after meaningful progress**
- **Pull frequently to stay synchronized**

### 3. Consensus Before Progress
For setup tasks (M0/M1), all 16 workers must agree before proceeding. For translation (M2), workers claim pages atomically.

---

## Branch Naming and Worker Discovery

### Branch Names Are Dynamic
Branches are created by Cursor with random names like:
```
cursor/multi-agent-parallel-translation-cca9
cursor/durov-book-translation-plan-7379
cursor/some-other-random-name-xxxx
```

**There is NO fixed naming convention.** Workers must discover each other dynamically.

### Worker Identity
Each worker identifies itself by:
1. **Branch Name**: The full branch name (e.g., `cursor/multi-agent-parallel-translation-cca9`)
2. **Short ID**: Last 4 characters of branch name (e.g., `cca9`) - used in commit messages

### Worker Discovery Protocol

**Step 1: Identify Your Own Branch**
```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_BRANCH (short: $MY_SHORT_ID)"
```

**Step 2: Discover All Worker Branches**
```bash
# Fetch all remote branches
git fetch origin --all

# List all cursor/* branches (these are potential workers)
git branch -r | grep 'origin/cursor/' | sed 's|origin/||'
```

**Step 3: Check Which Branches Have WORKER_STATE.md**
Only branches with `WORKER_STATE.md` are active workers:
```bash
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||'); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
    echo "Active worker: $branch"
  fi
done
```

### Worker Registration
When a worker starts, it MUST:
1. Create `WORKER_STATE.md` on its branch
2. Commit and push immediately
3. This registers the worker as "active"

Workers without `WORKER_STATE.md` are not considered part of the parallel execution.

---

## Worker State File: `WORKER_STATE.md`

Each worker maintains a `WORKER_STATE.md` file in their branch root. This is the primary state broadcast mechanism AND the registration signal.

**A branch with `WORKER_STATE.md` = An active worker**

### Format

```markdown
# Worker State: [SHORT_ID]

## Identity
- **Branch**: [full branch name, e.g., cursor/multi-agent-parallel-translation-cca9]
- **Short ID**: [last 4 chars, e.g., cca9]
- **Last Updated**: [ISO 8601 timestamp]
- **Heartbeat**: [Unix timestamp in seconds]

## Current Milestone
- **Milestone**: M0 | M1 | M2 | M3
- **Status**: working | waiting_consensus | blocked | completed

## M0/M1 Task Status
| Task ID | Description | Status | Result Hash |
|---------|-------------|--------|-------------|
| M0.1 | Install dependencies | done/pending/working | [sha256 first 8 chars] |
| M0.2 | Extract PDF text | done/pending/working | [sha256 first 8 chars] |
| ... | ... | ... | ... |

## M2 Page Claims
| Page | Status | Started | Completed |
|------|--------|---------|-----------|
| 13 | translating | 2024-01-15T10:30:00Z | - |
| 14 | done | 2024-01-15T10:00:00Z | 2024-01-15T10:25:00Z |

## Consensus Votes
| Topic | My Vote | Timestamp |
|-------|---------|-----------|
| format_approach | latex_xecjk | 2024-01-15T09:00:00Z |
| color_scheme | ru_black_en_blue | 2024-01-15T09:05:00Z |

## Known Workers
[List of discovered worker branches and their last seen status]

## Messages to Other Workers
[Free-form messages, warnings, or coordination notes]

## Blockers
[Any issues preventing progress]
```

---

## Commit Message Protocol

All commits must follow this format for machine parsing:

### State Broadcast Commits

```
[SHORT_ID] [MILESTONE] [ACTION]: [description]

STATE: [milestone].[task] = [status]
PAGES: [claimed pages, comma-separated]
HEARTBEAT: [unix timestamp]
```

Where `SHORT_ID` is the last 4 characters of your branch name.

### Examples

```
[cca9] M0 COMPLETE: Dependency installation verified
STATE: M0.1 = done
HEARTBEAT: 1705312800

[7379] M2 CLAIM: Starting pages 25-27
STATE: M2.translating
PAGES: 25,26,27
HEARTBEAT: 1705315000

[a2b3] M2 DONE: Completed page 42 translation
STATE: M2.page_done
PAGES: 42
HEARTBEAT: 1705318000
```

### Consensus Commits

```
[SHORT_ID] VOTE: [topic] = [choice]
CONSENSUS: [topic] = [choice]
HEARTBEAT: [unix timestamp]
```

### Sync Commits

```
[SHORT_ID] SYNC: Pulled states from all workers
OBSERVED: [list of short IDs seen]
HEARTBEAT: [unix timestamp]
```

---

## Communication Frequency Requirements

### Pull Frequency
| Phase | Minimum Pull Interval | Recommended |
|-------|----------------------|-------------|
| M0/M1 (Consensus) | Every 60 seconds | Every 30 seconds |
| M2 (Translation) | Every 120 seconds | Every 60 seconds |
| M3 (Assembly) | Every 60 seconds | Every 30 seconds |

### Push Frequency
| Event | Push Timing |
|-------|-------------|
| Task started | Immediately |
| Task completed | Immediately |
| Page claimed | Immediately |
| Page completed | Immediately |
| Error/blocker | Immediately |
| Heartbeat (if idle) | Every 5 minutes |

---

## Synchronization Protocol

### Step 1: Fetch All Remote Branches

```bash
# Fetch all remote branches
git fetch origin --all --prune
```

### Step 2: Discover Active Workers

```bash
# Find all cursor/* branches that have WORKER_STATE.md
ACTIVE_WORKERS=()
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
    ACTIVE_WORKERS+=("$branch")
    echo "Found active worker: $branch"
  fi
done
echo "Total active workers: ${#ACTIVE_WORKERS[@]}"
```

### Step 3: Read Other Workers' States

```bash
# For each active worker branch, read their WORKER_STATE.md
for branch in "${ACTIVE_WORKERS[@]}"; do
  echo "=== $branch ==="
  git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | head -30
done
```

### Step 4: Aggregate Global State

Parse all WORKER_STATE.md files to build a global view:
- Which pages are claimed/done (across all workers)
- Which tasks are complete
- Who is blocked
- Consensus vote tallies
- Total number of active workers

### Step 5: Update Local Decisions

Based on global state, decide:
- Which page to work on next (M2)
- Whether consensus is reached (M0/M1) - need >50% of active workers
- Who needs help
- Whether to wait for more workers to come online

---

## Milestone 0 & 1: Consensus Protocol

### Task Assignment Strategy

During M0/M1, tasks can be done redundantly. Multiple workers may complete the same task independently.

### Consensus Mechanism

For decisions requiring agreement (e.g., LaTeX vs Python, color scheme):

1. **Propose**: Worker commits their solution with result hash
2. **Vote**: Other workers review and vote (agree/disagree)
3. **Quorum**: Need >50% of **active workers** votes for the same solution
4. **Adopt**: Once quorum reached, all workers adopt that solution

**Important**: Quorum is based on active workers (those with WORKER_STATE.md), not a fixed 16. If only 10 workers are online, need 6 votes.

### Verification Before M2

Before any worker enters M2, they must:

1. **Discover all active worker branches**
2. **Collect their M0/M1 outputs**
3. **Run cross-verification tests**:
   - Execute other workers' test scripts with your outputs
   - Execute your test scripts with other workers' outputs
4. **All outputs must match** (hash comparison)
5. **Commit verification results**:
   ```
   [SHORT_ID] VERIFY: M0/M1 cross-check passed
   VERIFIED_WITH: [list of short IDs]
   RESULT_HASH: [common hash]
   READY_FOR_M2: true
   ```
6. **Wait for all active workers to report READY_FOR_M2: true**

---

## Milestone 2: Parallel Translation Protocol

### Page Assignment Algorithm

**Initial Assignment**: No fixed assignment. Each worker claims the lowest available page.

**Page Claiming Algorithm**:

```python
def claim_next_page(my_short_id, all_worker_states):
    """
    1. Scan all active workers' WORKER_STATE.md
    2. Collect all claimed and completed pages
    3. Claim the lowest available page
    """
    all_pages = set(range(1, 100))  # Pages 1-99
    
    claimed = set()
    completed = set()
    
    for worker_state in all_worker_states:
        claimed.update(worker_state.get_claimed_pages())
        completed.update(worker_state.get_completed_pages())
    
    available = sorted(all_pages - claimed - completed)
    
    if available:
        return available[0]  # Lowest available
    return None  # All done!
```

**Conflict Resolution**:
- If two workers claim the same page (race condition), the one with earlier commit timestamp wins
- Tie-breaker: Lexicographically earlier branch name wins
- Losing worker re-pulls and claims next available page

### Page Claim Protocol

1. **Pull** latest states from all active workers
2. **Identify** next available page (lowest unclaimed/uncompleted)
3. **Commit claim** immediately:
   ```
   [SHORT_ID] M2 CLAIM: Starting page YY
   PAGES: YY
   HEARTBEAT: [timestamp]
   ```
4. **Push** immediately
5. **Start translating** only after push succeeds

### Page Completion Protocol

1. **Complete translation** (all 4 languages)
2. **Save translation files** (JSON + PDF)
3. **Commit completion**:
   ```
   [SHORT_ID] M2 DONE: Completed page YY
   PAGES: YY
   OUTPUT_HASH: [sha256 of translation JSON]
   ```
4. **Push** immediately
5. **Pull** to check for new page claims
6. **Claim next page** (goto claim protocol)

### Progress Broadcast Format

After each page completion, update WORKER_STATE.md with:

```markdown
## M2 Progress
| Page | Status | Translation Hash | PDF Generated |
|------|--------|------------------|---------------|
| 5 | done | a8f3b2c1 | yes |
| 21 | done | c9d4e5f6 | yes |
| 37 | translating | - | no |
```

---

## Deadlock Prevention

### Timeout Rules

| Situation | Timeout | Action |
|-----------|---------|--------|
| Worker claims page but no progress commit | 30 minutes | Page becomes available again |
| Worker hasn't pushed in | 15 minutes | Consider worker stalled |
| Waiting for consensus | 20 minutes | Proceed with majority vote |
| Waiting for verification | 30 minutes | Re-run verification |

### Heartbeat Protocol

Workers must update their `HEARTBEAT` field in WORKER_STATE.md:
- At least every 5 minutes while active
- On every commit

If a worker's heartbeat is >15 minutes old, other workers may:
- Reclaim their pages
- Proceed without their vote
- Flag them as potentially stalled

### Stall Recovery

If a worker detects they're stalled (can't push, can't pull):
1. Log the error in WORKER_STATE.md
2. Attempt recovery (retry 3x with exponential backoff)
3. If still blocked, commit blocker status
4. Other workers will work around them

---

## Conflict Resolution Hierarchy

1. **Timestamp Priority**: Earlier commit timestamp wins
2. **Branch Name Priority**: Lexicographically earlier branch name wins (tiebreaker)
3. **Hash Comparison**: If outputs differ, workers vote on best version
4. **Majority Rule**: >50% of active workers agreement adopts solution

---

## Agent Startup Sequence

When an agent starts (or resumes):

```
1. IDENTIFY YOURSELF
   MY_BRANCH=$(git branch --show-current)
   MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
   # Example: cursor/multi-agent-parallel-translation-cca9 → cca9

2. CREATE/UPDATE WORKER_STATE.md
   - If first time: Create from template, fill in your branch info
   - If resuming: Update with current timestamp
   - This file is your registration signal!

3. SYNC - DISCOVER OTHER WORKERS
   git fetch origin --all --prune
   # Find all cursor/* branches with WORKER_STATE.md
   # Read each worker's state
   # Build global picture: who's online, what's claimed, what's done

4. BROADCAST YOUR PRESENCE
   git add WORKER_STATE.md
   git commit -m "[SHORT_ID] SYNC: Starting session
   HEARTBEAT: $(date +%s)"
   git push origin HEAD

5. ORIENT
   - What milestone are we in globally?
   - How many active workers?
   - What's my current task?
   - What tasks/pages are available?

6. EXECUTE
   - Perform next task based on global state
   - Commit/push after each significant action

7. REPEAT (goto step 3 every 60-120 seconds)
```

---

## Communication Message Types

All messages use `[SHORT_ID]` prefix (last 4 chars of your branch name).

### INFO (Informational)
```
[SHORT_ID] INFO: [message]
```
For status updates, progress notes, observations.

### CLAIM (Resource Claim)
```
[SHORT_ID] CLAIM: [resource type] = [resource id]
```
For claiming pages or tasks.

### DONE (Completion)
```
[SHORT_ID] DONE: [task/page description]
HASH: [output hash for verification]
```

### VOTE (Consensus)
```
[SHORT_ID] VOTE: [topic] = [choice]
```

### VERIFY (Verification)
```
[SHORT_ID] VERIFY: [what was verified]
RESULT: pass | fail
DETAILS: [specifics]
```

### ALERT (Important Notice)
```
[SHORT_ID] ALERT: [urgent message]
```
For blockers, errors, or coordination issues.

### REQUEST (Asking for Help)
```
[SHORT_ID] REQUEST: [what help is needed]
FROM: [specific short IDs or "ALL"]
```

---

## File Outputs and Hashing

### Hash Calculation

For verification, calculate SHA256 of output files:

```bash
# For translation JSON
sha256sum translations/raw/page_XXX.json | cut -c1-8

# For compiled PDF
sha256sum output/page_XXX_translated.pdf | cut -c1-8
```

### Shared Output Location

Final, agreed-upon outputs should be placed in standard locations so all workers can verify:

```
translations/
  raw/           # First-pass (any worker can write)
  verified/      # After cross-verification (consensus)
  final/         # After 3x review (consensus)
```

---

## Quick Reference: Command Sequences

### Get Your Short ID
```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "My Short ID: $MY_SHORT_ID"
```

### Discover Active Workers
```bash
git fetch origin --all --prune
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
    short_id=$(echo "$branch" | grep -oE '[^-]+$' | tail -c 5)
    echo "Active: $branch ($short_id)"
  fi
done
```

### Read All Worker States
```bash
git fetch origin --all --prune
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
    echo "=== $branch ==="
    git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | head -25
  fi
done
```

### Claim a Page
```bash
# Update WORKER_STATE.md with claim
# Then:
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] M2 CLAIM: Starting page YY
PAGES: YY
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Complete a Page
```bash
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)
git add translations/raw/page_YY.json output/page_YY_translated.pdf WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] M2 DONE: Completed page YY
PAGES: YY
OUTPUT_HASH: $(sha256sum translations/raw/page_YY.json | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Check Global Progress
```bash
# See which pages are done across all workers
git fetch origin --all --prune
git log --remotes --oneline --grep="M2 DONE" | sort
```

---

## Emergency Protocols

### If You Can't Push (Branch Conflict)
1. Pull with rebase: `git pull --rebase origin HEAD`
2. Resolve any conflicts
3. Push again
4. If still failing, commit blocker status and wait

### If You See Stale Data
1. Force fresh fetch: `git fetch origin --prune`
2. Check network connectivity
3. If persistent, broadcast ALERT message

### If Consensus Can't Be Reached
1. Wait additional 10 minutes for votes
2. If still stuck, worker with lowest ID makes final decision
3. All workers must adopt that decision

---

## Success Metrics

The protocol is working correctly when:
- All active workers can discover and see each other's states
- No two workers translate the same page
- Consensus is reached for M0/M1 decisions (>50% of active workers)
- All workers complete M2 within expected time
- Final outputs are identical across all branches

---

## Summary: Key Differences from Fixed Naming

| Aspect | Old (Fixed) | New (Dynamic) |
|--------|-------------|---------------|
| Branch names | `worker/01/durov-translation` | `cursor/random-name-xxxx` |
| Worker ID | Fixed 01-16 | Short ID (last 4 chars of branch) |
| Discovery | Iterate 1-16 | Scan all `cursor/*` branches |
| Registration | Implicit | WORKER_STATE.md presence |
| Quorum | 9/16 fixed | >50% of active workers |
| Conflict tiebreaker | Lower worker ID | Earlier branch name (lexical) |

---

*This protocol should be followed by all workers. Do not deviate without coordinating via ALERT messages.*
