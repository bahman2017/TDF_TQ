"""Toy deterministic field evolution on the count lattice.

These update rules are integer relaxation scaffolding—not physical dynamics.
"""

from dataclasses import dataclass

from tdf_tq.fields import DeltaTauField
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


def run_field_evolution(
    initial_field: DeltaTauField,
    steps: int,
    config: FieldEvolutionConfig | None = None,
    step_kind: str = "conservative_pairwise_relaxation",
) -> tuple[DeltaTauField, ...]:
    """Run deterministic field evolution; element 0 is the initial field."""
    _require_non_negative_int_steps("steps", steps)

    if step_kind == "identity":
        step_fn = identity_step
    elif step_kind == "conservative_pairwise_relaxation":
        step_fn = lambda f: conservative_pairwise_relaxation_step(f, config)
    else:
        raise ValueError(f"unknown step_kind: {step_kind!r}")

    history: list[DeltaTauField] = [initial_field]
    current = initial_field
    for _ in range(steps):
        current = step_fn(current)
        history.append(current)
    return tuple(history)
