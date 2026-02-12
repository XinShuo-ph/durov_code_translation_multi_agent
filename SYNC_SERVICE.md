# Sync Service (Executable Multi-Agent Coordination)

This repo intentionally treats **git as a message bus** for multi-agent coordination. The biggest failure mode in the earlier experiments was **manual syncing not actually happening**, which led to:

- duplicated pages (many agents “started at page 1”)
- agents discovering **stale branches from older experiments**
- one agent eventually “going solo” to avoid the coordination overhead

`tools/sync_service.py` turns the protocol into something agents can **run** (not just read).

## What it does

Given your current branch `cursor/<experiment-prefix>-<id>`, it:

- **filters peers by prefix** (only branches with the same `<experiment-prefix>`)
- fetches `origin` and reads each peer’s `WORKER_STATE.md`
- scans each peer branch for completed translation files:
  - canonical: `translations/page_XXX.json`
  - legacy (still recognized): `translations/raw/page_XXX.json`, `translations/final/page_XXX.json`
- computes the **next available page** (not completed and not claimed by an online worker)

## Commands (copy/paste)

### 1) See the current team + progress

```bash
python3 tools/sync_service.py status
```

### 2) Get the next available page

```bash
python3 tools/sync_service.py next-page
```

### 3) Check if a specific page is available

```bash
python3 tools/sync_service.py check-page 37
```

Machine-readable:

```bash
python3 tools/sync_service.py check-page 37 --json
```

### 4) Write a cache file (optional)

This writes `.sync/state.json` in the repo root.

```bash
python3 tools/sync_service.py scan
```

### 5) Run a daemon (optional)

For long sessions, you can keep `.sync/state.json` updated every minute:

```bash
python3 tools/sync_service.py daemon --interval-s 60 &
```

## Important assumptions

- **WORKER_STATE format**: `tools/sync_service.py` expects the simple template fields:
  - `- **Heartbeat**: <unix_ts>`
  - `- **Status**: ...`
  - `- **Claimed Page**: <n|none>`

If agents “invent a new WORKER_STATE format”, coordination becomes non-executable again.

## Tuning

- **online/offline threshold**: default is 10 minutes.

```bash
python3 tools/sync_service.py status --online-max-age-s 1200
```

