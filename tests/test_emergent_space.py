"""Tests for emergent spatial regions (Stage 2)."""

import pytest

from tdf_tq import SpatialBounds, SpatialSlice, TemporalPacket


def test_spatial_bounds_accepts_valid_non_negative_integer_bounds():
    bounds = SpatialBounds(max_N_a=2, max_N_b=3, max_N_c=1)
    assert bounds.max_N_a == 2
    assert bounds.max_N_b == 3
    assert bounds.max_N_c == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_N_a": -1, "max_N_b": 0, "max_N_c": 0},
        {"max_N_a": True, "max_N_b": 0, "max_N_c": 0},
        {"max_N_a": 1.0, "max_N_b": 0, "max_N_c": 0},
    ],
)
def test_spatial_bounds_rejects_invalid_values(kwargs):
    with pytest.raises((TypeError, ValueError)):
        SpatialBounds(**kwargs)


def test_spatial_bounds_contains_packet():
    bounds = SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=2)
    inside = TemporalPacket(N_a=1, N_b=2, N_c=0, N_t=5)
    outside = TemporalPacket(N_a=3, N_b=0, N_c=0, N_t=5)
    assert bounds.contains_packet(inside)
    assert not bounds.contains_packet(outside)
    assert bounds.contains_spatial_counts(2, 2, 2)
    assert not bounds.contains_spatial_counts(2, 2, 3)


def test_spatial_slice_validates_n_t():
    bounds = SpatialBounds(max_N_a=1, max_N_b=1, max_N_c=1)
    with pytest.raises((TypeError, ValueError)):
        SpatialSlice(N_t=-1, bounds=bounds)
    with pytest.raises(TypeError):
        SpatialSlice(N_t=True, bounds=bounds)


def test_spatial_slice_packets_count():
    bounds = SpatialBounds(max_N_a=2, max_N_b=1, max_N_c=0)
    slice_ = SpatialSlice(N_t=3, bounds=bounds)
    assert len(slice_.packets()) == (2 + 1) * (1 + 1) * (0 + 1)


def test_spatial_slice_packets_all_have_fixed_n_t():
    slice_ = SpatialSlice(
        N_t=7,
        bounds=SpatialBounds(max_N_a=1, max_N_b=1, max_N_c=1),
    )
    for packet in slice_.packets():
        assert packet.N_t == 7


def test_neighbors_within_bounds_returns_only_in_bound_neighbors():
    slice_ = SpatialSlice(
        N_t=0,
        bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0),
    )
    corner = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    neighbors = slice_.neighbors_within_bounds(corner)
    assert len(neighbors) == 1
    assert neighbors[0] == TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=0)

    interior = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=0)
    neighbors = slice_.neighbors_within_bounds(interior)
    assert len(neighbors) == 1
    assert neighbors[0] == TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)


def test_neighbors_within_bounds_boundary_is_deterministic():
    slice_ = SpatialSlice(
        N_t=2,
        bounds=SpatialBounds(max_N_a=1, max_N_b=1, max_N_c=0),
    )
    packet = TemporalPacket(N_a=1, N_b=1, N_c=0, N_t=2)
    neighbors = slice_.neighbors_within_bounds(packet)
    expected = (
        TemporalPacket(N_a=0, N_b=1, N_c=0, N_t=2),
        TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=2),
    )
    assert neighbors == expected


def test_neighbors_within_bounds_rejects_packet_not_in_slice():
    slice_ = SpatialSlice(
        N_t=0,
        bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0),
    )
    packet = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=1)
    with pytest.raises(ValueError, match="not contained"):
        slice_.neighbors_within_bounds(packet)


def test_zero_size_slice_has_one_packet_and_zero_neighbors():
    slice_ = SpatialSlice(
        N_t=4,
        bounds=SpatialBounds(max_N_a=0, max_N_b=0, max_N_c=0),
    )
    packets = slice_.packets()
    assert len(packets) == 1
    assert packets[0] == TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=4)
    assert slice_.neighbors_within_bounds(packets[0]) == ()
