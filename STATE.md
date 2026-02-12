# Project State

**Multi-Agent Parallel Translation — Stripe Protocol v2.0**

---

## Book

- **Title**: Код Дурова. Реальная история «ВКонтакте» и ее создателя
- **Author**: Николай В. Кононов (Nikolai V. Kononov)
- **Total Pages**: 99
- **Languages**: Russian → English, Chinese, Japanese

## Chapter Map

| Ch | Pages | Title |
|----|-------|-------|
| 0 | 1-4 | Front Matter |
| 0 | 5-6 | Предисловие (Preface) |
| 0 | 7-12 | Пролог (Prologue) |
| 1 | 13-22 | Ботанический сад |
| 2 | 23-37 | University years |
| 3 | 38-50 | VK founding |
| 4 | 51-64 | Growth |
| 5 | 65-78 | Conflicts |
| 6 | 79-91 | Philosophy |
| 7 | 92-98 | Future |
| - | 99 | About Author |

## Resources (Pre-Done)

| Resource | Location |
|----------|----------|
| Source text | `extracted/pages/page_001.txt` ... `page_099.txt` |
| Full text | `extracted/full.txt` |
| Glossary | `research/glossary.md` |
| Chapter summaries | `research/chapter_summaries.md` |
| Durov bio | `research/durov_bio.md` |
| VK history | `research/vk_history.md` |
| Cultural context | `research/russia_context.md` |
| Format examples | `examples/page_013_translation.json`, `page_043_translation.json` |
| PDF compiler | `tools/compile_pages.py` |
| Stripe calculator | `tools/compute_stripe.py` |

## How to Check Progress

```bash
# See global progress
python3 tools/compute_stripe.py --status

# See your assigned pages
python3 tools/compute_stripe.py

# Get next page to work on
python3 tools/compute_stripe.py --next
```

## Protocol

See `PROTOCOL.md` — Stripe-based parallel assignment with scavenge phase.

Key points:
1. Translate from minute zero (no setup phases)
2. Your pages are deterministic (computed from your ID)
3. Push after every page
4. After stripe is done, scavenge unclaimed pages
