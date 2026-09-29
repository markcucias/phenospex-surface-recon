# Working notes

Raw log written while working. The README is distilled from this at the end.
Rule: write the observation *and* what it means for the pipeline.

## Time log

| Date | Phase | Minutes | What |
|------|-------|---------|------|
|      | 0 Setup |       |      |

## Observations

### Header (before loading data) — to verify
- Two PlantEye scanners (`scanner_id`): x0 = ±270 mm, z0 = 1150 mm, pitch ∓20°. Point counts 2,060,516 / 1,138,143 (why unequal?).
- Units look like mm (`field_y_length` = 1980, x range ≈ −568..403).
- `profile` ≈ scan line (0..2432 over 1980 mm → ~0.8 mm apart); `x_pos` ≈ column on the laser line (55..1387).
- Colors are 16-bit R, G, B + NIR.
- Hypothesis: (scanner_id, profile, x_pos) is a unique grid cell → neighbours known without a k-d tree.

### Inspection results
<!-- paste numbers + figure names, then interpret -->

## Decisions

| Decision | Alternatives considered | Why |
|----------|------------------------|-----|
|          |                        |     |

## Experiments

<!-- one entry per run: what changed, parameters, result, screenshot, conclusion -->

## Open questions / ideas
