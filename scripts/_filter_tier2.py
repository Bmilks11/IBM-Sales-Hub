#!/usr/bin/env python3
"""List Tier 2 accounts that still need contact enrichment."""

import json
from pathlib import Path

BASE = Path(__file__).parent.parent

def main():
    pf = BASE / "data" / "prospects.json"
    if not pf.exists():
        print("No prospects.json found.")
        return
    prospects = json.loads(pf.read_text())
    needs_enrich = [p for p in prospects if p.get("tier") == 2 and not p.get("email")]
    print(f"Tier 2 accounts needing enrichment: {len(needs_enrich)}")
    for p in needs_enrich[:20]:
        print(f"  - {p.get('company')} | {p.get('industry')} | {p.get('city')}, {p.get('state')}")

if __name__ == "__main__":
    main()
