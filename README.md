# Durov Code Translation - Multi-Agent Parallel Workspace

This repo translates `Код Дурова` into EN / ZH / JA with multiple workers in parallel.

## Start Here

1. Read `PROTOCOL.md` (v3 executable protocol).
2. Use `tools/parallel_coord.py` for all coordination.
3. Keep machine-readable state in `WORKER_STATE.json`.

## Quick Commands

```bash
MY_SHORT_ID=$(git branch --show-current | awk -F- '{print $NF}')
test -f WORKER_STATE.json || cp WORKER_STATE_TEMPLATE.json WORKER_STATE.json

python3 tools/parallel_coord.py --fetch status
NEXT=$(python3 tools/parallel_coord.py --fetch next --worker "$MY_SHORT_ID")
python3 tools/parallel_coord.py --fetch claim --worker "$MY_SHORT_ID" --page "$NEXT"
```

After translation:

```bash
FILE="translations/page_$(printf '%03d' "$NEXT").json"
python3 tools/parallel_coord.py done --worker "$MY_SHORT_ID" --file "$FILE"
```

## Important Conventions

- Output path: `translations/page_XXX.json`
- One active claim per worker
- Heartbeat/claim state: `WORKER_STATE.json`
- Batch-local discovery only (same branch prefix)

## Repository Layout

- `PROTOCOL.md` - authoritative parallel protocol
- `WORKER_STATE_TEMPLATE.json` - machine-readable state template
- `WORKER_STATE_TEMPLATE.md` - optional human notes template
- `tools/parallel_coord.py` - executable coordinator
- `tools/compile_pages.py` - optional JSON->PDF page compiler
- `extracted/pages/page_XXX.txt` - source text by page
- `research/` - glossary and background docs

