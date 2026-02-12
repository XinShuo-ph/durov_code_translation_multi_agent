#!/usr/bin/env python3
"""
Compute stripe assignment and scan for unclaimed pages.

Usage:
    python3 tools/compute_stripe.py                  # Show my stripe + status
    python3 tools/compute_stripe.py --next            # Print next page to work on
    python3 tools/compute_stripe.py --scan            # Scan all branches for gaps
    python3 tools/compute_stripe.py --status          # Show global progress summary
    python3 tools/compute_stripe.py --total-pages 99  # Override total page count
"""

import subprocess
import sys
import os
import json
import re
from collections import defaultdict


def run(cmd, timeout=30):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""


def get_my_branch():
    return run("git branch --show-current")


def get_my_id(branch):
    match = re.search(r'([0-9a-f]{4})$', branch)
    return match.group(1) if match else branch[-4:]


def get_prefix(branch):
    """Extract experiment prefix (everything before the last -XXXX ID)."""
    return re.sub(r'-[^-]+$', '', branch)


def discover_peers(prefix):
    """Find all peer branches with the same prefix."""
    run("git fetch origin --prune", timeout=60)
    raw = run("git branch -r")
    peers = []
    for line in raw.splitlines():
        line = line.strip()
        branch = line.replace("origin/", "")
        # Match branches with our prefix
        if branch.startswith(f"cursor/{prefix}-"):
            short_id = branch.split("-")[-1]
            if re.match(r'^[0-9a-f]{4}$', short_id):
                peers.append(short_id)
    return sorted(set(peers))


def compute_stripe(my_pos, num_workers, total_pages):
    """Compute deterministic stripe pages for a given worker position."""
    pages = []
    p = my_pos + 1  # 1-indexed pages
    while p <= total_pages:
        pages.append(p)
        p += num_workers
    return pages


def scan_completed_pages(prefix, total_pages):
    """Scan all peer branches for completed translation files."""
    raw = run("git branch -r")
    completed = {}  # page_num -> branch that has it

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        branch = line.replace("origin/", "")
        if not branch.startswith(f"cursor/{prefix}-"):
            continue

        # List translation files on this branch
        files = run(f'git ls-tree --name-only "origin/{branch}" -- translations/ 2>/dev/null')
        for fname in files.splitlines():
            fname = fname.strip()
            if not fname:
                continue
            # Extract page number from filename like translations/page_001.json
            match = re.search(r'page_(\d+)', fname)
            if match:
                page_num = int(match.group(1))
                if page_num not in completed:
                    completed[page_num] = branch

    return completed


def scan_local_completed():
    """Check locally completed translations."""
    completed = set()
    translations_dir = "translations"
    if os.path.isdir(translations_dir):
        for fname in os.listdir(translations_dir):
            match = re.search(r'page_(\d+)', fname)
            if match:
                completed.add(int(match.group(1)))
    return completed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Compute stripe assignment and scan for work")
    parser.add_argument("--next", action="store_true", help="Print next page to work on")
    parser.add_argument("--scan", action="store_true", help="Scan all branches for gaps")
    parser.add_argument("--status", action="store_true", help="Show global progress summary")
    parser.add_argument("--total-pages", type=int, default=99, help="Total number of pages")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    total_pages = args.total_pages
    my_branch = get_my_branch()

    if not my_branch:
        print("ERROR: Not on a git branch", file=sys.stderr)
        sys.exit(1)

    my_id = get_my_id(my_branch)
    prefix = get_prefix(my_branch.replace("cursor/", ""))

    # Discover peers
    peers = discover_peers(prefix)
    num_workers = len(peers) if peers else 1

    # Find my position
    my_pos = 0
    if my_id in peers:
        my_pos = peers.index(my_id)

    # Compute stripe
    stripe = compute_stripe(my_pos, num_workers, total_pages)

    # Check local completions
    local_done = scan_local_completed()

    if args.scan or args.status or args.next:
        # Full scan of all branches
        completed = scan_completed_pages(prefix, total_pages)
        completed_set = set(completed.keys()) | local_done
        unclaimed = sorted(set(range(1, total_pages + 1)) - completed_set)
        remaining_stripe = [p for p in stripe if p not in completed_set]

        if args.next:
            # Return next page to work on
            if remaining_stripe:
                print(remaining_stripe[0])
            elif unclaimed:
                print(unclaimed[0])
            else:
                print("ALL_DONE")
            return

        if args.status:
            print(f"=== Global Progress ===")
            print(f"Total pages: {total_pages}")
            print(f"Completed: {len(completed_set)} ({100*len(completed_set)/total_pages:.0f}%)")
            print(f"Remaining: {len(unclaimed)}")
            print(f"Active workers: {num_workers}")
            if unclaimed:
                print(f"Next unclaimed: {unclaimed[:10]}{'...' if len(unclaimed) > 10 else ''}")
            print()

            # Per-worker breakdown
            worker_pages = defaultdict(list)
            for page, branch in completed.items():
                worker_id = branch.split("-")[-1]
                worker_pages[worker_id].append(page)
            for wid in sorted(worker_pages.keys()):
                pages = sorted(worker_pages[wid])
                print(f"  {wid}: {len(pages)} pages — {pages[:8]}{'...' if len(pages) > 8 else ''}")
            return

        if args.scan:
            print(f"=== Scan Results ===")
            print(f"Completed pages: {sorted(completed_set)}")
            print(f"Unclaimed pages: {unclaimed}")
            return

    # Default: show my assignment
    if args.json:
        output = {
            "my_id": my_id,
            "my_position": my_pos,
            "num_workers": num_workers,
            "peers": peers,
            "stripe_pages": stripe,
            "total_pages": total_pages,
            "local_completed": sorted(local_done),
            "remaining_stripe": [p for p in stripe if p not in local_done],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"=== Stripe Assignment ===")
        print(f"Worker ID:   {my_id}")
        print(f"Position:    {my_pos} of {num_workers}")
        print(f"Peers:       {', '.join(peers)}")
        print(f"My stripe:   {stripe}")
        remaining = [p for p in stripe if p not in local_done]
        print(f"Remaining:   {remaining}")
        print(f"Completed:   {sorted(local_done)}")
        if remaining:
            print(f"\nNext page to translate: {remaining[0]}")
        else:
            print(f"\nStripe complete! Run with --next to find scavenge pages.")


if __name__ == "__main__":
    main()
