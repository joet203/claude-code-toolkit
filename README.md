# claude-code-toolkit

A curated collection of **custom skills, plugins, and terminal add-ons** I built to get more out of agentic coding tools — [Claude Code](https://docs.anthropic.com/en/docs/claude-code), the [OpenAI Codex CLI](https://github.com/openai/codex), and the [kitty](https://sw.kovidgoyal.net/kitty/) terminal.

These are the pieces I actually use day to day. They're shared here as working examples of how to extend agent CLIs with reusable, model-invocable capabilities — and a couple of small terminal hacks for running several agent sessions at once.

> Everything here has been generalized from my personal setup — personal automations (job-hunt, resume, companion assistant) are intentionally left out. What remains is the genuinely reusable stuff.

---

## What's inside

```
skills/
  claude/        Standalone Claude Code skills (drop into ~/.claude/skills/)
  codex/         OpenAI Codex CLI skills (drop into ~/.codex/skills/)
plugins/         Claude Code plugins (marketplace-style, with plugin.json)
kitty/           Terminal add-ons for running/parking multiple agent sessions
docs/            Setup notes
```

### 🧠 Claude Code skills — `skills/claude/`

Standalone skills (a `SKILL.md` with YAML frontmatter). Claude auto-discovers them and invokes them by description — no registration needed.

| Skill | What it does |
|---|---|
| **visualize** | Render answers as a styled HTML page instead of dumping text in the terminal — research, comparisons, decision matrices, status dashboards. |
| **deploy** | Deploy to Vercel *and verify the live URL actually serves new content* — catches cache, SSO-protection, and duplicate-file footguns that hide behind "Deployment succeeded." |
| **factcheck** | Verify factual claims (prices, hours, quotes, citations, laws, dates) via web search before they land in published content; flag the unverifiable rather than guessing. |
| **grill-me** | Stress-test a plan or design by interviewing you relentlessly, resolving each branch of the decision tree until there's shared understanding. |
| **image-gen** | Generate images from text across three cost-ordered backends (local ComfyUI → pollinations.ai → Codex `gpt-image-2`). Includes the helper scripts. |

### ⚙️ Codex CLI skills — `skills/codex/`

| Skill | What it does |
|---|---|
| **vercel-deploy** | Deploy a project to Vercel from the Codex CLI and ensure it's publicly reachable. |
| **game-sprite-pipeline** | Generate, clean, align, and pack consistent game-ready sprite sheets from AI image output. Includes scripts. |
| **offbeat-joke** | Write short, genuinely offbeat / surreal / statistically-unlikely jokes. |

### 🔌 Plugins — `plugins/`

Packaged Claude Code plugins (`.claude-plugin/plugin.json` + `commands/`).

| Plugin | What it does |
|---|---|
| **codex** | Delegate a task to the OpenAI Codex CLI as a subagent from inside Claude Code — including fan-out to several Codex jobs in parallel. |
| **vercel-deploy** | A slash-command wrapper around the verified Vercel deploy flow. |

### 🐱 kitty terminal add-ons — `kitty/`

Small hacks for working with **multiple live agent sessions** in one terminal. See [`kitty/README.md`](kitty/README.md).

| Add-on | What it does |
|---|---|
| **tag-note.py** | Press a hotkey, type a short note, and a big bold label is drawn over a parked tab — a "where I left off" reminder. Pure stdlib, tiny built-in block font. |
| **peel-skill** | A Claude Code skill that moves the current session's tab into a shared side window so several Claude sessions can sit side by side. |

---

## Install

**Claude Code skills** — copy any folder into your skills directory:
```bash
cp -R skills/claude/visualize ~/.claude/skills/
```
They're live-reloaded and auto-discovered. No config.

**Codex skills** — same idea:
```bash
cp -R skills/codex/offbeat-joke ~/.codex/skills/
```

**Plugins** — copy into your plugins source dir, register in your marketplace, and enable in `~/.claude/settings.json`. See each plugin's folder.

**kitty add-ons** — see [`kitty/README.md`](kitty/README.md) for the two config lines.

---

## Why this exists

Agent CLIs are far more useful when you teach them reusable moves instead of re-explaining the same workflow every session. A skill is just a markdown file with a good description — the model decides when to use it. These are the ones that earned a permanent place in my setup.

## License

[MIT](LICENSE) — use, fork, adapt freely.
