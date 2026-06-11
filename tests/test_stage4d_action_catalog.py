"""Tests for Stage 4D minimal temporal Action catalog."""

import json

from tdf_tq.action_catalog import (
    VERDICT_READY,
    make_slice,
    neutral_seed_catalog,
    run_conservation_checks,
    run_stage4d_catalog_diagnostics,
    run_stage4d_minimal_action_catalog,
    compute_action_diagnostics,
)
from tdf_tq.actions import (
    minimal_action_catalog,
    run_action_steps,
)

REQUIRED_JSON_KEYS = {
    "stage",
    "statement",
    "merged_stage4c_reference",
    "action_catalog",
    "action_diagnostics",
    "conservation_results",
    "boundary_check_results",
    "legacy_rule_status",
    "roadmap_correction",
    "verdict",
    "limitations",
    "non_claims",
    "next_recommended_stage",
}


def test_action_metadata_schema():
    catalog = minimal_action_catalog()
    assert len(catalog) >= 6
    for action in catalog:
        meta = action.to_metadata_dict()
        for key in (
            "action_id",
            "label",
            "allowed_ingredients",
            "conserved_quantities",
            "forbidden_ingredients",
            "update_function_name",
            "scientific_status",
            "limitations",
        ):
            assert key in meta


def test_primary_catalog_includes_a0_through_a4():
    catalog = minimal_action_catalog()
    primary_ids = {a.action_id for a in catalog if not a.is_legacy}
    assert primary_ids == {
        "A0_identity_control",
        "A1_pairwise_relaxation",
        "A2_thresholded_relaxation_memory",
        "A3_local_temporal_inertia",
        "A4_finite_propagation_limited_diffusion",
    }


def test_identity_remains_trivial():
    catalog = minimal_action_catalog()
    identity = next(a for a in catalog if a.action_id == "A0_identity_control")
    seeds = neutral_seed_catalog(make_slice())
    field = seeds[0][1]
    history = run_action_steps(identity, field, 5)
    assert all(dict(history[0].values) == dict(h.values) for h in history)


def test_pairwise_relaxation_conserves_total_tau():
    catalog = minimal_action_catalog()
    relax = next(a for a in catalog if a.action_id == "A1_pairwise_relaxation")
    seeds = neutral_seed_catalog(make_slice())
    diag = compute_action_diagnostics(relax, seeds[0][1], steps=5)
    assert diag["total_tau_change"] == 0


def test_stage4d_json_schema():
    summary = run_stage4d_minimal_action_catalog()
    assert REQUIRED_JSON_KEYS <= set(summary.keys())
    assert summary["stage"] == "4D"
    assert summary["merged_stage4c_reference"]["stage4c_verdict"] == "FRAGILE_TOY_ARTIFACT"


def test_stage4d_json_deterministic():
    assert run_stage4d_minimal_action_catalog() == run_stage4d_minimal_action_catalog()


def test_stage4d_json_serializes():
    summary = run_stage4d_minimal_action_catalog()
    assert json.loads(json.dumps(summary, sort_keys=True)) == summary


def test_conservation_results_for_primary_actions():
    results = run_conservation_checks(minimal_action_catalog(), make_slice())
    for entry in results:
        if entry["action_id"] != "LEGACY_conservative_centered_cohesion":
            assert entry["conserved_total_tau"] is True


def test_catalog_diagnostics_runs():
    diagnostics, summary = run_stage4d_catalog_diagnostics()
    assert summary["run_count"] > 0
    assert diagnostics
    assert "A1_pairwise_relaxation" in summary["primary_actions"]


def test_stage4d_verdict_ready():
    summary = run_stage4d_minimal_action_catalog()
    assert summary["verdict"] in {VERDICT_READY, "ACTION_CATALOG_INCOMPLETE"}


def test_legacy_cohesion_excluded_from_benchmark():
    diagnostics, summary = run_stage4d_catalog_diagnostics()
    action_ids = {d["action_id"] for d in diagnostics}
    assert "LEGACY_conservative_centered_cohesion" not in action_ids
    assert summary["legacy_excluded_from_benchmark"]
