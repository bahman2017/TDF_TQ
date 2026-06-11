"""Toy finite-difference proxies from delta-tau fields.

These are count-lattice analysis helpers only—not GR curvature, not Newtonian
gravity, and not physical force.
"""

import math

from tdf_tq.fields import DeltaTauField
from tdf_tq.packets import TemporalPacket

__all__ = [
    "finite_difference_gradient",
    "gradient_magnitude",
    "gravity_like_direction_proxy",
    "laplacian_proxy",
    "normalized_direction",
]


def _require_counts_in_bounds(field: DeltaTauField, counts: tuple[int, int, int]) -> None:
    if not field.slice.bounds.contains_spatial_counts(*counts):
        raise ValueError(f"counts {counts} are outside field bounds")


def _axis_gradient(field: DeltaTauField, counts: tuple[int, int, int], axis: int) -> float:
    bounds = field.slice.bounds
    coords = list(counts)
    maxes = (bounds.max_N_a, bounds.max_N_b, bounds.max_N_c)
    c = coords[axis]
    max_c = maxes[axis]

    def tau_at(delta: int) -> int:
        shifted = list(counts)
        shifted[axis] += delta
        return field.tau_at_counts(shifted[0], shifted[1], shifted[2])

    has_minus = c > 0
    has_plus = c < max_c

    if has_minus and has_plus:
        return (tau_at(1) - tau_at(-1)) / 2.0
    if has_minus:
        return float(tau_at(0) - tau_at(-1))
    if has_plus:
        return float(tau_at(1) - tau_at(0))
    return 0.0


def finite_difference_gradient(
    field: DeltaTauField,
    counts: tuple[int, int, int],
) -> tuple[float, float, float]:
    """Finite-difference gradient of tau with respect to spatial count indices.

    Central differences in the interior; forward/backward at boundaries.
    Step size is one count unit. Not a physical acceleration.
    """
    _require_counts_in_bounds(field, counts)
    return (
        _axis_gradient(field, counts, 0),
        _axis_gradient(field, counts, 1),
        _axis_gradient(field, counts, 2),
    )


def gradient_magnitude(field: DeltaTauField, counts: tuple[int, int, int]) -> float:
    """Euclidean norm of the finite-difference gradient components."""
    grad = finite_difference_gradient(field, counts)
    return math.sqrt(grad[0] ** 2 + grad[1] ** 2 + grad[2] ** 2)


def laplacian_proxy(field: DeltaTauField, counts: tuple[int, int, int]) -> float:
    """Discrete roughness proxy: sum of (neighbor_tau - center_tau).

    Not GR curvature.
    """
    _require_counts_in_bounds(field, counts)
    center_tau = field.tau_at_counts(*counts)
    ref = TemporalPacket(
        N_a=counts[0],
        N_b=counts[1],
        N_c=counts[2],
        N_t=field.slice.N_t,
    )
    total = 0.0
    for neighbor in field.slice.neighbors_within_bounds(ref):
        total += field.tau_at_counts(neighbor.N_a, neighbor.N_b, neighbor.N_c) - center_tau
    return total


def gravity_like_direction_proxy(
    field: DeltaTauField,
    counts: tuple[int, int, int],
) -> tuple[float, float, float]:
    """Negative gradient direction proxy (-grad tau). Force-like proxy only."""
    grad = finite_difference_gradient(field, counts)
    return (-grad[0], -grad[1], -grad[2])


def normalized_direction(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    """Return a unit vector, or (0, 0, 0) when magnitude is zero."""
    magnitude = math.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)
    if magnitude == 0.0:
        return (0.0, 0.0, 0.0)
    return (vector[0] / magnitude, vector[1] / magnitude, vector[2] / magnitude)
