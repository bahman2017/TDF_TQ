"""Full packet-structure representations on the count lattice."""

from dataclasses import dataclass

from tdf_tq.fields import DeltaTauField
from tdf_tq.packets import TemporalPacket


@dataclass(frozen=True)
class PacketStructure:
    """A labeled collection of full packets ``(N_a, N_b, N_c, N_t)``."""

    packets: tuple[TemporalPacket, ...]
    label: str = "unlabeled"

    def __post_init__(self) -> None:
        if not isinstance(self.label, str):
            raise TypeError("label must be a string")
        if not self.packets:
            raise ValueError("packets must be non-empty")
        seen: set[tuple[int, int, int]] = set()
        for packet in self.packets:
            if not isinstance(packet, TemporalPacket):
                raise TypeError("every packet must be a TemporalPacket")
            key = (packet.N_a, packet.N_b, packet.N_c)
            if key in seen:
                raise ValueError(f"duplicate spatial counts in structure: {key}")
            seen.add(key)

    def spatial_support(self) -> tuple[tuple[int, int, int], ...]:
        """Deterministic sorted spatial count triples."""
        return tuple(sorted((p.N_a, p.N_b, p.N_c) for p in self.packets))

    def tau_values(self) -> dict[tuple[int, int, int], int]:
        """Map spatial counts to local N_t."""
        return {(p.N_a, p.N_b, p.N_c): p.N_t for p in self.packets}

    def total_tau(self) -> int:
        return sum(p.N_t for p in self.packets)

    def min_tau(self) -> int:
        return min(p.N_t for p in self.packets)

    def max_tau(self) -> int:
        return max(p.N_t for p in self.packets)

    def baseline_tau(self) -> int:
        """Baseline for excess diagnostics (minimum N_t)."""
        return self.min_tau()

    def excess_tau_values(self, baseline: int | None = None) -> dict[tuple[int, int, int], int]:
        """Excess tau above baseline at each spatial site."""
        base = self.baseline_tau() if baseline is None else baseline
        return {
            key: max(tau - base, 0)
            for key, tau in self.tau_values().items()
        }

    def total_excess_tau(self, baseline: int | None = None) -> int:
        return sum(self.excess_tau_values(baseline).values())

    def support_size(self) -> int:
        return len(self.packets)

    def support_size_above_baseline(self, baseline: int | None = None) -> int:
        excess = self.excess_tau_values(baseline)
        return sum(1 for value in excess.values() if value > 0)

    def center_of_excess_tau(
        self, baseline: int | None = None
    ) -> tuple[float, float, float] | None:
        """Weighted centroid of spatial counts using excess tau weights."""
        excess = self.excess_tau_values(baseline)
        total = sum(excess.values())
        if total == 0:
            return None
        weighted = [0.0, 0.0, 0.0]
        for (n_a, n_b, n_c), weight in excess.items():
            if weight > 0:
                weighted[0] += n_a * weight
                weighted[1] += n_b * weight
                weighted[2] += n_c * weight
        return (weighted[0] / total, weighted[1] / total, weighted[2] / total)

    def localization_ratio(self, baseline: int | None = None) -> float:
        """max excess / total excess; zero when there is no excess."""
        excess = self.excess_tau_values(baseline)
        total = sum(excess.values())
        if total == 0:
            return 0.0
        return max(excess.values()) / total


def packet_structure_from_field(
    field: DeltaTauField,
    label: str = "from_field",
) -> PacketStructure:
    """Convert a field into a full packet structure with local N_t per site."""
    if not isinstance(label, str):
        raise TypeError("label must be a string")
    return PacketStructure(packets=field.as_packets_with_local_tau(), label=label)


def support_overlap_ratio(structure_a: PacketStructure, structure_b: PacketStructure) -> float:
    """Jaccard overlap of spatial support sets."""
    set_a = set(structure_a.spatial_support())
    set_b = set(structure_b.spatial_support())
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def tau_profile_l1_difference(structure_a: PacketStructure, structure_b: PacketStructure) -> int:
    """L1 difference over the union of spatial supports (missing site counts as tau 0)."""
    tau_a = structure_a.tau_values()
    tau_b = structure_b.tau_values()
    all_keys = set(tau_a) | set(tau_b)
    return sum(abs(tau_a.get(key, 0) - tau_b.get(key, 0)) for key in all_keys)
