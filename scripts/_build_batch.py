#!/usr/bin/env python3
"""Build a new outreach batch from enriched Tier 2 accounts."""

import json
import argparse
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    pf = BASE / "data" / "prospects.json"
    if not pf.exists():
        print("No prospects.json found.")
        return

    prospects = json.loads(pf.read_text())
    ready = [p for p in prospects if p.get("tier") == 2 and p.get("email") and not p.get("contacted")]
    batch = ready[:args.limit]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    out = BASE / f"data/tier2_batch_{today}.json"
    out.write_text(json.dumps(batch, indent=2))
    print(f"Batch of {len(batch)} written to {out.name}")

if __name__ == "__main__":
    main()
