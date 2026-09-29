# Convenience targets. Everything here can also be run by hand (see README "Build & run").
#   make setup     create Python venv + install deps
#   make build     configure + compile the C++ tool (Release)
#   make inspect   run the data inspection script        (DATA=path/to/scan.ply)
#   make run       run the C++ reconstruction             (DATA=..., OUT=...)
#   make test      smoke test on a small synthetic cloud (no real data needed)

DATA   ?= data/scan.ply
OUT    ?= out/mesh.ply
PYTHON ?= python3.12
VENV   := .venv
PY     := $(VENV)/bin/python

.PHONY: setup build inspect run test clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r python/requirements.txt

build:
	cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
	cmake --build build -j

inspect:
	$(PY) python/inspect_cloud.py $(DATA)

run: build
	@mkdir -p $(dir $(OUT))
	./build/reconstruct $(DATA) $(OUT)

test: build
	@mkdir -p out
	$(PY) tests/make_synthetic_ply.py out/synthetic.ply
	./build/reconstruct out/synthetic.ply out/synthetic_mesh.ply

clean:
	rm -rf build out
