#!/usr/bin/env python3
"""
Multi-worker sync verification script.
Checks consistency across all active workers.
"""

import subprocess
import json
import sys
from pathlib import Path
from collections import defaultdict

def get_active_workers():
    """Get list of all active worker branches."""
    result = subprocess.run(
        ['git', 'fetch', '--all', '--prune'],
        capture_output=True,
        text=True
    )
    
    result = subprocess.run(
        ['git', 'branch', '-r'],
        capture_output=True,
        text=True
    )
    
    branches = []
    for line in result.stdout.split('\n'):
        if 'origin/cursor/' in line:
            branch = line.strip().replace('origin/', '')
            # Check if has WORKER_STATE.md
            check = subprocess.run(
                ['git', 'show', f'origin/{branch}:WORKER_STATE.md'],
                capture_output=True,
                text=True
            )
            if check.returncode == 0:
                short_id = branch.split('-')[-1]
                branches.append((branch, short_id))
    
    return branches

def get_worker_state(branch):
    """Extract key info from worker state."""
    result = subprocess.run(
        ['git', 'show', f'origin/{branch}:WORKER_STATE.md'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return None
    
    state = {
        'milestone': 'unknown',
        'status': 'unknown',
        'm0_done': False,
        'm1_done': False,
        'vote': None,
        'claimed_pages': [],
        'completed_pages': []
    }
    
    for line in result.stdout.split('\n'):
        if '**Milestone**:' in line:
            if 'M0' in line:
                state['milestone'] = 'M0'
            elif 'M1' in line:
                state['milestone'] = 'M1'
            elif 'M2' in line:
                state['milestone'] = 'M2'
        
        if '**Status**:' in line:
            if 'completed' in line:
                state['status'] = 'completed'
            elif 'working' in line:
                state['status'] = 'working'
        
        if 'format_approach' in line and '|' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                state['vote'] = parts[2].strip()
    
    return state

def verify_sync():
    """Verify synchronization across all workers."""
    print("=" * 60)
    print("Multi-Worker Sync Verification")
    print("=" * 60)
    
    workers = get_active_workers()
    print(f"\n✓ Found {len(workers)} active workers\n")
    
    # Collect states
    states = {}
    for branch, short_id in workers:
        state = get_worker_state(branch)
        if state:
            states[short_id] = state
            status_icon = "✓" if state['status'] == 'completed' else "→"
            print(f"  {status_icon} {short_id}: {state['milestone']} ({state['status']})")
    
    # Check M0 consensus
    print("\n" + "=" * 60)
    print("M0 Status:")
    m0_complete = sum(1 for s in states.values() if s['milestone'] in ['M1', 'M2'])
    print(f"  {m0_complete}/{len(states)} workers completed M0")
    
    # Check M1 votes
    print("\n" + "=" * 60)
    print("M1 Voting:")
    votes = defaultdict(int)
    for short_id, state in states.items():
        if state['vote']:
            votes[state['vote']] += 1
            print(f"  {short_id}: {state['vote']}")
    
    print("\nVote Tally:")
    for approach, count in sorted(votes.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(states)) * 100
        print(f"  {approach}: {count} votes ({percentage:.1f}%)")
    
    # Check if consensus reached
    quorum = len(states) // 2 + 1
    consensus = None
    for approach, count in votes.items():
        if count >= quorum:
            consensus = approach
            break
    
    print(f"\nQuorum needed: {quorum}/{len(states)} (>50%)")
    if consensus:
        print(f"✓ CONSENSUS REACHED: {consensus}")
    else:
        print(f"✗ No consensus yet (need {quorum - max(votes.values())} more votes)")
    
    # M2 readiness
    print("\n" + "=" * 60)
    print("M2 Readiness:")
    m1_complete = sum(1 for s in states.values() if s['milestone'] in ['M1', 'M2'] and s['status'] == 'completed')
    print(f"  {m1_complete}/{len(states)} workers completed M1")
    
    if consensus and m1_complete == len(states):
        print("\n✓ READY FOR M2: All workers complete, consensus reached")
        return True
    else:
        print(f"\n✗ NOT READY FOR M2")
        if not consensus:
            print(f"  - Waiting for voting consensus")
        if m1_complete < len(states):
            print(f"  - Waiting for {len(states) - m1_complete} workers to complete M1")
        return False

if __name__ == "__main__":
    ready = verify_sync()
    sys.exit(0 if ready else 1)
