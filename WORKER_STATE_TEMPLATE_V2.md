# Worker: [WORKER_ID]

**Branch**: [BRANCH_NAME]  
**Heartbeat**: [UNIX_TIMESTAMP]  
**Status**: idle

## Current Work
- **Claimed Page**: none
- **Claim Time**: -
- **Progress**: -

## Completed Pages
| Page | Completed At | Hash | Duration |
|------|--------------|------|----------|

## Statistics
- **Total Completed**: 0 pages
- **Average Time**: - minutes/page
- **Uptime**: 0 minutes
- **Last Sync**: [UNIX_TIMESTAMP]

---

## Setup Instructions

1. **Get your worker ID**:
   ```bash
   MY_BRANCH=$(git branch --show-current)
   MY_ID=${MY_BRANCH##*-}  # Last component after final dash
   echo "My worker ID: $MY_ID"
   ```

2. **Fill in this template**:
   ```bash
   cp WORKER_STATE_TEMPLATE_V2.md WORKER_STATE.md
   
   # Replace placeholders
   sed -i "s/\[WORKER_ID\]/$MY_ID/g" WORKER_STATE.md
   sed -i "s/\[BRANCH_NAME\]/$MY_BRANCH/g" WORKER_STATE.md
   sed -i "s/\[UNIX_TIMESTAMP\]/$(date +%s)/g" WORKER_STATE.md
   ```

3. **Start sync daemon (MANDATORY)**:
   ```bash
   python3 tools/sync_daemon.py --start &
   sleep 30  # Wait for initial sync
   ```

4. **Register yourself**:
   ```bash
   git add WORKER_STATE.md
   git commit -m "[$MY_ID] REGISTER: Worker online"
   git push -u origin HEAD
   ```

5. **Claim first page**:
   ```bash
   NEXT=$(python3 tools/sync_daemon.py --next-page)
   python3 tools/claim_page.py $NEXT
   ```

6. **Start working**:
   ```bash
   # Your translation workflow here
   # When done:
   python3 tools/complete_page.py $NEXT
   ```

---

## Heartbeat Maintenance

**CRITICAL**: Update heartbeat at least every 5 minutes:

```bash
# Manual heartbeat update
python3 tools/heartbeat.py

# Or automate it (every 3 minutes)
while true; do
    sleep 180
    python3 tools/heartbeat.py
done &
```

If your heartbeat goes stale (>10 min), other workers will:
- Mark you as offline
- Reclaim your pages after 15 minutes

---

## Example Filled-In State

```markdown
# Worker: a1b2

**Branch**: cursor/book-translation-task-a1b2  
**Heartbeat**: 1739328500  
**Status**: working

## Current Work
- **Claimed Page**: 42
- **Claim Time**: 1739328200
- **Progress**: 75%

## Completed Pages
| Page | Completed At | Hash | Duration |
|------|--------------|------|----------|
| 5    | 1739327800   | a8f3 | 4 min    |
| 8    | 1739328000   | b2c9 | 5 min    |
| 12   | 1739328100   | d4e1 | 3 min    |

## Statistics
- **Total Completed**: 3 pages
- **Average Time**: 4 minutes/page
- **Uptime**: 45 minutes
- **Last Sync**: 1739328450 (2 min ago)
```

---

## Troubleshooting

### Sync daemon not running
```bash
# Check if running
ps aux | grep sync_daemon

# Start if needed
python3 tools/sync_daemon.py --start &
```

### Lost race condition
```bash
# This is normal - try next page
NEXT=$(python3 tools/sync_daemon.py --next-page)
python3 tools/claim_page.py $NEXT
```

### Can't push
```bash
# Fetch first
git fetch origin
git rebase origin/$(git branch --show-current)

# Then try again
git push origin HEAD
```

---

Delete this instructions section from your WORKER_STATE.md after setup!
