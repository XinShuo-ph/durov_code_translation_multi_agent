#!/usr/bin/env python3
"""
Multi-Agent Sync Daemon

This daemon prevents the 83% duplication problem by:
1. Continuously syncing all worker states (every 60s)
2. Maintaining global view of claimed/completed pages
3. Validating page availability before claims
4. Detecting and reclaiming from stalled workers
5. Providing real-time team statistics

Usage:
    python3 sync_daemon.py --start          # Start daemon in background
    python3 sync_daemon.py --stop           # Stop daemon
    python3 sync_daemon.py --next-page      # Get next available page
    python3 sync_daemon.py --check-page N   # Check if page N is available
    python3 sync_daemon.py --status         # Show team status
    python3 sync_daemon.py --sync-now       # Force immediate sync
"""

import subprocess
import json
import time
import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import signal
import fcntl

# Configuration
SYNC_INTERVAL = 60  # seconds
HEARTBEAT_TIMEOUT = 600  # 10 minutes = offline
STALLED_TIMEOUT = 900  # 15 minutes = reclaimable
GLOBAL_STATE_FILE = ".sync/global_state.json"
DAEMON_PID_FILE = ".sync/daemon.pid"
DAEMON_LOG_FILE = ".sync/daemon.log"


class WorkerState:
    """Represents the state of a single worker"""
    
    def __init__(self, branch: str, short_id: str):
        self.branch = branch
        self.short_id = short_id
        self.heartbeat = 0
        self.status = "unknown"
        self.claimed_page = None
        self.completed_pages: List[int] = []
        self.started_at = None
        
    def is_online(self) -> bool:
        """Check if worker is online (heartbeat < 10min old)"""
        if self.heartbeat == 0:
            return False
        age = time.time() - self.heartbeat
        return age < HEARTBEAT_TIMEOUT
    
    def is_stalled(self) -> bool:
        """Check if worker is stalled (claimed page but no progress for 15min)"""
        if not self.claimed_page or not self.started_at:
            return False
        if not self.is_online():
            return True
        age = time.time() - self.heartbeat
        return age > STALLED_TIMEOUT
    
    def to_dict(self) -> dict:
        return {
            "branch": self.branch,
            "short_id": self.short_id,
            "heartbeat": self.heartbeat,
            "status": self.status,
            "claimed_page": self.claimed_page,
            "completed_pages": self.completed_pages,
            "started_at": self.started_at,
            "is_online": self.is_online(),
            "is_stalled": self.is_stalled()
        }


class GlobalState:
    """Global state of all workers and pages"""
    
    def __init__(self):
        self.workers: Dict[str, WorkerState] = {}
        self.completed_pages: Set[int] = set()
        self.claimed_pages: Dict[int, str] = {}  # page -> worker_id
        self.last_sync = 0
        self.total_pages = 99  # Default for Durov book
        
    def update_from_worker_state(self, branch: str, short_id: str, content: str):
        """Parse WORKER_STATE.md content and update global state"""
        worker = WorkerState(branch, short_id)
        
        # Parse heartbeat
        heartbeat_match = re.search(r'Heartbeat:\s*(\d+)', content)
        if heartbeat_match:
            worker.heartbeat = int(heartbeat_match.group(1))
        
        # Parse status
        status_match = re.search(r'Status:\s*(\w+)', content)
        if status_match:
            worker.status = status_match.group(1)
        
        # Parse claimed page
        claimed_match = re.search(r'Claimed Page:\s*(\d+)', content)
        if claimed_match:
            worker.claimed_page = int(claimed_match.group(1))
            
        # Parse started_at
        started_match = re.search(r'Started At:\s*([0-9T:Z+-]+)', content)
        if started_match:
            try:
                worker.started_at = datetime.fromisoformat(started_match.group(1).replace('Z', '+00:00')).timestamp()
            except:
                pass
        
        # Parse completed pages from table
        # Look for markdown table entries like: | 15 | 2026-01-01T05:30:00Z | a8f3b2c1 |
        for match in re.finditer(r'\|\s*(\d+)\s*\|.*?\|', content):
            page_num = int(match.group(1))
            if page_num > 0 and page_num <= self.total_pages:
                worker.completed_pages.append(page_num)
        
        self.workers[short_id] = worker
        
        # Update global completed pages
        self.completed_pages.update(worker.completed_pages)
        
        # Update global claimed pages (only from online workers)
        if worker.claimed_page and worker.is_online():
            self.claimed_pages[worker.claimed_page] = short_id
    
    def get_available_pages(self) -> List[int]:
        """Get list of available pages (not claimed and not completed)"""
        all_pages = set(range(1, self.total_pages + 1))
        unavailable = self.completed_pages | set(self.claimed_pages.keys())
        return sorted(all_pages - unavailable)
    
    def get_next_available_page(self) -> Optional[int]:
        """Get the lowest available page number"""
        available = self.get_available_pages()
        return available[0] if available else None
    
    def get_reclaimable_pages(self) -> List[Tuple[int, str]]:
        """Get pages claimed by stalled workers (page, worker_id)"""
        reclaimable = []
        for page, worker_id in self.claimed_pages.items():
            worker = self.workers.get(worker_id)
            if worker and worker.is_stalled():
                reclaimable.append((page, worker_id))
        return reclaimable
    
    def check_page_status(self, page: int) -> Tuple[str, Optional[str]]:
        """
        Check status of a specific page
        Returns: (status, worker_id)
        status: 'available', 'claimed', 'completed'
        """
        if page in self.completed_pages:
            return ('completed', None)
        if page in self.claimed_pages:
            return ('claimed', self.claimed_pages[page])
        return ('available', None)
    
    def to_dict(self) -> dict:
        return {
            "last_sync": self.last_sync,
            "last_sync_iso": datetime.fromtimestamp(self.last_sync).isoformat(),
            "total_pages": self.total_pages,
            "completed_pages": sorted(self.completed_pages),
            "claimed_pages": {str(k): v for k, v in self.claimed_pages.items()},
            "workers": {k: v.to_dict() for k, v in self.workers.items()},
            "statistics": {
                "total_workers": len(self.workers),
                "online_workers": sum(1 for w in self.workers.values() if w.is_online()),
                "offline_workers": sum(1 for w in self.workers.values() if not w.is_online()),
                "stalled_workers": sum(1 for w in self.workers.values() if w.is_stalled()),
                "completed_count": len(self.completed_pages),
                "claimed_count": len(self.claimed_pages),
                "available_count": len(self.get_available_pages()),
                "progress_percent": round(len(self.completed_pages) / self.total_pages * 100, 1)
            }
        }
    
    def save(self, filepath: str):
        """Save global state to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load(filepath: str) -> 'GlobalState':
        """Load global state from JSON file"""
        if not os.path.exists(filepath):
            return GlobalState()
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        state = GlobalState()
        state.last_sync = data.get('last_sync', 0)
        state.total_pages = data.get('total_pages', 99)
        state.completed_pages = set(data.get('completed_pages', []))
        state.claimed_pages = {int(k): v for k, v in data.get('claimed_pages', {}).items()}
        
        for worker_id, worker_data in data.get('workers', {}).items():
            worker = WorkerState(worker_data['branch'], worker_data['short_id'])
            worker.heartbeat = worker_data.get('heartbeat', 0)
            worker.status = worker_data.get('status', 'unknown')
            worker.claimed_page = worker_data.get('claimed_page')
            worker.completed_pages = worker_data.get('completed_pages', [])
            worker.started_at = worker_data.get('started_at')
            state.workers[worker_id] = worker
        
        return state


def run_command(cmd: List[str], capture_output=True) -> Tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return (result.returncode, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (1, "", "Command timed out")
    except Exception as e:
        return (1, "", str(e))


def discover_workers() -> List[Tuple[str, str]]:
    """
    Discover all active workers (branches with WORKER_STATE.md)
    Returns: List of (branch_name, short_id)
    """
    workers = []
    
    # Fetch all remote branches
    run_command(['git', 'fetch', 'origin', '--prune', '--quiet'])
    
    # List all cursor/* branches
    returncode, stdout, _ = run_command(['git', 'branch', '-r'])
    if returncode != 0:
        return workers
    
    cursor_branches = []
    for line in stdout.split('\n'):
        line = line.strip()
        if 'origin/cursor/' in line:
            branch = line.replace('origin/', '').strip()
            cursor_branches.append(branch)
    
    # Check which branches have WORKER_STATE.md
    for branch in cursor_branches:
        returncode, stdout, _ = run_command(
            ['git', 'show', f'origin/{branch}:WORKER_STATE.md']
        )
        if returncode == 0:
            # Extract short ID (last 4 chars)
            short_id = branch[-4:] if len(branch) >= 4 else branch
            workers.append((branch, short_id))
    
    return workers


def read_worker_state(branch: str) -> Optional[str]:
    """Read WORKER_STATE.md from a specific branch"""
    returncode, stdout, _ = run_command(
        ['git', 'show', f'origin/{branch}:WORKER_STATE.md']
    )
    if returncode == 0:
        return stdout
    return None


def sync_all_workers() -> GlobalState:
    """
    Sync all worker states and build global state
    This is the core function that prevents duplication
    """
    global_state = GlobalState()
    
    # Discover all active workers
    workers = discover_workers()
    
    # Read each worker's state
    for branch, short_id in workers:
        content = read_worker_state(branch)
        if content:
            global_state.update_from_worker_state(branch, short_id, content)
    
    global_state.last_sync = time.time()
    return global_state


def daemon_loop():
    """Main daemon loop - syncs every 60 seconds"""
    log_file = open(DAEMON_LOG_FILE, 'a')
    
    def log(msg: str):
        timestamp = datetime.now().isoformat()
        log_file.write(f"[{timestamp}] {msg}\n")
        log_file.flush()
    
    log("Sync daemon started")
    
    try:
        while True:
            try:
                log("Starting sync...")
                global_state = sync_all_workers()
                global_state.save(GLOBAL_STATE_FILE)
                
                stats = global_state.to_dict()['statistics']
                log(f"Sync complete: {stats['online_workers']} workers online, "
                    f"{stats['completed_count']} pages done, "
                    f"{stats['claimed_count']} claimed, "
                    f"{stats['available_count']} available")
                
                time.sleep(SYNC_INTERVAL)
                
            except Exception as e:
                log(f"Error during sync: {e}")
                time.sleep(SYNC_INTERVAL)
                
    except KeyboardInterrupt:
        log("Daemon stopped by user")
    finally:
        log_file.close()


def start_daemon():
    """Start the sync daemon in background"""
    # Check if daemon is already running
    if os.path.exists(DAEMON_PID_FILE):
        with open(DAEMON_PID_FILE, 'r') as f:
            old_pid = int(f.read().strip())
        try:
            os.kill(old_pid, 0)  # Check if process exists
            print(f"Daemon already running (PID {old_pid})")
            return
        except OSError:
            # Process doesn't exist, remove stale PID file
            os.remove(DAEMON_PID_FILE)
    
    # Fork and run daemon
    pid = os.fork()
    if pid > 0:
        # Parent process
        with open(DAEMON_PID_FILE, 'w') as f:
            f.write(str(pid))
        print(f"Sync daemon started (PID {pid})")
        print(f"Log: {DAEMON_LOG_FILE}")
        return
    
    # Child process - become daemon
    os.setsid()
    os.chdir('/')
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()
    
    daemon_loop()


def stop_daemon():
    """Stop the sync daemon"""
    if not os.path.exists(DAEMON_PID_FILE):
        print("Daemon not running")
        return
    
    with open(DAEMON_PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Daemon stopped (PID {pid})")
        os.remove(DAEMON_PID_FILE)
    except OSError:
        print(f"Daemon (PID {pid}) not found")
        os.remove(DAEMON_PID_FILE)


def get_next_page() -> Optional[int]:
    """Get next available page from cached global state"""
    if not os.path.exists(GLOBAL_STATE_FILE):
        # No cache, do immediate sync
        global_state = sync_all_workers()
        global_state.save(GLOBAL_STATE_FILE)
    else:
        global_state = GlobalState.load(GLOBAL_STATE_FILE)
    
    return global_state.get_next_available_page()


def check_page(page: int) -> Tuple[str, Optional[str]]:
    """Check if a specific page is available"""
    if not os.path.exists(GLOBAL_STATE_FILE):
        # No cache, do immediate sync
        global_state = sync_all_workers()
        global_state.save(GLOBAL_STATE_FILE)
    else:
        global_state = GlobalState.load(GLOBAL_STATE_FILE)
    
    return global_state.check_page_status(page)


def show_status():
    """Show current team status"""
    if not os.path.exists(GLOBAL_STATE_FILE):
        print("No global state found. Run --sync-now first.")
        return
    
    global_state = GlobalState.load(GLOBAL_STATE_FILE)
    data = global_state.to_dict()
    stats = data['statistics']
    
    print("\n=== TEAM STATUS ===")
    print(f"Last sync: {data['last_sync_iso']}")
    print(f"\nPages: {stats['completed_count']}/{data['total_pages']} complete ({stats['progress_percent']}%)")
    print(f"  Completed: {stats['completed_count']}")
    print(f"  Claimed: {stats['claimed_count']}")
    print(f"  Available: {stats['available_count']}")
    
    print(f"\nWorkers: {stats['total_workers']} total")
    print(f"  Online: {stats['online_workers']}")
    print(f"  Offline: {stats['offline_workers']}")
    print(f"  Stalled: {stats['stalled_workers']}")
    
    print("\n=== WORKER DETAILS ===")
    print(f"{'Worker':<8} {'Status':<12} {'Claimed':<8} {'Completed':<10} {'Heartbeat':<12}")
    print("-" * 60)
    
    for worker_id, worker_data in sorted(data['workers'].items()):
        status = "online" if worker_data['is_online'] else "OFFLINE"
        if worker_data['is_stalled']:
            status = "STALLED"
        
        claimed = str(worker_data['claimed_page']) if worker_data['claimed_page'] else "-"
        completed = len(worker_data['completed_pages'])
        
        if worker_data['heartbeat'] > 0:
            age = time.time() - worker_data['heartbeat']
            if age < 120:
                heartbeat = f"{int(age)}s ago"
            elif age < 3600:
                heartbeat = f"{int(age/60)}m ago"
            else:
                heartbeat = f"{int(age/3600)}h ago"
        else:
            heartbeat = "never"
        
        print(f"{worker_id:<8} {status:<12} {claimed:<8} {completed:<10} {heartbeat:<12}")
    
    # Show reclaimable pages
    reclaimable = global_state.get_reclaimable_pages()
    if reclaimable:
        print("\n=== RECLAIMABLE PAGES ===")
        for page, worker_id in reclaimable:
            print(f"Page {page}: claimed by {worker_id} (stalled)")


def sync_now():
    """Force immediate sync"""
    print("Syncing all worker states...")
    global_state = sync_all_workers()
    global_state.save(GLOBAL_STATE_FILE)
    stats = global_state.to_dict()['statistics']
    print(f"Sync complete: {stats['online_workers']} workers online, "
          f"{stats['completed_count']} pages done, "
          f"{stats['available_count']} available")


def show_reclaimable():
    """Show pages that can be reclaimed from stalled workers"""
    if not os.path.exists(GLOBAL_STATE_FILE):
        print("No global state found. Run --sync-now first.")
        return
    
    global_state = GlobalState.load(GLOBAL_STATE_FILE)
    reclaimable = global_state.get_reclaimable_pages()
    
    if not reclaimable:
        print("No reclaimable pages found.")
        return
    
    print("\n=== RECLAIMABLE PAGES ===")
    for page, worker_id in reclaimable:
        worker = global_state.workers[worker_id]
        age = time.time() - worker.heartbeat
        print(f"Page {page}: Claimed by {worker_id} ({int(age/60)} minutes ago, stalled)")


def main():
    parser = argparse.ArgumentParser(description='Multi-Agent Sync Daemon')
    parser.add_argument('--start', action='store_true', help='Start daemon in background')
    parser.add_argument('--stop', action='store_true', help='Stop daemon')
    parser.add_argument('--next-page', action='store_true', help='Get next available page')
    parser.add_argument('--check-page', type=int, metavar='N', help='Check if page N is available')
    parser.add_argument('--status', action='store_true', help='Show team status')
    parser.add_argument('--sync-now', action='store_true', help='Force immediate sync')
    parser.add_argument('--reclaimable', action='store_true', help='Show reclaimable pages')
    
    args = parser.parse_args()
    
    if args.start:
        start_daemon()
    elif args.stop:
        stop_daemon()
    elif args.next_page:
        page = get_next_page()
        if page:
            print(page)
        else:
            print("No pages available", file=sys.stderr)
            sys.exit(1)
    elif args.check_page:
        status, worker_id = check_page(args.check_page)
        if status == 'available':
            print("available")
        elif status == 'completed':
            print("completed")
        else:
            print(f"claimed_by_{worker_id}")
    elif args.status:
        show_status()
    elif args.sync_now:
        sync_now()
    elif args.reclaimable:
        show_reclaimable()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
