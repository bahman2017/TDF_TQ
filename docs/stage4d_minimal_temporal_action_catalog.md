# Stage 4D — Minimal Temporal Action Catalog

## Purpose

Stage 4D integrates the Stage 4C **FRAGILE_TOY_ARTIFACT** verdict and resets search discipline around a **minimal temporal Action catalog** with diagnostics only—no stable candidate search and no tuning of legacy cohesion rules.

## Stage 4C integration

Stage 4C showed Stage 4B nontrivial labels under `conservative_centered_cohesion` are fragile toy artifacts, not robust structures. Stage 4D therefore:

- Does **not** promote cohesion as a preferred physical candidate
- Includes cohesion only as a **legacy** entry with explicit warning
- Focuses primary catalog on Actions A0–A4 using allowed TDF ingredients only

## Primary Action catalog

| ID | Role |
|----|------|
| A0 | Identity control (trivial) |
| A1 | Pairwise relaxation (spreading baseline) |
| A2 | Thresholded relaxation with one-step memory |
| A3 | Local temporal inertia (no anchor) |
| A4 | Finite-propagation limited diffusion |

## Legacy rule

`LEGACY_conservative_centered_cohesion` — arbitrary retention heuristic from Stage 4B/4C; **not physical binding**. Excluded from primary benchmark matrix.

## Diagnostics (not physics)

Per Action × neutral seed: total tau before/after, max local change, support size trajectory, centroid drift, localization ratio, propagation radius, oscillation indicator, unchanged-history flag, global-anchor usage.

## Verdict categories

- **ACTION_CATALOG_READY** — boundaries pass, catalog complete, deterministic diagnostics
- **ACTION_CATALOG_INCOMPLETE** — missing pieces, no overclaim
- **BOUNDARY_FAIL** — forbidden physics encoded
- **TEST_FAIL** — deterministic tests fail

## Explicit non-claims

No GR, QM, particle, electron, photon, mass, charge, spin, hbar, alpha, or validated physics.

## Next stage

Stage 4 Emergent Structure Survey using primary Actions A0–A4 only.
