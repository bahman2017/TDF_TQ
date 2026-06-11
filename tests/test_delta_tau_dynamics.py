"""Tests for toy field evolution (Stage 3B)."""

import pytest

from tdf_tq import (
    DeltaTauField,
    FieldEvolutionConfig,
    SpatialBounds,
    SpatialSlice,
    conservative_pairwise_relaxation_step,
    identity_step,
    run_field_evolution,
    spatial_edges,
)


def _slice_1d(size: int = 2) -> SpatialSlice:
    return SpatialSlice(
        N_t=0,
        bounds=SpatialBounds(max_N_a=size, max_N_b=0, max_N_c=0),
    )


def _field_from_values(slice_: SpatialSlice, values: dict[tuple[int, int, int], int]) -> DeltaTauField:
    return DeltaTauField(slice=slice_, values=values)


def test_field_evolution_config_validates_threshold_and_max_transfer():
    FieldEvolutionConfig(threshold=1, max_transfer_per_edge=1)
    with pytest.raises(ValueError):
        FieldEvolutionConfig(threshold=0, max_transfer_per_edge=1)
    with pytest.raises(ValueError):
        FieldEvolutionConfig(threshold=1, max_transfer_per_edge=0)
    with pytest.raises(TypeError):
        FieldEvolutionConfig(threshold=True, max_transfer_per_edge=1)


def test_spatial_edges_returns_deterministic_unique_edges():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=1, max_N_c=0))
    edges = spatial_edges(slice_)
    assert edges == tuple(sorted(edges))
    assert len(edges) == len(set(edges))
    assert ((0, 0, 0), (1, 0, 0)) in edges
    assert ((0, 0, 0), (0, 1, 0)) in edges


def test_identity_step_preserves_values():
    slice_ = _slice_1d(1)
    values = {(0, 0, 0): 3, (1, 0, 0): 5}
    field = _field_from_values(slice_, values)
    result = identity_step(field)
    assert dict(result.values) == values


def test_conservative_pairwise_relaxation_preserves_total_tau():
    slice_ = _slice_1d(2)
    values = {(0, 0, 0): 20, (1, 0, 0): 10, (2, 0, 0): 5}
    field = _field_from_values(slice_, values)
    before = sum(field.values.values())
    after = conservative_pairwise_relaxation_step(field)
    assert sum(after.values.values()) == before


def test_relaxation_transfers_from_higher_to_lower_when_threshold_met():
    slice_ = _slice_1d(1)
    field = _field_from_values(slice_, {(0, 0, 0): 12, (1, 0, 0): 8})
    result = conservative_pairwise_relaxation_step(
        field, FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)
    )
    assert result.values[(0, 0, 0)] == 11
    assert result.values[(1, 0, 0)] == 9


def test_relaxation_does_not_transfer_when_below_threshold():
    slice_ = _slice_1d(1)
    field = _field_from_values(slice_, {(0, 0, 0): 11, (1, 0, 0): 10})
    result = conservative_pairwise_relaxation_step(
        field, FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)
    )
    assert dict(result.values) == dict(field.values)


def test_relaxation_never_creates_negative_tau():
    slice_ = _slice_1d(2)
    values = {(0, 0, 0): 0, (1, 0, 0): 10, (2, 0, 0): 0}
    field = _field_from_values(slice_, values)
    result = conservative_pairwise_relaxation_step(field)
    assert all(v >= 0 for v in result.values.values())


def test_run_field_evolution_returns_initial_plus_requested_steps():
    slice_ = _slice_1d(1)
    field = _field_from_values(slice_, {(0, 0, 0): 5, (1, 0, 0): 5})
    history = run_field_evolution(field, steps=2, step_kind="identity")
    assert len(history) == 3
    assert history[0] is field or dict(history[0].values) == dict(field.values)


def test_run_field_evolution_steps_zero_returns_only_initial():
    slice_ = _slice_1d(0)
    field = _field_from_values(slice_, {(0, 0, 0): 1})
    history = run_field_evolution(field, steps=0)
    assert history == (field,)


def test_run_field_evolution_rejects_negative_and_bool_steps():
    slice_ = _slice_1d(0)
    field = _field_from_values(slice_, {(0, 0, 0): 1})
    with pytest.raises(ValueError):
        run_field_evolution(field, steps=-1)
    with pytest.raises(TypeError):
        run_field_evolution(field, steps=True)


def test_run_field_evolution_rejects_unknown_step_kind():
    slice_ = _slice_1d(0)
    field = _field_from_values(slice_, {(0, 0, 0): 1})
    with pytest.raises(ValueError, match="unknown step_kind"):
        run_field_evolution(field, steps=1, step_kind="stochastic")


def test_relaxation_evolution_is_deterministic_across_repeated_runs():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=1, max_N_c=0))
    values = {(n_a, n_b, 0): 10 for n_a in range(3) for n_b in range(2)}
    values[(1, 0, 0)] = 20
    field = _field_from_values(slice_, values)
    config = FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)
    run_a = run_field_evolution(field, steps=3, config=config)
    run_b = run_field_evolution(field, steps=3, config=config)
    assert [dict(f.values) for f in run_a] == [dict(f.values) for f in run_b]
