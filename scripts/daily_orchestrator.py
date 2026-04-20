#!/usr/bin/env python3
"""
IBM Data Trust & Planning — Daily Outreach Orchestrator
Run when Bradley says "Run Today's Outreach"
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent

def run(cmd, check=False):
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode

def main():
    print("=== IBM Daily Outreach Orchestrator ===")
    print(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")

    print("Step 1: Checking daily cap...")
    rc = run("python3 scripts/daily_cap_check.py --verbose")
    if rc != 0:
        print("Already at 200/200. Done for today.")
        sys.exit(0)

    print("\nStep 2: Building today's queue...")
    run("python3 scripts/build_daily_queue.py")

    print("\nStep 3: Generating personalized emails...")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    batch_file = f"data/tier2_batch_{today}.json"
    run(f"python3 scripts/generate_emails.py --output {batch_file}")

    print(f"\nStep 4: Sending via Outlook...")
    run(f"python3 scripts/send_via_mail.py --batch {batch_file}")

    print("\nStep 5: Final status...")
    run("python3 scripts/daily_cap_check.py --verbose")

if __name__ == "__main__":
    main()
