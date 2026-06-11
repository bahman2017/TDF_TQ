"""Tests for spatial neighborhood primitives (Stage 1)."""

import pytest

from tdf_tq import TemporalPacket, is_spatial_unit_neighbor, spatial_unit_axis, spatial_unit_neighbors


def test_spatial_unit_neighbors_at_origin_returns_positive_axis_neighbors_only():
    origin = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2)
    neighbors = spatial_unit_neighbors(origin)
    assert len(neighbors) == 3
    assert TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=2) in neighbors
    assert TemporalPacket(N_a=0, N_b=1, N_c=0, N_t=2) in neighbors
    assert TemporalPacket(N_a=0, N_b=0, N_c=1, N_t=2) in neighbors
    for neighbor in neighbors:
        assert neighbor.N_t == origin.N_t


def test_spatial_unit_neighbors_interior_returns_six_neighbors():
    interior = TemporalPacket(N_a=1, N_b=1, N_c=1, N_t=0)
    neighbors = spatial_unit_neighbors(interior)
    assert len(neighbors) == 6
    expected = {
        TemporalPacket(N_a=0, N_b=1, N_c=1, N_t=0),
        TemporalPacket(N_a=2, N_b=1, N_c=1, N_t=0),
        TemporalPacket(N_a=1, N_b=0, N_c=1, N_t=0),
        TemporalPacket(N_a=1, N_b=2, N_c=1, N_t=0),
        TemporalPacket(N_a=1, N_b=1, N_c=0, N_t=0),
        TemporalPacket(N_a=1, N_b=1, N_c=2, N_t=0),
    }
    assert set(neighbors) == expected


def test_is_spatial_unit_neighbor_rejects_diagonal_moves():
    packet_a = TemporalPacket(N_a=1, N_b=1, N_c=0, N_t=3)
    packet_b = TemporalPacket(N_a=2, N_b=2, N_c=0, N_t=3)
    assert not is_spatial_unit_neighbor(packet_a, packet_b)


def test_is_spatial_unit_neighbor_rejects_temporal_layer_changes():
    packet_a = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=3)
    packet_b = TemporalPacket(N_a=2, N_b=0, N_c=0, N_t=4)
    assert not is_spatial_unit_neighbor(packet_a, packet_b)


@pytest.mark.parametrize(
    "packet_a, packet_b, expected_axis",
    [
        (
            TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=0),
            TemporalPacket(N_a=2, N_b=0, N_c=0, N_t=0),
            "N_a",
        ),
        (
            TemporalPacket(N_a=0, N_b=3, N_c=0, N_t=1),
            TemporalPacket(N_a=0, N_b=2, N_c=0, N_t=1),
            "N_b",
        ),
        (
            TemporalPacket(N_a=0, N_b=0, N_c=5, N_t=2),
            TemporalPacket(N_a=0, N_b=0, N_c=6, N_t=2),
            "N_c",
        ),
    ],
)
def test_spatial_unit_axis_returns_correct_axis(packet_a, packet_b, expected_axis):
    assert is_spatial_unit_neighbor(packet_a, packet_b)
    assert spatial_unit_axis(packet_a, packet_b) == expected_axis


def test_spatial_unit_axis_returns_none_for_invalid_pairs():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=2, N_b=0, N_c=0, N_t=0)
    assert spatial_unit_axis(packet_a, packet_b) is None

    packet_c = TemporalPacket(N_a=1, N_b=1, N_c=0, N_t=0)
    assert spatial_unit_axis(packet_a, packet_c) is None
