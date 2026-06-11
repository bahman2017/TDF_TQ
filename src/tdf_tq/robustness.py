"""Perturbation robustness evaluation for localized candidates (Stage 4B)."""

from dataclasses import dataclass

from tdf_tq.candidates import (
    CandidateEvaluation,
    LocalizedCandidateCriteria,
    evaluate_localized_candidate,
)
from tdf_tq.dynamics import FieldEvolutionConfig, run_field_evolution
from tdf_tq.fields import DeltaTauField
from tdf_tq.history import structure_history_from_field_sequence
from tdf_tq.neighborhoods import is_spatial_unit_neighbor, spatial_unit_neighbors
from tdf_tq.nontriviality import (
    CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
    NontrivialStabilityAssessment,
    classify_nontrivial_stability,
)
from tdf_tq.packets import TemporalPacket
from tdf_tq.structure import active_center_of_excess_tau, packet_structure_from_field

_MAX_PERTURBATIONS = 12


@dataclass(frozen=True)
class RobustnessResult:
    """Aggregated robustness outcome for one seed and update rule."""

    seed_label: str
    update_rule_label: str
    perturbation_count: int
    stable_count: int
    inconclusive_count: int
    fail_count: int
    robustness_ratio: float
    assessments: tuple[NontrivialStabilityAssessment, ...]


def _field_changed(initial: DeltaTauField, final: DeltaTauField) -> bool:
    return dict(initial.values) != dict(final.values)


def move_one_excess_tau_to_neighbor(
    field: DeltaTauField,
    source_counts: tuple[int, int, int],
    target_counts: tuple[int, int, int],
) -> DeltaTauField:
    """Move exactly one excess tau count from source to a unit neighbor."""
    baseline = field.min_tau()
    if not field.slice.bounds.contains_spatial_counts(*source_counts):
        raise ValueError("source_counts outside field bounds")
    if not field.slice.bounds.contains_spatial_counts(*target_counts):
        raise ValueError("target_counts outside field bounds")
    source_tau = field.tau_at_counts(*source_counts)
    if source_tau <= baseline:
        raise ValueError("source must have tau above baseline")
    source_packet = TemporalPacket(
        N_a=source_counts[0],
        N_b=source_counts[1],
        N_c=source_counts[2],
        N_t=field.slice.N_t,
    )
    target_packet = TemporalPacket(
        N_a=target_counts[0],
        N_b=target_counts[1],
        N_c=target_counts[2],
        N_t=field.slice.N_t,
    )
    if not is_spatial_unit_neighbor(source_packet, target_packet):
        raise ValueError("target must be a spatial unit neighbor of source")
    working = dict(field.values)
    working[source_counts] = source_tau - 1
    working[target_counts] = field.tau_at_counts(*target_counts) + 1
    return DeltaTauField(slice=field.slice, values=working)


def deterministic_single_step_perturbations(
    field: DeltaTauField,
) -> tuple[tuple[str, DeltaTauField], ...]:
    """Deterministic single-tau neighbor moves from active sites (max 12)."""
    baseline = field.min_tau()
    perturbations: list[tuple[str, DeltaTauField]] = []
    active_sites = sorted(
        key for key, tau in field.values.items() if tau > baseline
    )
    for source in active_sites:
        source_packet = TemporalPacket(
            N_a=source[0], N_b=source[1], N_c=source[2],
            N_t=field.slice.N_t,
        )
        neighbors = sorted(
            (n.N_a, n.N_b, n.N_c)
            for n in spatial_unit_neighbors(source_packet)
            if field.slice.bounds.contains_spatial_counts(n.N_a, n.N_b, n.N_c)
        )
        for target in neighbors:
            try:
                perturbed = move_one_excess_tau_to_neighbor(field, source, target)
            except ValueError:
                continue
            label = f"move_{source[0]}_{source[1]}_{source[2]}_to_{target[0]}_{target[1]}_{target[2]}"
            perturbations.append((label, perturbed))
            if len(perturbations) >= _MAX_PERTURBATIONS:
                return tuple(perturbations)
    return tuple(perturbations)


def _run_evolution_and_evaluate(
    initial_field: DeltaTauField,
    seed_label: str,
    update_rule_label: str,
    steps: int,
    evolution_config: FieldEvolutionConfig,
    criteria: LocalizedCandidateCriteria,
    anchor_counts: tuple[int, int, int] | None,
) -> tuple[CandidateEvaluation, bool]:
    kwargs: dict = {
        "steps": steps,
        "config": evolution_config,
        "step_kind": update_rule_label,
    }
    if update_rule_label == "conservative_centered_cohesion":
        kwargs["anchor_counts"] = anchor_counts
    fields = run_field_evolution(initial_field, **kwargs)
    history = structure_history_from_field_sequence(fields, label_prefix=seed_label)
    evaluation = evaluate_localized_candidate(history, criteria=criteria, seed_label=seed_label)
    changed = _field_changed(fields[0], fields[-1])
    return evaluation, changed


def evaluate_candidate_robustness(
    seed_label: str,
    initial_field: DeltaTauField,
    update_rule_label: str,
    steps: int,
    evolution_config: FieldEvolutionConfig,
    criteria: LocalizedCandidateCriteria,
    anchor_counts: tuple[int, int, int] | None = None,
) -> RobustnessResult:
    """Evaluate unperturbed and perturbed histories under one update rule."""
    if update_rule_label == "conservative_centered_cohesion" and anchor_counts is None:
        raise ValueError("anchor_counts required for conservative_centered_cohesion")

    unperturbed_eval, unperturbed_changed = _run_evolution_and_evaluate(
        initial_field,
        seed_label,
        update_rule_label,
        steps,
        evolution_config,
        criteria,
        anchor_counts,
    )

    perturbations = deterministic_single_step_perturbations(initial_field)
    perturbation_evals: list[tuple[CandidateEvaluation, bool]] = []
    for _label, perturbed_field in perturbations:
        perturbation_evals.append(
            _run_evolution_and_evaluate(
                perturbed_field,
                seed_label,
                update_rule_label,
                steps,
                evolution_config,
                criteria,
                anchor_counts,
            )
        )

    perturbation_robust = bool(perturbations) and all(
        peval.passed for peval, _ in perturbation_evals
    )

    assessments: list[NontrivialStabilityAssessment] = [
        classify_nontrivial_stability(
            unperturbed_eval,
            update_rule_label,
            unperturbed_changed,
            perturbation_robust,
        )
    ]
    for (_label, _field), (peval, pchanged) in zip(perturbations, perturbation_evals):
        assessments.append(
            classify_nontrivial_stability(
                peval,
                update_rule_label,
                pchanged,
                perturbation_robust=False,
            )
        )

    stable_count = sum(
        1 for a in assessments if a.classification == CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE
    )
    inconclusive_count = sum(
        1 for a in assessments if a.classification == "INCONCLUSIVE"
    )
    fail_count = sum(1 for a in assessments if a.classification == "FAIL")
    perturbation_count = len(assessments)
    robustness_ratio = stable_count / perturbation_count if perturbation_count else 0.0

    return RobustnessResult(
        seed_label=seed_label,
        update_rule_label=update_rule_label,
        perturbation_count=perturbation_count,
        stable_count=stable_count,
        inconclusive_count=inconclusive_count,
        fail_count=fail_count,
        robustness_ratio=robustness_ratio,
        assessments=tuple(assessments),
    )


def anchor_counts_from_field(field: DeltaTauField) -> tuple[int, int, int]:
    """Deterministic anchor from active excess centroid, else slice center."""
    structure = packet_structure_from_field(field, label="anchor_source")
    baseline = structure.baseline_tau()
    center = active_center_of_excess_tau(structure, baseline)
    if center is not None:
        anchor = (
            round(center[0]),
            round(center[1]),
            round(center[2]),
        )
        if field.slice.bounds.contains_spatial_counts(*anchor):
            return anchor
    return (
        field.slice.bounds.max_N_a // 2,
        field.slice.bounds.max_N_b // 2,
        field.slice.bounds.max_N_c // 2,
    )
