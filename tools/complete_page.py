#!/usr/bin/env python3
"""
Mark a page as complete.

Usage:
    python3 tools/complete_page.py PAGE_NUMBER
"""

import sys
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


def complete_page(page_num: int) -> None:
    """
    Mark page as complete.
    
    1. Verify translation file exists
    2. Add to completed pages table
    3. Clear current claim
    4. Commit and push
    """
    my_id = get_my_id()
    
    # Verify translation exists
    translation_file = Path(f"translations/page_{page_num:03d}.json")
    if not translation_file.exists():
        # Try raw/ directory
        translation_file = Path(f"translations/raw/page_{page_num:03d}.json")
        if not translation_file.exists():
            print(f"[{my_id}] ERROR: Translation file not found for page {page_num}")
            sys.exit(1)
    
    # Calculate file hash (simple hash of first 100 chars)
    content = translation_file.read_text()
    file_hash = hex(hash(content[:100]))[-8:]
    
    # Update WORKER_STATE.md
    worker_state_path = Path("WORKER_STATE.md")
    if not worker_state_path.exists():
        print(f"[{my_id}] ERROR: WORKER_STATE.md not found")
        sys.exit(1)
    
    state_content = worker_state_path.read_text()
    
    # Add to completed pages table
    timestamp = int(time.time())
    duration_min = 0  # TODO: Calculate from claim_time
    
    # Find the completed pages table and add new row
    table_marker = "## Completed Pages"
    if table_marker in state_content:
        # Find where to insert (after header row)
        lines = state_content.split('\n')
        insert_idx = None
        for i, line in enumerate(lines):
            if table_marker in line:
                # Skip past header and separator
                insert_idx = i + 3
                break
        
        if insert_idx:
            new_row = f"| {page_num}    | {timestamp}   | {file_hash} | {duration_min} min    |"
            lines.insert(insert_idx, new_row)
            state_content = '\n'.join(lines)
    
    # Clear current claim
    state_content = re.sub(
        r'\*\*Claimed Page\*\*:.*',
        '**Claimed Page**: none',
        state_content
    )
    
    state_content = re.sub(
        r'\*\*Claim Time\*\*:.*',
        '**Claim Time**: -',
        state_content
    )
    
    # Update heartbeat
    state_content = re.sub(
        r'\*\*Heartbeat\*\*:.*',
        f'**Heartbeat**: {timestamp}',
        state_content
    )
    
    # Update status to idle
    state_content = re.sub(
        r'\*\*Status\*\*:.*',
        '**Status**: idle',
        state_content
    )
    
    # Update statistics (total completed)
    # This is a bit hacky - just increment if we can find it
    match = re.search(r'\*\*Total Completed\*\*:\s*(\d+)', state_content)
    if match:
        current_total = int(match.group(1))
        new_total = current_total + 1
        state_content = re.sub(
            r'\*\*Total Completed\*\*:\s*\d+',
            f'**Total Completed**: {new_total}',
            state_content
        )
    
    worker_state_path.write_text(state_content)
    
    # Commit and push
    subprocess.run(["git", "add", str(translation_file), "WORKER_STATE.md"], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"[{my_id}] COMPLETE: Page {page_num} (hash: {file_hash})"],
        check=True
    )
    
    print(f"[{my_id}] Pushing completion...")
    result = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"[{my_id}] Page {page_num} marked as complete")
    else:
        print(f"[{my_id}] ERROR: Push failed: {result.stderr}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 tools/complete_page.py PAGE_NUMBER")
        sys.exit(1)
    
    try:
        page_num = int(sys.argv[1])
    except ValueError:
        print("ERROR: PAGE_NUMBER must be an integer")
        sys.exit(1)
    
    complete_page(page_num)


if __name__ == "__main__":
    main()
