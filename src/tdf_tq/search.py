"""Deterministic search for localized packet-structure candidates."""

from tdf_tq.candidates import (
    CandidateEvaluation,
    LocalizedCandidateCriteria,
    evaluate_localized_candidate,
)
from tdf_tq.dynamics import FieldEvolutionConfig, run_field_evolution
from tdf_tq.history import structure_history_from_field_sequence
from tdf_tq.nontriviality import CLASS_TRIVIAL_STABLE_CONTROL
from tdf_tq.patterns import deterministic_seed_suite
from tdf_tq.robustness import (
    RobustnessResult,
    anchor_counts_from_field,
    evaluate_candidate_robustness,
)
from tdf_tq.space import SpatialSlice

_STAGE4B_UPDATE_RULES = (
    "identity",
    "conservative_pairwise_relaxation",
    "conservative_centered_cohesion",
)

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


def run_stage4b_robustness_suite(
    slice_: SpatialSlice,
    baseline_tau: int,
    excess_tau: int,
    steps: int,
    evolution_config: FieldEvolutionConfig | None = None,
    criteria: LocalizedCandidateCriteria | None = None,
) -> tuple[RobustnessResult, ...]:
    """Run Stage 4B robustness suite over seeds and update-rule controls."""
    cfg = evolution_config or FieldEvolutionConfig()
    crit = criteria or LocalizedCandidateCriteria()
    results: list[RobustnessResult] = []
    for seed_label, initial_field in deterministic_seed_suite(slice_, baseline_tau, excess_tau):
        anchor = anchor_counts_from_field(initial_field)
        for rule in _STAGE4B_UPDATE_RULES:
            results.append(
                evaluate_candidate_robustness(
                    seed_label=seed_label,
                    initial_field=initial_field,
                    update_rule_label=rule,
                    steps=steps,
                    evolution_config=cfg,
                    criteria=crit,
                    anchor_counts=anchor if rule == "conservative_centered_cohesion" else None,
                )
            )
    return tuple(sorted(results, key=lambda r: (r.seed_label, r.update_rule_label)))


def best_stage4b_result(
    results: tuple[RobustnessResult, ...],
) -> RobustnessResult | None:
    """Select best robustness result; trivial-only controls rank lower."""
    if not results:
        return None

    def sort_key(result: RobustnessResult) -> tuple:
        trivial_only = all(
            a.classification == CLASS_TRIVIAL_STABLE_CONTROL for a in result.assessments
        )
        trivial_penalty = 1 if trivial_only else 0
        return (
            trivial_penalty,
            -result.stable_count,
            -result.robustness_ratio,
            result.fail_count,
            result.seed_label,
            result.update_rule_label,
        )

    return min(results, key=sort_key)
