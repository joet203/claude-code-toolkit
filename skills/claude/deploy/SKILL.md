---
name: deploy
description: Use when deploying a site to Vercel. Runs the deploy, verifies the live URL actually serves new content (not cached), checks/disables SSO protection for public sites, and scans for duplicate HTML files that may need the same edits. Prevents the recurring friction of trusting "Deployment succeeded" messages that hide cache, auth-protection, or duplicate-file issues.
---

# Deploy Skill

Pre-deploy checklist and post-deploy verification for Vercel sites. Built because "Deployment succeeded" messages repeatedly hide real problems (stale cache, SSO enabled by default, duplicate HTML files out of sync).

## When to Use

Invoke this skill whenever the user says "deploy", "ship it", "push to prod", or runs `vercel --prod` manually. Also use it after any significant edit to a deployed site.

## Steps

### 1. Pre-deploy scan — duplicate file check

Before deploying, scan the repo for HTML files that might need the same edit:

```bash
# Find HTML files in the project
find . -maxdepth 3 -name "*.html" -not -path "*/node_modules/*" -not -path "*/.vercel/*"
```

If multiple HTML files exist (e.g. `index.html`, `recipe.html`, `about.html`), ask the user whether the edit should apply to all of them. Common trap: recipe pages duplicated across files.

### 2. Run the deploy

```bash
vercel --prod
```

Capture the deployment URL from the output.

### 3. Post-deploy verification — content check

Wait ~5 seconds for propagation, then curl the URL and verify the NEW content is actually served. Do NOT just check HTTP 200 — grep for a string that you know was just added/changed:

```bash
sleep 5 && curl -sL "<DEPLOYED_URL>" | grep -c "<NEW_CONTENT_STRING>"
```

If the count is 0, the deploy is serving stale content. Common causes: Vercel cache, wrong project, edge caching. Bust it with a force redeploy or check the project config.

### 4. Check SSO / Deployment Protection

For public sites, SSO/password protection must be OFF. Check with:

```bash
# HEAD request should return 200, not 401
curl -sI "<DEPLOYED_URL>" | head -5
```

If you see `401` or `x-vercel-protection` headers, disable protection via API:

```bash
TOKEN=$(cat ~/Library/Application\ Support/com.vercel.cli/auth.json | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
PROJECT_ID="<project-id-from-vercel-dashboard>"
curl -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"passwordProtection":null,"ssoProtection":null}'
```

### 5. Report

Report back to the user with:
- Deployed URL
- Whether new content was verified on the live site (pass/fail + the grep result)
- Whether SSO/protection is disabled (pass/fail)
- Any duplicate HTML files that were found (so the user can confirm they were all updated)

## Failure modes to watch for

- **Stale cache**: URL returns 200 but content is old. Fix: redeploy with `--force` or investigate caching headers.
- **SSO enabled on new projects**: Vercel enables protection by default for new projects on some plans. Always check on first deploy.
- **Duplicate HTML files**: If user edited `index.html` but `recipe.html` has the same content, both need updating.
- **Wrong project**: `vercel --prod` deploys from current dir — confirm you're in the right repo.

## Example

User: "deploy the travel site"

1. Scan: found `index.html` and `arrival.html` — ask user if edits apply to both.
2. Run `vercel --prod` → got `https://bos2aus.vercel.app`.
3. Curl and grep for the new "Customs tips" section → found 1 match. Pass.
4. HEAD request returns 200, no protection headers. Pass.
5. Report: "Deployed to https://bos2aus.vercel.app. New content verified live. SSO disabled. Note: arrival.html has similar content — confirm it was updated too."
