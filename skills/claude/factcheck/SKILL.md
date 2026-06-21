---
name: factcheck
description: Use before writing factual claims (businesses, restaurants, prices, hours, quotes, citations, laws, bill numbers, dates) into deployed content — travel sites, advocacy pages, recipe guides, emails. Verifies every factual claim via WebSearch/WebFetch and flags unverified ones as "unverified" rather than guessing. Built because fabricated details (invented restaurants, wrong business hours, made-up quotes) have been the #1 source of rework across sessions.
---

# Factcheck Skill

Hard rule: before any factual claim about a real-world entity lands in user-facing content, it must be verified or marked unverified. Never fabricate plausible-sounding details to fill gaps.

## When to Use

Invoke BEFORE writing to any of:
- Travel sites (restaurants, hotels, business hours, prices)
- Advocacy pages (bill numbers, committee members, vote records, legal claims)
- Recipe/guide pages (ingredient prices, product specs, game facts like TotK/PO-33)
- Emails with factual claims (prices, dates, quotes from real people)
- Diary/log entries that reference external events

Also use this when the user says: "fact check this", "verify", "is this right?", "audit the page".

## Steps

### 1. Extract claims

Scan the proposed content and list every factual claim. A claim is anything that could be wrong:
- Named entities (restaurants, businesses, people, products)
- Numbers (prices, hours, distances, dates, bill numbers)
- Quotes attributed to real people
- Status claims ("closed", "open", "pending", "passed")
- Citations (academic, legal, news)

### 2. Verify each claim

For each claim, run a verification:

```
WebSearch("<claim as a factual query>")
```

Or for a specific known URL (e.g. a bill tracker page, a restaurant's own website):

```
WebFetch("<url>", "Does this page confirm <claim>?")
```

Mark each claim as:
- **CONFIRMED**: source clearly supports the claim
- **CONTRADICTED**: source says something different → must be fixed before writing
- **UNVERIFIED**: couldn't find an authoritative source → must be omitted or hedged

### 3. Rewrite

For each claim:
- **CONFIRMED**: keep as-is, optionally cite the source in a comment if it's high-stakes.
- **CONTRADICTED**: replace with the correct fact from the source.
- **UNVERIFIED**: either (a) omit entirely, (b) hedge ("reportedly", "as of last known update"), or (c) ask the user to confirm before writing.

NEVER invent a substitute to make the content feel complete. Empty is better than wrong.

### 4. Report

Tell the user:
- How many claims were checked
- How many were confirmed / contradicted / unverified
- What was changed as a result
- Which claims the user needs to confirm manually (if any)

## Common fabrication traps

Patterns that have produced made-up content in past sessions:
- **Restaurant recommendations**: Invented "Bodega Underground" for a travel site. Always check restaurant names against Google Maps or the business's own site.
- **Business hours / closure status**: Claimed businesses were closed without checking. Always fetch the business's current site or a recent review.
- **Game/product facts**: Got TotK and PO-33 details wrong from memory. Always search official sources or wikis.
- **Diary embellishment**: Added emotional/narrative details the user didn't provide. Only write what the user actually said.
- **Date swaps**: Got Apr 4/5 trip dates reversed. Double-check dates against the source (email, message, calendar).
- **Legal/bill claims**: Claimed bills had certain statuses without checking malegislature.gov. Always fetch the bill's own page.

## Example

User: "write a Boston restaurant section for the travel site with 3 good dinner spots near Back Bay"

WRONG approach: list 3 restaurants from memory.

RIGHT approach:
1. WebSearch("best dinner restaurants Back Bay Boston 2026")
2. For each candidate, WebFetch the restaurant's site to confirm it exists, is open, and is near Back Bay.
3. Write only the confirmed ones. If only 2 verified, write 2 — don't pad to 3 with a guess.
4. Report: "Verified 2 of 3 candidates. Dropped one that couldn't be confirmed as currently operating."
