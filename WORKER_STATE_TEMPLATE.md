# WORKER_STATE.md (Optional Human Notes)

`WORKER_STATE.json` is the machine-readable source of truth.

Use this markdown file only for optional human notes.

---

## Required (machine-readable)

```bash
cp WORKER_STATE_TEMPLATE.json WORKER_STATE.json
```

Update state via coordinator:

```bash
python3 tools/parallel_coord.py claim --worker "$MY_SHORT_ID" --page 23
python3 tools/parallel_coord.py done --worker "$MY_SHORT_ID" --file translations/page_023.json
python3 tools/parallel_coord.py heartbeat --worker "$MY_SHORT_ID" --status reviewing
```

---

## Optional markdown snapshot

```markdown
# Worker: abcd

- Branch: cursor/your-batch-abcd
- Status: translating
- Claimed Page: 23
- Last Heartbeat: 1767254400
- Completed Pages: 7, 8, 9

Notes:
- Reclaimed page 23 after stale claim timeout.
```

