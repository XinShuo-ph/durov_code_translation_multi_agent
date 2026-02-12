# Project State Reference

This file is informational. Runtime coordination is handled by:

```bash
python3 tools/parallel_coord.py status
```

## Runtime Commands

```bash
# Full snapshot (recommended)
python3 tools/parallel_coord.py --fetch status

# Next page recommendation
python3 tools/parallel_coord.py --fetch next --worker "$MY_SHORT_ID"

# Check a specific page
python3 tools/parallel_coord.py --fetch check --page 23
```

## Book Metadata

- Title: `Код Дурова. Реальная история «ВКонтакте» и ее создателя`
- Author: Nikolai V. Kononov
- Total pages: 99

## Chapter Structure

| Chapter | Pages | Title |
|---------|-------|-------|
| 0 | 1-4 | Front matter |
| 0 | 5-6 | Предисловие (Preface) |
| 0 | 7-12 | Пролог (Prologue) |
| 1 | 13-22 | Ботанический сад |
| 2 | 23-37 | University years |
| 3 | 38-50 | VK founding |
| 4 | 51-64 | Growth |
| 5 | 65-78 | Conflicts |
| 6 | 79-91 | Philosophy |
| 7 | 92-98 | Future |
| - | 99 | About the author |

