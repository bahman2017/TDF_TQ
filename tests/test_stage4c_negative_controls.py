"""Tests for Stage 4C negative controls."""

from tdf_tq.nontriviality import (
    CLASS_INCONCLUSIVE,
    CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
    CLASS_TRIVIAL_STABLE_CONTROL,
)
from tdf_tq.stage4c_audit import (
    build_candidate_field,
    deterministic_shuffled_excess_field,
    make_slice,
    run_negative_controls,
    run_stage4c_fragility_audit,
)


def test_identity_control_remains_trivial_stable():
    controls = run_negative_controls()
    identity = next(c for c in controls if c["control"] == "identity")
    assert identity["classification"] == CLASS_TRIVIAL_STABLE_CONTROL
    assert identity["changed"] is False


def test_relaxation_control_not_promoted_to_nontrivial():
    controls = run_negative_controls()
    relaxation = next(
        c for c in controls if c["control"] == "conservative_pairwise_relaxation"
    )
    assert relaxation["classification"] in (CLASS_INCONCLUSIVE, CLASS_TRIVIAL_STABLE_CONTROL)
    assert relaxation["classification"] != CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE


def test_shuffled_excess_field_not_nontrivial_candidate():
    controls = run_negative_controls()
    shuffled = next(c for c in controls if c["control"] == "shuffled_excess_field")
    assert shuffled["is_nontrivial"] is False


def test_unchanged_history_identity_not_nontrivial():
    controls = run_negative_controls()
    long_identity = next(c for c in controls if c["control"] == "identity_long_steps")
    assert long_identity["classification"] == CLASS_TRIVIAL_STABLE_CONTROL
    assert long_identity["is_nontrivial"] is False
    assert long_identity["changed"] is False


def test_shuffled_field_preserves_total_tau():
    slice_ = make_slice(2, 2, 0)
    field = build_candidate_field("compact_2x2_corner", slice_)
    before = sum(field.values.values())
    shuffled = deterministic_shuffled_excess_field(field)
    after = sum(shuffled.values.values())
    assert before == after


def test_stage4c_summary_negative_controls_present():
    summary = run_stage4c_fragility_audit()
    control_names = {entry["control"] for entry in summary["negative_controls"]}
    assert control_names >= {
        "identity",
        "conservative_pairwise_relaxation",
        "shuffled_excess_field",
        "identity_long_steps",
    }


def test_no_candidate_meets_robust_verdict_in_stage4c():
    summary = run_stage4c_fragility_audit()
    assert summary["verdict"] != "ROBUST_TOY_CANDIDATE"
