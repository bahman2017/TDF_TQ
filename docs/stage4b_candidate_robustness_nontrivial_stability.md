# Stage 4B — Candidate Robustness and Nontrivial-Stability Tests

## Purpose

Stage 4B stress-tests Stage 4A localized candidates under:

1. **Trivial stability controls** (identity / no-update freezing)
2. **Spreading baseline** (conservative pairwise relaxation)
3. **Toy retention rule** (conservative centered cohesion)
4. **Deterministic single-tau perturbations**

Stage 4A found **0 PASS, 3 INCONCLUSIVE, 0 FAIL** under relaxation. Stage 4B does **not** force a positive result.

## Relation to Stage 4A

Stage 4B reuses `LocalizedCandidateCriteria`, active-support diagnostics, and deterministic seeds. It adds classification of whether stability is **trivial** or **nontrivial** under update and perturbation tests.

## Trivial vs nontrivial

| Class | Meaning |
|-------|---------|
| **TRIVIAL_STABLE_CONTROL** | Identity or unchanged history—rejected as candidate evidence |
| **NONTRIVIAL_STABLE_TOY_CANDIDATE** | Passed criteria with history change and perturbation robustness |
| **INCONCLUSIVE** | Residual excess, criteria not fully met |
| **FAIL** | Clear failure |

> **A Stage 4B nontrivial-stable result, if found, is still not a particle and not an electron-like candidate.**

## Update rules

- **identity** — frozen control (not physics)
- **conservative_pairwise_relaxation** — spreading baseline from Stage 3B
- **conservative_centered_cohesion** — toy retention toward anchor on count lattice; **not** attraction, force, gravity, binding, charge, or mass

## Perturbation robustness

Single-tau moves from active sites to unit neighbors (deterministic, max 12). Unperturbed case requires all perturbation evaluations to pass Stage 4A criteria for `perturbation_robust=True`.

## Explicit non-claims

- No electron-like candidate yet.
- No real particle, positron, charge, spin, or mass.
- No QM, GR, or Newtonian recovery.
- No physical energy conservation.
- No physical 5D spacetime.
- No validated physics.

## Next stage

**Stage 4C — Nontrivial candidate refinement or negative-result analysis.**
