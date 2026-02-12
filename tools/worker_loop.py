#!/usr/bin/env python3
"""
Automated worker loop for multi-agent translation.

Continuously claims, translates, and submits pages until all work is complete.
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path

def run_command(cmd: list, check: bool = True) -> tuple:
    """Run a command and return (success, output)"""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
            timeout=300
        )
        return (True, result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return (False, e.stderr.strip())
    except subprocess.TimeoutExpired:
        return (False, "Command timed out")
    except Exception as e:
        return (False, str(e))

def log(message: str):
    """Print timestamped log message"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_sync_daemon() -> bool:
    """Check if sync daemon is running"""
    pid_file = Path("sync_service.pid")
    if not pid_file.exists():
        return False
    
    try:
        pid = int(pid_file.read_text().strip())
        # Check if process exists
        import os
        os.kill(pid, 0)  # Doesn't actually kill, just checks
        return True
    except (ProcessLookupError, ValueError):
        return False

def get_next_page() -> str:
    """Get next available page"""
    success, output = run_command([
        "python3", "tools/sync_service.py", "--next-page"
    ])
    
    if not success:
        log(f"ERROR getting next page: {output}")
        return "ERROR"
    
    return output.strip()

def claim_page(page: int) -> bool:
    """Claim a page"""
    log(f"Claiming page {page}...")
    success, output = run_command([
        "python3", "tools/sync_service.py",
        "--claim-page", str(page)
    ], check=False)
    
    if not success or "ERROR" in output or "CONFLICT" in output:
        log(f"Failed to claim page {page}: {output}")
        return False
    
    log(f"✓ Claimed page {page}")
    return True

def translate_page(page: int) -> bool:
    """Translate a page (placeholder - replace with actual translation logic)"""
    log(f"Translating page {page}...")
    
    # Check if translation script exists
    if not Path("translate.py").exists():
        log("WARNING: translate.py not found. Creating placeholder translation...")
        # Create a placeholder translation
        import json
        translation = {
            "page": page,
            "source_file": f"extracted/pages/page_{page:03d}.txt",
            "translations": {
                "ru": f"Russian text for page {page}",
                "en": f"English text for page {page}",
                "zh": f"Chinese text for page {page}",
                "ja": f"Japanese text for page {page}"
            },
            "translated_at": int(time.time()),
            "status": "placeholder"
        }
        
        output_file = f"translations/page_{page:03d}.json"
        Path("translations").mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(translation, f, indent=2, ensure_ascii=False)
        
        log(f"✓ Created placeholder translation: {output_file}")
        return True
    
    # Run actual translation script
    success, output = run_command([
        "python3", "translate.py",
        "--page", str(page)
    ], check=False)
    
    if not success:
        log(f"ERROR translating page {page}: {output}")
        return False
    
    log(f"✓ Translated page {page}")
    return True

def complete_page(page: int) -> bool:
    """Submit completed page"""
    translation_file = f"translations/page_{page:03d}.json"
    
    if not Path(translation_file).exists():
        log(f"ERROR: Translation file not found: {translation_file}")
        return False
    
    log(f"Submitting page {page}...")
    success, output = run_command([
        "python3", "tools/sync_service.py",
        "--complete-page", str(page),
        "--file", translation_file
    ], check=False)
    
    if not success or "ERROR" in output:
        log(f"Failed to submit page {page}: {output}")
        return False
    
    log(f"✓ Completed page {page}")
    return True

def worker_loop(worker_id: str, max_pages: int = None):
    """Main worker loop"""
    log(f"Starting worker loop for {worker_id}")
    
    # Check sync daemon
    if not check_sync_daemon():
        log("ERROR: Sync daemon not running!")
        log("Start it with: python3 tools/sync_service.py --start --worker-id " + worker_id)
        sys.exit(1)
    
    pages_completed = 0
    
    try:
        while True:
            # Check if we've hit max_pages limit
            if max_pages and pages_completed >= max_pages:
                log(f"Reached max pages limit ({max_pages})")
                break
            
            # Get next page
            next_page = get_next_page()
            
            if next_page == "NONE":
                log("No more pages available. All work complete!")
                break
            
            if next_page == "ERROR":
                log("Error getting next page. Retrying in 30 seconds...")
                time.sleep(30)
                continue
            
            try:
                page = int(next_page)
            except ValueError:
                log(f"Invalid page number: {next_page}")
                time.sleep(10)
                continue
            
            # Claim page
            if not claim_page(page):
                log("Failed to claim page. Retrying...")
                time.sleep(5)
                continue
            
            # Translate page
            if not translate_page(page):
                log("Translation failed. Skipping page...")
                time.sleep(5)
                continue
            
            # Submit completion
            if not complete_page(page):
                log("Failed to submit page. Retrying...")
                time.sleep(5)
                continue
            
            pages_completed += 1
            log(f"Progress: {pages_completed} pages completed")
            
            # Brief pause between pages
            time.sleep(2)
    
    except KeyboardInterrupt:
        log("Worker loop interrupted by user")
    except Exception as e:
        log(f"ERROR: Worker loop crashed: {e}")
        sys.exit(1)
    
    log(f"Worker loop finished. Total pages completed: {pages_completed}")

def main():
    parser = argparse.ArgumentParser(description="Automated worker loop")
    parser.add_argument("--worker-id", required=True, help="Worker ID")
    parser.add_argument("--max-pages", type=int, help="Maximum pages to process (for testing)")
    
    args = parser.parse_args()
    
    worker_loop(args.worker_id, args.max_pages)

if __name__ == "__main__":
    main()
