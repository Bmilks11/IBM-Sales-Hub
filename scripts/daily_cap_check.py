#!/usr/bin/env python3
"""
Check daily send cap. Exit code 1 if at or over cap.
Usage: python3 scripts/daily_cap_check.py [--verbose]
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

CAP = 200
LOG_FILE = Path(__file__).parent.parent / "data" / "send_log.json"

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not LOG_FILE.exists():
        if args.verbose:
            print(f"No log found. 0/{CAP} sent today.")
        sys.exit(0)

    log = json.loads(LOG_FILE.read_text())

    if log.get("date") != today_str():
        if args.verbose:
            print(f"New day. 0/{CAP} sent today.")
        sys.exit(0)

    count = log.get("count", 0)
    remaining = CAP - count

    if args.verbose:
        print(f"Daily cap: {count}/{CAP} sent | {remaining} remaining")

    if count >= CAP:
        if args.verbose:
            print("CAPPED: At daily limit. Stop all outreach.")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
