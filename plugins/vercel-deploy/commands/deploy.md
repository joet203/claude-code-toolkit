---
description: Deploy the current project to Vercel and ensure it's publicly accessible (disables SSO protection). Use when the user says "deploy", "vercel deploy", "push to vercel", or "make it live".
allowed-tools: [Bash, Read]
---

# Vercel Deploy

Deploy the current project to Vercel production and ensure the site is publicly accessible.

## Steps

1. Deploy to Vercel production:
```bash
vercel --prod --yes
```
Capture the deployment URL from the output (the `https://...vercel.app` line).

2. Disable SSO protection so the site is public (Vercel team has SSO enabled by default which forces a login prompt). Run this as a single bash command:
```bash
TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])") && PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])") && TEAM_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['orgId'])") && curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=$TEAM_ID" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"ssoProtection":null}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('SSO protection disabled for:', d.get('name','unknown'))"
```

3. Set a clean, memorable alias using the deployment URL from step 1:
```bash
vercel alias <deployment-url> <alias>.vercel.app
```
Try 2-3 short alias options. If one is taken, try the next.

4. Report all live URLs to the user.

## Alias Guidelines

Always try to set a short, memorable alias. Vercel's auto-generated names are ugly (e.g. `nick-lake.vercel.app`). Try these in order:

- **Shortest recognizable name** — e.g. `mabeans`, `bizd`
- **Abbreviations or acronyms** — e.g. the project's initials
- **Domain-style names** — e.g. `mabirds`, `survivor-odds`
- If the first choice is taken, try 2-3 more before falling back

Good aliases are:
- Short (under 12 chars ideally)
- Easy to type and say out loud
- No random suffixes or numbers
- Related to the project content

Try multiple aliases — a project can have several pointing to the same deployment. Suggest 2-3 options and set all that work.

## Other Tips

- **Redeployments**: The SSO disable is idempotent — safe to run every time. Aliases persist across deploys if the project name hasn't changed.
- **No build step needed**: For vanilla HTML/CSS/JS projects, Vercel serves them directly — no framework config required.
- **Vercel auth token**: Lives at `~/Library/Application Support/com.vercel.cli/auth.json`.
- **Check existing aliases**: Run `vercel ls` to see current deployments and their URLs.
- **Existing projects**: check `vercel project ls` for what already exists on your team, to avoid name collisions.
