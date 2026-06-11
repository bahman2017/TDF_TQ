"""Tests for localized candidate evaluation (Stage 4A)."""

import inspect

import pytest

from tdf_tq import (
    DeltaTauField,
    FieldEvolutionConfig,
    LocalizedCandidateCriteria,
    PacketStructure,
    SpatialBounds,
    SpatialSlice,
    TemporalPacket,
    evaluate_localized_candidate,
    packet_structure_from_field,
    run_field_evolution,
    single_peak_field,
    structure_history_from_field_sequence,
    uniform_delta_tau_field,
)
from tdf_tq import candidates as candidates_module


def _structure(label: str, *specs: tuple[int, int, int, int]) -> PacketStructure:
    packets = tuple(TemporalPacket(N_a=a, N_b=b, N_c=c, N_t=t) for a, b, c, t in specs)
    return PacketStructure(packets=packets, label=label)


def test_localized_candidate_criteria_validates_inputs():
    LocalizedCandidateCriteria()
    with pytest.raises(ValueError):
        LocalizedCandidateCriteria(min_final_localization_ratio=1.5)
    with pytest.raises(TypeError):
        LocalizedCandidateCriteria(require_total_tau_conserved="yes")


def test_uniform_history_evaluates_as_fail():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0))
    field = uniform_delta_tau_field(slice_, tau_value=10)
    history = structure_history_from_field_sequence((field, field), label_prefix="uniform")
    result = evaluate_localized_candidate(history, seed_label="uniform")
    assert result.verdict == "FAIL"
    assert not result.passed


def test_identity_single_peak_can_satisfy_criteria_with_limitations():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))
    field = single_peak_field(slice_, center=(1, 1, 0), baseline_tau=10, peak_excess_tau=10)
    fields = run_field_evolution(field, steps=2, step_kind="identity")
    history = structure_history_from_field_sequence(fields, label_prefix="peak")
    criteria = LocalizedCandidateCriteria(
        min_final_localization_ratio=0.5,
        max_center_drift=0.5,
        max_active_tau_profile_l1_step_change=0,
        min_active_support_overlap=1.0,
    )
    result = evaluate_localized_candidate(history, criteria=criteria, seed_label="peak")
    assert result.passed
    assert result.verdict == "PASS_TO_STAGE_4B"
    assert "not an electron" in result.limitations[0]


def test_relaxation_spread_can_fail_when_localization_drops():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))
    field = single_peak_field(slice_, center=(1, 1, 0), baseline_tau=10, peak_excess_tau=10)
    fields = run_field_evolution(
        field, steps=3, config=FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)
    )
    history = structure_history_from_field_sequence(fields, label_prefix="spread")
    criteria = LocalizedCandidateCriteria(min_final_localization_ratio=0.5)
    result = evaluate_localized_candidate(history, criteria=criteria, seed_label="spread")
    assert not result.passed
    assert result.metrics["final_active_localization_ratio"] < 0.5


def test_evaluate_uses_active_support_not_full_support():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=0, max_N_c=0))
    values = {(n_a, 0, 0): 10 for n_a in range(3)}
    values[(1, 0, 0)] = 20
    field = DeltaTauField(slice=slice_, values=values)
    history = structure_history_from_field_sequence((field,), label_prefix="active")
    result = evaluate_localized_candidate(history, seed_label="active")
    assert result.metrics["initial_active_support_size"] == 1
    assert result.metrics["initial_active_support_size"] != 3


def test_candidate_evaluation_verdict_is_deterministic():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0))
    field = single_peak_field(slice_, center=(0, 0, 0), baseline_tau=5, peak_excess_tau=3)
    history = structure_history_from_field_sequence((field,), label_prefix="d")
    r1 = evaluate_localized_candidate(history, seed_label="d")
    r2 = evaluate_localized_candidate(history, seed_label="d")
    assert r1.verdict == r2.verdict
    assert r1.passed == r2.passed


def test_no_electron_or_physical_claims_in_candidates_module():
    source = inspect.getsource(candidates_module)
    lowered = source.lower()
    for token in ("hbar", "alpha", "positron", "quantum mechanics", "mass"):
        assert token not in lowered
    assert "not an electron" in candidates_module._LIMITATION
