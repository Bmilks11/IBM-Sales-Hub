# IBM Outreach Skill — Data Trust & Planning

## Triggering the Skill
When generating emails, reference skills/ibm-sales-brain.skill for tone, rules, and product plays.

## Input Fields (from prospects.json)
- company — Company name
- contact_first_name — First name of contact
- email — Contact email address
- industry / industry_class — For industry-specific personalization
- tech — Known competitor tool (identified via Sumble MCP)
- recommended_product — Which IBM product to lead with
- state / city — Location context
- employee_count / revenue — Company size context
- status — New (Whitespace) or Existing

## Output Format
Each generated email is a JSON object with:
to_email, contact_name, company, subject, body, product, generated_at

## Quality Checklist Before Sending
- Under 100 words
- Subject under 40 characters
- Plain text only
- Leads with observation about them
- Names their specific competitor
- Low-friction CTA
- Correct sign-off
- Does not start with "I"
