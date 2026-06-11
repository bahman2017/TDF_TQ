# Stage 4C — Fragility Boundary and Negative-Result Audit Report

**Date:** 2026-06-10  
**Implementation branch:** `feature/stage4c-fragility-boundary-negative-result-audit`  
**Implementation commit hash:** `588817d`  
**Base branch:** `feature/stage0-repository-foundation`

## Executive summary

Stage 4C re-audited the two Stage 4B nontrivial toy labels (`compact_2x2_corner`, `plus_cross_center` under `conservative_centered_cohesion`) under stricter criteria, larger grids, expanded perturbations, and alternate cohesion anchors.

**Verdict: `FRAGILE_TOY_ARTIFACT`**

Neither candidate meets robust toy criteria. Stage 4B’s sparse unperturbed nontrivial labels do not survive stricter combined criteria with perturbation stress. This is acceptable negative evidence—not a failure of the program.

## What Stage 4C tested

| Dimension | Settings |
|-----------|----------|
| Candidates | `compact_2x2_corner`, `plus_cross_center` + `conservative_centered_cohesion` |
| Grid sizes | 3×3×1 native; 5×5×1 centered and off-center embeddings |
| Steps | 3, 5, 8, 13 |
| Criteria profiles | stage4b_original, stricter_localization, stricter_overlap, stricter_drift, combined_strict |
| Perturbations | single-tau, two-step (max 24), boundary-adjacent |
| Anchors | centroid, grid_center, shift_plus_a, shift_minus_b |

## Why this was the correct next step

Stage 4B reported 2 unperturbed `NONTRIVIAL_STABLE_TOY_CANDIDATE` assessments with robustness ratio ≈ 0.077 (1/13). That pattern signals possible finite-size, threshold, or anchor artifacts—not robust structure. Stage 4C deliberately applies broader stress without tuning new rules to force stability.

## Grid-size results (combined_strict)

| Seed | Grid | Placement | Passes (steps 3/5/8/13) |
|------|------|-----------|-------------------------|
| compact_2x2_corner | 3×3×1 | native | 2/4 |
| compact_2x2_corner | 5×5×1 | centered | 2/4 |
| compact_2x2_corner | 5×5×1 | off_center | 2/4 |
| plus_cross_center | 3×3×1 | native | 0/4 |
| plus_cross_center | 5×5×1 | centered | 0/4 |
| plus_cross_center | 5×5×1 | off_center | 0/4 |

**Observation:** `compact_2x2_corner` passes combined_strict on both grid sizes at some step counts, but not all. `plus_cross_center` fails combined_strict entirely. Neither shows robust multi-step stability under strict criteria.

## Criteria profile results (3×3×1, all steps)

| Seed | stage4b_original | stricter_localization | stricter_overlap | stricter_drift | combined_strict |
|------|------------------|----------------------|------------------|----------------|-----------------|
| compact_2x2_corner | 4/4 | 3/4 | 3/4 | 3/4 | 2/4 |
| plus_cross_center | 1/4 | 1/4 | 1/4 | 1/4 | 0/4 |

**Observation:** Stricter profiles reduce pass counts. `plus_cross_center` passes only under original Stage 4B criteria at one step count—consistent with threshold artifact behavior.

## Perturbation results (combined_strict, steps=3)

| Seed | Type | Unperturbed pass | Perturbation pass fraction |
|------|------|------------------|----------------------------|
| compact_2x2_corner | single_tau | no | 0.000 |
| compact_2x2_corner | two_step | no | 0.000 |
| compact_2x2_corner | boundary_adjacent | no | 0.000 |
| plus_cross_center | single_tau | no | 0.000 |
| plus_cross_center | two_step | no | 0.167 |
| plus_cross_center | boundary_adjacent | no | 0.000 |

**Observation:** No candidate achieves ≥50% perturbation pass fraction. Unperturbed combined_strict passes are absent at the perturbation audit step count (3). Stage 4B fragility is confirmed under expanded perturbation suites.

## Anchor-dependence results (combined_strict)

| Seed | Anchor | Passes (steps 3/5/8/13) |
|------|--------|-------------------------|
| compact_2x2_corner | centroid | 2/4 |
| compact_2x2_corner | grid_center | 2/4 |
| compact_2x2_corner | shift_plus_a | 2/4 |
| compact_2x2_corner | shift_minus_b | 2/4 |
| plus_cross_center | all anchors | 0/4 |

**Observation:** For `compact_2x2_corner`, alternate anchors yield identical pass counts on this grid—no single-anchor dependence detected, but passes remain sparse and fail perturbation stress.

## Negative controls

| Control | Classification | Nontrivial? |
|---------|----------------|-------------|
| identity | TRIVIAL_STABLE_CONTROL | no |
| conservative_pairwise_relaxation | INCONCLUSIVE | no |
| shuffled_excess_field | FAIL | no |
| identity_long_steps | TRIVIAL_STABLE_CONTROL | no |

Controls behave as required: identity remains trivial; relaxation spreads; shuffled fields are not promoted; unchanged histories are not nontrivial.

## Negative-result interpretation

Stage 4B’s apparent nontrivial stability was **fragile**:

- Perturbation suites fail under combined_strict criteria
- `plus_cross_center` fails strict criteria entirely
- `compact_2x2_corner` shows limited strict passes without perturbation robustness
- No candidate qualifies as `ROBUST_TOY_CANDIDATE`

This supports treating Stage 4B nontrivial labels as **toy-model artifacts** pending genuinely robust evidence—not as particle-like structure.

---

### Observations

- Stage 4B best candidate (`compact_2x2_corner`) retains some strict-criteria passes on 3×3 and 5×5 grids at selected step counts
- All perturbation assessments fall well below the 50% robust threshold
- `plus_cross_center` passes only under original Stage 4B criteria at one step

### Toy-model interpretation

The conservative centered cohesion rule can retain localized excess on small grids under loose criteria, but that retention does not survive as a robust, perturbation-stable toy structure under Stage 4C stress. The cohesion rule remains an arbitrary retention heuristic—not physical binding.

### Scientific limitations

- Audit thresholds are deterministic but not experimentally calibrated
- Grid sizes remain tiny (3×3 and 5×5)
- Cohesion is a toy rule, not derived physics
- Negative or fragile outcomes are acceptable and preferred over tuned positives

**No particle, electron, photon, mass, charge, spin, energy, hbar, alpha, QM, GR, or validated physics claim is made.**

## Deterministic JSON output

**Path:** `outputs/stage4c_fragility_boundary_negative_result_audit_summary.json`

## Next recommended stage

Document the negative-result boundary. Proceed to Stage 5 exploratory criteria design only if future work finds robust toy evidence; otherwise refine search space without overclaiming.
