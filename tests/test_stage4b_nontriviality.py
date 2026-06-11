"""Tests for nontrivial stability classification (Stage 4B)."""

import pytest

from tdf_tq import (
    CandidateEvaluation,
    NontrivialStabilityAssessment,
    classify_nontrivial_stability,
)
from tdf_tq.nontriviality import CLASS_INCONCLUSIVE, CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE, CLASS_TRIVIAL_STABLE_CONTROL


def _evaluation(passed: bool, verdict: str, seed: str = "s") -> CandidateEvaluation:
    return CandidateEvaluation(
        seed_label=seed,
        passed=passed,
        verdict=verdict,
        metrics={"final_active_localization_ratio": 0.5},
        limitations=("Toy candidate only; not a particle, not an electron, not validated physics.",),
    )


def test_nontrivial_stability_assessment_validates_classification():
    with pytest.raises(ValueError):
        NontrivialStabilityAssessment(
            seed_label="s",
            update_rule_label="identity",
            classification="INVALID",
            passed_nontrivial=False,
            metrics={},
            limitations=("Toy stability label only; not a particle, not an electron, not validated physics.",),
        )


def test_classify_identity_as_trivial_stable_control():
    result = classify_nontrivial_stability(
        _evaluation(True, "PASS_TO_STAGE_4B"),
        update_rule_label="identity",
        changed_across_history=True,
        perturbation_robust=True,
    )
    assert result.classification == CLASS_TRIVIAL_STABLE_CONTROL
    assert not result.passed_nontrivial


def test_unchanged_history_is_trivial_even_if_localized():
    result = classify_nontrivial_stability(
        _evaluation(True, "PASS_TO_STAGE_4B"),
        update_rule_label="conservative_pairwise_relaxation",
        changed_across_history=False,
        perturbation_robust=True,
    )
    assert result.classification == CLASS_TRIVIAL_STABLE_CONTROL


def test_passed_plus_robust_becomes_nontrivial_candidate():
    result = classify_nontrivial_stability(
        _evaluation(True, "PASS_TO_STAGE_4B"),
        update_rule_label="conservative_centered_cohesion",
        changed_across_history=True,
        perturbation_robust=True,
    )
    assert result.classification == CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE
    assert result.passed_nontrivial


def test_inconclusive_evaluation_becomes_inconclusive():
    result = classify_nontrivial_stability(
        _evaluation(False, "INCONCLUSIVE"),
        update_rule_label="conservative_pairwise_relaxation",
        changed_across_history=True,
        perturbation_robust=False,
    )
    assert result.classification == CLASS_INCONCLUSIVE


def test_fail_evaluation_becomes_fail():
    result = classify_nontrivial_stability(
        _evaluation(False, "FAIL"),
        update_rule_label="conservative_pairwise_relaxation",
        changed_across_history=True,
        perturbation_robust=False,
    )
    assert result.classification == "FAIL"


def test_limitations_contain_disclaimer():
    result = classify_nontrivial_stability(
        _evaluation(False, "INCONCLUSIVE"),
        update_rule_label="conservative_pairwise_relaxation",
        changed_across_history=True,
        perturbation_robust=False,
    )
    assert "not a particle" in result.limitations[0]
    assert "not an electron" in result.limitations[0]
