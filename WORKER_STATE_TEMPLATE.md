# Worker: [SHORT_ID]

## Status
- **Branch**: [YOUR_FULL_BRANCH_NAME]
- **Short ID**: [LAST_4_CHARS]
- **Heartbeat**: [UNIX_TIMESTAMP]
- **Status**: online

## Current Work
- **Claimed Page**: none
- **Started At**: -

## Completed Pages
| Page | Completed At | Hash |
|------|--------------|------|

## Peer Reviews
| Page | Author | Reviewed At | Result | Notes |
|------|--------|-------------|--------|-------|

## Known Workers (Last Sync)
| Short ID | Status | Claimed Page | Last Heartbeat |
|----------|--------|--------------|----------------|

## Notes
Ready to begin translation.

---

## Quick Usage

```bash
# 1) Set identity
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | awk -F- '{print $NF}' | tail -c 5)

# 2) Scope to this run family
export SYNC_BRANCH_GLOB="origin/cursor/book-translation-multi-agent-*"

# 3) Register worker state
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: register worker
HEARTBEAT: $(date +%s)"
git push origin HEAD

# 4) Ask coordinator for next action
python3 tools/sync_daemon.py --next-action --worker "$MY_BRANCH" --fetch
```
