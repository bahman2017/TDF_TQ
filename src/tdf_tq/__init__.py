"""TDF_TQ — Temporal Quantum Foundation."""

from tdf_tq.candidates import (
    CandidateEvaluation,
    LocalizedCandidateCriteria,
    evaluate_localized_candidate,
)
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
from tdf_tq.dynamics import (
    FieldEvolutionConfig,
    conservative_centered_cohesion_step,
    conservative_pairwise_relaxation_step,
    identity_step,
    run_field_evolution,
    spatial_edges,
)
from tdf_tq.nontriviality import (
    CLASS_FAIL,
    CLASS_INCONCLUSIVE,
    CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
    CLASS_TRIVIAL_STABLE_CONTROL,
    NontrivialStabilityAssessment,
    classify_nontrivial_stability,
)
from tdf_tq.robustness import (
    RobustnessResult,
    anchor_counts_from_field,
    deterministic_single_step_perturbations,
    evaluate_candidate_robustness,
    move_one_excess_tau_to_neighbor,
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
from tdf_tq.history import (
    StructureHistory,
    active_center_drift,
    active_center_series,
    active_localization_ratio_series,
    active_support_size_series,
    initial_baseline_tau,
    max_active_tau_profile_l1_step_change,
    min_active_support_overlap_between_steps,
    structure_history_from_field_sequence,
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
from tdf_tq.patterns import (
    compact_square_field,
    deterministic_seed_suite,
    plus_cross_field,
    single_peak_field,
)
from tdf_tq.relations import (
    PacketDelta,
    delta_tau_matches,
    packet_delta,
    same_spatial_position,
    same_temporal_layer,
    translate_packet,
)
from tdf_tq.search import (
    best_candidate_evaluation,
    best_stage4b_result,
    run_stable_localized_structure_search,
    run_stage4b_robustness_suite,
)
from tdf_tq.space import SpatialBounds, SpatialSlice
from tdf_tq.stability import is_history_quasi_stable, structure_persistence_score
from tdf_tq.structure import (
    PacketStructure,
    active_center_of_excess_tau,
    active_localization_ratio,
    active_support_above_baseline,
    active_support_overlap_ratio,
    active_support_size_above_baseline,
    active_tau_profile_l1_difference,
    active_tau_values_above_baseline,
    packet_structure_from_field,
    support_overlap_ratio,
    tau_profile_l1_difference,
)

__all__ = [
    "C_SYMBOL",
    "L_Q_SYMBOL",
    "T_Q_SYMBOL",
    "CLASS_FAIL",
    "CLASS_INCONCLUSIVE",
    "CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE",
    "CLASS_TRIVIAL_STABLE_CONTROL",
    "CandidateEvaluation",
    "DeltaTauField",
    "FieldEvolutionConfig",
    "LocalizedCandidateCriteria",
    "NontrivialStabilityAssessment",
    "RobustnessResult",
    "PacketDelta",
    "PacketStructure",
    "SpatialBounds",
    "SpatialSlice",
    "StructureHistory",
    "TemporalPacket",
    "active_center_drift",
    "active_center_of_excess_tau",
    "active_center_series",
    "active_localization_ratio",
    "active_localization_ratio_series",
    "active_support_above_baseline",
    "active_support_overlap_ratio",
    "active_support_size_above_baseline",
    "active_support_size_series",
    "active_tau_profile_l1_difference",
    "active_tau_values_above_baseline",
    "anchor_counts_from_field",
    "best_candidate_evaluation",
    "best_stage4b_result",
    "classify_nontrivial_stability",
    "compact_square_field",
    "conservative_centered_cohesion_step",
    "conservative_pairwise_relaxation_step",
    "deterministic_single_step_perturbations",
    "evaluate_candidate_robustness",
    "delta_tau",
    "delta_tau_matches",
    "deterministic_seed_suite",
    "deterministic_spatial_path",
    "emergent_euclidean_distance",
    "emergent_manhattan_distance",
    "emergent_unit_edge_length",
    "evaluate_localized_candidate",
    "finite_difference_gradient",
    "gradient_magnitude",
    "gravity_like_direction_proxy",
    "identity_step",
    "initial_baseline_tau",
    "is_history_quasi_stable",
    "is_spatial_unit_neighbor",
    "laplacian_proxy",
    "max_active_tau_profile_l1_step_change",
    "min_active_support_overlap_between_steps",
    "normalized_direction",
    "packet_delta",
    "packet_structure_from_field",
    "plus_cross_field",
    "radial_delta_tau_field",
    "move_one_excess_tau_to_neighbor",
    "run_field_evolution",
    "run_stable_localized_structure_search",
    "run_stage4b_robustness_suite",
    "same_spatial_position",
    "same_temporal_layer",
    "single_peak_field",
    "spatial_count_delta",
    "spatial_count_l1_distance",
    "spatial_edges",
    "spatial_graph_distance_steps",
    "spatial_unit_axis",
    "spatial_unit_neighbors",
    "structure_history_from_field_sequence",
    "structure_persistence_score",
    "support_overlap_ratio",
    "tau_profile_l1_difference",
    "translate_packet",
    "uniform_delta_tau_field",
    "working_speed_limit",
]

__version__ = "0.1.0"
