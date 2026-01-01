# Durov Code Book Translation Project

**Multi-Agent Parallel Translation System**

## Overview

This project translates "Код Дурова" (Durov Code) by Nikolai Kononov into a multilingual edition featuring Russian, English, Chinese, and Japanese in parallel.

## Multi-Agent Architecture

This project uses **multiple AI agents working in parallel**, each on their own git branch.

### Branch Discovery (Dynamic)

Branches are created by Cursor with random names like:
```
cursor/multi-agent-parallel-translation-cca9
cursor/durov-book-translation-plan-7379
cursor/some-task-description-xxxx
```

**Active workers** are identified by the presence of `WORKER_STATE.md` on their branch.

### Communication Method

Agents communicate via **git commits, pushes, and pulls**—using git as a message-passing interface (similar to MPI for distributed computing).

### Worker Identity

- **Branch Name**: Full branch name (e.g., `cursor/multi-agent-parallel-translation-cca9`)
- **Short ID**: Last 4 characters (e.g., `cca9`) - used in commit messages

### Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL.md` | Communication protocol for inter-agent coordination |
| `instructions.md` | Detailed task instructions and workflows |
| `STATE.md` | Global project state (shared) |
| `WORKER_STATE.md` | Individual worker state (per branch) - **REGISTERS worker** |
| `WORKER_STATE_TEMPLATE.md` | Template for new workers |

## Quick Start for Workers

1. **Identify yourself**:
   ```bash
   MY_BRANCH=$(git branch --show-current)
   MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
   echo "I am: $MY_SHORT_ID on branch $MY_BRANCH"
   ```

2. **Create WORKER_STATE.md**: Copy from template and fill in your info

3. **Commit and push**: This registers you as an active worker!

4. **Discover other workers**:
   ```bash
   git fetch origin --all --prune
   for b in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||'); do
     git show "origin/${b}:WORKER_STATE.md" &>/dev/null && echo "Active: $b"
   done
   ```

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

## Consensus

- Quorum = >50% of **active workers** (those with WORKER_STATE.md)
- Not a fixed number - based on who's online

## Files

- `durov_code_book.pdf` - Original Russian book (99 pages)
- `PROTOCOL.md` - Communication protocol
- `instructions.md` - Detailed instructions
- `STATE.md` - Global state
- `WORKER_STATE.md` - Your worker state (create this!)

---

*See `PROTOCOL.md` for detailed communication rules and `instructions.md` for task details.*
