---
name: image-gen
description: "Generate actual images from text, free, no paid API. Use whenever the user wants an image created — illustration, hero/header art, icon, texture, concept art, photo-style render, logo sketch, placeholder, or a picture to drop into a page or doc. Triggers on 'make an image', 'generate a picture of', 'create art', 'I need a graphic for', 'render', 'draw me', or any request that needs a visual rather than prompt text. Three backends: local ComfyUI (private, no limits), pollinations.ai (any size, needs internet), and Codex gpt-image-2 (best quality, uses ChatGPT Plus subscription limits — finals only). NOTE: for writing funny prompt TEXT (not images) use the image-prompts skill instead."
argument-hint: <description of the image to generate>
allowed-tools: [Bash, Read, Write]
---

# Image Generation

Generate real images from a text description — no paid API key. Two free helper scripts live in this skill's directory, plus a subscription-backed Codex backend for top quality; pick per the rules below. After generating, **always `open <path>`** (pops it up in Preview — the user wants to peek at every image) **and `Read` the file** so it's shown inline too.

Skill dir: `~/.claude/skills/image-gen/` — `comfy_gen.py` (local ComfyUI) and `pollinations_gen.py` (pollinations.ai).

## Pick a backend

Check ComfyUI first — it's local, private, unlimited, and free:

```bash
curl -s -m 3 -o /dev/null -w "%{http_code}" http://127.0.0.1:8188/system_stats
```

- **`200` → ComfyUI is up.** Prefer it for: privacy/offline, batches, square or portrait images (~512–768px native, SD1.5). ~25s per 512² image on this Mac (MPS). Use `comfy_gen.py`.
- **Not 200, OR the user wants a large/widescreen/modern-photoreal image → pollinations.** Handles arbitrary sizes (e.g. 1024×576 heroes) and needs no local setup. Requires internet. Use `pollinations_gen.py`. (Currently serves the **sana** model; the `--model` flag is ignored by their API right now — verify the live list with `curl -H "User-Agent: Mozilla/5.0" https://image.pollinations.ai/models`.)

When unsure, pollinations is the safer default for anything that has to look polished or non-square. ComfyUI wins when local/private/no-rate-limit matters.

- **Quality is the whole point (final hero art, logo, text-in-image, photoreal people) → Codex gpt-image-2.** Runs on the user's ChatGPT Plus subscription via the local Codex CLI — no API key, but each image turn burns Plus Codex usage 3–5× faster than a normal turn (~10–25 images per 5h window, shared with actual Codex coding use). Finals only; never for drafts, batches, or placeholders — iterate on the free backends first, then do one Codex pass.

## Generate

ComfyUI (local, square/portrait):
```bash
python3 ~/.claude/skills/image-gen/comfy_gen.py "PROMPT" \
  --out /tmp/<meaningful-name>.png --w 512 --h 512 --steps 25 --seed 42
# add --neg "things to avoid"; --ckpt to pick a checkpoint
```

Pollinations (any size, widescreen, photoreal):
```bash
python3 ~/.claude/skills/image-gen/pollinations_gen.py "PROMPT" \
  --out /tmp/<meaningful-name>.jpg --w 1600 --h 640 --seed 7
# serves the sana model (--model ignored). The helper auto-handles aspect:
# Sana renders 512² square and would STRETCH non-square / LETTERBOX large
# requests, so the helper renders a modest square then crops+upscales to your
# w×h — undistorted, full-bleed, any aspect. Pass --raw to bypass (may stretch).
```

Codex gpt-image-2 (subscription, best quality — finals only):
```bash
codex exec --skip-git-repo-check 'Use your image generation tool: PROMPT — style/detail notes. Save the image to /tmp/<meaningful-name>.png and output only that path. Do nothing else.' < /dev/null
```
**ALWAYS append `< /dev/null`.** Without it, `codex exec` blocks forever on "Reading additional input from stdin…" in non-interactive/agent shells (stdin never sends EOF) — this is the real cause of the so-called "hang," not OpenAI. With stdin closed it returns in seconds–minutes. The saved path is the last non-log line of stdout.
Sizes: 1024x1024, 1024x1536, 1536x1024 (model may render larger and downscale via sips — exact pixels not guaranteed). Raw outputs also land in `~/.codex/generated_images/<session>/`. One image ≈ 45K tokens of Plus usage; do NOT loop this in a batch.

**Text-in-image strength (Codex only):** gpt-image-2 renders **lots** of text accurately — it's the right backend for real infographics, charts, diagrams, slides, posters, and anything with labels/numbers. (The free backends — Sana/pollinations and SD1.5/ComfyUI — garble text; don't use them when words must be legible.) To get a true data infographic rather than generic "infographic-looking" art, **spell out every text string verbatim in quotes AND say where each goes** — header, a stat row of "NUMBER / LABEL" cards, named sections, per-bar chart labels ("Adam Detrick 399"), timeline rows, footer. Verified Jun 16 2026: a single image cleanly rendered ~30+ text elements across a multi-section portrait layout (header, 4 stat cards, a 6-item feature list, a 5-bar labeled chart, two big callouts, a 4-item list, a footer strip) with correct spelling. It handles 2:3 portrait well (rendered 864×1821). Still spot-check spelling at full size — it occasionally drops a character on dense small text; code-syntax strings with parens/symbols are the most fragile, so phrase labels as plain readable words where you can.

**Texture gotcha:** gpt-image-2 piles on crusty over-sharpened micro-texture ("overcooked" — the user's words) unless prompted away. Append something like "smooth painterly rendering, clean forms, soft atmospheric depth, no oversharpened texture, no HDR grit" to every gpt-image-2 prompt that isn't deliberately gritty.

**Concurrency gotcha:** never run two `codex exec` calls at once — concurrent execs wedge each other indefinitely (seen Jun 11 2026: parallel batch hung on every turn while a serial one proceeded). Strictly one at a time.

**Hang gotcha — ROOT CAUSE FOUND (Jun 16 2026):** the "wedges forever" failure is almost always `codex exec` **blocking on an open stdin** ("Reading additional input from stdin…"), NOT OpenAI's stream dying. In this agent harness stdin is an open pipe that never EOFs, so codex waits indefinitely. **Fix: always run with `< /dev/null`** (or `stdin=subprocess.DEVNULL` from Python). Verified Jun 16: a trivial text exec that "hung" past 150s with open stdin returned in **9s** with `< /dev/null`; the infographic image then generated cleanly in well under a minute. Still keep a watchdog (`subprocess.run(cmd, timeout=600, stdin=subprocess.DEVNULL)`) as a backstop for genuine stream death, but redirecting stdin is the actual cure. Don't `>/dev/null` the output — you need the path/errors.

> **Aspect-ratio gotcha (pollinations only):** never trust a raw non-square pollinations request — Sana stretches it. The helper fixes this for you; just pass the `--w`/`--h` you actually want. For HTML heroes you can also request a square and let CSS `object-fit:cover` shape it. ComfyUI honors exact dimensions natively (no stretch) but SD1.5 degrades past ~768px and on very wide frames.

The helper scripts print the saved path on success. A fixed `--seed` makes results reproducible; omit/vary it for variety (Codex has no seed control). **Name output files meaningfully** (subject, not `image1`), and after generating, **`open <path>`** (Preview popup — default, every image) then `Read` the file to display it inline.

## Writing the prompt

Be specific and visual: subject + setting + style + lighting + detail level. e.g. `"a red fox curled asleep in autumn leaves, golden hour, shallow depth of field, photorealistic, highly detailed"`. Name an art style when it matters (watercolor, flat vector, isometric 3D, oil painting, line art). For ComfyUI/SD1.5, the default negative prompt already filters common artifacts; add specifics (e.g. `--neg "extra fingers, text, signature"`) when needed.

If the user only wants creative *prompt ideas* as text (not a rendered image), that's the **image-prompts** skill, not this one.

## Failure handling

- ComfyUI submit fails / errors on server → fall back to pollinations.
- Pollinations 403 → the helper already sends a browser User-Agent; a persistent 403/empty body means rate-limited or down, so fall back to ComfyUI (if up) or tell the user.
- Pollinations **402 Payment Required** (first seen Jun 11, 2026 — generation 402s even though `/models` still answers) → their free anonymous access may be ending or temporarily gated. Fall back to ComfyUI; if this persists across days, treat pollinations as dead and consider replacing this backend.
- Don't silently retry more than the scripts already do; report which backend you used.
