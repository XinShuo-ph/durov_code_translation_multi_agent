# Migration Guide: Protocol v1 → v2

## Overview

This guide helps you migrate from the milestone-based protocol (v1) to the sync-daemon-based protocol (v2).

**Key Changes**:
- ✅ Eliminated M0/M1/M2 milestone system
- ✅ Added mandatory sync daemon
- ✅ Simplified WORKER_STATE.md format
- ✅ Added atomic page claiming tools
- ✅ Automated conflict detection

---

## For Active Projects

### Step 1: Coordinate with Other Workers

Create a coordination commit:

```bash
git commit --allow-empty -m "[$MY_ID] NOTICE: Preparing for protocol v2 migration"
git push
```

Wait for all workers to acknowledge or go offline (stale heartbeat).

### Step 2: Install New Tools

On your branch:

```bash
# Fetch latest PROTOCOL_V2.md and tools
git fetch origin main  # Or wherever the new protocol is
git checkout origin/main -- PROTOCOL_V2.md tools/sync_daemon.py tools/claim_page.py tools/heartbeat.py tools/complete_page.py

# Make executable
chmod +x tools/*.py
```

### Step 3: Migrate Your WORKER_STATE.md

**Option A: Manual Migration**

1. Open your current `WORKER_STATE.md`
2. Remove these sections:
   - Milestone status (M0/M1/M2)
   - Consensus votes
   - Session logs
   - Messages to other workers
   - Manual "Known Workers" table

3. Keep these sections:
   - Worker identity
   - Heartbeat
   - Current claimed page (if any)
   - Completed pages list

4. Reformat to match `WORKER_STATE_TEMPLATE_V2.md`

**Option B: Automated Migration**

```bash
# Backup current state
cp WORKER_STATE.md WORKER_STATE.md.backup

# Generate new state from template
MY_BRANCH=$(git branch --show-current)
MY_ID=${MY_BRANCH##*-}

cp WORKER_STATE_TEMPLATE_V2.md WORKER_STATE.md
sed -i "s/\[WORKER_ID\]/$MY_ID/g" WORKER_STATE.md
sed -i "s/\[BRANCH_NAME\]/$MY_BRANCH/g" WORKER_STATE.md
sed -i "s/\[UNIX_TIMESTAMP\]/$(date +%s)/g" WORKER_STATE.md

# Manually copy over completed pages from backup
```

### Step 4: Start Sync Daemon

```bash
python3 tools/sync_daemon.py --start &
sleep 30  # Wait for initial sync
```

Verify it's running:

```bash
python3 tools/sync_daemon.py --status
```

### Step 5: Commit Migration

```bash
git add WORKER_STATE.md PROTOCOL_V2.md tools/
git commit -m "[$MY_ID] MIGRATE: Switched to protocol v2"
git push
```

### Step 6: Resume Work

```bash
# If you had a claimed page, reclaim it
python3 tools/claim_page.py YOUR_PAGE

# Or get next available
NEXT=$(python3 tools/sync_daemon.py --next-page)
python3 tools/claim_page.py $NEXT

# Continue working...
```

---

## For New Projects

Just start with protocol v2 from the beginning:

```bash
# 1. Copy protocol and templates
cp PROTOCOL_V2.md PROTOCOL.md
cp WORKER_STATE_TEMPLATE_V2.md WORKER_STATE_TEMPLATE.md

# 2. Follow quick start in PROTOCOL_V2.md
# (60 seconds to first claim)
```

---

## Verification Checklist

After migration, verify:

- [ ] Sync daemon is running (`ps aux | grep sync_daemon`)
- [ ] WORKER_STATE.md is in v2 format (no milestones)
- [ ] Can claim pages (`python3 tools/sync_daemon.py --next-page`)
- [ ] Heartbeat updates work (`python3 tools/heartbeat.py`)
- [ ] Other workers are visible (`python3 tools/sync_daemon.py --status`)

---

## Troubleshooting

### Sync daemon won't start

**Problem**: `python3 tools/sync_daemon.py --start` hangs or errors

**Solutions**:
1. Check Python version: `python3 --version` (need 3.7+)
2. Check git access: `git fetch origin --all`
3. Check write permissions: `ls -la .sync/`

### Can't see other workers

**Problem**: `python3 tools/sync_daemon.py --status` shows 0 workers

**Solutions**:
1. Wait 60 seconds for first sync cycle
2. Force sync: `python3 tools/sync_daemon.py --force-sync`
3. Check git remote: `git remote -v`
4. Verify other workers have pushed: `git fetch origin --all && git branch -r`

### Lost race condition on every claim

**Problem**: Always lose page claims to other workers

**Solutions**:
1. Check your system time: `date +%s` (should match real time)
2. Check git commit timestamps: `git log --format="%ct %s" -1`
3. Try claiming a specific page: `python3 tools/claim_page.py 75`

### Heartbeat going stale

**Problem**: Other workers think you're offline

**Solutions**:
1. Set up automatic heartbeat:
   ```bash
   # Run in background
   while true; do sleep 180; python3 tools/heartbeat.py; done &
   ```
2. Check git push works: `git push origin HEAD`
3. Verify WORKER_STATE.md has correct format

---

## Rollback Procedure

If migration fails, you can rollback:

```bash
# Restore old WORKER_STATE.md
cp WORKER_STATE.md.backup WORKER_STATE.md

# Stop sync daemon
python3 tools/sync_daemon.py --stop

# Commit rollback
git add WORKER_STATE.md
git commit -m "[$MY_ID] ROLLBACK: Reverting to protocol v1"
git push
```

Then coordinate with other workers to retry migration.

---

## FAQ

### Q: Do all workers need to migrate at once?

**A**: No, but it's recommended. Protocol v2 is backward-compatible in the sense that:
- v2 workers can see v1 workers (via WORKER_STATE.md parsing)
- v1 workers may not see v2 workers' claims correctly
- Mixed deployments may have race conditions

**Best practice**: Coordinate a migration window.

### Q: What happens to work in progress?

**A**: Nothing is lost:
- Completed pages remain in `translations/`
- Current claims can be reclaimed
- Git history preserves everything

### Q: Can I test v2 on a separate branch first?

**A**: Yes! Recommended flow:

```bash
# Create test branch
git checkout -b test-protocol-v2

# Install v2 tools
# ... follow migration steps ...

# Test claiming/completing a page
python3 tools/sync_daemon.py --start &
sleep 30
NEXT=$(python3 tools/sync_daemon.py --next-page)
python3 tools/claim_page.py $NEXT

# If satisfied, merge to main branch
git checkout original-branch
git merge test-protocol-v2
```

### Q: How do I monitor the migration?

**A**: Use sync daemon status:

```bash
# Watch migration progress
watch -n 10 'python3 tools/sync_daemon.py --status'
```

You'll see:
- Workers online increasing as others migrate
- Old milestone-based states disappearing
- Page claims becoming more consistent

---

## Timeline Estimate

| Project Size | Migration Time |
|-------------|---------------|
| 1-4 workers | 15 minutes |
| 5-10 workers | 30 minutes |
| 11-16 workers | 45-60 minutes |
| 17+ workers | 1-2 hours |

Most time is spent on coordination, not the migration itself.

---

## Support

If you encounter issues:

1. Check `.sync/warnings.log` for daemon warnings
2. Check `.sync/global_state.json` for system state
3. Review `PROTOCOL_V2.md` for detailed specs

---

**Happy migrating! The improved protocol will make your multi-agent system much more efficient.**
