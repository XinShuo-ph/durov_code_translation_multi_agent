#!/usr/bin/env python3
"""
Sync Daemon - Continuous synchronization of multi-agent state

This daemon runs in the background and:
1. Fetches all worker branches every N seconds
2. Parses WORKER_STATE.md from each branch
3. Builds global state (who's online, what's claimed/completed)
4. Writes to .sync_cache/global_state.json for other tools to use
5. Detects offline workers and makes their pages available for reclaim

Usage:
    python3 sync_daemon.py --start --interval 60 &
    python3 sync_daemon.py --status
    python3 sync_daemon.py --sync-now
    python3 sync_daemon.py --stop
"""

import subprocess
import json
import time
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional

CACHE_DIR = Path(".sync_cache")
GLOBAL_STATE_FILE = CACHE_DIR / "global_state.json"
PID_FILE = CACHE_DIR / "daemon.pid"
LOG_FILE = CACHE_DIR / "sync.log"

HEARTBEAT_ONLINE_THRESHOLD = 600  # 10 minutes
RECLAIM_THRESHOLD = 900  # 15 minutes


def log(message: str):
    """Write log message to file and optionally stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    
    CACHE_DIR.mkdir(exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")
    
    if "--verbose" in sys.argv:
        print(log_msg)


def run_git_command(args: List[str], timeout: int = 30) -> Optional[str]:
    """Run git command and return output, or None on error"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            log(f"Git command failed: git {' '.join(args)}")
            log(f"Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        log(f"Git command timeout: git {' '.join(args)}")
        return None
    except Exception as e:
        log(f"Git command error: {e}")
        return None


def get_worker_branches() -> List[str]:
    """Get all cursor/* branches that might be worker branches"""
    output = run_git_command(["branch", "-r"])
    if not output:
        return []
    
    branches = []
    for line in output.split('\n'):
        line = line.strip()
        if line.startswith("origin/cursor/"):
            branch = line.replace("origin/", "")
            branches.append(branch)
    
    return branches


def parse_worker_state(branch: str) -> Optional[Dict]:
    """Parse WORKER_STATE.md from a branch"""
    # Try to get WORKER_STATE.md from the branch
    content = run_git_command(["show", f"origin/{branch}:WORKER_STATE.md"])
    if not content:
        return None
    
    # Extract worker ID from branch name
    worker_id = branch.split('-')[-1][:4] if '-' in branch else branch[:4]
    
    # Parse the markdown file
    worker_data = {
        "id": worker_id,
        "branch": branch,
        "status": "unknown",
        "heartbeat": 0,
        "claimed": [],
        "completed": [],
        "last_sync": 0
    }
    
    # Extract heartbeat
    heartbeat_match = re.search(r'Heartbeat[:\s]+(\d+)', content)
    if heartbeat_match:
        worker_data["heartbeat"] = int(heartbeat_match.group(1))
    
    # Extract status
    status_match = re.search(r'Status[:\s]+(\w+)', content)
    if status_match:
        worker_data["status"] = status_match.group(1)
    
    # Extract claimed pages (look for arrays or lists)
    claimed_match = re.search(r'Claimed Pages?[:\s]+\[([^\]]*)\]', content, re.IGNORECASE)
    if claimed_match:
        claimed_str = claimed_match.group(1)
        worker_data["claimed"] = [int(x.strip()) for x in claimed_str.split(',') if x.strip().isdigit()]
    
    # Extract completed pages from table
    # Look for lines like: | 13   | gap  | 1735689600   | a8f3b2c1 | 842 |
    completed_pages = set()
    for line in content.split('\n'):
        if '|' in line and not line.strip().startswith('|--'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 2 and parts[1].isdigit():
                completed_pages.add(int(parts[1]))
    
    worker_data["completed"] = sorted(list(completed_pages))
    
    # Determine if worker is online
    current_time = int(time.time())
    age = current_time - worker_data["heartbeat"]
    
    if age > HEARTBEAT_ONLINE_THRESHOLD:
        worker_data["status"] = "offline"
    elif worker_data["status"] == "unknown":
        worker_data["status"] = "online"
    
    return worker_data


def sync_all_workers(total_pages: int = 99) -> Dict:
    """Sync all worker branches and build global state"""
    log("Starting sync...")
    
    # Fetch all remote branches
    log("Fetching remote branches...")
    run_git_command(["fetch", "origin", "--prune"])
    
    # Get all worker branches
    branches = get_worker_branches()
    log(f"Found {len(branches)} cursor branches")
    
    # Parse each worker's state
    workers = []
    all_claimed = set()
    all_completed = set()
    
    for branch in branches:
        worker_data = parse_worker_state(branch)
        if worker_data:
            workers.append(worker_data)
            all_claimed.update(worker_data["claimed"])
            all_completed.update(worker_data["completed"])
    
    log(f"Parsed {len(workers)} worker states")
    
    # Calculate global state
    all_pages = set(range(1, total_pages + 1))
    available = sorted(all_pages - all_claimed - all_completed)
    
    # Find gaps (pages where lower and higher numbers are completed)
    gaps = []
    for page in available:
        has_lower = any(p < page for p in all_completed)
        has_higher = any(p > page for p in all_completed)
        if has_lower and has_higher:
            gaps.append(page)
    
    # Find pages available for reclaim (claimed by offline workers >15min)
    current_time = int(time.time())
    reclaimable = []
    for worker in workers:
        age = current_time - worker["heartbeat"]
        if age > RECLAIM_THRESHOLD and worker["claimed"]:
            reclaimable.extend(worker["claimed"])
    
    global_state = {
        "workers": workers,
        "pages": {
            "claimed": sorted(list(all_claimed)),
            "completed": sorted(list(all_completed)),
            "available": available,
            "gaps": sorted(gaps),
            "reclaimable": sorted(reclaimable)
        },
        "summary": {
            "total_pages": total_pages,
            "completed_count": len(all_completed),
            "claimed_count": len(all_claimed),
            "available_count": len(available),
            "gap_count": len(gaps),
            "online_workers": sum(1 for w in workers if w["status"] == "online"),
            "total_workers": len(workers)
        },
        "last_sync": current_time
    }
    
    log(f"Sync complete: {global_state['summary']['completed_count']} completed, "
        f"{global_state['summary']['claimed_count']} claimed, "
        f"{global_state['summary']['gap_count']} gaps, "
        f"{global_state['summary']['online_workers']}/{global_state['summary']['total_workers']} workers online")
    
    return global_state


def save_global_state(state: Dict):
    """Save global state to cache file"""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(GLOBAL_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    log(f"Global state saved to {GLOBAL_STATE_FILE}")


def load_global_state() -> Optional[Dict]:
    """Load global state from cache file"""
    if not GLOBAL_STATE_FILE.exists():
        return None
    
    try:
        with open(GLOBAL_STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error loading global state: {e}")
        return None


def daemon_loop(interval: int = 60, total_pages: int = 99):
    """Main daemon loop - sync every N seconds"""
    log(f"Daemon starting with {interval}s interval")
    
    # Save PID
    CACHE_DIR.mkdir(exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        while True:
            try:
                state = sync_all_workers(total_pages)
                save_global_state(state)
            except Exception as e:
                log(f"Sync error: {e}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        log("Daemon stopped by user")
    finally:
        # Clean up PID file
        if PID_FILE.exists():
            PID_FILE.unlink()


def check_daemon_status() -> bool:
    """Check if daemon is running"""
    if not PID_FILE.exists():
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process exists
        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks
        return True
    except (ProcessLookupError, ValueError):
        # PID file exists but process doesn't
        PID_FILE.unlink()
        return False


def stop_daemon():
    """Stop the running daemon"""
    if not PID_FILE.exists():
        print("Daemon is not running")
        return
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        os.kill(pid, 15)  # SIGTERM
        print(f"Sent stop signal to daemon (PID {pid})")
        
        # Wait for cleanup
        time.sleep(2)
        if PID_FILE.exists():
            PID_FILE.unlink()
    except Exception as e:
        print(f"Error stopping daemon: {e}")


def main():
    parser = argparse.ArgumentParser(description="Multi-agent sync daemon")
    parser.add_argument("--start", action="store_true", help="Start daemon")
    parser.add_argument("--stop", action="store_true", help="Stop daemon")
    parser.add_argument("--status", action="store_true", help="Check daemon status")
    parser.add_argument("--sync-now", action="store_true", help="Run single sync immediately")
    parser.add_argument("--interval", type=int, default=60, help="Sync interval in seconds (default: 60)")
    parser.add_argument("--total-pages", type=int, default=99, help="Total pages in project (default: 99)")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging to stdout")
    
    args = parser.parse_args()
    
    if args.status:
        is_running = check_daemon_status()
        if is_running:
            print("✅ Daemon is running")
            state = load_global_state()
            if state:
                age = int(time.time()) - state["last_sync"]
                print(f"Last sync: {age}s ago")
                print(f"Status: {state['summary']}")
        else:
            print("❌ Daemon is not running")
        sys.exit(0)
    
    if args.stop:
        stop_daemon()
        sys.exit(0)
    
    if args.sync_now:
        print("Running sync now...")
        state = sync_all_workers(args.total_pages)
        save_global_state(state)
        print(f"✅ Sync complete: {state['summary']}")
        sys.exit(0)
    
    if args.start:
        if check_daemon_status():
            print("❌ Daemon is already running")
            sys.exit(1)
        
        print(f"Starting daemon with {args.interval}s interval...")
        print(f"Logs: {LOG_FILE}")
        
        # Fork to background if not already
        if os.fork() != 0:
            # Parent process
            time.sleep(2)  # Let child start
            if check_daemon_status():
                print("✅ Daemon started")
            else:
                print("❌ Daemon failed to start, check logs")
            sys.exit(0)
        else:
            # Child process - become daemon
            os.setsid()
            daemon_loop(args.interval, args.total_pages)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
