# WORKER_STATE v3

Branch: cursor/book-translation-multi-agent-xxxx
Short-ID: xxxx
Heartbeat: 0
Status: idle
Claimed-Page: none
Claimed-At: -
Last-Sync: 0
Completed-Pages:
Known-Online-Workers:
Notes:

---

## Field Rules

- `Heartbeat`: Unix timestamp (`date +%s`), refresh at least every 5 minutes.
- `Status`: one of `idle`, `translating`, `reviewing`, `blocked`, `offline`.
- `Claimed-Page`: page number or `none`.
- `Completed-Pages`: comma-separated page numbers (example: `1,2,3,4`).
- `Known-Online-Workers`: comma-separated short ids from latest sync.

Keep field names exactly as written so tooling can parse them.

---

## Quick Initialization

```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | rg -o '[^-]+$')
NOW=$(date +%s)

cp WORKER_STATE_TEMPLATE.md WORKER_STATE.md

# Fill values:
# Branch: $MY_BRANCH
# Short-ID: $MY_SHORT_ID
# Heartbeat: $NOW
# Last-Sync: $NOW

git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] SYNC: worker online
HEARTBEAT: $NOW"
git push origin HEAD
```

---

## Update Examples

### Claim page 17

```text
Heartbeat: 1767250000
Status: translating
Claimed-Page: 17
Claimed-At: 1767250000
Last-Sync: 1767250000
```

### Complete page 17

```text
Heartbeat: 1767250300
Status: idle
Claimed-Page: none
Claimed-At: -
Completed-Pages: 7,8,9,17
Last-Sync: 1767250300
```

