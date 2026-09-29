# 3D Surface Reconstruction – PlantEye Point Cloud

Converts a dual-PlantEye point cloud (PLY) of a plant tray into a triangle mesh (PLY).

<!-- TODO (write last): 2–3 sentences. What the pipeline does, the main idea, and the headline result
     (e.g. mesh size, runtime, median point-to-mesh error). -->

**Status:** work in progress.

## Build & run

Requirements: a C++17 compiler, CMake ≥ 3.16. Python 3.10–3.12 is only needed for analysis scripts.
Tested on macOS (Apple clang) and Ubuntu (GCC); CI builds both on every push.

```bash
# C++ tool (no third-party install needed; the PLY library is vendored)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
./build/reconstruct data/scan.ply out/mesh.ply

# Python analysis environment (optional)
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r python/requirements.txt
python python/inspect_cloud.py data/scan.ply
```

Shortcut: `make build`, `make run DATA=data/scan.ply`, `make inspect`, `make test`.

## Repository layout

```
cpp/src/            C++ reconstruction tool (main deliverable)
python/             data inspection, prototypes, baselines, evaluation
tests/              synthetic test data generator (used by CI)
third_party/happly  single-header PLY reader/writer (MIT)
results/            metrics and figures referenced in this README
docs/notes.md       working log: observations, decisions, timings
data/               input point cloud goes here (git-ignored)
```

## 1. Data analysis
<!-- TODO: what the scan contains, sensor setup (two scanners), units, point spacing, grid structure,
     noise/outliers, spectral channels. Include figure(s) from results/figures. -->

## 2. Approach
<!-- TODO: pipeline stages, and WHY each method was chosen for this data. -->

## 3. Parameters & design decisions
<!-- TODO: table of parameters, value, and how the value was derived (e.g. "3× median NN spacing"). -->

## 4. Evaluation
<!-- TODO: metrics (point-to-mesh distance, triangle count, components, runtime) and the comparison
     against baselines (e.g. Poisson / Ball Pivoting). -->

| Method | Triangles | Components | Median dist [mm] | 95th pct [mm] | Runtime [s] |
|--------|-----------|------------|------------------|---------------|-------------|
|        |           |            |                  |               |             |

## 5. Limitations & failure cases
<!-- TODO -->

## 6. Future work
<!-- TODO -->

## Use of AI tools
<!-- TODO: short and honest — what AI assistants were used for, and how outputs were verified. -->
