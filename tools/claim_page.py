#!/usr/bin/env python3
"""
Page Claiming Tool - Smart page claiming with gap detection and quota enforcement

This tool:
1. Reads global state from sync daemon
2. Checks worker's current quota status
3. Finds next page using gap-first priority
4. Updates WORKER_STATE.md with claim
5. Commits and pushes immediately

Usage:
    python3 claim_page.py --get-next          # Show next page without claiming
    python3 claim_page.py --claim-next        # Claim next page
    python3 claim_page.py --claim 42          # Claim specific page
    python3 claim_page.py --release 42        # Release a claimed page
"""

import subprocess
import json
import time
import sys
import re
import argparse
from pathlib import Path
from typing import Optional, List, Dict

CACHE_DIR = Path(".sync_cache")
GLOBAL_STATE_FILE = CACHE_DIR / "global_state.json"


def load_global_state() -> Optional[Dict]:
    """Load global state from sync daemon cache"""
    if not GLOBAL_STATE_FILE.exists():
        print("❌ Global state not found. Is sync daemon running?")
        print("Start it with: python3 tools/sync_daemon.py --start --interval 60 &")
        return None
    
    try:
        with open(GLOBAL_STATE_FILE, 'r') as f:
            state = json.load(f)
        
        # Check if state is stale
        age = int(time.time()) - state["last_sync"]
        if age > 180:  # 3 minutes
            print(f"⚠️  Global state is {age}s old (stale)")
            print("Run: python3 tools/sync_daemon.py --sync-now")
        
        return state
    except Exception as e:
        print(f"❌ Error loading global state: {e}")
        return None


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
            # Extract last 4 chars after last dash
            worker_id = branch.split('-')[-1][:4] if '-' in branch else branch[:4]
            return worker_id
        return None
    except Exception:
        return None


def get_my_worker_data(state: Dict, worker_id: str) -> Optional[Dict]:
    """Get current worker's data from global state"""
    for worker in state["workers"]:
        if worker["id"] == worker_id:
            return worker
    return None


def calculate_quota(state: Dict, worker_id: str) -> Dict:
    """Calculate quota status for worker"""
    online_workers = [w for w in state["workers"] if w["status"] == "online"]
    total_pages = state["summary"]["total_pages"]
    
    if not online_workers:
        return {
            "can_work": False,
            "reason": "No online workers found",
            "fair_share": 0,
            "max_pages": 0,
            "completed": 0
        }
    
    fair_share = total_pages // len(online_workers)
    buffer = max(2, int(fair_share * 0.2))  # 20% buffer, minimum 2
    max_pages = fair_share + buffer
    
    my_data = get_my_worker_data(state, worker_id)
    if not my_data:
        # New worker
        completed = 0
    else:
        completed = len(my_data["completed"])
    
    can_work = completed < max_pages
    
    return {
        "can_work": can_work,
        "reason": f"Completed {completed}/{max_pages} pages" if can_work else f"Over quota: {completed}/{max_pages}",
        "fair_share": fair_share,
        "max_pages": max_pages,
        "completed": completed,
        "online_workers": len(online_workers)
    }


def get_next_page(state: Dict, prefer_gaps: bool = True) -> Optional[int]:
    """Get next page to claim using gap-first priority"""
    available = state["pages"]["available"]
    gaps = state["pages"]["gaps"]
    reclaimable = state["pages"]["reclaimable"]
    
    # Priority 1: Reclaimable pages (from offline workers)
    if reclaimable:
        return sorted(reclaimable)[0]
    
    # Priority 2: Gaps (if prefer_gaps is True)
    if prefer_gaps and gaps:
        return sorted(gaps)[0]
    
    # Priority 3: Lowest available page
    if available:
        return sorted(available)[0]
    
    return None


def update_worker_state_file(page: int, action: str = "claim"):
    """Update WORKER_STATE.md with claim or release"""
    worker_state_file = Path("WORKER_STATE.md")
    
    if not worker_state_file.exists():
        print("❌ WORKER_STATE.md not found. Create it first.")
        return False
    
    content = worker_state_file.read_text()
    
    # Update heartbeat
    current_time = int(time.time())
    content = re.sub(
        r'(Heartbeat[:\s]+)\d+',
        f'\\g<1>{current_time}',
        content
    )
    
    # Update claimed pages
    if action == "claim":
        # Find current claimed pages
        claimed_match = re.search(r'Claimed Pages?[:\s]+\[([^\]]*)\]', content, re.IGNORECASE)
        if claimed_match:
            claimed_str = claimed_match.group(1)
            claimed = [int(x.strip()) for x in claimed_str.split(',') if x.strip().isdigit()]
            if page not in claimed:
                claimed.append(page)
            claimed_str_new = ', '.join(str(p) for p in sorted(claimed))
            content = re.sub(
                r'(Claimed Pages?[:\s]+)\[[^\]]*\]',
                f'\\g<1>[{claimed_str_new}]',
                content,
                flags=re.IGNORECASE
            )
        else:
            # Add claimed pages field if not exists
            # Find the "Current Work" section and add after it
            content = re.sub(
                r'(## Current Work)',
                f'\\g<1>\n- **Claimed Pages**: [{page}]',
                content
            )
    
    elif action == "release":
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
    
    worker_state_file.write_text(content)
    return True


def git_commit_and_push(message: str) -> bool:
    """Commit and push changes"""
    try:
        # Add WORKER_STATE.md
        subprocess.run(["git", "add", "WORKER_STATE.md"], check=True)
        
        # Commit
        subprocess.run(["git", "commit", "-m", message], check=True)
        
        # Push
        result = subprocess.run(["git", "push", "origin", "HEAD"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️  Push failed: {result.stderr}")
            return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False


def claim_page(page: int, page_type: str = "seq") -> bool:
    """Claim a specific page"""
    worker_id = get_my_worker_id()
    if not worker_id:
        print("❌ Could not determine worker ID")
        return False
    
    # Update WORKER_STATE.md
    if not update_worker_state_file(page, action="claim"):
        return False
    
    # Commit and push
    current_time = int(time.time())
    message = f"[{worker_id}] CLAIM: Starting page {page} ({page_type})\nHEARTBEAT: {current_time}\nPAGE: {page}\nTYPE: {page_type}"
    
    if git_commit_and_push(message):
        print(f"✅ Claimed page {page} ({page_type})")
        return True
    else:
        print(f"❌ Failed to claim page {page}")
        return False


def release_page(page: int, reason: str = "manual release") -> bool:
    """Release a claimed page"""
    worker_id = get_my_worker_id()
    if not worker_id:
        print("❌ Could not determine worker ID")
        return False
    
    # Update WORKER_STATE.md
    if not update_worker_state_file(page, action="release"):
        return False
    
    # Commit and push
    current_time = int(time.time())
    message = f"[{worker_id}] RELEASE: Releasing page {page}\nHEARTBEAT: {current_time}\nPAGE: {page}\nREASON: {reason}"
    
    if git_commit_and_push(message):
        print(f"✅ Released page {page}")
        return True
    else:
        print(f"❌ Failed to release page {page}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Smart page claiming tool")
    parser.add_argument("--get-next", action="store_true", help="Show next page without claiming")
    parser.add_argument("--claim-next", action="store_true", help="Claim next page")
    parser.add_argument("--claim", type=int, help="Claim specific page number")
    parser.add_argument("--release", type=int, help="Release claimed page")
    parser.add_argument("--no-gaps", action="store_true", help="Don't prefer gaps (claim lowest sequential)")
    parser.add_argument("--force", action="store_true", help="Skip quota check")
    
    args = parser.parse_args()
    
    # Load global state
    state = load_global_state()
    if not state:
        sys.exit(1)
    
    worker_id = get_my_worker_id()
    if not worker_id:
        print("❌ Could not determine worker ID from branch name")
        sys.exit(1)
    
    print(f"Worker ID: {worker_id}")
    
    # Handle release
    if args.release:
        if release_page(args.release):
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Check quota (unless forced)
    if not args.force:
        quota = calculate_quota(state, worker_id)
        print(f"Quota: {quota['completed']}/{quota['max_pages']} pages (fair share: {quota['fair_share']}, {quota['online_workers']} workers)")
        
        if not quota["can_work"]:
            print(f"❌ {quota['reason']}")
            print("Wait for other workers to catch up, or use --force to override")
            sys.exit(1)
    
    # Get next page
    if args.get_next or args.claim_next:
        next_page = get_next_page(state, prefer_gaps=not args.no_gaps)
        
        if next_page is None:
            print("✅ No pages available (all claimed or completed)")
            sys.exit(0)
        
        # Determine page type
        if next_page in state["pages"]["reclaimable"]:
            page_type = "reclaim"
        elif next_page in state["pages"]["gaps"]:
            page_type = "gap"
        else:
            page_type = "seq"
        
        if args.get_next:
            print(f"Next page: {next_page} ({page_type})")
            sys.exit(0)
        else:
            # Claim it
            if claim_page(next_page, page_type):
                sys.exit(0)
            else:
                sys.exit(1)
    
    # Claim specific page
    if args.claim:
        # Check if page is available
        if args.claim in state["pages"]["completed"]:
            print(f"❌ Page {args.claim} is already completed")
            sys.exit(1)
        
        if args.claim in state["pages"]["claimed"] and args.claim not in state["pages"]["reclaimable"]:
            print(f"❌ Page {args.claim} is already claimed by another worker")
            sys.exit(1)
        
        # Determine page type
        if args.claim in state["pages"]["reclaimable"]:
            page_type = "reclaim"
        elif args.claim in state["pages"]["gaps"]:
            page_type = "gap"
        else:
            page_type = "seq"
        
        if claim_page(args.claim, page_type):
            sys.exit(0)
        else:
            sys.exit(1)
    
    # No action specified
    parser.print_help()


if __name__ == "__main__":
    main()
