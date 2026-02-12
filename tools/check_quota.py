#!/usr/bin/env python3
"""
Quota Checker - Ensure fair work distribution

Checks if a worker has completed their fair share of work.
Prevents any single worker from doing too much while others sit idle.

Usage:
    python3 check_quota.py                    # Full quota report
    python3 check_quota.py --status-only      # Just print status (for scripts)
    python3 check_quota.py --can-work         # Exit 0 if can work, 1 if over quota
"""

import json
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Optional

CACHE_DIR = Path(".sync_cache")
GLOBAL_STATE_FILE = CACHE_DIR / "global_state.json"


def load_global_state() -> Optional[Dict]:
    """Load global state from sync daemon cache"""
    if not GLOBAL_STATE_FILE.exists():
        print("❌ Global state not found. Is sync daemon running?", file=sys.stderr)
        return None
    
    try:
        with open(GLOBAL_STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading global state: {e}", file=sys.stderr)
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
            worker_id = branch.split('-')[-1][:4] if '-' in branch else branch[:4]
            return worker_id
        return None
    except Exception:
        return None


def calculate_quota(state: Dict, worker_id: str) -> Dict:
    """Calculate detailed quota information"""
    online_workers = [w for w in state["workers"] if w["status"] == "online"]
    total_pages = state["summary"]["total_pages"]
    completed_pages = state["summary"]["completed_count"]
    
    if not online_workers:
        return {
            "status": "ERROR",
            "can_work": False,
            "message": "No online workers found",
            "my_completed": 0,
            "my_claimed": 0,
            "fair_share": 0,
            "max_pages": 0,
            "total_pages": total_pages,
            "online_workers": 0,
            "avg_completed": 0,
            "pages_until_limit": 0,
            "pages_vs_fair": 0
        }
    
    # Fair share calculation
    fair_share = total_pages // len(online_workers)
    buffer = max(2, int(fair_share * 0.2))  # 20% buffer
    max_pages = fair_share + buffer
    
    # Find my data
    my_data = None
    for worker in state["workers"]:
        if worker["id"] == worker_id:
            my_data = worker
            break
    
    if not my_data:
        # New worker, hasn't registered yet
        my_completed = 0
        my_claimed = 0
    else:
        my_completed = len(my_data["completed"])
        my_claimed = len(my_data["claimed"])
    
    # Calculate other workers' stats
    other_workers_completed = [len(w["completed"]) for w in online_workers if w["id"] != worker_id]
    avg_completed = sum(other_workers_completed) / len(other_workers_completed) if other_workers_completed else 0
    
    # Determine status
    if my_completed >= max_pages:
        status = "OVER_LIMIT"
        can_work = False
        message = f"Over quota: completed {my_completed} pages, limit is {max_pages}"
    elif my_completed > fair_share + 1:
        status = "NEAR_LIMIT"
        can_work = True
        message = f"Near limit: completed {my_completed} pages, fair share is {fair_share}"
    elif my_completed >= fair_share - 2:
        status = "AT_TARGET"
        can_work = True
        message = f"At target: completed {my_completed} pages, fair share is {fair_share}"
    else:
        status = "BELOW_TARGET"
        can_work = True
        message = f"Below target: completed {my_completed} pages, fair share is {fair_share}"
    
    return {
        "status": status,
        "can_work": can_work,
        "message": message,
        "my_completed": my_completed,
        "my_claimed": my_claimed,
        "fair_share": fair_share,
        "max_pages": max_pages,
        "total_pages": total_pages,
        "online_workers": len(online_workers),
        "avg_completed": avg_completed,
        "pages_until_limit": max(0, max_pages - my_completed),
        "pages_vs_fair": my_completed - fair_share
    }


def print_quota_report(quota: Dict):
    """Print detailed quota report"""
    print("=" * 60)
    print("WORK QUOTA STATUS")
    print("=" * 60)
    print()
    print(f"Total pages in project:  {quota['total_pages']}")
    print(f"Online workers:          {quota['online_workers']}")
    print(f"Fair share per worker:   {quota['fair_share']} pages")
    print(f"Maximum before pause:    {quota['max_pages']} pages (fair share + 20% buffer)")
    print()
    print(f"Your completed pages:    {quota['my_completed']}")
    print(f"Your claimed pages:      {quota['my_claimed']}")
    print(f"Average (other workers): {quota['avg_completed']:.1f} pages")
    print()
    
    # Status with visual indicator
    status_symbols = {
        "BELOW_TARGET": "⬇️ ",
        "AT_TARGET": "✅",
        "NEAR_LIMIT": "⚠️ ",
        "OVER_LIMIT": "🛑"
    }
    symbol = status_symbols.get(quota['status'], "")
    print(f"Status: {symbol} {quota['status']}")
    print(f"Message: {quota['message']}")
    print()
    
    if quota['can_work']:
        print(f"✅ You CAN claim more pages")
        print(f"   Pages until limit: {quota['pages_until_limit']}")
        if quota['status'] == "NEAR_LIMIT":
            print(f"   ⚠️  Approaching limit - prefer gaps over sequential pages")
    else:
        print(f"🛑 You should WAIT for other workers to catch up")
        print(f"   You are {-quota['pages_vs_fair']} pages over fair share")
        print(f"   Recommendation: Wait 5-10 minutes and check again")
    print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Check work quota status")
    parser.add_argument("--status-only", action="store_true", help="Print only status string")
    parser.add_argument("--can-work", action="store_true", help="Exit 0 if can work, 1 if not")
    
    args = parser.parse_args()
    
    # Load state
    state = load_global_state()
    if not state:
        sys.exit(1)
    
    # Get worker ID
    worker_id = get_my_worker_id()
    if not worker_id:
        print("❌ Could not determine worker ID", file=sys.stderr)
        sys.exit(1)
    
    # Calculate quota
    quota = calculate_quota(state, worker_id)
    
    if args.status_only:
        print(quota['status'])
        sys.exit(0)
    
    if args.can_work:
        sys.exit(0 if quota['can_work'] else 1)
    
    # Full report
    print_quota_report(quota)


if __name__ == "__main__":
    main()
