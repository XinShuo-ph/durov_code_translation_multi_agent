# Multi-Agent Parallel Work Protocol

A concise, executable protocol for coordinating N parallel AI agents on divisible tasks using git-based communication.

## The Problem

When launching 16 AI agents to work in parallel, naive "claim lowest available" protocols fail catastrophically:

- **Redundant setup**: Every agent independently re-does the same prep work (10+ min each)
- **Consensus deadlocks**: Agents wait for votes that never reach quorum because agents keep dying
- **No work spreading**: Without shared state, every agent starts at work unit 1
- **Phase gates**: Agents die during mandatory setup phases before doing any real work
- **Protocol overhead**: Long protocol documents consume agent context

In two 16-agent experiments, the top single agent translated more pages than the other 15 combined. Pages 2-4 were translated 10-11 times each while pages 37-99 were never touched.

## The Solution: Discover, Divide, Work, Fill

```
START ──► Discover peers ──► Compute pages ──► Work independently ──► Fill gaps ──► DONE
          (60 sec max)       (10 sec)          (90% of session)       (remaining)
```

1. **Discover**: One `git fetch`, sort branches, find your index
2. **Divide**: Interleaved assignment (worker k gets pages k+1, k+1+N, k+1+2N, ...)
3. **Work**: Produce output for your assigned pages. No sync needed.
4. **Fill**: Fetch all branches, find missing pages, complete them.

Key properties:
- **Zero setup**: All prep work is pre-done on `main`
- **Zero coordination during work**: Deterministic assignment eliminates conflicts
- **One sync**: Only at startup to count peers
- **Resilient**: If workers die, their orphaned pages are spread across the book, not clustered

## Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | The complete multi-agent protocol (v3) |
| `EXPERIMENT_ANALYSIS.md` | Detailed analysis of two failed 16-agent experiments |
| `instructions.md` | Task-specific instructions (translation) |

## How to Use

1. Prepare all source materials on `main` before launching agents
2. Copy `PROTOCOL.md` into your project
3. Write concise task instructions (under 200 lines)
4. Launch N agents on branches with a common prefix
5. Agents self-coordinate using the protocol

See `PROTOCOL.md` for the full protocol and adaptation guide.
