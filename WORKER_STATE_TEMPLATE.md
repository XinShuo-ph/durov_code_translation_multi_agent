# Worker State Template

**This protocol uses `WORKER_STATE.json` (not Markdown) for machine-parseable state.**

To initialize your worker state:

```bash
cp WORKER_STATE_TEMPLATE.json WORKER_STATE.json
```

Then edit `WORKER_STATE.json` to fill in your details:
- `worker_id`: Last segment of your branch name (e.g., `c68e`)
- `branch`: Your full branch name
- `batch_prefix`: Branch name without the final `-XXXX` suffix
- `heartbeat`: Current Unix timestamp (`date +%s`)

See `WORKER_STATE_TEMPLATE.json` for the JSON schema.
