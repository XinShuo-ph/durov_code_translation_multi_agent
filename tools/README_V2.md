# Multi-Agent Protocol V2 Tools

This directory contains tools that implement and enforce the Multi-Agent Parallel Protocol V2.

## Overview

These tools solve the critical coordination problems observed in previous multi-agent translation sessions:
- **Problem 1**: Only 3/16 agents did meaningful work (first wave)
- **Problem 2**: One agent completed 85+ pages alone while others sat idle
- **Problem 3**: No real-time coordination led to gaps and duplicates

**V2 Solution**: Automatic synchronization, quota enforcement, and gap-first claiming.

## Quick Start

```bash
# 1. Start sync daemon (MANDATORY - do this first!)
python3 tools/sync_daemon.py --start --interval 60 &

# 2. Wait for initial sync
sleep 30

# 3. Check if you can work
python3 tools/check_quota.py

# 4. Claim next page (gap-first priority)
python3 tools/claim_page.py --claim-next

# 5. Do translation work...
# (your translation code here)

# 6. Mark page as complete
python3 tools/update_worker_state.py --complete 42 --commit

# 7. Monitor overall health
python3 tools/monitor_load.py
```

## Tools Reference

### 1. sync_daemon.py - Continuous Synchronization

**Purpose**: Fetches all worker branches every 60 seconds and builds global state.

**Critical**: This prevents the 83% wasted effort seen in previous sessions where workers translated the same pages.

```bash
# Start daemon (run in background)
python3 tools/sync_daemon.py --start --interval 60 &

# Check if running
python3 tools/sync_daemon.py --status

# Force immediate sync
python3 tools/sync_daemon.py --sync-now

# Stop daemon
python3 tools/sync_daemon.py --stop
```

**Output**: `.sync_cache/global_state.json` - contains:
- All workers' status, heartbeats, claimed/completed pages
- Available pages, gaps, reclaimable pages
- Summary statistics

**Logs**: `.sync_cache/sync.log`

### 2. claim_page.py - Smart Page Claiming

**Purpose**: Claim pages with gap-first priority and quota enforcement.

**Features**:
- Automatically finds gaps in page sequence
- Checks quota before allowing claim
- Detects conflicts (rare with sync daemon)
- Updates WORKER_STATE.md and commits immediately

```bash
# Show next page without claiming
python3 tools/claim_page.py --get-next
# Output: Page 13 (gap)

# Claim next page (gap-first)
python3 tools/claim_page.py --claim-next

# Claim specific page
python3 tools/claim_page.py --claim 42

# Claim sequential (skip gaps)
python3 tools/claim_page.py --claim-next --no-gaps

# Release a claim (can't complete it)
python3 tools/claim_page.py --release 42

# Override quota check (use with caution)
python3 tools/claim_page.py --claim-next --force
```

**Priority order**:
1. Reclaimable pages (from offline workers)
2. Gaps (pages where lower AND higher pages are completed)
3. Lowest unclaimed sequential page

### 3. check_quota.py - Fair Work Distribution

**Purpose**: Ensure no worker does >25% more than fair share.

**Formula**: 
- Fair share = `total_pages / online_workers`
- Max allowed = `fair_share + 20% buffer`
- Example: 100 pages, 10 workers → fair_share=10, max=12

```bash
# Full quota report
python3 tools/check_quota.py

# Just print status (for scripts)
python3 tools/check_quota.py --status-only
# Output: AT_TARGET | BELOW_TARGET | NEAR_LIMIT | OVER_LIMIT

# Exit code check (for scripting)
python3 tools/check_quota.py --can-work
echo $?  # 0 = can work, 1 = over quota
```

**Status levels**:
- `BELOW_TARGET`: <(fair_share - 2) pages → Claim aggressively
- `AT_TARGET`: Within ±2 of fair_share → Normal claiming
- `NEAR_LIMIT`: Above fair_share but below max → Prefer gaps
- `OVER_LIMIT`: ≥max pages → STOP, wait for others

### 4. monitor_load.py - Real-time Dashboard

**Purpose**: Visualize work distribution and identify problems.

```bash
# Full dashboard
python3 tools/monitor_load.py

# Compact one-line view
python3 tools/monitor_load.py --compact

# JSON output (for scripts/automation)
python3 tools/monitor_load.py --json
```

**Shows**:
- Worker status table (online/offline, completed, claimed, quota status)
- Load distribution statistics (std deviation)
- Gaps in page sequence
- Recommendations (who should pause, who should claim more)

**Example output**:
```
================================================================================
MULTI-AGENT LOAD DISTRIBUTION DASHBOARD
================================================================================

Last sync: 45s ago
Total pages: 99
Completed: 42 (42.4%)
Claimed: 5
Available: 52
Gaps: 3

Status: ⚠️  ISSUES DETECTED
  - High load imbalance: 28.5% deviation

Load distribution: 28.5% std deviation ⚠️
Average pages/worker: 6.0

================================================================================
WORKER STATUS
--------------------------------------------------------------------------------
Worker   Status   Done   Claimed    Heartbeat    Quota       
--------------------------------------------------------------------------------
c68e     online ✓ 15     [16]       2m ago       OVER 🛑
14ce     online ✓ 10     []         3m ago       OK ✅
c3ab     online ✓ 8      []         5m ago       OK ✅
991c     online ✓ 4      []         8m ago       BELOW ⬇️
f6c8     online ✓ 3      []         6m ago       BELOW ⬇️
e5f7     offline ✗ 2      []         45m ago      -           
--------------------------------------------------------------------------------

GAPS IN PAGE SEQUENCE:
  13, 17, 23

================================================================================
RECOMMENDATIONS
--------------------------------------------------------------------------------
⏸️  Workers should PAUSE (over quota): c68e
⚡ Workers should CLAIM MORE: 991c, f6c8
🔍 Focus on GAPS first: 3 gaps need filling
⚠️  Offline workers: e5f7
================================================================================
```

### 5. update_worker_state.py - State Management

**Purpose**: Update WORKER_STATE.md fields without manual editing.

```bash
# Move page from claimed to completed
python3 tools/update_worker_state.py --complete 42

# Update status field
python3 tools/update_worker_state.py --set-status idle

# Update heartbeat only
python3 tools/update_worker_state.py --heartbeat

# Commit and push after update
python3 tools/update_worker_state.py --complete 42 --commit
```

**Use cases**:
- Mark page complete after translation
- Update status when pausing/resuming
- Keep heartbeat alive during long operations

### 6. metrics.py - Protocol Health Monitoring

**Purpose**: Track protocol effectiveness and health.

```bash
# Full health report
python3 tools/metrics.py --report

# Set baseline (do this at project start)
python3 tools/metrics.py --baseline

# JSON output
python3 tools/metrics.py --json
```

**Metrics tracked**:
- **Load distribution**: Std deviation of pages/worker (target: <15%)
- **Gap percentage**: Gaps as % of completed pages (target: <5%)
- **Worker participation**: % of workers online (target: >85%)
- **Coverage rate**: Pages/hour vs baseline (target: 100%+)

**Health scoring**:
- 90-100: HEALTHY ✅
- 70-89: FAIR ⚠️
- 50-69: POOR ⚠️
- <50: CRITICAL 🛑

**Example output**:
```
================================================================================
PROTOCOL HEALTH REPORT
================================================================================

Overall Status: ✅ HEALTHY
Health Score: 92/100

================================================================================
DETAILED METRICS
--------------------------------------------------------------------------------
Load Distribution:
  Standard Deviation: 2.3 pages
  Deviation %: 12.5% ✅ Excellent
  Average pages/worker: 8.5

Gap Coverage:
  Gap count: 2
  Gap %: 3.2% ✅ Excellent

Worker Participation:
  Online workers: 14/16
  Participation %: 87.5% ✅ Excellent

Coverage Rate:
  Current rate: 8.2 pages/hour
  vs Baseline: 105.0% ✅ Excellent

Project Completion:
  Pages: 68/99
  Progress: 68.7%
  [█████████████████████████████████░░░░░░░░░░░░░░░░░] 68.7%
================================================================================
```

## Workflow Integration

### Recommended Work Loop

```bash
#!/bin/bash
# work_loop.sh - Automated multi-agent work loop

set -e

# Ensure sync daemon is running
if ! python3 tools/sync_daemon.py --status &>/dev/null; then
  python3 tools/sync_daemon.py --start --interval 60 &
  sleep 30
fi

while true; do
  # Check quota
  if ! python3 tools/check_quota.py --can-work; then
    echo "⏸️  Over quota, waiting 5 minutes..."
    sleep 300
    continue
  fi
  
  # Get next page
  NEXT_PAGE=$(python3 tools/claim_page.py --get-next)
  if [ -z "$NEXT_PAGE" ]; then
    echo "✅ All pages claimed or completed!"
    break
  fi
  
  # Claim it
  if ! python3 tools/claim_page.py --claim-next; then
    echo "❌ Failed to claim page"
    sleep 60
    continue
  fi
  
  # Extract page number from output
  PAGE_NUM=$(echo "$NEXT_PAGE" | grep -oE '[0-9]+' | head -1)
  
  # Do translation (your script here)
  echo "🔄 Translating page $PAGE_NUM..."
  # python3 translate.py $PAGE_NUM
  
  # Mark complete
  python3 tools/update_worker_state.py --complete $PAGE_NUM --commit
  
  echo "✅ Page $PAGE_NUM complete"
  
  # Small delay to avoid race conditions
  sleep 10
done

echo "🎉 Work complete!"
```

## Cache Directory

All tools use `.sync_cache/` for coordination:

```
.sync_cache/
├── global_state.json    # Current state of all workers
├── baseline.json        # Baseline metrics for comparison
├── sync.log            # Sync daemon logs
└── daemon.pid          # Sync daemon process ID
```

**Important**: Do NOT commit `.sync_cache/` to git - it's ephemeral state.

Add to `.gitignore`:
```
.sync_cache/
```

## Troubleshooting

### "Global state not found"

**Problem**: Sync daemon not running.

**Solution**:
```bash
python3 tools/sync_daemon.py --start --interval 60 &
sleep 30
```

### "Over quota" but other workers inactive

**Problem**: Quota calculated with offline workers.

**Solution**: Wait 15 minutes - offline workers will be removed from calculation automatically.

Or check status:
```bash
python3 tools/monitor_load.py
# See which workers are offline
```

### Daemon appears stuck

**Problem**: Daemon process crashed but PID file remains.

**Solution**:
```bash
rm -rf .sync_cache/
python3 tools/sync_daemon.py --start --interval 60 &
```

### Duplicate translations

**Problem**: CRITICAL - sync completely broken.

**Solution**:
1. All workers STOP immediately
2. Verify daemon on each worker: `python3 tools/sync_daemon.py --status`
3. Restart daemon on all workers
4. Wait 2 minutes for sync
5. Resume work

## Performance Tips

### Optimize Sync Interval

Default is 60 seconds. Adjust based on needs:

```bash
# Fast-paced work (many workers, small pages)
python3 tools/sync_daemon.py --start --interval 30 &

# Slower work (few workers, large pages)
python3 tools/sync_daemon.py --start --interval 90 &
```

**Tradeoff**: Shorter interval = better coordination, more git fetches.

### Monitor Health Regularly

Set up periodic monitoring:

```bash
# Add to crontab
*/10 * * * * cd /path/to/project && python3 tools/monitor_load.py --compact >> load.log
```

### Baseline Early

Set baseline after first hour of work:

```bash
# After ~1 hour
python3 tools/metrics.py --baseline

# Then check regularly
python3 tools/metrics.py --report
```

## Architecture Notes

### Why a Daemon?

Previous protocol (V1) relied on manual syncing every 2-3 minutes. In practice:
- Agents forgot to sync
- Manual sync was inconsistent
- Led to 83% duplicate work

V2 daemon ensures:
- Automatic, consistent syncing
- No human/agent forgetfulness
- Real-time global state

### Why Quotas?

Previous sessions showed extreme imbalance:
- 3 workers did 234/386 pages (60%)
- One worker did 85 pages alone
- Many workers sat idle

Quotas enforce fairness:
- All workers contribute
- No single worker overloaded
- Better parallelization

### Why Gap-First?

Pages should form continuous sequence for:
- Easier review
- Better reader experience
- Earlier detection of coverage issues

Gap-first claiming ensures:
- Minimal gaps in final output
- Quick identification of problem areas
- Continuous coverage

## Testing

Test the tools before starting work:

```bash
# 1. Start daemon
python3 tools/sync_daemon.py --start --interval 60 &
sleep 30

# 2. Check status
python3 tools/sync_daemon.py --status

# 3. View global state
cat .sync_cache/global_state.json

# 4. Check quota
python3 tools/check_quota.py

# 5. Get next page (don't claim)
python3 tools/claim_page.py --get-next

# 6. Monitor
python3 tools/monitor_load.py

# 7. Stop daemon
python3 tools/sync_daemon.py --stop
```

## Migration from V1

If migrating from V1 protocol:

```bash
# 1. All workers: Install new tools
git fetch origin
git checkout origin/cursor/agent-collaboration-protocol-c94a -- tools/

# 2. All workers: Start daemon
python3 tools/sync_daemon.py --start --interval 60 &
sleep 30

# 3. All workers: Check quota
python3 tools/check_quota.py

# 4. Resume work using new tools
python3 tools/claim_page.py --claim-next
```

## Support

For issues or questions:
- Check logs: `.sync_cache/sync.log`
- Run health check: `python3 tools/metrics.py --report`
- View load: `python3 tools/monitor_load.py`

## Version

Protocol V2.0
Tools last updated: 2026-02-12
