"""Checks whether (profile, x_pos) grid neighbours are also neighbours in 3D, and measures
point spacing, tray noise and the height offset between the two scanners.

Usage: python python/analyse_grid.py data/scan.ply
"""
import math
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from plyfile import PlyData

# Read off results/figures/inspection.png
WALL_X_MAX = -500.0
OUTLIER_Z_MAX = 1500.0
# Flat, empty piece of tray that both scanners see
PATCH_X = (150.0, 300.0)
PATCH_Y = (400.0, 600.0)


# grid[row][col] = index of the point in that cell, or -1 if empty
def build_grid(profiles, columns):
    first_row = min(profiles)
    first_col = min(columns)
    n_rows = max(profiles) - first_row + 1
    n_cols = max(columns) - first_col + 1

    grid = [[-1] * n_cols for _ in range(n_rows)]
    for i in range(len(profiles)):
        grid[profiles[i] - first_row][columns[i] - first_col] = i
    return grid


# 3D distances to the next cell on the same laser line and on the next scan line
def neighbour_distances(grid, points):
    along_line = []
    across_lines = []
    n_rows = len(grid)
    n_cols = len(grid[0])

    for r in range(n_rows):
        for c in range(n_cols):
            i = grid[r][c]
            if i == -1:
                continue

            if c + 1 < n_cols:
                j = grid[r][c + 1]
                if j != -1:
                    along_line.append(math.dist(points[i], points[j]))

            if r + 1 < n_rows:
                j = grid[r + 1][c]
                if j != -1:
                    across_lines.append(math.dist(points[i], points[j]))

    return along_line, across_lines


# Returns (point count, median z, std of z) of the flat tray patch
def tray_patch(points):
    zs = [z for (x, y, z) in points
          if PATCH_X[0] <= x <= PATCH_X[1] and PATCH_Y[0] <= y <= PATCH_Y[1]]
    if not zs:
        return 0, float("nan"), float("nan")

    # Drop stray points at the edges of the tray holes
    middle = float(np.median(zs))
    zs = [z for z in zs if abs(z - middle) < 5.0]
    return len(zs), float(np.median(zs)), float(np.std(zs))


def describe(name, distances):
    p50, p90, p99, p999 = np.percentile(distances, [50, 90, 99, 99.9])
    print(f"  {name}: {len(distances):,} pairs")
    print(f"    median {p50:.3f} mm | 90% below {p90:.3f} | 99% below {p99:.2f} | 99.9% below {p999:.1f}")
    longer = [f">{t} mm: {sum(d > t for d in distances) / len(distances):.2%}" for t in (1.5, 3, 5, 10)]
    print("    share of pairs longer than  " + "   ".join(longer))


path = sys.argv[1]
t0 = time.time()
v = PlyData.read(path)["vertex"].data

xs, ys, zs = v["x"].tolist(), v["y"].tolist(), v["z"].tolist()
sids, profs, cols = v["scanner_id"].tolist(), v["profile"].tolist(), v["x_pos"].tolist()

# Each scanner gets its own grid, so split the points first
scanners = {}
for i in range(len(xs)):
    s = sids[i]
    if s not in scanners:
        scanners[s] = {"points": [], "profiles": [], "columns": []}
    scanners[s]["points"].append((xs[i], ys[i], zs[i]))
    scanners[s]["profiles"].append(profs[i])
    scanners[s]["columns"].append(cols[i])
print(f"Loaded and split {len(xs):,} points in {time.time() - t0:.1f} s")

fig, axes = plt.subplots(1, len(scanners), figsize=(15, 5), sharey=True)
if len(scanners) == 1:
    axes = [axes]
log_bins = np.logspace(-2, 3, 200)   # 0.01 mm to 1000 mm
tray = {}

for plot, s in zip(axes, sorted(scanners)):
    data = scanners[s]
    points = data["points"]

    grid = build_grid(data["profiles"], data["columns"])
    n_cells = len(grid) * len(grid[0])
    print(f"\n=== scanner {s}: {len(points):,} points | grid {len(grid)} rows x {len(grid[0])} columns"
          f" | {len(points) / n_cells:.1%} of cells filled")

    t0 = time.time()
    along, across = neighbour_distances(grid, points)
    print(f"  (distances computed in {time.time() - t0:.1f} s)")
    describe("next point on the same laser line", along)
    describe("same column, next scan line     ", across)

    n, median_z, spread = tray_patch(points)
    tray[s] = median_z
    print(f"  flat tray patch: {n:,} points, median z {median_z:.2f} mm, spread (std) {spread:.3f} mm")

    wall = sum(1 for (x, y, z) in points if x < WALL_X_MAX)
    low = sum(1 for (x, y, z) in points if z < OUTLIER_Z_MAX)
    print(f"  points in the wall region: {wall:,} | points far below the tray: {low:,}")

    plot.hist(along, bins=log_bins, histtype="step", log=True, label="same laser line")
    plot.hist(across, bins=log_bins, histtype="step", log=True, label="next scan line")
    plot.set_xscale("log")
    plot.set_xlabel("3D distance between grid neighbours [mm]")
    plot.set_title(f"scanner {s}")
    plot.legend()

if len(tray) == 2:
    print(f"\nSame tray patch seen by both scanners: height difference {tray[1] - tray[0]:+.2f} mm")

print("\nColour values (stored as 16-bit):")
for ch in ("red", "green", "blue", "nir"):
    values = v[ch]
    p50, p99, p999 = np.percentile(values, [50, 99, 99.9])
    print(f"  {ch:5s} median {p50:6.0f} | 99% below {p99:6.0f} | 99.9% below {p999:6.0f} | "
          f"max {values.max():6d} | zeros {(values == 0).sum():,}")

plt.tight_layout()
plt.savefig("results/figures/grid_neighbours.png", dpi=110)
print("\nSaved results/figures/grid_neighbours.png")
