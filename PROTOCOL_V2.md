# Multi-Agent Parallel Protocol V2.0

## Executive Summary

This protocol enables **balanced, efficient** parallel work by multiple AI agents. It addresses critical failures from previous translation sessions where:
- Only 3/16 agents did meaningful work (first wave)
- Three agents completed 60% of work while others sat idle (second wave)
- No real-time coordination led to duplicate work and gaps

**Key Improvements over V1:**
1. **Mandatory sync daemon** for real-time coordination
2. **Load balancing enforcement** - agents stop when they've done their fair share
3. **Active gap detection** - prioritize filling gaps over claiming sequential pages
4. **Heartbeat monitoring** - automatic detection and recovery from stuck agents
5. **Work quotas** - prevent any agent from doing >25% more than average

---

## Core Principles

### 1. Fair Work Distribution
**Rule**: No agent should complete more than `CEILING(total_pages / active_agents) + 5` pages before others catch up.

**Example**: With 100 pages and 10 agents:
- Target per agent: 10 pages
- Maximum before pause: 15 pages
- Agent must wait for others to catch up before claiming more

### 2. Gap-First Claiming
Agents must claim pages in this priority order:
1. **Gaps** in page sequence (e.g., if pages 1-10, 15-20 exist, claim page 11-14)
2. **Lowest unclaimed** page number
3. **Reclaimed** from offline workers (>15min stale heartbeat)

### 3. Continuous Sync
- **Every 60 seconds**: Automatic sync via daemon
- **Before claiming**: Manual sync required
- **After completion**: Immediate push to broadcast

### 4. Visible Progress
All agents maintain and update:
- `WORKER_STATE.md` - real-time status
- Translation files in `translations/page_XXX.json`
- Heartbeat timestamp in every commit

---

## Quick Start (5 Steps)

```bash
# 1. Identify yourself
export MY_BRANCH=$(git branch --show-current)
export MY_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)

# 2. Start sync daemon (MANDATORY - do this first!)
python3 tools/sync_daemon.py --start --interval 60 &
sleep 30  # Wait for initial sync

# 3. Check your work quota
python3 tools/check_quota.py

# 4. Get next page to claim (automatically finds gaps/lowest)
NEXT_PAGE=$(python3 tools/claim_page.py --get-next)

# 5. Start working
python3 tools/claim_page.py --claim $NEXT_PAGE
# ... do translation work ...
git add translations/page_${NEXT_PAGE}.json WORKER_STATE.md
git commit -m "[$MY_ID] DONE: Completed page $NEXT_PAGE HEARTBEAT: $(date +%s)"
git push origin HEAD
```

---

## Architecture

### Component 1: Sync Daemon (MANDATORY)

**Purpose**: Prevent 83% wasted effort seen in previous sessions.

**Location**: `tools/sync_daemon.py`

**What it does**:
- Fetches all worker branches every 60 seconds
- Builds global state: who's online, what pages are claimed/completed
- Detects offline workers (stale heartbeat >10min)
- Makes pages available for reclaim from offline workers
- Writes cached state to `.sync_cache/global_state.json`

**Usage**:
```bash
# Start daemon (run this FIRST, before any work)
python3 tools/sync_daemon.py --start --interval 60 &

# Check sync status
python3 tools/sync_daemon.py --status

# Manual sync (daemon does this automatically)
python3 tools/sync_daemon.py --sync-now

# Stop daemon
python3 tools/sync_daemon.py --stop
```

**Output**: `.sync_cache/global_state.json`
```json
{
  "workers": [
    {"id": "14ce", "status": "online", "heartbeat": 1767246060, "claimed": [15], "completed": [8,10,11,12,14]},
    {"id": "c3ab", "status": "online", "heartbeat": 1767243720, "claimed": [], "completed": [7,8,9,10,11,12]}
  ],
  "pages": {
    "claimed": [15],
    "completed": [7,8,9,10,11,12,14],
    "available": [1,2,3,4,5,6,13,16,17,...],
    "gaps": [13]
  },
  "last_sync": 1767246100
}
```

### Component 2: Page Claiming Tool

**Purpose**: Enforce gap-first claiming and quota limits.

**Location**: `tools/claim_page.py`

**What it does**:
- Reads `.sync_cache/global_state.json`
- Checks your work quota (have you done your fair share?)
- Finds next page using gap-first priority
- Updates WORKER_STATE.md with claim
- Commits and pushes claim immediately

**Usage**:
```bash
# Get next page (doesn't claim, just shows)
python3 tools/claim_page.py --get-next
# Output: Page 13 (gap)

# Claim next page (updates state, commits, pushes)
python3 tools/claim_page.py --claim-next
# Output: Claimed page 13, pushed to origin

# Claim specific page
python3 tools/claim_page.py --claim 42
# Output: Claimed page 42, pushed to origin

# Release a claim (if you can't complete it)
python3 tools/claim_page.py --release 42
```

### Component 3: Quota Checker

**Purpose**: Ensure fair work distribution, prevent one agent from doing everything.

**Location**: `tools/check_quota.py`

**What it does**:
- Calculates fair share: `total_pages / active_workers`
- Checks how many pages you've completed
- Returns status: `can_work`, `at_limit`, `over_limit`
- Blocks claiming if you're >25% over fair share

**Usage**:
```bash
python3 tools/check_quota.py

# Output example:
# Total pages: 99
# Active workers: 10
# Fair share: 10 pages
# Your completed: 8 pages
# Status: CAN_WORK (2 pages below fair share)
# You can claim up to 12 pages (fair share + 20% buffer)

# Or if over quota:
# Status: OVER_LIMIT (15 pages, limit is 12)
# Please wait for other workers to catch up
# Estimated wait: 5-10 minutes
```

### Component 4: Load Balancing Monitor

**Purpose**: Visualize work distribution, identify stuck/inactive workers.

**Location**: `tools/monitor_load.py`

**What it does**:
- Reads global state
- Shows work distribution across all workers
- Highlights workers who are over/under quota
- Identifies offline/stuck workers

**Usage**:
```bash
python3 tools/monitor_load.py

# Output:
# === LOAD DISTRIBUTION ===
# Worker   Status   Completed  Claimed  Last Heartbeat  Quota Status
# 14ce     online   12         [15]     2m ago         OK (at target)
# c3ab     online   6          []       5m ago         BELOW (4 short)
# c68e     online   29         [30]     1m ago         OVER_QUOTA ⚠️
# f6c8     online   3          []       8m ago         BELOW (7 short)
# 991c     offline  4          []       45m ago        STALE ⚠️
# 
# Gaps: [13, 17, 23, 24, 25, 26, ...]
# Recommendation: Focus on gaps, c68e should pause, c3ab and f6c8 should claim more
```

---

## Detailed Workflow

### Phase 1: Startup (Once per session)

```bash
#!/bin/bash
set -e

# 1. Identify yourself
export MY_BRANCH=$(git branch --show-current)
export MY_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am worker: $MY_ID"

# 2. Create WORKER_STATE.md if not exists
if [ ! -f WORKER_STATE.md ]; then
  cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
  sed -i "s/\[SHORT_ID\]/$MY_ID/g" WORKER_STATE.md
  sed -i "s|\[full branch name\]|$MY_BRANCH|g" WORKER_STATE.md
fi

# 3. Start sync daemon (CRITICAL!)
python3 tools/sync_daemon.py --start --interval 60 &
echo "Sync daemon started, waiting for initial sync..."
sleep 30

# 4. Initial sync and registration
git fetch origin --prune
git add WORKER_STATE.md
git commit -m "[$MY_ID] SYNC: Starting session, registering worker HEARTBEAT: $(date +%s)"
git push origin HEAD

echo "✓ Startup complete. Ready to work."
```

### Phase 2: Work Loop (Continuous)

```bash
#!/bin/bash
set -e

while true; do
  # 1. Check quota - am I allowed to work?
  QUOTA_STATUS=$(python3 tools/check_quota.py --status-only)
  
  if [ "$QUOTA_STATUS" = "OVER_LIMIT" ]; then
    echo "⏸️  Over quota, waiting for others to catch up..."
    sleep 300  # Wait 5 minutes
    continue
  fi
  
  # 2. Get next page (gap-first priority)
  NEXT_PAGE=$(python3 tools/claim_page.py --get-next)
  
  if [ -z "$NEXT_PAGE" ]; then
    echo "✅ All pages claimed or completed!"
    break
  fi
  
  echo "📄 Claiming page $NEXT_PAGE..."
  python3 tools/claim_page.py --claim $NEXT_PAGE
  
  # 3. Do the actual translation work
  # (Your translation script here)
  python3 tools/translate_page.py $NEXT_PAGE
  
  # 4. Verify translation was created
  if [ ! -f "translations/page_$(printf '%03d' $NEXT_PAGE).json" ]; then
    echo "❌ Translation failed for page $NEXT_PAGE"
    python3 tools/claim_page.py --release $NEXT_PAGE
    continue
  fi
  
  # 5. Update WORKER_STATE.md (move page from claimed to completed)
  python3 tools/update_worker_state.py --complete $NEXT_PAGE
  
  # 6. Commit and push immediately
  git add translations/page_$(printf '%03d' $NEXT_PAGE).json WORKER_STATE.md
  git commit -m "[$MY_ID] DONE: Completed page $NEXT_PAGE HASH: $(sha256sum translations/page_$(printf '%03d' $NEXT_PAGE).json | cut -c1-8) HEARTBEAT: $(date +%s)"
  git push origin HEAD
  
  echo "✅ Completed page $NEXT_PAGE"
  
  # Sync happens automatically via daemon
  # Small delay to avoid race conditions
  sleep 10
done

echo "🎉 Work complete!"
```

### Phase 3: Shutdown (End of session)

```bash
#!/bin/bash

# 1. Stop sync daemon
python3 tools/sync_daemon.py --stop

# 2. Final state update
python3 tools/update_worker_state.py --set-status idle
git add WORKER_STATE.md
git commit -m "[$MY_ID] SYNC: Ending session HEARTBEAT: $(date +%s)"
git push origin HEAD

echo "Session ended cleanly."
```

---

## WORKER_STATE.md Format (Enhanced)

```markdown
# Worker: [SHORT_ID]

## Status
- **Branch**: [full branch name]
- **Short ID**: [4 chars]
- **Heartbeat**: [Unix timestamp]
- **Status**: online | translating | idle | paused_over_quota
- **Session Started**: [timestamp]
- **Last Sync**: [timestamp]

## Work Quota
- **Completed Pages**: [count]
- **Fair Share**: [calculated]
- **Quota Status**: below_target | at_target | over_quota
- **Can Claim**: yes | no

## Current Work
- **Claimed Pages**: [array of page numbers]
- **Working On**: [page number or null]
- **Started At**: [timestamp]

## Completed Pages
| Page | Type | Completed At | Hash | Size |
|------|------|--------------|------|------|
| 13   | gap  | 1735689600   | a8f3b2c1 | 842 |
| 14   | seq  | 1735690200   | c9d4e5f6 | 756 |

Legend: Type = gap (filled a gap) | seq (sequential) | reclaim (from offline worker)

## Known Workers (Last Sync)
| Short ID | Status | Completed | Claimed | Quota | Last Heartbeat |
|----------|--------|-----------|---------|-------|----------------|
| abc1     | online | 12        | [15]    | OK    | 2m ago         |
| def2     | online | 8         | []      | BELOW | 3m ago         |
| ghi3     | offline| 4         | []      | -     | 47m ago        |

## Session Log
- 2026-01-01 04:30:00 - Session started
- 2026-01-01 04:35:00 - Claimed page 13 (gap)
- 2026-01-01 04:42:00 - Completed page 13
- 2026-01-01 04:45:00 - Claimed page 14
- 2026-01-01 04:52:00 - Completed page 14
- 2026-01-01 05:00:00 - Paused (over quota, waiting for others)
```

---

## Commit Message Format (Enforced)

All commits must follow this format for machine parsing:

```
[SHORT_ID] ACTION: Description
HEARTBEAT: [unix timestamp]
[Optional fields]
```

### Required Actions

| Action | When | Required Fields |
|--------|------|-----------------|
| `SYNC` | Starting session, periodic sync | `HEARTBEAT` |
| `CLAIM` | Claiming a page | `HEARTBEAT`, `PAGE` |
| `PROGRESS` | Mid-page update | `HEARTBEAT`, `PAGE`, `PERCENT` |
| `DONE` | Completed translation | `HEARTBEAT`, `PAGE`, `HASH` |
| `RELEASE` | Releasing a claim | `HEARTBEAT`, `PAGE`, `REASON` |
| `PAUSE` | Over quota, pausing | `HEARTBEAT`, `REASON` |

### Examples

```bash
# Starting
git commit -m "[c123] SYNC: Starting session, registering worker
HEARTBEAT: $(date +%s)"

# Claiming (gap)
git commit -m "[c123] CLAIM: Starting page 13 (gap)
HEARTBEAT: $(date +%s)
PAGE: 13
TYPE: gap"

# Progress update (optional, for long pages)
git commit -m "[c123] PROGRESS: Page 13 at 60%
HEARTBEAT: $(date +%s)
PAGE: 13
PERCENT: 60"

# Completion
git commit -m "[c123] DONE: Completed page 13
HEARTBEAT: $(date +%s)
PAGE: 13
HASH: a8f3b2c1
SIZE: 842"

# Releasing a claim (e.g., too difficult, need help)
git commit -m "[c123] RELEASE: Releasing page 13
HEARTBEAT: $(date +%s)
PAGE: 13
REASON: Complex poetry, need specialist"

# Pausing (over quota)
git commit -m "[c123] PAUSE: Over quota, waiting for others
HEARTBEAT: $(date +%s)
REASON: Completed 15 pages, fair share is 10"
```

---

## Quota System Details

### Calculating Fair Share

```python
total_pages = 99  # Or whatever the project has
online_workers = count_workers_with_heartbeat_under_10min()
fair_share = ceil(total_pages / online_workers)
buffer = ceil(fair_share * 0.2)  # 20% buffer
max_pages = fair_share + buffer
```

### Quota States

| State | Condition | Action |
|-------|-----------|--------|
| `BELOW_TARGET` | `completed < fair_share - 2` | Claim aggressively |
| `AT_TARGET` | `fair_share - 2 <= completed <= fair_share + 2` | Normal claiming |
| `NEAR_LIMIT` | `fair_share + 2 < completed < max_pages` | Claim cautiously, prefer gaps |
| `OVER_LIMIT` | `completed >= max_pages` | **STOP claiming**, wait for others |

### Grace Period

When you hit quota:
1. **Finish current page** (don't abandon mid-work)
2. **Wait 5 minutes** for sync to settle
3. **Recheck quota** (fair share may have changed if workers joined/left)
4. **If still over**: Wait another 5 minutes
5. **After 30 minutes over quota**: Switch to "helper" mode (review, quality check, documentation)

---

## Gap Detection Algorithm

Gaps are prioritized to ensure continuous page coverage.

```python
def find_gaps(completed_pages, total_pages):
    """
    Find gaps in page sequence.
    Priority: smallest gaps first (easier to fill).
    """
    all_pages = set(range(1, total_pages + 1))
    completed = set(completed_pages)
    unclaimed = sorted(all_pages - completed)
    
    gaps = []
    sequences = []
    
    for page in unclaimed:
        # Is this a gap? (i.e., completed pages exist both before and after)
        has_before = any(p < page for p in completed)
        has_after = any(p > page for p in completed)
        
        if has_before and has_after:
            gaps.append(page)
        else:
            sequences.append(page)
    
    # Return gaps first, then sequential pages
    return gaps + sequences
```

### Example

```
Completed: [1,2,3,7,8,9,15,16,17]
Unclaimed: [4,5,6,10,11,12,13,14,18,19,...]

Gaps: [4,5,6,10,11,12,13,14]  <- Priority
Sequential: [18,19,20,...]     <- After gaps filled
```

---

## Offline Worker Handling

### Detection

Worker is considered offline if:
```
current_time - worker.heartbeat > 600  # 10 minutes
```

### Reclaim Process

1. **15 minute grace period**: Pages claimed by offline worker are marked "at risk"
2. **After 15 minutes**: Pages become available for reclaim
3. **Reclaiming**: Use `--reclaim` flag
   ```bash
   python3 tools/claim_page.py --reclaim 42
   ```
4. **Notification**: Update WORKER_STATE.md with note
   ```
   Reclaimed page 42 from worker [abc1] (offline 47 minutes)
   ```

### Worker Returns Online

When previously offline worker comes back:
1. **Sync immediately**: `python3 tools/sync_daemon.py --sync-now`
2. **Check claimed pages**: Script will detect if they were reclaimed
3. **If reclaimed**: Automatically release claim, get next available page
4. **If still yours**: Continue where you left off

---

## Conflict Resolution

### Page Claim Conflict (Rare)

Two workers claim same page simultaneously (race condition).

**Resolution**:
1. **Earlier timestamp wins** (commit timestamp, not heartbeat)
2. Losing worker's claim is automatically released
3. Losing worker gets next available page
4. Tools handle this automatically:
   ```bash
   python3 tools/claim_page.py --claim 42
   # Output: Conflict detected on page 42, worker [abc1] claimed 12 seconds earlier
   #         Releasing your claim, getting next page...
   #         Claimed page 43 instead
   ```

### Duplicate Translation (Worse)

Two workers both complete same page (serious coordination failure).

**Resolution**:
1. **Earlier completion timestamp wins**
2. Later translation is moved to `duplicates/page_XXX_worker_YYY.json`
3. Losing worker is **NOT** credited for this page (doesn't count toward quota)
4. Alert sent to all workers:
   ```
   ⚠️  Duplicate detected: Page 42
   Winner: worker [abc1] (completed 2026-01-01 04:30:00)
   Duplicate: worker [def2] (completed 2026-01-01 04:35:00)
   This indicates a sync failure. All workers should restart sync daemon.
   ```

### Prevention

Duplicates should be **extremely rare** with V2 protocol:
- Sync daemon runs every 60 seconds
- Claims are pushed immediately (not batched)
- Tools check global state before every claim

If you see duplicates, **sync daemon is not running** - this is a critical failure.

---

## Performance Metrics

The protocol tracks these metrics to ensure health:

### Individual Worker Metrics

- **Pages per hour**: Track translation speed
- **Quota compliance**: % of time spent within quota
- **Sync frequency**: Actual vs expected (should be 60s)
- **Heartbeat regularity**: Gaps >5min are warnings

### System-Wide Metrics

- **Load distribution**: Std deviation of pages completed across workers
  - Target: <15% deviation
  - Warning: >25% deviation
  - Critical: >40% deviation (one worker doing too much)
- **Gap count**: How many gaps exist in page sequence
  - Target: <5% of completed pages
  - Warning: >10%
- **Duplicate rate**: Duplicates per 100 pages
  - Target: 0
  - Acceptable: <1
  - Critical: >2 (sync is broken)
- **Coverage rate**: Pages completed per hour (all workers combined)
  - Baseline: Measure in first hour
  - Warning: <50% of baseline (workers stuck or offline)

### Monitoring

```bash
python3 tools/metrics.py --report

# Output:
# === PROTOCOL HEALTH ===
# Active workers: 8
# Load distribution: 12% std dev ✓
# Gap count: 3 (4.2% of completed) ✓
# Duplicate rate: 0.0% ✓
# Coverage rate: 8.4 pages/hour (105% of baseline) ✓
# 
# Status: HEALTHY ✓
```

---

## Troubleshooting

### Issue: Worker stuck "over quota" for >30 minutes

**Diagnosis**: Other workers not claiming work.

**Solution**:
```bash
# Check if other workers are actually online
python3 tools/monitor_load.py

# If many workers are offline:
# - Wait for them to return, OR
# - Quota will recalculate without offline workers after 15 min
# - Recheck: python3 tools/check_quota.py
```

### Issue: Sync daemon crashed

**Symptoms**: No updates in `.sync_cache/global_state.json` for >2 minutes.

**Solution**:
```bash
# Check daemon status
python3 tools/sync_daemon.py --status

# If not running, restart
python3 tools/sync_daemon.py --start --interval 60 &

# Manual sync to catch up
python3 tools/sync_daemon.py --sync-now
```

### Issue: Cannot claim any page, but gaps exist

**Diagnosis**: Global state cache is stale.

**Solution**:
```bash
# Force sync
rm -rf .sync_cache
python3 tools/sync_daemon.py --sync-now

# Try claim again
python3 tools/claim_page.py --get-next
```

### Issue: Duplicate translations appearing

**Diagnosis**: **CRITICAL** - Sync is completely broken.

**Solution**:
1. **All workers STOP immediately**
2. Verify sync daemon is running: `python3 tools/sync_daemon.py --status`
3. If not running on ANY worker, this is the problem
4. Restart daemon on all workers
5. Wait 2 minutes for sync to settle
6. Resume work

### Issue: One worker doing everything

**Diagnosis**: Others are respecting quota, but this one is not.

**Solution**:
```bash
# Check if rogue worker is using tools
git log origin/cursor/ROGUE_BRANCH --oneline | grep "CLAIM\|DONE"

# If commits don't have proper format, worker is NOT using tools
# Contact that worker (if human-driven) or investigate why tools aren't running
```

---

## Migration from V1 to V2

If you have an existing V1 session:

### 1. Install new tools
```bash
git fetch origin
git checkout origin/cursor/agent-collaboration-protocol-c94a -- tools/
```

### 2. Start sync daemon (all workers)
```bash
python3 tools/sync_daemon.py --start --interval 60 &
```

### 3. Let sync settle (2 minutes)
```bash
sleep 120
```

### 4. Check your quota
```bash
python3 tools/check_quota.py
```

### 5. Resume work using new workflow
```bash
# Use tools instead of manual claiming
python3 tools/claim_page.py --claim-next
```

### 6. Monitor health
```bash
python3 tools/monitor_load.py
python3 tools/metrics.py --report
```

---

## Protocol Summary

### What's New in V2

| Feature | V1 | V2 |
|---------|----|----|
| Sync frequency | Manual (every 2-3 min) | Automatic (60s daemon) |
| Page claiming | Manual checking | Tool-enforced with gaps priority |
| Load balancing | None (honor system) | Enforced quotas with pause |
| Offline handling | Manual reclaim | Automatic after 15min |
| Duplicate prevention | Hope for the best | Sync daemon + immediate push |
| Monitoring | Manual log reading | Real-time dashboard |
| Gap detection | Manual scanning | Automatic, gap-first claiming |

### Success Criteria

A V2 session is successful if:
1. ✅ Load distribution std dev <15%
2. ✅ All workers complete within 20% of fair share
3. ✅ <5% gaps in final page sequence
4. ✅ Zero duplicates
5. ✅ >80% of workers active (not idle/offline)

### Expected Improvements

Based on V1 failures:
- **First wave**: 7/16 workers active → **Target**: 13-15/16 active
- **Load balance**: 3 workers did 60% → **Target**: Top 3 workers <40%
- **Duplicates**: Unknown (likely 5-10%) → **Target**: <1%
- **Gaps**: Unknown (likely 10-15%) → **Target**: <5%

---

## License

This protocol is released under MIT License. Use freely, improve, and share.

## Credits

- Based on collaborative translation protocol from StoneRecords project
- Enhanced with lessons learned from Durov Code book translation (16 multi-agent branches)
- Contributions from multiple AI agents across cursor/* branches
