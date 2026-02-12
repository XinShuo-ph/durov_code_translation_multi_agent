#!/usr/bin/env python3
"""
Protocol Health Metrics - Monitor multi-agent protocol health

Tracks:
- Load distribution (std deviation)
- Gap percentage
- Duplicate rate
- Coverage rate (pages/hour)
- Worker participation rate

Usage:
    python3 metrics.py --report        # Full health report
    python3 metrics.py --baseline      # Set baseline for coverage rate
    python3 metrics.py --json          # JSON output
"""

import json
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

CACHE_DIR = Path(".sync_cache")
GLOBAL_STATE_FILE = CACHE_DIR / "global_state.json"
BASELINE_FILE = CACHE_DIR / "baseline.json"


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


def load_baseline() -> Optional[Dict]:
    """Load baseline metrics"""
    if not BASELINE_FILE.exists():
        return None
    
    try:
        with open(BASELINE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_baseline(metrics: Dict):
    """Save baseline metrics"""
    CACHE_DIR.mkdir(exist_ok=True)
    with open(BASELINE_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Baseline saved to {BASELINE_FILE}")


def calculate_health_metrics(state: Dict, baseline: Optional[Dict] = None) -> Dict:
    """Calculate comprehensive health metrics"""
    workers = state["workers"]
    online_workers = [w for w in workers if w["status"] == "online"]
    
    # Load distribution
    if online_workers:
        completed_counts = [len(w["completed"]) for w in online_workers]
        total_completed = sum(completed_counts)
        avg_completed = total_completed / len(online_workers)
        
        if len(completed_counts) > 1:
            variance = sum((x - avg_completed) ** 2 for x in completed_counts) / len(completed_counts)
            std_dev = variance ** 0.5
            std_dev_pct = (std_dev / avg_completed * 100) if avg_completed > 0 else 0
        else:
            std_dev = 0
            std_dev_pct = 0
    else:
        total_completed = 0
        avg_completed = 0
        std_dev = 0
        std_dev_pct = 0
    
    # Gap percentage
    gap_count = len(state["pages"]["gaps"])
    gap_pct = (gap_count / max(1, total_completed)) * 100
    
    # Worker participation
    total_workers = len(workers)
    online_count = len(online_workers)
    participation_pct = (online_count / max(1, total_workers)) * 100
    
    # Coverage rate (requires baseline)
    coverage_rate = None
    coverage_pct = None
    if baseline:
        time_elapsed = state["last_sync"] - baseline.get("timestamp", state["last_sync"])
        pages_added = total_completed - baseline.get("completed", 0)
        
        if time_elapsed > 0:
            coverage_rate = (pages_added / time_elapsed) * 3600  # pages per hour
            baseline_rate = baseline.get("coverage_rate", coverage_rate)
            coverage_pct = (coverage_rate / baseline_rate * 100) if baseline_rate > 0 else 100
    
    # Health scoring
    health_score = 100
    issues = []
    warnings = []
    
    # Load distribution (30 points)
    if std_dev_pct > 40:
        health_score -= 30
        issues.append(f"Critical load imbalance: {std_dev_pct:.1f}% deviation")
    elif std_dev_pct > 25:
        health_score -= 15
        warnings.append(f"High load imbalance: {std_dev_pct:.1f}% deviation")
    elif std_dev_pct > 15:
        health_score -= 5
        warnings.append(f"Moderate load imbalance: {std_dev_pct:.1f}% deviation")
    
    # Gap percentage (20 points)
    if gap_pct > 10:
        health_score -= 20
        issues.append(f"Too many gaps: {gap_pct:.1f}%")
    elif gap_pct > 5:
        health_score -= 10
        warnings.append(f"Some gaps: {gap_pct:.1f}%")
    
    # Worker participation (30 points)
    if participation_pct < 50:
        health_score -= 30
        issues.append(f"Low participation: {participation_pct:.1f}%")
    elif participation_pct < 70:
        health_score -= 15
        warnings.append(f"Moderate participation: {participation_pct:.1f}%")
    elif participation_pct < 85:
        health_score -= 5
        warnings.append(f"Good participation: {participation_pct:.1f}%")
    
    # Coverage rate (20 points)
    if coverage_pct is not None:
        if coverage_pct < 50:
            health_score -= 20
            issues.append(f"Low coverage rate: {coverage_pct:.1f}% of baseline")
        elif coverage_pct < 80:
            health_score -= 10
            warnings.append(f"Below baseline coverage: {coverage_pct:.1f}%")
    
    # Overall health status
    if health_score >= 90:
        status = "HEALTHY"
    elif health_score >= 70:
        status = "FAIR"
    elif health_score >= 50:
        status = "POOR"
    else:
        status = "CRITICAL"
    
    return {
        "status": status,
        "health_score": health_score,
        "issues": issues,
        "warnings": warnings,
        "metrics": {
            "load_distribution": {
                "std_dev": std_dev,
                "std_dev_pct": std_dev_pct,
                "avg_completed": avg_completed,
                "threshold_excellent": 15,
                "threshold_good": 25,
                "threshold_poor": 40
            },
            "gaps": {
                "count": gap_count,
                "percentage": gap_pct,
                "threshold_excellent": 5,
                "threshold_good": 10
            },
            "participation": {
                "online_workers": online_count,
                "total_workers": total_workers,
                "percentage": participation_pct,
                "threshold_excellent": 85,
                "threshold_good": 70,
                "threshold_poor": 50
            },
            "coverage": {
                "rate": coverage_rate,
                "percentage_of_baseline": coverage_pct,
                "threshold_excellent": 100,
                "threshold_good": 80,
                "threshold_poor": 50
            },
            "completion": {
                "completed": total_completed,
                "total": state["summary"]["total_pages"],
                "percentage": (total_completed / state["summary"]["total_pages"] * 100)
            }
        }
    }


def print_health_report(health: Dict):
    """Print detailed health report"""
    print("=" * 80)
    print("PROTOCOL HEALTH REPORT")
    print("=" * 80)
    print()
    
    # Overall status
    status_symbols = {
        "HEALTHY": "✅",
        "FAIR": "⚠️ ",
        "POOR": "⚠️ ",
        "CRITICAL": "🛑"
    }
    symbol = status_symbols.get(health["status"], "")
    print(f"Overall Status: {symbol} {health['status']}")
    print(f"Health Score: {health['health_score']}/100")
    print()
    
    # Critical issues
    if health["issues"]:
        print("🛑 CRITICAL ISSUES:")
        for issue in health["issues"]:
            print(f"  - {issue}")
        print()
    
    # Warnings
    if health["warnings"]:
        print("⚠️  WARNINGS:")
        for warning in health["warnings"]:
            print(f"  - {warning}")
        print()
    
    # Detailed metrics
    print("=" * 80)
    print("DETAILED METRICS")
    print("-" * 80)
    
    # Load distribution
    ld = health["metrics"]["load_distribution"]
    print(f"Load Distribution:")
    print(f"  Standard Deviation: {ld['std_dev']:.2f} pages")
    print(f"  Deviation %: {ld['std_dev_pct']:.1f}%", end="")
    if ld['std_dev_pct'] < ld['threshold_excellent']:
        print(" ✅ Excellent")
    elif ld['std_dev_pct'] < ld['threshold_good']:
        print(" ⚠️  Fair")
    else:
        print(" 🛑 Poor")
    print(f"  Average pages/worker: {ld['avg_completed']:.1f}")
    print()
    
    # Gaps
    gaps = health["metrics"]["gaps"]
    print(f"Gap Coverage:")
    print(f"  Gap count: {gaps['count']}")
    print(f"  Gap %: {gaps['percentage']:.1f}%", end="")
    if gaps['percentage'] < gaps['threshold_excellent']:
        print(" ✅ Excellent")
    elif gaps['percentage'] < gaps['threshold_good']:
        print(" ⚠️  Fair")
    else:
        print(" 🛑 Poor")
    print()
    
    # Participation
    part = health["metrics"]["participation"]
    print(f"Worker Participation:")
    print(f"  Online workers: {part['online_workers']}/{part['total_workers']}")
    print(f"  Participation %: {part['percentage']:.1f}%", end="")
    if part['percentage'] >= part['threshold_excellent']:
        print(" ✅ Excellent")
    elif part['percentage'] >= part['threshold_good']:
        print(" ⚠️  Fair")
    elif part['percentage'] >= part['threshold_poor']:
        print(" ⚠️  Poor")
    else:
        print(" 🛑 Critical")
    print()
    
    # Coverage rate
    cov = health["metrics"]["coverage"]
    print(f"Coverage Rate:")
    if cov['rate'] is not None:
        print(f"  Current rate: {cov['rate']:.2f} pages/hour")
        print(f"  vs Baseline: {cov['percentage_of_baseline']:.1f}%", end="")
        if cov['percentage_of_baseline'] >= cov['threshold_excellent']:
            print(" ✅ Excellent")
        elif cov['percentage_of_baseline'] >= cov['threshold_good']:
            print(" ⚠️  Fair")
        else:
            print(" 🛑 Poor")
    else:
        print("  No baseline set - run with --baseline to set")
    print()
    
    # Completion
    comp = health["metrics"]["completion"]
    print(f"Project Completion:")
    print(f"  Pages: {comp['completed']}/{comp['total']}")
    print(f"  Progress: {comp['percentage']:.1f}%")
    
    # Progress bar
    bar_length = 50
    filled = int(bar_length * comp['percentage'] / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"  [{bar}] {comp['percentage']:.1f}%")
    
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Protocol health metrics")
    parser.add_argument("--report", action="store_true", help="Full health report")
    parser.add_argument("--baseline", action="store_true", help="Set current state as baseline")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    # Load state
    state = load_global_state()
    if not state:
        sys.exit(1)
    
    # Handle baseline setting
    if args.baseline:
        baseline_data = {
            "timestamp": state["last_sync"],
            "completed": state["summary"]["completed_count"],
            "workers": state["summary"]["total_workers"],
            "coverage_rate": 5.0  # Default assumption: 5 pages/hour baseline
        }
        save_baseline(baseline_data)
        print(f"Baseline set: {baseline_data}")
        sys.exit(0)
    
    # Calculate health
    baseline = load_baseline()
    health = calculate_health_metrics(state, baseline)
    
    if args.json:
        print(json.dumps(health, indent=2))
    else:
        print_health_report(health)


if __name__ == "__main__":
    main()
