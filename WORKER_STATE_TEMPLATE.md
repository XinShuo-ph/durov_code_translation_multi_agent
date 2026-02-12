# Worker: [SHORT_ID]

## Status
- **Branch**: [YOUR_FULL_BRANCH_NAME]
- **Short ID**: [LAST_4_CHARS]
- **Protocol Version**: 2
- **Heartbeat**: [UNIX_TIMESTAMP]
- **Status**: online

## Current Work
- **Claimed Page**: none
- **Lease Expires At**: -
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

## Update Rules (Do Not Delete)

1. Keep this file machine-parseable. Do not rename headings or field labels.
2. When claiming a page:
   - set `Status: translating`
   - set `Claimed Page: <page>`
   - set `Lease Expires At: <now+900>`
   - set `Started At: <now>`
   - set `Heartbeat: <now>`
3. When finishing a page:
   - append a row to `Completed Pages`
   - reset claim fields to `none` / `-`
   - set `Status: online` (or `idle` if stopping)
   - set `Heartbeat: <now>`
4. Push every CLAIM and DONE update immediately.
