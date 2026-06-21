---
name: peel
description: Use when the user says "/peel", "peel this session", "send this to the side window", "unpeel", "pop this back out", or asks where a session is parked. Toggles the current kitty tab (with the running Claude session inside it) between a shared OS window titled "claude-peel" — where multiple Claude sessions sit side by side — and its own window. Creates the peel window on first use. Requires kitty with remote control enabled (already configured in ~/.config/kitty/kitty.conf).
---

# Peel Skill

Park (or pop out) the current Claude session's kitty tab in a shared `claude-peel` OS
window, so multiple Claude sessions sit side by side as tabs in one window.

All the logic lives in **`peel.sh`** (next to this file). The skill's job is just to pick
the mode and run it. Do not re-implement the kitty commands inline — the script encodes
load-bearing details (the `window_id:` matcher, the anchor-tab marker) that are easy to
get wrong from memory.

## When to Use

Invoke when the user says `/peel`, "peel this", "send this to the side", "unpeel",
"pop this back out", "bring it back", or asks where the session is parked.

Do NOT invoke for: running a one-off command in a side window, opening a file in a
separate editor, or anything that isn't "move this whole Claude session between the
shared window and its own window."

## How to run it

Run the script and relay its one-line output to the user. Pick the mode from intent:

| User intent                                              | Command                                  |
|----------------------------------------------------------|------------------------------------------|
| "/peel", "peel this", "send to the side" (default)       | `bash ~/.claude/skills/peel/peel.sh`     |
| "unpeel", "pop out", "bring it back"                     | `bash ~/.claude/skills/peel/peel.sh back`|
| "where is this session?", "am I peeled?"                | `bash ~/.claude/skills/peel/peel.sh status` |
| Force INTO the peel window                                | `bash ~/.claude/skills/peel/peel.sh peel`|

The no-argument form is a **toggle**: it peels if the session is currently outside the
peel window, and unpeels if it's already inside. For a plain `/peel` this is what you
want — it Just Works whether or not the session is already parked. Use the explicit
`back`/`peel` modes only when the user clearly asks for one direction.

The script is idempotent and self-describing: peeling an already-peeled tab, or unpeeling
a free tab, prints a harmless "already …" line and changes nothing. After it runs, the
user sees the window change on screen, so a short text confirmation is enough.

## How it works (reference — the script does this for you)

- The peel window is identified by a tab titled **`peel-anchor`** (also tagged user-var
  `peel_anchor=1`). The script creates it on first peel with
  `kitty @ launch --type=os-window --os-window-title=claude-peel --tab-title=peel-anchor --var peel_anchor=1 --keep-focus`.
  **The OS-window title is NOT a reliable marker** — kitty overwrites
  `--os-window-title` with the active tab's title, so `kitty @ ls` reports it empty. The
  anchor tab is the only durable identity.
- Peel = `detach-tab --match window_id:$KITTY_WINDOW_ID --target-tab title:^peel-anchor$`
  (move this tab into the anchor's OS window). Unpeel = the same `detach-tab` with **no**
  `--target-tab`, which sends the tab into a brand-new OS window.
- **Match on `window_id:`, never `id:` or `state:focused`.** `--match id:N` resolves
  against tab-ids first, and tab-id / window-id ranges overlap once sessions have
  churned, so `id:$KITTY_WINDOW_ID` can silently peel a *different* session's tab.
  `state:focused` peels whatever the user is looking at. `window_id:` matches "the tab
  containing the window with this id" — unambiguous. (This was the real cause of the
  Jun 2026 wrong-tab bug, first misattributed to focus, then to stale env. The env value
  was always correct; only the matcher field was wrong.)
- `$KITTY_WINDOW_ID` is inherited by every shell in the tab and identifies the invoking
  session regardless of focus. If it's empty the session isn't inside kitty; the script
  refuses rather than guessing a tab.

## Cross-process caveat

kitty's `listen_on` is per-PID (`unix:/tmp/kitty-{kitty_pid}`), so `kitty @` only reaches
windows in the **same** kitty process. Cmd-N windows share the process (peel works among
them). Windows launched separately via Spotlight/Dock/Finder are different processes and
can't be targeted. If peel fails with "no matching window," the script prints this cause
and the fix: add `macos_single_instance yes` to `~/.config/kitty/kitty.conf` and relaunch
kitty (every launch then shares one process). Tradeoff: a crash of that one process closes
all windows — so it's left to the user's discretion, not enabled by the skill.

## Error handling

The script exits non-zero with a `peel: …` message that already names the cause and fix.
Just relay it. The common ones:

- `kitty not on PATH` → kitty isn't installed or not on the shell PATH.
- `remote control is unavailable` → add `allow_remote_control yes` to kitty.conf
  (already set in the user's config, so this shouldn't happen).
- `KITTY_WINDOW_ID is empty` → the session isn't running inside kitty; stop, don't guess.
- `couldn't reach the claude-peel window … separate kitty process` → the cross-process
  case above.

## Notes

- The anchor tab is intentionally empty so it isn't closed by accident. If the user closes it
  manually, the next peel recreates the window (any sessions still in the old window stay
  put — move them with another `/peel` from each).
- Peel moves the *whole kitty tab*: the Claude process and any other shells in that tab
  travel together and keep running through the move.
- After peeling, Cmd-` cycles back to the previous OS window.
