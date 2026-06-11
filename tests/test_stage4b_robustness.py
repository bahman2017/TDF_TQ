"""Tests for perturbation robustness (Stage 4B)."""

import pytest

from tdf_tq import (
    FieldEvolutionConfig,
    LocalizedCandidateCriteria,
    SpatialBounds,
    SpatialSlice,
    deterministic_single_step_perturbations,
    evaluate_candidate_robustness,
    move_one_excess_tau_to_neighbor,
    single_peak_field,
)
from tdf_tq.nontriviality import CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE, CLASS_TRIVIAL_STABLE_CONTROL


def _slice() -> SpatialSlice:
    return SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))


def _peak_field():
    return single_peak_field(_slice(), center=(1, 1, 0), baseline_tau=10, peak_excess_tau=10)


def test_move_one_excess_preserves_total_tau():
    field = _peak_field()
    before = sum(field.values.values())
    moved = move_one_excess_tau_to_neighbor(field, (1, 1, 0), (1, 0, 0))
    after = sum(moved.values.values())
    assert before == after


def test_move_one_excess_rejects_non_neighbor():
    field = _peak_field()
    with pytest.raises(ValueError):
        move_one_excess_tau_to_neighbor(field, (1, 1, 0), (0, 0, 0))


def test_deterministic_perturbations_is_deterministic():
    field = _peak_field()
    assert deterministic_single_step_perturbations(field) == deterministic_single_step_perturbations(field)


def test_perturbations_preserve_total_tau():
    field = _peak_field()
    for _label, perturbed in deterministic_single_step_perturbations(field):
        assert sum(perturbed.values.values()) == sum(field.values.values())


def test_evaluate_candidate_robustness_deterministic_counts():
    field = _peak_field()
    cfg = FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)
    crit = LocalizedCandidateCriteria()
    r1 = evaluate_candidate_robustness(
        "peak", field, "identity", steps=2, evolution_config=cfg, criteria=crit
    )
    r2 = evaluate_candidate_robustness(
        "peak", field, "identity", steps=2, evolution_config=cfg, criteria=crit
    )
    assert r1.stable_count == r2.stable_count
    assert r1.perturbation_count == r2.perturbation_count


def test_robustness_ratio_between_zero_and_one():
    field = _peak_field()
    result = evaluate_candidate_robustness(
        "peak",
        field,
        "conservative_pairwise_relaxation",
        steps=1,
        evolution_config=FieldEvolutionConfig(),
        criteria=LocalizedCandidateCriteria(),
    )
    assert 0.0 <= result.robustness_ratio <= 1.0


def test_trivial_stable_control_not_counted_as_stable():
    field = _peak_field()
    result = evaluate_candidate_robustness(
        "peak",
        field,
        "identity",
        steps=2,
        evolution_config=FieldEvolutionConfig(),
        criteria=LocalizedCandidateCriteria(),
    )
    assert result.stable_count == 0
    assert all(
        a.classification != CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE or not a.passed_nontrivial
        for a in result.assessments
        if a.classification == CLASS_TRIVIAL_STABLE_CONTROL
    )


def test_repeated_robustness_runs_identical():
    field = _peak_field()
    kwargs = dict(
        seed_label="peak",
        initial_field=field,
        update_rule_label="conservative_pairwise_relaxation",
        steps=2,
        evolution_config=FieldEvolutionConfig(),
        criteria=LocalizedCandidateCriteria(),
    )
    assert evaluate_candidate_robustness(**kwargs).robustness_ratio == evaluate_candidate_robustness(
        **kwargs
    ).robustness_ratio
