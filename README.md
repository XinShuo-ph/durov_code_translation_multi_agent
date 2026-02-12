# Multi-Agent Parallel Work Protocol

A battle-tested protocol for coordinating multiple AI agents working in parallel on independent git branches.

## The Problem

When N AI agents start simultaneously on separate git branches, they must divide work without duplicating effort. But there's no shared mutable state — each agent has its own branch, and git-based communication has multi-second latency.

Naive approaches ("claim the lowest available unit") produce catastrophic duplication: in real experiments with 16 agents, pages 2-3 were each translated by **11 agents**. 77% of all work was wasted.

## The Solution

**Hash-partitioned deterministic assignment.** Each agent derives a unique starting position from its branch name and works forward from there. No claiming, no voting, no state files. Agents push completed work to their branch and periodically sync to skip units that others have already finished.

```
1. start = hash(branch_suffix) % total_units + 1
2. Work forward from start, wrapping at the end
3. Push after every completed unit
4. Sync every ~5 units to skip what others finished
5. Keep going until everything is done
```

## Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | The complete protocol specification |
| `ANALYSIS.md` | Data-driven analysis of previous 16-agent experiments |

## Results from Analysis

| Metric | Old Protocol | New Protocol (projected) |
|--------|-------------|------------------------|
| Startup overhead | 10-20 min/agent | < 1 min/agent |
| Page duplication | 77% waste | ~2% waste |
| Agent utilization | 3 of 16 productive | All productive agents contribute unique work |
| Effective speedup | 1.5-3x with 16 agents | ~15x with 16 agents |

## Applicability

This protocol works for any embarrassingly parallel workload: translation, code generation, data processing, testing, document review — anything that can be divided into numbered independent units with file-based output.

## Origin

Developed after analyzing two failed 16-agent translation experiments on "Durov Code" (Nikolai Kononov) and incorporating lessons from the [StoneRecords multi-agent translation project](https://github.com/XinShuo-ph/StoneRecords_translation_multi_agent/).
