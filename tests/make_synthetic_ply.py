"""Generate a small synthetic PLY with the same vertex layout as the PlantEye scan.

Used for smoke tests and CI, so the pipeline can be tested without the real (large) data file.
Scene: a flat tray at z=0 with a smooth bump ("plant"), sampled on a (profile, x_pos) grid
by two virtual scanners, plus a few random outliers.

Usage: python tests/make_synthetic_ply.py out.ply
"""
import sys

import numpy as np
from plyfile import PlyData, PlyElement

rng = np.random.default_rng(42)
rows = []
for scanner_id in (0, 1):
    for profile in range(120):                   # scan lines, 2 mm apart in y
        for x_pos in range(0, 100):               # columns along the laser line, 2 mm apart in x
            if rng.random() < 0.05:                # ~5% dropouts, like missing laser returns
                continue
            x = x_pos * 2.0 + scanner_id * 0.5     # slight offset between the two scanners
            y = profile * 2.0
            z = 40.0 * np.exp(-((x - 100) ** 2 + (y - 120) ** 2) / (2 * 30.0 ** 2))  # bump
            z += rng.normal(0, 0.2)                # sensor noise
            green = 30000 if z > 5 else 12000
            rows.append((x, y, z, len(rows), scanner_id, profile, x_pos, 10000, green, 9000, 40000 if z > 5 else 15000))

for _ in range(50):                                # floating outliers
    rows.append((rng.uniform(0, 200), rng.uniform(0, 240), rng.uniform(60, 120), len(rows), 0, 0, 0, 0, 0, 0, 0))

dtype = [("x", "f4"), ("y", "f4"), ("z", "f4"), ("index", "u4"), ("scanner_id", "u1"),
         ("profile", "u4"), ("x_pos", "u4"), ("red", "u2"), ("green", "u2"), ("blue", "u2"), ("nir", "u2")]
arr = np.array(rows, dtype=dtype)
PlyData([PlyElement.describe(arr, "vertex")], byte_order="<").write(sys.argv[1])
print(f"wrote {len(arr)} points to {sys.argv[1]}")
