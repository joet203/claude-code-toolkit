# kitty add-ons for multi-session agent work

Two small hacks that make it easier to run **several live agent sessions** (Claude Code, Codex) at once in the [kitty](https://sw.kovidgoyal.net/kitty/) terminal.

## tag-note.py — "where did I leave off?" labels

When you have a dozen tabs each running a different agent session, you lose track of which is which. Press a hotkey, type a short note, and a **big bold label** is drawn over the current tab as an overlay. Press any key to dismiss.

Pure Python stdlib — it ships its own tiny 3×5 block font and upscales it with `█` blocks, so there are no dependencies.

**Setup** — copy the script and bind a key in `kitty.conf`:

```conf
# Draw a big note over the current tab (press, type, dismiss)
map ctrl+shift+p launch --type=overlay --title "📌 tag" python3 ~/.config/kitty/tag-note.py
```

```bash
cp tag-note.py ~/.config/kitty/tag-note.py
```

## peel — park sessions side by side

`peel-skill/` is a **Claude Code skill** (not a kitty script). When invoked, it moves the current kitty tab — with the running Claude session still inside it — into a shared OS window titled `claude-peel`, so multiple Claude sessions can be parked next to each other in one window. Saying it again pops the session back out.

It drives kitty over its remote-control socket, which requires these lines at the top of `kitty.conf`:

```conf
allow_remote_control yes
listen_on unix:/tmp/kitty-{kitty_pid}
```

> The per-PID socket matters: tools that target a specific session (peel, and similar orchestration) need to address one window by its pid. Don't replace it with a single fixed `listen_on`.

**Setup** — install like any standalone skill:
```bash
cp -R peel-skill ~/.claude/skills/peel
```
