#!/bin/bash
# Helper script to mark a page as complete

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 PAGE_NUMBER"
    exit 1
fi

PAGE_NUM=$1

# Get short ID
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)

# Check if translation file exists
TRANSLATION_FILE="translations/page_${PAGE_NUM}.json"
if [ ! -f "$TRANSLATION_FILE" ]; then
    echo "Error: Translation file not found: $TRANSLATION_FILE"
    exit 1
fi

# Calculate hash
HASH=$(sha256sum "$TRANSLATION_FILE" | cut -c1-8)
echo "Translation hash: $HASH"

# Get current timestamp
NOW=$(date +%s)
ISO_NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Update WORKER_STATE.md
echo "Updating WORKER_STATE.md..."

# Clear claimed page
sed -i "s/^- \*\*Claimed Page\*\*:.*/- **Claimed Page**: none/" WORKER_STATE.md

# Add to completed pages table (insert before the empty line after table header)
# Find the table and insert new row
awk -v page="$PAGE_NUM" -v iso="$ISO_NOW" -v hash="$HASH" '
/^\| Page \| Completed At \| Hash \|/ {
    print
    next
}
/^\|------\|/ && !inserted {
    print
    print "| " page " | " iso " | " hash " |"
    inserted = 1
    next
}
{print}
' WORKER_STATE.md > WORKER_STATE.md.tmp && mv WORKER_STATE.md.tmp WORKER_STATE.md

# Update heartbeat
sed -i "s/^- \*\*Heartbeat\*\*:.*/- **Heartbeat**: $NOW/" WORKER_STATE.md

# Commit and push
echo "Committing completion of page $PAGE_NUM..."
git add "$TRANSLATION_FILE" WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] DONE: Page $PAGE_NUM
HASH: $HASH
HEARTBEAT: $NOW"
git push origin HEAD

echo "✓ Page $PAGE_NUM marked as complete"
echo ""
echo "Next: Claim next page with ./tools/claim_page.sh"
