# Collaborative Translation Protocol

## Overview

This protocol enables multiple AI agents to work **collaboratively** on translating the Durov Code book. Workers communicate via git, share progress, and dynamically distribute workload. The protocol is designed to be robust against worker disconnection and reconnection.

**Key Philosophy**: Workers are a team, not isolated freelancers. They know who else is working, what pages are claimed, and can adapt when workers join or leave.

---

## Core Concepts

### 1. Worker Identity
- **Branch Name**: Your full branch (e.g., `cursor/some-task-abc123`)
- **Short ID**: Last 4 characters of branch name (e.g., `c123`)
- **Registration**: Creating `WORKER_STATE.md` on your branch registers you as active

### 2. Communication via Git
| Action | Meaning |
|--------|---------|
| Commit + Push | Broadcast your state to the team |
| Fetch + Read other branches | Receive team updates |
| WORKER_STATE.md | Your live status file |

### 3. Heartbeat System
- Workers must include a **Unix timestamp** in every commit
- Heartbeat in WORKER_STATE.md must be updated at least every **5 minutes**
- Workers with stale heartbeats (>10 minutes) are considered **offline**

---

## The Sync Loop

Every worker follows this loop continuously:

```
┌─────────────────────────────────────────────────────────────┐
│  1. SYNC: Fetch all branches, discover active workers       │
│  2. BUILD PICTURE: Who's online? What pages are claimed?    │
│  3. CLAIM: If I need a page, claim the lowest available     │
│  4. TRANSLATE: Work on my claimed page                      │
│  5. BROADCAST: Commit & push my progress                    │
│  6. REPEAT every 2-3 minutes                                │
└─────────────────────────────────────────────────────────────┘
```

**Sync frequency**: Every 2-3 minutes (or after completing each page)

---

## Worker Discovery

### Identifying Yourself
```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_SHORT_ID on $MY_BRANCH"
```

### Discovering All Active Workers
```bash
git fetch origin --prune

# Find all cursor/* branches with WORKER_STATE.md
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null 2>&1; then
    short_id=$(echo "$branch" | grep -oE '[^-]+$' | tail -c 5)
    heartbeat=$(git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | grep -oP 'Heartbeat: \K[0-9]+' | head -1)
    echo "Active: $short_id ($branch) - Heartbeat: $heartbeat"
  fi
done
```

### Counting Online Workers
A worker is **online** if:
1. They have `WORKER_STATE.md` on their branch
2. Their heartbeat is less than 10 minutes old

Workers with heartbeats older than 10 minutes are considered **offline** (may have lost connection).

---

## Page Assignment

### Simple Rule: Claim the Lowest Available Page

```python
# Pseudocode for page claiming
def get_next_page():
    all_pages = set(range(1, 100))  # Pages 1-99
    
    # Read all active workers' states
    claimed = set()      # Pages currently being translated
    completed = set()    # Pages already done (translation exists)
    
    for worker in active_workers:
        claimed.update(worker.claimed_pages)
        completed.update(worker.completed_pages)
    
    # Also check translations/ directory for completed work
    for file in translations/*.json:
        completed.add(file.page_number)
    
    available = sorted(all_pages - claimed - completed)
    return available[0] if available else None
```

### Claim Protocol

1. **Sync first**: Always fetch and read other workers' states before claiming
2. **Claim one page**: Update WORKER_STATE.md with your claimed page
3. **Push immediately**: Make your claim visible to others
4. **Verify**: Re-fetch to check for conflicts (rare but possible)

### Conflict Resolution
If two workers claim the same page (race condition):
- **Earlier timestamp wins** (commit timestamp)
- Losing worker should re-sync and claim next available page
- This is rare with proper sync discipline

---

## WORKER_STATE.md Format

Each worker maintains this file on their branch:

```markdown
# Worker: [SHORT_ID]

## Status
- **Branch**: [full branch name]
- **Short ID**: [4 chars]
- **Heartbeat**: [Unix timestamp]
- **Status**: online | translating | idle

## Current Work
- **Claimed Page**: [page number or "none"]
- **Started At**: [timestamp when started this page]

## Completed Pages
| Page | Completed At | Hash |
|------|--------------|------|
| 13   | 1735689600   | a8f3b2c1 |
| 14   | 1735690200   | c9d4e5f6 |

## Known Workers (Last Sync)
| Short ID | Status | Claimed Page | Last Heartbeat |
|----------|--------|--------------|----------------|
| abc1     | online | 15           | 1735689900     |
| def2     | online | 16           | 1735689850     |
| ghi3     | offline| 17           | 1735685000     |

## Notes
[Any messages for the team]
```

---

## Handling Worker Disconnection

### Detecting Offline Workers
When you sync, check each worker's heartbeat:
```bash
current_time=$(date +%s)
worker_heartbeat=1735685000  # From their WORKER_STATE.md

age=$((current_time - worker_heartbeat))
if [ $age -gt 600 ]; then  # 600 seconds = 10 minutes
    echo "Worker is OFFLINE (stale heartbeat)"
fi
```

### Reclaiming Pages from Offline Workers
If a worker has been offline for **15+ minutes** and has a claimed page:
1. Their page becomes available for reclaiming
2. Any online worker can claim it
3. Note in your WORKER_STATE.md: "Reclaimed page X from [offline_worker]"

### What the Returning Worker Should Do
When a worker comes back online after being disconnected:
1. **Sync first**: Fetch all branches, read all states
2. **Check your old page**: Is it still yours or was it reclaimed?
3. **If reclaimed**: Claim the next available page, continue working
4. **If still yours**: Continue where you left off
5. **Update heartbeat**: Push immediately to show you're back

---

## Handling Worker Reconnection

### New Worker Joining
When a new worker starts:
1. Create WORKER_STATE.md (registers you as active)
2. Sync to discover existing workers
3. Build global picture (who has what)
4. Claim lowest available page
5. Start translating

### Existing Workers Noticing New Worker
During regular sync, workers will naturally discover new workers:
1. Fetch shows new branch with WORKER_STATE.md
2. Add to "Known Workers" table
3. No special action needed - workload auto-balances

### Workload Rebalancing
Workload naturally rebalances as workers join/leave:
- New workers take the lowest available pages
- When a worker finishes a page, they take the next lowest available
- No explicit "rebalancing" needed - it's emergent

---

## Commit Message Format

Use this format for machine-readable commits:

```
[SHORT_ID] ACTION: Description
HEARTBEAT: [unix timestamp]
```

### Action Types

| Action | When to Use |
|--------|-------------|
| `SYNC` | Starting session, syncing with team |
| `CLAIM` | Claiming a page to translate |
| `PROGRESS` | Partial progress on a page |
| `DONE` | Completed a page translation |
| `RECLAIM` | Taking over an abandoned page |

### Examples
```bash
# Starting session
git commit -m "[c123] SYNC: Starting session, discovering workers
HEARTBEAT: $(date +%s)"

# Claiming a page
git commit -m "[c123] CLAIM: Starting page 15
HEARTBEAT: $(date +%s)"

# Completing a page
git commit -m "[c123] DONE: Completed page 15
HASH: a8f3b2c1
HEARTBEAT: $(date +%s)"
```

---

## Work Product Sharing

### Translation Files
Completed translations go in `translations/page_XXX.json`:
```
translations/
├── page_001.json
├── page_002.json
└── ...
```

### Syncing Work Products
When you complete a page:
1. Save `translations/page_XXX.json`
2. Commit with DONE message
3. Push to your branch

Other workers can see your completed pages by:
```bash
# Check what translations exist on another worker's branch
git show "origin/$other_branch:translations/page_015.json" 2>/dev/null
```

### Aggregating All Work
At the end, all translations can be collected from all worker branches:
```bash
for branch in $(git branch -r | grep 'origin/cursor/'); do
  for page in $(seq 1 99); do
    file="translations/page_$(printf '%03d' $page).json"
    if git show "origin/${branch}:$file" &>/dev/null 2>&1; then
      echo "Found page $page on $branch"
    fi
  done
done
```

---

## Quick Reference Commands

### Startup Sequence
```bash
# 1. Identify yourself
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)

# 2. Create WORKER_STATE.md (copy from template, fill in your info)
cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
# Edit WORKER_STATE.md with your details

# 3. Sync and discover
git fetch origin --prune
# Read other workers' states...

# 4. Register yourself
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: Registering as active worker
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Regular Sync (Every 2-3 Minutes)
```bash
# Fetch all branches
git fetch origin --prune

# Read each active worker's state
for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | head -30
done
```

### Claim a Page
```bash
# Update WORKER_STATE.md with your claim
# Then:
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] CLAIM: Starting page 15
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

### Complete a Page
```bash
git add translations/page_015.json WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] DONE: Completed page 15
HASH: $(sha256sum translations/page_015.json | cut -c1-8)
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

---

## Timeouts and Thresholds

| Situation | Threshold | Action |
|-----------|-----------|--------|
| Sync frequency | 2-3 min | Fetch and read other workers |
| Heartbeat update | 5 min max | Push a commit to stay "online" |
| Worker considered offline | 10 min | Not included in workload calc |
| Page can be reclaimed | 15 min | Other workers can take it |
| Push after claiming | Immediate | Don't start without pushing |

---

## Anti-Patterns to Avoid

| Don't Do This | Do This Instead |
|---------------|-----------------|
| Claim multiple pages at once | Claim one page, finish it, claim next |
| Skip syncing before claiming | Always sync first |
| Forget to push claims | Push immediately after claiming |
| Let heartbeat go stale | Commit at least every 5 min |
| Ignore offline workers | Reclaim their pages after 15 min |
| Work in isolation | Sync regularly, share progress |

---

## Protocol Summary

1. **Everyone knows everyone**: Regular syncs keep global awareness
2. **Simple page assignment**: Lowest available page number
3. **Heartbeats keep us honest**: Stale = offline
4. **Graceful disconnection**: Pages get reclaimed, no work lost
5. **Easy reconnection**: Sync, check status, claim new page
6. **Work products shared**: Translations visible on each branch

This protocol ensures the team works together efficiently while being robust against the realities of distributed systems (workers come and go, connections drop, etc.).
