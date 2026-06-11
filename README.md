# TDF_TQ — Temporal Quantum Foundation

Extension of the Time Delay Field (TDF) program exploring whether a **time-first** model can generate emergent space, effective gravity, stable particle-like structures, and later QM-like behavior.

**Current stage:** Stage 3A — Delta tau field proxy primitives.

## Mission

Build deterministic, testable scaffolding around locked temporal primitives (`t_q`, `N_t`, `Δτ`) and emergent spatial packet counts—without claiming derived GR, QM, Standard Model particles, or validated fundamental constants.

## Stage 3A — Delta tau field proxy primitives

Stage 3A assigns **distributed tau = N_t** values on the Stage 2 spatial count lattice and computes toy finite-difference quantities:

- `DeltaTauField` — tau per spatial site `(N_a, N_b, N_c)`
- Gradient, Laplacian-like roughness, and **gravity-like direction proxy** (`-grad tau`)

These are **count-lattice analysis helpers only**—not derived gravity, not GR curvature, and not physical force. Distributed Δτ is explored as a possible **effective-gravity precursor**, not asserted as gravity or matter.

## Stage 2 — Emergent space toy model

- `SpatialSlice` — rectangular regions at a reference `N_t`
- Graph adjacency and provisional spatial metrics from counts only

Spatial distance does **not** use field tau; a change in `N_t` alone is temporal mismatch, not spatial separation.

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
- [Stage 3A field proxies](docs/stage3a_delta_tau_field_proxy_primitives.md) — delta-tau fields and toy proxies

## Scientific caution

This repository contains **working definitions and toy-model code only**. It does **not**:

- derive general relativity or Newtonian gravity;
- derive quantum mechanics;
- derive electrons, photons, mass, charge, spin, **ħ**, or **α**;
- provide experimental validation;
- claim that gravity-like proxies are real gravitational force.

Read all results through the claim maturity hierarchy in the canonical reference. Particle and radiation language should use **“candidate”** until stronger evidence exists.

## License

MIT — see [LICENSE](LICENSE).
