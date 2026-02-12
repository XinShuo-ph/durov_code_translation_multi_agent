# Agent: [ID]

- **Branch**: [full branch name]
- **Heartbeat**: [unix timestamp]
- **Current Unit**: none
- **Status**: starting

## Completed
(none yet)

## Log
- [timestamp] Starting session

---

## Setup Instructions

```bash
# 1. Get your identity
MY_BRANCH=$(git branch --show-current)
MY_ID=$(echo "$MY_BRANCH" | grep -oE '[^-]+$')

# 2. Compute starting unit
OFFSET=$(printf '%d' "0x${MY_ID}" 2>/dev/null || echo "0")
TOTAL_UNITS=99  # <-- adjust for your project
START_UNIT=$(( (OFFSET % TOTAL_UNITS) + 1 ))
echo "Starting at unit $START_UNIT"

# 3. Copy this template
cp AGENT_STATE_TEMPLATE.md AGENT_STATE.md

# 4. Fill in your details (replace placeholders above)

# 5. Commit and push to register
git add AGENT_STATE.md
git commit -m "[$MY_ID] Register as active agent, starting at unit $START_UNIT"
git push -u origin HEAD

# 6. DELETE this "Setup Instructions" section from your AGENT_STATE.md

# 7. Start producing output immediately!
```
