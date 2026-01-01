import subprocess
import re
import time
import sys

def get_branches():
    cmd = "git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def get_file_content(branch, filename):
    cmd = f"git show origin/{branch}:{filename}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout

def get_translation_files(branch):
    # Check for any json file in translations/ folder (recursive)
    cmd = f"git ls-tree -r origin/{branch} --name-only | grep 'translations/.*page_.*.json'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    files = result.stdout.strip().split('\n')
    pages = []
    for f in files:
        if not f: continue
        match = re.search(r'page_(\d+).json', f)
        if match:
            pages.append(int(match.group(1)))
    return pages

def parse_worker_state(content):
    if not content:
        return None
    
    state = {}
    
    # Heartbeat
    heartbeat_match = re.search(r'Heartbeat\*{0,2}:\s*(\d+)', content, re.IGNORECASE)
    if heartbeat_match:
        state['heartbeat'] = int(heartbeat_match.group(1))
    else:
        state['heartbeat'] = 0
        
    # Status
    status_match = re.search(r'Status\*{0,2}:\s*(\w+)', content, re.IGNORECASE)
    if status_match:
        state['status'] = status_match.group(1)
    else:
        state['status'] = 'unknown'

    # Claimed Page
    claimed_match = re.search(r'Claimed Page\*{0,2}:\s*(\S+)', content, re.IGNORECASE)
    if claimed_match:
        val = claimed_match.group(1).lower()
        if val == 'none' or val == '-':
            state['claimed_page'] = None
        else:
            try:
                state['claimed_page'] = int(val)
            except:
                state['claimed_page'] = None
    else:
        state['claimed_page'] = None

    # Check for completed pages in tables (Markdown table format)
    # Looking for lines like "| 22 | done |" or "| 22 | Completed |"
    completed_in_md = []
    # Simple regex for table rows with page number and 'done'/'completed'
    table_rows = re.findall(r'\|\s*(\d+)\s*\|\s*(?:done|completed)\s*\|', content, re.IGNORECASE)
    for p in table_rows:
        completed_in_md.append(int(p))
    
    state['completed_in_md'] = completed_in_md
    
    # Also look for claims in tables if not found in header
    # e.g. "| 23 | translating |" or "| 23 | claimed |"
    if state['claimed_page'] is None:
        claim_rows = re.findall(r'\|\s*(\d+)\s*\|\s*(?:translating|claimed|in_progress)\s*\|', content, re.IGNORECASE)
        if claim_rows:
            # Take the last one if multiple? Or assume only one active.
            state['claimed_page'] = int(claim_rows[-1])

    return state

def main():
    branches = get_branches()
    known_workers = []
    all_claimed_completed = set()
    
    current_time = int(time.time())
    
    print(f"Current time: {current_time}")

    for branch in branches:
        if not branch: continue
        short_id = branch.split('-')[-1]
        
        content = get_file_content(branch, 'WORKER_STATE.md')
        if not content:
            continue
            
        state = parse_worker_state(content)
        if not state:
            continue
            
        # Check if offline
        is_online = (current_time - state['heartbeat']) < 600
        
        worker_info = {
            'short_id': short_id,
            'branch': branch,
            'status': state['status'],
            'claimed_page': state['claimed_page'],
            'heartbeat': state['heartbeat'],
            'is_online': is_online
        }
        known_workers.append(worker_info)
        
        # If online, respect claim. If offline > 15 min, ignore claim (allow reclaim)
        # 15 min = 900 sec.
        if is_online or (current_time - state['heartbeat'] < 900):
            if state['claimed_page']:
                all_claimed_completed.add(state['claimed_page'])
        
        # Add completed pages from MD
        all_claimed_completed.update(state['completed_in_md'])
        
        # Get completed pages from translation files
        completed_files = get_translation_files(branch)
        all_claimed_completed.update(completed_files)

    print("\nKnown Workers:")
    for w in known_workers:
        print(f"{w['short_id']} | {w['status']} | Claimed: {w['claimed_page']} | Heartbeat: {w['heartbeat']} | Online: {w['is_online']}")

    print("\nUnavailable Pages (Claimed or Completed):")
    unavailable = sorted(list(all_claimed_completed))
    print(unavailable)
    
    # Find lowest available page
    # Start from 1. 0 is front matter, usually handled separately but instructions say:
    # Chapter 0: 1-4, 5-6, 7-12.
    # So page 1 is valid.
    for page in range(1, 100):
        if page not in all_claimed_completed:
            print(f"\nLowest available page: {page}")
            break

if __name__ == "__main__":
    main()
