# Stage 3C — Fundamental TDF Action Discovery

## Purpose

Stage 3C builds a conservative **Action-discovery framework** for TDF_TQ. Actions are minimal deterministic temporal evolution rules derived from locked TDF primitives (`t_q`, `τ = N_t`, `Δτ = ΔN_t`, emergent spatial neighborhoods, working speed limit `c = l_q / t_q`).

This stage evaluates Actions **before** continuing particle-like, photon-like, electron-like, GR-like, or QM-like construction.

## Why Stage 3C precedes further structure work

Stages 4A–4B searched for localized structure under specific update rules and found fragile toy labels (robustness ratio ≈ 0.077 under cohesion). Stage 3C returns to the more fundamental question: **which minimal Actions**, derived from temporal principles alone, produce spreading, smoothing, localization, propagation, conserved-quantity candidates, geometry proxies, or phase-coherence proxies?

## Action catalog (A0–A6)

| ID | Name | Purpose |
|----|------|---------|
| A0 | identity_control | Trivial-stability control; no update |
| A1 | pairwise_relaxation | Local Δτ smoothing (existing rule) |
| A2 | threshold_relaxation | Threshold-gated smoothing |
| A3 | memory_weighted_relaxation | One-step memory-weighted smoothing |
| A4 | finite_propagation_delay | At most one neighbor transfer per step |
| A5 | local_curvature_pressure | Laplacian-proxy pressure smoothing |
| A6 | phase_coherence_probe | Identity evolution + phase diagnostics only |

## Metrics (toy diagnostics only)

Metrics are separated from Actions. They measure outcomes but are **not** real energy, curvature, mass, gravity, or quantum phase.

See `action_metrics.py` for definitions including: total tau conservation, active support size, localization/spreading scores, finite-speed violations, phase-coherence proxy, effective-geometry proxy.

## Benchmark configuration

- **Grids:** 3×3×1 and 5×5×1
- **Steps:** 0, 1, 2, 3, 5, 8, 13
- **Seeds:** single_peak_center, compact_2x2_corner, plus_cross_center, ring_shell, two_peak_symmetric, gradient_slab, random_seeded_low/high_amplitude (deterministic)

## Classification tags

Conservative multi-tag labels: `TRIVIAL_CONTROL`, `SPREADING_SMOOTHING`, `LOCALIZED_PERSISTENT_TOY_PATTERN`, `PROPAGATING_TOY_PATTERN`, `OSCILLATORY_TOY_PATTERN`, `CONSERVED_QUANTITY_CANDIDATE`, `FINITE_SPEED_CLEAN`, `FINITE_SPEED_VIOLATION`, `INCONCLUSIVE`, `FAIL`.

## GR-like and QM-like boundary checks

- **Geometry proxy:** whether distributed Δτ gradients yield stable effective-geometry proxy patterns for later weak-field testing—not GR recovery.
- **Phase proxy:** whether phase_coherence_proxy, oscillation, or recurrence merit later QM-like exploratory tests—not Schrödinger dynamics.

## Verdict categories

| Verdict | Meaning |
|---------|---------|
| PASS_ACTION_CATALOG_READY | Catalog + metrics complete; nontrivial toy behavior observed; no overclaims |
| INCONCLUSIVE_ACTION_BEHAVIOR | Framework works; no meaningful nontrivial behavior yet |
| FAIL | Tests fail, nondeterminism, broken conservation/speed checks, or overclaim |

## Explicit non-claims

- No GR, QM, particle, electron, photon, mass, charge, spin, hbar, alpha, or empirical validation claim.
- Actions are toy-model scaffolding only.

## Relation to Stage 4B

Stage 4B robustness results are preserved and remain useful. Stage 3C does not remove or overwrite Stage 4A/4B outputs. Stage 4B showed fragile nontrivial labels under cohesion; Stage 3C systematically maps simpler Action behaviors first.

## Next stage

Use Action-informed rules for later structure search (Stage 4+) or weak-field proxy tests (Stage 8) if geometry candidates persist.
