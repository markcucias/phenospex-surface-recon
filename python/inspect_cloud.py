"""First look at the point cloud: attribute ranges, scanners, grid uniqueness, point spacing, NDVI.

Usage: python python/inspect_cloud.py data/scan.ply [--out results/figures]
"""
import argparse
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from plyfile import PlyData
from scipy.spatial import cKDTree

parser = argparse.ArgumentParser()
parser.add_argument("ply")
parser.add_argument("--out", default="results/figures")
args = parser.parse_args()
out_dir = Path(args.out)
out_dir.mkdir(parents=True, exist_ok=True)

t0 = time.time()
v = PlyData.read(args.ply)["vertex"].data
print(f"Loaded {len(v):,} points in {time.time() - t0:.1f} s\n")

# Range of every attribute
print(f"{'field':<11}{'type':<8}{'min':>12}{'max':>12}{'mean':>12}{'unique':>11}")
for name in v.dtype.names:
    c = v[name]
    print(f"{name:<11}{str(c.dtype):<8}{c.min():>12.2f}{c.max():>12.2f}{c.mean():>12.2f}{len(np.unique(c)):>11,}")

print("\nFirst 5 rows:")
for row in v[:5]:
    print(row)

# Per scanner: point count, ranges, and whether the file is stored in scan order
print()
for s in np.unique(v["scanner_id"]):
    mine = v[v["scanner_id"] == s]
    profile = mine["profile"].astype(np.int64)
    in_order = np.all(np.diff(profile) >= 0)
    print(f"scanner {s}: {len(mine):,} pts | profile {profile.min()}..{profile.max()} | "
          f"x_pos {mine['x_pos'].min()}..{mine['x_pos'].max()} | sorted by profile: {in_order}")

# Does every point have its own (scanner, profile, x_pos) cell?
cells = np.column_stack([v["scanner_id"], v["profile"], v["x_pos"]]).astype(np.int64)
print(f"\nUnique (scanner, profile, x_pos) cells: {len(np.unique(cells, axis=0)):,} of {len(v):,} points")

# Point spacing: distance to the nearest neighbour, for a random sample of points
xyz = np.column_stack([v["x"], v["y"], v["z"]]).astype(np.float64)
tree = cKDTree(xyz)
rng = np.random.default_rng(0)
sample = rng.choice(len(xyz), size=min(200_000, len(xyz)), replace=False)
dist, _ = tree.query(xyz[sample], k=2)   # k=2: the closest point is the point itself
nn = dist[:, 1]
print("NN distance percentiles 5/25/50/75/95/99 [mm]:",
      np.round(np.percentile(nn, [5, 25, 50, 75, 95, 99]), 3))

# NDVI: plants reflect a lot of NIR and little red, so they get high values
red = v["red"].astype(np.float64)
nir = v["nir"].astype(np.float64)
ndvi = (nir - red) / (nir + red + 1e-9)

# Plots (scatter plots use a random subset to stay fast)
sub = rng.choice(len(v), size=min(300_000, len(v)), replace=False)
x, y, z, scanner = v["x"][sub], v["y"][sub], v["z"][sub], v["scanner_id"][sub]
lo, hi = np.percentile(ndvi, [2, 98])

fig, ax = plt.subplots(2, 3, figsize=(18, 11))

ax[0, 0].hist(v["z"], bins=300, log=True)
ax[0, 0].set_title("z histogram (log count)")

ax[0, 1].hist(nn[nn < np.percentile(nn, 99)], bins=200)
ax[0, 1].set_title("nearest-neighbour distance [mm]")

ax[0, 2].hist(ndvi, bins=200, log=True)
ax[0, 2].set_title("NDVI histogram (log count)")

ax[1, 0].scatter(x, y, c=scanner, s=0.05, cmap="coolwarm")
ax[1, 0].set_title("top view, colour = scanner_id")

ax[1, 1].scatter(x, y, c=ndvi[sub], s=0.05, cmap="RdYlGn", vmin=lo, vmax=hi)
ax[1, 1].set_title("top view, colour = NDVI")

ax[1, 2].scatter(x, z, c=scanner, s=0.05, cmap="coolwarm")
ax[1, 2].set_title("side view (x vs z), colour = scanner_id")

for a in (ax[1, 0], ax[1, 1], ax[1, 2]):
    a.set_aspect("equal")

plt.tight_layout()
fig_path = out_dir / "inspection.png"
plt.savefig(fig_path, dpi=110)
print(f"\nSaved {fig_path}")
