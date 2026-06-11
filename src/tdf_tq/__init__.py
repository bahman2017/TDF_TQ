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
from tdf_tq.fields import (
    DeltaTauField,
    radial_delta_tau_field,
    uniform_delta_tau_field,
)
from tdf_tq.gravity_proxy import (
    finite_difference_gradient,
    gradient_magnitude,
    gravity_like_direction_proxy,
    laplacian_proxy,
    normalized_direction,
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
    "DeltaTauField",
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
    "finite_difference_gradient",
    "gradient_magnitude",
    "gravity_like_direction_proxy",
    "is_spatial_unit_neighbor",
    "laplacian_proxy",
    "normalized_direction",
    "packet_delta",
    "radial_delta_tau_field",
    "same_spatial_position",
    "same_temporal_layer",
    "spatial_count_delta",
    "spatial_count_l1_distance",
    "spatial_graph_distance_steps",
    "spatial_unit_axis",
    "spatial_unit_neighbors",
    "translate_packet",
    "uniform_delta_tau_field",
    "working_speed_limit",
]

__version__ = "0.1.0"
