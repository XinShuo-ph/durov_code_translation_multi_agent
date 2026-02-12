#!/usr/bin/env python3
"""
Multi-Agent Sync Service

Provides automated synchronization and coordination for multi-agent translation.

Features:
- Auto-fetches all branches every 30 seconds
- Maintains global state cache
- Provides atomic page claiming
- Detects and resolves conflicts
- Auto-updates worker heartbeats
"""

import json
import os
import sys
import time
import subprocess
import argparse
import signal
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import hashlib

class SyncService:
    """Core sync service for multi-agent coordination"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.state = {}
        self.last_sync = 0
        self.running = True
        self.sync_interval = 30  # seconds
        self.cache_dir = Path(".sync_cache")
        self.pid_file = Path("sync_service.pid")
        self.log_file = Path("sync_service.log")
        
    def log(self, message: str):
        """Write to log file"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_msg)
        print(message)
    
    def load_global_state(self) -> Dict[str, Any]:
        """Load STATE.json from disk"""
        if not os.path.exists("STATE.json"):
            self.log("ERROR: STATE.json not found. Run init_project.py first.")
            return {}
        
        with open("STATE.json", 'r') as f:
            return json.load(f)
    
    def save_global_state(self, state: Dict[str, Any]):
        """Save STATE.json to disk"""
        state['last_updated'] = int(time.time())
        with open("STATE.json", 'w') as f:
            json.dump(state, f, indent=2)
    
    def git_fetch_all(self):
        """Fetch all remote branches"""
        try:
            subprocess.run(
                ["git", "fetch", "origin", "--prune"],
                check=True,
                capture_output=True,
                timeout=30
            )
            return True
        except Exception as e:
            self.log(f"ERROR: Git fetch failed: {e}")
            return False
    
    def git_push(self) -> bool:
        """Push current branch"""
        try:
            result = subprocess.run(
                ["git", "push", "-u", "origin", "HEAD"],
                check=True,
                capture_output=True,
                timeout=30
            )
            return True
        except Exception as e:
            self.log(f"ERROR: Git push failed: {e}")
            return False
    
    def get_all_branches(self) -> List[str]:
        """Get list of all remote cursor/* branches"""
        try:
            result = subprocess.run(
                ["git", "branch", "-r"],
                check=True,
                capture_output=True,
                text=True
            )
            
            branches = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if line.startswith("origin/cursor/"):
                    branch = line.replace("origin/", "")
                    branches.append(branch)
            
            return branches
        except Exception as e:
            self.log(f"ERROR: Failed to get branches: {e}")
            return []
    
    def read_file_from_branch(self, branch: str, filepath: str) -> Optional[str]:
        """Read file content from a specific branch"""
        try:
            result = subprocess.run(
                ["git", "show", f"origin/{branch}:{filepath}"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout
        except:
            return None
    
    def aggregate_worker_states(self) -> Dict[str, Any]:
        """Collect all worker states from all branches"""
        workers = {}
        branches = self.get_all_branches()
        
        self.log(f"Aggregating states from {len(branches)} branches...")
        
        for branch in branches:
            # Extract worker ID from branch name
            worker_id = branch.split('-')[-1]
            
            # Try to read worker state file
            worker_file = f"worker-states/worker-{worker_id}.json"
            content = self.read_file_from_branch(branch, worker_file)
            
            if content:
                try:
                    state = json.loads(content)
                    state['branch'] = branch
                    workers[worker_id] = state
                except json.JSONDecodeError:
                    self.log(f"WARNING: Invalid JSON in {branch}:{worker_file}")
        
        self.log(f"Found {len(workers)} workers with valid states")
        return workers
    
    def update_global_state(self) -> Dict[str, Any]:
        """Build global state from all worker states"""
        # Load current global state
        global_state = self.load_global_state()
        if not global_state:
            return {}
        
        # Aggregate all worker states
        workers = self.aggregate_worker_states()
        
        # Compute claimed, completed, available pages
        claimed = {}
        completed = set()
        now = int(time.time())
        
        for worker_id, state in workers.items():
            # Check if worker is online (heartbeat < 10 min old)
            heartbeat = state.get('heartbeat', 0)
            age = now - heartbeat
            
            if age > 600:  # 10 minutes
                state['status'] = 'offline'
                # Don't count offline workers' claims after 15 min
                if age > 900:
                    continue
            
            # Collect claimed page
            claimed_page = state.get('claimed_page')
            if claimed_page:
                claimed[claimed_page] = {
                    'worker_id': worker_id,
                    'claimed_at': state.get('claim_time', 0),
                    'status': state.get('status', 'unknown')
                }
            
            # Collect completed pages
            for page_info in state.get('completed_pages', []):
                if isinstance(page_info, dict):
                    completed.add(page_info['page'])
                else:
                    completed.add(page_info)
        
        # Calculate available pages
        total_pages = global_state['total_pages']
        all_pages = set(range(1, total_pages + 1))
        available = sorted(all_pages - set(claimed.keys()) - completed)
        
        # Update global state
        global_state['workers'] = workers
        global_state['claimed_pages'] = claimed
        global_state['completed_pages'] = sorted(completed)
        global_state['available_pages'] = available
        global_state['last_updated'] = now
        
        return global_state
    
    def detect_conflicts(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find duplicate page claims"""
        conflicts = []
        
        # Group workers by claimed page
        claims_by_page = {}
        for worker_id, worker_state in state['workers'].items():
            page = worker_state.get('claimed_page')
            if page:
                if page not in claims_by_page:
                    claims_by_page[page] = []
                claims_by_page[page].append({
                    'worker_id': worker_id,
                    'claim_time': worker_state.get('claim_time', 0)
                })
        
        # Find pages with multiple claims
        for page, claims in claims_by_page.items():
            if len(claims) > 1:
                conflicts.append({
                    'page': page,
                    'claims': claims
                })
        
        return conflicts
    
    def get_next_available_page(self) -> Optional[int]:
        """Get the next available page number"""
        state = self.update_global_state()
        
        if not state or not state['available_pages']:
            return None
        
        return state['available_pages'][0]
    
    def claim_page(self, page: int) -> str:
        """
        Atomically claim a page.
        Returns: "SUCCESS", "CONFLICT", or "ERROR"
        """
        # 1. Check page availability
        state = self.update_global_state()
        
        if page in state['completed_pages']:
            return f"ERROR: Page {page} already completed"
        
        if page in state['claimed_pages']:
            existing = state['claimed_pages'][page]
            return f"ERROR: Page {page} already claimed by {existing['worker_id']}"
        
        # 2. Create/update worker state
        worker_state_file = Path(f"worker-states/worker-{self.worker_id}.json")
        
        if worker_state_file.exists():
            with open(worker_state_file, 'r') as f:
                worker_state = json.load(f)
        else:
            # Create new worker state
            worker_state = {
                "worker_id": self.worker_id,
                "branch": self.get_current_branch(),
                "completed_pages": [],
                "stats": {
                    "pages_completed": 0,
                    "pages_claimed": 0
                }
            }
        
        # Update claim
        worker_state['claimed_page'] = page
        worker_state['claim_time'] = int(time.time())
        worker_state['heartbeat'] = int(time.time())
        worker_state['status'] = 'claiming'
        
        # Write worker state
        with open(worker_state_file, 'w') as f:
            json.dump(worker_state, f, indent=2)
        
        # 3. Git commit and push
        try:
            subprocess.run(["git", "add", str(worker_state_file)], check=True)
            subprocess.run([
                "git", "commit", "-m",
                f"[{self.worker_id}] CLAIM: Page {page} HEARTBEAT: {worker_state['claim_time']}"
            ], check=True)
            
            if not self.git_push():
                return "ERROR: Failed to push claim"
            
        except Exception as e:
            return f"ERROR: Git operations failed: {e}"
        
        # 4. Immediate re-fetch to check for conflicts
        time.sleep(2)  # Brief delay to let remote settle
        self.git_fetch_all()
        
        # 5. Validate claim
        state = self.update_global_state()
        claimed_info = state['claimed_pages'].get(page)
        
        if not claimed_info:
            return "ERROR: Claim validation failed"
        
        if claimed_info['worker_id'] != self.worker_id:
            # Someone else claimed it earlier
            self.revert_claim()
            return f"CONFLICT: Page {page} claimed by {claimed_info['worker_id']}"
        
        # 6. Confirm claim
        worker_state['status'] = 'translating'
        with open(worker_state_file, 'w') as f:
            json.dump(worker_state, f, indent=2)
        
        try:
            subprocess.run(["git", "add", str(worker_state_file)], check=True)
            subprocess.run([
                "git", "commit", "-m",
                f"[{self.worker_id}] CLAIM CONFIRMED: Page {page}"
            ], check=True)
            self.git_push()
        except:
            pass  # Confirmation push is best-effort
        
        return "SUCCESS"
    
    def complete_page(self, page: int, translation_file: str) -> str:
        """
        Mark page as completed and submit translation.
        Returns: "SUCCESS" or "ERROR: ..."
        """
        # Validate translation file exists
        if not os.path.exists(translation_file):
            return f"ERROR: Translation file not found: {translation_file}"
        
        # Validate JSON
        try:
            with open(translation_file, 'r') as f:
                translation_data = json.load(f)
        except json.JSONDecodeError as e:
            return f"ERROR: Invalid JSON in translation file: {e}"
        
        # Load worker state
        worker_state_file = Path(f"worker-states/worker-{self.worker_id}.json")
        if not worker_state_file.exists():
            return "ERROR: Worker state not found"
        
        with open(worker_state_file, 'r') as f:
            worker_state = json.load(f)
        
        # Update worker state
        worker_state['claimed_page'] = None
        worker_state['status'] = 'online'
        worker_state['heartbeat'] = int(time.time())
        
        # Add to completed pages
        page_hash = hashlib.sha256(
            json.dumps(translation_data, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        worker_state['completed_pages'].append({
            'page': page,
            'completed_at': int(time.time()),
            'hash': page_hash
        })
        
        worker_state['stats']['pages_completed'] = len(worker_state['completed_pages'])
        
        # Save worker state
        with open(worker_state_file, 'w') as f:
            json.dump(worker_state, f, indent=2)
        
        # Update global state
        global_state = self.load_global_state()
        if page not in global_state['completed_pages']:
            global_state['completed_pages'].append(page)
            global_state['completed_pages'].sort()
        
        if page in global_state['claimed_pages']:
            del global_state['claimed_pages'][page]
        
        if page in global_state['available_pages']:
            global_state['available_pages'].remove(page)
        
        global_state['stats']['total_completions'] += 1
        
        self.save_global_state(global_state)
        
        # Git commit and push
        try:
            subprocess.run(["git", "add", translation_file, str(worker_state_file), "STATE.json"], check=True)
            
            commit_msg = f"[{self.worker_id}] DONE: Page {page} HASH: {page_hash} HEARTBEAT: {worker_state['heartbeat']}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            if not self.git_push():
                return "ERROR: Failed to push completion"
            
            return "SUCCESS"
            
        except Exception as e:
            return f"ERROR: Git operations failed: {e}"
    
    def revert_claim(self):
        """Revert a claim (used when conflict detected)"""
        worker_state_file = Path(f"worker-states/worker-{self.worker_id}.json")
        
        if worker_state_file.exists():
            with open(worker_state_file, 'r') as f:
                worker_state = json.load(f)
            
            worker_state['claimed_page'] = None
            worker_state['status'] = 'online'
            
            with open(worker_state_file, 'w') as f:
                json.dump(worker_state, f, indent=2)
    
    def get_current_branch(self) -> str:
        """Get current git branch name"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def get_status(self) -> Dict[str, Any]:
        """Get global project status"""
        state = self.update_global_state()
        
        if not state:
            return {"error": "Failed to load state"}
        
        online_workers = sum(
            1 for w in state['workers'].values()
            if w.get('status') != 'offline'
        )
        
        return {
            "project": state['project'],
            "total_pages": state['total_pages'],
            "completed": len(state['completed_pages']),
            "claimed": len(state['claimed_pages']),
            "available": len(state['available_pages']),
            "workers_total": len(state['workers']),
            "workers_online": online_workers,
            "progress_percent": round(len(state['completed_pages']) / state['total_pages'] * 100, 1)
        }
    
    def update_heartbeat(self):
        """Update worker heartbeat"""
        worker_state_file = Path(f"worker-states/worker-{self.worker_id}.json")
        
        if not worker_state_file.exists():
            return
        
        with open(worker_state_file, 'r') as f:
            worker_state = json.load(f)
        
        worker_state['heartbeat'] = int(time.time())
        
        with open(worker_state_file, 'w') as f:
            json.dump(worker_state, f, indent=2)
        
        # Push heartbeat update (best effort, don't fail if it doesn't work)
        try:
            subprocess.run(["git", "add", str(worker_state_file)], check=True, timeout=5)
            subprocess.run([
                "git", "commit", "-m",
                f"[{self.worker_id}] HEARTBEAT: {worker_state['heartbeat']}"
            ], check=True, timeout=5)
            self.git_push()
        except:
            pass  # Heartbeat updates are best-effort
    
    def run_daemon(self):
        """Main daemon loop"""
        self.log(f"Starting sync daemon for worker {self.worker_id}")
        
        # Write PID file
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, lambda sig, frame: self.stop_daemon())
        signal.signal(signal.SIGINT, lambda sig, frame: self.stop_daemon())
        
        last_heartbeat = 0
        
        try:
            while self.running:
                # Fetch and sync
                self.log("Syncing...")
                self.git_fetch_all()
                state = self.update_global_state()
                
                # Update heartbeat every 60 seconds
                now = time.time()
                if now - last_heartbeat > 60:
                    self.update_heartbeat()
                    last_heartbeat = now
                
                # Detect conflicts
                conflicts = self.detect_conflicts(state)
                if conflicts:
                    self.log(f"WARNING: {len(conflicts)} conflicts detected")
                
                # Sleep
                time.sleep(self.sync_interval)
                
        except Exception as e:
            self.log(f"ERROR: Daemon error: {e}")
        finally:
            self.stop_daemon()
    
    def stop_daemon(self):
        """Stop the daemon"""
        self.running = False
        if self.pid_file.exists():
            self.pid_file.unlink()
        self.log("Sync daemon stopped")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Sync Service")
    parser.add_argument("--worker-id", help="Worker ID (4 characters)")
    parser.add_argument("--start", action="store_true", help="Start sync daemon")
    parser.add_argument("--stop", action="store_true", help="Stop sync daemon")
    parser.add_argument("--status", action="store_true", help="Get project status")
    parser.add_argument("--next-page", action="store_true", help="Get next available page")
    parser.add_argument("--claim-page", type=int, help="Claim a page")
    parser.add_argument("--complete-page", type=int, help="Complete a page")
    parser.add_argument("--file", help="Translation file (for --complete-page)")
    parser.add_argument("--check-page", type=int, help="Check if page is available")
    
    args = parser.parse_args()
    
    # Commands that don't require worker_id
    if args.stop:
        pid_file = Path("sync_service.pid")
        if pid_file.exists():
            pid = int(pid_file.read_text().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print("Sync daemon stopped")
            except ProcessLookupError:
                print("Sync daemon not running")
                pid_file.unlink()
        else:
            print("Sync daemon not running")
        return
    
    if args.status:
        service = SyncService("status")
        status = service.get_status()
        print(f"Project: {status.get('project', 'unknown')}")
        print(f"Total pages: {status.get('total_pages', 0)}")
        print(f"Completed: {status.get('completed', 0)} ({status.get('progress_percent', 0)}%)")
        print(f"Claimed: {status.get('claimed', 0)}")
        print(f"Available: {status.get('available', 0)}")
        print(f"Workers online: {status.get('workers_online', 0)}/{status.get('workers_total', 0)}")
        return
    
    # Commands that require worker_id
    if not args.worker_id:
        print("ERROR: --worker-id required")
        sys.exit(1)
    
    service = SyncService(args.worker_id)
    
    if args.start:
        # Check if already running
        if service.pid_file.exists():
            print("ERROR: Sync daemon already running")
            print(f"PID: {service.pid_file.read_text().strip()}")
            sys.exit(1)
        
        # Start daemon
        service.run_daemon()
    
    elif args.next_page:
        page = service.get_next_available_page()
        if page:
            print(page)
        else:
            print("NONE")
    
    elif args.claim_page:
        result = service.claim_page(args.claim_page)
        print(result)
        if not result.startswith("SUCCESS"):
            sys.exit(1)
    
    elif args.complete_page:
        if not args.file:
            print("ERROR: --file required for --complete-page")
            sys.exit(1)
        
        result = service.complete_page(args.complete_page, args.file)
        print(result)
        if not result.startswith("SUCCESS"):
            sys.exit(1)
    
    elif args.check_page:
        state = service.update_global_state()
        if args.check_page in state['available_pages']:
            print("AVAILABLE")
        elif args.check_page in state['completed_pages']:
            print("COMPLETED")
        elif args.check_page in state['claimed_pages']:
            claimed_by = state['claimed_pages'][args.check_page]['worker_id']
            print(f"CLAIMED by {claimed_by}")
        else:
            print("UNKNOWN")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
