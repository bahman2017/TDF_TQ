"""Provisional spatial metrics on the emergent count lattice.

Spatial metrics depend on (N_a, N_b, N_c) only. N_t (tau) does not enter
spatial distance. Graph paths are combinatorial scaffolding, not motion.
"""

from tdf_tq.neighborhoods import is_spatial_unit_neighbor
from tdf_tq.packets import TemporalPacket

__all__ = [
    "deterministic_spatial_path",
    "emergent_manhattan_distance",
    "emergent_unit_edge_length",
    "spatial_count_l1_distance",
    "spatial_graph_distance_steps",
]


def _require_positive_l_q(l_q: float) -> None:
    if l_q <= 0:
        raise ValueError("l_q must be strictly positive")


def spatial_count_l1_distance(packet_a: TemporalPacket, packet_b: TemporalPacket) -> int:
    """L1 distance on spatial counts; N_t is ignored."""
    return (
        abs(packet_b.N_a - packet_a.N_a)
        + abs(packet_b.N_b - packet_a.N_b)
        + abs(packet_b.N_c - packet_a.N_c)
    )


def emergent_manhattan_distance(
    packet_a: TemporalPacket,
    packet_b: TemporalPacket,
    l_q: float = 1.0,
) -> float:
    """Toy Manhattan distance: l_q times spatial L1 count distance."""
    _require_positive_l_q(l_q)
    return l_q * spatial_count_l1_distance(packet_a, packet_b)


def emergent_unit_edge_length(
    packet_a: TemporalPacket,
    packet_b: TemporalPacket,
    l_q: float = 1.0,
) -> float:
    """Return l_q for spatial unit neighbors at the same N_t; else raise."""
    _require_positive_l_q(l_q)
    if not is_spatial_unit_neighbor(packet_a, packet_b):
        raise ValueError("packets are not spatial unit neighbors at the same N_t")
    return l_q


def spatial_graph_distance_steps(
    packet_a: TemporalPacket,
    packet_b: TemporalPacket,
) -> int:
    """Shortest-path step count on the spatial unit-neighbor graph at fixed N_t.

    Equals spatial L1 distance on the count lattice. This is graph distance,
    not motion or dynamics.
    """
    if packet_a.N_t != packet_b.N_t:
        raise ValueError("packets must share the same N_t for spatial graph distance")
    return spatial_count_l1_distance(packet_a, packet_b)


def deterministic_spatial_path(
    packet_a: TemporalPacket,
    packet_b: TemporalPacket,
) -> tuple[TemporalPacket, ...]:
    """Deterministic shortest spatial path using axis order N_a, N_b, N_c.

    Consecutive packets are spatial unit neighbors. Includes start and end.
    Graph path only—not a physical trajectory.
    """
    if packet_a.N_t != packet_b.N_t:
        raise ValueError("packets must share the same N_t for a spatial path")
    path: list[TemporalPacket] = [packet_a]
    current = packet_a
    n_t = packet_a.N_t

    for attr, target in (
        ("N_a", packet_b.N_a),
        ("N_b", packet_b.N_b),
        ("N_c", packet_b.N_c),
    ):
        while getattr(current, attr) != target:
            step = 1 if getattr(current, attr) < target else -1
            kwargs = {
                "N_a": current.N_a,
                "N_b": current.N_b,
                "N_c": current.N_c,
                "N_t": n_t,
            }
            kwargs[attr] = getattr(current, attr) + step
            current = TemporalPacket(**kwargs)
            path.append(current)

    return tuple(path)
