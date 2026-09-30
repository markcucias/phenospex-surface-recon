"""Small fake PlantEye scan for CI and quick tests: a flat tray with a bump ("plant"),
seen by two scanners on a (profile, x_pos) grid, plus some floating outliers.

Usage: python tests/make_synthetic_ply.py out.ply
"""
import sys

import numpy as np
from plyfile import PlyData, PlyElement

SPACING = 2.0   # mm between grid cells

rng = np.random.default_rng(42)
rows = []

for scanner in (0, 1):
    for profile in range(120):
        for x_pos in range(100):
            # ~5 % missing points, like cells where the laser wasn't seen
            if rng.random() < 0.05:
                continue

            x = x_pos * SPACING + scanner * 0.5   # small offset between the two scanners
            y = profile * SPACING
            z = 40.0 * np.exp(-((x - 100) ** 2 + (y - 120) ** 2) / (2 * 30.0 ** 2))
            z += rng.normal(0, 0.2)

            is_plant = z > 5
            green = 30000 if is_plant else 12000
            nir = 40000 if is_plant else 15000
            rows.append((x, y, z, len(rows), scanner, profile, x_pos, 10000, green, 9000, nir))

for _ in range(50):
    x, y, z = rng.uniform(0, 200), rng.uniform(0, 240), rng.uniform(60, 120)
    rows.append((x, y, z, len(rows), 0, 0, 0, 0, 0, 0, 0))

# Same vertex layout as the real scan
dtype = [("x", "f4"), ("y", "f4"), ("z", "f4"), ("index", "u4"), ("scanner_id", "u1"),
         ("profile", "u4"), ("x_pos", "u4"), ("red", "u2"), ("green", "u2"), ("blue", "u2"), ("nir", "u2")]
vertices = np.array(rows, dtype=dtype)
PlyData([PlyElement.describe(vertices, "vertex")], byte_order="<").write(sys.argv[1])
print(f"wrote {len(vertices)} points to {sys.argv[1]}")
