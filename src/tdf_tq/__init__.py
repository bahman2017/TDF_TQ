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
from tdf_tq.metrics import (
    deterministic_spatial_path,
    emergent_manhattan_distance,
    emergent_unit_edge_length,
    spatial_count_l1_distance,
    spatial_graph_distance_steps,
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
from tdf_tq.space import SpatialBounds, SpatialSlice

__all__ = [
    "C_SYMBOL",
    "L_Q_SYMBOL",
    "T_Q_SYMBOL",
    "PacketDelta",
    "SpatialBounds",
    "SpatialSlice",
    "TemporalPacket",
    "delta_tau",
    "delta_tau_matches",
    "deterministic_spatial_path",
    "emergent_euclidean_distance",
    "emergent_manhattan_distance",
    "emergent_unit_edge_length",
    "is_spatial_unit_neighbor",
    "packet_delta",
    "same_spatial_position",
    "same_temporal_layer",
    "spatial_count_delta",
    "spatial_count_l1_distance",
    "spatial_graph_distance_steps",
    "spatial_unit_axis",
    "spatial_unit_neighbors",
    "translate_packet",
    "working_speed_limit",
]

__version__ = "0.1.0"
