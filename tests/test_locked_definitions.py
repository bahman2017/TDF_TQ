"""Tests aligned with locked TDF_TQ definitions (Stage 0)."""

import math

import pytest

from tdf_tq import TemporalPacket, delta_tau, emergent_euclidean_distance, working_speed_limit


def test_temporal_packet_accepts_valid_non_negative_integers():
    packet = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=4)
    assert packet.N_a == 1
    assert packet.N_b == 2
    assert packet.N_c == 3
    assert packet.N_t == 4


@pytest.mark.parametrize(
    "kwargs",
    [
        {"N_a": -1, "N_b": 0, "N_c": 0, "N_t": 0},
        {"N_a": 0, "N_b": -1, "N_c": 0, "N_t": 0},
        {"N_a": 0, "N_b": 0, "N_c": -1, "N_t": 0},
        {"N_a": 0, "N_b": 0, "N_c": 0, "N_t": -1},
    ],
)
def test_temporal_packet_rejects_negative_values(kwargs):
    with pytest.raises(ValueError):
        TemporalPacket(**kwargs)


def test_tau_equals_n_t():
    packet = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=7)
    assert packet.tau == packet.N_t
    assert packet.tau == 7


def test_delta_tau_equals_delta_n_t():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=3)
    packet_b = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=10)
    assert delta_tau(packet_a, packet_b) == packet_b.N_t - packet_a.N_t
    assert delta_tau(packet_a, packet_b) == 7


def test_emergent_distance_unit_step_along_n_a():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=5)
    packet_b = TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=5)
    l_q = 2.5
    assert emergent_euclidean_distance(packet_a, packet_b, l_q=l_q) == l_q


def test_working_speed_limit_computation():
    assert working_speed_limit(2, 4) == 0.5


@pytest.mark.parametrize("t_q", [0, -1, -0.001])
def test_working_speed_limit_rejects_non_positive_t_q(t_q):
    with pytest.raises(ValueError, match="t_q must be strictly positive"):
        working_speed_limit(1.0, t_q)


def test_spatial_counts_property():
    packet = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=0)
    assert packet.spatial_counts == (1, 2, 3)


def test_emergent_distance_zero_for_identical_packets():
    packet = TemporalPacket(N_a=2, N_b=3, N_c=4, N_t=1)
    assert emergent_euclidean_distance(packet, packet) == 0.0


def test_emergent_distance_pythagorean():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=0)
    packet_b = TemporalPacket(N_a=3, N_b=4, N_c=0, N_t=0)
    l_q = 1.0
    expected = l_q * math.sqrt(9 + 16)
    assert emergent_euclidean_distance(packet_a, packet_b, l_q=l_q) == expected
