import subprocess
import re
import json
import time

def get_active_workers():
    cmd = "git branch -r | grep 'origin/cursor/' | sed 's|origin/||' | tr -d ' '"
    branches = subprocess.check_output(cmd, shell=True).decode('utf-8').strip().split('\n')
    
    workers = []
    claimed_pages = set()
    completed_pages = set()
    
    for branch in branches:
        if not branch: continue
        
        try:
            # Check if WORKER_STATE.md exists
            subprocess.check_call(f"git show 'origin/{branch}:WORKER_STATE.md' > /dev/null 2>&1", shell=True)
            
            # Read content
            content = subprocess.check_output(f"git show 'origin/{branch}:WORKER_STATE.md'", shell=True).decode('utf-8')
            
            short_id = branch.split('-')[-1]
            
            # Extract heartbeat
            heartbeat_match = re.search(r'Heartbeat\*\*: (\d+)', content)
            heartbeat = int(heartbeat_match.group(1)) if heartbeat_match else 0
            
            # Extract claimed page
            claimed_match = re.search(r'Claimed Page\*\*: (\d+|none)', content)
            claimed = claimed_match.group(1) if claimed_match else "none"
            if claimed != "none":
                claimed_pages.add(int(claimed))
                
            # Extract completed pages
            # Look for lines like "| 13 |" in the table
            completed_matches = re.findall(r'\|\s*(\d+)\s*\|', content)
            for page in completed_matches:
                completed_pages.add(int(page))
            
            workers.append({
                'short_id': short_id,
                'branch': branch,
                'heartbeat': heartbeat,
                'claimed': claimed,
                'status': 'online' if (time.time() - heartbeat) < 600 else 'offline'
            })
            
        except subprocess.CalledProcessError:
            continue
            
    return workers, claimed_pages, completed_pages

workers, claimed, completed = get_active_workers()

print(f"Found {len(workers)} workers")
print(f"Claimed pages: {sorted(list(claimed))}")
print(f"Completed pages: {sorted(list(completed))}")

# Find lowest available page
all_pages = set(range(1, 100))
available = sorted(list(all_pages - claimed - completed))

if available:
    print(f"Next available page: {available[0]}")
else:
    print("No pages available!")

# Generate known workers table for my state file
print("\n## Known Workers Table")
print("| Short ID | Status | Claimed Page | Last Heartbeat |")
print("|----------|--------|--------------|----------------|")
for w in workers:
    print(f"| {w['short_id']} | {w['status']} | {w['claimed']} | {w['heartbeat']} |")
