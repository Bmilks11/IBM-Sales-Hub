# IBM Data Trust & Planning — Autonomous Prospecting System

This is Bradley Milks's autonomous sales prospecting system. Bradley is an Account Executive at IBM (bradley.milks@ibm.com) on the Data Trust & Planning team, selling to prospects in Florida.

## HARD RULE: No Gmail Drafts

**NEVER call `gmail_create_draft` or any Gmail MCP tool to create email drafts.** All outreach emails are sent exclusively through Apple Mail.app via `send_via_mail.py`. Gmail is used only for scanning replies/bounces, never for sending or drafting. This applies to ALL tiers, ALL accounts, ALL contexts. There are zero exceptions.

## HARD RULE: Never Mention Pricing

**NEVER reference pricing, cost, ROI figures, savings percentages, or any commercial terms in outreach emails.** The goal of outreach is to book a meeting — not to sell on price. Pricing conversations happen in discovery calls, not cold emails. This applies to ALL emails, ALL tiers, ALL products. There are zero exceptions.

## When Bradley Opens a Fresh Session and Says "Run Today's Outreach"

Execute this sequence automatically, no clarifying questions needed:

1. Run:  python3 scripts/daily_cap_check.py --verbose
   - If already at 200/200, stop and report summary
   - If under cap, continue

2. Run:  python3 scripts/daily_orchestrator.py
   - Builds today's queue (follow-ups first, then new outreach)
   - Generates email prompts

3. Check if queue is empty or small:
   - If follow-ups + ready < (200 - already_sent_today), enrich more Tier 2 accounts
   - See Enrichment Workflow below

4. Generate personalized emails using the IBM Sales Brain skill
   - Follow EMAIL RULES strictly
   - Write batch to data/tier2_batch_<date>.json
   - Tier 1 accounts are NEVER drafted or queued

5. Send via:
   python3 scripts/send_via_mail.py --batch data/tier2_batch_<date>.json

6. Stop when cumulative sends = 200 for the day

7. Report final status to Bradley

## Critical Rules (non-negotiable)

### Daily 200 cap
- Hard stop at 200 per day
- Counter auto-resets at 00:00 UTC — no manual reset needed
- Enforced by scripts/daily_cap_check.py (exit code 1 when capped) and scripts/send_via_mail.py
- Before every enrichment batch, call daily_cap_check.py

### Territory and Account Targeting
- Bradley's territory is Florida
- Mix of net-new (New Whitespace) and existing customer expansion
- New (Whitespace) accounts: use displacement/consolidation plays only
- Existing accounts: use expansion plays — cross-sell additional IBM products
- Always confirm account is in Florida territory before queuing

### Email format (mobile + desktop)
- Plain text only. No HTML, bold, italic, or links in brackets.
- Subject line under 40 characters (fits mobile lock screen without truncation)
- 2-3 short paragraphs, blank line between each
- No sentence over 20 words. No bullets, dashes, or numbered lists.
- Under 100 words total
- Sign off with exactly:

Bradley Milks
Account Executive, Data Trust & Planning | IBM | Florida

- Lead with an observation about THEM, not about IBM
- Name their specific competitor tool if known (from account.tech field)
- Low-friction CTA: "10 min, no pitch" style
- Vary openers across every batch — never repeat the same first line
- Never start with "I" as the first word
- Never say "I hope this email finds you well"
- No buzzwords: leverage, synergy, solutions, best-in-class, cutting-edge
- NEVER mention pricing, cost savings, ROI, or any commercial figures

### Sending method
- All outreach goes through Apple Mail.app via send_via_mail.py (AppleScript). No exceptions.
- Mail.app must have bradley.milks@ibm.com configured as a sending account.
- Log all outreach in Salesforce after sending
- Gmail is read-only for replies and bounces only
- Never use Microsoft Outlook or any other mail client for automated sending

## Account Tiers

### Tier 1 — Strategic (Manual Only)
- High-value named accounts requiring personally crafted outreach
- NEVER auto-draft or auto-send Tier 1 emails
- Bradley writes these himself with Claude's assistance on request

### Tier 2 — New Whitespace (Automated Batch)
- Net-new prospects with no IBM relationship
- Status = "New (Whitespace)" in prospects.json
- These are the accounts in the automated daily batch
- Use displacement/consolidation plays

### Tier 3 — Existing (Expansion)
- Current IBM customers
- Status = "Existing (Continued)" or "Existing (PY-1 New Client)"
- Use expansion plays — cross-sell additional IBM products
- Handled separately from Tier 2 batch

## Products and Sales Plays

### Planning Analytics (TM1 / Cognos)
What it is: IBM's enterprise FP&A and planning platform.
Pain points: Manual Excel-based planning, slow close cycles, no scenario modeling, disconnected finance and operations data.
Displacement targets: Anaplan, OneStream, Workday Adaptive Insights, Oracle EPM, Vena.
Play: Modernize FP&A — faster planning cycles, real-time scenario modeling, eliminate spreadsheet sprawl.
Best fit: CFOs, VP Finance, FP&A Directors at mid-market to enterprise companies.

### watsonx.data
What it is: IBM's open lakehouse platform for unified data management across clouds.
Pain points: Data silos, fragmented cloud infrastructure, AI-readiness gaps, warehouse sprawl.
Displacement targets: Snowflake, Databricks, AWS Redshift, Google BigQuery.
Play: Unify data across clouds, reduce warehouse dependency, accelerate AI-ready data infrastructure.
Best fit: CDOs, Data Engineering leads, CTOs at data-intensive organizations.

### watsonx.data Integration
What it is: IBM's data integration and pipeline platform (DataStage / Cloud Pak for Data).
Pain points: Fragmented ETL pipelines, high MuleSoft/Informatica licensing costs, integration sprawl.
Displacement targets: MuleSoft, Informatica, Talend, Azure Data Factory, Boomi.
Play: Simplify data pipelines, reduce integration complexity, build AI-ready data flows faster.
Best fit: Data Engineering leads, IT Architecture, CTO offices.

### Guardium
What it is: IBM's data security and compliance platform (DSPM, database activity monitoring, access governance).
Pain points: Compliance gaps (SOC2, GDPR, HIPAA, PCI), audit failures, uncontrolled data access, shadow data sprawl.
Displacement targets: Varonis, Imperva, Microsoft Purview, Securiti.ai.
Play: Achieve audit readiness, govern data access at scale, automate compliance reporting.
Best fit: CISOs, Compliance Officers, Data Governance leads, VP IT.

## Enrichment Workflow

When the queue is thin, enrich more Tier 2 accounts:

1. Pull from ZoomInfo or Sales Nav using ICP filters:
   - Florida territory
   - 50 to 5000 employees
   - Titles: CFO, VP Finance, CISO, CDO, CTO, VP Engineering, Director of Data, Head of Analytics

2. Check tech stack via Sumble MCP to identify which competitor tool they are running

3. Add to data/prospects.json with tier: 2, status: "New (Whitespace)"

4. Run python3 scripts/daily_cap_check.py before adding to batch

## IBM Sales Brain Skill
Use skills/ibm-sales-brain.skill for generating all outreach emails.

## Data Files
- data/prospects.json — Master prospect list
- data/send_log.json — Daily send log (tracks 200/day cap, auto-created)
- data/today_queue.json — Today's outreach queue (auto-generated)
- data/tier2_batch_<date>.json — Generated email batch
- data/enrichment_log.json — Enrichment history

## Tools Stack
- ZoomInfo — Prospect sourcing and contact enrichment
- LinkedIn Sales Navigator — Account research, contact finding
- Sumble MCP — Tech stack intelligence (identify competitor tools)
- Salesforce — CRM (log all outreach activity)
- Apple Mail.app — Email sending via AppleScript (IBM account must be configured)
