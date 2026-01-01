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

## Branch Naming Convention

```
worker/[WORKER_ID]/durov-translation

Examples:
  worker/01/durov-translation
  worker/02/durov-translation
  ...
  worker/16/durov-translation
```

Workers identify themselves by extracting WORKER_ID from their current branch name.

---

## Worker State File: `WORKER_STATE.md`

Each worker maintains a `WORKER_STATE.md` file in their branch root. This is the primary state broadcast mechanism.

### Format

```markdown
# Worker [ID] State

## Identity
- **Worker ID**: [01-16]
- **Branch**: worker/[ID]/durov-translation
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
[WORKER-XX] [MILESTONE] [ACTION]: [description]

STATE: [milestone].[task] = [status]
PAGES: [claimed pages, comma-separated]
HEARTBEAT: [unix timestamp]
```

### Examples

```
[WORKER-03] M0 COMPLETE: Dependency installation verified
STATE: M0.1 = done
HEARTBEAT: 1705312800

[WORKER-07] M2 CLAIM: Starting pages 25-27
STATE: M2.translating
PAGES: 25,26,27
HEARTBEAT: 1705315000

[WORKER-12] M2 DONE: Completed page 42 translation
STATE: M2.page_done
PAGES: 42
HEARTBEAT: 1705318000
```

### Consensus Commits

```
[WORKER-XX] VOTE: [topic] = [choice]
CONSENSUS: [topic] = [choice]
HEARTBEAT: [unix timestamp]
```

### Sync Commits

```
[WORKER-XX] SYNC: Pulled states from all workers
OBSERVED: [list of worker IDs seen]
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
# Fetch all worker branches
git fetch origin 'refs/heads/worker/*:refs/remotes/origin/worker/*'
```

### Step 2: Read Other Workers' States

```bash
# For each worker branch, read their WORKER_STATE.md
for i in $(seq -w 1 16); do
  git show origin/worker/${i}/durov-translation:WORKER_STATE.md 2>/dev/null
done
```

### Step 3: Aggregate Global State

Parse all WORKER_STATE.md files to build a global view:
- Which pages are claimed/done
- Which tasks are complete
- Who is blocked
- Consensus vote tallies

### Step 4: Update Local Decisions

Based on global state, decide:
- Which page to work on next (M2)
- Whether consensus is reached (M0/M1)
- Who needs help

---

## Milestone 0 & 1: Consensus Protocol

### Task Assignment Strategy

During M0/M1, tasks can be done redundantly. Multiple workers may complete the same task independently.

### Consensus Mechanism

For decisions requiring agreement (e.g., LaTeX vs Python, color scheme):

1. **Propose**: Worker commits their solution with result hash
2. **Vote**: Other workers review and vote (agree/disagree)
3. **Quorum**: Need 9/16 (>50%) votes for the same solution
4. **Adopt**: Once quorum reached, all workers adopt that solution

### Verification Before M2

Before any worker enters M2, they must:

1. **Collect all 16 branches' M0/M1 outputs**
2. **Run cross-verification tests**:
   - Execute other workers' test scripts with your outputs
   - Execute your test scripts with other workers' outputs
3. **All outputs must match** (hash comparison)
4. **Commit verification results**:
   ```
   [WORKER-XX] VERIFY: M0/M1 cross-check passed
   VERIFIED_WITH: 01,02,03,...,16
   RESULT_HASH: [common hash]
   READY_FOR_M2: true
   ```
5. **Wait for all 16 workers to report READY_FOR_M2: true**

---

## Milestone 2: Parallel Translation Protocol

### Page Assignment Algorithm

**Initial Assignment**: Worker N claims page N (Worker 1 → Page 1, Worker 16 → Page 16)

**Subsequent Assignment** (after completing a page):

```python
def claim_next_page(worker_id, global_state):
    # Get list of all pages (1-99)
    all_pages = set(range(1, 100))
    
    # Remove claimed and completed pages
    claimed = global_state.get_claimed_pages()
    completed = global_state.get_completed_pages()
    available = all_pages - claimed - completed
    
    if not available:
        return None  # All pages assigned
    
    # Claim the lowest available page number
    # (Ensures no conflicts if multiple workers pull at same time)
    next_page = min(available)
    return next_page
```

**Conflict Resolution**:
- If two workers claim the same page (race condition), the one with earlier timestamp wins
- Losing worker re-pulls and claims next available page

### Page Claim Protocol

1. **Pull** latest states from all workers
2. **Identify** next available page
3. **Commit claim** immediately:
   ```
   [WORKER-XX] M2 CLAIM: Starting page YY
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
   [WORKER-XX] M2 DONE: Completed page YY
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

1. **Timestamp Priority**: Earlier timestamp wins
2. **Worker ID Priority**: Lower worker ID wins (tiebreaker)
3. **Hash Comparison**: If outputs differ, workers vote on best version
4. **Majority Rule**: >50% agreement adopts solution

---

## Agent Startup Sequence

When an agent starts (or resumes):

```
1. IDENTIFY
   - Determine own worker ID from branch name
   - Read local WORKER_STATE.md if exists

2. SYNC
   - git fetch all worker branches
   - Parse all WORKER_STATE.md files
   - Build global state picture

3. ORIENT
   - What milestone are we in globally?
   - What is my current task?
   - What tasks are available?

4. BROADCAST
   - Update my WORKER_STATE.md with current status
   - Commit and push heartbeat

5. EXECUTE
   - Perform next task based on global state
   - Commit/push after each significant action

6. REPEAT (goto SYNC every 60-120 seconds)
```

---

## Communication Message Types

### INFO (Informational)
```
[WORKER-XX] INFO: [message]
```
For status updates, progress notes, observations.

### CLAIM (Resource Claim)
```
[WORKER-XX] CLAIM: [resource type] = [resource id]
```
For claiming pages or tasks.

### DONE (Completion)
```
[WORKER-XX] DONE: [task/page description]
HASH: [output hash for verification]
```

### VOTE (Consensus)
```
[WORKER-XX] VOTE: [topic] = [choice]
```

### VERIFY (Verification)
```
[WORKER-XX] VERIFY: [what was verified]
RESULT: pass | fail
DETAILS: [specifics]
```

### ALERT (Important Notice)
```
[WORKER-XX] ALERT: [urgent message]
```
For blockers, errors, or coordination issues.

### REQUEST (Asking for Help)
```
[WORKER-XX] REQUEST: [what help is needed]
FROM: [specific worker IDs or "ALL"]
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

### Sync and Check State
```bash
git fetch origin 'refs/heads/worker/*:refs/remotes/origin/worker/*'
for i in $(seq -w 1 16); do
  echo "=== Worker $i ==="
  git show origin/worker/${i}/durov-translation:WORKER_STATE.md 2>/dev/null | head -20
done
```

### Claim a Page
```bash
# Update WORKER_STATE.md with claim
# Then:
git add WORKER_STATE.md
git commit -m "[WORKER-XX] M2 CLAIM: Starting page YY
PAGES: YY
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Complete a Page
```bash
git add translations/raw/page_YY.json output/page_YY_translated.pdf WORKER_STATE.md
git commit -m "[WORKER-XX] M2 DONE: Completed page YY
PAGES: YY
OUTPUT_HASH: $(sha256sum translations/raw/page_YY.json | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Check Global Progress
```bash
# See which pages are done across all workers
git fetch origin 'refs/heads/worker/*:refs/remotes/origin/worker/*'
git log --all --oneline --grep="M2 DONE" | sort
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
- All 16 workers can see each other's states
- No two workers translate the same page
- Consensus is reached for M0/M1 decisions
- All workers complete M2 within expected time
- Final outputs are identical across all branches

---

*This protocol should be followed by all 16 workers. Do not deviate without coordinating via ALERT messages.*
