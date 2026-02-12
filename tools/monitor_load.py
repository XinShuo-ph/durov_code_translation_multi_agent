#!/usr/bin/env python3
"""
Load Balancing Monitor - Visualize work distribution across agents

Shows:
- Work distribution across all workers
- Who's over/under quota
- Offline/stuck workers
- Gaps in page coverage
- Recommendations for better balance

Usage:
    python3 monitor_load.py                   # Full dashboard
    python3 monitor_load.py --compact         # Compact view
    python3 monitor_load.py --json            # JSON output for scripts
"""

import json
import sys
import argparse
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

CACHE_DIR = Path(".sync_cache")
GLOBAL_STATE_FILE = CACHE_DIR / "global_state.json"


def load_global_state() -> Dict:
    """Load global state from sync daemon cache"""
    if not GLOBAL_STATE_FILE.exists():
        print("❌ Global state not found. Is sync daemon running?", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(GLOBAL_STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading global state: {e}", file=sys.stderr)
        sys.exit(1)


def format_heartbeat_age(timestamp: int) -> str:
    """Format heartbeat age in human-readable form"""
    age = int(time.time()) - timestamp
    
    if age < 60:
        return f"{age}s ago"
    elif age < 3600:
        return f"{age // 60}m ago"
    elif age < 86400:
        return f"{age // 3600}h ago"
    else:
        return f"{age // 86400}d ago"


def calculate_load_balance_metrics(state: Dict) -> Dict:
    """Calculate load balance metrics"""
    workers = state["workers"]
    online_workers = [w for w in workers if w["status"] == "online"]
    
    if not workers:
        return {"healthy": False, "reason": "No workers found"}
    
    if not online_workers:
        return {"healthy": False, "reason": "No online workers"}
    
    # Calculate statistics
    completed_counts = [len(w["completed"]) for w in online_workers]
    total_completed = sum(completed_counts)
    avg_completed = total_completed / len(online_workers) if online_workers else 0
    
    # Calculate standard deviation
    if len(completed_counts) > 1:
        variance = sum((x - avg_completed) ** 2 for x in completed_counts) / len(completed_counts)
        std_dev = variance ** 0.5
        std_dev_pct = (std_dev / avg_completed * 100) if avg_completed > 0 else 0
    else:
        std_dev = 0
        std_dev_pct = 0
    
    # Health check
    healthy = True
    issues = []
    
    if std_dev_pct > 40:
        healthy = False
        issues.append(f"High load imbalance: {std_dev_pct:.1f}% deviation")
    
    if len(state["pages"]["gaps"]) > len(state["pages"]["completed"]) * 0.1:
        healthy = False
        issues.append(f"Too many gaps: {len(state['pages']['gaps'])} gaps")
    
    offline_count = len(workers) - len(online_workers)
    if offline_count > len(workers) * 0.3:
        healthy = False
        issues.append(f"Too many offline workers: {offline_count}/{len(workers)}")
    
    return {
        "healthy": healthy,
        "issues": issues,
        "total_workers": len(workers),
        "online_workers": len(online_workers),
        "avg_completed": avg_completed,
        "std_dev": std_dev,
        "std_dev_pct": std_dev_pct,
        "total_completed": total_completed,
        "gap_count": len(state["pages"]["gaps"]),
        "gap_pct": (len(state["pages"]["gaps"]) / max(1, total_completed)) * 100
    }


def print_full_dashboard(state: Dict):
    """Print full monitoring dashboard"""
    metrics = calculate_load_balance_metrics(state)
    
    print("=" * 80)
    print("MULTI-AGENT LOAD DISTRIBUTION DASHBOARD")
    print("=" * 80)
    print()
    
    # Summary
    print(f"Last sync: {format_heartbeat_age(state['last_sync'])}")
    print(f"Total pages: {state['summary']['total_pages']}")
    print(f"Completed: {state['summary']['completed_count']} ({state['summary']['completed_count']/state['summary']['total_pages']*100:.1f}%)")
    print(f"Claimed: {state['summary']['claimed_count']}")
    print(f"Available: {state['summary']['available_count']}")
    print(f"Gaps: {state['summary']['gap_count']}")
    print()
    
    # Health status
    if metrics["healthy"]:
        print("Status: ✅ HEALTHY")
    else:
        print("Status: ⚠️  ISSUES DETECTED")
        for issue in metrics["issues"]:
            print(f"  - {issue}")
    print()
    
    # Load balance stats
    print(f"Load distribution: {metrics['std_dev_pct']:.1f}% std deviation", end="")
    if metrics['std_dev_pct'] < 15:
        print(" ✅")
    elif metrics['std_dev_pct'] < 25:
        print(" ⚠️")
    else:
        print(" 🛑")
    print(f"Average pages/worker: {metrics['avg_completed']:.1f}")
    print()
    
    # Worker table
    print("=" * 80)
    print("WORKER STATUS")
    print("-" * 80)
    print(f"{'Worker':<8} {'Status':<8} {'Done':<6} {'Claimed':<10} {'Heartbeat':<12} {'Quota':<12}")
    print("-" * 80)
    
    # Calculate fair share for quota status
    fair_share = state['summary']['total_pages'] // metrics['online_workers'] if metrics['online_workers'] > 0 else 0
    max_pages = fair_share + max(2, int(fair_share * 0.2))
    
    # Sort workers: online first, then by completed pages (descending)
    sorted_workers = sorted(
        state["workers"],
        key=lambda w: (w["status"] != "online", -len(w["completed"]))
    )
    
    for worker in sorted_workers:
        worker_id = worker["id"]
        status = worker["status"]
        completed = len(worker["completed"])
        claimed = worker["claimed"]
        claimed_str = f"{claimed}" if claimed else "[]"
        heartbeat_age = format_heartbeat_age(worker["heartbeat"])
        
        # Quota status
        if status != "online":
            quota_status = "-"
        elif completed >= max_pages:
            quota_status = "OVER 🛑"
        elif completed > fair_share + 1:
            quota_status = "NEAR ⚠️"
        elif completed >= fair_share - 2:
            quota_status = "OK ✅"
        else:
            quota_status = "BELOW ⬇️"
        
        # Format status with emoji
        status_display = status
        if status == "online":
            status_display = "online ✓"
        elif status == "offline":
            status_display = "offline ✗"
        
        print(f"{worker_id:<8} {status_display:<8} {completed:<6} {claimed_str:<10} {heartbeat_age:<12} {quota_status:<12}")
    
    print("-" * 80)
    print()
    
    # Gaps
    if state["pages"]["gaps"]:
        print("GAPS IN PAGE SEQUENCE:")
        gaps = state["pages"]["gaps"]
        if len(gaps) <= 20:
            print(f"  {', '.join(map(str, gaps))}")
        else:
            print(f"  {', '.join(map(str, gaps[:20]))}... ({len(gaps)} total)")
        print()
    
    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("-" * 80)
    
    overloaded = [w for w in state["workers"] if w["status"] == "online" and len(w["completed"]) >= max_pages]
    underloaded = [w for w in state["workers"] if w["status"] == "online" and len(w["completed"]) < fair_share - 2]
    offline = [w for w in state["workers"] if w["status"] == "offline"]
    
    if overloaded:
        print(f"⏸️  Workers should PAUSE (over quota): {', '.join(w['id'] for w in overloaded)}")
    
    if underloaded:
        print(f"⚡ Workers should CLAIM MORE: {', '.join(w['id'] for w in underloaded)}")
    
    if state["pages"]["gaps"]:
        print(f"🔍 Focus on GAPS first: {len(state['pages']['gaps'])} gaps need filling")
    
    if offline:
        print(f"⚠️  Offline workers: {', '.join(w['id'] for w in offline)}")
        if any(w["claimed"] for w in offline):
            print(f"   Some offline workers have claimed pages - these can be reclaimed")
    
    if not (overloaded or underloaded or state["pages"]["gaps"] or offline):
        print("✅ Everything looks good! Keep up the balanced work.")
    
    print("=" * 80)


def print_compact_view(state: Dict):
    """Print compact view"""
    metrics = calculate_load_balance_metrics(state)
    
    status_symbol = "✅" if metrics.get("healthy", False) else "⚠️"
    std_dev_pct = metrics.get("std_dev_pct", 0) if isinstance(metrics, dict) and "std_dev_pct" in metrics else 0
    print(f"{status_symbol} Workers: {state['summary']['online_workers']}/{state['summary']['total_workers']} online | "
          f"Completed: {state['summary']['completed_count']}/{state['summary']['total_pages']} | "
          f"Gaps: {state['summary']['gap_count']} | "
          f"Balance: {std_dev_pct:.1f}% dev")


def main():
    parser = argparse.ArgumentParser(description="Monitor multi-agent load distribution")
    parser.add_argument("--compact", action="store_true", help="Compact one-line view")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    state = load_global_state()
    metrics = calculate_load_balance_metrics(state)
    
    if args.json:
        output = {
            "state": state,
            "metrics": metrics
        }
        print(json.dumps(output, indent=2))
    elif args.compact:
        print_compact_view(state)
    else:
        print_full_dashboard(state)


if __name__ == "__main__":
    main()
