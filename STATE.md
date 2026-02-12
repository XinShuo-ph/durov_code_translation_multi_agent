# Project State

**Multi-Agent Parallel Translation**

---

## How to Check Status

```bash
python3 tools/coord.py --fetch status
```

Or manually:

```bash
git fetch origin --prune

BATCH_PREFIX=$(git branch --show-current | sed 's/-[^-]*$//')
for branch in $(git branch -r | grep "origin/${BATCH_PREFIX}-" | tr -d ' '); do
  echo "--- $branch ---"
  git show "${branch}:WORKER_STATE.json" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "(no state)"
done
```

---

## Book Information

- **Title**: Код Дурова. Реальная история «ВКонтакте» и ее создателя
- **Author**: Николай В. Кононов (Nikolai V. Kononov)
- **Total Pages**: 99
- **Subject**: Biography of Pavel Durov and history of VKontakte

---

## Chapter Structure

| Chapter | Pages | Title |
|---------|-------|-------|
| 0 | 1-4 | Front Matter (title, contents) |
| 0 | 5-6 | Предисловие (Preface) |
| 0 | 7-12 | Пролог (Prologue) |
| 1 | 13-22 | Ботанический сад (Botanical Garden) |
| 2 | 23-37 | Chapter 2 - University years |
| 3 | 38-50 | Chapter 3 - VK founding |
| 4 | 51-64 | Chapter 4 - Growth |
| 5 | 65-78 | Chapter 5 - Conflicts |
| 6 | 79-91 | Chapter 6 - Philosophy |
| 7 | 92-98 | Chapter 7 - Future |
| - | 99 | About Author |

---

## Resources Available

### Pre-Extracted Text
- `extracted/pages/page_001.txt` through `page_099.txt`
- `extracted/full.txt` — complete book text

### Research Documents
- `research/durov_bio.md` — Pavel Durov biography
- `research/vk_history.md` — VKontakte history
- `research/russia_context.md` — Cultural context
- `research/chapter_summaries.md` — Chapter summaries
- `research/glossary.md` — Terminology guide

### Example Translations (Format Reference Only)
- `examples/page_013_translation.json`
- `examples/page_043_translation.json`

**Note**: Examples show format only, not complete translations.

### Tools
- `tools/coord.py` — Coordination tool for Phase 2 scavenging + status
- `tools/validate_translation.py` — Translation JSON validator
- `tools/compile_pages.py` — JSON to PDF compiler

---

## Translation Output Location

Workers save translations to:
```
translations/page_XXX.json
```

Optional PDF output:
```
output/page_XXX.pdf
```

Review notes (during balance gate HOLD):
```
reviews/page_XXX.<worker_id>.md
```

---

## Protocol Summary

1. **Phase 1 — STRIPE**: Each worker translates their deterministic page set (no coordination)
2. **Phase 2 — SCAVENGE**: Fill remaining gaps using `tools/coord.py`
3. **Balance Gate**: Fast workers review peers before claiming more pages
4. **Validate**: Every page validated before pushing
5. **Push**: After every completed page

See `PROTOCOL.md` for full details.

---

## Timeouts

| Situation | Threshold |
|-----------|-----------|
| Worker considered offline | 10 min stale heartbeat |
| Claim reclaimable | 15 min after worker goes offline |
| Push after completion | Immediate |

---

*Each worker maintains `WORKER_STATE.json` on their branch for real-time status.*
