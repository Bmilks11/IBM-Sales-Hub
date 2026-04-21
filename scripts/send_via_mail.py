#!/usr/bin/env python3
"""
Send emails via SMTP (Microsoft 365 / IBM Exchange Online).
Credentials loaded from .env file in repo root.
Hard cap of 200 sends/day enforced before and during sending.

Setup:
  Copy .env.example to .env and fill in:
    SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

  IBM users: if standard password fails, generate an App Password at
  myaccount.microsoft.com -> Security -> App passwords
"""

import json
import smtplib
import ssl
import sys
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
CAP = 200
LOG_FILE = BASE / "data" / "send_log.json"
ENV_FILE = BASE / ".env"

FROM_EMAIL = "bradley.milks@ibm.com"
FROM_NAME = "Bradley Milks"

# Default IBM/M365 SMTP settings — override in .env
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587

def load_env():
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            import os
            os.environ.setdefault(key.strip(), val.strip())

def get_smtp_creds():
    import os
    server = os.environ.get("SMTP_SERVER", SMTP_SERVER)
    port = int(os.environ.get("SMTP_PORT", SMTP_PORT))
    user = os.environ.get("SMTP_USER", FROM_EMAIL)
    password = os.environ.get("SMTP_PASSWORD", "")
    if not password:
        print("ERROR: SMTP_PASSWORD not set. Add it to your .env file.")
        sys.exit(1)
    return server, port, user, password

def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text())
    return {"date": "", "count": 0, "sent": []}

def save_log(log):
    LOG_FILE.parent.mkdir(exist_ok=True)
    LOG_FILE.write_text(json.dumps(log, indent=2))

def today_str():
    return datetime.utcnow().strftime("%Y-%m-%d")

def send_email(smtp, to_email, subject, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))
    smtp.sendmail(FROM_EMAIL, to_email, msg.as_string())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env()

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

    if args.dry_run:
        for email in emails[:remaining]:
            print(f"DRY RUN — To: {email.get('to_email')} | Subject: {email.get('subject')}")
            print(f"{email.get('body')}\n---")
        return

    server, port, user, password = get_smtp_creds()
    print(f"Connecting to {server}:{port}...")

    context = ssl.create_default_context()
    sent_count = 0

    try:
        with smtplib.SMTP(server, port, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.login(user, password)
            print("Connected.\n")

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

                try:
                    send_email(smtp, to, subject, body)
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

    except smtplib.SMTPAuthenticationError:
        print("AUTH FAILED: Check SMTP_USER and SMTP_PASSWORD in .env")
        print("IBM tip: generate an App Password at myaccount.microsoft.com -> Security -> App passwords")
        sys.exit(1)
    except Exception as e:
        print(f"SMTP connection error: {e}")
        sys.exit(1)

    print(f"\nDone. Sent {sent_count} this run. Total today: {log['count']}/{CAP}")

if __name__ == "__main__":
    main()
