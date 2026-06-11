"""Tests for gravity-like field proxies (Stage 3A)."""

import inspect
import math

import pytest

from tdf_tq import (
    DeltaTauField,
    SpatialBounds,
    SpatialSlice,
    finite_difference_gradient,
    gradient_magnitude,
    gravity_like_direction_proxy,
    laplacian_proxy,
    normalized_direction,
    radial_delta_tau_field,
    uniform_delta_tau_field,
)
from tdf_tq import gravity_proxy as gravity_proxy_module


def _linear_n_a_field(max_n_a: int = 2) -> DeltaTauField:
    slice_ = SpatialSlice(
        N_t=0,
        bounds=SpatialBounds(max_N_a=max_n_a, max_N_b=0, max_N_c=0),
    )
    values = {(n_a, 0, 0): n_a for n_a in range(max_n_a + 1)}
    return DeltaTauField(slice=slice_, values=values)


def test_uniform_field_gradient_is_zero():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))
    field = uniform_delta_tau_field(slice_, tau_value=5)
    for n_a in range(3):
        for n_b in range(3):
            assert finite_difference_gradient(field, (n_a, n_b, 0)) == (0.0, 0.0, 0.0)


def test_uniform_field_laplacian_proxy_is_zero():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=1, max_N_c=0))
    field = uniform_delta_tau_field(slice_, tau_value=5)
    assert laplacian_proxy(field, (0, 0, 0)) == 0.0
    assert laplacian_proxy(field, (1, 1, 0)) == 0.0


def test_linear_tau_profile_along_n_a_has_expected_gradient():
    field = _linear_n_a_field(max_n_a=2)
    assert finite_difference_gradient(field, (1, 0, 0)) == (1.0, 0.0, 0.0)


def test_boundary_forward_backward_differences_are_deterministic():
    field = _linear_n_a_field(max_n_a=2)
    assert finite_difference_gradient(field, (0, 0, 0)) == (1.0, 0.0, 0.0)
    assert finite_difference_gradient(field, (2, 0, 0)) == (1.0, 0.0, 0.0)


def test_gradient_magnitude_matches_euclidean_norm():
    field = _linear_n_a_field(max_n_a=2)
    grad = finite_difference_gradient(field, (1, 0, 0))
    assert gradient_magnitude(field, (1, 0, 0)) == math.sqrt(
        grad[0] ** 2 + grad[1] ** 2 + grad[2] ** 2
    )


def test_gravity_like_direction_proxy_returns_negative_gradient():
    field = _linear_n_a_field(max_n_a=2)
    grad = finite_difference_gradient(field, (1, 0, 0))
    direction = gravity_like_direction_proxy(field, (1, 0, 0))
    assert direction == (-grad[0], -grad[1], -grad[2])


def test_normalized_direction_zero_for_zero_input():
    assert normalized_direction((0.0, 0.0, 0.0)) == (0.0, 0.0, 0.0)


def test_normalized_direction_unit_vector_for_nonzero_input():
    result = normalized_direction((3.0, 0.0, 4.0))
    assert result == (0.6, 0.0, 0.8)
    magnitude = math.sqrt(result[0] ** 2 + result[1] ** 2 + result[2] ** 2)
    assert magnitude == pytest.approx(1.0)


def test_radial_field_nonzero_gradient_away_from_center():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=2, max_N_c=0))
    field = radial_delta_tau_field(slice_, center=(0, 0, 0), base_tau=10, strength=2)
    grad = finite_difference_gradient(field, (1, 1, 0))
    assert grad != (0.0, 0.0, 0.0)


def test_laplacian_proxy_deterministic_at_boundary_and_interior():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=2, max_N_b=0, max_N_c=0))
    field = radial_delta_tau_field(slice_, center=(0, 0, 0), base_tau=0, strength=1)
    assert laplacian_proxy(field, (0, 0, 0)) == 1.0
    assert laplacian_proxy(field, (1, 0, 0)) == 0.0
    assert laplacian_proxy(field, (2, 0, 0)) == -1.0


def test_proxy_functions_reject_counts_outside_bounds():
    slice_ = SpatialSlice(N_t=0, bounds=SpatialBounds(max_N_a=1, max_N_b=0, max_N_c=0))
    field = uniform_delta_tau_field(slice_, tau_value=1)
    with pytest.raises(ValueError, match="outside"):
        finite_difference_gradient(field, (2, 0, 0))
    with pytest.raises(ValueError, match="outside"):
        laplacian_proxy(field, (2, 0, 0))
    with pytest.raises(ValueError, match="outside"):
        gravity_like_direction_proxy(field, (2, 0, 0))


def test_no_physical_constants_in_gravity_proxy_module():
    source = inspect.getsource(gravity_proxy_module)
    forbidden = ("G_newton", "hbar", "Planck", "electron_mass", "charge", "spin")
    for token in forbidden:
        assert token not in source
