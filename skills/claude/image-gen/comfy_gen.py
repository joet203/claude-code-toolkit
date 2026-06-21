#!/usr/bin/env python3
"""Generate an image with a local ComfyUI server (txt2img, SD1.5 checkpoint).

Usage:
  python3 comfy_gen.py "a prompt" [--out PATH] [--neg "negative prompt"]
      [--w 512] [--h 512] [--steps 25] [--cfg 7] [--seed N] [--ckpt NAME]

Exit codes: 0 ok, 1 server unreachable, 2 generation failed.
Prints the saved file path on success.
"""
import argparse, json, sys, time, urllib.request, urllib.error, urllib.parse, os

HOST = os.environ.get("COMFYUI_HOST", "http://127.0.0.1:8188")


def _get(path, timeout=10):
    with urllib.request.urlopen(f"{HOST}{path}", timeout=timeout) as r:
        return json.load(r)


def pick_checkpoint(preferred=None):
    info = _get("/object_info/CheckpointLoaderSimple")
    names = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    if not names:
        raise RuntimeError("no checkpoints installed in ComfyUI")
    if preferred and preferred in names:
        return preferred
    return names[0]


def build_workflow(a, ckpt):
    return {
        "4": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": ckpt}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": a.w, "height": a.h, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode",
              "inputs": {"text": a.prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode",
              "inputs": {"text": a.neg, "clip": ["4", 1]}},
        "3": {"class_type": "KSampler",
              "inputs": {"seed": a.seed, "steps": a.steps, "cfg": a.cfg,
                         "sampler_name": "dpmpp_2m", "scheduler": "karras",
                         "denoise": 1.0, "model": ["4", 0],
                         "positive": ["6", 0], "negative": ["7", 0],
                         "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode",
              "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "claude_imggen", "images": ["8", 0]}},
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--out", default=f"/tmp/imggen-{int(time.time())}.png")
    p.add_argument("--neg", default="lowres, bad anatomy, worst quality, low quality, blurry, watermark, text")
    p.add_argument("--w", type=int, default=512)
    p.add_argument("--h", type=int, default=512)
    p.add_argument("--steps", type=int, default=25)
    p.add_argument("--cfg", type=float, default=7.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--ckpt", default=None)
    a = p.parse_args()

    try:
        ckpt = pick_checkpoint(a.ckpt)
    except (urllib.error.URLError, ConnectionError, OSError) as e:
        print(f"ComfyUI not reachable at {HOST}: {e}", file=sys.stderr)
        return 1

    wf = build_workflow(a, ckpt)
    body = json.dumps({"prompt": wf}).encode()
    try:
        req = urllib.request.Request(f"{HOST}/prompt", data=body,
                                     headers={"Content-Type": "application/json"})
        pid = json.load(urllib.request.urlopen(req, timeout=15))["prompt_id"]
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        detail = e.read().decode() if hasattr(e, "read") else str(e)
        print(f"submit failed: {detail}", file=sys.stderr)
        return 2

    # Poll history until the prompt completes (MPS SD1.5 ~ tens of seconds).
    img = None
    for _ in range(180):
        time.sleep(1)
        hist = _get(f"/history/{pid}")
        if pid in hist:
            outs = hist[pid].get("outputs", {})
            imgs = outs.get("9", {}).get("images", [])
            if imgs:
                img = imgs[0]
                break
            if hist[pid].get("status", {}).get("status_str") == "error":
                print("generation errored on server", file=sys.stderr)
                return 2
    if not img:
        print("timed out waiting for image", file=sys.stderr)
        return 2

    q = urllib.parse.urlencode({"filename": img["filename"],
                                "subfolder": img.get("subfolder", ""),
                                "type": img.get("type", "output")})
    with urllib.request.urlopen(f"{HOST}/view?{q}", timeout=30) as r:
        data = r.read()
    with open(a.out, "wb") as f:
        f.write(data)
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
