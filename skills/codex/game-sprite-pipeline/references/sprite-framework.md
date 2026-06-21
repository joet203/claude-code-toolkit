# Sprite Framework

## Quality Targets

- One consistent character identity per sheet.
- One consistent outfit per lifecycle stage.
- Fixed frame width and height for all frames in an animation family.
- Same foot baseline across frames.
- Transparent background, not visual checkerboard.
- Transparent gutters around every frame.
- No text, labels, grid lines, shadows, or cropping in source prompts.
- Source image preserved separately from processed game sheets.

## Character Bible Template

```text
Name:
Age/stage:
Species/body:
Face:
Outfit:
Accessories:
Camera:
Facing:
Style:
Do not include:
```

## Young Wilson Bible

```text
Name: Young Wilson.
Age/stage: school-age dog before priesthood.
Species/body: small tan chihuahua-pug mix, compact body, short legs, expressive face.
Face: dark floppy ears, huge glossy dark eyes, black nose, pale white muzzle, gentle happy expression.
Outfit: navy school coat, brown satchel strap and small satchel, no priest collar.
Camera: full body, side-facing 3/4 view.
Facing: right by default; flip in engine for left.
Style: cute high-quality polished 3D storybook/Nintendo-like game illustration.
Do not include: priest collar, adult priest outfit, text labels, background scene, cropped paws, changed outfit between frames.
```

## Generation Checklist

Before generating:

- Decide animation rows and frame counts.
- Decide exact outfit and age stage.
- Keep one animation family per generation when quality matters.
- Include "same exact character, outfit, proportions, camera angle, scale, baseline."
- Include "full body visible in every frame."
- Include "transparent background", then assume post-processing is still needed.

After generating:

- View the image.
- Confirm row/column structure.
- Confirm no frames are cut off.
- Confirm outfit consistency.
- Confirm face and ears remain recognizable.
- Confirm walking includes contact, down, passing/crossover, and up frames.

## Integration Checklist

- Use one fixed outer character box in CSS or engine code.
- Put sprite sheet on an inner element.
- Do not resize the outer box between idle and walk.
- Use `steps(frameCount)` or explicit frame positions.
- Change animation classes only on state transitions.
- Reset background position when stopping.
- Play idle after stopping.
- Keep direction flip on the inner sprite, not the outer movement box.

## Metadata Shape

```json
{
  "character": "young-wilson",
  "frameWidth": 320,
  "frameHeight": 363,
  "pivot": { "x": 160, "y": 341 },
  "baselineY": 341,
  "animations": {
    "idle": { "sheet": "young-wilson-idle.png", "frames": 4, "durationMs": 950 },
    "walk": { "sheet": "young-wilson-walk.png", "frames": 8, "durationMs": 1020 }
  }
}
```
