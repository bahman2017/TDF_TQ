"""Tests for Stage 4C fragility boundary audit."""

import json

import pytest

from tdf_tq.stage4c_audit import (
    STAGE4B_BEST_RESULT,
    STAGE4C_CANDIDATES,
    VERDICT_FRAGILE_TOY_ARTIFACT,
    VERDICT_INCONCLUSIVE,
    VERDICT_NEGATIVE_RESULT,
    VERDICT_ROBUST_TOY_CANDIDATE,
    audit_candidate,
    criteria_profiles,
    deterministic_two_step_perturbations,
    embed_field_in_larger_grid,
    make_slice,
    build_candidate_field,
    determine_stage4c_verdict,
    run_stage4c_fragility_audit,
)

REQUIRED_TOP_LEVEL_KEYS = {
    "stage",
    "statement",
    "input_stage4b_best_result",
    "audit_config",
    "candidate_results",
    "grid_size_results",
    "criteria_profile_results",
    "perturbation_results",
    "anchor_dependence_results",
    "negative_controls",
    "verdict",
    "limitations",
    "non_claims",
    "next_recommended_stage",
}

VALID_VERDICTS = {
    VERDICT_ROBUST_TOY_CANDIDATE,
    VERDICT_FRAGILE_TOY_ARTIFACT,
    VERDICT_NEGATIVE_RESULT,
    VERDICT_INCONCLUSIVE,
}


def test_stage4c_summary_json_schema_fields():
    summary = run_stage4c_fragility_audit()
    assert REQUIRED_TOP_LEVEL_KEYS <= set(summary.keys())
    assert summary["stage"] == "4C"
    assert summary["input_stage4b_best_result"] == STAGE4B_BEST_RESULT
    assert summary["verdict"] in VALID_VERDICTS
    assert isinstance(summary["limitations"], list)
    assert isinstance(summary["non_claims"], list)


def test_stage4c_summary_is_deterministic():
    first = run_stage4c_fragility_audit()
    second = run_stage4c_fragility_audit()
    assert first == second


def test_stage4c_summary_serializes_to_json():
    summary = run_stage4c_fragility_audit()
    encoded = json.dumps(summary, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded == summary


def test_criteria_profiles_include_all_named_profiles():
    profiles = criteria_profiles()
    assert set(profiles) == {
        "stage4b_original",
        "stricter_localization",
        "stricter_overlap",
        "stricter_drift",
        "combined_strict",
    }


def test_two_step_perturbations_capped_at_24():
    slice_ = make_slice(2, 2, 0)
    field = build_candidate_field("compact_2x2_corner", slice_)
    perturbations = deterministic_two_step_perturbations(field)
    assert len(perturbations) <= 24
    assert perturbations


def test_embed_field_in_larger_grid_preserves_pattern():
    slice_3 = make_slice(2, 2, 0)
    slice_5 = make_slice(4, 4, 0)
    field_3 = build_candidate_field("compact_2x2_corner", slice_3)
    embedded = embed_field_in_larger_grid(field_3, slice_5, (1, 1, 0), baseline_tau=10)
    assert embedded.slice.bounds.max_N_a == 4
    assert embedded.values[(1, 1, 0)] > 10


def test_audit_candidate_covers_both_stage4b_seeds():
    for seed, rule in STAGE4C_CANDIDATES:
        record = audit_candidate(seed, rule)
        assert record.seed_label == seed
        assert record.update_rule_label == rule
        assert record.grid_size_results
        assert record.criteria_profile_results
        assert record.perturbation_results
        assert record.anchor_dependence_results


def test_finite_size_grid_results_include_3x3_and_5x5():
    record = audit_candidate("compact_2x2_corner", "conservative_centered_cohesion")
    grids = {entry["grid"] for entry in record.grid_size_results}
    assert grids == {"3x3x1", "5x5x1"}
    placements_5 = {
        entry["placement"]
        for entry in record.grid_size_results
        if entry["grid"] == "5x5x1"
    }
    assert placements_5 == {"centered", "off_center"}


def test_anchor_dependence_audit_includes_alternate_anchors():
    record = audit_candidate("compact_2x2_corner", "conservative_centered_cohesion")
    anchor_names = {entry["anchor_name"] for entry in record.anchor_dependence_results}
    assert "centroid" in anchor_names
    assert "grid_center" in anchor_names


def test_determine_stage4c_verdict_fragile_for_stage4b_candidates():
    records = tuple(
        audit_candidate(seed, rule) for seed, rule in STAGE4C_CANDIDATES
    )
    verdict = determine_stage4c_verdict(records)
    assert verdict == VERDICT_FRAGILE_TOY_ARTIFACT


def test_run_stage4c_audit_verdict_matches_determine():
    summary = run_stage4c_fragility_audit()
    records = tuple(
        audit_candidate(seed, rule) for seed, rule in STAGE4C_CANDIDATES
    )
    assert summary["verdict"] == determine_stage4c_verdict(records)


def test_flattened_results_include_seed_labels():
    summary = run_stage4c_fragility_audit()
    for key in (
        "grid_size_results",
        "criteria_profile_results",
        "perturbation_results",
        "anchor_dependence_results",
    ):
        for entry in summary[key]:
            assert "seed_label" in entry
            assert "update_rule_label" in entry
