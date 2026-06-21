#!/usr/bin/env python3
import argparse
import json
import shutil
from collections import deque
from pathlib import Path

from PIL import Image


def parse_rows(value):
    rows = []
    for part in value.split(","):
        name, count = part.split(":", 1)
        rows.append((name.strip(), int(count)))
    return rows


def remove_checkerboard(im):
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            mx = max(r, g, b)
            mn = min(r, g, b)
            if mn >= 224 and (mx - mn) <= 10:
                pix[x, y] = (255, 255, 255, 0)
            elif mn >= 238 and (mx - mn) <= 18:
                pix[x, y] = (255, 255, 255, 0)
    return im


def connected_components(im, alpha_threshold=120, min_area=3000):
    alpha = im.getchannel("A")
    w, h = im.size
    seen = set()
    comps = []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or alpha.getpixel((x, y)) < alpha_threshold:
                continue
            q = deque([(x, y)])
            seen.add((x, y))
            xs = []
            ys = []
            while q:
                cx, cy = q.popleft()
                xs.append(cx)
                ys.append(cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if (
                        0 <= nx < w
                        and 0 <= ny < h
                        and (nx, ny) not in seen
                        and alpha.getpixel((nx, ny)) >= alpha_threshold
                    ):
                        seen.add((nx, ny))
                        q.append((nx, ny))
            if len(xs) >= min_area:
                comps.append(
                    {
                        "area": len(xs),
                        "bbox": (min(xs), min(ys), max(xs) + 1, max(ys) + 1),
                        "cx": sum(xs) / len(xs),
                        "cy": sum(ys) / len(ys),
                    }
                )
    return comps


def extract_component(im, bbox, pad=10):
    w, h = im.size
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(w, x1 + pad)
    y1 = min(h, y1 + pad)
    crop = im.crop((x0, y0, x1, y1))
    bbox = crop.getchannel("A").getbbox()
    return crop.crop(bbox) if bbox else crop


def make_sheet(im, components, frame_width, frame_height, target_height):
    sheet = Image.new("RGBA", (frame_width * len(components), frame_height), (0, 0, 0, 0))
    for i, component in enumerate(components):
        fr = extract_component(im, component["bbox"])
        ratio = min((frame_width - 38) / fr.width, target_height / fr.height)
        nw = max(1, round(fr.width * ratio))
        nh = max(1, round(fr.height * ratio))
        fr = fr.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (frame_width, frame_height), (0, 0, 0, 0))
        canvas.alpha_composite(fr, ((frame_width - nw) // 2, frame_height - 22 - nh))
        sheet.alpha_composite(canvas, (i * frame_width, 0))
    return sheet


def save_preview(sheet, path):
    bg = Image.new("RGBA", sheet.size, (239, 231, 212, 255))
    px = bg.load()
    for y in range(sheet.height):
        for x in range(sheet.width):
            if (x // 24 + y // 24) % 2:
                px[x, y] = (219, 209, 187, 255)
    bg.alpha_composite(sheet)
    bg.save(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--rows", required=True, help="Comma list like idle:4,walk:8")
    parser.add_argument("--frame-width", type=int, default=320)
    parser.add_argument("--frame-height", type=int, default=363)
    parser.add_argument("--target-height", type=int, default=300)
    args = parser.parse_args()

    src = Path(args.input)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_copy = out_dir / f"{args.prefix}-source.png"
    alpha_copy = out_dir / f"{args.prefix}-source-alpha.png"
    shutil.copy2(src, source_copy)

    im = remove_checkerboard(Image.open(src))
    im.save(alpha_copy)

    rows = parse_rows(args.rows)
    comps = connected_components(im)
    comps_sorted = sorted(comps, key=lambda c: (c["cy"], c["cx"]))
    expected = sum(count for _, count in rows)
    if len(comps_sorted) < expected:
        raise SystemExit(f"Expected at least {expected} components, found {len(comps_sorted)}")

    row_bands = []
    remaining = comps_sorted[:]
    for name, count in rows:
        band = sorted(remaining[:count], key=lambda c: c["cx"])
        row_bands.append((name, band))
        remaining = remaining[count:]

    metadata = {
        "source": source_copy.name,
        "alphaSource": alpha_copy.name,
        "frameWidth": args.frame_width,
        "frameHeight": args.frame_height,
        "pivot": {"x": args.frame_width // 2, "y": args.frame_height - 22},
        "baselineY": args.frame_height - 22,
        "animations": {},
    }

    for name, band in row_bands:
        sheet = make_sheet(im, band, args.frame_width, args.frame_height, args.target_height)
        sheet_path = out_dir / f"{args.prefix}-{name}.png"
        preview_path = out_dir / f"{args.prefix}-{name}-preview.png"
        sheet.save(sheet_path)
        save_preview(sheet, preview_path)
        metadata["animations"][name] = {
            "sheet": sheet_path.name,
            "preview": preview_path.name,
            "frames": len(band),
        }

    meta_path = out_dir / f"{args.prefix}-sprites.json"
    meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
