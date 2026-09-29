"""First look at the PlantEye point cloud: attributes, grid structure, spacing, spectra.

Usage: python python/inspect_cloud.py data/scan.ply [--out results/figures]
"""
import argparse
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # render to file, no window needed
import matplotlib.pyplot as plt
import numpy as np
from plyfile import PlyData
from scipy.spatial import cKDTree

ap = argparse.ArgumentParser()
ap.add_argument("ply")
ap.add_argument("--out", default="results/figures")
args = ap.parse_args()
out_dir = Path(args.out)
out_dir.mkdir(parents=True, exist_ok=True)

t0 = time.time()
v = PlyData.read(args.ply)["vertex"].data   # numpy structured array: one row per point
print(f"Loaded {len(v):,} points in {time.time() - t0:.1f} s\n")

# 1) Range of every attribute. Tells you units, bit depth, and which fields look like indices.
print(f"{'field':<11}{'type':<8}{'min':>12}{'max':>12}{'mean':>12}{'unique':>11}")
for name in v.dtype.names:
    c = v[name]
    print(f"{name:<11}{str(c.dtype):<8}{c.min():>12.2f}{c.max():>12.2f}{c.mean():>12.2f}{len(np.unique(c)):>11,}")

print("\nFirst 5 rows:")
for row in v[:5]:
    print(row)

# 2) Per scanner: point count, profile/x_pos ranges, and whether the file is stored in scan order
print()
for s in np.unique(v["scanner_id"]):
    m = v["scanner_id"] == s
    p, xp = v["profile"][m], v["x_pos"][m]
    in_order = np.all(np.diff(p.astype(np.int64)) >= 0)
    print(f"scanner {s}: {m.sum():,} pts | profile {p.min()}..{p.max()} | "
          f"x_pos {xp.min()}..{xp.max()} | sorted by profile: {in_order}")

# 3) THE key test: is (scanner_id, profile, x_pos) unique per point?
#    Pack the three numbers into one 64-bit integer so np.unique can count distinct cells.
key = (v["scanner_id"].astype(np.int64) << 42) | (v["profile"].astype(np.int64) << 21) | v["x_pos"].astype(np.int64)
print(f"\nUnique (scanner, profile, x_pos) cells: {len(np.unique(key)):,} of {len(v):,} points")

# 4) Point spacing = distance from a point to its nearest neighbour (k-d tree query).
xyz = np.column_stack([v["x"], v["y"], v["z"]]).astype(np.float64)
t0 = time.time()
tree = cKDTree(xyz)
print(f"\nk-d tree built in {time.time() - t0:.1f} s")
rng = np.random.default_rng(0)
sample = rng.choice(len(xyz), size=min(200_000, len(xyz)), replace=False)
dist, _ = tree.query(xyz[sample], k=2)     # k=2 because the closest point is the point itself
nn = dist[:, 1]
print("NN distance percentiles 5/25/50/75/95/99 [mm]:",
      np.round(np.percentile(nn, [5, 25, 50, 75, 95, 99]), 3))

# 5) NDVI: living plants reflect NIR strongly and absorb red -> high value
red, nir = v["red"].astype(np.float64), v["nir"].astype(np.float64)
ndvi = (nir - red) / (nir + red + 1e-9)

# 6) Plots
sub = rng.choice(len(v), size=min(300_000, len(v)), replace=False)
lo, hi = np.percentile(ndvi, [2, 98])
fig, ax = plt.subplots(2, 3, figsize=(18, 11))
ax[0, 0].hist(v["z"], bins=300, log=True); ax[0, 0].set_title("z histogram (log count)")
ax[0, 1].hist(nn[nn < np.percentile(nn, 99)], bins=200); ax[0, 1].set_title("nearest-neighbour distance [mm]")
ax[0, 2].hist(ndvi, bins=200, log=True); ax[0, 2].set_title("NDVI histogram (log count)")
ax[1, 0].scatter(v["x"][sub], v["y"][sub], c=v["scanner_id"][sub], s=0.05, cmap="coolwarm")
ax[1, 0].set_title("top view, colour = scanner_id"); ax[1, 0].set_aspect("equal")
ax[1, 1].scatter(v["x"][sub], v["y"][sub], c=ndvi[sub], s=0.05, cmap="RdYlGn", vmin=lo, vmax=hi)
ax[1, 1].set_title("top view, colour = NDVI"); ax[1, 1].set_aspect("equal")
ax[1, 2].scatter(v["x"][sub], v["z"][sub], c=v["scanner_id"][sub], s=0.05, cmap="coolwarm")
ax[1, 2].set_title("side view (x vs z), colour = scanner_id"); ax[1, 2].set_aspect("equal")
plt.tight_layout()
fig_path = out_dir / "inspection.png"
plt.savefig(fig_path, dpi=110)
print(f"\nSaved {fig_path}")
