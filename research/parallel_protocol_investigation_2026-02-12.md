# Multi-Agent Parallelism Investigation (16 Branches)

Date: 2026-02-12  
Scope: `origin/cursor/book-translation-multi-agent-*` (16 branches)

## Executive Summary

Translation quality was generally acceptable on completed pages, but collaboration quality was poor:

- Only **3/16 workers** produced sustained page output.
- **1 worker (c68e)** became the sole active translator in the end.
- Work was duplicated on many pages, while large page ranges were untouched.

This confirms the concern: the prior protocol did not maintain true parallel execution.

## Observed Metrics

### 1) Contribution skew

- Branches analyzed: **16**
- Pages produced per branch (tip snapshot):
  - `c68e`: 31 pages
  - `14ce`: 14 pages
  - `c3ab`: 8 pages
  - `991c`: 4 pages
  - `e5f7`: 4 pages
  - `19b6`, `4e64`, `81f0`, `e545`, `f6c8`: 2 pages each
  - `49ab`, `655c`, `6d12`, `7ae4`, `8e97`, `de92`: 0 pages
- Median pages/branch: **2**
- Branches with 0 pages: **6**
- Branches with >= 8 pages: **3**

### 2) Coverage and duplication

- Total page files produced across all branches: **71**
- Unique pages covered: **37** (pages 1-43 only)
- Duplicate output volume: **34/71 artifacts** (~48%)
- Pages duplicated most:
  - Page 13: 7 branches
  - Page 43: 7 branches
  - Pages 8, 10, 11, 12: 3-4 branches

### 3) Time-series collapse to one worker

Distinct active translators in 10-minute buckets dropped as follows:

- Early run: 4-7 active workers per bucket
- Mid run: 2 workers (`14ce`, `c68e`)
- Final ~40 minutes: **1 worker only (`c68e`)**

In the final 30 minutes of translation commits, only `c68e` committed translation work.

## Root Causes

1. **No enforceable fairness rule**
   - Fast workers could continue claiming indefinitely while slower workers remained online.
   - No lead cap, no per-worker progress floor.

2. **State format drift**
   - `WORKER_STATE.md` evolved into incompatible, ad hoc formats.
   - Machine-readable coordination degraded.

3. **Pre-claim checks were advisory, not mandatory**
   - Protocol said "sync first", but had no executable gate that blocked unsafe claims.

4. **No automatic reclaim workflow**
   - Offline/stale claims were defined in prose but not enforced by tooling.

5. **Protocol too long and under-constrained operationally**
   - Agents could satisfy local interpretation while violating team-level parallelism goals.

## Protocol Design Requirements (Derived)

The replacement protocol must be:

1. **Concise**: short enough to follow under pressure.
2. **Executable**: command-level checks before claiming work.
3. **Machine-checkable**: strict, parseable worker state fields.
4. **Fairness-aware**: prevent one worker from running far ahead when peers are online.
5. **Fail-safe**: degrade gracefully to solo mode when peers truly go offline.

## Implemented Response

This investigation led to:

- `PROTOCOL.md` rewritten as a concise executable protocol
- `tools/coord.py` added for status/next/stale coordination commands
- `WORKER_STATE_TEMPLATE.md` replaced with strict machine-parseable schema

