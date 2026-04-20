#!/usr/bin/env python3
"""
Build today's outreach queue.
Priority: follow-ups first, then new Tier 2 (New Whitespace) accounts.
"""

import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
PROSPECTS_FILE = BASE / "data" / "prospects.json"
LOG_FILE = BASE / "data" / "send_log.json"
QUEUE_FILE = BASE / "data" / "today_queue.json"

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def main():
    if not PROSPECTS_FILE.exists():
        print("ERROR: data/prospects.json not found.")
        return

    prospects = json.loads(PROSPECTS_FILE.read_text())

    send_log = {}
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())
        for entry in log.get("sent", []):
            send_log[entry.get("company", "")] = entry.get("sent_at", "")

    follow_ups = []
    new_outreach = []

    for p in prospects:
        tier = p.get("tier", 2)
        company = p.get("company", "")

        if tier == 1:
            continue

        last_sent = send_log.get(company, "")

        if last_sent:
            sent_date = datetime.fromisoformat(last_sent[:10])
            days_ago = (datetime.utcnow() - sent_date).days
            if 3 <= days_ago <= 7 and not p.get("replied"):
                follow_ups.append(p)
            continue

        if tier in (2, 3) and p.get("email") and not p.get("contacted"):
            new_outreach.append(p)

    queue = follow_ups + new_outreach
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))
    print(f"Queue: {len(follow_ups)} follow-ups + {len(new_outreach)} new = {len(queue)} total")

if __name__ == "__main__":
    main()
