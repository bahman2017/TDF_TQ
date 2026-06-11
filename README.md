# TDF_TQ — Temporal Quantum Foundation

Extension of the Time Delay Field (TDF) program exploring whether a **time-first** model can generate emergent space, effective gravity, stable particle-like structures, and later QM-like behavior.

**Current stage:** Stage 4A — Stable localized Delta tau packet-structure search.

## Mission

Build deterministic, testable scaffolding around locked temporal primitives (`t_q`, `N_t`, `Δτ`) and emergent spatial packet counts—without claiming derived GR, QM, Standard Model particles, or validated fundamental constants.

## Stage 4A — Stable localized structure search

Stage 4A searches for **localized stable packet-structure candidates** on the 5D toy state-space `(N_a, N_b, N_c, N_t)` plus update-history index `k`:

- **Active support** above a fixed baseline (not full lattice support)
- Deterministic seed patterns (single peak, plus-cross, compact block)
- Conservative pairwise relaxation evolution
- `LocalizedCandidateCriteria` → PASS / INCONCLUSIVE / FAIL

**Passing Stage 4A is not an electron-like candidate yet.** Results are toy candidates only—not particles, not electrons, not validated physics.

## Stage 3B — 5D packet-structure history

Field evolution, structure histories, persistence diagnostics on full packet states.

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
- [Stage 4A structure search](docs/stage4a_stable_localized_delta_tau_structure_search.md)

## Scientific caution

This repository contains **working definitions and toy-model code only**. It does **not**:

- derive general relativity, Newtonian gravity, or quantum mechanics;
- identify electrons, photons, mass, charge, spin, **ħ**, or **α**;
- provide experimental validation;
- claim that Stage 4A candidates are particles or electron-like structures.

FAIL and INCONCLUSIVE search outcomes are scientifically acceptable. Read all results through the claim maturity hierarchy in the canonical reference.

## License

MIT — see [LICENSE](LICENSE).
