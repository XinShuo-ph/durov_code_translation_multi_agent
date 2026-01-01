# Multi-Agent Coordination Protocol v2.0

## Design Philosophy

This protocol is designed based on lessons learned from the first 16-agent run. The key insight: **simpler is better**. Workers that ignored the complex consensus protocol and just started translating were the most productive.

### Core Principles

1. **Independence First**: Each worker can complete their task without any other worker
2. **No Blocking Dependencies**: Never wait for consensus, votes, or other workers
3. **Graceful Degradation**: Works correctly with 1 worker or 100 workers
4. **Simple Communication**: Git commits are informational, not required for progress
5. **Conflict Tolerance**: Duplicate work is acceptable, better than no work

---

## What Failed in v1.0

| v1.0 Requirement | Problem | v2.0 Solution |
|------------------|---------|---------------|
| Wait for 50% consensus on format | Workers deadlocked waiting | No consensus - use any working tool |
| M0 → M1 → M2 → M3 phases | Workers stuck between phases | Single phase: translate |
| Sync every 60-120 seconds | Workers that couldn't sync were blocked | Sync is optional |
| Claim pages via git before translating | Race conditions, duplicates | Claim via file existence |
| 16-worker quorum assumptions | Fewer workers couldn't proceed | Works with any N ≥ 1 |

---

## Worker Lifecycle

### 1. Start (30 seconds)

```bash
# Identify yourself
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "I am: $MY_SHORT_ID"
```

### 2. Check Existing Work (30 seconds)

```bash
# What translations already exist?
ls translations/*.json 2>/dev/null | wc -l
# Find the lowest untranslated page
```

### 3. Translate (90% of your time)

Just translate pages. That's it.

### 4. Save and Commit (after each page)

```bash
git add translations/page_XXX.json
git commit -m "[SHORT_ID] Translated page XXX"
git push origin HEAD
```

### 5. Repeat

Go to step 2, find next page.

---

## Page Claiming Protocol

### The Simple Rule

**First to create `translations/page_XXX.json` claims that page.**

No pre-claiming, no broadcast, no waiting for acknowledgment.

### Finding Your Next Page

```python
# Pseudocode for finding next page to translate
def find_next_page():
    all_pages = set(range(1, 100))  # Pages 1-99
    
    # Check local filesystem
    existing = set()
    for f in glob("translations/page_*.json"):
        page_num = extract_page_number(f)
        existing.add(page_num)
    
    available = sorted(all_pages - existing)
    if available:
        return available[0]  # Lowest available
    return None  # All done!
```

### Handling Duplicates

If two workers translate the same page:
1. **Both keep their work** - both versions are committed to their branches
2. **Final merge decides** - during final assembly, one version is chosen
3. **No conflict during work** - workers don't need to coordinate

This is intentional. Losing a small amount of work to duplicates is better than workers blocking each other.

---

## Git Communication (Optional)

### When to Commit

| Event | Commit? | Push? |
|-------|---------|-------|
| Completed a page translation | Yes | Yes |
| Starting a new page | No | No |
| Every 5 pages | Yes (batch) | Yes |
| End of session | Yes | Yes |

### Commit Message Format

Simple and parseable:

```
[SHORT_ID] Translated page XXX

Optional details
```

Examples:
```
[c68e] Translated page 23

Chapter 2 - University years, Durov's early programming
```

```
[14ce] Translated pages 15-18

Batch commit: Chapter 1 completion
```

### What NOT to Commit

- ❌ "Starting work on page X"
- ❌ "Waiting for consensus"
- ❌ "M0 complete, M1 starting"
- ❌ Empty state updates

---

## WORKER_STATE.md (Optional)

Maintaining a worker state file is optional but helpful for visibility.

### Minimal Format

```markdown
# Worker: [SHORT_ID]

## Status
- Branch: [branch name]
- Last Active: [timestamp]
- Pages Translated: [count]

## Completed Pages
1, 2, 3, 4, ...

## Currently Working On
Page 5
```

### When to Update
- After completing each page (optional)
- At end of session (recommended)

---

## Handling Worker Loss

The protocol is designed to be robust to worker loss:

### If a Worker Disappears

1. **Their completed work is preserved** in their branch
2. **Their in-progress page** is NOT pre-claimed, so others can translate it
3. **No coordination required** to continue without them

### If Most Workers Disappear

1. **Remaining workers continue normally**
2. **No quorum requirements** - one worker can finish the project alone
3. **Final assembly works with any set of completed pages**

### If All Workers Disappear

1. **All committed work is preserved** in branches
2. **New workers can pick up** by checking existing translations/
3. **No state file required** to resume

---

## Conflict Resolution

### Same Page Translated by Multiple Workers

Both translations are kept. Resolution happens at merge time:
1. Compare both JSONs
2. Choose the more complete one (more sentences)
3. If equal, choose by branch name (alphabetically first)

### Different Translation Quality

No runtime resolution. Quality review happens post-hoc.

### Git Push Conflicts

```bash
# If push fails
git pull --rebase origin HEAD
git push origin HEAD
```

This should be rare since workers are modifying different files.

---

## No Consensus Needed

### Format/Tools
Each worker uses whatever PDF/text extraction and JSON generation tools work in their environment. The only requirement is the JSON output format.

### Color Scheme
Not needed at the translation stage. Colors are applied during final PDF generation.

### Page Assignment
Workers self-assign by checking what's already translated. No voting.

---

## Timeout Rules

### There Are None

Workers don't need to timeout on anything:
- No waiting for other workers
- No waiting for votes
- No waiting for consensus
- No waiting for sync

If you're waiting, **you're doing it wrong**. Just translate.

---

## Final Assembly

When all pages are translated:

1. **Any worker can assemble** - first to do it wins
2. **Collect all page_XXX.json** from all branches
3. **Handle duplicates** by choosing one version
4. **Generate final output** (PDF or combined JSON)

### Assembly Trigger

Assembly happens when:
- All 99 page JSONs exist, OR
- Designated deadline reached, OR
- Manual trigger

---

## Quick Reference

### Your Job

1. Find untranslated page (lowest number)
2. Read extracted text from `extracted/pages/page_XXX.txt`
3. Translate to EN, ZH, JA
4. Save to `translations/page_XXX.json`
5. Commit and push
6. Repeat

### Not Your Job

- Voting on approaches
- Waiting for consensus
- Syncing with other workers
- Pre-claiming pages
- Writing research docs
- Extracting PDF text

### Emergency Contact

If truly stuck, add a file:
```
BLOCKED_[SHORT_ID].md
```

With description of the issue. But this should rarely be needed.

---

## Comparison: v1.0 vs v2.0

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| Start translating | After M0, M1 consensus | Immediately |
| Page claiming | Git commit broadcast | File creation |
| Worker discovery | Required, complex | Optional |
| Consensus | Required for format | None |
| Minimum workers | Implicit 16 | 1 |
| Sync frequency | Every 60-120 sec | When convenient |
| Blocking waits | Many | None |
| State file | Required | Optional |
| Setup tasks | M0 (all workers) | Pre-done |
| Format exploration | M1 (all workers) | Use any working tool |

---

## Why This Works

### Mathematical Argument

With N workers and P pages:
- v1.0: O(N) coordination overhead per page claim
- v2.0: O(1) coordination overhead (just check file existence)

### Practical Argument

The most productive workers in the first run (c68e: 29 pages, 14ce: 12 pages) were the ones that essentially ignored the protocol and just translated.

### Failure Mode Comparison

| Failure | v1.0 Result | v2.0 Result |
|---------|-------------|-------------|
| Worker crashes | Page claim orphaned, timeout needed | No effect, page remains unclaimed |
| Network issues | Worker can't participate | Worker continues locally, pushes later |
| Consensus deadlock | All workers blocked | Impossible, no consensus |
| All workers crash | Project stalls | Completed work preserved |

---

## Summary

**The protocol is: there is no protocol.**

Translate pages. Save as JSON. Commit and push. Repeat.

Everything else is optional optimization.

---

*This protocol prioritizes completion over coordination. A project with 99 pages translated (with some duplicates) is better than a project with 10 pages translated (with perfect coordination).*
