"""Tests for delta-tau fields (Stage 3A)."""

import pytest

from tdf_tq import (
    DeltaTauField,
    SpatialBounds,
    SpatialSlice,
    TemporalPacket,
    radial_delta_tau_field,
    uniform_delta_tau_field,
)


def _small_slice() -> SpatialSlice:
    return SpatialSlice(
        N_t=0,
        bounds=SpatialBounds(max_N_a=1, max_N_b=1, max_N_c=0),
    )


def test_uniform_field_fills_every_spatial_position():
    slice_ = _small_slice()
    field = uniform_delta_tau_field(slice_, tau_value=7)
    assert len(field.values) == 4
    assert all(v == 7 for v in field.values.values())


def test_field_rejects_missing_positions():
    slice_ = _small_slice()
    with pytest.raises(ValueError, match="missing"):
        DeltaTauField(slice=slice_, values={(0, 0, 0): 1})


def test_field_rejects_extra_out_of_bounds_positions():
    slice_ = _small_slice()
    values = {(n_a, n_b, 0): 1 for n_a in range(2) for n_b in range(2)}
    values[(2, 0, 0)] = 1
    with pytest.raises(ValueError):
        DeltaTauField(slice=slice_, values=values)


def test_field_rejects_negative_tau_values():
    slice_ = _small_slice()
    values = {(n_a, n_b, 0): -1 for n_a in range(2) for n_b in range(2)}
    with pytest.raises(ValueError):
        DeltaTauField(slice=slice_, values=values)


def test_field_rejects_bool_tau_values():
    slice_ = _small_slice()
    values = {(0, 0, 0): True, (0, 1, 0): 1, (1, 0, 0): 1, (1, 1, 0): 1}
    with pytest.raises(TypeError):
        DeltaTauField(slice=slice_, values=values)


def test_tau_at_counts_returns_expected_values():
    slice_ = _small_slice()
    field = uniform_delta_tau_field(slice_, tau_value=5)
    assert field.tau_at_counts(1, 0, 0) == 5


def test_tau_at_packet_uses_spatial_counts():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0))
    field = uniform_delta_tau_field(slice_, tau_value=3)
    packet = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=99)
    assert field.tau_at_packet(packet) == 3


def test_delta_tau_between_counts_equals_difference():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=0, max_N_c=0))
    values = {(0, 0, 0): 10, (1, 0, 0): 14, (2, 0, 0): 18}
    field = DeltaTauField(slice=slice_, values=values)
    assert field.delta_tau_between_counts((0, 0, 0), (2, 0, 0)) == 8


def test_as_packets_with_local_tau_deterministic_order():
    slice_ = _small_slice()
    field = uniform_delta_tau_field(slice_, tau_value=2)
    packets = field.as_packets_with_local_tau()
    assert packets == (
        TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2),
        TemporalPacket(N_a=0, N_b=1, N_c=0, N_t=2),
        TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=2),
        TemporalPacket(N_a=1, N_b=1, N_c=0, N_t=2),
    )


def test_mean_min_max_tau():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0))
    values = {(0, 0, 0): 2, (1, 0, 0): 8}
    field = DeltaTauField(slice=slice_, values=values)
    assert field.mean_tau() == 5.0
    assert field.min_tau() == 2
    assert field.max_tau() == 8


def test_radial_field_strength_zero_equals_uniform_base_tau():
    slice_ = _small_slice()
    field = radial_delta_tau_field(slice_, center=(0, 0, 0), base_tau=10, strength=0)
    assert field.min_tau() == 10
    assert field.max_tau() == 10


def test_radial_field_increases_with_manhattan_distance():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=0, max_N_c=0))
    field = radial_delta_tau_field(slice_, center=(0, 0, 0), base_tau=0, strength=1)
    assert field.tau_at_counts(0, 0, 0) == 0
    assert field.tau_at_counts(1, 0, 0) == 1
    assert field.tau_at_counts(2, 0, 0) == 2


def test_radial_field_rejects_center_outside_bounds():
    slice_ = _small_slice()
    with pytest.raises(ValueError, match="center"):
        radial_delta_tau_field(slice_, center=(5, 0, 0), base_tau=0, strength=1)


def test_radial_field_rejects_negative_strength():
    slice_ = _small_slice()
    with pytest.raises(ValueError):
        radial_delta_tau_field(slice_, center=(0, 0, 0), base_tau=0, strength=-1)
