#!/usr/bin/env python3
"""
Generate personalized IBM Planning Analytics outreach emails.
Planning Analytics is the primary product for all Tier 2 outreach.
Other products only used if account.recommended_product explicitly set.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent

SIGN_OFF = "Bradley Milks\nAccount Executive, Data Trust & Planning | IBM | Florida"

# Planning Analytics is PRIMARY — all other products are secondary
PRIMARY_PRODUCT = "Planning Analytics"

PRODUCT_PLAYS = {
    "Planning Analytics": {
        "competitors": ["Anaplan", "OneStream", "Workday Adaptive", "Oracle EPM", "Excel", "Vena"],
        "angles": [
            "manual planning cycles and spreadsheet-driven forecasting",
            "slow scenario modeling and close cycles",
            "finance teams spending more time building models than making decisions",
            "planning cycles that can't keep pace with business change"
        ],
        "play": "AI-powered planning — real-time scenarios, automated forecasting, generative AI for FP&A",
        "titles": ["CFO", "VP Finance", "FP&A Director", "Head of Planning", "Controller", "VP Strategy"]
    },
    "watsonx.data": {
        "competitors": ["Snowflake", "Databricks", "AWS Redshift"],
        "angles": ["fragmented data infrastructure and warehouse sprawl"],
        "play": "unified open lakehouse — reduce warehouse dependency, accelerate AI-ready data",
        "titles": ["CDO", "CTO", "VP Engineering", "Head of Data"]
    },
    "watsonx.data Integration": {
        "competitors": ["MuleSoft", "Informatica", "Talend", "Azure Data Factory"],
        "angles": ["fragmented pipelines and high integration complexity"],
        "play": "simplified data pipelines — reduce integration sprawl, build AI-ready data flows",
        "titles": ["CTO", "VP Engineering", "Head of Data Engineering"]
    },
    "Guardium": {
        "competitors": ["Varonis", "Imperva", "Microsoft Purview"],
        "angles": ["compliance gaps and uncontrolled data access"],
        "play": "data security and audit readiness — govern access, automate compliance reporting",
        "titles": ["CISO", "VP IT", "Compliance Officer", "Data Governance Lead"]
    }
}

OPENERS = [
    "Noticed {company} is running {competitor} for {angle}.",
    "Most {title}s I talk to in {industry} hit the same wall around {angle}.",
    "Saw {company} is growing the finance team — curious if {angle} has kept pace.",
    "Teams running {competitor} at {company}'s scale usually start asking about {angle}.",
    "Curious how {company} is handling {angle} as the business scales."
]

def generate_email(prospect, index=0):
    company = prospect.get("company", "")
    contact = prospect.get("contact_first_name", "")
    to_email = prospect.get("email", "")
    tech = prospect.get("tech", "")
    industry = prospect.get("industry", "your industry")

    # Planning Analytics is default unless explicitly overridden
    product = prospect.get("recommended_product", PRIMARY_PRODUCT)
    if product not in PRODUCT_PLAYS:
        product = PRIMARY_PRODUCT

    play = PRODUCT_PLAYS[product]
    competitor = tech if tech in play["competitors"] else play["competitors"][0]
    angle = play["angles"][index % len(play["angles"])]
    title = play["titles"][0]

    opener_template = OPENERS[index % len(OPENERS)]
    opener = opener_template.format(
        company=company,
        competitor=competitor,
        angle=angle,
        industry=industry,
        title=title
    )

    subject = f"Quick thought on {company}"[:39]

    body = (
        f"{opener}\n\n"
        f"Finance teams in {industry} I work with are moving toward {play['play']} — "
        f"usually changes how quickly they can respond to what the business is asking for.\n\n"
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
    batch = [generate_email(p, i) for i, p in enumerate(queue) if p.get("email")]

    out = BASE / args.output
    out.write_text(json.dumps(batch, indent=2))
    print(f"Generated {len(batch)} Planning Analytics emails -> {args.output}")

if __name__ == "__main__":
    main()
