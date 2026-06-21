#!/usr/bin/env python3
"""
tag-note — leave a big bold blue note over a parked kitty tab.

Bound to a kitty key (see kitty.conf). Press it, type a short note, and a large
bright-blue label appears in the lower-middle of the window (an overlay covering the
parked session) so you remember where you left off / why it's open. Press a key to dismiss.

Pure stdlib: a tiny 3x5 block font, upscaled, drawn with █ blocks.
"""
import json
import os
import shutil
import subprocess
import sys

# 3-wide x 5-tall bitmap font ('#' = on). Notes are upper-cased before rendering.
F = {
    'A': [" # ","# #","###","# #","# #"], 'B': ["## ","# #","## ","# #","## "],
    'C': [" ##","#  ","#  ","#  "," ##"], 'D': ["## ","# #","# #","# #","## "],
    'E': ["###","#  ","## ","#  ","###"], 'F': ["###","#  ","## ","#  ","#  "],
    'G': [" ##","#  ","# #","# #"," ##"], 'H': ["# #","# #","###","# #","# #"],
    'I': ["###"," # "," # "," # ","###"], 'J': ["  #","  #","  #","# #"," # "],
    'K': ["# #","# #","## ","# #","# #"], 'L': ["#  ","#  ","#  ","#  ","###"],
    'M': ["# #","###","###","# #","# #"], 'N': ["# #","## ","###"," ##","# #"],
    'O': [" # ","# #","# #","# #"," # "], 'P': ["## ","# #","## ","#  ","#  "],
    'Q': [" # ","# #","# #"," # ","  #"], 'R': ["## ","# #","## ","# #","# #"],
    'S': [" ##","#  "," # ","  #","## "], 'T': ["###"," # "," # "," # "," # "],
    'U': ["# #","# #","# #","# #","###"], 'V': ["# #","# #","# #","# #"," # "],
    'W': ["# #","# #","###","###","# #"], 'X': ["# #","# #"," # ","# #","# #"],
    'Y': ["# #","# #"," # "," # "," # "], 'Z': ["###","  #"," # ","#  ","###"],
    '0': ["###","# #","# #","# #","###"], '1': [" # ","## "," # "," # ","###"],
    '2': ["## ","  #"," # ","#  ","###"], '3': ["###","  #"," ##","  #","###"],
    '4': ["# #","# #","###","  #","  #"], '5': ["###","#  ","## ","  #","## "],
    '6': [" ##","#  ","## ","# #"," # "], '7': ["###","  #"," # "," # "," # "],
    '8': [" # ","# #"," # ","# #"," # "], '9': [" # ","# #"," ##","  #","## "],
    ' ': ["   ","   ","   ","   ","   "], '.': ["   ","   ","   ","   "," # "],
    ',': ["   ","   ","   "," # "," # "], '!': [" # "," # "," # ","   "," # "],
    '?': ["## ","  #"," # ","   "," # "], ':': ["   "," # ","   "," # ","   "],
    '-': ["   ","   ","###","   ","   "], "'": [" # "," # ","   ","   ","   "],
    '/': ["  #","  #"," # ","#  ","#  "], '(': [" ##","#  ","#  ","#  "," ##"],
    ')': ["## ","  #","  #","  #","## "], '#': ["# #","###","# #","###","# #"],
}
BLUE = "\033[1;94m"          # bold bright blue (the note)
DIMBG = "\033[38;5;240m"     # faint gray (the dimmed session text behind it)
DIM = "\033[2;37m"
RESET = "\033[0m"
BLOCK = "█"


def sibling_screen():
    """Snapshot the session window sharing this tab, so we can show it dimmed behind the note."""
    try:
        me = int(os.environ.get("KITTY_WINDOW_ID", "0"))
        tree = json.loads(subprocess.check_output(["kitty", "@", "ls"], timeout=4))
        target = None
        for ow in tree:
            for tab in ow["tabs"]:
                ids = [w["id"] for w in tab["windows"]]
                if me in ids:
                    sibs = [w for w in tab["windows"] if w["id"] != me]
                    target = next((w for w in sibs if any(
                        "claude" in " ".join(p.get("cmdline", [])) for p in w.get("foreground_processes", []))),
                        sibs[0] if sibs else None)
        if not target:
            return []
        txt = subprocess.check_output(
            ["kitty", "@", "get-text", "--match", f"id:{target['id']}", "--extent", "screen"],
            timeout=4).decode(errors="ignore")
        return txt.splitlines()
    except Exception:
        return []


def glyph(ch):
    return F.get(ch.upper(), F[' '])


def render_word(word, scale):
    """Return the list of text rows for one word at the given pixel scale."""
    rows = [""] * (5 * scale)
    for ch in word:
        g = glyph(ch)
        for r in range(5):
            line = "".join((BLOCK if px == "#" else " ") * scale for px in g[r])
            for s in range(scale):
                rows[r * scale + s] += line + " " * scale  # 1px gap between letters
    return rows


def wrap_lines(text, scale, max_cols):
    """Greedy word-wrap so each rendered line fits the terminal width."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if len(render_word(trial, scale)[0]) > max_cols and cur:
            out.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        out.append(cur)
    return out or [""]


def main():
    sys.stdout.write("\033[?25h")  # cursor visible for the prompt
    try:
        note = input(f"{BLUE}📌 Tag this tab — type a note:{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not note:
        return

    bg = sibling_screen()
    cols, lines = shutil.get_terminal_size((80, 24))
    # smaller note: start at scale 2, shrink to 1 only if it doesn't fit
    scale = 2
    while scale > 1 and (len(render_word(note.split()[0] if note.split() else note, scale)[0]) > cols
                         or 5 * scale > lines // 2):
        scale -= 1
    blocks = wrap_lines(note, scale, cols - 2)

    rendered = []
    for i, ln in enumerate(blocks):
        rendered.extend(render_word(ln, scale))
        if i < len(blocks) - 1:
            rendered.append("")  # blank row between wrapped lines

    height = len(rendered)
    top = max(1, lines - height - 2)                 # anchored low, near the bottom

    out = ["\033[2J\033[H"]                          # clear screen
    # paint the session snapshot as the background, slightly dimmed (faint attribute)
    for r, line in enumerate(bg[:lines]):
        if line.strip():
            out.append(f"\033[{r + 1};1H\033[0;2m{line[:cols]}{RESET}")
    for i, row in enumerate(rendered):
        pad = max(0, (cols - len(row)) // 2)
        # paint only the blue blocks; leave gaps untouched so the dimmed text shows through
        col = pad + 1
        for ch in row:
            if ch == BLOCK:
                out.append(f"\033[{top + i};{col}H{BLUE}{BLOCK}{RESET}")
            col += 1
    out.append(f"\033[{lines};1H{DIM}  press any key to dismiss{RESET}")
    out.append("\033[?25l")                          # hide cursor
    sys.stdout.write("".join(out))
    sys.stdout.flush()

    # wait for a single keypress, then exit (overlay closes)
    try:
        import termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        try:
            input()
        except Exception:
            pass
    sys.stdout.write("\033[?25h\033[0m")


if __name__ == "__main__":
    main()
