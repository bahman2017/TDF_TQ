# Stage 4D — Minimal Temporal Action Catalog Report

**Date:** 2026-06-10  
**Implementation branch:** `feature/stage4d-minimal-temporal-action-catalog`  
**Implementation commit hash:** `445db9b`  
**Base branch:** `feature/stage0-repository-foundation` (Stage 4C merged at `60126f1`)

## Executive summary

Stage 4D merges Stage 4C’s **FRAGILE_TOY_ARTIFACT** verdict into search discipline and ships a **minimal temporal Action catalog** (A0–A4) with deterministic diagnostics only. Legacy `conservative_centered_cohesion` is retained with warning but excluded from the primary benchmark matrix.

**Verdict: `ACTION_CATALOG_READY`**

## Stage 4C merge

| Item | Value |
|------|-------|
| Integration commit | `60126f1` |
| Stage 4C verdict | `FRAGILE_TOY_ARTIFACT` |
| Stage 4B best | `compact_2x2_corner` + cohesion |
| Robustness ratio | ≈ 0.077 |

Stage 4D does **not** tune cohesion to recover nontrivial labels.

## Primary Action catalog

| ID | Label | Conserves total τ | Global anchor |
|----|-------|-------------------|---------------|
| A0 | Identity control | yes | no |
| A1 | Pairwise relaxation | yes | no |
| A2 | Thresholded relaxation + memory | yes | no |
| A3 | Local temporal inertia | yes | no |
| A4 | Finite-propagation limited diffusion | yes | no |

## Legacy rule status

| ID | Status |
|----|--------|
| LEGACY_conservative_centered_cohesion | Arbitrary retention heuristic; not physical binding; excluded from primary benchmark |

## Roadmap correction

Corrected near-term sequence: Stage 3 Fundamental Temporal Actions → Stage 4 Emergent Structure Survey → … → Stage 10 Documentation.

Deferred legacy wording: electron-like criteria, photon-like candidate, near-term particle derivation targets.

## Diagnostics summary

150 primary-catalog runs (5 Actions × 5 neutral seeds × 6 step counts on 3×3 grid).

Observations:

- A0 unchanged on all seeds (trivial control)
- A1–A4 conserve total τ on tested seeds
- A1 shows expected spreading (support size increases on peaked seeds)
- A4 limits to one neighbor transfer per step
- No primary Action uses global anchor or particle labels

## Boundary checks

All primary Actions pass ingredient/boundary metadata checks. Non-legacy Actions do not use global anchors.

## Scientific interpretation

Stage 4C demonstrated that cohesion-based nontrivial labels are fragile artifacts. Stage 4D resets discipline: future structure surveys should use Actions A0–A4 built from local τ, Δτ, neighbors, finite propagation, and optional memory—inertia only. Spreading under A1 remains the dominant nontrivial behavior; localization without anchors is weak and not promoted as structure evidence.

## Limitations

- Catalog/diagnostics only; no candidate search
- 3×3 grid benchmark
- Legacy cohesion documented but not recommended

## Explicit non-claims

**No GR, QM, particle, electron, photon, mass, charge, spin, hbar, alpha, or validated physics claim is made.**

## Deterministic JSON

**Path:** `outputs/stage4d_minimal_temporal_action_catalog_summary.json`

## Next recommended stage

Stage 4 Emergent Structure Survey using primary Actions A0–A4 only.
