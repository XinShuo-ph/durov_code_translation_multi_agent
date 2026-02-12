#!/usr/bin/env python3
"""
Initialize multi-agent project structure.

Creates:
- STATE.json (global project state)
- worker-states/ (directory for individual worker states)
- translations/ (directory for completed translations)
"""

import json
import os
import sys
from pathlib import Path
import time

# Project configuration
CONFIG = {
    "project": "durov-code-translation",
    "total_pages": 99,
    "source_pdf": "durov_code_book.pdf",
    "languages": ["ru", "en", "zh", "ja"]
}

def init_state_file():
    """Create initial STATE.json"""
    state = {
        "project": CONFIG["project"],
        "total_pages": CONFIG["total_pages"],
        "languages": CONFIG["languages"],
        "initialized_at": int(time.time()),
        "last_updated": int(time.time()),
        "completed_pages": [],
        "claimed_pages": {},
        "available_pages": list(range(1, CONFIG["total_pages"] + 1)),
        "workers": {},
        "stats": {
            "total_completions": 0,
            "total_claims": 0,
            "conflicts_detected": 0,
            "pages_reclaimed": 0
        }
    }
    
    # Check if STATE.json already exists
    if os.path.exists("STATE.json"):
        print("⚠️  STATE.json already exists")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("Skipping STATE.json creation")
            return False
    
    with open("STATE.json", 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✓ Created STATE.json")
    return True

def init_directories():
    """Create required directories"""
    directories = [
        "worker-states",
        "translations"
    ]
    
    for dir_name in directories:
        path = Path(dir_name)
        if path.exists():
            print(f"✓ {dir_name}/ already exists")
        else:
            path.mkdir(parents=True, exist_ok=True)
            # Create .gitkeep to ensure directory is tracked
            (path / ".gitkeep").touch()
            print(f"✓ Created {dir_name}/")

def create_gitignore_entries():
    """Add necessary .gitignore entries"""
    gitignore_path = Path(".gitignore")
    
    entries_to_add = [
        "# Sync service runtime",
        "sync_service.pid",
        "sync_service.log",
        ".sync_cache/",
        "",
        "# Worker state backups",
        "worker-states/*.bak",
        ""
    ]
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "sync_service.pid" in content:
            print("✓ .gitignore already configured")
            return
    
    with open(".gitignore", 'a') as f:
        f.write('\n'.join(entries_to_add))
    
    print("✓ Updated .gitignore")

def validate_environment():
    """Check that required files exist"""
    required_files = [
        "durov_code_book.pdf",
        "extracted/full.txt"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Warning: Missing files:")
        for f in missing:
            print(f"  - {f}")
        print("\nProject initialization will continue, but translation may fail without source files.")
    else:
        print("✓ Source files validated")

def create_readme():
    """Create PROTOCOL_V2_README.md with quick start"""
    readme_content = """# Multi-Agent Translation - Quick Start

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
    python3 tools/sync_service.py --complete-page $PAGE \\
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
"""
    
    with open("PROTOCOL_V2_README.md", 'w') as f:
        f.write(readme_content)
    
    print("✓ Created PROTOCOL_V2_README.md")

def main():
    print("=" * 60)
    print("Multi-Agent Translation Project Initialization")
    print("=" * 60)
    print()
    
    # Validate environment
    validate_environment()
    print()
    
    # Initialize directories
    print("Creating directories...")
    init_directories()
    print()
    
    # Initialize state file
    print("Creating global state...")
    init_state_file()
    print()
    
    # Update gitignore
    print("Configuring git...")
    create_gitignore_entries()
    print()
    
    # Create README
    print("Creating documentation...")
    create_readme()
    print()
    
    print("=" * 60)
    print("✓ Initialization complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review STATE.json and worker-states/ directory")
    print("2. Commit changes: git add STATE.json worker-states/ translations/")
    print("3. Push to your branch: git push -u origin HEAD")
    print("4. Start sync service: python3 tools/sync_service.py --start --worker-id XXXX")
    print()
    print("See PROTOCOL_V2_README.md for full workflow.")

if __name__ == "__main__":
    main()
