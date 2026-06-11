"""Tests for Stage 3C Action interface and step implementations."""

import pytest

from tdf_tq.actions import (
    ActionEvolutionState,
    FinitePropagationDelayAction,
    IdentityControlAction,
    MemoryWeightedRelaxationAction,
    PairwiseRelaxationAction,
    ThresholdRelaxationAction,
    default_action_catalog,
    run_action_steps,
)
from tdf_tq.patterns import single_peak_field
from tdf_tq.space import SpatialBounds, SpatialSlice


def _slice() -> SpatialSlice:
    return SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))


def _peak_field():
    return single_peak_field(_slice(), center=(1, 1, 0), baseline_tau=10, peak_excess_tau=10)


def test_action_catalog_has_seven_actions():
    catalog = default_action_catalog()
    assert len(catalog) == 7
    ids = [action.spec.action_id for action in catalog]
    assert ids == [
        "A0_identity_control",
        "A1_pairwise_relaxation",
        "A2_threshold_relaxation",
        "A3_memory_weighted_relaxation",
        "A4_finite_propagation_delay",
        "A5_local_curvature_pressure",
        "A6_phase_coherence_probe",
    ]


def test_action_spec_required_fields():
    action = IdentityControlAction()
    spec = action.spec
    assert spec.action_id
    assert spec.description
    assert spec.allowed_ingredients
    assert spec.forbidden_encoded_physics
    assert spec.conservation_notes
    assert spec.boundary_notes
    assert spec.maturity_level == "C"


def test_identity_control_remains_unchanged():
    field = _peak_field()
    action = IdentityControlAction()
    result = action.step(field)
    assert dict(result.values) == dict(field.values)


def test_pairwise_relaxation_conserves_total_tau():
    field = _peak_field()
    action = PairwiseRelaxationAction()
    before = sum(field.values.values())
    after = action.step(field)
    assert sum(after.values.values()) == before


def test_threshold_relaxation_is_deterministic():
    field = _peak_field()
    action = ThresholdRelaxationAction()
    assert dict(action.step(field).values) == dict(action.step(field).values)


def test_memory_action_deterministic_with_state():
    field = _peak_field()
    action = MemoryWeightedRelaxationAction()
    state = ActionEvolutionState(previous_field=field)
    first = action.step(field, state=state)
    second = action.step(field, state=state)
    assert dict(first.values) == dict(second.values)


def test_finite_propagation_action_at_most_one_transfer():
    field = _peak_field()
    action = FinitePropagationDelayAction()
    before = sum(field.values.values())
    after = action.step(field)
    assert sum(after.values.values()) == before
    changed_sites = sum(1 for k in field.values if field.values[k] != after.values[k])
    assert changed_sites <= 2


def test_run_action_steps_reproducible():
    field = _peak_field()
    action = PairwiseRelaxationAction()
    run_a = run_action_steps(action, field, 5)
    run_b = run_action_steps(action, field, 5)
    assert [dict(f.values) for f in run_a] == [dict(f.values) for f in run_b]


def test_run_action_steps_rejects_negative_steps():
    field = _peak_field()
    with pytest.raises(ValueError):
        run_action_steps(IdentityControlAction(), field, -1)


def test_default_action_catalog_count():
    assert len(default_action_catalog()) == 7
