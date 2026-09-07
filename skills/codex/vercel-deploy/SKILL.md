---
name: vercel-deploy
description: Deploy websites and web apps to Vercel. Use when a user asks to deploy, publish, put a project live, make a Vercel site public, disable Vercel SSO protection, assign a clean `vercel.app` alias, or verify a production deployment URL.
---

# Vercel Deploy

## Overview

Deploy to production quickly and leave the site in a shareable state: linked project, public access, memorable alias, and verified live URL.

## Quick Workflow

1. Check Vercel CLI and auth first with `which vercel`, `vercel whoami`, and `vercel teams ls`.
2. If the repo is not linked, prefer creating or linking the project with the intended alias name first.
3. Deploy production with `vercel --prod --yes`.
4. Disable SSO protection after first deploy of a new project so the site is actually public.
5. Set or confirm a short memorable alias.
6. Verify the final URL with `curl -I` and report the public links back to the user.

## Linking

- Prefer your default team scope unless the repo is already linked to a different one, or the user asks for another team.
- If `.vercel/project.json` is missing and the user wants a specific hostname, create the project with that name first:

```bash
vercel project add <project-name> --scope <your-vercel-team>
vercel link --yes --project <project-name> --scope <your-vercel-team>
```

- If the repo is already linked, do not relink unless there is a concrete reason.

## Deploy

- Use the fastest production path:

```bash
vercel --prod --yes --scope <your-vercel-team>
```

- Capture both the deployment URL and the final promoted production URL.
- For simple static HTML/CSS/JS projects, assume no build customization is needed unless the repo says otherwise.

## Public Access

- Vercel team SSO can block public sharing on new projects. Run this idempotent patch after the project is linked:

```bash
TOKEN=$(python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])") && \
PROJECT_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['projectId'])") && \
TEAM_ID=$(python3 -c "import json; print(json.load(open('.vercel/project.json'))['orgId'])") && \
curl -s -X PATCH "https://api.vercel.com/v9/projects/$PROJECT_ID?teamId=$TEAM_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ssoProtection":null}'
```

- Confirm the project still responds with `HTTP 200` after the patch.

## Alias Strategy

- If the user gives a target alias, try that exact `*.vercel.app` name first.
- Prefer short memorable names that match the project name, because Vercel often auto-promotes `<project-name>.vercel.app` on production.
- If the alias is taken, try 2-3 close fallbacks instead of stopping immediately.
- Manual alias command:

```bash
vercel alias set <deployment-url> <alias>.vercel.app
```

## Verification

- Verify the main URL with `curl -I`.
- Verify any important secondary routes the user cares about.
- If the deployment is static-only, say so explicitly.
- If the app depends on local files, local servers, or writable disk state, call out that those behaviors will not persist on Vercel without an external backend.

## Output

Report back with:

- Final public URL
- Any important secondary URL
- Whether SSO protection was disabled
- Whether the alias was claimed or a fallback was needed
- Any deployment caveat that affects real use
