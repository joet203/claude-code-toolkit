---
name: game-sprite-pipeline
description: Generate, clean, align, and integrate consistent game-ready character sprite sheets from AI image outputs. Use when working on 2D/2.5D game character sprites, animation sheets, transparent-background sprite assets, frame slicing, alpha cleanup, fixed frame boxes, baseline/pivot alignment, idle/walk/action animation loops, or image-model prompts for consistent game sprites.
---

# Game Sprite Pipeline

Use this skill to turn image-model sprite-sheet outputs into usable game assets. Treat generated sheets as source material, then apply deterministic cleanup before integrating them into a game.

## Core Rule

Do not trust raw AI sprite sheets as game-ready. Always post-process them into fixed-size RGBA sheets with stable frame dimensions, transparent gutters, consistent baseline, and matching metadata.

## Workflow

1. Define a character bible:
   - Species/body/proportions.
   - Outfit and accessories.
   - Camera angle and facing direction.
   - Rendering style.
   - Forbidden variations, such as outfit changes or collar appearing too early.

2. Generate a unified source sheet:
   - Prefer one sheet containing related animations for the same character.
   - Ask for fixed rows: for example, row 1 idle, row 2 walk.
   - Require same character, outfit, scale, angle, foot baseline, and full body in every frame.
   - Ask for transparent background, but expect fake checkerboard and clean it later.

3. Inspect the source:
   - View the image before processing.
   - Confirm frame count, pose order, outfit consistency, and whether feet/heads are cropped.
   - Reject or regenerate if the character identity changes heavily across frames.

4. Process into game sheets:
   - Convert fake checkerboard/near-white background to alpha.
   - Detect each character pose as a connected component.
   - Crop each pose, keeping only the main component.
   - Normalize height while preserving proportions.
   - Place every pose into the same frame size.
   - Bottom-align feet to one baseline.
   - Add transparent gutters to prevent browser/game texture bleed.
   - Export separate sheets per animation.

5. Integrate and test:
   - Use one fixed display box per character.
   - Swap only the inner sprite sheet/animation class, not the outer character box.
   - Change animation state only when movement starts/stops, not every frame.
   - Test idle, movement, direction flip, clipping, size popping, and console errors.

6. Persist metadata:
   - Record frame width, height, frame count, frame duration, pivot point, and baseline.
   - Keep original generated source next to processed sheets.

## Prompt Pattern

Use a strict prompt like:

```text
Game-ready sprite sheet, transparent background, one consistent character only:
[character bible].

Same exact character, same outfit, same proportions, same camera angle, same scale,
full body visible, feet on same baseline, no cropping, no text.

Grid: [row/column layout].
Row 1: [animation and frames].
Row 2: [animation and frames].
[Facing direction]. Clear readable motion. Stable head/nose. Even spacing between frames.
```

## Recommended Animation Order

Build animations in this order:

1. Idle: 4 frames.
2. Walk: 8 frames, including passing/crossover poses.
3. Happy/celebrate: 4 frames.
4. Think/listen: 4 frames.
5. Pray/solemn: 4 frames.
6. Startled: 4 frames.
7. Receive item: 4 frames.

## Scripts

Use `scripts/process_sprite_sheet.py` when converting a generated sprite sheet into separate animation sheets. It expects rows with known frame counts and exports cleaned RGBA sheets plus previews.

Example:

```bash
python3 ~/.codex/skills/game-sprite-pipeline/scripts/process_sprite_sheet.py \
  --input /path/to/generated.png \
  --output-dir /path/to/assets/generated/character/sprites \
  --prefix young-wilson \
  --rows idle:4,walk:8 \
  --frame-width 320 \
  --frame-height 363
```

Read `references/sprite-framework.md` for the complete project framework and decision checklist.
