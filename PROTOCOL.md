# Multi-Agent Parallel Collaboration Protocol v2.0

**Philosophy**: Agents are a **coordinated team**, not isolated workers. Every agent actively synchronizes, balances workload, and avoids duplication.

**Work Unit**: Individual pages (not chapters). One page = one atomic unit of work.

---

## 🚨 CRITICAL: The 83% Waste Problem

**Previous sessions had 83% wasted effort:**
- Pages 8-12: Translated by 3 different agents (3x duplication)
- Pages 17-22: Translated by 2 different agents (2x duplication)  
- 12/16 agents: Barely participated (idle or stuck in setup)
- 1 agent: Translated 18 pages alone while others waited

**Root causes:**
1. No real-time synchronization before claiming pages
2. Complex consensus protocol blocked agent startup
3. No workload balancing mechanism
4. No reclaiming of work from stalled agents

**This protocol solves these problems.**

---

## Core Principles

### 1. Sync BEFORE Claim (Zero Duplication)
```
NEVER claim a page without syncing first.
ALWAYS check global state before claiming.
If in doubt, sync again.
```

### 2. Fast Startup (No Consensus Blocking)
```
First agent sets the approach → Others adopt it
No voting, no waiting for consensus
Setup tasks done by first 1-2 agents
Others jump straight to translation
```

### 3. Active Workload Balancing
```
Agents monitor each other's workload
If an agent has >3x more pages than you, help them
Claim pages strategically to balance the team
```

### 4. Aggressive Reclaiming
```
Agent stalled for 15 min? Reclaim their pages
Agent hasn't heartbeat for 10 min? Assume offline
Don't wait - the book must be finished
```

---

## Quick Start (First 60 Seconds)

### New Agent Joining

```bash
# 1. Identify yourself (5 seconds)
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_SHORT_ID"

# 2. Register (10 seconds)
cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
# Edit: Fill in your branch and short_id
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] JOIN: Registering as active worker
HEARTBEAT: $(date +%s)"
git push -u origin HEAD

# 3. Start sync daemon (5 seconds)
python3 tools/sync_daemon.py --start &
sleep 5  # Let it do initial sync

# 4. Get work and start (40 seconds)
# The sync daemon will tell you what to do:
# - If setup needed: Do one setup task
# - If setup done: Start translating
# Just ask the daemon for next page and GO!

NEXT_PAGE=$(python3 tools/sync_daemon.py --next-page)
# Start translating $NEXT_PAGE immediately
```

**Total time from start to productive work: 60 seconds**

---

## The Sync Daemon (Mandatory)

### Why Mandatory?

Without the daemon:
- 83% duplication (proven from 16-agent experiment)
- Agents work in isolation
- No awareness of team state

With the daemon:
- 0% duplication (proven from reference implementation)
- Real-time team awareness
- Automatic conflict prevention

### Starting the Daemon

```bash
# This is the FIRST thing you do after registering
python3 tools/sync_daemon.py --start &

# Daemon runs in background, syncing every 60 seconds
# It maintains a global state file: .sync/global_state.json
```

### Daemon Functions

The daemon automatically:
1. **Fetches all branches** every 60 seconds
2. **Reads all WORKER_STATE.md files** from active workers
3. **Builds global picture**: Who's online, what's claimed, what's done
4. **Detects stalled workers**: Heartbeat >10min = offline
5. **Reclaims pages**: From workers offline >15min
6. **Updates local cache**: `.sync/global_state.json`

### Querying the Daemon

```bash
# Get next available page
python3 tools/sync_daemon.py --next-page
# Output: 42

# Check if a specific page is available
python3 tools/sync_daemon.py --check-page 42
# Output: available | claimed_by_c3ab | completed

# See global status
python3 tools/sync_daemon.py --status
# Output: 
# Active workers: 12
# Completed pages: 35
# Claimed pages: 8
# Available pages: 56
# Stalled workers: 2 (ab12, cd34)

# Force immediate sync (don't wait for 60s interval)
python3 tools/sync_daemon.py --sync-now
```

---

## Worker Registration

### WORKER_STATE.md Format

```markdown
# Worker: [SHORT_ID]

## Identity
- **Branch**: [full branch name]
- **Short ID**: [last 4 chars]
- **Heartbeat**: [unix timestamp] ⚠️ MUST UPDATE EVERY 5 MIN
- **Status**: translating | idle | offline

## Current Work
- **Claimed Page**: [page number or "none"]
- **Started At**: [ISO timestamp]
- **Estimated Completion**: [ISO timestamp, be realistic]

## Completed Pages
| Page | Completed At | Hash | 
|------|--------------|------|
| 15   | 2026-01-01T05:30:00Z | a8f3b2c1 |
| 23   | 2026-01-01T06:15:00Z | c9d4e5f6 |

## Statistics (This Session)
- **Pages completed**: 2
- **Average time per page**: 25 minutes
- **Currently working on**: Page 42
- **Work started**: 2026-01-01T05:00:00Z
- **Last sync**: 2026-01-01T06:20:00Z

## Team Awareness
Last synced: 2026-01-01T06:20:00Z

| Worker | Status | Claimed | Completed | Last Heartbeat |
|--------|--------|---------|-----------|----------------|
| ab12   | online | 43      | 12        | 2min ago       |
| cd34   | online | 44      | 8         | 1min ago       |
| ef56   | STALLED| 45      | 5         | 18min ago ⚠️   |

## Notes
[Any messages to the team]
```

### Heartbeat Rules

**CRITICAL**: Your heartbeat is how the team knows you're alive.

```bash
# Update heartbeat on EVERY commit
HEARTBEAT: $(date +%s)

# If you haven't committed in 5 minutes, push a heartbeat:
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] HEARTBEAT
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

**Heartbeat timeout**:
- >10 minutes: You're considered offline
- >15 minutes: Your claimed pages can be reclaimed
- >30 minutes: You're assumed dead, fully ignored

---

## Page Claiming Protocol

### The Golden Rule

```
1. Query daemon: "Is this page available?"
2. If yes, claim it IMMEDIATELY
3. Push claim to origin IMMEDIATELY
4. Query daemon again: "Did my claim succeed?"
5. If race condition detected, un-claim and try next page
6. Start working ONLY after claim is confirmed
```

### Step-by-Step Claim Sequence

```bash
# 1. Get next available page from daemon
NEXT_PAGE=$(python3 tools/sync_daemon.py --next-page)
echo "Next available page: $NEXT_PAGE"

# 2. Update WORKER_STATE.md immediately
# Add to "Claimed Page" field
# Update heartbeat

# 3. Commit and push claim IMMEDIATELY
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] CLAIM: Page $NEXT_PAGE
HEARTBEAT: $(date +%s)"
git push origin HEAD

# 4. Verify claim succeeded (check for race condition)
sleep 5  # Give other agents time to push
python3 tools/sync_daemon.py --check-page $NEXT_PAGE

# 5. If output says "claimed_by_YOU", start working
# If output says "claimed_by_OTHER", you lost the race - try again
```

### Conflict Resolution (Race Condition)

If two agents claim the same page simultaneously:

1. **Earlier timestamp wins** (commit timestamp, not push timestamp)
2. **Tie-breaker**: Lexicographically earlier branch name
3. **Loser must**: Un-claim page, update WORKER_STATE.md, try next page
4. **Winner**: Continue working

The sync daemon detects this automatically and reports it via `--check-page`.

---

## Page Completion Protocol

```bash
# 1. Finish translation (all required formats)
# 2. Save output files
# 3. Calculate hash
HASH=$(sha256sum translations/page_${PAGE_NUM}.json | cut -c1-8)

# 4. Update WORKER_STATE.md
# - Move page from "Claimed Page" to "Completed Pages" table
# - Update statistics
# - Update heartbeat

# 5. Commit with DONE message
git add translations/page_${PAGE_NUM}.json WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] DONE: Page $PAGE_NUM
HASH: $HASH
HEARTBEAT: $(date +%s)"
git push origin HEAD

# 6. Immediately claim next page (loop back to claim protocol)
```

---

## Workload Balancing

### The Balancing Rule

```
Every 3 pages you complete, check team balance:
- If any agent has >2x your completed count, slow down
- If any agent has <0.5x your completed count, speed up
- If you're way ahead, help with unclaimed pages in middle of book
```

### Balancing Strategies

**If you're ahead (completed >3x average):**
- Take a break, let others catch up
- Help with difficult pages (longer chapters)
- Review your work quality
- OR: Keep going but from different part of book (jump ahead)

**If you're behind (completed <0.5x average):**
- Claim consecutive pages (build momentum)
- Ask for help in WORKER_STATE.md notes
- Check if you're doing unnecessary work (e.g., over-polishing)

**If team is balanced:**
- Everyone keeps claiming lowest available page
- Efficient parallel progress

### Monitoring Balance

```bash
# Check team balance
python3 tools/sync_daemon.py --balance

# Output:
# Worker | Completed | Rate (pages/hour) | Status
# -------|-----------|-------------------|--------
# ab12   | 15        | 3.2               | ⚡ Fast
# cd34   | 14        | 3.0               | ✓ Good
# ef56   | 13        | 2.8               | ✓ Good
# gh78   | 4         | 0.9               | ⚠️ Slow
# ij90   | 2         | 0.4               | 🐌 Very slow
#
# Balance: GOOD (std dev: 4.2 pages)
# Recommendation: Keep going
```

---

## Stalled Worker Recovery

### Detecting Stalled Workers

A worker is **stalled** if:
- Heartbeat >10 minutes old
- Has claimed page but no progress commit
- Status stuck in "translating" for >30 minutes

### Reclaiming from Stalled Workers

```bash
# Daemon automatically detects stalled workers
# After 15 minutes, their pages become reclaimable

# Check for reclaimable pages
python3 tools/sync_daemon.py --reclaimable

# Output:
# Page 42: Claimed by ef56 (18 minutes ago, stalled)
# Page 43: Claimed by gh78 (22 minutes ago, stalled)

# Reclaim a page
python3 tools/sync_daemon.py --reclaim 42

# This updates your WORKER_STATE.md with:
# "Reclaimed page 42 from ef56 (stalled 18min)"
```

### What to Do When You Come Back Online

If you were offline and come back:

```bash
# 1. Restart sync daemon
python3 tools/sync_daemon.py --start &

# 2. Check your old claimed page
python3 tools/sync_daemon.py --check-page YOUR_OLD_PAGE

# 3. If it was reclaimed: No problem! Claim next available
# 4. If it's still yours: Continue where you left off

# 5. Update heartbeat immediately to show you're back
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] BACK: Resuming work
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

---

## Setup Phase (Simplified)

### Previous Problem
- Complex M0/M1 consensus phases
- Workers blocked waiting for votes
- 30+ minutes before translation started

### New Approach: First-In, First-Done

**First worker** (earliest to register):
1. Does setup tasks (install deps, create templates, translate 1 demo page)
2. Commits setup files
3. Starts translating

**All other workers**:
1. See setup is done (check for `setup_complete` file)
2. Adopt the approach (copy templates)
3. Start translating immediately
4. No voting, no consensus, no waiting

### Setup Tasks

Only the **first 1-2 workers** need to do this:

```bash
# Check if setup is done
if [ -f .setup_complete ]; then
  echo "Setup already done by another worker, starting translation"
  # Copy templates from their branch
  git show "origin/FIRST_WORKER_BRANCH:tools/template.tex" > tools/template.tex
  # Start translating
else
  echo "I'm first, doing setup"
  
  # Do setup tasks:
  # 1. Install dependencies
  # 2. Create LaTeX/PDF template
  # 3. Translate 1 demo page (to verify approach works)
  
  # Mark setup complete
  touch .setup_complete
  git add .setup_complete tools/
  git commit -m "[$MY_SHORT_ID] SETUP: Complete, approach verified"
  git push origin HEAD
  
  # Start translating
fi
```

**Time saved**: 20-30 minutes (from 30+ min to <60 seconds for later workers)

---

## Commit Message Format

### Standard Format

```
[$SHORT_ID] ACTION: Description
HEARTBEAT: [unix timestamp]
```

### Actions

| Action | When | Example |
|--------|------|---------|
| `JOIN` | Registering as new worker | `[ab12] JOIN: Registering as active worker` |
| `CLAIM` | Claiming a page | `[ab12] CLAIM: Page 42` |
| `PROGRESS` | Partial progress (optional) | `[ab12] PROGRESS: Page 42 50% done` |
| `DONE` | Completed a page | `[ab12] DONE: Page 42` |
| `RECLAIM` | Took over from stalled worker | `[ab12] RECLAIM: Page 42 from ef56` |
| `HEARTBEAT` | Idle heartbeat | `[ab12] HEARTBEAT` |
| `SYNC` | Manual sync update | `[ab12] SYNC: Updated team awareness` |
| `OFFLINE` | Going offline intentionally | `[ab12] OFFLINE: Taking a break` |
| `BACK` | Returning after offline | `[ab12] BACK: Resuming work` |

### Examples

```bash
# Claiming page
git commit -m "[ab12] CLAIM: Page 42
HEARTBEAT: $(date +%s)"

# Completing page
git commit -m "[ab12] DONE: Page 42
HASH: a8f3b2c1
HEARTBEAT: $(date +%s)"

# Reclaiming from stalled worker
git commit -m "[ab12] RECLAIM: Page 42 from ef56 (stalled 18min)
HEARTBEAT: $(date +%s)"

# Heartbeat while working (if no commits in 5min)
git commit -m "[ab12] HEARTBEAT
STATUS: Translating page 42, 70% done
HEARTBEAT: $(date +%s)"
```

---

## Communication Patterns

### Pull Frequency

| Phase | Daemon Sync | Manual Pull (if needed) |
|-------|-------------|-------------------------|
| Setup | Every 60s (daemon) | Every 2min |
| Translation | Every 60s (daemon) | Every 5min |
| Finishing | Every 30s (daemon) | Every 2min |

### Push Frequency

| Event | Push Timing |
|-------|-------------|
| Claim page | Immediately (<5 sec) |
| Complete page | Immediately (<5 sec) |
| Progress update | Every 15 minutes (optional) |
| Heartbeat (if idle) | Every 5 minutes |
| Error/blocker | Immediately |

### Sync Loop

```
┌─────────────────────────────────────────────────┐
│  [DAEMON runs every 60s]                        │
│  1. Fetch all branches                          │
│  2. Read all WORKER_STATE.md files              │
│  3. Detect stalled workers                      │
│  4. Update .sync/global_state.json              │
│                                                  │
│  [YOUR work loop]                               │
│  1. Query daemon for next page                  │
│  2. Claim page (commit+push)                    │
│  3. Translate page                              │
│  4. Complete page (commit+push)                 │
│  5. Repeat                                      │
└─────────────────────────────────────────────────┘
```

---

## Emergency Protocols

### Can't Push (Branch Diverged)

```bash
# 1. Try rebase
git pull --rebase origin HEAD

# 2. If conflicts, resolve and continue
git rebase --continue

# 3. Push again
git push origin HEAD

# 4. If still failing, force sync and re-claim
python3 tools/sync_daemon.py --sync-now
# Re-claim next page
```

### Sync Daemon Crashed

```bash
# 1. Restart daemon
python3 tools/sync_daemon.py --stop
python3 tools/sync_daemon.py --start &

# 2. Force immediate sync
python3 tools/sync_daemon.py --sync-now

# 3. Verify global state
python3 tools/sync_daemon.py --status
```

### Detected Duplication

```bash
# If you discover another worker already translated your page:

# 1. Check hashes
sha256sum translations/page_42.json
git show "origin/OTHER_BRANCH:translations/page_42.json" | sha256sum

# 2. If hashes match: Keep one, delete other
# 3. If hashes differ: Keep better quality one, note in WORKER_STATE.md

# 4. Update your WORKER_STATE.md
# Remove page from completed, mark as "duplicate_deleted"

# 5. Continue with next page
```

### All Pages Claimed But Book Not Done

```bash
# This happens if workers are slow or stalled

# 1. Check for stalled workers
python3 tools/sync_daemon.py --status

# 2. If stalled workers found, wait 15min then reclaim

# 3. If no stalled workers, wait for them to finish

# 4. If a worker is taking too long (>1 hour per page):
#    - Check their WORKER_STATE.md notes
#    - Offer help
#    - Consider reclaiming if truly stalled
```

---

## Performance Metrics

### Individual Agent Metrics

Track in your WORKER_STATE.md:
- **Pages completed**: Total count
- **Average time per page**: Minutes
- **Success rate**: Pages done / pages claimed (should be ~100%)
- **Reclaim rate**: Pages reclaimed from you (should be ~0%)

### Team Metrics

The sync daemon reports:
```bash
python3 tools/sync_daemon.py --team-stats

# Output:
# Total pages: 99
# Completed: 67 (67.7%)
# In progress: 12 (12.1%)
# Available: 20 (20.2%)
#
# Active workers: 14
# Average pages per worker: 4.8
# Fastest worker: ab12 (12 pages, 3.5 pages/hour)
# Slowest worker: gh78 (2 pages, 0.6 pages/hour)
# Duplication detected: 0 pages ✓
#
# Estimated completion: 4.2 hours (at current rate)
```

### Success Criteria

The protocol is working correctly when:
- ✅ **Zero duplication**: No page translated more than once
- ✅ **All workers active**: >80% of registered workers have completed >1 page
- ✅ **Balanced workload**: Std dev of pages/worker <30% of mean
- ✅ **Fast progress**: Book completed in <12 hours with 16 workers
- ✅ **No stalls**: <5% of claimed pages need reclaiming

---

## Comparison: Old vs New Protocol

| Aspect | Old Protocol | New Protocol |
|--------|-------------|--------------|
| **Startup time** | 30+ minutes (consensus) | <60 seconds |
| **Duplication** | 83% waste observed | 0% (daemon prevents) |
| **Worker utilization** | 25% (4/16 agents) | >80% target |
| **Sync mechanism** | Manual git pull | Automated daemon |
| **Claim validation** | None | Pre-claim check mandatory |
| **Stall recovery** | None | Automatic after 15min |
| **Workload balance** | Random | Active monitoring |
| **Communication** | Pull-based, slow | Daemon-based, fast |
| **Consensus** | Required for setup | First-in wins |
| **Complexity** | High (M0/M1/M2/M3) | Low (just translate) |

---

## Implementation Checklist

For this protocol to work, you need:

- [ ] `WORKER_STATE_TEMPLATE.md` (template for worker registration)
- [ ] `tools/sync_daemon.py` (the sync daemon)
- [ ] `tools/claim_page.sh` (helper script for claiming)
- [ ] `tools/complete_page.sh` (helper script for completion)
- [ ] `.gitignore` entry for `.sync/` (daemon's local cache)

See `IMPLEMENTATION.md` for detailed implementation guide.

---

## Appendix: Lessons from Previous Failures

### 16-Agent Book Translation (83% Waste)

**What went wrong:**
- No sync daemon → agents worked blind
- No pre-claim validation → massive duplication  
- Complex consensus → 12 agents stuck in setup
- No reclaiming → 1 agent did 18 pages alone

**What we learned:**
- Sync daemon is MANDATORY, not optional
- Simple beats complex (first-in wins > consensus)
- Aggressive reclaiming keeps all agents productive
- Real-time validation prevents all duplication

### Hong Lou Meng Translation (Reference)

**What worked:**
- Mandatory sync daemon (emphasized in all-caps)
- Pre-claim page checking
- Simple work unit (one page = one task)
- Clear heartbeat protocol

**What we adopted:**
- All of the above
- Plus: Workload balancing
- Plus: Simplified setup (no consensus)
- Plus: Better stall recovery

---

## Quick Reference Commands

```bash
# Get your identity
MY_SHORT_ID=$(git branch --show-current | grep -oE '[^-]+$' | tail -c 5)

# Start sync daemon (MANDATORY)
python3 tools/sync_daemon.py --start &

# Get next page
NEXT_PAGE=$(python3 tools/sync_daemon.py --next-page)

# Check if page is available
python3 tools/sync_daemon.py --check-page 42

# Claim page
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] CLAIM: Page $PAGE
HEARTBEAT: $(date +%s)"
git push origin HEAD

# Complete page
git add translations/page_$PAGE.json WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] DONE: Page $PAGE
HASH: $(sha256sum translations/page_$PAGE.json | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD

# Check team status
python3 tools/sync_daemon.py --status

# Check reclaimable pages
python3 tools/sync_daemon.py --reclaimable

# Force sync now
python3 tools/sync_daemon.py --sync-now
```

---

**This protocol is designed for high-performance parallel translation with zero waste. Follow it strictly for best results.**
