#!/usr/bin/env python3
"""
Send emails via Microsoft Outlook on Mac using AppleScript.
Outlook must be open and signed into bradley.milks@ibm.com.
Hard cap of 200 sends/day enforced before and during sending.
"""

import json
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path

CAP = 200
LOG_FILE = Path(__file__).parent.parent / "data" / "send_log.json"
FROM_EMAIL = "bradley.milks@ibm.com"

def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {"date": "", "count": 0, "sent": []}

def save_log(log):
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.write_text(json.dumps(log, indent=2))

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def send_via_outlook(to_email, subject, body):
    """Send email via Microsoft Outlook using AppleScript."""
    body_esc = body.replace("\\", "\\\\").replace('"', '\\"')
    subject_esc = subject.replace('"', '\\"')
    script = f'''
    tell application "Microsoft Outlook"
        set newMsg to make new outgoing message with properties {{subject:"{subject_esc}", plain text content:"{body_esc}"}}
        tell newMsg
            set sender to "{FROM_EMAIL}"
            make new recipient with properties {{email address:{{address:"{to_email}"}}}}
        end tell
        send newMsg
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    batch_file = Path(args.batch)
    if not batch_file.exists():
        print(f"ERROR: Batch file not found: {batch_file}")
        sys.exit(1)

    emails = json.loads(batch_file.read_text())
    log = load_log()

    if log["date"] != today_str():
        log = {"date": today_str(), "count": 0, "sent": []}

    remaining = CAP - log["count"]
    if remaining <= 0:
        print(f"CAPPED: Already at {CAP}/day. No sends.")
        sys.exit(1)

    sent_count = 0
    for email in emails:
        if sent_count >= remaining:
            print(f"CAPPED mid-batch at {CAP}/day.")
            break

        to = email.get("to_email")
        subject = email.get("subject")
        body = email.get("body")
        company = email.get("company", "")

        if not all([to, subject, body]):
            print(f"SKIP: Missing fields for {company}")
            continue

        if args.dry_run:
            print(f"DRY RUN — To: {to} | Subject: {subject}\n{body}\n---")
            sent_count += 1
            continue

        try:
            send_via_outlook(to, subject, body)
            log["count"] += 1
            log["sent"].append({
                "to": to,
                "company": company,
                "subject": subject,
                "sent_at": datetime.utcnow().isoformat()
            })
            save_log(log)
            sent_count += 1
            print(f"SENT ({log['count']}/{CAP}): {to} — {company}")
        except Exception as e:
            print(f"ERROR sending to {to}: {e}")

    print(f"\nDone. Sent {sent_count} this run. Total today: {log['count']}/{CAP}")

if __name__ == "__main__":
    main()
