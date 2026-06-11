"""Tests for Stage 4B control rules and suite (Stage 4B)."""

import inspect

import pytest

from tdf_tq import (
    FieldEvolutionConfig,
    SpatialBounds,
    SpatialSlice,
    best_stage4b_result,
    conservative_centered_cohesion_step,
    run_field_evolution,
    run_stage4b_robustness_suite,
    single_peak_field,
)
from tdf_tq import search as search_module
from tdf_tq.nontriviality import CLASS_TRIVIAL_STABLE_CONTROL


def _slice() -> SpatialSlice:
    return SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))


def test_identity_control_is_trivial_not_candidate():
    results = run_stage4b_robustness_suite(_slice(), 10, 10, steps=2)
    identity_results = [r for r in results if r.update_rule_label == "identity"]
    assert identity_results
    for result in identity_results:
        assert all(
            a.classification == CLASS_TRIVIAL_STABLE_CONTROL for a in result.assessments
        )
        assert result.stable_count == 0


def test_conservative_pairwise_relaxation_remains_deterministic():
    field = single_peak_field(_slice(), (1, 1, 0), 10, 10)
    run_a = run_field_evolution(field, steps=2, step_kind="conservative_pairwise_relaxation")
    run_b = run_field_evolution(field, steps=2, step_kind="conservative_pairwise_relaxation")
    assert [dict(f.values) for f in run_a] == [dict(f.values) for f in run_b]


def test_conservative_centered_cohesion_preserves_total_tau():
    field = single_peak_field(_slice(), (1, 1, 0), 10, 10)
    before = sum(field.values.values())
    after = conservative_centered_cohesion_step(field, anchor_counts=(1, 1, 0))
    assert sum(after.values.values()) == before


def test_conservative_centered_cohesion_no_negative_tau():
    field = single_peak_field(_slice(), (1, 1, 0), 10, 10)
    after = conservative_centered_cohesion_step(field, anchor_counts=(1, 1, 0))
    assert all(v >= 0 for v in after.values.values())


def test_run_stage4b_suite_includes_all_rule_labels():
    results = run_stage4b_robustness_suite(_slice(), 10, 10, steps=1)
    rules = {r.update_rule_label for r in results}
    assert rules == {
        "identity",
        "conservative_pairwise_relaxation",
        "conservative_centered_cohesion",
    }


def test_best_stage4b_result_is_deterministic():
    results = run_stage4b_robustness_suite(_slice(), 10, 10, steps=3)
    assert best_stage4b_result(results) == best_stage4b_result(results)


def test_no_physical_claims_in_search_module():
    source = inspect.getsource(search_module).lower()
    for token in ("hbar", "alpha", "positron", "quantum mechanics"):
        assert token not in source
