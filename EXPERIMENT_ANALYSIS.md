# Experiment Analysis: Multi-Agent Parallel Work

**Date**: February 2026
**Experiments analyzed**: 2 rounds, 32 total agents
**Repository**: Durov Code book translation project

---

## Experiment Overview

Two rounds of 16 parallel AI agents were launched to collaboratively translate a 99-page Russian book into English, Chinese, and Japanese. Both rounds revealed severe parallelism failures.

---

## Round 1: `book-translation-multi-agent-*` (16 branches)

### Timeline

All 16 agents started simultaneously at ~04:30 UTC on Jan 1, 2026.

| Agent ID | Commits | Translations | Duration (min) | Outcome |
|----------|---------|-------------|----------------|---------|
| c68e | 33 | 31 | 97 | **Primary worker** -- translated pages 6-36 |
| 14ce | 22 | 126* | 55 | Translated pages 8-22 (126 includes PDFs) |
| c3ab | 12 | 107* | 33 | Translated pages 7-12 (107 includes PDFs) |
| 991c | 16 | 6 | 16 | Pages 1-4 |
| f6c8 | 13 | 2 | 17 | Pages 5-6 |
| e5f7 | 10 | 4 | 14 | Pages 2-3 |
| 6d12 | 12 | 0 | 16 | Stuck in M1, claimed page 1 then died |
| 655c | 7 | 0 | 12 | Stuck building verification tools |
| 7ae4 | 6 | 0 | 12 | Stuck in M1 format voting |
| 4e64 | 6 | 2 | 9 | Stuck waiting for M1 consensus |
| 81f0 | 4 | 2 | 7 | Stuck in M1 |
| e545 | 1 | 104 | 0 | Single bulk commit (likely copied work) |
| 49ab | 1 | 0 | 0 | Registered, never produced output |
| 19b6 | 1 | 2 | 0 | Single commit |
| 8e97 | 1 | 0 | 0 | Single commit |
| de92 | 1 | 0 | 0 | Single commit |

*Translation counts include both JSON and PDF files.

### Key Observations

1. **Only 3 of 16 agents did meaningful translation work** (c68e, 14ce, c3ab)
2. **c68e single-handedly translated 31 pages** while 13 agents produced 0-6 pages each
3. **8 agents got stuck in M0/M1 phases** doing redundant setup work
4. **4 agents made only 1 commit** and never engaged with the protocol
5. All agents independently performed the same setup (text extraction, research, format exploration)
6. The consensus-voting mechanism for format selection created deadlocks

### Time Waste Analysis

Every agent spent 10-18 minutes on redundant work before any translation:
- M0 (setup): 5-10 min per agent (installing deps, extracting text, writing research)
- M1 (format): 5-10 min per agent (exploring LaTeX vs Python, creating demos, voting)
- By the time M2 (translation) started, most agents had exhausted their context

**Estimated waste**: 13 agents x 15 min of non-productive work = **195 minutes** of agent time wasted on duplicate setup.

---

## Round 2: `collaborative-translation-initiation-*` (16 branches)

### Timeline

Started after protocol revision, all agents launched at ~07:17 UTC on Jan 1, 2026.

| Agent ID | Commits | Translations | Duration (min) | Outcome |
|----------|---------|-------------|----------------|---------|
| ba2f | 18 | 99 | 266 | **Completed entire book alone** |
| f4a6 | 88 | 85 | 230 | 85 pages, good quality |
| d536 | 51 | 49 | 139 | 49 pages, some quality issues |
| b9fb | 64 | 62 | 104 | 62 pages (38-99 range) |
| 8fb2 | 39 | 38 | 106 | 38 pages (37-77 range) |
| 7030 | 26 | 11 | 22 | Died after 22 min |
| 4900 | 24 | 12 | 14 | Pages 1-12, died |
| 5aa9 | 21 | 10 | 18 | Died after 18 min |
| 02bd | 19 | 9 | 13 | Died after 13 min |
| a361 | 16 | 7 | 10 | Died after 10 min |
| 056e | 12 | 5 | 11 | Died after 11 min |
| 37cb | 8 | 3 | 2 | Copyright refusal |
| 82a5 | 1 | 5 | 0 | Single commit |
| 723f | 1 | 4 | 0 | Single commit |
| 6050 | 1 | 3 | 0 | Single commit |
| 7e4a | 1 | 1 | 0 | Single commit |

### Key Observations

1. **ba2f completed all 99 pages alone** in 266 minutes (4.4 hours)
2. **Massive duplication**: Page 2 was translated by 11 different agents
3. **Only 5 agents worked longer than 20 minutes**
4. **11 agents died within 22 minutes**, most within 14 minutes
5. The 5 long-lived agents produced a combined ~333 translation files for 99 pages (3.4x duplication)
6. Agents still discovered wrong-experiment branches, confusing their state awareness

### Duplication Analysis

| Pages | Times Translated | Waste Factor |
|-------|-----------------|--------------|
| 1-12 | 5-11 times each | Very high |
| 13-36 | 3-5 times each | High |
| 37-77 | 2-4 times each | Moderate |
| 78-99 | 1-2 times each | Low |

**All agents started from page 1**, causing early pages to have extreme duplication while later pages had less.

---

## Root Cause Analysis

### 1. Phased Pipeline (M0 → M1 → M2)

**Impact**: 13/16 agents in Round 1 never reached translation.

The protocol required all agents to independently complete:
- M0: Install dependencies, extract PDF text, write 5+ research documents
- M1: Explore LaTeX/Python PDF approaches, create demo pages, cast format votes, wait for consensus
- M2: Actually translate

Each phase took 10-15 minutes. Agents with limited context (or that hit errors) died in M0 or M1.

**Fix in v3**: No phases. All setup is pre-completed. Agents start producing immediately.

### 2. Consensus/Voting Deadlock

**Impact**: 8/16 agents in Round 1 got stuck waiting for votes.

The protocol required 50% of agents to agree on a format approach before translation could begin. But with agents dying at different rates, quorum was never reliably achieved.

**Fix in v3**: No consensus mechanism. Everything is pre-decided. Zero blocking dependencies.

### 3. Same Starting Point

**Impact**: 11/16 agents in Round 2 translated page 2.

Every agent used the rule "claim the lowest available page," which meant they all started at page 1. Since sync was imperfect and agents started simultaneously, they all raced for the same pages.

**Fix in v3**: Deterministic starting offset computed from branch ID hash. With 16 agents and 99 pages, agents naturally spread ~6 pages apart.

### 4. Short Agent Lifespan

**Impact**: 11/16 agents in Round 2 died within 22 minutes.

Agents ran out of context, hit errors, or stopped for unknown reasons. The protocol didn't account for agents having short lives.

**Fix in v3**: Strong continuous-execution language. Minimal overhead. Every second counts.

### 5. Wrong-Experiment Branch Discovery

**Impact**: Multiple agents built incorrect world models.

Agents running `git branch -r | grep 'origin/cursor/'` discovered branches from ALL experiments, not just the current one. They saw stale heartbeats, wrong page claims, and ghost workers.

**Fix in v3**: Mandatory experiment-prefix filtering in all branch discovery commands.

### 6. Redundant Work Without Value

**Impact**: ~195 agent-minutes wasted in Round 1 on setup.

Every agent independently extracted PDF text (already done), wrote biography/history/context research (already provided), and explored PDF generation tools (already implemented). This work was both redundant across agents AND redundant with pre-existing resources.

**Fix in v3**: Explicit prohibition against setup work, research, tool building. All resources are pre-provided.

---

## What Worked

1. **Simple claim-and-produce loop**: Agents that skipped the protocol overhead and just translated pages (c68e, ba2f) were by far the most productive
2. **Git-based state sharing**: The commit + push mechanism for sharing state fundamentally works
3. **File-existence checking**: Checking for output files is more reliable than parsing state files
4. **Independent branches**: Each agent having its own branch eliminated merge conflicts entirely
5. **Translation quality was acceptable**: The actual translation output was usable, the problem was purely coordination

---

## Quantitative Summary

| Metric | Round 1 | Round 2 |
|--------|---------|---------|
| Total agents | 16 | 16 |
| Agents that produced >10 units | 3 | 5 |
| Agents that died in < 15 min | 10 | 11 |
| Agent that did the most work | c68e (31 pages) | ba2f (99 pages) |
| Duplication factor (pages translated / unique pages) | ~2x | ~3.4x |
| Time to complete all 99 pages | Not completed | 266 min (by 1 agent) |
| Effective parallelism (productive agents / total agents) | 19% | 31% |
| Time wasted on setup/coordination (per agent, avg) | 15 min | 5 min |

---

## Recommendations Implemented in Protocol v3

1. **Zero setup overhead**: All resources pre-provided, agents start producing in < 60 seconds
2. **Deterministic work scattering**: Starting offset from branch ID hash, not sequential from 1
3. **No phases, no consensus, no voting**: Single continuous produce loop
4. **Experiment-prefix isolation**: Only discover branches from current experiment
5. **File-existence based progress tracking**: Check output files, not state files
6. **Strong continuous-execution language**: Explicit "do not stop" instructions repeated multiple times
7. **Minimal state file**: Optional, lightweight, no complex formatting
8. **Duplicate tolerance**: Accept < 10% duplication as cheaper than coordination
9. **Generic design**: Protocol is task-agnostic, adaptable to any parallel work
10. **Pocket reference**: Full protocol fits on one card for quick agent absorption
