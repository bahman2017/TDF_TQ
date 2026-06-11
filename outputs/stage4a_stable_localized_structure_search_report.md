# Stage 4A — Stable Localized Delta Tau Structure Search Report

**Date:** 2026-06-10  
**Branch:** `feature/stage4a-stable-localized-delta-tau-structure-search`  
**Commits:**
- `9c639ef` — Stage 4A stable localized delta tau structure search
- `f2a4a8e` — Stage 4A output report
- `9310952` — Stage 4A integration merge into `feature/stage0-repository-foundation`

## Changed files

| Path | Purpose |
|------|---------|
| `src/tdf_tq/structure.py` | Active-support diagnostics |
| `src/tdf_tq/history.py` | Fixed-baseline active history series |
| `src/tdf_tq/patterns.py` | Deterministic seed patterns |
| `src/tdf_tq/candidates.py` | Criteria and evaluation |
| `src/tdf_tq/search.py` | Search runner and best-candidate selection |
| `src/tdf_tq/__init__.py` | Stage 4A exports |
| `tests/test_active_structure_support.py` | Active support tests |
| `tests/test_seed_patterns.py` | Pattern tests |
| `tests/test_candidate_evaluation.py` | Evaluation tests |
| `tests/test_stable_structure_search.py` | Search tests |
| `docs/stage4a_stable_localized_delta_tau_structure_search.md` | Stage 4A scope |
| `docs/roadmap.md` | Stage 4A current; Stage 4B next |
| `README.md` | Stage 4A summary |
| `outputs/stage3b_5d_packet_structure_history_report.md` | Preflight: both Stage 3B commits |
| `outputs/stage4a_stable_localized_structure_search_summary.json` | Deterministic search example |
| `.gitignore` | Whitelist Stage 4A outputs |

## Tests run

```bash
python -m pytest -v
```

**Environment:** Python 3.12.10, pytest 9.0.3

## Test result summary

| Result | Count |
|--------|-------|
| Passed | 168 |
| Failed | 0 |
| Skipped | 0 |

Stage 4A additions (29 new tests) cover active support, seeds, evaluation, and search determinism.

All 139 prior Stage 0–3B tests remain passing.

## Deterministic JSON output

**Path:** `outputs/stage4a_stable_localized_structure_search_summary.json`

3×3 lattice, baseline=10, excess=10, 3 relaxation steps: **0 PASS**, **3 INCONCLUSIVE**, **0 FAIL**. Best: `compact_2x2_corner` (INCONCLUSIVE).

## Candidate search conclusion

**No stable localized candidate passed the current toy criteria.**

Relaxation spreads excess tau across the lattice, increasing active support size and reducing localization below thresholds. INCONCLUSIVE outcomes indicate residual excess with partial localization—not particle claims.

## Scientific interpretation

Stage 4A implements **active-support-based candidate search** (maturity A–C):

- Fixed baseline distinguishes localized excess from full-lattice occupancy
- Deterministic seeds + conservative relaxation produce reproducible histories
- PASS / INCONCLUSIVE / FAIL verdicts with mandatory limitation text

A PASS would mean “study further in Stage 4B”—not electron, not particle, not validated physics.

## Limitations

- **Toy relaxation spreads peaks** — default 3-step search may not find PASS candidates
- **Criteria are arbitrary thresholds** — not derived from experiment or theory
- **Finite seed suite only** — no exhaustive structure search
- **No particles identified** — candidates are diagnostic labels only
- **No validated TDF_TQ physics**

## Next recommended stage

**Stage 4B — Candidate robustness and nontrivial-stability tests:** stress-test any Stage 4A passes; refine criteria and seeds without overclaiming.
