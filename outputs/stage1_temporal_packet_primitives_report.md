# Stage 1 — Temporal Packet Primitives Report

**Date:** 2026-06-10  
**Branch:** `feature/stage1-temporal-packet-primitives`  
**Commits:**
- `8b13724` — Stage 1 temporal packet primitives
- `27b2ee7` — Stage 1 output report

## Changed files

| Path | Purpose |
|------|---------|
| `src/tdf_tq/relations.py` | `PacketDelta`, `packet_delta`, `translate_packet`, equality checks |
| `src/tdf_tq/neighborhoods.py` | Spatial unit neighbors, axis detection |
| `src/tdf_tq/__init__.py` | Public exports for Stage 1 primitives |
| `tests/test_packet_relations.py` | Relation and delta tests |
| `tests/test_packet_neighborhoods.py` | Neighborhood adjacency tests |
| `docs/stage1_temporal_packet_primitives.md` | Stage 1 scope, definitions, non-claims |
| `docs/roadmap.md` | Current stage updated to Stage 1 |
| `outputs/stage0_repository_foundation_report.md` | Preflight: both Stage 0 commits recorded |
| `.gitignore` | Whitelist for Stage 1 output report |

## Tests run

```bash
python -m pytest -v
```

**Environment:** Python 3.12.10, pytest 9.0.3

## Test result summary

| Result | Count |
|--------|-------|
| Passed | 37 |
| Failed | 0 |
| Skipped | 0 |

Stage 1 additions (20 new tests) cover:

- `PacketDelta` signed integers; rejects bool/non-int
- `packet_delta` component-wise differences and antisymmetry
- `translate_packet` success and negative-count rejection
- `same_spatial_position` / `same_temporal_layer` independence
- Origin neighbors (+3 axes only); interior neighbors (6)
- Diagonal and temporal-layer rejection for unit neighbors
- `spatial_unit_axis` for valid/invalid pairs

All 17 Stage 0 tests remain passing.

## Scientific interpretation

Stage 1 adds **maturity level A–C count primitives** on top of Stage 0:

- **PacketDelta** encodes signed differences between packets; `delta_tau` property preserves **Δτ = ΔN_t** without equating mismatch to matter.
- **translate_packet** applies deltas with non-negativity invariants—algebra on counts, not physical motion.
- **Spatial unit neighbors** define adjacency on `(N_a, N_b, N_c)` at fixed `N_t`—a discrete graph scaffold for emergent space, not validated geometry or dynamics.

No gravity, QM, particle candidates, or calibrated constants are introduced.

## Limitations

- **No temporal evolution** — count comparisons only; no simulation timestep or dynamics.
- **3D count lattice only** — no topology, curvature, or metric beyond Stage 0 Euclidean toy distance.
- **Boundary omission** — neighbors below zero are dropped, not wrapped or reflected.
- **No physical interpretation** — adjacency is combinatorial; `l_q` scaling from Stage 0 is not wired into neighborhoods yet.
- **No validated TDF_TQ physics** — all behavior is deterministic scaffolding.

## Next recommended stage

**Stage 2 — Emergent space toy model:** connect neighborhoods to provisional spatial structure and metrics using the primitives defined here.
