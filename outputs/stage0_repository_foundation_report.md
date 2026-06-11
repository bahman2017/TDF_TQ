# Stage 0 — Repository Foundation Report

**Date:** 2026-06-10  
**Branch:** `feature/stage0-repository-foundation`  
**Commit hash:** `15bb4df`

## Changed files

| Path | Purpose |
|------|---------|
| `.gitignore` | Python/build/venv ignores; outputs whitelist |
| `LICENSE` | MIT license |
| `README.md` | Project mission, install, tests, caution |
| `pyproject.toml` | Modern packaging (`tdf-tq`, Python ≥3.10, pytest dev) |
| `src/tdf_tq/__init__.py` | Public API exports |
| `src/tdf_tq/constants.py` | Symbolic constants, `working_speed_limit` |
| `src/tdf_tq/packets.py` | Frozen `TemporalPacket` dataclass |
| `src/tdf_tq/distances.py` | `delta_tau`, spatial deltas, emergent Euclidean distance |
| `tests/test_imports.py` | Import smoke tests |
| `tests/test_locked_definitions.py` | Locked-definition alignment tests |
| `docs/canonical_reference.md` | Locked definitions, maturity hierarchy, non-claims |
| `docs/roadmap.md` | Stages 0–10 roadmap |
| `docs/scientific_boundaries.md` | Scope and language conventions |
| `outputs/README.md` | Outputs directory purpose |

## Tests run

```bash
python -m pytest -v
```

**Environment:** Python 3.12.10, pytest 9.0.3

## Test result summary

| Result | Count |
|--------|-------|
| Passed | 17 |
| Failed | 0 |
| Skipped | 0 |

All required Stage 0 checks passed:

- Package imports
- `TemporalPacket` accepts valid non-negative integers
- `TemporalPacket` rejects negative values
- `tau == N_t`
- `delta_tau == ΔN_t`
- Emergent distance `(0,0,0,N_t)` → `(1,0,0,N_t)` equals `l_q`
- `working_speed_limit(2, 4) == 0.5`
- `working_speed_limit` rejects `t_q <= 0`

## Scientific interpretation

Stage 0 establishes **repository scaffolding only** (maturity level A: locked definitions encoded in docs and minimal types). The code implements:

- **Temporal packets** with `N_t` as local progression count `tau`.
- **Temporal mismatch** `Δτ` as a count difference, explicitly not equated to matter.
- **Emergent spatial distance** as a provisional Euclidean toy metric from spatial count differences scaled by `l_q`.
- **Working speed limit** `c = l_q / t_q` as a symbolic relation without physical calibration.

No gravitational, quantum, or particle physics is implemented or claimed.

## Limitations

- **No physical units or measured constants** — `l_q` and `t_q` are symbolic/toy defaults only.
- **Euclidean emergent distance** is a flat toy limit, not curved spacetime or GR.
- **Python ≥3.10 required** — system default 3.9 will not install the package as specified.
- **No simulation or dynamics** — packets are static data containers; no evolution rules yet.
- **No validated TDF_TQ physics** — all content is working definitions and test scaffolding.

## Next recommended stage

**Stage 1 — Temporal packet primitives:** extend packet types, invariants, and neighborhood relations needed for the emergent space toy model (Stage 2).
