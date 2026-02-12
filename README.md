# Multi-Agent Parallel Work Protocol

This repository contains a **battle-tested protocol for parallel multi-agent collaboration**, designed after analyzing 32 agent sessions across 2 experiments that revealed critical coordination failures.

## The Problem

When multiple AI agents work in parallel on the same project (e.g., translating a 99-page book), naive coordination protocols produce **76% wasted effort** through duplicate work, setup phase bloat, and consensus deadlock. In our experiments:

- Pages 2 and 3 were each translated **11 times** by different agents
- **56% of agents** (9/16) produced zero useful output
- **1 agent** ended up translating the entire book alone
- Agents spent their sessions on research and voting instead of the actual task

## The Solution

The `PROTOCOL.md` in this repo implements a **stripe-based parallel work protocol** that eliminates these failures:

1. **Deterministic work assignment** — Each agent gets a pre-computed, non-overlapping set of pages (a "stripe") based on its ID. Zero coordination needed for initial work.
2. **No setup phases** — Agents translate from minute zero. All research, format decisions, and tooling are pre-done.
3. **Two-phase design** — STRIPE (parallel, no coordination) then SCAVENGE (fill gaps from dead agents).
4. **File existence as coordination signal** — Instead of parsing complex state files, agents scan for output files across branches.

### Expected improvement:

| Metric | Old Protocol | New Protocol |
|--------|-------------|--------------|
| Wasted effort | 76% | < 5% |
| Agent utilization | 44% (7/16 active) | > 90% |
| Setup time per agent | 60-120 min | < 2 min |
| Pages translated per agent | 0-6 (median 1) | ~6-8 each |

## Repository Structure

```
PROTOCOL.md                  # The parallel work protocol (START HERE)
instructions.md              # Task-specific instructions (translation details)
STATE.md                     # Project state reference
WORKER_STATE_TEMPLATE.md     # Template for agent registration

tools/
├── compute_stripe.py        # Stripe calculator and progress scanner
├── compile_pages.py         # JSON → PDF compiler
└── README.md                # Tool documentation

extracted/                   # Source material (pre-extracted text)
research/                    # Background research (pre-done)
examples/                    # Output format examples
translations/                # Agent output (one JSON per page)
output/                      # Generated PDFs
```

## Using This Protocol

### For a new multi-agent project:

1. Pre-complete all setup work (research, format decisions, tooling)
2. Adapt `PROTOCOL.md` to your task (replace page references with your work units)
3. Set `TOTAL_PAGES` in `tools/compute_stripe.py` to your total work unit count
4. Launch N agents on branches `cursor/your-project-XXXX`
5. Each agent reads `PROTOCOL.md`, computes its stripe, and starts working

### For an agent joining this project:

1. Read `PROTOCOL.md` (the parallel work protocol)
2. Run `python3 tools/compute_stripe.py` to see your assigned pages
3. Start translating your first stripe page immediately
4. Push after each page. Sync between pages. Never stop voluntarily.

## Experiment History

This protocol was developed by analyzing failures from two experiments:

### Experiment 1: `book-translation-multi-agent-*` (16 agents)
- 5/16 agents never started (setup failures)
- 4/16 agents stuck in format voting (consensus deadlock)
- 3/16 agents did significant work
- 1 agent (c68e) translated 30+ pages alone

### Experiment 2: `collaborative-translation-initiation-*` (16 agents)
- 76% duplicate work (307/406 page-translations were duplicates)
- 1 agent (ba2f) translated all 99 pages by itself
- Pages 2-3 translated 11 times each
- 4/16 agents produced only 1 commit

See `PROTOCOL.md` for the full post-mortem and the protocol designed to fix these issues.
