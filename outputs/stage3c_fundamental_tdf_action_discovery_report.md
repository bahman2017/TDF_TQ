# Stage 3C — Fundamental TDF Action Discovery Report

**Date:** 2026-06-10  
**Implementation branch:** `feature/stage3c-fundamental-tdf-action-discovery`  
**Implementation commit hash:** `09a4c39`  
**Base branch:** `feature/stage0-repository-foundation`

## Executive summary

Stage 3C implements a deterministic conservative **Action-discovery framework** with seven toy Actions (A0–A6), eighteen outcome metrics, eight benchmark seeds, and multi-tag behavior classification across 3×3×1 and 5×5×1 grids.

**Verdict: `PASS_ACTION_CATALOG_READY`**

Multiple Actions show nontrivial toy behavior (spreading, localization candidates, finite-speed patterns, geometry/phase diagnostics) without overclaiming GR, QM, or particle derivation.

## Why Stage 3C was inserted before further particle-candidate work

Stage 4B found sparse unperturbed nontrivial labels under `conservative_centered_cohesion` with robustness ratio ≈ 0.077—fragile toy artifacts under perturbation. Before continuing structure or particle-candidate exploration, Stage 3C asks which **minimal temporal Actions** derived from τ = N_t primitives naturally produce spreading, smoothing, localization, propagation, conserved-quantity candidates, or exploratory geometry/phase proxies.

## Preflight summary

| Item | State |
|------|-------|
| Locked definitions | τ = N_t, Δτ = ΔN_t, emergent space, c = l_q / t_q preserved |
| Stage 4B result | 2 unperturbed NONTRIVIAL labels; 1/13 perturbation pass; fragile |
| Manuscript .tex refs | Not present locally; canonical docs used |
| Prior tests | 190 passing on integration branch before Stage 3C |

Stage 4A/4B outputs preserved; not overwritten.

## Action catalog

| ID | Description | Conserves total τ |
|----|-------------|-------------------|
| A0_identity_control | No update; trivial control | yes |
| A1_pairwise_relaxation | Local pairwise smoothing | yes |
| A2_threshold_relaxation | Threshold-gated smoothing | yes |
| A3_memory_weighted_relaxation | Memory-weighted smoothing | yes |
| A4_finite_propagation_delay | One transfer per step max | yes |
| A5_local_curvature_pressure | Laplacian-proxy pressure | yes |
| A6_phase_coherence_probe | Identity + phase diagnostics | yes |

## Metric table (toy diagnostics only)

| Metric | Role |
|--------|------|
| total_tau / total_tau_change | Conservation check |
| active_support_size | Spreading/localization |
| localization_score / spreading_score | Pattern shape |
| finite_speed_violation_count | Toy c = l_q / t_q audit |
| phase_coherence_proxy | QM-like exploratory diagnostic |
| effective_geometry_proxy | GR-like weak-field candidate diagnostic |
| oscillation_score / recurrence_score | Dynamics shape |

## Benchmark results (aggregate tags observed)

| Action | Tags observed (sample) |
|--------|------------------------|
| A0 | CONSERVED_QUANTITY_CANDIDATE, TRIVIAL_CONTROL |
| A1 | SPREADING_SMOOTHING, LOCALIZED_PERSISTENT_TOY_PATTERN, FINITE_SPEED_CLEAN/VIOLATION |
| A2 | SPREADING_SMOOTHING, LOCALIZED_PERSISTENT_TOY_PATTERN |
| A3 | SPREADING_SMOOTHING, PROPAGATING_TOY_PATTERN, OSCILLATORY_TOY_PATTERN |
| A4 | SPREADING_SMOOTHING, FINITE_SPEED_CLEAN, PROPAGATING_TOY_PATTERN |
| A5 | SPREADING_SMOOTHING, LOCALIZED_PERSISTENT_TOY_PATTERN, PROPAGATING_TOY_PATTERN |
| A6 | CONSERVED_QUANTITY_CANDIDATE (phase diagnostics on static field) |

**784 deterministic benchmark runs** (7 actions × 8 seeds × 2 grids × 7 step counts).

## Observations

- A1–A5 produce spreading/smoothing on peaked and random seeds while conserving total τ.
- A4 enforces at most one neighbor transfer per step; finite-speed classifications vary by seed/grid.
- A5 (Laplacian-proxy pressure) shows localized and propagating toy tags on some seeds.
- A6 leaves fields unchanged; phase_coherence_proxy provides exploratory diagnostic values only.
- A0 correctly remains trivial control across all seeds.

## Conservative interpretations

- **Spreading/smoothing** is the dominant nontrivial behavior under relaxation-family Actions—consistent with Stage 4A INCONCLUSIVE spreading pattern under A1.
- **Localization tags** appear on some runs but are not perturbation-robust structure evidence (cf. Stage 4B fragility).
- **Geometry and phase proxies** flag Actions worth later weak-field or QM-like exploratory tests—they do not constitute GR or QM recovery.

## Negative results

- No Action produces robust particle-like persistence across the full benchmark matrix.
- A6 shows no dynamical phase evolution (identity step by design).
- Threshold relaxation (A2) reduces activity vs A1 on some seeds—higher threshold delays spreading.

## Scientific limitations

- Tiny grids only (3×3, 5×5).
- Integer toy rules; not continuum field theory.
- Metrics are count-lattice diagnostics, not calibrated physical observables.
- Memory and curvature Actions are generic scaffolds, not tuned for positive structure outcomes.

## Recommended next stage

Return to Stage 4 structure exploration using Action-informed update rules (e.g., A4 finite-speed variants, A5 curvature pressure) with Stage 4B-style robustness audits. Consider Stage 8 weak-field proxy tests if geometry candidates persist.

## Explicit non-claims

**No GR derivation. No QM derivation. No particle, electron, photon, mass, charge, spin, hbar, alpha, or empirical validation claim is made.**

Metrics are toy diagnostics—not real energy, curvature, mass, gravity, or quantum phase.

## Deterministic JSON output

**Path:** `outputs/stage3c_fundamental_tdf_action_discovery_summary.json`
