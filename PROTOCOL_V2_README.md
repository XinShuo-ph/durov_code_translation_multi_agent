# Multi-Agent Translation - Quick Start

## First Time Setup

```bash
# Initialize project structure
python3 tools/init_project.py

# Create your worker branch
git checkout -b cursor/translation-work-XXXX

# Commit initial state
git add STATE.json worker-states/ translations/ .gitignore
git commit -m "Initialize multi-agent project structure"
git push -u origin HEAD
```

## Daily Workflow

```bash
# 1. Start sync service (mandatory!)
python3 tools/sync_service.py --start --worker-id XXXX

# 2. Run automated work loop
python3 tools/worker_loop.py --worker-id XXXX

# Or manual control:
while true; do
    PAGE=$(python3 tools/sync_service.py --next-page)
    [ "$PAGE" = "NONE" ] && break
    
    python3 tools/sync_service.py --claim-page $PAGE
    python3 translate.py --page $PAGE
    python3 tools/sync_service.py --complete-page $PAGE \
        --file translations/page_$(printf '%03d' $PAGE).json
done

# 3. Stop sync service when done
python3 tools/sync_service.py --stop
```

## Monitoring Progress

```bash
# Check global status
python3 tools/sync_service.py --status

# Check your status
python3 tools/sync_service.py --my-status

# Start web dashboard
python3 tools/dashboard.py --port 8080
```

## Troubleshooting

**Sync service won't start:**
```bash
# Check if already running
ps aux | grep sync_service

# Kill old instance
pkill -f sync_service.py

# Try again
python3 tools/sync_service.py --start --worker-id XXXX
```

**Claim conflicts:**
```bash
# Sync service handles automatically
# If you lose a claim, just request next page
python3 tools/sync_service.py --next-page
```

**See full protocol:** Read `PROTOCOL_V2.md`
