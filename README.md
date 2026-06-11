# TDF_TQ — Temporal Quantum Foundation

Extension of the Time Delay Field (TDF) program exploring whether a **time-first** model can generate emergent space, effective gravity, stable particle-like structures, and later QM-like behavior.

**Current stage:** Stage 2 — Emergent space toy model.

## Mission

Build deterministic, testable scaffolding around locked temporal primitives (`t_q`, `N_t`, `Δτ`) and emergent spatial packet counts—without claiming derived GR, QM, Standard Model particles, or validated fundamental constants.

## Stage 2 — Emergent space toy model

Stage 2 connects Stage 1 neighborhood primitives into a **finite spatial count lattice**:

- `SpatialSlice` — rectangular regions of `(N_a, N_b, N_c)` at fixed `N_t`
- Graph adjacency via spatial unit neighbors within bounds
- Provisional metrics: Manhattan/graph distance and Stage 0 Euclidean toy distance, both from spatial counts only

`N_t` controls **tau** (local temporal progression). Spatial distance does **not** use `N_t`; a change in `N_t` alone is temporal mismatch, not spatial separation.

## Install

```bash
git clone https://github.com/bahman2017/TDF_TQ.git
cd TDF_TQ
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run tests

```bash
python -m pytest
```

## Documentation

- [Canonical reference](docs/canonical_reference.md) — locked definitions and claim maturity
- [Roadmap](docs/roadmap.md) — staged development plan
- [Scientific boundaries](docs/scientific_boundaries.md) — what this repo is and is not
- [Stage 2 emergent space](docs/stage2_emergent_space_toy_model.md) — count lattice and provisional metrics

## Scientific caution

This repository contains **working definitions and toy-model code only**. It does **not**:

- derive general relativity or quantum mechanics;
- derive electrons, photons, mass, charge, spin, **ħ**, or **α**;
- provide experimental validation;
- claim that count-lattice graph distance is physical space.

Read all results through the claim maturity hierarchy in the canonical reference. Particle and radiation language should use **“candidate”** until stronger evidence exists.

## License

MIT — see [LICENSE](LICENSE).
