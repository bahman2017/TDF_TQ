"""TDF_TQ — Temporal Quantum Foundation (Stage 0 repository foundation)."""

from tdf_tq.constants import (
    C_SYMBOL,
    L_Q_SYMBOL,
    T_Q_SYMBOL,
    working_speed_limit,
)
from tdf_tq.distances import (
    delta_tau,
    emergent_euclidean_distance,
    spatial_count_delta,
)
from tdf_tq.packets import TemporalPacket

__all__ = [
    "C_SYMBOL",
    "L_Q_SYMBOL",
    "T_Q_SYMBOL",
    "TemporalPacket",
    "delta_tau",
    "emergent_euclidean_distance",
    "spatial_count_delta",
    "working_speed_limit",
]

__version__ = "0.1.0"
