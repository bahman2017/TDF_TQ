# TDF_TQ — Temporal Quantum Foundation

Extension of the Time Delay Field (TDF) program exploring whether a **time-first** model can generate emergent space, effective gravity, stable particle-like structures, and later QM-like behavior.

**Current stage:** Stage 4B — Candidate robustness and nontrivial-stability tests.

## Mission

Build deterministic, testable scaffolding around locked temporal primitives (`t_q`, `N_t`, `Δτ`) and emergent spatial packet counts—without claiming derived GR, QM, Standard Model particles, or validated fundamental constants.

## Stage 4B — Candidate robustness and nontrivial-stability

Stage 4B distinguishes trivial stability (identity controls), spreading (relaxation), and possible nontrivial toy stability under:

- Deterministic perturbation tests
- `conservative_centered_cohesion` toy retention rule (not physics)
- Classifications: `TRIVIAL_STABLE_CONTROL`, `NONTRIVIAL_STABLE_TOY_CANDIDATE`, `INCONCLUSIVE`, `FAIL`

**Stage 4B does not identify electron-like candidates.** A nontrivial-stable toy label means study further in Stage 4C/5 criteria only—not a particle claim.

## Stage 4A — Stable localized structure search

Active-support candidate search with PASS / INCONCLUSIVE / FAIL verdicts. Stage 4A found 0 PASS under default relaxation (3 INCONCLUSIVE).

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
- [Stage 4B robustness](docs/stage4b_candidate_robustness_nontrivial_stability.md)

## Scientific caution

This repository contains **working definitions and toy-model code only**. It does **not** derive GR, QM, electrons, mass, charge, spin, **ħ**, or **α**, or provide experimental validation. FAIL, INCONCLUSIVE, and weak nontrivial toy labels are acceptable scientific outcomes.

## License

MIT — see [LICENSE](LICENSE).
