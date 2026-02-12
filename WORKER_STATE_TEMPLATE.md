# Optional: WORKER_STATE.md (minimal template)

This file is **optional** in Protocol v3. Coordination should not depend on it.
If you want a human-readable status file on your branch, keep it minimal.

---

# Worker: [SHORT_ID]

## Identity
- **Branch**: [cursor/exp-<ID>-<role>-<xxxx>]
- **Short ID**: [xxxx]
- **Experiment**: [exp-<ID>]
- **Last Active**: [ISO timestamp]

## Progress
- **Completed Pages**: [comma-separated list, e.g. 12, 19, 20]
- **Currently Working On**: [page number or "none"]

## Notes
[Optional: brief message for integrator/reviewers]

---

## How to Use This Template

1. **Copy this file** to `WORKER_STATE.md`:
   ```bash
   cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
   ```

2. **Get your identity**:
   ```bash
   MY_BRANCH=$(git branch --show-current)
   MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[0-9a-fA-F]{4}$' || true)
   echo "Branch: $MY_BRANCH"
   echo "Short ID: $MY_SHORT_ID"
   ```

3. **Fill in your details**:
   - Replace `[ISO timestamp]` with `$(date -u +%Y-%m-%dT%H:%M:%SZ)`

4. **Commit and push** (this registers you!):
   ```bash
   git add WORKER_STATE.md
   git commit -m "[$MY_SHORT_ID] status: update worker state"
   git push origin HEAD
   ```

5. **Delete this "How to Use" section** from your WORKER_STATE.md

---

## Example Filled-In State

```markdown
# Worker: a1b2

## Identity
- **Branch**: cursor/exp-005-translate-a1b2
- **Short ID**: a1b2
- **Experiment**: exp-005
- **Last Active**: 2026-02-12T00:00:00Z

## Progress
- **Completed Pages**: 12, 19, 20
- **Currently Working On**: 21

## Notes
Pushing pages as soon as they validate.
```
