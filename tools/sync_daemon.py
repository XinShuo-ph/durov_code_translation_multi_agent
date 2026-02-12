#!/usr/bin/env python3
"""
Multi-Agent Sync Daemon

Continuously syncs with all worker branches to maintain authoritative view
of claimed/completed pages and active workers.

This is the MANDATORY synchronization service for protocol v2.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class WorkerInfo:
    """Information about a worker parsed from their branch."""
    id: str
    branch: str
    status: str  # online, offline, working, idle
    heartbeat: int  # Unix timestamp
    claimed_page: Optional[int]
    claim_time: Optional[int]
    completed_pages: List[int]
    stats: Dict[str, float]
    
    def is_online(self, now: int) -> bool:
        """Worker is online if heartbeat is <10 minutes old."""
        return (now - self.heartbeat) < 600
    
    def is_stale(self, now: int) -> bool:
        """Worker is stale if heartbeat is >10 minutes old."""
        return (now - self.heartbeat) >= 600
    
    def claim_age_minutes(self, now: int) -> float:
        """Age of current claim in minutes."""
        if self.claim_time is None:
            return 0
        return (now - self.claim_time) / 60


@dataclass
class PageInfo:
    """Information about a page's status."""
    page: int
    status: str  # available, claimed, completed, stale
    claimed_by: Optional[str]
    claim_time: Optional[int]
    completed_by: Optional[str]
    completion_time: Optional[int]
    hash: Optional[str]


class SyncDaemon:
    """
    Multi-agent synchronization daemon.
    
    Continuously fetches all worker branches and maintains
    authoritative view of system state.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent
        self.workspace_root = Path(workspace_root)
        self.sync_dir = self.workspace_root / ".sync"
        self.sync_dir.mkdir(exist_ok=True)
        
        self.state_file = self.sync_dir / "global_state.json"
        self.warnings_file = self.sync_dir / "warnings.log"
        self.pid_file = self.sync_dir / "daemon.pid"
        
        # Get my identity
        self.my_branch = self._get_current_branch()
        self.my_id = self._extract_worker_id(self.my_branch)
        
        # Cached state
        self.workers: Dict[str, WorkerInfo] = {}
        self.pages: Dict[int, PageInfo] = {}
        self.last_sync: int = 0
        
    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    def _extract_worker_id(self, branch: str) -> str:
        """Extract worker ID from branch name (last component after final dash)."""
        if not branch:
            return "unknown"
        parts = branch.split('-')
        return parts[-1] if parts else "unknown"
    
    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run git command."""
        return subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=check,
            cwd=self.workspace_root
        )
    
    def _fetch_all_branches(self) -> None:
        """Fetch all remote branches."""
        self._run_git(["fetch", "origin", "--all", "--prune"])
    
    def _list_worker_branches(self) -> List[str]:
        """List all cursor/* branches."""
        result = self._run_git(["branch", "-r"])
        branches = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("origin/cursor/"):
                branch = line.replace("origin/", "")
                branches.append(branch)
        return branches
    
    def _has_worker_state(self, branch: str) -> bool:
        """Check if branch has WORKER_STATE.md."""
        result = self._run_git(
            ["show", f"origin/{branch}:WORKER_STATE.md"],
            check=False
        )
        return result.returncode == 0
    
    def _get_file_from_branch(self, branch: str, filepath: str) -> Optional[str]:
        """Get file contents from a branch."""
        result = self._run_git(
            ["show", f"origin/{branch}:{filepath}"],
            check=False
        )
        if result.returncode == 0:
            return result.stdout
        return None
    
    def _parse_worker_state(self, branch: str) -> Optional[WorkerInfo]:
        """Parse WORKER_STATE.md from a branch."""
        content = self._get_file_from_branch(branch, "WORKER_STATE.md")
        if content is None:
            return None
        
        worker_id = self._extract_worker_id(branch)
        
        # Parse fields with regex
        heartbeat_match = re.search(r'\*\*Heartbeat\*\*:\s*(\d+)', content)
        status_match = re.search(r'\*\*Status\*\*:\s*(\w+)', content)
        claimed_page_match = re.search(r'\*\*Claimed Page\*\*:\s*(\d+|none)', content)
        claim_time_match = re.search(r'\*\*Claim Time\*\*:\s*(\d+)', content)
        
        heartbeat = int(heartbeat_match.group(1)) if heartbeat_match else 0
        status = status_match.group(1) if status_match else "unknown"
        
        claimed_page = None
        if claimed_page_match and claimed_page_match.group(1) != "none":
            try:
                claimed_page = int(claimed_page_match.group(1))
            except ValueError:
                claimed_page = None
        
        claim_time = None
        if claim_time_match:
            claim_time = int(claim_time_match.group(1))
        
        # Parse completed pages table
        completed_pages = []
        for match in re.finditer(r'\|\s*(\d+)\s*\|', content):
            try:
                page = int(match.group(1))
                if 1 <= page <= 999:  # Valid page numbers
                    completed_pages.append(page)
            except ValueError:
                continue
        
        # Remove duplicates and sort
        completed_pages = sorted(set(completed_pages))
        
        # Calculate stats
        stats = {
            "total_completed": len(completed_pages),
            "avg_time_minutes": 0.0,  # Would need to parse from table
            "uptime_minutes": 0.0  # Would need to calculate
        }
        
        return WorkerInfo(
            id=worker_id,
            branch=branch,
            status=status,
            heartbeat=heartbeat,
            claimed_page=claimed_page,
            claim_time=claim_time,
            completed_pages=completed_pages,
            stats=stats
        )
    
    def _scan_translations(self, branch: str) -> List[Tuple[int, str]]:
        """Scan translations/ directory on a branch for completed pages.
        
        Returns list of (page_number, hash) tuples.
        """
        result = self._run_git(
            ["ls-tree", "-r", "--name-only", f"origin/{branch}"],
            check=False
        )
        
        if result.returncode != 0:
            return []
        
        completed = []
        for line in result.stdout.splitlines():
            # Match translations/page_NNN.json or translations/raw/page_NNN.json
            match = re.search(r'translations/(?:raw/)?page_(\d+)\.json', line)
            if match:
                page_num = int(match.group(1))
                
                # Get file hash
                file_content = self._get_file_from_branch(branch, line)
                if file_content:
                    # Simple hash of first 100 chars
                    hash_val = hex(hash(file_content[:100]))[-8:]
                    completed.append((page_num, hash_val))
        
        return completed
    
    def sync(self) -> None:
        """
        Perform a full sync cycle.
        
        1. Fetch all branches
        2. Parse all WORKER_STATE.md files
        3. Scan for completed translations
        4. Detect conflicts
        5. Update global state
        """
        now = int(time.time())
        
        # Fetch all branches
        self._fetch_all_branches()
        
        # Find all worker branches
        branches = self._list_worker_branches()
        
        # Parse worker states
        workers = {}
        for branch in branches:
            if self._has_worker_state(branch):
                worker = self._parse_worker_state(branch)
                if worker:
                    workers[worker.id] = worker
        
        # Build page status map
        pages = {}
        
        # First pass: Mark completed pages
        for worker in workers.values():
            # From WORKER_STATE.md completed_pages
            for page in worker.completed_pages:
                if page not in pages:
                    pages[page] = PageInfo(
                        page=page,
                        status="completed",
                        claimed_by=None,
                        claim_time=None,
                        completed_by=worker.id,
                        completion_time=None,
                        hash=None
                    )
            
            # From translations/ directory
            for page, hash_val in self._scan_translations(worker.branch):
                if page in pages:
                    pages[page].hash = hash_val
                else:
                    pages[page] = PageInfo(
                        page=page,
                        status="completed",
                        claimed_by=None,
                        claim_time=None,
                        completed_by=worker.id,
                        completion_time=None,
                        hash=hash_val
                    )
        
        # Second pass: Mark claimed pages
        for worker in workers.values():
            if worker.claimed_page is not None:
                page = worker.claimed_page
                
                # If page is already completed, this is an orphaned claim
                if page in pages and pages[page].status == "completed":
                    self._log_warning(
                        f"Worker {worker.id} claims completed page {page}"
                    )
                    continue
                
                # Check for conflicts (multiple claims)
                if page in pages and pages[page].status == "claimed":
                    # Conflict! Multiple workers claim same page
                    self._detect_claim_conflict(page, pages[page], worker, now)
                else:
                    # New claim
                    status = "claimed"
                    if worker.is_stale(now):
                        status = "stale"
                    
                    pages[page] = PageInfo(
                        page=page,
                        status=status,
                        claimed_by=worker.id,
                        claim_time=worker.claim_time,
                        completed_by=None,
                        completion_time=None,
                        hash=None
                    )
        
        # Update cached state
        self.workers = workers
        self.pages = pages
        self.last_sync = now
        
        # Write global state to disk
        self._write_global_state()
    
    def _detect_claim_conflict(self, page: int, existing: PageInfo, 
                               new_worker: WorkerInfo, now: int) -> None:
        """
        Detect and resolve claim conflict.
        
        Resolution: Earliest claim_time wins. If tie, alphabetical worker ID.
        """
        existing_worker_id = existing.claimed_by
        existing_claim_time = existing.claim_time or 0
        new_claim_time = new_worker.claim_time or 0
        
        # Determine winner
        if abs(existing_claim_time - new_claim_time) > 5:
            # Clear winner by timestamp
            if new_claim_time < existing_claim_time:
                winner = new_worker.id
                loser = existing_worker_id
            else:
                winner = existing_worker_id
                loser = new_worker.id
        else:
            # Tie - use alphabetical
            if new_worker.id < existing_worker_id:
                winner = new_worker.id
                loser = existing_worker_id
            else:
                winner = existing_worker_id
                loser = new_worker.id
        
        # Log conflict
        self._log_warning(
            f"Page {page} conflict: {existing_worker_id} vs {new_worker.id} "
            f"(winner: {winner})"
        )
        
        # Update page status
        if winner == new_worker.id:
            self.pages[page] = PageInfo(
                page=page,
                status="claimed",
                claimed_by=new_worker.id,
                claim_time=new_claim_time,
                completed_by=None,
                completion_time=None,
                hash=None
            )
    
    def _log_warning(self, message: str) -> None:
        """Log warning to warnings.log."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.warnings_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def _write_global_state(self) -> None:
        """Write global state to JSON file."""
        now = int(time.time())
        
        state = {
            "last_update": now,
            "workers": [asdict(w) for w in self.workers.values()],
            "pages": {
                str(p): asdict(info) for p, info in self.pages.items()
            },
            "stats": self._calculate_stats(),
            "conflicts": [],
            "stale_claims": self._find_stale_claims()
        }
        
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def _calculate_stats(self) -> Dict:
        """Calculate global statistics."""
        now = int(time.time())
        
        workers_online = sum(1 for w in self.workers.values() if w.is_online(now))
        workers_offline = len(self.workers) - workers_online
        
        completed = sum(1 for p in self.pages.values() if p.status == "completed")
        claimed = sum(1 for p in self.pages.values() if p.status == "claimed")
        stale = sum(1 for p in self.pages.values() if p.status == "stale")
        
        # Assume total pages is max(99, highest page number seen)
        total_pages = 99
        if self.pages:
            total_pages = max(99, max(self.pages.keys()))
        
        available = total_pages - completed - claimed - stale
        
        return {
            "total_pages": total_pages,
            "completed": completed,
            "claimed": claimed,
            "stale": stale,
            "available": max(0, available),
            "workers_online": workers_online,
            "workers_offline": workers_offline
        }
    
    def _find_stale_claims(self) -> List[Dict]:
        """Find stale claims that can be reclaimed."""
        now = int(time.time())
        stale = []
        
        for page, info in self.pages.items():
            if info.status in ["claimed", "stale"] and info.claimed_by:
                worker = self.workers.get(info.claimed_by)
                if worker and worker.is_stale(now):
                    age_minutes = worker.claim_age_minutes(now)
                    stale.append({
                        "page": page,
                        "worker": info.claimed_by,
                        "age_minutes": age_minutes
                    })
        
        return stale
    
    def next_page(self) -> Optional[int]:
        """Get next available page (lowest number)."""
        # Reload state from disk
        self._load_state()
        
        stats = self._calculate_stats()
        total_pages = stats["total_pages"]
        
        # Find lowest available page
        for page in range(1, total_pages + 1):
            if page not in self.pages:
                return page
            if self.pages[page].status == "available":
                return page
        
        return None
    
    def check_page(self, page: int) -> str:
        """
        Check status of a specific page.
        
        Returns: "AVAILABLE" | "CLAIMED_BY:worker_id" | "COMPLETED" | "STALE"
        """
        self._load_state()
        
        if page not in self.pages:
            return "AVAILABLE"
        
        info = self.pages[page]
        if info.status == "completed":
            return "COMPLETED"
        elif info.status == "claimed":
            return f"CLAIMED_BY:{info.claimed_by}"
        elif info.status == "stale":
            return "STALE"
        else:
            return "AVAILABLE"
    
    def who_claimed(self, page: int) -> Optional[str]:
        """Return worker ID who claimed a page, or None."""
        self._load_state()
        
        if page in self.pages:
            return self.pages[page].claimed_by
        return None
    
    def get_stale_claims(self) -> List[Tuple[int, Dict]]:
        """Get list of stale claims that can be reclaimed."""
        self._load_state()
        
        stale_claims = self._find_stale_claims()
        result = []
        for claim in stale_claims:
            page = claim["page"]
            worker_id = claim["worker"]
            if worker_id in self.workers:
                result.append((page, asdict(self.workers[worker_id])))
        
        return result
    
    def get_stats(self) -> Dict:
        """Get global statistics."""
        self._load_state()
        return self._calculate_stats()
    
    def my_status(self) -> Optional[Dict]:
        """Get my worker status."""
        self._load_state()
        
        if self.my_id in self.workers:
            return asdict(self.workers[self.my_id])
        return None
    
    def _load_state(self) -> None:
        """Load state from disk if it exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                
                # Reconstruct workers
                self.workers = {}
                for w_data in state.get("workers", []):
                    worker = WorkerInfo(**w_data)
                    self.workers[worker.id] = worker
                
                # Reconstruct pages
                self.pages = {}
                for page_str, p_data in state.get("pages", {}).items():
                    page_num = int(page_str)
                    self.pages[page_num] = PageInfo(**p_data)
                
                self.last_sync = state.get("last_update", 0)
            except Exception as e:
                # State file corrupted, will resync
                pass
    
    def run_daemon(self, interval: int = 60) -> None:
        """
        Run sync daemon in foreground.
        
        Syncs every `interval` seconds (default: 60).
        """
        print(f"Sync daemon starting (interval: {interval}s)")
        print(f"My ID: {self.my_id}")
        print(f"State file: {self.state_file}")
        
        # Write PID
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))
        
        try:
            while True:
                print(f"\n[{time.strftime('%H:%M:%S')}] Syncing...")
                try:
                    self.sync()
                    stats = self._calculate_stats()
                    print(f"  Workers online: {stats['workers_online']}")
                    print(f"  Pages completed: {stats['completed']}")
                    print(f"  Pages claimed: {stats['claimed']}")
                    print(f"  Pages available: {stats['available']}")
                except Exception as e:
                    print(f"  ERROR during sync: {e}")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nShutting down sync daemon...")
            self.pid_file.unlink(missing_ok=True)
    
    def stop_daemon(self) -> None:
        """Stop running daemon."""
        if self.pid_file.exists():
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 15)  # SIGTERM
                print(f"Stopped daemon (PID {pid})")
                self.pid_file.unlink()
            except ProcessLookupError:
                print(f"Daemon not running (stale PID file)")
                self.pid_file.unlink()
        else:
            print("No daemon running")


def main():
    parser = argparse.ArgumentParser(description="Multi-agent sync daemon")
    parser.add_argument("--start", action="store_true", help="Start daemon")
    parser.add_argument("--stop", action="store_true", help="Stop daemon")
    parser.add_argument("--status", action="store_true", help="Print global status")
    parser.add_argument("--next-page", action="store_true", help="Get next available page")
    parser.add_argument("--check-page", type=int, help="Check specific page status")
    parser.add_argument("--my-status", action="store_true", help="Get my worker status")
    parser.add_argument("--force-sync", action="store_true", help="Force immediate sync")
    parser.add_argument("--metrics", action="store_true", help="Print metrics")
    parser.add_argument("--interval", type=int, default=60, help="Sync interval (seconds)")
    
    args = parser.parse_args()
    
    daemon = SyncDaemon()
    
    if args.start:
        daemon.run_daemon(interval=args.interval)
    
    elif args.stop:
        daemon.stop_daemon()
    
    elif args.status:
        daemon.sync()  # Force sync
        stats = daemon.get_stats()
        print("Global Status:")
        print(f"  Total pages: {stats['total_pages']}")
        print(f"  Completed: {stats['completed']}")
        print(f"  Claimed: {stats['claimed']}")
        print(f"  Stale: {stats['stale']}")
        print(f"  Available: {stats['available']}")
        print(f"  Workers online: {stats['workers_online']}")
        print(f"  Workers offline: {stats['workers_offline']}")
    
    elif args.next_page:
        next_page = daemon.next_page()
        if next_page:
            print(next_page)
        else:
            print("No pages available")
            sys.exit(1)
    
    elif args.check_page is not None:
        status = daemon.check_page(args.check_page)
        print(status)
    
    elif args.my_status:
        status = daemon.my_status()
        if status:
            print(f"Worker: {status['id']}")
            print(f"Status: {status['status']}")
            print(f"Claimed: {status['claimed_page'] or 'none'}")
            print(f"Completed: {len(status['completed_pages'])} pages")
            print(f"Heartbeat: {status['heartbeat']}")
        else:
            print("Not registered (no WORKER_STATE.md)")
    
    elif args.force_sync:
        daemon.sync()
        print("Sync complete")
    
    elif args.metrics:
        daemon._load_state()
        # Calculate metrics
        # TODO: Implement metrics calculation
        print("Metrics not yet implemented")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
