# Worker: [SHORT_ID]

## Identity
- **Branch**: [your branch name]
- **Short ID**: [last 4 characters]
- **Started**: [timestamp]

## Progress

### Completed Pages
[List page numbers as you complete them]

Example:
- Page 13 ✅
- Page 14 ✅
- Page 15 ✅

### Current Page
[Page number you're working on]

### Total Translated
[count] pages

---

## Session Log
[Optional: brief notes about your session]

---

## How to Create Your Worker State

1. Copy this file to `WORKER_STATE.md`
2. Replace placeholders with your info:

```bash
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)
echo "Branch: $MY_BRANCH"
echo "Short ID: $MY_SHORT_ID"
```

3. Update as you translate pages (optional)
4. Commit periodically (optional)

**Note:** This file is optional. The only required output is the translation JSON files in `translations/`.

---

*Delete everything below this line after creating your WORKER_STATE.md*
