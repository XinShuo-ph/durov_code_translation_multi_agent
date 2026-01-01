# Durov Code Book Translation Project

**Multi-Agent Parallel Translation System with 16 Workers**

## Overview

This project translates "Код Дурова" (Durov Code) by Nikolai Kononov into a multilingual edition featuring Russian, English, Chinese, and Japanese in parallel.

## Multi-Agent Architecture

This project uses **16 AI agents working in parallel**, each on their own git branch:

```
worker/01/durov-translation
worker/02/durov-translation
...
worker/16/durov-translation
```

### Communication Method

Agents communicate via **git commits, pushes, and pulls**—using git as a message-passing interface (similar to MPI for distributed computing).

### Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | Communication protocol for inter-agent coordination |
| `instructions.md` | Detailed task instructions and workflows |
| `STATE.md` | Global project state (shared) |
| `WORKER_STATE.md` | Individual worker state (per branch) |
| `WORKER_STATE_TEMPLATE.md` | Template for new workers |

## Quick Start for Workers

1. **Identify yourself**: Check your branch name to determine worker ID
2. **Create WORKER_STATE.md**: Copy from template and update
3. **Sync with others**: Fetch all worker branches
4. **Broadcast**: Commit and push your initial state
5. **Begin work**: Follow instructions.md for your milestone

## Project Milestones

| Milestone | Description | Execution Mode |
|-----------|-------------|----------------|
| M0 | Setup & Research | Parallel (all workers) |
| M1 | Format Exploration | Parallel with consensus |
| M2 | Translation (99 pages) | Parallel page assignment |
| M3 | Final Assembly | Leader + verifiers |

## Target Output

A multilingual PDF where each original Russian page is followed by 1-2 pages of translation, with each sentence appearing in four languages, color-coded:

- **Russian**: Black
- **English**: Blue  
- **Chinese**: Red
- **Japanese**: Green

## Communication Frequency

- **Pull all branches**: Every 60-120 seconds
- **Push updates**: After every significant action
- **Heartbeat**: Every 5 minutes minimum

## Files

- `durov_code_book.pdf` - Original Russian book (99 pages)
- `PROTOCOL.md` - Communication protocol
- `instructions.md` - Detailed instructions
- `STATE.md` - Global state
- `WORKER_STATE.md` - Your worker state

---

*See `PROTOCOL.md` for detailed communication rules and `instructions.md` for task details.*
