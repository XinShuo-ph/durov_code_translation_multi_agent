# Quick Start Guide

**Goal**: Get from zero to productive work in 60 seconds.

---

## Prerequisites

- Git repository cloned
- Python 3.6+ installed
- On your own git branch (cursor/something-xxxx)

---

## Step-by-Step (60 Seconds)

### 1. Identify Yourself (5 seconds)

```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_SHORT_ID on branch $MY_BRANCH"
```

Example output: `I am: 7aa1 on branch cursor/agent-collaboration-protocol-7aa1`

---

### 2. Register as Worker (15 seconds)

```bash
# Copy template
cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md

# Edit the file (replace placeholders)
# You need to replace:
# - [BRANCH_NAME] → your full branch name
# - [SHORT_ID] → your short ID (last 4 chars)
# - [UNIX_TIMESTAMP] → current Unix timestamp
# - [ISO_TIMESTAMP] → current ISO timestamp

# Quick way to get timestamps:
echo "Unix: $(date +%s)"
echo "ISO: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# After editing, commit and push
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] JOIN: Registering as active worker
HEARTBEAT: $(date +%s)"
git push -u origin HEAD
```

---

### 3. Start Sync Daemon (10 seconds)

```bash
# THIS IS MANDATORY - prevents 83% duplication problem
python3 tools/sync_daemon.py --start &

# Wait for initial sync
sleep 5

# Verify daemon is running
python3 tools/sync_daemon.py --status
```

You should see output showing:
- Number of active workers
- Completed/claimed/available pages
- Worker details

---

### 4. Claim First Page (5 seconds)

```bash
./tools/claim_page.sh
```

This will:
1. Query daemon for next available page
2. Update your WORKER_STATE.md
3. Commit and push the claim
4. Tell you which page to work on

---

### 5. Translate Page (20 minutes typical)

Work on your claimed page. Save output to:
```
translations/page_NNN.json
```

Format:
```json
{
  "page": NNN,
  "chapter": X,
  "sentences": [
    {
      "id": 1,
      "ru": "Russian text",
      "en": "English translation",
      "zh": "Chinese translation",
      "ja": "Japanese translation"
    }
  ]
}
```

---

### 6. Complete Page (5 seconds)

```bash
./tools/complete_page.sh NNN
```

This will:
1. Calculate hash of your translation
2. Update WORKER_STATE.md (move page from claimed to completed)
3. Commit and push the completed work
4. Free the page for next claim

---

### 7. Repeat

```bash
./tools/claim_page.sh
# ... translate ...
./tools/complete_page.sh NNN
# ... repeat ...
```

---

## Common Commands

### Check team status
```bash
python3 tools/sync_daemon.py --status
```

Shows:
- How many workers are online
- How many pages are done/claimed/available
- Which workers are stalled
- Individual worker progress

### Get next available page
```bash
python3 tools/sync_daemon.py --next-page
```

Returns the lowest available page number.

### Check if specific page is available
```bash
python3 tools/sync_daemon.py --check-page 42
```

Returns: `available` | `claimed_by_xxxx` | `completed`

### Force immediate sync
```bash
python3 tools/sync_daemon.py --sync-now
```

Useful if you think the cache is stale.

### Check for reclaimable pages
```bash
python3 tools/sync_daemon.py --reclaimable
```

Shows pages claimed by stalled workers (can be reclaimed).

### Stop daemon
```bash
python3 tools/sync_daemon.py --stop
```

---

## Troubleshooting

### Daemon not starting
```bash
# Check if already running
cat .sync/daemon.pid

# Stop old daemon
python3 tools/sync_daemon.py --stop

# Start fresh
python3 tools/sync_daemon.py --start &
```

### No pages available
```bash
# Check status
python3 tools/sync_daemon.py --status

# If many pages claimed but not completed, workers may be slow
# Check for stalled workers:
python3 tools/sync_daemon.py --reclaimable
```

### Page claimed by another worker
```bash
# This is rare (race condition)
# Solution: Just claim next page
./tools/claim_page.sh
```

### Heartbeat timeout warning
```bash
# Push a heartbeat every 5 minutes if you're still working
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] HEARTBEAT
STATUS: Still translating page 42
HEARTBEAT: $(date +%s)"
git push origin HEAD
```

---

## Monitoring Your Progress

Your WORKER_STATE.md tracks:
- Pages you've completed (in the table)
- Current claimed page
- Statistics (pages/hour rate)
- Last heartbeat

Other workers can see this to coordinate with you.

---

## Best Practices

### DO:
✅ Start sync daemon FIRST (before claiming)  
✅ Push immediately after claiming  
✅ Push immediately after completing  
✅ Update heartbeat every 5 minutes  
✅ Use helper scripts (claim_page.sh, complete_page.sh)  
✅ Check team status occasionally  

### DON'T:
❌ Claim multiple pages at once  
❌ Work without sync daemon  
❌ Forget to push after claiming  
❌ Let heartbeat go >10 minutes  
❌ Manually edit WORKER_STATE.md without committing  

---

## Quick Reference

| Task | Command |
|------|---------|
| Start daemon | `python3 tools/sync_daemon.py --start &` |
| Claim page | `./tools/claim_page.sh` |
| Complete page | `./tools/complete_page.sh N` |
| Check status | `python3 tools/sync_daemon.py --status` |
| Next page | `python3 tools/sync_daemon.py --next-page` |
| Heartbeat | `git commit -m "[$MY_SHORT_ID] HEARTBEAT..."` |

---

**That's it! You're ready to contribute.**

For detailed protocol info, see `PROTOCOL.md`.  
For implementation details, see `IMPLEMENTATION.md`.
