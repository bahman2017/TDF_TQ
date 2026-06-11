"""Tests for active-support diagnostics (Stage 4A)."""

import pytest

from tdf_tq import (
    PacketStructure,
    TemporalPacket,
    active_center_of_excess_tau,
    active_support_above_baseline,
    active_support_overlap_ratio,
    active_support_size_above_baseline,
    active_tau_profile_l1_difference,
    active_tau_values_above_baseline,
    support_overlap_ratio,
)


def _structure(*specs: tuple[int, int, int, int]) -> PacketStructure:
    return PacketStructure(
        packets=tuple(TemporalPacket(N_a=a, N_b=b, N_c=c, N_t=t) for a, b, c, t in specs)
    )


def test_active_support_returns_only_sites_above_baseline():
    structure = _structure((0, 0, 0, 5), (1, 0, 0, 8), (2, 0, 0, 5))
    assert active_support_above_baseline(structure, baseline=5) == ((1, 0, 0),)


def test_active_support_empty_for_uniform_structure():
    structure = _structure((0, 0, 0, 7), (1, 0, 0, 7))
    assert active_support_above_baseline(structure) == ()


def test_active_support_size_above_baseline():
    structure = _structure((0, 0, 0, 0), (1, 0, 0, 4), (2, 0, 0, 2))
    assert active_support_size_above_baseline(structure, baseline=0) == 2


def test_active_tau_values_above_baseline_returns_excess_only():
    structure = _structure((0, 0, 0, 10), (1, 0, 0, 15))
    assert active_tau_values_above_baseline(structure, baseline=10) == {(1, 0, 0): 5}


def test_active_center_none_for_no_active_excess():
    structure = _structure((0, 0, 0, 3), (1, 0, 0, 3))
    assert active_center_of_excess_tau(structure) is None


def test_active_center_weighted_centroid():
    structure = _structure((0, 0, 0, 0), (2, 4, 0, 10))
    assert active_center_of_excess_tau(structure, baseline=0) == (2.0, 4.0, 0.0)


def test_active_support_overlap_uses_active_not_full_lattice():
    full = _structure((0, 0, 0, 5), (1, 0, 0, 5), (2, 0, 0, 5))
    peak_a = _structure((0, 0, 0, 5), (1, 0, 0, 10), (2, 0, 0, 5))
    peak_b = _structure((0, 0, 0, 5), (1, 0, 0, 5), (2, 0, 0, 10))
    assert support_overlap_ratio(full, full) == 1.0
    assert active_support_overlap_ratio(peak_a, peak_b, baseline_a=5, baseline_b=5) == 0.0


def test_active_tau_profile_l1_difference_with_missing_active_sites():
    a = _structure((0, 0, 0, 10), (1, 0, 0, 15))
    b = _structure((0, 0, 0, 10), (2, 0, 0, 12))
    assert active_tau_profile_l1_difference(a, b, baseline_a=10, baseline_b=10) == 7


def test_fixed_baseline_differs_from_per_step_min_baseline():
    structure = _structure((0, 0, 0, 5), (1, 0, 0, 12))
    fixed = active_support_size_above_baseline(structure, baseline=5)
    dynamic = active_support_size_above_baseline(structure, baseline=None)
    assert fixed == 1
    assert dynamic == 1
    structure2 = _structure((0, 0, 0, 3), (1, 0, 0, 8))
    assert active_support_size_above_baseline(structure2, baseline=3) == 1
    assert active_support_size_above_baseline(structure2) == 1

