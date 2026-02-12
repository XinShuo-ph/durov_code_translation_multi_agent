#!/usr/bin/env python3
"""
Worker State Updater - Update WORKER_STATE.md fields

Helper tool to update worker state file without manual editing.

Usage:
    python3 update_worker_state.py --complete 42       # Move page from claimed to completed
    python3 update_worker_state.py --set-status idle   # Update status field
    python3 update_worker_state.py --heartbeat         # Update heartbeat only
"""

import re
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import Optional

WORKER_STATE_FILE = Path("WORKER_STATE.md")


def update_heartbeat(content: str) -> str:
    """Update heartbeat timestamp"""
    current_time = int(time.time())
    content = re.sub(
        r'(Heartbeat[:\s]+)\d+',
        f'\\g<1>{current_time}',
        content
    )
    return content


def update_status(content: str, new_status: str) -> str:
    """Update status field"""
    content = re.sub(
        r'(\*\*Status\*\*[:\s]+)\w+',
        f'\\g<1>{new_status}',
        content
    )
    return content


def move_page_to_completed(content: str, page: int) -> str:
    """Move page from claimed to completed"""
    # Remove from claimed
    claimed_match = re.search(r'Claimed Pages?[:\s]+\[([^\]]*)\]', content, re.IGNORECASE)
    if claimed_match:
        claimed_str = claimed_match.group(1)
        claimed = [int(x.strip()) for x in claimed_str.split(',') if x.strip().isdigit()]
        if page in claimed:
            claimed.remove(page)
        claimed_str_new = ', '.join(str(p) for p in sorted(claimed))
        content = re.sub(
            r'(Claimed Pages?[:\s]+)\[[^\]]*\]',
            f'\\g<1>[{claimed_str_new}]',
            content,
            flags=re.IGNORECASE
        )
    
    # Add to completed table
    # Find the completed pages table and add new row
    current_time = int(time.time())
    # Simple hash for demonstration
    page_hash = hex(hash(f"page_{page}_{current_time}"))[2:10]
    
    # Look for the table header
    table_pattern = r'(## Completed Pages.*?\n\|[^\n]+\n\|[-\s|]+\n)'
    match = re.search(table_pattern, content, re.DOTALL)
    if match:
        # Insert after the table header
        new_row = f"| {page}   | seq  | {current_time}   | {page_hash} | - |\n"
        content = re.sub(
            table_pattern,
            f'\\g<1>{new_row}',
            content,
            flags=re.DOTALL
        )
    else:
        # Table doesn't exist, create it
        completed_section = f"""
## Completed Pages
| Page | Type | Completed At | Hash | Size |
|------|------|--------------|------|------|
| {page}   | seq  | {current_time}   | {page_hash} | - |
"""
        # Add after Current Work section
        content = re.sub(
            r'(## Current Work.*?\n(?:\-[^\n]+\n)*)',
            f'\\g<1>\n{completed_section}',
            content,
            flags=re.DOTALL
        )
    
    return content


def get_my_worker_id() -> Optional[str]:
    """Get current worker ID from branch name"""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            worker_id = branch.split('-')[-1][:4] if '-' in branch else branch[:4]
            return worker_id
        return None
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Update WORKER_STATE.md")
    parser.add_argument("--complete", type=int, help="Move page from claimed to completed")
    parser.add_argument("--set-status", choices=["online", "translating", "idle", "paused_over_quota"],
                       help="Update status field")
    parser.add_argument("--heartbeat", action="store_true", help="Update heartbeat only")
    parser.add_argument("--commit", action="store_true", help="Commit and push after update")
    
    args = parser.parse_args()
    
    if not WORKER_STATE_FILE.exists():
        print("❌ WORKER_STATE.md not found", file=sys.stderr)
        sys.exit(1)
    
    # Read current content
    content = WORKER_STATE_FILE.read_text()
    
    # Apply updates
    modified = False
    
    if args.complete:
        content = move_page_to_completed(content, args.complete)
        content = update_heartbeat(content)
        modified = True
        print(f"✅ Moved page {args.complete} to completed")
    
    if args.set_status:
        content = update_status(content, args.set_status)
        content = update_heartbeat(content)
        modified = True
        print(f"✅ Status updated to: {args.set_status}")
    
    if args.heartbeat:
        content = update_heartbeat(content)
        modified = True
        print("✅ Heartbeat updated")
    
    if not modified:
        parser.print_help()
        sys.exit(0)
    
    # Write back
    WORKER_STATE_FILE.write_text(content)
    
    # Commit if requested
    if args.commit:
        worker_id = get_my_worker_id()
        if not worker_id:
            print("⚠️  Could not determine worker ID, skipping commit", file=sys.stderr)
            sys.exit(0)
        
        try:
            subprocess.run(["git", "add", "WORKER_STATE.md"], check=True)
            
            # Build commit message
            current_time = int(time.time())
            if args.complete:
                message = f"[{worker_id}] DONE: Completed page {args.complete}\nHEARTBEAT: {current_time}"
            elif args.set_status:
                message = f"[{worker_id}] UPDATE: Status changed to {args.set_status}\nHEARTBEAT: {current_time}"
            else:
                message = f"[{worker_id}] HEARTBEAT: {current_time}"
            
            subprocess.run(["git", "commit", "-m", message], check=True)
            subprocess.run(["git", "push", "origin", "HEAD"], check=True)
            print("✅ Changes committed and pushed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git operation failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
