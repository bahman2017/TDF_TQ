"""Deterministic seed patterns for localized structure search."""

from tdf_tq.fields import DeltaTauField
from tdf_tq.neighborhoods import spatial_unit_neighbors
from tdf_tq.packets import TemporalPacket
from tdf_tq.space import SpatialSlice


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def _require_positive_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")


def _spatial_positions(slice_: SpatialSlice) -> tuple[tuple[int, int, int], ...]:
    positions: list[tuple[int, int, int]] = []
    for n_a in range(slice_.bounds.max_N_a + 1):
        for n_b in range(slice_.bounds.max_N_b + 1):
            for n_c in range(slice_.bounds.max_N_c + 1):
                positions.append((n_a, n_b, n_c))
    return tuple(positions)


def _baseline_values(slice_: SpatialSlice, baseline_tau: int) -> dict[tuple[int, int, int], int]:
    return {pos: baseline_tau for pos in _spatial_positions(slice_)}


def _validate_center_in_bounds(slice_: SpatialSlice, center: tuple[int, int, int]) -> None:
    if len(center) != 3:
        raise ValueError("center must be a 3-tuple")
    for name, value in zip(("N_a", "N_b", "N_c"), center):
        _require_non_negative_int(name, value)
    if not slice_.bounds.contains_spatial_counts(*center):
        raise ValueError("center must lie inside slice spatial bounds")


def single_peak_field(
    slice_: SpatialSlice,
    center: tuple[int, int, int],
    baseline_tau: int,
    peak_excess_tau: int,
) -> DeltaTauField:
    """Baseline everywhere with a single peak excess at center."""
    _require_non_negative_int("baseline_tau", baseline_tau)
    _require_positive_int("peak_excess_tau", peak_excess_tau)
    _validate_center_in_bounds(slice_, center)
    values = _baseline_values(slice_, baseline_tau)
    values[center] = baseline_tau + peak_excess_tau
    return DeltaTauField(slice=slice_, values=values)


def plus_cross_field(
    slice_: SpatialSlice,
    center: tuple[int, int, int],
    baseline_tau: int,
    center_excess_tau: int,
    arm_excess_tau: int,
) -> DeltaTauField:
    """Baseline with cross-shaped excess at center and unit-neighbor arms."""
    _require_non_negative_int("baseline_tau", baseline_tau)
    _require_positive_int("center_excess_tau", center_excess_tau)
    _require_positive_int("arm_excess_tau", arm_excess_tau)
    _validate_center_in_bounds(slice_, center)
    values = _baseline_values(slice_, baseline_tau)
    values[center] = baseline_tau + center_excess_tau
    center_packet = TemporalPacket(
        N_a=center[0], N_b=center[1], N_c=center[2], N_t=slice_.N_t
    )
    for neighbor in spatial_unit_neighbors(center_packet):
        if slice_.bounds.contains_packet(neighbor):
            key = (neighbor.N_a, neighbor.N_b, neighbor.N_c)
            values[key] = baseline_tau + arm_excess_tau
    return DeltaTauField(slice=slice_, values=values)


def compact_square_field(
    slice_: SpatialSlice,
    lower_corner: tuple[int, int, int],
    baseline_tau: int,
    block_excess_tau: int,
    size_N_a: int,
    size_N_b: int,
    size_N_c: int = 1,
) -> DeltaTauField:
    """Baseline with a compact rectangular block of excess tau."""
    _require_non_negative_int("baseline_tau", baseline_tau)
    _require_positive_int("block_excess_tau", block_excess_tau)
    _require_positive_int("size_N_a", size_N_a)
    _require_positive_int("size_N_b", size_N_b)
    _require_positive_int("size_N_c", size_N_c)
    _validate_center_in_bounds(slice_, lower_corner)
    values = _baseline_values(slice_, baseline_tau)
    la, lb, lc = lower_corner
    for n_a in range(la, la + size_N_a):
        for n_b in range(lb, lb + size_N_b):
            for n_c in range(lc, lc + size_N_c):
                if not slice_.bounds.contains_spatial_counts(n_a, n_b, n_c):
                    raise ValueError("compact block extends outside slice bounds")
                values[(n_a, n_b, n_c)] = baseline_tau + block_excess_tau
    return DeltaTauField(slice=slice_, values=values)


def deterministic_seed_suite(
    slice_: SpatialSlice,
    baseline_tau: int,
    excess_tau: int,
) -> tuple[tuple[str, DeltaTauField], ...]:
    """Deterministic labeled seeds; omit patterns that do not fit bounds."""
    _require_non_negative_int("baseline_tau", baseline_tau)
    _require_positive_int("excess_tau", excess_tau)
    seeds: list[tuple[str, DeltaTauField]] = []
    center = (
        slice_.bounds.max_N_a // 2,
        slice_.bounds.max_N_b // 2,
        slice_.bounds.max_N_c // 2,
    )
    if slice_.bounds.contains_spatial_counts(*center):
        seeds.append(
            (
                "single_peak_center",
                single_peak_field(slice_, center, baseline_tau, excess_tau),
            )
        )
        seeds.append(
            (
                "plus_cross_center",
                plus_cross_field(
                    slice_, center, baseline_tau, excess_tau, max(1, excess_tau // 2)
                ),
            )
        )
    if (
        slice_.bounds.max_N_a >= 1
        and slice_.bounds.max_N_b >= 1
        and slice_.bounds.contains_spatial_counts(0, 0, 0)
    ):
        try:
            seeds.append(
                (
                    "compact_2x2_corner",
                    compact_square_field(
                        slice_,
                        lower_corner=(0, 0, 0),
                        baseline_tau=baseline_tau,
                        block_excess_tau=excess_tau,
                        size_N_a=2,
                        size_N_b=2,
                        size_N_c=1,
                    ),
                )
            )
        except ValueError:
            pass
    return tuple(seeds)
