"""Localized packet-structure candidate evaluation (Stage 4A)."""

import math
from dataclasses import dataclass

from tdf_tq.history import (
    StructureHistory,
    active_center_drift,
    active_localization_ratio_series,
    active_support_size_series,
    initial_baseline_tau,
    max_active_tau_profile_l1_step_change,
    min_active_support_overlap_between_steps,
)
from tdf_tq.stability import structure_persistence_score
from tdf_tq.structure import (
    active_localization_ratio,
    active_support_size_above_baseline,
)

_LIMITATION = "Toy candidate only; not a particle, not an electron, not validated physics."

_VERDICT_PASS = "PASS_TO_STAGE_4B"
_VERDICT_INCONCLUSIVE = "INCONCLUSIVE"
_VERDICT_FAIL = "FAIL"


def _require_non_negative_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def _require_positive_int(name: str, value: object) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
    if value < 1:
        raise ValueError(f"{name} must be >= 1, got {value}")


@dataclass(frozen=True)
class LocalizedCandidateCriteria:
    """Toy thresholds for localized packet-structure candidates."""

    min_total_excess_tau: int = 1
    max_final_active_support_size: int = 6
    min_final_localization_ratio: float = 0.20
    max_center_drift: float = 1.0
    max_active_tau_profile_l1_step_change: int = 12
    min_active_support_overlap: float = 0.25
    require_total_tau_conserved: bool = True

    def __post_init__(self) -> None:
        _require_non_negative_int("min_total_excess_tau", self.min_total_excess_tau)
        _require_positive_int("max_final_active_support_size", self.max_final_active_support_size)
        if not math.isfinite(self.min_final_localization_ratio):
            raise ValueError("min_final_localization_ratio must be finite")
        if not 0.0 <= self.min_final_localization_ratio <= 1.0:
            raise ValueError("min_final_localization_ratio must be in [0, 1]")
        if not math.isfinite(self.max_center_drift) or self.max_center_drift < 0:
            raise ValueError("max_center_drift must be a non-negative finite float")
        _require_non_negative_int(
            "max_active_tau_profile_l1_step_change",
            self.max_active_tau_profile_l1_step_change,
        )
        if not math.isfinite(self.min_active_support_overlap):
            raise ValueError("min_active_support_overlap must be finite")
        if not 0.0 <= self.min_active_support_overlap <= 1.0:
            raise ValueError("min_active_support_overlap must be in [0, 1]")
        if not isinstance(self.require_total_tau_conserved, bool):
            raise TypeError("require_total_tau_conserved must be a bool")


@dataclass(frozen=True)
class CandidateEvaluation:
    """Result of evaluating one seed history against toy criteria."""

    seed_label: str
    passed: bool
    verdict: str
    metrics: dict[str, object]
    limitations: tuple[str, ...]


def evaluate_localized_candidate(
    history: StructureHistory,
    criteria: LocalizedCandidateCriteria | None = None,
    baseline: int | None = None,
    seed_label: str = "unlabeled_seed",
) -> CandidateEvaluation:
    """Evaluate a structure history using active-support diagnostics only."""
    crit = criteria or LocalizedCandidateCriteria()
    base = initial_baseline_tau(history) if baseline is None else baseline
    if not isinstance(base, int) or isinstance(base, bool):
        raise TypeError("baseline must be an integer")
    if base < 0:
        raise ValueError("baseline must be non-negative")

    initial = history.initial()
    final = history.final()
    conserved = history.total_tau_conserved()
    initial_excess = initial.total_excess_tau(base)
    final_excess = final.total_excess_tau(base)
    initial_active_size = active_support_size_above_baseline(initial, base)
    final_active_size = active_support_size_above_baseline(final, base)
    initial_loc = active_localization_ratio(initial, base)
    final_loc = active_localization_ratio(final, base)
    center_drift = active_center_drift(history, base)
    max_step_change = max_active_tau_profile_l1_step_change(history, base)
    min_overlap = min_active_support_overlap_between_steps(history, base)
    persistence = structure_persistence_score(history)

    metrics: dict[str, object] = {
        "baseline_tau": base,
        "total_tau_conserved": conserved,
        "initial_total_excess_tau": initial_excess,
        "final_total_excess_tau": final_excess,
        "initial_active_support_size": initial_active_size,
        "final_active_support_size": final_active_size,
        "initial_active_localization_ratio": initial_loc,
        "final_active_localization_ratio": final_loc,
        "active_center_drift": center_drift,
        "max_active_tau_profile_l1_step_change": max_step_change,
        "min_active_support_overlap_between_steps": min_overlap,
        "persistence_score": persistence,
    }

    checks = [
        final_excess >= crit.min_total_excess_tau,
        final_active_size <= crit.max_final_active_support_size,
        final_loc >= crit.min_final_localization_ratio,
        center_drift is not None and center_drift <= crit.max_center_drift,
        max_step_change <= crit.max_active_tau_profile_l1_step_change,
        min_overlap >= crit.min_active_support_overlap,
        (not crit.require_total_tau_conserved) or conserved,
    ]
    passed = all(checks)

    if final_excess == 0:
        verdict = _VERDICT_FAIL
        passed = False
    elif passed:
        verdict = _VERDICT_PASS
    elif final_excess > 0 and final_loc > 0.0:
        verdict = _VERDICT_INCONCLUSIVE
    else:
        verdict = _VERDICT_FAIL

    return CandidateEvaluation(
        seed_label=seed_label,
        passed=passed,
        verdict=verdict,
        metrics=metrics,
        limitations=(_LIMITATION,),
    )
