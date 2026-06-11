"""Tests for stability diagnostics (Stage 3B)."""

import inspect

import pytest

from tdf_tq import (
    DeltaTauField,
    PacketStructure,
    SpatialBounds,
    SpatialSlice,
    StructureHistory,
    TemporalPacket,
    is_history_quasi_stable,
    structure_persistence_score,
)
from tdf_tq import stability as stability_module


def _structure(label: str, *specs: tuple[int, int, int, int]) -> PacketStructure:
    packets = tuple(TemporalPacket(N_a=a, N_b=b, N_c=c, N_t=t) for a, b, c, t in specs)
    return PacketStructure(packets=packets, label=label)


def test_is_history_quasi_stable_true_for_identity_history():
    structure = _structure("s", (0, 0, 0, 5), (1, 0, 0, 5))
    history = StructureHistory(structures=(structure, structure, structure))
    assert is_history_quasi_stable(history, max_allowed_tau_profile_l1_step_change=0, min_allowed_support_overlap=1.0)


def test_is_history_quasi_stable_false_for_unstable_history():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 20)),
            _structure("b", (0, 0, 0, 0)),
        )
    )
    assert not is_history_quasi_stable(history, max_allowed_tau_profile_l1_step_change=1, min_allowed_support_overlap=1.0)


def test_structure_persistence_score_is_deterministic():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 0), (1, 0, 0, 10)),
            _structure("b", (0, 0, 0, 2), (1, 0, 0, 8)),
        )
    )
    assert structure_persistence_score(history) == structure_persistence_score(history)


def test_structure_persistence_score_between_zero_and_one():
    history = StructureHistory(structures=(_structure("a", (0, 0, 0, 1)),))
    score = structure_persistence_score(history)
    assert 0.0 <= score <= 1.0


def test_persistence_score_decreases_when_tau_not_conserved_or_overlap_drops():
    stable = StructureHistory(structures=(_structure("a", (0, 0, 0, 5), (1, 0, 0, 5)),) * 2)
    unstable_tau = StructureHistory(
        structures=(_structure("a", (0, 0, 0, 5)), _structure("b", (0, 0, 0, 10)))
    )
    disjoint = StructureHistory(
        structures=(_structure("a", (0, 0, 0, 5)), _structure("b", (1, 0, 0, 5)))
    )
    assert structure_persistence_score(stable) > structure_persistence_score(unstable_tau)
    assert structure_persistence_score(stable) > structure_persistence_score(disjoint)


def test_no_physical_constants_in_stability_module():
    source = inspect.getsource(stability_module)
    forbidden = ("electron", "hbar", "alpha", "G_newton", "planck")
    lowered = source.lower()
    for token in forbidden:
        assert token not in lowered
