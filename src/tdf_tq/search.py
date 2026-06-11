"""Deterministic search for localized packet-structure candidates."""

from tdf_tq.candidates import (
    CandidateEvaluation,
    LocalizedCandidateCriteria,
    evaluate_localized_candidate,
)
from tdf_tq.dynamics import FieldEvolutionConfig, run_field_evolution
from tdf_tq.history import structure_history_from_field_sequence
from tdf_tq.patterns import deterministic_seed_suite
from tdf_tq.space import SpatialSlice

_VERDICT_PASS = "PASS_TO_STAGE_4B"
_VERDICT_INCONCLUSIVE = "INCONCLUSIVE"


def run_stable_localized_structure_search(
    slice_: SpatialSlice,
    baseline_tau: int,
    excess_tau: int,
    steps: int,
    evolution_config: FieldEvolutionConfig | None = None,
    criteria: LocalizedCandidateCriteria | None = None,
) -> tuple[CandidateEvaluation, ...]:
    """Search deterministic seeds with conservative relaxation evolution."""
    seeds = deterministic_seed_suite(slice_, baseline_tau, excess_tau)
    evaluations: list[CandidateEvaluation] = []
    for seed_label, initial_field in seeds:
        fields = run_field_evolution(
            initial_field,
            steps=steps,
            config=evolution_config,
            step_kind="conservative_pairwise_relaxation",
        )
        history = structure_history_from_field_sequence(fields, label_prefix=seed_label)
        evaluations.append(
            evaluate_localized_candidate(
                history,
                criteria=criteria,
                seed_label=seed_label,
            )
        )
    return tuple(sorted(evaluations, key=lambda e: e.seed_label))


def best_candidate_evaluation(
    evaluations: tuple[CandidateEvaluation, ...],
) -> CandidateEvaluation | None:
    """Select the best evaluation by deterministic priority rules."""
    if not evaluations:
        return None

    def sort_key(evaluation: CandidateEvaluation) -> tuple:
        verdict_rank = {
            _VERDICT_PASS: 0,
            _VERDICT_INCONCLUSIVE: 1,
            "FAIL": 2,
        }[evaluation.verdict]
        final_loc = float(evaluation.metrics.get("final_active_localization_ratio", 0.0))
        final_active = int(evaluation.metrics.get("final_active_support_size", 0))
        return (verdict_rank, -final_loc, final_active, evaluation.seed_label)

    return min(evaluations, key=sort_key)
