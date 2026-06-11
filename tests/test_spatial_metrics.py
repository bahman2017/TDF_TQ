"""Tests for provisional spatial metrics (Stage 2)."""

import math

import pytest

from tdf_tq import (
    TemporalPacket,
    deterministic_spatial_path,
    emergent_euclidean_distance,
    emergent_manhattan_distance,
    emergent_unit_edge_length,
    is_spatial_unit_neighbor,
    spatial_count_l1_distance,
    spatial_graph_distance_steps,
)


def test_spatial_count_l1_distance_ignores_n_t():
    packet_a = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=0)
    packet_b = TemporalPacket(N_a=4, N_b=0, N_c=3, N_t=99)
    assert spatial_count_l1_distance(packet_a, packet_b) == 3 + 2 + 0


def test_emergent_manhattan_distance_scales_by_l_q():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=1)
    packet_b = TemporalPacket(N_a=2, N_b=1, N_c=0, N_t=1)
    assert emergent_manhattan_distance(packet_a, packet_b, l_q=1.5) == 4.5


@pytest.mark.parametrize("l_q", [0, -1.0])
def test_emergent_manhattan_distance_rejects_non_positive_l_q(l_q):
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=0)
    with pytest.raises(ValueError, match="l_q must be strictly positive"):
        emergent_manhattan_distance(packet_a, packet_b, l_q=l_q)


def test_emergent_unit_edge_length_returns_l_q_for_unit_neighbors():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2)
    packet_b = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=2)
    assert emergent_unit_edge_length(packet_a, packet_b, l_q=1.5) == 1.5


def test_emergent_unit_edge_length_rejects_diagonal_moves():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=1, N_c=0, N_t=0)
    with pytest.raises(ValueError):
        emergent_unit_edge_length(packet_a, packet_b)


def test_emergent_unit_edge_length_rejects_temporal_layer_changes():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=1)
    with pytest.raises(ValueError):
        emergent_unit_edge_length(packet_a, packet_b)


def test_spatial_graph_distance_steps_equals_l1_for_same_n_t():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2)
    packet_b = TemporalPacket(N_a=2, N_b=1, N_c=0, N_t=2)
    assert spatial_graph_distance_steps(packet_a, packet_b) == 3
    assert spatial_graph_distance_steps(packet_a, packet_b) == spatial_count_l1_distance(
        packet_a, packet_b
    )


def test_spatial_graph_distance_steps_rejects_different_n_t():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=1)
    with pytest.raises(ValueError, match="same N_t"):
        spatial_graph_distance_steps(packet_a, packet_b)


def test_deterministic_spatial_path_length_equals_graph_distance_plus_one():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2)
    packet_b = TemporalPacket(N_a=2, N_b=1, N_c=0, N_t=2)
    path = deterministic_spatial_path(packet_a, packet_b)
    steps = spatial_graph_distance_steps(packet_a, packet_b)
    assert len(path) == steps + 1


def test_deterministic_spatial_path_consecutive_packets_are_neighbors():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2)
    packet_b = TemporalPacket(N_a=2, N_b=1, N_c=0, N_t=2)
    path = deterministic_spatial_path(packet_a, packet_b)
    for left, right in zip(path, path[1:]):
        assert is_spatial_unit_neighbor(left, right)


def test_deterministic_spatial_path_axis_order():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2)
    packet_b = TemporalPacket(N_a=2, N_b=1, N_c=0, N_t=2)
    path = deterministic_spatial_path(packet_a, packet_b)
    expected = (
        TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=2),
        TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=2),
        TemporalPacket(N_a=2, N_b=0, N_c=0, N_t=2),
        TemporalPacket(N_a=2, N_b=1, N_c=0, N_t=2),
    )
    assert path == expected


def test_deterministic_spatial_path_rejects_different_n_t():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=1)
    with pytest.raises(ValueError, match="same N_t"):
        deterministic_spatial_path(packet_a, packet_b)


def test_spatial_metrics_zero_when_only_n_t_differs():
    packet_a = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=10)
    assert spatial_count_l1_distance(packet_a, packet_b) == 0
    assert emergent_manhattan_distance(packet_a, packet_b) == 0.0
    assert emergent_euclidean_distance(packet_a, packet_b) == 0.0


@pytest.mark.parametrize(
    "a, b, c",
    [
        (
            TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0),
            TemporalPacket(N_a=2, N_b=0, N_c=0, N_t=0),
            TemporalPacket(N_a=2, N_b=3, N_c=0, N_t=0),
        ),
        (
            TemporalPacket(N_a=1, N_b=1, N_c=1, N_t=1),
            TemporalPacket(N_a=3, N_b=1, N_c=1, N_t=1),
            TemporalPacket(N_a=3, N_b=4, N_c=2, N_t=1),
        ),
    ],
)
def test_triangle_inequality_manhattan(a, b, c):
    d_ab = emergent_manhattan_distance(a, b)
    d_bc = emergent_manhattan_distance(b, c)
    d_ac = emergent_manhattan_distance(a, c)
    assert d_ac <= d_ab + d_bc + 1e-12


def test_euclidean_and_manhattan_use_spatial_counts_only():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=3, N_b=4, N_c=0, N_t=99)
    l_q = 2.0
    assert emergent_manhattan_distance(packet_a, packet_b, l_q=l_q) == l_q * 7
    assert emergent_euclidean_distance(packet_a, packet_b, l_q=l_q) == l_q * math.sqrt(25)
