"""Spatial neighborhood primitives on the emergent count lattice.

These functions define adjacency on non-negative integer spatial packet counts
at a fixed temporal layer (N_t). They are graph/count primitives for toy-model
scaffolding—not a claim of physical space, metric geometry, or dynamics.
"""

from tdf_tq.packets import TemporalPacket


def spatial_unit_neighbors(packet: TemporalPacket) -> tuple[TemporalPacket, ...]:
    """Return spatial unit neighbors at the same N_t.

    Each neighbor differs by exactly ±1 in one spatial component. Neighbors that
    would require negative counts are omitted (boundary behavior).
    """
    neighbors: list[TemporalPacket] = []
    for attr in ("N_a", "N_b", "N_c"):
        current = getattr(packet, attr)
        if current > 0:
            kwargs = {
                "N_a": packet.N_a,
                "N_b": packet.N_b,
                "N_c": packet.N_c,
                "N_t": packet.N_t,
            }
            kwargs[attr] = current - 1
            neighbors.append(TemporalPacket(**kwargs))
        kwargs = {
            "N_a": packet.N_a,
            "N_b": packet.N_b,
            "N_c": packet.N_c,
            "N_t": packet.N_t,
        }
        kwargs[attr] = current + 1
        neighbors.append(TemporalPacket(**kwargs))
    return tuple(neighbors)


def is_spatial_unit_neighbor(packet_a: TemporalPacket, packet_b: TemporalPacket) -> bool:
    """True iff packets are spatial unit neighbors on the count lattice."""
    if packet_a.N_t != packet_b.N_t:
        return False
    deltas = (
        packet_b.N_a - packet_a.N_a,
        packet_b.N_b - packet_a.N_b,
        packet_b.N_c - packet_a.N_c,
    )
    non_zero = [d for d in deltas if d != 0]
    if len(non_zero) != 1:
        return False
    return abs(non_zero[0]) == 1


def spatial_unit_axis(packet_a: TemporalPacket, packet_b: TemporalPacket) -> str | None:
    """Return the spatial axis label for a valid unit neighbor pair, else None."""
    if not is_spatial_unit_neighbor(packet_a, packet_b):
        return None
    if packet_b.N_a != packet_a.N_a:
        return "N_a"
    if packet_b.N_b != packet_a.N_b:
        return "N_b"
    if packet_b.N_c != packet_a.N_c:
        return "N_c"
    return None
