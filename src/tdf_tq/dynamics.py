"""Toy deterministic field evolution on the count lattice.

These update rules are integer relaxation scaffolding—not physical dynamics.
"""

from dataclasses import dataclass

from tdf_tq.fields import DeltaTauField
from tdf_tq.metrics import deterministic_spatial_path, spatial_count_l1_distance
from tdf_tq.packets import TemporalPacket
from tdf_tq.space import SpatialSlice


def _require_positive_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")


def _require_non_negative_int_steps(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


@dataclass(frozen=True)
class FieldEvolutionConfig:
    """Parameters for toy conservative pairwise relaxation."""

    threshold: int = 2
    max_transfer_per_edge: int = 1

    def __post_init__(self) -> None:
        _require_positive_int("threshold", self.threshold)
        _require_positive_int("max_transfer_per_edge", self.max_transfer_per_edge)


def spatial_edges(
    slice_: SpatialSlice,
) -> tuple[tuple[tuple[int, int, int], tuple[int, int, int]], ...]:
    """Unique undirected spatial unit-neighbor edges in deterministic sorted order."""
    edge_set: set[tuple[tuple[int, int, int], tuple[int, int, int]]] = set()
    for packet in slice_.packets():
        for neighbor in slice_.neighbors_within_bounds(packet):
            a = (packet.N_a, packet.N_b, packet.N_c)
            b = (neighbor.N_a, neighbor.N_b, neighbor.N_c)
            edge = (a, b) if a < b else (b, a)
            edge_set.add(edge)
    return tuple(sorted(edge_set))


def identity_step(field: DeltaTauField) -> DeltaTauField:
    """Return an unchanged copy of the field."""
    return DeltaTauField(slice=field.slice, values=dict(field.values))


def conservative_pairwise_relaxation_step(
    field: DeltaTauField,
    config: FieldEvolutionConfig | None = None,
) -> DeltaTauField:
    """Toy integer relaxation: transfer tau across edges when difference >= threshold.

    Updates are applied sequentially in deterministic edge order. Total tau is
    conserved exactly. Not physics.
    """
    cfg = config or FieldEvolutionConfig()
    working: dict[tuple[int, int, int], int] = dict(field.values)

    for a, b in spatial_edges(field.slice):
        tau_a = working[a]
        tau_b = working[b]
        diff = tau_a - tau_b
        if diff >= cfg.threshold:
            transfer = min(cfg.max_transfer_per_edge, diff)
            working[a] = tau_a - transfer
            working[b] = tau_b + transfer
        elif -diff >= cfg.threshold:
            transfer = min(cfg.max_transfer_per_edge, -diff)
            working[a] = tau_a + transfer
            working[b] = tau_b - transfer

    return DeltaTauField(slice=field.slice, values=working)


def _validate_anchor_counts(
    field: DeltaTauField,
    anchor_counts: tuple[int, int, int],
) -> None:
    if len(anchor_counts) != 3:
        raise ValueError("anchor_counts must be a 3-tuple")
    for name, value in zip(("N_a", "N_b", "N_c"), anchor_counts):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"anchor {name} must be an integer")
        if value < 0:
            raise ValueError(f"anchor {name} must be non-negative")
    if not field.slice.bounds.contains_spatial_counts(*anchor_counts):
        raise ValueError("anchor_counts must lie inside slice spatial bounds")


def conservative_centered_cohesion_step(
    field: DeltaTauField,
    anchor_counts: tuple[int, int, int],
    config: FieldEvolutionConfig | None = None,
) -> DeltaTauField:
    """Toy retention rule: shift excess tau one step toward anchor on count lattice.

    Not attraction, force, gravity, binding energy, charge, or mass.
    """
    cfg = config or FieldEvolutionConfig()
    _validate_anchor_counts(field, anchor_counts)
    working: dict[tuple[int, int, int], int] = dict(field.values)
    baseline = field.min_tau()
    anchor_packet = TemporalPacket(
        N_a=anchor_counts[0],
        N_b=anchor_counts[1],
        N_c=anchor_counts[2],
        N_t=field.slice.N_t,
    )

    for source in sorted(
        key for key, tau in working.items() if tau > baseline and key != anchor_counts
    ):
        source_packet = TemporalPacket(
            N_a=source[0], N_b=source[1], N_c=source[2], N_t=field.slice.N_t
        )
        path = deterministic_spatial_path(source_packet, anchor_packet)
        if len(path) < 2:
            continue
        dest = (path[1].N_a, path[1].N_b, path[1].N_c)
        source_dist = spatial_count_l1_distance(source_packet, anchor_packet)
        dest_packet = path[1]
        dest_dist = spatial_count_l1_distance(dest_packet, anchor_packet)
        if dest_dist >= source_dist:
            continue
        excess = working[source] - baseline
        if excess <= 0:
            continue
        transfer = min(cfg.max_transfer_per_edge, excess)
        working[source] -= transfer
        working[dest] += transfer

    return DeltaTauField(slice=field.slice, values=working)


def run_field_evolution(
    initial_field: DeltaTauField,
    steps: int,
    config: FieldEvolutionConfig | None = None,
    step_kind: str = "conservative_pairwise_relaxation",
    anchor_counts: tuple[int, int, int] | None = None,
) -> tuple[DeltaTauField, ...]:
    """Run deterministic field evolution; element 0 is the initial field."""
    _require_non_negative_int_steps("steps", steps)

    if step_kind == "identity":
        step_fn = identity_step
    elif step_kind == "conservative_pairwise_relaxation":
        step_fn = lambda f: conservative_pairwise_relaxation_step(f, config)
    elif step_kind == "conservative_centered_cohesion":
        if anchor_counts is None:
            raise ValueError("anchor_counts is required for conservative_centered_cohesion")
        step_fn = lambda f: conservative_centered_cohesion_step(f, anchor_counts, config)
    else:
        raise ValueError(f"unknown step_kind: {step_kind!r}")

    history: list[DeltaTauField] = [initial_field]
    current = initial_field
    for _ in range(steps):
        current = step_fn(current)
        history.append(current)
    return tuple(history)
