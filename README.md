# TDF_TQ — Temporal Quantum Foundation

Extension of the Time Delay Field (TDF) program exploring whether a **time-first** model can generate emergent space, effective gravity, stable particle-like structures, and later QM-like behavior.

**Current stage:** Stage 3B — 5D packet-structure history and stability primitives.

## Mission

Build deterministic, testable scaffolding around locked temporal primitives (`t_q`, `N_t`, `Δτ`) and emergent spatial packet counts—without claiming derived GR, QM, Standard Model particles, or validated fundamental constants.

## Stage 3B — 5D packet-structure history and stability

Stage 3B extends Stage 3A with **history-based diagnostics** over full packet structures `E = (N_a, N_b, N_c, N_t)`:

- **5D toy state-space:** four packet counts plus discrete update-history index `k` — **not physical 5D spacetime**
- `PacketStructure`, `StructureHistory` — persistence and localization over toy update series
- Conservative pairwise relaxation — integer toy evolution with exact total-tau bookkeeping (not physical energy)
- Quasi-stability and persistence scores — search tools only

**Electron-like candidates are not tested yet.** No particles, mass, charge, spin, or QM claims.

## Stage 3A — Delta tau field proxy primitives

Distributed tau fields, finite-difference gradient/Laplacian proxies, gravity-**like** direction proxy (`-grad tau`) — count-lattice scaffolding only, not derived gravity.

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
- [Stage 3B history & stability](docs/stage3b_5d_packet_structure_history_stability.md)

## Scientific caution

This repository contains **working definitions and toy-model code only**. It does **not**:

- derive general relativity, Newtonian gravity, or quantum mechanics;
- derive electrons, photons, mass, charge, spin, **ħ**, or **α**;
- provide experimental validation;
- claim that toy field evolution is physical dynamics;
- claim that 5D toy state-space is physical spacetime.

Read all results through the claim maturity hierarchy in the canonical reference. Particle language should use **“candidate”** until stronger evidence exists.

## License

MIT — see [LICENSE](LICENSE).
