# Project State

**Multi-Agent Collaborative Translation**

---

## How to Check Active Workers

```bash
git fetch origin --prune

for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
  if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null 2>&1; then
    short_id=$(echo "$branch" | grep -oE '[^-]+$' | tail -c 5)
    heartbeat=$(git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | grep -oP 'Heartbeat: \K[0-9]+' | head -1)
    now=$(date +%s)
    age=$((now - heartbeat))
    if [ $age -lt 600 ]; then
      echo "ONLINE:  $short_id (heartbeat ${age}s ago)"
    else
      echo "OFFLINE: $short_id (heartbeat ${age}s ago)"
    fi
  fi
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
- `extracted/full.txt` - complete book text

### Research Documents
- `research/durov_bio.md` - Pavel Durov biography
- `research/vk_history.md` - VKontakte history
- `research/russia_context.md` - Cultural context
- `research/chapter_summaries.md` - Chapter summaries
- `research/glossary.md` - Terminology guide

### Example Translations (Format Reference Only)
- `examples/page_013_translation.json`
- `examples/page_043_translation.json`

**Note**: Examples show format only, not complete translations.

### PDF Generation Tools
- `tools/compile_pages.py` - JSON to PDF compiler
- `tools/README.md` - Tool documentation

---

## Translation Output Location

Workers save translations to:
```
translations/
├── page_001.json
├── page_002.json
└── ...
```

Generated PDFs go to:
```
output/
├── page_001.pdf
├── page_002.pdf
└── ...
```

---

## Protocol Summary

1. **Register**: Create WORKER_STATE.md to join the team
2. **Sync**: Fetch other workers every 2-3 minutes
3. **Claim**: Take lowest available page, push immediately
4. **Translate**: Russian → English, Chinese, Japanese
5. **Complete**: Save JSON, push, claim next page
6. **Repeat**: Until all 99 pages are done

See `PROTOCOL.md` for full details.

---

## Timeouts

| Situation | Threshold |
|-----------|-----------|
| Worker considered offline | 10 min stale heartbeat |
| Page can be reclaimed | 15 min after worker goes offline |
| Sync frequency | 2-3 minutes |
| Heartbeat update | At least every 5 min |

---

*Each worker maintains their own `WORKER_STATE.md` for detailed status.*
