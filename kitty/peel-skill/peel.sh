#!/usr/bin/env bash
#
# peel.sh — park (or pop out) the current kitty tab in the shared "claude-peel" OS window.
#
# Usage:
#   peel.sh           toggle: peel if this tab is outside the peel window, unpeel if inside
#   peel.sh peel      force peel  (move this tab INTO the peel window)
#   peel.sh back      force unpeel (pop this tab OUT into its own new OS window)
#   peel.sh status    print where this tab is, change nothing
#
# Design notes (load-bearing — read before editing):
#  * The peel window is identified ONLY by a tab titled "peel-anchor" (also tagged
#    user-var peel_anchor=1). The OS-window title is NOT reliable: kitty overwrites
#    --os-window-title with the active tab's title, so `kitty @ ls` reports it empty.
#  * Always match THIS tab with `window_id:$KITTY_WINDOW_ID`, never `id:` and never
#    `state:focused`. `id:` resolves against tab-ids first (which overlap window-ids),
#    and `state:focused` is whatever the user is looking at — both peel the wrong tab.
#  * detach-tab with --target-tab moves into that tab's OS window; WITHOUT --target-tab
#    it creates a new OS window. That asymmetry is how peel and unpeel are both one call.

set -euo pipefail

ANCHOR_TITLE="peel-anchor"
PEEL_WINDOW_TITLE="claude-peel"

die() { printf 'peel: %s\n' "$*" >&2; exit 1; }

command -v kitty >/dev/null 2>&1 || die "kitty not on PATH — is kitty installed and on PATH?"
[ -n "${KITTY_WINDOW_ID:-}" ] || die "KITTY_WINDOW_ID is empty — this shell isn't running inside a kitty tab. Refusing to guess a tab."

# One snapshot of kitty state; classify it in Python (robust JSON, no jq dependency).
state="$(kitty @ ls 2>/dev/null)" || die "kitty remote control is unavailable — check 'allow_remote_control yes' in ~/.config/kitty/kitty.conf"

# Emits two flags: "<anchor_present> <i_am_peeled>" (e.g. "1 0").
classify="$(
  KITTY_WINDOW_ID="$KITTY_WINDOW_ID" ANCHOR_TITLE="$ANCHOR_TITLE" python3 - "$state" <<'PY'
import sys, json, os
try:
    state = json.loads(sys.argv[1])
except Exception:
    print("0 0"); sys.exit(0)
me = int(os.environ["KITTY_WINDOW_ID"])
anchor = os.environ["ANCHOR_TITLE"]
anchor_present = i_am_peeled = 0
for osw in state:
    tabs = osw.get("tabs", [])
    has_anchor = any(
        t.get("title") == anchor or t.get("user_vars", {}).get("peel_anchor") == "1"
        for t in tabs
    )
    has_me = any(w.get("id") == me for t in tabs for w in t.get("windows", []))
    if has_anchor:
        anchor_present = 1
        if has_me:
            i_am_peeled = 1
print(anchor_present, i_am_peeled)
PY
)"
anchor_present="${classify% *}"
i_am_peeled="${classify#* }"

mode="${1:-toggle}"
case "$mode" in
  status)
    if [ "$i_am_peeled" = 1 ]; then echo "this tab is IN the $PEEL_WINDOW_TITLE window"; else echo "this tab is OUTSIDE the $PEEL_WINDOW_TITLE window"; fi
    [ "$anchor_present" = 1 ] && echo "peel window: present" || echo "peel window: not created yet"
    exit 0 ;;
  toggle) [ "$i_am_peeled" = 1 ] && mode=back || mode=peel ;;
  peel|back) ;;
  *) die "unknown mode '$mode' — use: peel | back | toggle | status" ;;
esac

if [ "$mode" = back ]; then
  if [ "$i_am_peeled" != 1 ]; then
    echo "already in its own window — nothing to unpeel"
    exit 0
  fi
  kitty @ detach-tab --match "window_id:$KITTY_WINDOW_ID" \
    || die "failed to detach this tab into a new window"
  echo "unpeeled — this session is now in its own window"
  exit 0
fi

# mode = peel
if [ "$i_am_peeled" = 1 ]; then
  echo "already peeled — this session is in the $PEEL_WINDOW_TITLE window"
  exit 0
fi

# Create the peel window if its anchor is missing.
if [ "$anchor_present" != 1 ]; then
  kitty @ launch --type=os-window \
    --os-window-title="$PEEL_WINDOW_TITLE" \
    --tab-title="$ANCHOR_TITLE" \
    --var peel_anchor=1 \
    --keep-focus >/dev/null \
    || die "failed to create the $PEEL_WINDOW_TITLE window"
fi

# Move this tab into the peel window. Capture stderr to give the cross-process hint.
err="$(kitty @ detach-tab --match "window_id:$KITTY_WINDOW_ID" --target-tab "title:^${ANCHOR_TITLE}\$" 2>&1)" || {
  case "$err" in
    *[Nn]"o matching"*)
      die "couldn't reach the $PEEL_WINDOW_TITLE window — it's likely a separate kitty process (Spotlight/Dock-launched). Fix: add 'macos_single_instance yes' to ~/.config/kitty/kitty.conf, then relaunch kitty." ;;
    *) die "detach failed: $err" ;;
  esac
}
echo "peeled — this session is now in the $PEEL_WINDOW_TITLE window"
