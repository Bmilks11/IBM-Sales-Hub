#!/usr/bin/env python3
"""
Generate personalized IBM outreach emails using the IBM Sales Brain.
Reads today_queue.json, writes batch JSON for send_via_mail.py.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent

SIGN_OFF = "Bradley Milks\nAccount Executive, Data Trust & Planning | IBM | Florida"

PRODUCT_PLAYS = {
    "Planning Analytics": {
        "competitors": ["Anaplan", "OneStream", "Workday Adaptive", "Oracle EPM"],
        "pain": "manual planning cycles and spreadsheet sprawl",
        "play": "faster FP&A cycles and real-time scenario modeling"
    },
    "watsonx.data": {
        "competitors": ["Snowflake", "Databricks", "AWS Redshift"],
        "pain": "rising data warehouse costs and siloed data",
        "play": "cutting cloud data costs while unifying data across environments"
    },
    "watsonx.data Integration": {
        "competitors": ["MuleSoft", "Informatica", "Talend", "Azure Data Factory"],
        "pain": "fragmented pipelines and high integration licensing costs",
        "play": "simplifying data pipelines and reducing integration spend"
    },
    "Guardium": {
        "competitors": ["Varonis", "Imperva", "Microsoft Purview"],
        "pain": "compliance gaps and uncontrolled data access",
        "play": "achieving audit readiness and governing data access at scale"
    }
}

def generate_email(prospect):
    company = prospect.get("company", "")
    contact = prospect.get("contact_first_name", "")
    to_email = prospect.get("email", "")
    tech = prospect.get("tech", "")
    industry = prospect.get("industry", "your industry")
    product = prospect.get("recommended_product", "Planning Analytics")
    play = PRODUCT_PLAYS.get(product, PRODUCT_PLAYS["Planning Analytics"])
    competitor = tech if tech in play["competitors"] else play["competitors"][0]

    subject = f"Quick thought on {company}"[:39]

    body = (
        f"Noticed {company} is running {competitor} for {play['pain'].split(' and ')[0]}.\n\n"
        f"Teams I work with in {industry} are moving toward {play['play']} — "
        f"usually cuts time and cost faster than most expect.\n\n"
        f"Worth 10 minutes to see if it maps to what you're working through?\n\n"
        f"{SIGN_OFF}"
    )

    return {
        "to_email": to_email,
        "contact_name": contact,
        "company": company,
        "subject": subject,
        "body": body,
        "product": product,
        "generated_at": datetime.utcnow().isoformat()
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=f"data/tier2_batch_{datetime.utcnow().strftime('%Y-%m-%d')}.json")
    args = parser.parse_args()

    queue_file = BASE / "data" / "today_queue.json"
    if not queue_file.exists():
        print("ERROR: today_queue.json not found. Run build_daily_queue.py first.")
        return

    queue = json.loads(queue_file.read_text())
    batch = [generate_email(p) for p in queue if p.get("email")]

    out = BASE / args.output
    out.write_text(json.dumps(batch, indent=2))
    print(f"Generated {len(batch)} emails -> {args.output}")

if __name__ == "__main__":
    main()
