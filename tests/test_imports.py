"""Package import smoke tests."""

import tdf_tq
from tdf_tq import (
    C_SYMBOL,
    L_Q_SYMBOL,
    T_Q_SYMBOL,
    TemporalPacket,
    delta_tau,
    emergent_euclidean_distance,
    spatial_count_delta,
    working_speed_limit,
)


def test_package_version():
    assert tdf_tq.__version__ == "0.1.0"


def test_public_symbols_importable():
    assert T_Q_SYMBOL == "t_q"
    assert L_Q_SYMBOL == "l_q"
    assert C_SYMBOL == "c"
    assert callable(working_speed_limit)
    assert callable(TemporalPacket)
    assert callable(delta_tau)
    assert callable(spatial_count_delta)
    assert callable(emergent_euclidean_distance)
