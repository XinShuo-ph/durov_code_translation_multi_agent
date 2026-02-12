#!/usr/bin/env python3
"""
Atomic page claiming tool.

Usage:
    python3 tools/claim_page.py PAGE_NUMBER
"""

import sys
import subprocess
import time
import re
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))
from sync_daemon import SyncDaemon


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


def update_worker_state(claimed_page: int, claim_time: int) -> None:
    """Update WORKER_STATE.md with new claim."""
    worker_state_path = Path("WORKER_STATE.md")
    
    if not worker_state_path.exists():
        print("ERROR: WORKER_STATE.md not found. Run registration first.")
        sys.exit(1)
    
    content = worker_state_path.read_text()
    
    # Update claimed page
    content = re.sub(
        r'\*\*Claimed Page\*\*:.*',
        f'**Claimed Page**: {claimed_page}',
        content
    )
    
    # Update claim time
    content = re.sub(
        r'\*\*Claim Time\*\*:.*',
        f'**Claim Time**: {claim_time}',
        content
    )
    
    # Update heartbeat
    content = re.sub(
        r'\*\*Heartbeat\*\*:.*',
        f'**Heartbeat**: {claim_time}',
        content
    )
    
    # Update status to working
    content = re.sub(
        r'\*\*Status\*\*:.*',
        f'**Status**: working',
        content
    )
    
    worker_state_path.write_text(content)


def unclaim_page() -> None:
    """Remove claim from WORKER_STATE.md."""
    worker_state_path = Path("WORKER_STATE.md")
    
    if not worker_state_path.exists():
        return
    
    content = worker_state_path.read_text()
    
    # Clear claimed page
    content = re.sub(
        r'\*\*Claimed Page\*\*:.*',
        f'**Claimed Page**: none',
        content
    )
    
    # Clear claim time
    content = re.sub(
        r'\*\*Claim Time\*\*:.*',
        f'**Claim Time**: -',
        content
    )
    
    # Update status to idle
    content = re.sub(
        r'\*\*Status\*\*:.*',
        f'**Status**: idle',
        content
    )
    
    worker_state_path.write_text(content)


def claim_page(page_num: int) -> bool:
    """
    Atomically claim a page.
    
    Returns True if successful, False if lost race condition.
    """
    my_id = get_my_id()
    daemon = SyncDaemon()
    
    # Step 1: Pre-flight check
    print(f"[{my_id}] Checking page {page_num}...")
    status = daemon.check_page(page_num)
    
    if status == "COMPLETED":
        print(f"[{my_id}] Page {page_num} is already completed")
        return False
    elif status.startswith("CLAIMED_BY:"):
        claimer = status.split(":")[1]
        print(f"[{my_id}] Page {page_num} is already claimed by {claimer}")
        return False
    elif status != "AVAILABLE" and status != "STALE":
        print(f"[{my_id}] Page {page_num} status: {status}")
        return False
    
    print(f"[{my_id}] Page {page_num} is available")
    
    # Step 2: Update local state
    claim_time = int(time.time())
    update_worker_state(page_num, claim_time)
    print(f"[{my_id}] Updated WORKER_STATE.md")
    
    # Step 3: Broadcast claim
    subprocess.run(["git", "add", "WORKER_STATE.md"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"[{my_id}] CLAIM: Page {page_num}"],
        check=True
    )
    
    print(f"[{my_id}] Pushing claim...")
    result = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[{my_id}] ERROR: Push failed: {result.stderr}")
        return False
    
    print(f"[{my_id}] Claim broadcasted")
    
    # Step 4: Verification (wait for sync)
    print(f"[{my_id}] Waiting 10 seconds for sync verification...")
    time.sleep(10)
    
    # Force sync
    daemon.sync()
    
    current_claimer = daemon.who_claimed(page_num)
    if current_claimer != my_id:
        print(f"[{my_id}] Lost race condition - {current_claimer} claimed page {page_num} first")
        print(f"[{my_id}] Unclaiming...")
        
        # Revert our state
        unclaim_page()
        subprocess.run(["git", "add", "WORKER_STATE.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"[{my_id}] UNCLAIM: Page {page_num} (lost race)"],
            check=True
        )
        subprocess.run(["git", "push", "origin", "HEAD"], check=False)
        
        return False
    
    # Success!
    print(f"[{my_id}] Successfully claimed page {page_num}")
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 tools/claim_page.py PAGE_NUMBER")
        sys.exit(1)
    
    try:
        page_num = int(sys.argv[1])
    except ValueError:
        print("ERROR: PAGE_NUMBER must be an integer")
        sys.exit(1)
    
    if page_num < 1:
        print("ERROR: PAGE_NUMBER must be >= 1")
        sys.exit(1)
    
    success = claim_page(page_num)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
