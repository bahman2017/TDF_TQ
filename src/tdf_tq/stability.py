"""Toy stability diagnostics over structure histories.

Not a physical stability proof. No mass, energy, charge, or particle claims.
"""

from tdf_tq.history import StructureHistory

__all__ = [
    "is_history_quasi_stable",
    "structure_persistence_score",
]


def is_history_quasi_stable(
    history: StructureHistory,
    max_allowed_tau_profile_l1_step_change: int,
    min_allowed_support_overlap: float,
) -> bool:
    """True when the history passes toy quasi-stability thresholds."""
    summary = history.quasi_stable_summary(
        max_allowed_tau_profile_l1_step_change,
        min_allowed_support_overlap,
    )
    return bool(summary["quasi_stable_pass"])


def structure_persistence_score(history: StructureHistory) -> float:
    """Deterministic persistence score in [0, 1] combining conservation, overlap, smoothness.

    Formula (documented toy diagnostic):

    ``score = (conservation_factor + min_overlap + step_smoothness) / 3``

    where:

    - ``conservation_factor`` is 1.0 if total tau is conserved across steps, else 0.0
    - ``min_overlap`` is ``min_support_overlap_between_steps`` in [0, 1]
    - ``step_smoothness`` is ``1 / (1 + max_tau_profile_l1_step_change)``

    This is not a physical stability proof.
    """
    conservation_factor = 1.0 if history.total_tau_conserved() else 0.0
    min_overlap = history.min_support_overlap_between_steps()
    max_change = history.max_tau_profile_l1_step_change()
    step_smoothness = 1.0 / (1.0 + max_change)
    return (conservation_factor + min_overlap + step_smoothness) / 3.0
