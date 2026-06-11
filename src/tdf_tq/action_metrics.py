"""Stage 3C outcome metrics for Action benchmark runs.

These are toy diagnostic scores only—not real energy, curvature, mass, gravity, or quantum phase.
"""

from __future__ import annotations

import cmath
import math
from typing import Any

from tdf_tq.fields import DeltaTauField
from tdf_tq.gravity_proxy import finite_difference_gradient, gradient_magnitude, laplacian_proxy
from tdf_tq.metrics import emergent_manhattan_distance
from tdf_tq.packets import TemporalPacket
from tdf_tq.structure import (
    active_center_of_excess_tau,
    active_localization_ratio,
    active_support_size_above_baseline,
    packet_structure_from_field,
)

METRIC_DEFINITIONS: dict[str, str] = {
    "total_tau": "Sum of tau over all lattice sites (not physical energy).",
    "total_tau_change": "Final minus initial total tau (conservation diagnostic).",
    "active_support_size": "Count of sites with tau above baseline excess threshold.",
    "support_centroid": "Active-excess weighted centroid on count lattice.",
    "centroid_drift": "Manhattan drift of active centroid from initial to final.",
    "max_tau": "Maximum tau on lattice.",
    "min_tau": "Minimum tau on lattice.",
    "tau_variance": "Variance of tau values across lattice sites.",
    "tau_gradient_l1": "Sum of gradient magnitudes over interior/boundary sites.",
    "discrete_laplacian_energy_proxy": "Sum of squared discrete Laplacian proxy values.",
    "propagation_radius": "Max Manhattan radius of active support from centroid.",
    "finite_speed_violation_count": "Steps where active support grew beyond one-hop envelope.",
    "localization_score": "Active localization ratio at final step.",
    "spreading_score": "Normalized increase in active support size.",
    "oscillation_score": "Normalized sign-change score of profile L1 deltas.",
    "recurrence_score": "Similarity of final profile to earliest nontrivial step.",
    "memory_sensitivity_score": "Mean absolute step change (memory diagnostic).",
    "phase_coherence_proxy": "Bounded |mean(exp(-i * excess_tau))| over active sites.",
    "effective_geometry_proxy": "Mean gradient magnitude (geometry diagnostic only).",
}


def _spatial_positions(field: DeltaTauField) -> tuple[tuple[int, int, int], ...]:
    positions: list[tuple[int, int, int]] = []
    b = field.slice.bounds
    for n_a in range(b.max_N_a + 1):
        for n_b in range(b.max_N_b + 1):
            for n_c in range(b.max_N_c + 1):
                positions.append((n_a, n_b, n_c))
    return tuple(positions)


def _total_tau(field: DeltaTauField) -> int:
    return sum(field.values.values())


def _tau_variance(field: DeltaTauField) -> float:
    values = list(field.values.values())
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def _tau_gradient_l1(field: DeltaTauField) -> float:
    total = 0.0
    for site in _spatial_positions(field):
        total += gradient_magnitude(field, site)
    return total


def _discrete_laplacian_energy_proxy(field: DeltaTauField) -> float:
    total = 0.0
    for site in _spatial_positions(field):
        lap = laplacian_proxy(field, site)
        total += lap * lap
    return total


def _active_support_set(field: DeltaTauField, baseline: int) -> set[tuple[int, int, int]]:
    return {
        key
        for key, tau in field.values.items()
        if tau > baseline
    }


def _propagation_radius(field: DeltaTauField, baseline: int) -> float:
    structure = packet_structure_from_field(field)
    centroid = active_center_of_excess_tau(structure, baseline)
    if centroid is None:
        return 0.0
    cx, cy, cz = centroid
    active = _active_support_set(field, baseline)
    if not active:
        return 0.0
    center_packet = TemporalPacket(
        N_a=int(round(cx)), N_b=int(round(cy)), N_c=int(round(cz)), N_t=field.slice.N_t
    )
    max_radius = 0.0
    for site in active:
        packet = TemporalPacket(N_a=site[0], N_b=site[1], N_c=site[2], N_t=field.slice.N_t)
        max_radius = max(max_radius, float(emergent_manhattan_distance(center_packet, packet)))
    return max_radius


def _one_hop_envelope(support: set[tuple[int, int, int]], slice_) -> set[tuple[int, int, int]]:
    envelope = set(support)
    for site in support:
        packet = TemporalPacket(N_a=site[0], N_b=site[1], N_c=site[2], N_t=slice_.N_t)
        for neighbor in slice_.neighbors_within_bounds(packet):
            envelope.add((neighbor.N_a, neighbor.N_b, neighbor.N_c))
    return envelope


def finite_speed_violation_count(
    history: tuple[DeltaTauField, ...],
    baseline: int | None = None,
) -> int:
    """Count steps where active support escapes the previous one-hop envelope."""
    if len(history) < 2:
        return 0
    violations = 0
    for prev, curr in zip(history[:-1], history[1:]):
        base = baseline if baseline is not None else prev.min_tau()
        prev_active = _active_support_set(prev, base)
        curr_active = _active_support_set(curr, base)
        if not curr_active:
            continue
        envelope = _one_hop_envelope(prev_active, prev.slice)
        if not curr_active.issubset(envelope):
            violations += 1
    return violations


def phase_coherence_proxy(field: DeltaTauField, baseline: int | None = None) -> float:
    """Bounded coherence proxy from excess tau only; not a wavefunction."""
    base = baseline if baseline is not None else field.min_tau()
    excesses = [tau - base for tau in field.values.values() if tau > base]
    if not excesses:
        return 1.0
    unit_vectors = [cmath.exp(-1j * float(ex)) for ex in excesses]
    return abs(sum(unit_vectors) / len(unit_vectors))


def effective_geometry_proxy(field: DeltaTauField) -> float:
    """Mean gradient magnitude; geometry diagnostic only."""
    sites = _spatial_positions(field)
    if not sites:
        return 0.0
    return _tau_gradient_l1(field) / len(sites)


def _profile_l1(field_a: DeltaTauField, field_b: DeltaTauField) -> int:
    keys = set(field_a.values) | set(field_b.values)
    return sum(abs(field_a.values.get(k, 0) - field_b.values.get(k, 0)) for k in keys)


def oscillation_score(history: tuple[DeltaTauField, ...]) -> float:
    """Normalized oscillation proxy from successive profile L1 changes."""
    if len(history) < 3:
        return 0.0
    deltas = [_profile_l1(history[i - 1], history[i]) for i in range(1, len(history))]
    sign_changes = sum(
        1
        for i in range(1, len(deltas))
        if deltas[i] > 0 and deltas[i - 1] > 0 and ((deltas[i] - deltas[i - 1]) * deltas[i - 1] < 0)
    )
    return sign_changes / max(len(deltas) - 1, 1)


def recurrence_score(history: tuple[DeltaTauField, ...]) -> float:
    """Similarity of final field to the step-1 profile (1.0 = identical profiles)."""
    if len(history) < 2:
        return 1.0
    initial_l1 = _profile_l1(history[0], history[1])
    final_l1 = _profile_l1(history[0], history[-1])
    if initial_l1 == 0 and final_l1 == 0:
        return 1.0
    denom = max(initial_l1, final_l1, 1)
    return max(0.0, 1.0 - final_l1 / denom)


def memory_sensitivity_score(history: tuple[DeltaTauField, ...]) -> float:
    """Mean absolute profile L1 step change."""
    if len(history) < 2:
        return 0.0
    changes = [_profile_l1(history[i - 1], history[i]) for i in range(1, len(history))]
    return sum(changes) / len(changes)


def compute_action_metrics(
    initial_field: DeltaTauField,
    final_field: DeltaTauField,
    history: tuple[DeltaTauField, ...],
    baseline: int | None = None,
) -> dict[str, Any]:
    """Compute all Stage 3C Action benchmark metrics."""
    base = baseline if baseline is not None else initial_field.min_tau()
    initial_structure = packet_structure_from_field(initial_field)
    final_structure = packet_structure_from_field(final_field)

    initial_support = active_support_size_above_baseline(initial_structure, base)
    final_support = active_support_size_above_baseline(final_structure, base)
    grid_sites = len(_spatial_positions(initial_field))
    spreading = (final_support - initial_support) / max(grid_sites, 1)

    initial_centroid = active_center_of_excess_tau(initial_structure, base)
    final_centroid = active_center_of_excess_tau(final_structure, base)
    if initial_centroid and final_centroid:
        centroid_drift = sum(abs(a - b) for a, b in zip(initial_centroid, final_centroid))
    else:
        centroid_drift = 0.0

    return {
        "total_tau": _total_tau(final_field),
        "total_tau_change": _total_tau(final_field) - _total_tau(initial_field),
        "active_support_size": final_support,
        "support_centroid": list(final_centroid) if final_centroid else None,
        "centroid_drift": centroid_drift,
        "max_tau": max(final_field.values.values()),
        "min_tau": min(final_field.values.values()),
        "tau_variance": _tau_variance(final_field),
        "tau_gradient_l1": _tau_gradient_l1(final_field),
        "discrete_laplacian_energy_proxy": _discrete_laplacian_energy_proxy(final_field),
        "propagation_radius": _propagation_radius(final_field, base),
        "finite_speed_violation_count": finite_speed_violation_count(history, base),
        "localization_score": active_localization_ratio(final_structure, base),
        "spreading_score": spreading,
        "oscillation_score": oscillation_score(history),
        "recurrence_score": recurrence_score(history),
        "memory_sensitivity_score": memory_sensitivity_score(history),
        "phase_coherence_proxy": phase_coherence_proxy(final_field, base),
        "effective_geometry_proxy": effective_geometry_proxy(final_field),
    }
