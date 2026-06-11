# Stage 4B — Candidate Robustness and Nontrivial-Stability Report

**Date:** 2026-06-10  
**Implementation branch:** `feature/stage4b-candidate-robustness-nontrivial-stability`  
**Implementation commit hash:** `6094582`

## Changed files

| Path | Purpose |
|------|---------|
| `src/tdf_tq/nontriviality.py` | Nontrivial stability classification |
| `src/tdf_tq/robustness.py` | Perturbations and robustness evaluation |
| `src/tdf_tq/dynamics.py` | `conservative_centered_cohesion_step`, extended evolution |
| `src/tdf_tq/search.py` | `run_stage4b_robustness_suite`, `best_stage4b_result` |
| `src/tdf_tq/__init__.py` | Stage 4B exports |
| `tests/test_stage4b_*.py` | Nontriviality, robustness, control tests |
| `docs/stage4b_candidate_robustness_nontrivial_stability.md` | Stage 4B scope |
| `docs/roadmap.md` | Stage 4B current; Stage 4C next |
| `README.md` | Stage 4B summary |
| `outputs/stage4a_stable_localized_structure_search_report.md` | Preflight: Stage 4A commits |
| `outputs/stage4b_candidate_robustness_nontrivial_stability_summary.json` | Deterministic example |

## Tests run

```bash
python -m pytest -v
```

**Environment:** Python 3.12.10, pytest 9.0.3

## Test result summary

| Result | Count |
|--------|-------|
| Passed | 190 |
| Failed | 0 |
| Skipped | 0 |

Stage 4B additions (22 new tests). All 168 prior tests remain passing.

## Deterministic JSON output

**Path:** `outputs/stage4b_candidate_robustness_nontrivial_stability_summary.json`

3×3 example: identity → TRIVIAL_STABLE_CONTROL; relaxation → INCONCLUSIVE; cohesion → 2 unperturbed NONTRIVIAL (compact_2x2, plus_cross) with low robustness ratio (~0.077).

## Robustness conclusion

**2 unperturbed NONTRIVIAL_STABLE_TOY_CANDIDATE assessments** under `conservative_centered_cohesion` (compact_2x2_corner, plus_cross_center)—each 1/13 assessments, perturbation cases mostly FAIL.

Relaxation remains INCONCLUSIVE (spreading). Identity correctly classified as TRIVIAL_STABLE_CONTROL.

**This is not a particle or electron claim.** Low robustness ratio indicates fragile toy stability only.

## Scientific interpretation

Stage 4B adds **trivial vs nontrivial discrimination** (maturity A–C):

- Rejects identity/no-change as candidate evidence
- Confirms relaxation spreading matches Stage 4A INCONCLUSIVE pattern
- Tests toy cohesion retention—not gravity, force, or binding
- Perturbation suite exposes fragility of apparent nontrivial passes

## Limitations

- **Cohesion rule is arbitrary toy retention**, not derived physics
- **Nontrivial passes are sparse** (unperturbed only in example)
- **Perturbation cases often FAIL** even when unperturbed passes
- **No electron-like or particle identification**
- **No validated TDF_TQ physics**

## Next recommended stage

**Stage 4C — Nontrivial candidate refinement or negative-result analysis:** tighten criteria, expand seeds, or document negative results without overclaiming.
