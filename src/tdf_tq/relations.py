"""Deterministic relations between temporal packets (count-level primitives)."""

from dataclasses import dataclass

from tdf_tq.packets import TemporalPacket


def _require_int_field(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")


@dataclass(frozen=True)
class PacketDelta:
    """Signed component-wise difference between two temporal packets.

    Deltas may be negative. This is a count relation, not a time-evolution step.
    """

    dN_a: int
    dN_b: int
    dN_c: int
    dN_t: int

    def __post_init__(self) -> None:
        for name, value in (
            ("dN_a", self.dN_a),
            ("dN_b", self.dN_b),
            ("dN_c", self.dN_c),
            ("dN_t", self.dN_t),
        ):
            _require_int_field(name, value)

    @property
    def spatial_delta(self) -> tuple[int, int, int]:
        """Spatial count differences as (dN_a, dN_b, dN_c)."""
        return (self.dN_a, self.dN_b, self.dN_c)

    @property
    def delta_tau(self) -> int:
        """Temporal count difference (Δτ = ΔN_t at the packet level)."""
        return self.dN_t


def packet_delta(packet_a: TemporalPacket, packet_b: TemporalPacket) -> PacketDelta:
    """Return component-wise packet_b - packet_a as a PacketDelta."""
    return PacketDelta(
        dN_a=packet_b.N_a - packet_a.N_a,
        dN_b=packet_b.N_b - packet_a.N_b,
        dN_c=packet_b.N_c - packet_a.N_c,
        dN_t=packet_b.N_t - packet_a.N_t,
    )


def translate_packet(packet: TemporalPacket, delta: PacketDelta) -> TemporalPacket:
    """Return a new packet with counts shifted by delta.

    Raises
    ------
    ValueError
        If any resulting count would be negative.
    """
    new_counts = (
        packet.N_a + delta.dN_a,
        packet.N_b + delta.dN_b,
        packet.N_c + delta.dN_c,
        packet.N_t + delta.dN_t,
    )
    for name, value in zip(("N_a", "N_b", "N_c", "N_t"), new_counts):
        if value < 0:
            raise ValueError(
                f"translation would make {name} negative ({value}); "
                "packet counts must remain non-negative"
            )
    return TemporalPacket(N_a=new_counts[0], N_b=new_counts[1], N_c=new_counts[2], N_t=new_counts[3])


def same_spatial_position(packet_a: TemporalPacket, packet_b: TemporalPacket) -> bool:
    """True when spatial counts match, regardless of N_t."""
    return packet_a.spatial_counts == packet_b.spatial_counts


def same_temporal_layer(packet_a: TemporalPacket, packet_b: TemporalPacket) -> bool:
    """True when N_t matches, regardless of spatial counts."""
    return packet_a.N_t == packet_b.N_t


def delta_tau_matches(
    packet_a: TemporalPacket,
    packet_b: TemporalPacket,
    expected_delta_tau: int,
) -> bool:
    """True when packet_b.N_t - packet_a.N_t equals expected_delta_tau."""
    _require_int_field("expected_delta_tau", expected_delta_tau)
    return packet_b.N_t - packet_a.N_t == expected_delta_tau
