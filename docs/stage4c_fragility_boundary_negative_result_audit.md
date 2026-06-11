# Stage 4C — Fragility Boundary and Negative-Result Audit

## Purpose

Stage 4C audits fragile Stage 4B nontrivial toy labels under **stricter, broader, deterministic checks**. This stage does **not** engineer positive results or add new cohesion rules to force stability.

Stage 4B found sparse unperturbed `NONTRIVIAL_STABLE_TOY_CANDIDATE` labels (`compact_2x2_corner`, `plus_cross_center` under `conservative_centered_cohesion`) with robustness ratio ≈ 0.077. Stage 4C asks whether those labels survive:

- Larger grid embeddings (5×5×1 centered and off-center)
- Multiple step counts (3, 5, 8, 13)
- Stricter criteria profiles (localization, overlap, drift, combined strict)
- Expanded perturbation suites (single-tau, two-step capped at 24, boundary-adjacent)
- Alternate cohesion anchors (centroid, grid center, shifted)

## Relation to Stage 4B

Stage 4C reuses Stage 4B seeds, update rules, and classification machinery. It adds audit utilities in `stage4c_audit.py` and verdict logic:

| Verdict | Meaning |
|---------|---------|
| **ROBUST_TOY_CANDIDATE** | Passes combined strict criteria across multiple steps, at least one 5×5 embedding, and ≥50% perturbation assessments |
| **FRAGILE_TOY_ARTIFACT** | Passes only unperturbed, or only under one anchor/grid/criteria setting |
| **NEGATIVE_RESULT** | No candidate meets robust criteria and no fragile passes remain |
| **INCONCLUSIVE** | Mixed results below robust threshold |

## Criteria profiles

1. **stage4b_original** — default `LocalizedCandidateCriteria`
2. **stricter_localization** — min final localization ratio 0.50
3. **stricter_overlap** — min active support overlap 0.75
4. **stricter_drift** — max center drift 0.5
5. **combined_strict** — all stricter thresholds plus max active support size 4

## Negative controls

- **identity** must remain `TRIVIAL_STABLE_CONTROL`
- **conservative_pairwise_relaxation** must remain spreading / `INCONCLUSIVE`
- **shuffled excess field** must not be promoted to nontrivial
- **unchanged identity histories** must never be nontrivial

## Explicit non-claims

- No particle, electron, photon, mass, charge, spin, energy, **ħ**, **α**, QM, GR, or validated physics.
- `conservative_centered_cohesion` is an **arbitrary toy retention rule**, not attraction, force, gravity, or binding.
- Negative or fragile outcomes are scientifically acceptable and preferred over tuned positives.

## Next stage

If no robust toy evidence appears, document the negative-result boundary and defer broad structure search. Stage 5 exploratory criteria design only if robust toy evidence emerges.
