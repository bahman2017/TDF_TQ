# Stage 4A — Stable Localized Delta Tau Packet-Structure Search

## Purpose

Stage 4A searches for **localized stable packet-structure candidates** using Stage 3B 5D toy state-space tooling: `E = (N_a, N_b, N_c, N_t)` plus update-history index `k`.

Results are **toy candidates only**—not particles, not electrons, not validated structures.

## Relation to Stage 3B

| Stage 3B | Stage 4A |
|----------|----------|
| Field evolution, histories, persistence scores | Deterministic seed search + candidate criteria |
| Full-lattice support diagnostics | **Active support above fixed baseline** |
| Quasi-stability thresholds | PASS / INCONCLUSIVE / FAIL verdicts |

## Why active support?

When a `DeltaTauField` fills an entire slice, every site appears in full `spatial_support`. **Localization must use active support**—sites where `N_t > baseline`—so uniform lattices are not misclassified as localized peaks.

## Localized toy candidate

A candidate is a `StructureHistory` from a deterministic seed evolved by conservative pairwise relaxation, evaluated with `LocalizedCandidateCriteria` on **active-support metrics** at a **fixed initial baseline**.

## Candidate criteria (defaults)

- Minimum final total excess tau
- Maximum final **active** support size
- Minimum final active localization ratio
- Maximum active center drift
- Maximum active tau-profile L1 step change
- Minimum active support overlap between steps
- Optional total-tau conservation requirement

## Seed patterns

- `single_peak_center` — one active site
- `plus_cross_center` — center + unit-neighbor arms
- `compact_2x2_corner` — compact block (when bounds allow)

## Search dynamics

`run_stable_localized_structure_search` runs deterministic seeds through `conservative_pairwise_relaxation`—toy integer relaxation, not physical dynamics.

## Verdict interpretation

| Verdict | Meaning |
|---------|---------|
| **PASS_TO_STAGE_4B** | All toy criteria satisfied; study further in Stage 4B |
| **INCONCLUSIVE** | Excess remains but criteria not fully met |
| **FAIL** | No meaningful excess or criteria clearly failed |

> **A Stage 4A pass means only that a toy localized Δτ packet-structure candidate should be studied further. It does not mean particle, electron, mass, charge, spin, or QM behavior.**

Passing Stage 4A is **not an electron-like candidate yet**.

## Explicit non-claims

- No electron-like candidate yet (even on PASS).
- No real particle, positron, charge, spin, or mass.
- No QM, GR, or Newtonian recovery.
- No physical energy conservation.
- No physical 5D spacetime.
- No validated physics.

## Next stage

**Stage 4B — Candidate robustness and nontrivial-stability tests.**
