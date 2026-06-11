"""Tests for Stage 3C Action outcome metrics."""

from tdf_tq.action_metrics import (
    METRIC_DEFINITIONS,
    compute_action_metrics,
    finite_speed_violation_count,
    phase_coherence_proxy,
)
from tdf_tq.actions import IdentityControlAction, PairwiseRelaxationAction, run_action_steps
from tdf_tq.patterns import single_peak_field
from tdf_tq.space import SpatialBounds, SpatialSlice


def _slice() -> SpatialSlice:
    return SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))


def _peak_field():
    return single_peak_field(_slice(), center=(1, 1, 0), baseline_tau=10, peak_excess_tau=10)


def test_metric_definitions_include_required_keys():
    required = {
        "total_tau",
        "total_tau_change",
        "active_support_size",
        "localization_score",
        "spreading_score",
        "phase_coherence_proxy",
        "effective_geometry_proxy",
        "finite_speed_violation_count",
    }
    assert required <= set(METRIC_DEFINITIONS)


def test_compute_action_metrics_schema():
    field = _peak_field()
    history = run_action_steps(PairwiseRelaxationAction(), field, 3)
    metrics = compute_action_metrics(field, history[-1], history)
    assert metrics["total_tau_change"] == 0
    assert metrics["active_support_size"] >= 1
    assert 0.0 <= metrics["phase_coherence_proxy"] <= 1.0
    assert metrics["effective_geometry_proxy"] >= 0.0


def test_identity_metrics_show_zero_change():
    field = _peak_field()
    history = run_action_steps(IdentityControlAction(), field, 3)
    metrics = compute_action_metrics(field, history[-1], history)
    assert metrics["total_tau_change"] == 0
    assert metrics["finite_speed_violation_count"] == 0


def test_phase_coherence_proxy_bounded():
    field = _peak_field()
    value = phase_coherence_proxy(field)
    assert 0.0 <= value <= 1.0


def test_finite_speed_violation_count_for_identity():
    field = _peak_field()
    history = run_action_steps(IdentityControlAction(), field, 5)
    assert finite_speed_violation_count(history) == 0


def test_spreading_increases_support_under_relaxation():
    field = _peak_field()
    history = run_action_steps(PairwiseRelaxationAction(), field, 8)
    initial_metrics = compute_action_metrics(field, history[1], history[:2])
    final_metrics = compute_action_metrics(field, history[-1], history)
    assert final_metrics["active_support_size"] >= initial_metrics["active_support_size"]
