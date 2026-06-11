"""History of packet structures across toy update steps."""

from dataclasses import dataclass

from tdf_tq.fields import DeltaTauField
import math

from tdf_tq.structure import (
    PacketStructure,
    active_center_of_excess_tau,
    active_localization_ratio,
    active_support_overlap_ratio,
    active_support_size_above_baseline,
    active_tau_profile_l1_difference,
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


def initial_baseline_tau(history: StructureHistory) -> int:
    """Fixed baseline tau from the initial structure."""
    return history.initial().baseline_tau()


def _resolve_history_baseline(history: StructureHistory, baseline: int | None) -> int:
    if baseline is None:
        return initial_baseline_tau(history)
    if not isinstance(baseline, int) or isinstance(baseline, bool):
        raise TypeError("baseline must be an integer")
    if baseline < 0:
        raise ValueError("baseline must be non-negative")
    return baseline


def active_support_size_series(
    history: StructureHistory,
    baseline: int | None = None,
) -> tuple[int, ...]:
    base = _resolve_history_baseline(history, baseline)
    return tuple(
        active_support_size_above_baseline(structure, base) for structure in history.structures
    )


def active_center_series(
    history: StructureHistory,
    baseline: int | None = None,
) -> tuple[tuple[float, float, float] | None, ...]:
    base = _resolve_history_baseline(history, baseline)
    return tuple(
        active_center_of_excess_tau(structure, base) for structure in history.structures
    )


def active_localization_ratio_series(
    history: StructureHistory,
    baseline: int | None = None,
) -> tuple[float, ...]:
    base = _resolve_history_baseline(history, baseline)
    return tuple(
        active_localization_ratio(structure, base) for structure in history.structures
    )


def max_active_tau_profile_l1_step_change(
    history: StructureHistory,
    baseline: int | None = None,
) -> int:
    base = _resolve_history_baseline(history, baseline)
    if history.length() < 2:
        return 0
    return max(
        active_tau_profile_l1_difference(
            history.structures[i], history.structures[i + 1], base, base
        )
        for i in range(history.length() - 1)
    )


def min_active_support_overlap_between_steps(
    history: StructureHistory,
    baseline: int | None = None,
) -> float:
    base = _resolve_history_baseline(history, baseline)
    if history.length() < 2:
        return 1.0
    return min(
        active_support_overlap_ratio(
            history.structures[i], history.structures[i + 1], base, base
        )
        for i in range(history.length() - 1)
    )


def active_center_drift(
    history: StructureHistory,
    baseline: int | None = None,
) -> float | None:
    """Euclidean distance between initial and final active excess centroids."""
    base = _resolve_history_baseline(history, baseline)
    initial_center = active_center_of_excess_tau(history.initial(), base)
    final_center = active_center_of_excess_tau(history.final(), base)
    if initial_center is None or final_center is None:
        return None
    return math.sqrt(
        (final_center[0] - initial_center[0]) ** 2
        + (final_center[1] - initial_center[1]) ** 2
        + (final_center[2] - initial_center[2]) ** 2
    )


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
