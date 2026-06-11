"""Tests for packet structures (Stage 3B)."""

import pytest

from tdf_tq import (
    DeltaTauField,
    PacketStructure,
    SpatialBounds,
    SpatialSlice,
    TemporalPacket,
    packet_structure_from_field,
    support_overlap_ratio,
    tau_profile_l1_difference,
    uniform_delta_tau_field,
)


def _packets(*specs: tuple[int, int, int, int]) -> tuple[TemporalPacket, ...]:
    return tuple(TemporalPacket(N_a=a, N_b=b, N_c=c, N_t=t) for a, b, c, t in specs)


def test_packet_structure_rejects_empty_packet_tuple():
    with pytest.raises(ValueError):
        PacketStructure(packets=())


def test_packet_structure_rejects_duplicate_spatial_counts():
    packets = _packets((0, 0, 0, 1), (0, 0, 0, 2))
    with pytest.raises(ValueError, match="duplicate"):
        PacketStructure(packets=packets)


def test_spatial_support_is_deterministic_sorted():
    structure = PacketStructure(packets=_packets((1, 0, 0, 1), (0, 1, 0, 2), (0, 0, 0, 3)))
    assert structure.spatial_support() == ((0, 0, 0), (0, 1, 0), (1, 0, 0))


def test_tau_values_maps_spatial_counts_to_n_t():
    structure = PacketStructure(packets=_packets((1, 2, 0, 7)))
    assert structure.tau_values() == {(1, 2, 0): 7}


def test_total_min_max_tau():
    structure = PacketStructure(packets=_packets((0, 0, 0, 2), (1, 0, 0, 8)))
    assert structure.total_tau() == 10
    assert structure.min_tau() == 2
    assert structure.max_tau() == 8


def test_baseline_tau_equals_min_tau():
    structure = PacketStructure(packets=_packets((0, 0, 0, 4), (1, 0, 0, 9)))
    assert structure.baseline_tau() == structure.min_tau()


def test_excess_tau_values():
    structure = PacketStructure(packets=_packets((0, 0, 0, 5), (1, 0, 0, 8)))
    assert structure.excess_tau_values() == {(0, 0, 0): 0, (1, 0, 0): 3}


def test_total_excess_tau():
    structure = PacketStructure(packets=_packets((0, 0, 0, 5), (1, 0, 0, 8), (2, 0, 0, 6)))
    assert structure.total_excess_tau() == 4


def test_support_size_above_baseline():
    structure = PacketStructure(packets=_packets((0, 0, 0, 5), (1, 0, 0, 8), (2, 0, 0, 5)))
    assert structure.support_size_above_baseline() == 1


def test_localization_ratio_uniform_structure():
    structure = PacketStructure(packets=_packets((0, 0, 0, 5), (1, 0, 0, 5)))
    assert structure.localization_ratio() == 0.0


def test_localization_ratio_single_site_excess():
    structure = PacketStructure(packets=_packets((0, 0, 0, 0), (1, 0, 0, 10)))
    assert structure.localization_ratio() == 1.0


def test_center_of_excess_tau_none_for_uniform():
    structure = PacketStructure(packets=_packets((0, 0, 0, 3), (1, 0, 0, 3)))
    assert structure.center_of_excess_tau() is None


def test_center_of_excess_tau_weighted_centroid():
    structure = PacketStructure(packets=_packets((0, 0, 0, 0), (2, 4, 0, 10)))
    assert structure.center_of_excess_tau() == (2.0, 4.0, 0.0)


def test_packet_structure_from_field_preserves_full_packets():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0))
    field = uniform_delta_tau_field(slice_, tau_value=6)
    structure = packet_structure_from_field(field)
    assert structure.packets == (
        TemporalPacket(N_a=0, N_b=0, N_c=0, N_t=6),
        TemporalPacket(N_a=1, N_b=0, N_c=0, N_t=6),
    )


def test_support_overlap_ratio_jaccard():
    a = PacketStructure(packets=_packets((0, 0, 0, 1), (1, 0, 0, 1)))
    b = PacketStructure(packets=_packets((1, 0, 0, 1), (2, 0, 0, 1)))
    assert support_overlap_ratio(a, b) == 1 / 3


def test_tau_profile_l1_difference_same_and_different_supports():
    a = PacketStructure(packets=_packets((0, 0, 0, 5), (1, 0, 0, 7)))
    b = PacketStructure(packets=_packets((0, 0, 0, 5), (1, 0, 0, 3)))
    assert tau_profile_l1_difference(a, b) == 4
    c = PacketStructure(packets=_packets((0, 0, 0, 5), (2, 0, 0, 2)))
    assert tau_profile_l1_difference(a, c) == 9
