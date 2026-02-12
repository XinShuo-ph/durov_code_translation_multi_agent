# Multi-Agent Parallel Work Protocol

A battle-tested protocol for coordinating N AI agents working in parallel on divisible tasks via git branches.

## Problem

When N agents are launched simultaneously on the same task:
- Most agents waste time on redundant setup instead of producing output
- All agents race for the same starting work unit, causing massive duplication
- Agents block each other waiting for consensus or phase gates
- Short-lived agents (< 15 min) contribute nothing due to overhead
- One agent ends up doing all the work

**Observed in practice**: Across 32 agent runs, effective parallelism was only 19-31%. One agent single-handedly completed the entire 99-page task.

## Solution

Protocol v3 eliminates all coordination overhead:

| Principle | Implementation |
|-----------|---------------|
| Zero setup | All resources pre-provided, produce in < 60 seconds |
| Deterministic scattering | Start offset = hash(branch_id) mod N_units |
| No blocking | No phases, no voting, no consensus |
| File-based tracking | Check output files, not state files |
| Continuous execution | Never stop, never wait, just produce |
| Duplicate tolerance | < 10% duplication is acceptable |

## Files

| File | Description |
|------|-------------|
| `PROTOCOL.md` | The full multi-agent parallel work protocol (v3) |
| `EXPERIMENT_ANALYSIS.md` | Detailed analysis of 32 agent runs across 2 experiments |
| `AGENT_STATE_TEMPLATE.md` | Template for agent state files |

## How to Use

1. **Pre-complete all setup** for your task (tools, resources, examples)
2. **Write a `TASK.md`** describing exactly what one unit of work requires
3. **Copy `PROTOCOL.md`** into your project
4. **Set the variables**: `TOTAL_UNITS`, `BRANCH_PREFIX`, output directory
5. **Launch agents** -- each on its own branch matching the prefix
6. **Collect results** from all branches after completion

## Adapting to Your Task

The protocol is generic. Example configurations:

```
Book Translation:  unit=page,     TOTAL_UNITS=99,  output=translations/page_XXX.json
Code Migration:    unit=file,     TOTAL_UNITS=250, output=migrated/module_XXX.py
Test Generation:   unit=module,   TOTAL_UNITS=80,  output=tests/test_module_XXX.py
Data Processing:   unit=chunk,    TOTAL_UNITS=500, output=processed/chunk_XXX.csv
```

## Prior Work

This protocol was developed by analyzing:
- 16 agents on `book-translation-multi-agent-*` branches (Round 1)
- 16 agents on `collaborative-translation-initiation-*` branches (Round 2)
- The [StoneRecords translation project](https://github.com/XinShuo-ph/StoneRecords_translation_multi_agent) protocol
- Protocol v1 (phased, consensus-based) and v2 (no-protocol approach)

See `EXPERIMENT_ANALYSIS.md` for the full investigation.

## Key Insight

> The most productive agents in every experiment were the ones that ignored the coordination protocol and just started producing output. Protocol v3 codifies this: **the protocol is to minimize the protocol**.
