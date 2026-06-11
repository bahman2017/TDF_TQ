"""Tests for structure histories (Stage 3B)."""

import pytest

from tdf_tq import (
    DeltaTauField,
    FieldEvolutionConfig,
    PacketStructure,
    SpatialBounds,
    SpatialSlice,
    StructureHistory,
    TemporalPacket,
    packet_structure_from_field,
    run_field_evolution,
    structure_history_from_field_sequence,
    uniform_delta_tau_field,
)


def _structure(label: str, *specs: tuple[int, int, int, int]) -> PacketStructure:
    packets = tuple(TemporalPacket(N_a=a, N_b=b, N_c=c, N_t=t) for a, b, c, t in specs)
    return PacketStructure(packets=packets, label=label)


def test_structure_history_rejects_empty_sequence():
    with pytest.raises(ValueError):
        StructureHistory(structures=())


def test_length_initial_final():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 1)),
            _structure("b", (0, 0, 0, 2)),
        )
    )
    assert history.length() == 2
    assert history.initial().label == "a"
    assert history.final().label == "b"


def test_total_tau_series():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 3), (1, 0, 0, 4)),
            _structure("b", (0, 0, 0, 5), (1, 0, 0, 5)),
        )
    )
    assert history.total_tau_series() == (7, 10)


def test_localization_ratio_series():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 0), (1, 0, 0, 10)),
            _structure("b", (0, 0, 0, 5), (1, 0, 0, 5)),
        )
    )
    assert history.localization_ratio_series()[0] == 1.0
    assert history.localization_ratio_series()[1] == 0.0


def test_support_size_series():
    history = StructureHistory(structures=(_structure("a", (0, 0, 0, 1)),))
    assert history.support_size_series() == (1,)


def test_center_series():
    history = StructureHistory(
        structures=(_structure("a", (0, 0, 0, 0), (2, 0, 0, 4)),)
    )
    assert history.center_series() == ((2.0, 0.0, 0.0),)


def test_max_tau_profile_l1_step_change():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 10), (1, 0, 0, 0)),
            _structure("b", (0, 0, 0, 5), (1, 0, 0, 5)),
        )
    )
    assert history.max_tau_profile_l1_step_change() == 10


def test_min_support_overlap_between_steps():
    a = _structure("a", (0, 0, 0, 1), (1, 0, 0, 1))
    b = _structure("b", (1, 0, 0, 1), (2, 0, 0, 1))
    history = StructureHistory(structures=(a, b))
    assert history.min_support_overlap_between_steps() == 1 / 3


def test_total_tau_conserved_for_conservative_field_evolution():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=0, max_N_c=0))
    values = {(0, 0, 0): 20, (1, 0, 0): 10, (2, 0, 0): 5}
    field = DeltaTauField(slice=slice_, values=values)
    fields = run_field_evolution(field, steps=3)
    history = structure_history_from_field_sequence(fields)
    assert history.total_tau_conserved()


def test_quasi_stable_summary_returns_required_keys():
    history = StructureHistory(structures=(_structure("a", (0, 0, 0, 1)),))
    summary = history.quasi_stable_summary(1, 0.5)
    required = {
        "total_tau_conserved",
        "max_tau_profile_l1_step_change",
        "min_support_overlap_between_steps",
        "initial_localization_ratio",
        "final_localization_ratio",
        "initial_support_size",
        "final_support_size",
        "initial_center",
        "final_center",
        "quasi_stable_pass",
    }
    assert required <= set(summary)


def test_quasi_stable_summary_fails_if_max_step_change_above_threshold():
    history = StructureHistory(
        structures=(
            _structure("a", (0, 0, 0, 10)),
            _structure("b", (0, 0, 0, 0)),
        )
    )
    summary = history.quasi_stable_summary(max_allowed_tau_profile_l1_step_change=5, min_allowed_support_overlap=0.0)
    assert summary["quasi_stable_pass"] is False


def test_quasi_stable_summary_fails_if_support_overlap_below_threshold():
    a = _structure("a", (0, 0, 0, 5), (1, 0, 0, 5))
    b = _structure("b", (2, 0, 0, 5), (3, 0, 0, 5))
    history = StructureHistory(structures=(a, b))
    summary = history.quasi_stable_summary(
        max_allowed_tau_profile_l1_step_change=100,
        min_allowed_support_overlap=0.5,
    )
    assert summary["quasi_stable_pass"] is False


def test_structure_history_from_field_sequence_labels_deterministically():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=0, max_N_b=0, max_N_c=0))
    fields = (
        uniform_delta_tau_field(slice_, 1),
        uniform_delta_tau_field(slice_, 2),
    )
    history = structure_history_from_field_sequence(fields)
    assert history.structures[0].label == "step_0"
    assert history.structures[1].label == "step_1"
