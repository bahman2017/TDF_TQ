"""History of packet structures across toy update steps."""

from dataclasses import dataclass

from tdf_tq.fields import DeltaTauField
from tdf_tq.structure import (
    PacketStructure,
    packet_structure_from_field,
    support_overlap_ratio,
    tau_profile_l1_difference,
)


@dataclass(frozen=True)
class StructureHistory:
    """Sequence of packet structures indexed by discrete update step k."""

    structures: tuple[PacketStructure, ...]
    update_label: str = "toy_update_history"

    def __post_init__(self) -> None:
        if not isinstance(self.update_label, str):
            raise TypeError("update_label must be a string")
        if not self.structures:
            raise ValueError("structures must be non-empty")
        for structure in self.structures:
            if not isinstance(structure, PacketStructure):
                raise TypeError("every structure must be a PacketStructure")

    def length(self) -> int:
        return len(self.structures)

    def initial(self) -> PacketStructure:
        return self.structures[0]

    def final(self) -> PacketStructure:
        return self.structures[-1]

    def total_tau_series(self) -> tuple[int, ...]:
        return tuple(s.total_tau() for s in self.structures)

    def total_excess_tau_series(self) -> tuple[int, ...]:
        return tuple(s.total_excess_tau() for s in self.structures)

    def localization_ratio_series(self) -> tuple[float, ...]:
        return tuple(s.localization_ratio() for s in self.structures)

    def support_size_series(self) -> tuple[int, ...]:
        return tuple(s.support_size() for s in self.structures)

    def center_series(self) -> tuple[tuple[float, float, float] | None, ...]:
        return tuple(s.center_of_excess_tau() for s in self.structures)

    def max_tau_profile_l1_step_change(self) -> int:
        if self.length() < 2:
            return 0
        return max(
            tau_profile_l1_difference(self.structures[i], self.structures[i + 1])
            for i in range(self.length() - 1)
        )

    def min_support_overlap_between_steps(self) -> float:
        if self.length() < 2:
            return 1.0
        return min(
            support_overlap_ratio(self.structures[i], self.structures[i + 1])
            for i in range(self.length() - 1)
        )

    def total_tau_conserved(self) -> bool:
        series = self.total_tau_series()
        return all(value == series[0] for value in series)

    def quasi_stable_summary(
        self,
        max_allowed_tau_profile_l1_step_change: int,
        min_allowed_support_overlap: float,
    ) -> dict[str, object]:
        """Toy stability diagnostic summary (not a physical stability proof)."""
        initial = self.initial()
        final = self.final()
        max_change = self.max_tau_profile_l1_step_change()
        min_overlap = self.min_support_overlap_between_steps()
        conserved = self.total_tau_conserved()
        quasi_stable_pass = (
            conserved
            and max_change <= max_allowed_tau_profile_l1_step_change
            and min_overlap >= min_allowed_support_overlap
        )
        return {
            "total_tau_conserved": conserved,
            "max_tau_profile_l1_step_change": max_change,
            "min_support_overlap_between_steps": min_overlap,
            "initial_localization_ratio": initial.localization_ratio(),
            "final_localization_ratio": final.localization_ratio(),
            "initial_support_size": initial.support_size(),
            "final_support_size": final.support_size(),
            "initial_center": initial.center_of_excess_tau(),
            "final_center": final.center_of_excess_tau(),
            "quasi_stable_pass": quasi_stable_pass,
        }


def structure_history_from_field_sequence(
    fields: tuple[DeltaTauField, ...],
    label_prefix: str = "step",
) -> StructureHistory:
    """Build a structure history from a sequence of fields."""
    if not fields:
        raise ValueError("fields must be non-empty")
    if not isinstance(label_prefix, str):
        raise TypeError("label_prefix must be a string")
    structures = tuple(
        packet_structure_from_field(field, label=f"{label_prefix}_{index}")
        for index, field in enumerate(fields)
    )
    return StructureHistory(structures=structures)
