# Stage 3A — Delta Tau Field Proxy Primitives Report

**Date:** 2026-06-10  
**Branch:** `feature/stage3a-delta-tau-field-proxy-primitives`  
**Commits:**
- `c192a16` — Stage 3A delta tau field proxy primitives
- `f35e97c` — Stage 3A output report

## Changed files

| Path | Purpose |
|------|---------|
| `src/tdf_tq/fields.py` | `DeltaTauField`, uniform/radial constructors |
| `src/tdf_tq/gravity_proxy.py` | Gradient, Laplacian, direction proxies |
| `src/tdf_tq/__init__.py` | Stage 3A public exports |
| `tests/test_delta_tau_fields.py` | Field validation and constructor tests |
| `tests/test_gravity_proxy.py` | Proxy behavior tests |
| `docs/stage3a_delta_tau_field_proxy_primitives.md` | Stage 3A scope and non-claims |
| `docs/roadmap.md` | Stage 3A current; Stage 3 full marked future |
| `README.md` | Stage 3A summary and caution |
| `outputs/stage2_emergent_space_toy_model_report.md` | Preflight: both Stage 2 commits |
| `outputs/stage3a_delta_tau_field_proxy_summary.json` | Deterministic example |
| `.gitignore` | Whitelist Stage 3A outputs |

## Tests run

```bash
python -m pytest -v
```

**Environment:** Python 3.12.10, pytest 9.0.3

## Test result summary

| Result | Count |
|--------|-------|
| Passed | 92 |
| Failed | 0 |
| Skipped | 0 |

Stage 3A additions (26 new tests) cover:

- `DeltaTauField` completeness, validation, statistics
- Uniform and radial toy profiles
- Zero/nonzero gradients, boundary differences
- Laplacian proxy at boundary/interior
- Direction proxy, normalization
- No physical constants in proxy module

All 66 prior Stage 0–2 tests remain passing.

## Deterministic JSON output

**Path:** `outputs/stage3a_delta_tau_field_proxy_summary.json`

Radial field on 3×3×1 lattice, center `(0,0,0)`, `base_tau=10`, `strength=2`, evaluated at `(1,1,0)`: tau=14, gradient `(2,2,0)`, direction `(-2,-2,0)`.

## Scientific interpretation

Stage 3A introduces a **toy field-analysis layer** (maturity A–C):

- **DeltaTauField** stores distributed **tau = N_t** on spatial count sites—Δτ between sites is count difference, not matter.
- Finite-difference **gradient** and **Laplacian proxy** are discrete count-lattice operators, not GR curvature.
- **gravity_like_direction_proxy** returns `-grad(tau)` as a direction precursor only—no G, mass, or force claim.

Distributed Δτ is explored as a possible **effective-gravity precursor**, not asserted as gravity.

## Limitations

- **No dynamics or evolution** — static fields only.
- **No Newtonian/GR recovery** — no comparison to 1/r or metric equations.
- **No physical units** — differences are in count indices, not meters or seconds.
- **Radial profile is arbitrary** — Manhattan toy template, not a potential derived from theory.
- **slice.N_t is reference-only** — field tau may differ from slice label.
- **No validated TDF_TQ physics** — proxies are scaffolding, not experimental gravity.

## Next recommended stage

**Stage 3B / Stage 3 (full):** compare field proxies to Newtonian/GR-like effective tests on selected toy configurations—still without overclaiming derivation or validation.
