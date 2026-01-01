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

## Known Workers (Last Sync)
| Short ID | Status | Claimed Page | Last Heartbeat |
|----------|--------|--------------|----------------|

## Notes
Ready to begin translation.

---

## How to Use This Template

1. **Copy this file** to `WORKER_STATE.md`:
   ```bash
   cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
   ```

2. **Get your identity**:
   ```bash
   MY_BRANCH=$(git branch --show-current)
   MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
   echo "Branch: $MY_BRANCH"
   echo "Short ID: $MY_SHORT_ID"
   ```

3. **Fill in your details**:
   - Replace `[YOUR_FULL_BRANCH_NAME]` with your branch
   - Replace `[LAST_4_CHARS]` with your short ID
   - Replace `[UNIX_TIMESTAMP]` with `$(date +%s)`

4. **Commit and push** (this registers you!):
   ```bash
   git add WORKER_STATE.md
   git commit -m "[$MY_SHORT_ID] SYNC: Registering as active worker
   HEARTBEAT: $(date +%s)"
   git push origin HEAD
   ```

5. **Delete this "How to Use" section** from your WORKER_STATE.md

---

## Example Filled-In State

```markdown
# Worker: a1b2

## Status
- **Branch**: cursor/book-translation-task-a1b2
- **Short ID**: a1b2
- **Heartbeat**: 1735689600
- **Status**: translating

## Current Work
- **Claimed Page**: 15
- **Started At**: 1735689500

## Completed Pages
| Page | Completed At | Hash |
|------|--------------|------|
| 13   | 1735688400   | a8f3b2c1 |
| 14   | 1735689000   | c9d4e5f6 |

## Known Workers (Last Sync)
| Short ID | Status | Claimed Page | Last Heartbeat |
|----------|--------|--------------|----------------|
| c3d4     | online | 16           | 1735689550     |
| e5f6     | online | 17           | 1735689500     |
| g7h8     | offline| 18           | 1735685000     |

## Notes
Working on Chapter 1. Synced at 1735689600.
```
