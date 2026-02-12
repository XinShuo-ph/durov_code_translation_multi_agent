#!/bin/bash
# Helper script to claim a page

set -e

# Get short ID
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)

# Get next available page from daemon
echo "Querying sync daemon for next available page..."
NEXT_PAGE=$(python3 tools/sync_daemon.py --next-page)

if [ -z "$NEXT_PAGE" ]; then
    echo "Error: No pages available"
    exit 1
fi

echo "Next available page: $NEXT_PAGE"

# Update WORKER_STATE.md
echo "Updating WORKER_STATE.md..."

# Get current timestamp
NOW=$(date +%s)
ISO_NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Update the claimed page field
sed -i "s/^- \*\*Claimed Page\*\*:.*/- **Claimed Page**: $NEXT_PAGE/" WORKER_STATE.md
sed -i "s/^- \*\*Started At\*\*:.*/- **Started At**: $ISO_NOW/" WORKER_STATE.md
sed -i "s/^- \*\*Heartbeat\*\*:.*/- **Heartbeat**: $NOW/" WORKER_STATE.md
sed -i "s/^- \*\*Currently working on\*\*:.*/- **Currently working on**: Page $NEXT_PAGE/" WORKER_STATE.md

# Commit and push immediately
echo "Claiming page $NEXT_PAGE..."
git add WORKER_STATE.md
git commit -m "[$MY_SHORT_ID] CLAIM: Page $NEXT_PAGE
HEARTBEAT: $NOW"
git push origin HEAD

echo "✓ Page $NEXT_PAGE claimed successfully"
echo ""
echo "Next steps:"
echo "1. Translate page $NEXT_PAGE"
echo "2. Save to translations/page_$NEXT_PAGE.json"
echo "3. Run: ./tools/complete_page.sh $NEXT_PAGE"
