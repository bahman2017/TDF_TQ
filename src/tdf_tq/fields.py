"""Delta-tau fields on the emergent spatial count lattice."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from tdf_tq.metrics import spatial_count_l1_distance
from tdf_tq.packets import TemporalPacket
from tdf_tq.space import SpatialSlice


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def _spatial_positions(slice_: SpatialSlice) -> tuple[tuple[int, int, int], ...]:
    positions: list[tuple[int, int, int]] = []
    for n_a in range(slice_.bounds.max_N_a + 1):
        for n_b in range(slice_.bounds.max_N_b + 1):
            for n_c in range(slice_.bounds.max_N_c + 1):
                positions.append((n_a, n_b, n_c))
    return tuple(positions)


def _validate_spatial_key(key: object) -> tuple[int, int, int]:
    if not isinstance(key, tuple) or len(key) != 3:
        raise TypeError("field keys must be tuples (N_a, N_b, N_c)")
    n_a, n_b, n_c = key
    for name, value in (("N_a", n_a), ("N_b", n_b), ("N_c", n_c)):
        _require_non_negative_int(name, value)
    return (n_a, n_b, n_c)


@dataclass(frozen=True)
class DeltaTauField:
    """Distributed tau = N_t values on a spatial count lattice.

    Keys are spatial triples ``(N_a, N_b, N_c)``; values are local progression
    counts. ``slice.N_t`` is a reference layer label only—the field may assign
    different tau at each spatial site.
    """

    slice: SpatialSlice
    values: Mapping[tuple[int, int, int], int]

    def __post_init__(self) -> None:
        validated: dict[tuple[int, int, int], int] = {}
        for key, value in self.values.items():
            spatial_key = _validate_spatial_key(key)
            if not self.slice.bounds.contains_spatial_counts(*spatial_key):
                raise ValueError(
                    f"field key {spatial_key} is outside slice spatial bounds"
                )
            _require_non_negative_int("tau", value)
            if spatial_key in validated:
                raise ValueError(f"duplicate field key {spatial_key}")
            validated[spatial_key] = value

        required = set(_spatial_positions(self.slice))
        provided = set(validated)
        if provided != required:
            missing = required - provided
            extra = provided - required
            if missing:
                raise ValueError(f"field missing spatial positions: {sorted(missing)}")
            raise ValueError(f"field has out-of-bounds or extra positions: {sorted(extra)}")

        object.__setattr__(self, "values", MappingProxyType(validated))

    def tau_at_counts(self, N_a: int, N_b: int, N_c: int) -> int:
        """Return tau at spatial counts inside the slice bounds."""
        _require_non_negative_int("N_a", N_a)
        _require_non_negative_int("N_b", N_b)
        _require_non_negative_int("N_c", N_c)
        key = (N_a, N_b, N_c)
        if not self.slice.bounds.contains_spatial_counts(N_a, N_b, N_c):
            raise ValueError(f"spatial counts {key} are outside field bounds")
        return self.values[key]

    def tau_at_packet(self, packet: TemporalPacket) -> int:
        """Return tau at the packet's spatial counts (N_t on packet is ignored)."""
        if not self.slice.bounds.contains_packet(packet):
            raise ValueError("packet spatial counts are outside field bounds")
        return self.tau_at_counts(packet.N_a, packet.N_b, packet.N_c)

    def delta_tau_between_counts(
        self,
        a_counts: tuple[int, int, int],
        b_counts: tuple[int, int, int],
    ) -> int:
        """Return tau(b) - tau(a) using spatial counts only."""
        return self.tau_at_counts(*b_counts) - self.tau_at_counts(*a_counts)

    def delta_tau_between_packets(
        self,
        packet_a: TemporalPacket,
        packet_b: TemporalPacket,
    ) -> int:
        """Return tau difference using spatial counts only."""
        return self.tau_at_packet(packet_b) - self.tau_at_packet(packet_a)

    def as_packets_with_local_tau(self) -> tuple[TemporalPacket, ...]:
        """Packets with field-assigned N_t in deterministic lattice order."""
        return tuple(
            TemporalPacket(N_a=n_a, N_b=n_b, N_c=n_c, N_t=self.values[(n_a, n_b, n_c)])
            for n_a, n_b, n_c in _spatial_positions(self.slice)
        )

    def mean_tau(self) -> float:
        """Arithmetic mean of field tau values."""
        vals = list(self.values.values())
        return sum(vals) / len(vals)

    def min_tau(self) -> int:
        return min(self.values.values())

    def max_tau(self) -> int:
        return max(self.values.values())


def uniform_delta_tau_field(slice_: SpatialSlice, tau_value: int) -> DeltaTauField:
    """Constant tau over every spatial position in the slice."""
    _require_non_negative_int("tau_value", tau_value)
    values = {pos: tau_value for pos in _spatial_positions(slice_)}
    return DeltaTauField(slice=slice_, values=values)


def radial_delta_tau_field(
    slice_: SpatialSlice,
    center: tuple[int, int, int],
    base_tau: int,
    strength: int,
) -> DeltaTauField:
    """Toy radial profile: tau = base_tau + strength * Manhattan distance from center.

    Deterministic scaffolding only—not a physical potential.
    """
    _require_non_negative_int("base_tau", base_tau)
    _require_non_negative_int("strength", strength)
    center_key = _validate_spatial_key(center)
    if not slice_.bounds.contains_spatial_counts(*center_key):
        raise ValueError("center must lie inside slice spatial bounds")

    center_packet = TemporalPacket(
        N_a=center_key[0], N_b=center_key[1], N_c=center_key[2], N_t=slice_.N_t
    )
    values: dict[tuple[int, int, int], int] = {}
    for pos in _spatial_positions(slice_):
        site = TemporalPacket(N_a=pos[0], N_b=pos[1], N_c=pos[2], N_t=slice_.N_t)
        distance = spatial_count_l1_distance(center_packet, site)
        values[pos] = base_tau + strength * distance
    return DeltaTauField(slice=slice_, values=values)
