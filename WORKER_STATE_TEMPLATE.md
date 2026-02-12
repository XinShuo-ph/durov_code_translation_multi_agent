# Worker: <short_id>

## Identity
- **Branch**: <your branch name>
- **Short ID**: <last 4 chars (recommended)>
- **Slot (0-15)**: <optional; computed by tools/sync.py>

## Status
- **Heartbeat**: <unix timestamp>
- **Status**: online | translating | reviewing | integrating | blocked

## Current Work
- **Claimed Page**: none
- **Started At**: -

## Progress
- **Last Completed Page**: -
- **Last Review Note**: -

## Notes
<messages / blockers / what you plan to do next>

---

## Minimal registration (push‑proof)

```bash
cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md
# edit placeholders
git add WORKER_STATE.md
git commit -m "[<id>] SYNC: register\nHEARTBEAT: $(date +%s)"
git push origin HEAD
```

