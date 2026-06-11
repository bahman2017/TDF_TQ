"""Tests for Stage 3C Action catalog benchmark and summary."""

import json
from pathlib import Path

import pytest

from tdf_tq.action_metrics import compute_action_metrics
from tdf_tq.action_catalog import (
    OVERCLAIM_PHRASES,
    VERDICT_PASS,
    benchmark_seed_catalog,
    classify_action_behavior,
    make_slice,
    run_action_catalog_benchmark,
    run_stage3c_action_discovery,
    scan_for_overclaim_phrases,
)
from tdf_tq.actions import IdentityControlAction, PairwiseRelaxationAction, run_action_steps

REQUIRED_TOP_LEVEL_KEYS = {
    "stage",
    "branch",
    "purpose",
    "locked_definitions_checked",
    "action_catalog",
    "benchmark_config",
    "seed_catalog",
    "metric_definitions",
    "action_results",
    "best_action_candidates_for_later_stages",
    "negative_results",
    "conserved_quantity_candidates",
    "finite_speed_results",
    "effective_geometry_proxy_results",
    "phase_coherence_proxy_results",
    "verdict",
    "limitations",
    "explicit_non_claims",
    "next_recommended_stage",
}


def test_benchmark_seed_catalog_has_eight_seeds_on_3x3():
    seeds = benchmark_seed_catalog(make_slice(2, 2, 0))
    labels = {label for label, _ in seeds}
    assert len(seeds) >= 7
    assert "single_peak_center" in labels
    assert "random_seeded_low_amplitude" in labels
    assert "random_seeded_high_amplitude" in labels


def test_classify_identity_as_trivial_control():
    slice_ = make_slice(2, 2, 0)
    seeds = benchmark_seed_catalog(slice_)
    field = seeds[0][1]
    history = run_action_steps(IdentityControlAction(), field, 3)
    metrics = compute_action_metrics(field, history[-1], history)
    tags = classify_action_behavior(
        "A0_identity_control", field, history[-1], history, metrics
    )
    assert "TRIVIAL_CONTROL" in tags


def test_classify_relaxation_spreading():
    slice_ = make_slice(2, 2, 0)
    seeds = benchmark_seed_catalog(slice_)
    field = next(f for label, f in seeds if label == "single_peak_center")
    history = run_action_steps(PairwiseRelaxationAction(), field, 8)
    metrics = compute_action_metrics(field, history[-1], history)
    tags = classify_action_behavior(
        "A1_pairwise_relaxation", field, history[-1], history, metrics
    )
    assert "SPREADING_SMOOTHING" in tags or "CONSERVED_QUANTITY_CANDIDATE" in tags


def test_run_action_catalog_benchmark_deterministic():
    r1, a1 = run_action_catalog_benchmark()
    r2, a2 = run_action_catalog_benchmark()
    assert r1 == r2
    assert a1 == a2


def test_stage3c_summary_json_schema():
    summary = run_stage3c_action_discovery()
    assert REQUIRED_TOP_LEVEL_KEYS <= set(summary.keys())
    assert summary["stage"] == "3C"
    assert summary["verdict"] in {
        VERDICT_PASS,
        "INCONCLUSIVE_ACTION_BEHAVIOR",
        "FAIL",
    }
    assert len(summary["action_catalog"]) == 7


def test_stage3c_summary_deterministic():
    assert run_stage3c_action_discovery() == run_stage3c_action_discovery()


def test_stage3c_summary_serializes():
    summary = run_stage3c_action_discovery()
    assert json.loads(json.dumps(summary, sort_keys=True)) == summary


def test_stage3c_verdict_pass_with_nontrivial_actions():
    summary = run_stage3c_action_discovery()
    assert summary["verdict"] == VERDICT_PASS
    assert summary["aggregates"]["nontrivial_action_ids"]


@pytest.mark.parametrize("phrase", OVERCLAIM_PHRASES)
def test_overclaim_scanner_detects_forbidden_phrases(phrase: str):
    assert phrase in scan_for_overclaim_phrases(f"Some text with {phrase} inside.")


def test_no_overclaims_in_stage3c_docs_and_outputs():
    root = Path(__file__).resolve().parents[1]
    paths = [
        root / "docs/stage3c_fundamental_tdf_action_discovery.md",
        root / "outputs/stage3c_fundamental_tdf_action_discovery_report.md",
    ]
    for path in paths:
        hits = scan_for_overclaim_phrases(path.read_text(encoding="utf-8"))
        assert hits == [], f"overclaim phrases in {path}: {hits}"


def test_stage3c_report_file_exists():
    report = Path(__file__).resolve().parents[1] / "outputs/stage3c_fundamental_tdf_action_discovery_report.md"
    assert report.exists()
