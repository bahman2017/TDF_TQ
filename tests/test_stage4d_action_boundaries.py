"""Tests for Stage 4D Action scientific boundary checks."""

from pathlib import Path

import pytest

from tdf_tq.action_catalog import run_stage4d_minimal_action_catalog
from tdf_tq.actions import (
    FORBIDDEN_INGREDIENT_TOKENS,
    minimal_action_catalog,
    validate_action_boundary,
)

FORBIDDEN_LABEL_TOKENS = (
    "electron",
    "photon",
    "positron",
    "mass",
    "charge",
    "spin",
)


def test_all_actions_declare_allowed_and_forbidden_ingredients():
    for action in minimal_action_catalog():
        assert action.allowed_ingredients
        assert action.forbidden_ingredients


def test_primary_actions_do_not_use_global_anchor():
    for action in minimal_action_catalog():
        if not action.is_legacy:
            assert action.uses_global_anchor is False


def test_no_primary_action_uses_particle_labels():
    for action in minimal_action_catalog():
        if action.is_legacy:
            continue
        searchable = f"{action.label} {action.scientific_status}".lower()
        for token in FORBIDDEN_LABEL_TOKENS:
            assert token not in searchable


def test_no_primary_action_metadata_boundary_violations():
    for action in minimal_action_catalog():
        if action.is_legacy:
            continue
        assert validate_action_boundary(action) == []


def test_legacy_cohesion_has_warning_and_is_marked_legacy():
    legacy = next(
        a for a in minimal_action_catalog() if a.action_id.startswith("LEGACY_")
    )
    assert legacy.is_legacy
    assert legacy.legacy_warning
    assert "arbitrary" in legacy.legacy_warning.lower()
    assert legacy.uses_global_anchor


def test_boundary_check_results_pass():
    summary = run_stage4d_minimal_action_catalog()
    assert summary["boundary_check_results"]["passed"] is True
    assert summary["verdict"] != "BOUNDARY_FAIL"


def test_no_explicit_target_object_construction_in_primary_actions():
    for action in minimal_action_catalog():
        if action.is_legacy:
            continue
        forbidden = set(action.forbidden_ingredients)
        assert "target_center" in forbidden or "particle_identity" in forbidden


def test_roadmap_no_near_term_electron_photon_targets():
    roadmap = (Path(__file__).resolve().parents[1] / "docs/roadmap.md").read_text(
        encoding="utf-8"
    )
    assert "electron-like candidate criteria" not in roadmap
    assert "photon-like candidate" not in roadmap
    assert "Fundamental Temporal Actions" in roadmap
    assert "Emergent Structure Survey" in roadmap


@pytest.mark.parametrize("token", sorted(FORBIDDEN_INGREDIENT_TOKENS))
def test_forbidden_ingredient_tokens_defined(token: str):
    assert isinstance(token, str)
