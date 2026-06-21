#!/usr/bin/env python3
"""Generate an image via pollinations.ai (free, no API key, needs internet).

Usage:
  python3 pollinations_gen.py "a prompt" [--out PATH] [--w 1024] [--h 1024]
      [--seed N] [--raw]

Prints the saved file path on success. Exit 0 ok, 2 failed.

ASPECT RATIO (important): pollinations currently serves the "sana" model, which
generates natively at 512x512. Two failure modes verified 2026-05:
  * a NON-SQUARE request comes back STRETCHED (square render scaled to fit), and
  * a LARGE square request (>=1024) comes back LETTERBOXED with black bars.
So we always render a modest SQUARE (<=768, where Sana fills the frame), then
center-CROP to the requested aspect and upscale to the requested w x h with
`sips` (macOS, no deps). That yields an undistorted, full-bleed image at any
aspect. Pass --raw to skip all of this and request w x h directly (may stretch).
The first request can also return 200 with 0 bytes (cold start) — we retry.
"""
import argparse, subprocess, sys, time, urllib.parse, urllib.request, urllib.error

GEN = 768  # square render size that Sana fills cleanly (no stretch, no letterbox)


def fetch(prompt, w, h, model, seed):
    params = {"width": w, "height": h, "nologo": "true", "model": model}
    if seed is not None:
        params["seed"] = seed
    url = (f"https://image.pollinations.ai/prompt/"
           f"{urllib.parse.quote(prompt)}?{urllib.parse.urlencode(params)}")
    # pollinations 403s the default Python-urllib UA; send a browser-like one.
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = b""
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
        except (urllib.error.URLError, OSError) as e:
            print(f"attempt {attempt+1}: {e}", file=sys.stderr)
            data = b""
        if len(data) > 1000:
            return data
        time.sleep(3)  # cold start — give the model a moment
    return None


def sips(*args):
    r = subprocess.run(["sips", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"warning: sips {' '.join(args)} -> {r.stderr.strip()}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--out", default=f"/tmp/imggen-{int(time.time())}.jpg")
    p.add_argument("--w", type=int, default=1024)
    p.add_argument("--h", type=int, default=1024)
    # Pollinations serves only "sana" and IGNORES this param (verified 2026-05).
    p.add_argument("--model", default="sana")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--raw", action="store_true",
                   help="request w x h directly, no square-gen/crop (may stretch)")
    a = p.parse_args()

    if a.raw:
        data = fetch(a.prompt, a.w, a.h, a.model, a.seed)
    else:
        data = fetch(a.prompt, GEN, GEN, a.model, a.seed)
    if not data:
        print("pollinations returned no image (rate limit or outage?)", file=sys.stderr)
        return 2

    with open(a.out, "wb") as f:
        f.write(data)
    if a.raw:
        print(a.out)
        return 0

    # Square -> requested aspect: center-crop within the GEN box, then upscale.
    if a.w >= a.h:
        crop_w, crop_h = GEN, max(1, round(GEN * a.h / a.w))
    else:
        crop_w, crop_h = max(1, round(GEN * a.w / a.h)), GEN
    if (crop_w, crop_h) != (GEN, GEN):
        sips("-c", str(crop_h), str(crop_w), a.out)   # sips -c is HEIGHT WIDTH
    if (a.w, a.h) != (crop_w, crop_h):
        sips("-z", str(a.h), str(a.w), a.out)          # upscale to exact request

    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
