"""Tests for deterministic seed patterns (Stage 4A)."""

import pytest

from tdf_tq import (
    SpatialBounds,
    SpatialSlice,
    compact_square_field,
    deterministic_seed_suite,
    plus_cross_field,
    single_peak_field,
)


def _slice() -> SpatialSlice:
    return SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))


def test_single_peak_creates_one_active_site():
    field = single_peak_field(_slice(), center=(1, 1, 0), baseline_tau=10, peak_excess_tau=5)
    active = [k for k, v in field.values.items() if v > 10]
    assert active == [(1, 1, 0)]
    assert field.values[(1, 1, 0)] == 15


def test_plus_cross_creates_center_and_arms():
    field = plus_cross_field(
        _slice(), center=(1, 1, 0), baseline_tau=10, center_excess_tau=8, arm_excess_tau=4
    )
    assert field.values[(1, 1, 0)] == 18
    assert field.values[(0, 1, 0)] == 14
    assert field.values[(2, 1, 0)] == 14
    assert field.values[(1, 0, 0)] == 14
    assert field.values[(1, 2, 0)] == 14


def test_plus_cross_handles_boundaries():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=0, max_N_b=0, max_N_c=0))
    field = plus_cross_field(
        slice_, center=(0, 0, 0), baseline_tau=5, center_excess_tau=3, arm_excess_tau=1
    )
    assert field.values[(0, 0, 0)] == 8
    assert len(field.values) == 1


def test_compact_square_creates_expected_block():
    field = compact_square_field(
        _slice(),
        lower_corner=(0, 0, 0),
        baseline_tau=10,
        block_excess_tau=6,
        size_N_a=2,
        size_N_b=2,
    )
    block_sites = {(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)}
    for site in block_sites:
        assert field.values[site] == 16
    assert field.values[(2, 2, 0)] == 10


def test_pattern_constructors_reject_invalid_inputs():
    with pytest.raises(ValueError):
        single_peak_field(_slice(), center=(5, 0, 0), baseline_tau=10, peak_excess_tau=1)
    with pytest.raises(ValueError):
        single_peak_field(_slice(), center=(0, 0, 0), baseline_tau=-1, peak_excess_tau=1)
    with pytest.raises(ValueError):
        single_peak_field(_slice(), center=(0, 0, 0), baseline_tau=10, peak_excess_tau=0)
    with pytest.raises(ValueError):
        compact_square_field(
            _slice(), (0, 0, 0), 10, 5, size_N_a=0, size_N_b=2
        )


def test_deterministic_seed_suite_is_deterministic_and_omits_impossible():
    slice_ = _slice()
    suite_a = deterministic_seed_suite(slice_, baseline_tau=10, excess_tau=5)
    suite_b = deterministic_seed_suite(slice_, baseline_tau=10, excess_tau=5)
    assert suite_a == suite_b
    labels = [label for label, _ in suite_a]
    assert "single_peak_center" in labels
    assert "plus_cross_center" in labels
    assert "compact_2x2_corner" in labels

    tiny = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=0, max_N_b=0, max_N_c=0))
    tiny_suite = deterministic_seed_suite(tiny, 10, 5)
    assert len(tiny_suite) == 2
