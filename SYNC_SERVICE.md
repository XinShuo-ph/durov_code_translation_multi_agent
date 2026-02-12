# Sync Service (No-Duplication + High Parallelism)

This project uses **git remote branches** as the communication bus between agents. To make parallel work reliable (and avoid “everyone translates the same pages”), we provide an **executable sync helper**:

- `tools/sync.py`: fetches `origin/*`, scans worker branches, and derives:
  - which pages are **done** (translation JSON exists anywhere)
  - which pages are **claimed** (best-effort from `WORKER_STATE.md`)
  - which pages are **reviewed** (a review note exists anywhere)
  - the **next page** for you (deterministic sharding + work stealing)

## Commands

### Refresh + cache (recommended before choosing work)

```bash
python3 tools/sync.py refresh
```

### Global status

```bash
python3 tools/sync.py status --workers
```

### Deterministic sharding (16-way parallel by default)

```bash
# next page in your shard (no collisions if all 16 agents run)
python3 tools/sync.py next --mode shard

# list all pages in your shard
python3 tools/sync.py shard
```

### Work stealing (when your shard is empty, or you’re filling gaps)

```bash
python3 tools/sync.py next --mode steal
```

### Review queue (buddy system)

By default, each slot reviews the **previous slot’s** shard (slot \(k\) reviews slot \(k-1\)).

```bash
python3 tools/sync.py review-queue
```

## Conventions this tool recognizes

- **Translations**:
  - Preferred path: `translations/page_XXX.json`
  - Legacy path supported: `translations/final/page_XXX.json`
- **Reviews**:
  - `reviews/page_XXX.<reviewer_short_id>.md`
- **Claims**:
  - Best-effort parse of `WORKER_STATE.md` (works with multiple historical formats)

## Why not a background daemon?

Some agent environments don’t reliably keep background processes alive. `tools/sync.py` is designed to be:

- fast enough to run often
- deterministic (sharding) so even imperfect syncing still yields parallel progress

