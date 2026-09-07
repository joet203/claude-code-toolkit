---
name: visualize
description: "Generate a rich, styled HTML page to visualize information instead of dumping text in the terminal. Use this whenever the response would be long, dense, or benefit from visual hierarchy — research results, comparisons, decision matrices, project status, learning guides, code explanations, API docs, recipe breakdowns, or any multi-section answer. If the user asks to 'visualize', 'show me', 'break down', 'compare', or the answer would exceed ~30 lines of terminal output, this skill makes it dramatically easier to read."
argument-hint: <topic or question>
allowed-tools: [Bash, Read, Write, Glob, Grep, WebSearch, WebFetch]
---

# Visualize

Generate a single-file HTML page that presents information in a rich, readable, visually striking format — then open it in the browser. Terminal text is for quick answers. For anything dense, structured, or worth studying, HTML wins by a mile.

## When to use this

Any time the answer would be a wall of text:
- "Compare X vs Y vs Z"
- "Explain how this system works"
- "What's the status of the project"
- "Research topic X and summarize"
- "Break down this recipe/API/architecture"
- "Show me everything about..."

## Task

The user wants to visualize: $ARGUMENTS

## Instructions

### 1. Gather the information

Research, read files, search — whatever is needed to build a complete answer. Do the work you'd normally do, but hold the output for the HTML page.

### 2. Choose a design direction

Every page should feel intentionally designed, not templated. Before writing HTML, decide:

- **Aesthetic tone** for this specific content — editorial magazine? technical dashboard? study guide? decision brief? Pick one and commit. The content should drive the design, not the other way around.
- **Font pairing** — choose a distinctive display font + a clean body font from Google Fonts. NEVER reuse the same pairing across pages. Avoid overused choices (Inter, Roboto, Space Grotesk, system fonts). Look for characterful serifs (Fraunces, Playfair Display, Libre Baskerville, Lora), geometric sans (Outfit, Syne, General Sans), humanist faces (Source Serif 4, Literata), or monospaced display (JetBrains Mono, IBM Plex Mono). Mix unexpected pairings.
- **Color palette** — start from a dark base (#0a0a1a to #1a1a2e range) but build a unique accent palette for each page. Use 1 dominant accent + 2-3 supporting colors. Bright accents against dark backgrounds. Don't default to the same gold/blue/pink every time — try emerald + coral, electric blue + warm amber, mint + magenta, etc.
- **Images?** — decide whether generated imagery would genuinely strengthen the page (a hero/header image, section illustrations, atmospheric background, concept art). For data-heavy or reference pages, often no — type and color carry it. For editorial, narrative, travel, story, or mood-driven pages, a well-placed image lifts it a lot. If yes, see the optional image step below.
- **Taste** — when generating imagery, art-direct to a taste profile you keep as a notes file, so the look stays consistent across pages instead of drifting per request. Record the direction it should follow (for example: cinematic or photoreal, painterly concept art, retro-analog film grain; not flat vector) and append a dated note to that file whenever the user reacts strongly to a page or an image.

### 2b. (Optional) Generate images

Only when images would clearly help (per the decision above). Use the **image-gen** skill's backends to create images locally — never hotlink or invent image URLs:

```bash
# widescreen hero (pollinations — any size, needs internet)
python3 ~/.claude/skills/image-gen/pollinations_gen.py "PROMPT matching the page's tone" \
  --out /tmp/visualize-hero-$(date +%s).jpg --w 1600 --h 600
# or local/private (ComfyUI, if http://127.0.0.1:8188 is up) — square/portrait
python3 ~/.claude/skills/image-gen/comfy_gen.py "PROMPT" --out /tmp/visualize-img-$(date +%s).png
```

For a page where the hero image IS the centerpiece (showpiece/editorial pages the user will keep or share), one Codex gpt-image-2 pass beats the free backends on quality — but it burns ChatGPT Plus Codex limits 3–5×/turn, so at most one per page, never for section fillers:

```bash
codex exec --skip-git-repo-check 'Use your image generation tool: PROMPT. Save to /tmp/visualize-hero-$(date +%s).png, output only the path. Do nothing else.'
```

Match the image style to the chosen aesthetic tone. Embed them in the HTML — either reference the local file path directly in `<img src>`, or for a fully portable single file, base64-inline it (`data:image/jpeg;base64,...` via `base64 -i FILE`). **Always display embedded images with `object-fit:cover`** on a sized container — that crops to fill, so nothing ever looks stretched even if the source aspect differs. Keep images tasteful and few; they support the content, they don't replace the typography/layout work. Skip entirely if internet and ComfyUI are both unavailable.

(The pollinations helper already handles aspect ratios correctly — it won't stretch — so just pass the `--w`/`--h` you want. See the image-gen skill's aspect-ratio note for why.)

### 3. Generate the HTML page

Write a single HTML file to `/tmp/visualize-$(date +%s).html`.

**Typography — the most important thing:**
- Base font size: `18-20px`. This is for reading, not squinting.
- Line-height: `1.7-1.9` for body text. Generous.
- Section headings: `clamp(1.8rem, 3.5vw, 2.8rem)` — big, bold, unmissable
- Sub-headings: `clamp(1.2rem, 2vw, 1.5rem)`
- Weight variation matters: 300 for body, 500 for emphasis, 700-800 for headings. Use the full weight range.
- Letter-spacing on uppercase labels: `0.08-0.15em`
- Measure (line length): max `70ch` for body text blocks. Wider for tables/grids.

**Layout — use the full screen:**
- Full viewport width — no cramped max-width containers
- For 3+ sections: sticky sidebar nav (220-250px) with clickable TOC on desktop, collapses to top bar on mobile
- Use CSS grid for side-by-side content — 2 or 3 columns where it makes sense
- Asymmetric layouts are more interesting than centered everything
- Generous padding: `2-4vw` on main content, `1.2-1.5em` inside cards
- Clear visual separation between sections — different subtle background shades, not just borders

**Visual density — information-rich but scannable:**
- Tables for any structured/comparative data. Alternating row backgrounds. Sticky header on long tables.
- Color-coded badges/pills for categories, status, types — small rounded elements with translucent backgrounds
- Highlighted key terms inline with colored `<mark>` or `<span>` — numbers in one color, warnings in another, recommendations in a third
- `<details><summary>` for deep dives, long lists, code blocks, supplementary info — collapsed by default so the page scans fast but everything is accessible
- Checkboxes with localStorage persistence where checklists/todo tracking makes sense
- Progress bars or visual indicators for status/completion data

**Atmosphere — make it feel designed:**
- Subtle grain/noise texture overlay (SVG filter, opacity 0.02-0.04)
- Gradient meshes or subtle radial gradients on hero/header areas
- Cards with slight border + hover state (translateY, glow, border-color change)
- Staggered fade-in animations on load (animation-delay per section, 0.1-0.15s increments)
- Smooth scroll behavior
- Consider: thin accent borders on section edges, decorative dividers, subtle box-shadows with colored tints

**Code & technical content:**
- Dark code blocks (#0d1117 or darker) with monospace font
- Copy button (top-right, small, unobtrusive)
- Syntax color hints where possible (strings in green-ish, keywords in purple-ish, comments dimmed)

**Core principles — dense, readable, varied:**
- Every section should have a distinct background color — not all the same card color. Alternate between 3-4 subtle dark shades so your eye knows when a section changes.
- Use color aggressively on text — key terms, numbers, warnings, tips should all be different colors inline. A paragraph with no color is a missed opportunity.
- Font size should be LARGE (18-20px body) but the layout should be COMPACT — tight padding, dense grids, minimal wasted space. Big text in a tight layout reads fast.
- Vary font weight constantly — 300 body, 500 inline emphasis, 600 labels, 700 subheadings, 800 headings. Weight variation creates hierarchy without needing more space.
- Every piece of information should have the right container — tables for comparisons, cards for categories, callouts for advice, badges for status, checklists for actions. Don't default to bullet lists.
- Expand/collapse everything that isn't essential on first scan. The page should look clean at first glance but have depth when you click in.

**Recommended patterns — reach for these:**

- **Callout boxes** — do/don't/tip blocks with colored left border and tinted background, placed side by side in a 2-col grid. Green-ish for "do", red-ish for "don't", amber-ish for tips. Far more scannable than inline advice.
- **Big number cards** — large stat/metric in a centered card (font-size 2.5-3rem, font-weight 800) with a small uppercase label below. Use for key numbers that anchor a section.
- **Do vs Don't columns** — side by side grid comparing good and bad approaches. Instant visual contrast.
- **Before/After or Weak/Strong tables** — concrete examples showing the difference, not abstract rules. People learn from specifics.
- **Numbered section headings** — prefix h2 with "01", "02" etc. Gives a sense of progress and structure through the page.
- **Frequency/status badges inside tables** — color-coded pills in table cells ("very common", "moderate", "critical"). Makes tables scannable without reading every cell.
- **Persistent checklist** — `<input type="checkbox">` with localStorage. Use at the end for actionable items, prep lists, todo tracking.
- **Arrow bullets** — use "→" instead of "•" in card lists for a more directional, action-oriented feel.
- **Accent underlines on headings** — thin colored `::before` bar under h2 border, alternating colors per section. Adds visual rhythm.
- **Radial gradient glow** — subtle `radial-gradient` with accent color at 0.05-0.08 opacity on hero/header areas. Creates atmosphere without being distracting.
- **Hover states on cards** — `translateY(-3px)` + border-color change + subtle box-shadow with accent color tint. Makes the page feel interactive.

**The page must:**
- Be a single self-contained HTML file (inline CSS/JS, no external deps except Google Fonts)
- Work on desktop and mobile (responsive grid, sidebar collapses, tables scroll horizontally)
- Feel like something from a design portfolio — Stripe docs quality, Linear changelog quality, not a styled README
- Have NO wake lock script

### 4. Open it

```bash
open /tmp/visualize-{timestamp}.html
```

### 5. Report back

Tell the user: the file path, a 1-line summary of what's in it, and that it's open in their browser. Keep the terminal response to 2-3 lines max — the HTML page IS the answer.

## Design anti-patterns to avoid

- Same font pairing every time (pick new ones each page)
- Same color scheme every time (build a fresh palette)
- Narrow centered column with tons of whitespace on sides
- Small body text (under 16px)
- Walls of bullet points that could be a table
- Generic card grids that all look identical
- Flat design with no depth or atmosphere
- Timid, evenly-distributed color — use a dominant accent with sharp contrast

## Scaling complexity

- Short content (under 10 items, 1-3 sections): clean cards, no sidebar, no TOC. Simple and elegant.
- Medium content (10-30 items, 3-6 sections): sidebar TOC, expandable details, 1-2 tables.
- Large content (30+ items, 6+ sections): full sidebar nav, multiple tables, heavy use of collapse/expand, search/filter if appropriate.
