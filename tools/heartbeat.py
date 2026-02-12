#!/usr/bin/env python3
"""
Update worker heartbeat.

Usage:
    python3 tools/heartbeat.py
"""

import subprocess
import time
import re
from pathlib import Path


def get_my_id() -> str:
    """Get my worker ID from branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True
    )
    branch = result.stdout.strip()
    parts = branch.split('-')
    return parts[-1] if parts else "unknown"


def update_heartbeat() -> None:
    """Update heartbeat timestamp in WORKER_STATE.md."""
    worker_state_path = Path("WORKER_STATE.md")
    
    if not worker_state_path.exists():
        print("ERROR: WORKER_STATE.md not found")
        return
    
    content = worker_state_path.read_text()
    timestamp = int(time.time())
    
    # Update heartbeat
    content = re.sub(
        r'\*\*Heartbeat\*\*:.*',
        f'**Heartbeat**: {timestamp}',
        content
    )
    
    worker_state_path.write_text(content)
    
    # Commit and push
    my_id = get_my_id()
    
    subprocess.run(["git", "add", "WORKER_STATE.md"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"[{my_id}] HEARTBEAT"],
        check=True
    )
    
    result = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"[{my_id}] Heartbeat updated (timestamp: {timestamp})")
    else:
        print(f"[{my_id}] ERROR: Push failed: {result.stderr}")


if __name__ == "__main__":
    update_heartbeat()
