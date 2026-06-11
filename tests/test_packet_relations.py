"""Tests for packet relations and PacketDelta (Stage 1)."""

import pytest

from tdf_tq import PacketDelta, TemporalPacket, packet_delta, translate_packet
from tdf_tq.relations import (
    delta_tau_matches,
    same_spatial_position,
    same_temporal_layer,
)


def test_packet_delta_accepts_signed_integer_deltas():
    delta = PacketDelta(dN_a=-2, dN_b=3, dN_c=0, dN_t=-1)
    assert delta.spatial_delta == (-2, 3, 0)
    assert delta.delta_tau == -1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dN_a": True, "dN_b": 0, "dN_c": 0, "dN_t": 0},
        {"dN_a": 1.5, "dN_b": 0, "dN_c": 0, "dN_t": 0},
        {"dN_a": 0, "dN_b": "1", "dN_c": 0, "dN_t": 0},
    ],
)
def test_packet_delta_rejects_bool_and_non_integer_values(kwargs):
    with pytest.raises(TypeError):
        PacketDelta(**kwargs)


def test_packet_delta_returns_component_wise_differences():
    packet_a = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=4)
    packet_b = TemporalPacket(N_a=4, N_b=0, N_c=3, N_t=7)
    delta = packet_delta(packet_a, packet_b)
    assert delta.dN_a == 3
    assert delta.dN_b == -2
    assert delta.dN_c == 0
    assert delta.dN_t == 3
    assert delta.spatial_delta == (3, -2, 0)
    assert delta.delta_tau == 3


def test_packet_delta_symmetry():
    packet_a = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=4)
    packet_b = TemporalPacket(N_a=4, N_b=0, N_c=3, N_t=7)
    delta_ab = packet_delta(packet_a, packet_b)
    delta_ba = packet_delta(packet_b, packet_a)
    assert delta_ab.dN_a == -delta_ba.dN_a
    assert delta_ab.dN_b == -delta_ba.dN_b
    assert delta_ab.dN_c == -delta_ba.dN_c
    assert delta_ab.dN_t == -delta_ba.dN_t


def test_translate_packet_produces_expected_packet():
    packet = TemporalPacket(N_a=2, N_b=3, N_c=4, N_t=5)
    delta = PacketDelta(dN_a=1, dN_b=-1, dN_c=0, dN_t=2)
    result = translate_packet(packet, delta)
    assert result == TemporalPacket(N_a=3, N_b=2, N_c=4, N_t=7)


@pytest.mark.parametrize(
    "delta_kwargs",
    [
        {"dN_a": -3, "dN_b": 0, "dN_c": 0, "dN_t": 0},
        {"dN_a": 0, "dN_b": 0, "dN_c": 0, "dN_t": -1},
    ],
)
def test_translate_packet_rejects_negative_resulting_counts(delta_kwargs):
    packet = TemporalPacket(N_a=2, N_b=0, N_c=0, N_t=0)
    delta = PacketDelta(**delta_kwargs)
    with pytest.raises(ValueError, match="non-negative"):
        translate_packet(packet, delta)


def test_same_spatial_position_with_different_n_t():
    packet_a = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=0)
    packet_b = TemporalPacket(N_a=1, N_b=2, N_c=3, N_t=9)
    assert same_spatial_position(packet_a, packet_b)
    packet_c = TemporalPacket(N_a=1, N_b=2, N_c=4, N_t=9)
    assert not same_spatial_position(packet_a, packet_c)


def test_same_temporal_layer_with_different_spatial_counts():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=5)
    packet_b = TemporalPacket(N_a=3, N_b=1, N_c=2, N_t=5)
    assert same_temporal_layer(packet_a, packet_b)
    packet_c = TemporalPacket(N_a=3, N_b=1, N_c=2, N_t=6)
    assert not same_temporal_layer(packet_a, packet_c)


def test_delta_tau_matches():
    packet_a = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=3)
    packet_b = TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=10)
    assert delta_tau_matches(packet_a, packet_b, 7)
    assert not delta_tau_matches(packet_a, packet_b, 6)
