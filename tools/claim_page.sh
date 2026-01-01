#!/bin/bash
# Helper script to claim next available page for M2 translation
# Usage: ./claim_page.sh

# Get worker info
MY_BRANCH=$(git branch --show-current)
MY_SHORT_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$' | tail -c 5)

echo "Worker: $MY_SHORT_ID"
echo "Syncing with other workers..."

# Fetch all branches
git fetch --all --prune 2>/dev/null

# Collect claimed and completed pages from all workers
CLAIMED_PAGES=()
COMPLETED_PAGES=()

for branch in $(git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '); do
    if git show "origin/${branch}:WORKER_STATE.md" &>/dev/null; then
        # Extract claimed pages (status = translating or claimed)
        claimed=$(git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | \
                 grep -E "^\| [0-9]+ \| (translating|claimed)" | \
                 awk -F'|' '{print $2}' | tr -d ' ')
        CLAIMED_PAGES+=($claimed)
        
        # Extract completed pages
        completed=$(git show "origin/${branch}:WORKER_STATE.md" 2>/dev/null | \
                   grep -E "^\| [0-9]+ \| done" | \
                   awk -F'|' '{print $2}' | tr -d ' ')
        COMPLETED_PAGES+=($completed)
    fi
done

# Find lowest available page (1-99)
NEXT_PAGE=""
for page in {1..99}; do
    if [[ ! " ${CLAIMED_PAGES[@]} " =~ " ${page} " ]] && \
       [[ ! " ${COMPLETED_PAGES[@]} " =~ " ${page} " ]]; then
        NEXT_PAGE=$page
        break
    fi
done

if [ -z "$NEXT_PAGE" ]; then
    echo "No pages available! All claimed or completed."
    exit 0
fi

echo "Next available page: $NEXT_PAGE"
echo "Claim this page? (y/n)"
read -r response

if [[ "$response" != "y" ]]; then
    echo "Cancelled."
    exit 0
fi

# Update WORKER_STATE.md with claim
# This is a simplified version - actual implementation would parse and update the table
echo "To claim page $NEXT_PAGE, update WORKER_STATE.md M2 section manually, then:"
echo ""
echo "git add WORKER_STATE.md"
echo "git commit -m \"[$MY_SHORT_ID] M2 CLAIM: Starting page $NEXT_PAGE"
echo "PAGES: $NEXT_PAGE"
echo "HEARTBEAT: \$(date +%s)\""
echo "git push origin HEAD"
