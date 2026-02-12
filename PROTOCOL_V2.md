# Multi-Agent Parallel Protocol v2.0

> **Design Goal**: Enable 16+ AI agents to collaborate effectively with minimal duplication, automatic coordination, and graceful handling of worker joins/leaves.

## Critical Lessons from Previous Attempts

Previous multi-agent translation attempts suffered from:
- **40-60% work duplication** (same pages translated by multiple workers)
- **Poor participation** (only 3/16 workers contributing meaningfully)
- **Single-worker completion** (eventually one worker doing everything alone)

**Root Cause**: Manual sync protocols fail. Workers skip syncing, claim duplicate pages, and work in isolation.

**Solution**: Mandatory automation + validation + enforcement.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GLOBAL STATE (Git)                           │
│  - STATE.json: Canonical project state                          │
│  - worker-states/*.json: Individual worker status               │
│  - translations/*.json: Completed work products                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲ push/fetch
                              │
┌─────────────────────────────┼─────────────────────────────────────┐
│                        SYNC SERVICE                              │
│  - Auto-fetches every 30s                                        │
│  - Builds global state view                                      │
│  - Validates page claims                                         │
│  - Detects conflicts                                             │
│  - Manages work queue                                            │
└──────────────────────────────────────────────────────────────────┘
                              ▲
                              │ API calls
                              │
┌─────────────────────────────┼─────────────────────────────────────┐
│                        WORKER AGENT                              │
│  1. Start sync service (mandatory)                               │
│  2. Request next page via API                                    │
│  3. Claim page atomically                                        │
│  4. Translate page                                               │
│  5. Submit work + update state                                   │
│  6. Repeat                                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Setup (One-Time)

### For the First Worker

```bash
# Clone repo and create your branch
git checkout -b cursor/translation-work-XXXX

# Initialize global state (if not exists)
python3 tools/init_project.py

# This creates:
# - STATE.json (project-wide state)
# - worker-states/ (directory for worker states)
# - translations/ (directory for completed pages)

git add STATE.json worker-states/ translations/
git commit -m "Initialize multi-agent project"
git push -u origin HEAD
```

### For Subsequent Workers

```bash
# Create your branch
git checkout -b cursor/translation-work-YYYY

# Sync from main/primary branch
git fetch origin
git merge origin/main  # or wherever STATE.json lives

# You now have the current project state
```

---

## Phase 2: Work Loop (Continuous)

### Step 1: Start Sync Service (MANDATORY)

```bash
# Start the sync daemon in background
python3 tools/sync_service.py --start --worker-id XXXX

# This daemon:
# - Fetches all branches every 30 seconds
# - Aggregates all worker-states/*.json into memory
# - Tracks claimed, completed, available pages
# - Provides API endpoints for workers
```

**Workers MUST start sync service before claiming any work.**

### Step 2: Request Next Available Page

```bash
# Get next page assignment
NEXT_PAGE=$(python3 tools/sync_service.py --next-page)

# Returns: 
# - Page number (e.g., "42") if available
# - "NONE" if all pages claimed or completed
# - "ERROR: sync service not running" if daemon not started

if [ "$NEXT_PAGE" = "NONE" ]; then
    echo "No pages available. All work done or claimed."
    exit 0
fi
```

**How it works**:
- Daemon maintains global state of all pages (1-N)
- Tracks three sets: `claimed`, `completed`, `available`
- Returns `min(available)` - lowest unclaimed, uncompleted page
- Updates internal state (but doesn't commit yet)

### Step 3: Claim Page Atomically

```bash
# Claim the page (creates worker state + pushes)
python3 tools/sync_service.py --claim-page $NEXT_PAGE

# This does:
# 1. Updates worker-states/worker-XXXX.json with claim
# 2. git add worker-states/worker-XXXX.json
# 3. git commit -m "[XXXX] CLAIM: Page $NEXT_PAGE"
# 4. git push origin HEAD
# 5. Immediately re-fetches to check for conflicts
# 6. Returns SUCCESS or CONFLICT

# If CONFLICT detected:
#   - Another worker claimed same page with earlier timestamp
#   - Daemon automatically reverts claim
#   - Worker should request next page again
```

**Atomic Claim Protocol**:
```python
def claim_page(worker_id, page_num):
    # 1. Update worker state
    state = {
        "worker_id": worker_id,
        "claimed_page": page_num,
        "claim_time": time.time(),
        "status": "claiming"
    }
    
    # 2. Write to worker-states/
    write_json(f"worker-states/worker-{worker_id}.json", state)
    
    # 3. Git commit + push
    git_add(f"worker-states/worker-{worker_id}.json")
    git_commit(f"[{worker_id}] CLAIM: Page {page_num} at {state['claim_time']}")
    git_push()
    
    # 4. Immediate re-sync
    git_fetch_all()
    
    # 5. Validate claim
    all_claims = get_all_worker_states()
    conflicts = [w for w in all_claims 
                 if w['claimed_page'] == page_num 
                 and w['worker_id'] != worker_id]
    
    if conflicts:
        # Find earliest claim
        earliest = min([worker_id] + conflicts, 
                      key=lambda w: all_claims[w]['claim_time'])
        
        if earliest != worker_id:
            # We lost the race - revert
            revert_claim(worker_id)
            return "CONFLICT"
    
    # 6. We won - update status
    state['status'] = "translating"
    write_json(f"worker-states/worker-{worker_id}.json", state)
    git_add_commit_push("[{worker_id}] CLAIM CONFIRMED: Page {page_num}")
    
    return "SUCCESS"
```

### Step 4: Translate Page

```bash
# Worker does the actual translation work
# (This is the existing translation logic)

# Input: extracted/pages/page_042.txt
# Output: translations/page_042.json

python3 translate.py --page $NEXT_PAGE
```

### Step 5: Submit Work

```bash
# Submit completed translation
python3 tools/sync_service.py --complete-page $NEXT_PAGE \
    --translation-file translations/page_042.json

# This does:
# 1. Validates translation file exists and is valid JSON
# 2. Updates worker state: claimed_page = None, completed_pages += [42]
# 3. Updates global STATE.json: completed += [42]
# 4. git add translations/page_042.json worker-states/worker-XXXX.json STATE.json
# 5. git commit -m "[XXXX] DONE: Page 42 - <title>"
# 6. git push origin HEAD
```

### Step 6: Repeat

```bash
# Immediately get next page
# (Daemon already synced after submitting previous page)

NEXT_PAGE=$(python3 tools/sync_service.py --next-page)
# ... repeat from Step 3
```

---

## State Management

### Global State: `STATE.json`

**Single source of truth** for project status.

```json
{
  "project": "durov-code-translation",
  "total_pages": 99,
  "last_updated": 1767270000,
  "completed_pages": [1, 2, 3, 5, 8, 13],
  "claimed_pages": {
    "14": {
      "worker_id": "abc1",
      "claimed_at": 1767269500,
      "status": "translating"
    },
    "15": {
      "worker_id": "def2", 
      "claimed_at": 1767269600,
      "status": "translating"
    }
  },
  "available_pages": [4, 6, 7, 9, 10, 11, 12, 16, 17, 18, ...],
  "workers": {
    "abc1": {
      "branch": "cursor/translation-work-abc1",
      "last_heartbeat": 1767269900,
      "status": "online",
      "completed_count": 3
    },
    "def2": {
      "branch": "cursor/translation-work-def2",
      "last_heartbeat": 1767269850,
      "status": "online", 
      "completed_count": 2
    }
  }
}
```

**Update Frequency**: After every page claim or completion.

### Worker State: `worker-states/worker-XXXX.json`

Each worker maintains their own state file.

```json
{
  "worker_id": "abc1",
  "branch": "cursor/translation-work-abc1",
  "heartbeat": 1767269900,
  "status": "translating",
  "claimed_page": 14,
  "claim_time": 1767269500,
  "completed_pages": [
    {
      "page": 1,
      "completed_at": 1767268000,
      "hash": "a8f3b2c1"
    },
    {
      "page": 2,
      "completed_at": 1767268500,
      "hash": "c9d4e5f6"
    }
  ],
  "stats": {
    "pages_completed": 3,
    "pages_claimed": 1,
    "avg_time_per_page": 450
  }
}
```

**Update Frequency**: 
- On claim: immediately
- On completion: immediately  
- Heartbeat: every 60 seconds (automatic via daemon)

---

## Sync Service Implementation

### Core Responsibilities

1. **Auto-fetch**: Pull all branches every 30 seconds
2. **State aggregation**: Build global view from all `worker-states/*.json`
3. **Conflict detection**: Identify duplicate claims
4. **Work queue**: Maintain list of available pages
5. **API endpoints**: Provide commands for workers
6. **Heartbeat**: Update worker heartbeat automatically

### API Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `--start` | Start sync daemon | `python3 tools/sync_service.py --start --worker-id abc1` |
| `--stop` | Stop sync daemon | `python3 tools/sync_service.py --stop` |
| `--status` | Get global project status | `python3 tools/sync_service.py --status` |
| `--next-page` | Get next available page | `python3 tools/sync_service.py --next-page` |
| `--claim-page N` | Claim page N atomically | `python3 tools/sync_service.py --claim-page 42` |
| `--complete-page N` | Mark page N complete | `python3 tools/sync_service.py --complete-page 42 --file translations/page_042.json` |
| `--check-page N` | Check if page available | `python3 tools/sync_service.py --check-page 42` |

### Sync Loop Pseudocode

```python
class SyncService:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.state = {}
        self.last_sync = 0
        
    def run_loop(self):
        while True:
            try:
                # 1. Fetch all branches
                self.git_fetch_all()
                
                # 2. Read all worker states
                self.aggregate_worker_states()
                
                # 3. Build global state
                self.update_global_state()
                
                # 4. Detect conflicts
                conflicts = self.detect_conflicts()
                if conflicts:
                    self.handle_conflicts(conflicts)
                
                # 5. Update heartbeat
                self.update_heartbeat()
                
                # 6. Sleep
                time.sleep(30)
                
            except Exception as e:
                log_error(e)
                time.sleep(60)  # Back off on errors
    
    def aggregate_worker_states(self):
        """Read all worker-states/*.json from all branches"""
        self.state['workers'] = {}
        
        for branch in self.get_all_branches():
            try:
                # Read worker state from branch
                worker_file = f"origin/{branch}:worker-states/worker-*.json"
                state = self.git_show_json(worker_file)
                
                if state:
                    worker_id = state['worker_id']
                    self.state['workers'][worker_id] = state
            except:
                continue
    
    def update_global_state(self):
        """Build global view of claimed/completed pages"""
        claimed = {}
        completed = set()
        
        for worker_id, state in self.state['workers'].items():
            # Check heartbeat
            age = time.time() - state['heartbeat']
            if age > 600:  # 10 minutes
                state['status'] = 'offline'
                continue
            
            # Collect claimed pages
            if state.get('claimed_page'):
                claimed[state['claimed_page']] = {
                    'worker_id': worker_id,
                    'claimed_at': state['claim_time'],
                    'status': state['status']
                }
            
            # Collect completed pages
            for page_info in state.get('completed_pages', []):
                completed.add(page_info['page'])
        
        # Update global state
        total_pages = 99  # or read from config
        all_pages = set(range(1, total_pages + 1))
        available = sorted(all_pages - set(claimed.keys()) - completed)
        
        self.state['completed_pages'] = sorted(completed)
        self.state['claimed_pages'] = claimed
        self.state['available_pages'] = available
        self.state['last_updated'] = time.time()
    
    def detect_conflicts(self):
        """Find duplicate page claims"""
        conflicts = []
        
        # Group workers by claimed page
        claims_by_page = {}
        for worker_id, state in self.state['workers'].items():
            page = state.get('claimed_page')
            if page:
                if page not in claims_by_page:
                    claims_by_page[page] = []
                claims_by_page[page].append(worker_id)
        
        # Identify conflicts (multiple workers claiming same page)
        for page, workers in claims_by_page.items():
            if len(workers) > 1:
                conflicts.append({
                    'page': page,
                    'workers': workers
                })
        
        return conflicts
    
    def handle_conflicts(self, conflicts):
        """Resolve conflicts - earliest claim wins"""
        for conflict in conflicts:
            page = conflict['page']
            workers = conflict['workers']
            
            # Find worker with earliest claim
            claims = [(w, self.state['workers'][w]['claim_time']) 
                     for w in workers]
            winner = min(claims, key=lambda x: x[1])[0]
            losers = [w for w in workers if w != winner]
            
            # If we're a loser, revert our claim
            if self.worker_id in losers:
                self.revert_claim()
                log(f"Lost claim for page {page} to {winner}")
```

---

## Conflict Resolution

### Automatic Conflict Detection

Conflicts occur when:
1. Two workers claim same page within sync window (~30s)
2. Network delays cause race conditions
3. Worker rejoins and re-claims their old page

### Resolution Strategy

**Rule**: Earliest claim timestamp wins.

```python
def resolve_conflict(page_num, worker_claims):
    """
    worker_claims = [
        {'worker_id': 'abc1', 'claim_time': 1767269500},
        {'worker_id': 'def2', 'claim_time': 1767269505}
    ]
    """
    # Sort by claim time
    sorted_claims = sorted(worker_claims, key=lambda x: x['claim_time'])
    
    winner = sorted_claims[0]
    losers = sorted_claims[1:]
    
    # Winner keeps the page
    # Losers automatically revert their claim
    
    for loser in losers:
        notify_worker(loser['worker_id'], 
                     f"Lost claim for page {page_num} to {winner['worker_id']}")
        revert_claim(loser['worker_id'], page_num)
```

### Handling Offline Workers

**Scenario**: Worker claims page, then goes offline.

**Detection**: Heartbeat older than 10 minutes.

**Action**: 
1. After 10 min: Worker marked as "offline"
2. After 15 min: Worker's claimed page becomes available for reclaim
3. Sync service updates global state: move page from "claimed" to "available"

```python
def check_stale_claims(self):
    """Reclaim pages from offline workers"""
    now = time.time()
    
    for page, claim_info in self.state['claimed_pages'].items():
        worker_id = claim_info['worker_id']
        worker = self.state['workers'][worker_id]
        
        heartbeat_age = now - worker['heartbeat']
        claim_age = now - claim_info['claimed_at']
        
        if heartbeat_age > 900:  # 15 minutes offline
            # Reclaim the page
            log(f"Reclaiming page {page} from offline worker {worker_id}")
            
            # Remove from claimed_pages
            del self.state['claimed_pages'][page]
            
            # Add back to available
            self.state['available_pages'].append(page)
            self.state['available_pages'].sort()
            
            # Update global state file
            self.update_state_file()
```

---

## Worker Lifecycle

### Joining the Project

```bash
# 1. Create branch
git checkout -b cursor/translation-work-XXXX

# 2. Sync project state
git fetch origin
git merge origin/main  # Get STATE.json and existing work

# 3. Register as worker
python3 tools/sync_service.py --register --worker-id XXXX

# This creates worker-states/worker-XXXX.json and pushes it

# 4. Start sync daemon
python3 tools/sync_service.py --start --worker-id XXXX

# 5. Begin work loop
while true; do
    PAGE=$(python3 tools/sync_service.py --next-page)
    if [ "$PAGE" = "NONE" ]; then
        break
    fi
    
    python3 tools/sync_service.py --claim-page $PAGE
    python3 translate.py --page $PAGE
    python3 tools/sync_service.py --complete-page $PAGE \
        --file translations/page_$PAGE.json
done
```

### Leaving the Project

**Graceful Shutdown**:
```bash
# Stop sync daemon
python3 tools/sync_service.py --stop

# Update worker state to "offline"
python3 tools/sync_service.py --unregister --worker-id XXXX

# If you have a claimed page, release it
python3 tools/sync_service.py --release-claim
```

**Ungraceful Disconnect** (network loss, crash, etc.):
- Worker heartbeat goes stale (>10 min)
- Sync service automatically marks worker offline
- After 15 min, claimed page is reclaimed
- Worker can rejoin later and resume

### Rejoining After Disconnect

```bash
# 1. Fetch latest state
git fetch origin
git merge origin/main

# 2. Check your old state
python3 tools/sync_service.py --my-status

# Output shows:
# - Your last claimed page (if any)
# - Whether it was reclaimed
# - Your completed pages

# 3. Restart sync daemon
python3 tools/sync_service.py --start --worker-id XXXX

# 4. Resume work
# If your old page was reclaimed, daemon automatically assigns next page
```

---

## Tooling Implementation

### Required Tools

All in `tools/` directory:

| Tool | Purpose |
|------|---------|
| `init_project.py` | Initialize STATE.json and directories |
| `sync_service.py` | Core sync daemon and API |
| `translate.py` | Translation worker logic |
| `validate_state.py` | Validate STATE.json integrity |
| `dashboard.py` | Real-time progress dashboard |

### Sample: sync_service.py CLI

```bash
# Start daemon
python3 tools/sync_service.py --start --worker-id abc1

# Get status
python3 tools/sync_service.py --status
# Output:
# Project: durov-code-translation
# Total pages: 99
# Completed: 42 (42.4%)
# Claimed: 8
# Available: 49
# Workers online: 5/12

# Get next page
python3 tools/sync_service.py --next-page
# Output: 43

# Claim page
python3 tools/sync_service.py --claim-page 43
# Output: SUCCESS - Page 43 claimed

# Check specific page
python3 tools/sync_service.py --check-page 50
# Output: AVAILABLE

# Complete page
python3 tools/sync_service.py --complete-page 43 \
    --file translations/page_043.json
# Output: SUCCESS - Page 43 completed and submitted

# Stop daemon
python3 tools/sync_service.py --stop
```

---

## Progress Monitoring

### Real-Time Dashboard

```bash
# Start dashboard server
python3 tools/dashboard.py --port 8080

# Opens browser to http://localhost:8080
# Shows:
# - Project progress bar
# - Active workers (green = online, grey = offline)
# - Page status (completed = green, claimed = yellow, available = white)
# - Recent activity feed
# - Worker leaderboard
```

### Dashboard UI (ASCII for terminals)

```
╔════════════════════════════════════════════════════════════╗
║            Durov Code Translation Progress                 ║
╠════════════════════════════════════════════════════════════╣
║ Progress: [████████████████░░░░░░░░] 65/99 pages (65.7%)  ║
╠════════════════════════════════════════════════════════════╣
║ Workers Online: 8/12                                       ║
║ ● abc1  [15 pages] Translating page 66                    ║
║ ● def2  [12 pages] Translating page 67                    ║
║ ● ghi3  [9 pages]  Translating page 68                    ║
║ ○ jkl4  [0 pages]  OFFLINE (stale 12m)                    ║
╠════════════════════════════════════════════════════════════╣
║ Available Pages: 25                                        ║
║ 69 70 71 72 73 74 75 76 77 78 79 80 ...                   ║
╠════════════════════════════════════════════════════════════╣
║ Recent Activity:                                           ║
║ [13:45] abc1 completed page 65                            ║
║ [13:44] def2 completed page 64                            ║
║ [13:43] ghi3 completed page 63                            ║
║ [13:41] jkl4 went offline                                 ║
╚════════════════════════════════════════════════════════════╝
```

---

## Enforcement Mechanisms

### 1. Pre-Commit Hooks

```bash
# .git/hooks/pre-commit

#!/bin/bash
# Validate worker state before committing

python3 tools/validate_state.py --worker-state worker-states/worker-*.json

if [ $? -ne 0 ]; then
    echo "ERROR: Invalid worker state. Commit rejected."
    exit 1
fi
```

### 2. Claim Validation

Workers **cannot** claim a page without going through sync service:

```bash
# This will FAIL:
echo '{"claimed_page": 42}' > worker-states/worker-abc1.json
git commit -m "Claiming page 42"

# Error: Claim must go through sync_service.py --claim-page
```

Sync service is the **only** way to claim pages.

### 3. Mandatory Daemon Check

```bash
# Before any work command
python3 tools/sync_service.py --next-page

# If daemon not running:
# ERROR: Sync service not running. Start with: sync_service.py --start
```

### 4. State File Schema Validation

```python
# All STATE.json and worker-*.json files must validate against schema

WORKER_STATE_SCHEMA = {
    "type": "object",
    "required": ["worker_id", "branch", "heartbeat", "status"],
    "properties": {
        "worker_id": {"type": "string", "pattern": "^[a-z0-9]{4}$"},
        "branch": {"type": "string"},
        "heartbeat": {"type": "number"},
        "status": {"enum": ["online", "translating", "offline"]},
        "claimed_page": {"type": ["number", "null"]},
        "completed_pages": {"type": "array"}
    }
}
```

---

## Anti-Patterns (Enforced by Tooling)

| Anti-Pattern | How It's Prevented |
|--------------|-------------------|
| Claiming multiple pages | Sync service only allows one claimed_page per worker |
| Skipping sync | Commands fail if daemon not running |
| Manual state editing | Pre-commit hooks validate schema |
| Duplicate claims | Atomic claim + immediate conflict detection |
| Stale heartbeats | Daemon auto-updates every 60s |
| Working offline | Next-page command requires live sync service |

---

## Protocol Comparison

### Old Protocol (PROTOCOL.md)

```
Worker: "I'll claim page 42"
         *edits WORKER_STATE.md manually*
         *commits and pushes*
         *2 minutes later, fetches*
         "Oh no, someone else claimed it too!"
```

**Problems**:
- Manual editing → errors
- Delayed sync → conflicts
- No validation → duplicates
- Trust-based → fails at scale

### New Protocol (PROTOCOL_V2.md)

```
Worker: "Give me next page"
Daemon: *checks global state*
        "Page 42 is available"
Worker: "Claim page 42"
Daemon: *atomic claim*
        *immediate push*
        *immediate re-fetch*
        *validates no conflict*
        "SUCCESS - page 42 is yours"
Worker: *translates page 42*
Worker: "Complete page 42"
Daemon: *validates translation*
        *updates global state*
        *pushes completion*
        "SUCCESS - page 42 completed"
```

**Improvements**:
- Automated sync → no manual errors
- Immediate validation → conflict detected instantly
- Atomic operations → no race conditions
- Enforced workflow → consistency guaranteed

---

## Migration Guide

### From PROTOCOL.md to PROTOCOL_V2.md

1. **Stop all workers** using old protocol
2. **Install new tools**: `git pull` to get `tools/sync_service.py`
3. **Initialize global state**: `python3 tools/init_project.py`
4. **Restart workers** with new protocol:
   ```bash
   python3 tools/sync_service.py --start --worker-id XXXX
   ```

### Backward Compatibility

Old `WORKER_STATE.md` files can be migrated:

```bash
python3 tools/migrate_worker_state.py \
    --from WORKER_STATE.md \
    --to worker-states/worker-XXXX.json
```

---

## Success Metrics

Track these to measure protocol effectiveness:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Work Duplication Rate** | <5% | `completed_pages_total / (workers * completed_pages_unique)` |
| **Worker Participation** | >80% | `workers_with_completions / total_workers` |
| **Claim Conflict Rate** | <10% | `claims_conflicted / claims_total` |
| **Average Pages per Worker** | Balanced | `std_dev(pages_per_worker)` should be low |
| **Pages Reclaimed** | <15% | `pages_reclaimed / pages_claimed` |

### Sample Success Dashboard

```
╔════════════════════════════════════════════════════════════╗
║                  Protocol Effectiveness                    ║
╠════════════════════════════════════════════════════════════╣
║ Work Duplication:    2.1% ✓ (target: <5%)                 ║
║ Worker Participation: 87.5% ✓ (target: >80%)              ║
║ Claim Conflicts:     4.3% ✓ (target: <10%)                ║
║ Work Distribution:   σ=3.2 pages ✓ (balanced)             ║
║ Pages Reclaimed:     8.1% ✓ (target: <15%)                ║
╠════════════════════════════════════════════════════════════╣
║ Status: HEALTHY ✓                                          ║
╚════════════════════════════════════════════════════════════╝
```

---

## Summary: Key Improvements Over v1

| Aspect | v1 (PROTOCOL.md) | v2 (PROTOCOL_V2.md) |
|--------|------------------|---------------------|
| **Sync** | Manual (every 2-3 min) | Automatic daemon (every 30s) |
| **Claiming** | Manual edit + push | API call with validation |
| **Conflict Detection** | Manual check | Automatic + immediate |
| **Conflict Resolution** | Manual | Automatic (earliest wins) |
| **State Management** | Per-worker MD files | Global JSON + worker JSON |
| **Validation** | None | Schema + pre-commit hooks |
| **Work Distribution** | Honor system | Enforced queue |
| **Heartbeat** | Manual commits | Auto-updated by daemon |
| **Offline Handling** | Manual reclaim | Auto-reclaim after 15min |
| **Visibility** | None | Real-time dashboard |

**Result**: Expect >95% reduction in duplicate work, >80% worker participation, graceful scaling to 16+ workers.

---

## Quick Start (TL;DR)

```bash
# First time setup
git checkout -b cursor/translation-work-XXXX
python3 tools/init_project.py  # If first worker
python3 tools/sync_service.py --start --worker-id XXXX

# Work loop (automatic)
python3 tools/worker_loop.py --worker-id XXXX

# Or manual control
while true; do
    PAGE=$(python3 tools/sync_service.py --next-page)
    [ "$PAGE" = "NONE" ] && break
    
    python3 tools/sync_service.py --claim-page $PAGE
    python3 translate.py --page $PAGE
    python3 tools/sync_service.py --complete-page $PAGE \
        --file translations/page_$PAGE.json
done
```

**That's it.** The sync service handles everything else automatically.

---

## Appendix: Implementation Checklist

- [ ] `tools/init_project.py` - Initialize STATE.json
- [ ] `tools/sync_service.py` - Core sync daemon
  - [ ] --start: Start daemon
  - [ ] --stop: Stop daemon
  - [ ] --next-page: Get next available
  - [ ] --claim-page: Atomic claim
  - [ ] --complete-page: Submit work
  - [ ] --status: Global status
  - [ ] --my-status: Worker status
- [ ] `tools/validate_state.py` - JSON schema validation
- [ ] `tools/dashboard.py` - Progress monitoring
- [ ] `tools/worker_loop.py` - Automated work loop
- [ ] `tools/migrate_worker_state.py` - Migration from v1
- [ ] `.git/hooks/pre-commit` - State validation hook
- [ ] `STATE.json` schema definition
- [ ] `worker-states/*.json` schema definition
- [ ] Documentation: Usage examples
- [ ] Documentation: Troubleshooting guide

---

**Protocol v2.0 - Designed for reliable multi-agent collaboration at scale.**
