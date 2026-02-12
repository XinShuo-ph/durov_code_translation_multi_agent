# Worker: [SHORT_ID]
- Branch: [FULL_BRANCH_NAME]
- Status: starting
- Stripe: []
- Completed: []
- Current: none
- Last push: [UNIX_TIMESTAMP]

## Setup

```bash
# 1. Get your identity
MY_BRANCH=$(git branch --show-current)
MY_ID=$(echo "$MY_BRANCH" | grep -oE '[0-9a-f]{4}$')
echo "I am: $MY_ID"

# 2. Compute your stripe assignment
python3 tools/compute_stripe.py

# 3. Fill in this template, then:
git add WORKER_STATE.md
git commit -m "[$MY_ID] START: registered"
git push -u origin HEAD
```

After setup, delete this "Setup" section and start translating your first stripe page.
