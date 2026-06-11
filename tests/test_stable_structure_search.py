"""Tests for stable localized structure search (Stage 4A)."""

import pytest

from tdf_tq import (
    FieldEvolutionConfig,
    LocalizedCandidateCriteria,
    SpatialBounds,
    SpatialSlice,
    best_candidate_evaluation,
    run_stable_localized_structure_search,
)


def _slice() -> SpatialSlice:
    return SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))


def test_search_returns_deterministic_evaluations():
    run_a = run_stable_localized_structure_search(
        _slice(), baseline_tau=10, excess_tau=10, steps=3
    )
    run_b = run_stable_localized_structure_search(
        _slice(), baseline_tau=10, excess_tau=10, steps=3
    )
    assert [(e.seed_label, e.verdict, e.passed) for e in run_a] == [
        (e.seed_label, e.verdict, e.passed) for e in run_b
    ]


def test_evaluations_sorted_by_seed_label():
    evaluations = run_stable_localized_structure_search(
        _slice(), baseline_tau=10, excess_tau=5, steps=1
    )
    labels = [e.seed_label for e in evaluations]
    assert labels == sorted(labels)


def test_best_candidate_evaluation_is_deterministic():
    evaluations = run_stable_localized_structure_search(
        _slice(), baseline_tau=10, excess_tau=10, steps=3
    )
    assert best_candidate_evaluation(evaluations) == best_candidate_evaluation(evaluations)


def test_search_handles_no_fitting_seeds():
    tiny = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=0, max_N_b=0, max_N_c=0))
    evaluations = run_stable_localized_structure_search(tiny, 10, 5, steps=1)
    assert len(evaluations) == 2
    assert best_candidate_evaluation(evaluations) is not None


def test_search_output_verdicts_only_allowed_values():
    evaluations = run_stable_localized_structure_search(
        _slice(), baseline_tau=10, excess_tau=10, steps=3
    )
    allowed = {"PASS_TO_STAGE_4B", "INCONCLUSIVE", "FAIL"}
    for evaluation in evaluations:
        assert evaluation.verdict in allowed


def test_search_does_not_force_positive_candidate():
    evaluations = run_stable_localized_structure_search(
        _slice(),
        baseline_tau=10,
        excess_tau=10,
        steps=10,
        evolution_config=FieldEvolutionConfig(threshold=1, max_transfer_per_edge=2),
        criteria=LocalizedCandidateCriteria(min_final_localization_ratio=0.99),
    )
    assert not all(e.passed for e in evaluations)


def test_repeated_runs_produce_identical_metrics():
    kwargs = dict(
        slice_=_slice(),
        baseline_tau=10,
        excess_tau=10,
        steps=3,
        evolution_config=FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1),
    )
    run_a = run_stable_localized_structure_search(**kwargs)
    run_b = run_stable_localized_structure_search(**kwargs)
    assert [e.metrics for e in run_a] == [e.metrics for e in run_b]
