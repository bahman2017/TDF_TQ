"""TDF_TQ — Temporal Quantum Foundation."""

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
from tdf_tq.neighborhoods import (
    is_spatial_unit_neighbor,
    spatial_unit_axis,
    spatial_unit_neighbors,
)
from tdf_tq.packets import TemporalPacket
from tdf_tq.relations import (
    PacketDelta,
    delta_tau_matches,
    packet_delta,
    same_spatial_position,
    same_temporal_layer,
    translate_packet,
)

__all__ = [
    "C_SYMBOL",
    "L_Q_SYMBOL",
    "T_Q_SYMBOL",
    "PacketDelta",
    "TemporalPacket",
    "delta_tau",
    "delta_tau_matches",
    "emergent_euclidean_distance",
    "is_spatial_unit_neighbor",
    "packet_delta",
    "same_spatial_position",
    "same_temporal_layer",
    "spatial_count_delta",
    "spatial_unit_axis",
    "spatial_unit_neighbors",
    "translate_packet",
    "working_speed_limit",
]

__version__ = "0.1.0"
