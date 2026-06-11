"""Finite emergent spatial regions on the count lattice."""

from dataclasses import dataclass

from tdf_tq.neighborhoods import spatial_unit_neighbors
from tdf_tq.packets import TemporalPacket


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


@dataclass(frozen=True)
class SpatialBounds:
    """Inclusive upper bounds on spatial packet counts."""

    max_N_a: int
    max_N_b: int
    max_N_c: int

    def __post_init__(self) -> None:
        for name, value in (
            ("max_N_a", self.max_N_a),
            ("max_N_b", self.max_N_b),
            ("max_N_c", self.max_N_c),
        ):
            _require_non_negative_int(name, value)

    def contains_spatial_counts(self, N_a: int, N_b: int, N_c: int) -> bool:
        """True when spatial counts lie within the bounded region."""
        return (
            0 <= N_a <= self.max_N_a
            and 0 <= N_b <= self.max_N_b
            and 0 <= N_c <= self.max_N_c
        )

    def contains_packet(self, packet: TemporalPacket) -> bool:
        """True when the packet's spatial counts lie within the bounded region."""
        return self.contains_spatial_counts(packet.N_a, packet.N_b, packet.N_c)


@dataclass(frozen=True)
class SpatialSlice:
    """A finite rectangular spatial region at a fixed temporal layer N_t."""

    N_t: int
    bounds: SpatialBounds

    def __post_init__(self) -> None:
        _require_non_negative_int("N_t", self.N_t)

    def packets(self) -> tuple[TemporalPacket, ...]:
        """All packets with 0 <= N_a/b/c <= max and fixed N_t."""
        result: list[TemporalPacket] = []
        for n_a in range(self.bounds.max_N_a + 1):
            for n_b in range(self.bounds.max_N_b + 1):
                for n_c in range(self.bounds.max_N_c + 1):
                    result.append(
                        TemporalPacket(N_a=n_a, N_b=n_b, N_c=n_c, N_t=self.N_t)
                    )
        return tuple(result)

    def contains_packet(self, packet: TemporalPacket) -> bool:
        """True when packet is inside bounds and on this temporal layer."""
        return packet.N_t == self.N_t and self.bounds.contains_packet(packet)

    def neighbors_within_bounds(self, packet: TemporalPacket) -> tuple[TemporalPacket, ...]:
        """Spatial unit neighbors of packet that remain inside this slice.

        Raises
        ------
        ValueError
            If packet is not contained in this slice.
        """
        if not self.contains_packet(packet):
            raise ValueError("packet is not contained in this spatial slice")
        return tuple(
            neighbor
            for neighbor in spatial_unit_neighbors(packet)
            if self.contains_packet(neighbor)
        )
