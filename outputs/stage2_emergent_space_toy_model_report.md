# Stage 2 — Emergent Space Toy Model Report

**Date:** 2026-06-10  
**Branch:** `feature/stage2-emergent-space-toy-model`  
**Commit hash:** `432796b`

## Changed files

| Path | Purpose |
|------|---------|
| `src/tdf_tq/space.py` | `SpatialBounds`, `SpatialSlice`, bounded neighbors |
| `src/tdf_tq/metrics.py` | L1/Manhattan/graph metrics, deterministic paths |
| `src/tdf_tq/__init__.py` | Stage 2 public exports |
| `tests/test_emergent_space.py` | Spatial region and slice tests |
| `tests/test_spatial_metrics.py` | Metric and path tests |
| `docs/stage2_emergent_space_toy_model.md` | Stage 2 scope, definitions, non-claims |
| `docs/roadmap.md` | Current stage updated to Stage 2 |
| `README.md` | Stage 2 summary and current stage |
| `outputs/stage1_temporal_packet_primitives_report.md` | Preflight: both Stage 1 commits recorded |
| `outputs/stage2_emergent_space_summary.json` | Deterministic example summary |
| `.gitignore` | Whitelist Stage 2 outputs |

## Tests run

```bash
python -m pytest -v
```

**Environment:** Python 3.12.10, pytest 9.0.3

## Test result summary

| Result | Count |
|--------|-------|
| Passed | 66 |
| Failed | 0 |
| Skipped | 0 |

Stage 2 additions (29 new tests) cover:

- `SpatialBounds` / `SpatialSlice` validation and enumeration
- In-bound neighbors, boundary determinism, zero-size slice
- L1/Manhattan/Euclidean spatial-only distances
- Unit edge length, graph steps, deterministic paths
- Triangle inequality examples; N_t ignored by spatial metrics

All 37 prior Stage 0–1 tests remain passing.

## Deterministic JSON output

**Path:** `outputs/stage2_emergent_space_summary.json`

Example: `(0,0,0,2)` → `(2,1,0,2)` at `l_q=1.5` yields L1=3, Manhattan=4.5, Euclidean≈3.354, graph steps=3, path `[(0,0,0),(1,0,0),(2,0,0),(2,1,0)]` at fixed `N_t=2`.

## Scientific interpretation

Stage 2 wires Stage 1 adjacency into a **finite count-lattice toy model** (maturity A–C):

- **SpatialSlice** enumerates emergent spatial indices at fixed **tau = N_t**.
- Spatial metrics use `(N_a, N_b, N_c)` only; **ΔN_t alone is temporal mismatch, not spatial separation**.
- Graph distance and deterministic paths are combinatorial scaffolding—not motion, fields, or validated geometry.

Stage 0 Euclidean distance remains a provisional flat toy limit; Stage 2 adds Manhattan/graph views consistent with unit-neighbor adjacency.

## Limitations

- **Finite rectangular regions only** — no unbounded space, topology, or curvature.
- **No temporal evolution** — paths are static graph constructions.
- **No gravity or Δτ forces** — temporal mismatch is not yet coupled to spatial structure.
- **Axis-ordered paths** — deterministic but not unique shortest paths in general.
- **No physical calibration** — `l_q` is a toy scale factor, not a measured length.
- **No validated TDF_TQ physics** — count lattice ≠ physical space.

## Next recommended stage

**Stage 3 — Delta tau gravity proxy:** explore distributed effective gravity from temporal mismatch while preserving conservative language and non-claims.
