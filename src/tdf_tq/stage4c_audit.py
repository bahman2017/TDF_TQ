"""Stage 4C fragility boundary and negative-result audit utilities."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from tdf_tq.candidates import LocalizedCandidateCriteria, evaluate_localized_candidate
from tdf_tq.dynamics import FieldEvolutionConfig, run_field_evolution
from tdf_tq.fields import DeltaTauField
from tdf_tq.history import structure_history_from_field_sequence
from tdf_tq.nontriviality import (
    CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
    CLASS_TRIVIAL_STABLE_CONTROL,
    NontrivialStabilityAssessment,
    classify_nontrivial_stability,
)
from tdf_tq.patterns import compact_square_field, plus_cross_field
from tdf_tq.robustness import (
    anchor_counts_from_field,
    deterministic_single_step_perturbations,
    move_one_excess_tau_to_neighbor,
)
from tdf_tq.space import SpatialBounds, SpatialSlice

STAGE4B_BEST_RESULT = {
    "seed_label": "compact_2x2_corner",
    "update_rule_label": "conservative_centered_cohesion",
    "stable_count": 1,
    "robustness_ratio": 0.07692307692307693,
}

STAGE4C_CANDIDATES = (
    ("compact_2x2_corner", "conservative_centered_cohesion"),
    ("plus_cross_center", "conservative_centered_cohesion"),
)

VERDICT_ROBUST_TOY_CANDIDATE = "ROBUST_TOY_CANDIDATE"
VERDICT_FRAGILE_TOY_ARTIFACT = "FRAGILE_TOY_ARTIFACT"
VERDICT_NEGATIVE_RESULT = "NEGATIVE_RESULT"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE"

_LIMITATION = (
    "Toy audit label only; not a particle, not an electron, not validated physics."
)
_NON_CLAIMS = (
    "No particle, electron, photon, mass, charge, spin, energy, hbar, alpha, QM, GR, or validated physics.",
)

GRID_SIZES: tuple[tuple[str, int, int, int], ...] = (
    ("3x3x1", 2, 2, 0),
    ("5x5x1", 4, 4, 0),
)

STEP_COUNTS: tuple[int, ...] = (3, 5, 8, 13)

DEFAULT_BASELINE_TAU = 10
DEFAULT_EXCESS_TAU = 10
DEFAULT_EVOLUTION_CONFIG = FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)


def criteria_profiles() -> dict[str, LocalizedCandidateCriteria]:
    """Named Stage 4C criteria profiles."""
    base = LocalizedCandidateCriteria()
    return {
        "stage4b_original": base,
        "stricter_localization": LocalizedCandidateCriteria(
            min_final_localization_ratio=0.50,
        ),
        "stricter_overlap": LocalizedCandidateCriteria(
            min_active_support_overlap=0.75,
        ),
        "stricter_drift": LocalizedCandidateCriteria(
            max_center_drift=0.5,
        ),
        "combined_strict": LocalizedCandidateCriteria(
            min_final_localization_ratio=0.50,
            min_active_support_overlap=0.75,
            max_center_drift=0.5,
            max_final_active_support_size=4,
        ),
    }


def make_slice(max_n_a: int, max_n_b: int, max_n_c: int = 0) -> SpatialSlice:
    return SpatialSlice(
        N_t=0,
        bounds=SpatialBounds(max_N_a=max_n_a, max_N_b=max_n_b, max_N_c=max_n_c),
    )


def _spatial_positions(slice_: SpatialSlice) -> tuple[tuple[int, int, int], ...]:
    positions: list[tuple[int, int, int]] = []
    for n_a in range(slice_.bounds.max_N_a + 1):
        for n_b in range(slice_.bounds.max_N_b + 1):
            for n_c in range(slice_.bounds.max_N_c + 1):
                positions.append((n_a, n_b, n_c))
    return tuple(positions)


def build_candidate_field(
    seed_label: str,
    slice_: SpatialSlice,
    baseline_tau: int = DEFAULT_BASELINE_TAU,
    excess_tau: int = DEFAULT_EXCESS_TAU,
    lower_corner: tuple[int, int, int] = (0, 0, 0),
) -> DeltaTauField:
    """Build deterministic candidate seed field on a slice."""
    center = (
        slice_.bounds.max_N_a // 2,
        slice_.bounds.max_N_b // 2,
        slice_.bounds.max_N_c // 2,
    )
    if seed_label == "compact_2x2_corner":
        return compact_square_field(
            slice_,
            lower_corner=lower_corner,
            baseline_tau=baseline_tau,
            block_excess_tau=excess_tau,
            size_N_a=2,
            size_N_b=2,
            size_N_c=1,
        )
    if seed_label == "plus_cross_center":
        return plus_cross_field(
            slice_,
            center=center,
            baseline_tau=baseline_tau,
            center_excess_tau=excess_tau,
            arm_excess_tau=max(1, excess_tau // 2),
        )
    raise ValueError(f"unknown seed_label: {seed_label!r}")


def embed_field_in_larger_grid(
    source_field: DeltaTauField,
    target_slice: SpatialSlice,
    offset: tuple[int, int, int],
    baseline_tau: int = DEFAULT_BASELINE_TAU,
) -> DeltaTauField:
    """Embed a smaller-grid pattern into a larger grid at offset."""
    values = {pos: baseline_tau for pos in _spatial_positions(target_slice)}
    for (n_a, n_b, n_c), tau in source_field.values.items():
        key = (n_a + offset[0], n_b + offset[1], n_c + offset[2])
        if target_slice.bounds.contains_spatial_counts(*key):
            values[key] = tau
    return DeltaTauField(slice=target_slice, values=values)


def _is_boundary_site(
    counts: tuple[int, int, int],
    slice_: SpatialSlice,
) -> bool:
    n_a, n_b, n_c = counts
    b = slice_.bounds
    return (
        n_a in (0, b.max_N_a)
        or n_b in (0, b.max_N_b)
        or n_c in (0, b.max_N_c)
    )


def deterministic_two_step_perturbations(
    field: DeltaTauField,
    max_count: int = 24,
) -> tuple[tuple[str, DeltaTauField], ...]:
    """Apply two sequential single-tau moves (deterministic, capped)."""
    singles = deterministic_single_step_perturbations(field)
    results: list[tuple[str, DeltaTauField]] = []
    for label_a, field_a in singles:
        for label_b, field_b in deterministic_single_step_perturbations(field_a):
            results.append((f"two_step_{label_a}__{label_b}", field_b))
            if len(results) >= max_count:
                return tuple(results)
    return tuple(results)


def boundary_adjacent_perturbations(
    field: DeltaTauField,
) -> tuple[tuple[str, DeltaTauField], ...]:
    """Single-tau moves where source or target lies on the grid boundary."""
    results: list[tuple[str, DeltaTauField]] = []
    for label, perturbed in deterministic_single_step_perturbations(field):
        parts = label.replace("move_", "").split("_to_")
        if len(parts) != 2:
            continue
        src = tuple(int(x) for x in parts[0].split("_"))
        dst = tuple(int(x) for x in parts[1].split("_"))
        if _is_boundary_site(src, field.slice) or _is_boundary_site(dst, field.slice):
            results.append((f"boundary_{label}", perturbed))
    return tuple(results)


def deterministic_shuffled_excess_field(field: DeltaTauField) -> DeltaTauField:
    """Deterministic negative control: rotate excess among active sites."""
    baseline = field.min_tau()
    active = sorted(key for key, tau in field.values.items() if tau > baseline)
    if len(active) < 2:
        return DeltaTauField(slice=field.slice, values=dict(field.values))
    excesses = [field.values[key] - baseline for key in active]
    rotated = excesses[1:] + excesses[:1]
    values = dict(field.values)
    for key, excess in zip(active, rotated):
        values[key] = baseline + excess
    return DeltaTauField(slice=field.slice, values=values)


def alternate_anchors(
    field: DeltaTauField,
) -> dict[str, tuple[int, int, int]]:
    """Deterministic anchor variants for cohesion audits."""
    b = field.slice.bounds
    grid_center = (b.max_N_a // 2, b.max_N_b // 2, b.max_N_c // 2)
    centroid = anchor_counts_from_field(field)
    anchors: dict[str, tuple[int, int, int]] = {
        "centroid": centroid,
        "grid_center": grid_center,
    }
    cx, cy, cz = centroid
    for name, candidate in (
        ("shift_plus_a", (cx + 1, cy, cz)),
        ("shift_minus_b", (cx, cy - 1 if cy > 0 else cy, cz)),
    ):
        if field.slice.bounds.contains_spatial_counts(*candidate):
            anchors[name] = candidate
    return anchors


def _field_changed(initial: DeltaTauField, final: DeltaTauField) -> bool:
    return dict(initial.values) != dict(final.values)


def _evaluate_field(
    initial_field: DeltaTauField,
    seed_label: str,
    update_rule: str,
    steps: int,
    config: FieldEvolutionConfig,
    criteria: LocalizedCandidateCriteria,
    anchor: tuple[int, int, int] | None,
) -> tuple[bool, bool, NontrivialStabilityAssessment]:
    kwargs: dict[str, Any] = {
        "steps": steps,
        "config": config,
        "step_kind": update_rule,
    }
    if update_rule == "conservative_centered_cohesion":
        kwargs["anchor_counts"] = anchor
    fields = run_field_evolution(initial_field, **kwargs)
    history = structure_history_from_field_sequence(fields, label_prefix=seed_label)
    evaluation = evaluate_localized_candidate(history, criteria=criteria, seed_label=seed_label)
    changed = _field_changed(fields[0], fields[-1])
    perturbation_robust = False
    assessment = classify_nontrivial_stability(
        evaluation, update_rule, changed, perturbation_robust
    )
    return evaluation.passed, changed, assessment


def _evaluate_perturbation_suite(
    initial_field: DeltaTauField,
    seed_label: str,
    update_rule: str,
    steps: int,
    config: FieldEvolutionConfig,
    criteria: LocalizedCandidateCriteria,
    anchor: tuple[int, int, int] | None,
    perturbations: Sequence[tuple[str, DeltaTauField]],
) -> dict[str, Any]:
    unperturbed_passed, changed, unperturbed_assessment = _evaluate_field(
        initial_field, seed_label, update_rule, steps, config, criteria, anchor
    )
    perturbation_results: list[dict[str, Any]] = []
    passed_count = 0
    nontrivial_count = 0
    for label, perturbed in perturbations:
        passed, pchanged, assessment = _evaluate_field(
            perturbed, seed_label, update_rule, steps, config, criteria, anchor
        )
        if passed:
            passed_count += 1
        if assessment.classification == CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE:
            nontrivial_count += 1
        perturbation_results.append(
            {
                "label": label,
                "evaluation_passed": passed,
                "classification": assessment.classification,
            }
        )
    total = len(perturbations)
    return {
        "unperturbed_passed": unperturbed_passed,
        "unperturbed_classification": unperturbed_assessment.classification,
        "changed_across_history": changed,
        "perturbation_total": total,
        "perturbation_passed_count": passed_count,
        "perturbation_pass_fraction": passed_count / total if total else 0.0,
        "perturbation_nontrivial_count": nontrivial_count,
        "perturbations": perturbation_results,
    }


def _all_perturbations(field: DeltaTauField) -> tuple[tuple[str, DeltaTauField], ...]:
    combined: list[tuple[str, DeltaTauField]] = []
    seen: set[tuple[tuple[int, int, int], ...]] = set()
    for generator in (
        deterministic_single_step_perturbations,
        deterministic_two_step_perturbations,
        boundary_adjacent_perturbations,
    ):
        for label, perturbed in generator(field):
            key = tuple(sorted(perturbed.values.items()))
            if key in seen:
                continue
            seen.add(key)
            combined.append((label, perturbed))
    return tuple(combined)


@dataclass(frozen=True)
class CandidateAuditRecord:
    seed_label: str
    update_rule_label: str
    grid_size_results: tuple[dict[str, Any], ...]
    criteria_profile_results: tuple[dict[str, Any], ...]
    perturbation_results: tuple[dict[str, Any], ...]
    anchor_dependence_results: tuple[dict[str, Any], ...]
    fragile_pass_conditions: int
    robust_pass_conditions: int


def audit_candidate(
    seed_label: str,
    update_rule: str,
    baseline_tau: int = DEFAULT_BASELINE_TAU,
    excess_tau: int = DEFAULT_EXCESS_TAU,
    config: FieldEvolutionConfig = DEFAULT_EVOLUTION_CONFIG,
) -> CandidateAuditRecord:
    """Run full Stage 4C audit for one Stage 4B candidate."""
    profiles = criteria_profiles()
    grid_results: list[dict[str, Any]] = []
    criteria_results: list[dict[str, Any]] = []
    perturbation_results: list[dict[str, Any]] = []
    anchor_results: list[dict[str, Any]] = []
    fragile_pass = 0
    robust_pass = 0

    slice_3 = make_slice(2, 2, 0)
    field_3 = build_candidate_field(seed_label, slice_3, baseline_tau, excess_tau)
    slice_5 = make_slice(4, 4, 0)

    for grid_name, max_a, max_b, max_c in GRID_SIZES:
        if grid_name == "3x3x1":
            field = field_3
            placements = (("native", (0, 0, 0)),)
        else:
            placements = (
                ("centered", (1, 1, 0)),
                ("off_center", (0, 0, 0)),
            )
            field = None
        for placement_name, offset in placements:
            if field is None:
                target_slice = make_slice(max_a, max_b, max_c)
                field = embed_field_in_larger_grid(field_3, target_slice, offset, baseline_tau)
            anchor = anchor_counts_from_field(field)
            step_outcomes: list[dict[str, Any]] = []
            for steps in STEP_COUNTS:
                passed, _, assessment = _evaluate_field(
                    field,
                    seed_label,
                    update_rule,
                    steps,
                    config,
                    profiles["combined_strict"],
                    anchor,
                )
                step_outcomes.append(
                    {
                        "steps": steps,
                        "passed_combined_strict": passed,
                        "classification": assessment.classification,
                    }
                )
            grid_results.append(
                {
                    "grid": grid_name,
                    "placement": placement_name,
                    "offset": list(offset),
                    "step_outcomes": step_outcomes,
                }
            )
            field = None

    field = field_3
    anchor = anchor_counts_from_field(field)
    for profile_name, criteria in profiles.items():
        for steps in STEP_COUNTS:
            passed, _, assessment = _evaluate_field(
                field, seed_label, update_rule, steps, config, criteria, anchor
            )
            entry = {
                "profile": profile_name,
                "steps": steps,
                "passed": passed,
                "classification": assessment.classification,
            }
            criteria_results.append(entry)
            if passed and profile_name != "stage4b_original":
                fragile_pass += 1
            if passed and profile_name == "combined_strict" and steps in (5, 8, 13):
                robust_pass += 1

    perturbations = _all_perturbations(field)
    for ptype, generator in (
        ("single_tau", deterministic_single_step_perturbations),
        ("two_step", deterministic_two_step_perturbations),
        ("boundary_adjacent", boundary_adjacent_perturbations),
    ):
        subset = generator(field)
        result = _evaluate_perturbation_suite(
            field,
            seed_label,
            update_rule,
            steps=3,
            config=config,
            criteria=profiles["combined_strict"],
            anchor=anchor,
            perturbations=subset,
        )
        perturbation_results.append({"type": ptype, **result})

    for anchor_name, anchor_pos in alternate_anchors(field).items():
        outcomes: list[dict[str, Any]] = []
        for steps in STEP_COUNTS:
            passed, changed, assessment = _evaluate_field(
                field,
                seed_label,
                update_rule,
                steps,
                config,
                profiles["combined_strict"],
                anchor_pos,
            )
            outcomes.append(
                {
                    "steps": steps,
                    "passed": passed,
                    "classification": assessment.classification,
                    "changed": changed,
                }
            )
        anchor_results.append({"anchor_name": anchor_name, "anchor": list(anchor_pos), "outcomes": outcomes})

    return CandidateAuditRecord(
        seed_label=seed_label,
        update_rule_label=update_rule,
        grid_size_results=tuple(grid_results),
        criteria_profile_results=tuple(criteria_results),
        perturbation_results=tuple(perturbation_results),
        anchor_dependence_results=tuple(anchor_results),
        fragile_pass_conditions=fragile_pass,
        robust_pass_conditions=robust_pass,
    )


def run_negative_controls(
    baseline_tau: int = DEFAULT_BASELINE_TAU,
    excess_tau: int = DEFAULT_EXCESS_TAU,
    config: FieldEvolutionConfig = DEFAULT_EVOLUTION_CONFIG,
) -> tuple[dict[str, Any], ...]:
    """Deterministic negative controls for Stage 4C."""
    slice_3 = make_slice(2, 2, 0)
    field = build_candidate_field("compact_2x2_corner", slice_3, baseline_tau, excess_tau)
    criteria = criteria_profiles()["stage4b_original"]
    controls: list[dict[str, Any]] = []

    for rule in ("identity", "conservative_pairwise_relaxation"):
        passed, changed, assessment = _evaluate_field(
            field, "control", rule, 3, config, criteria, None
        )
        controls.append(
            {
                "control": rule,
                "passed": passed,
                "classification": assessment.classification,
                "changed": changed,
            }
        )

    shuffled = deterministic_shuffled_excess_field(field)
    passed, changed, assessment = _evaluate_field(
        shuffled,
        "shuffled_control",
        "conservative_centered_cohesion",
        3,
        config,
        criteria,
        anchor_counts_from_field(shuffled),
    )
    controls.append(
        {
            "control": "shuffled_excess_field",
            "passed": passed,
            "classification": assessment.classification,
            "changed": changed,
            "is_nontrivial": assessment.classification == CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
        }
    )

    passed, changed, assessment = _evaluate_field(
        field,
        "unchanged_identity",
        "identity",
        8,
        config,
        criteria,
        None,
    )
    controls.append(
        {
            "control": "identity_long_steps",
            "classification": assessment.classification,
            "is_nontrivial": assessment.classification == CLASS_NONTRIVIAL_STABLE_TOY_CANDIDATE,
            "changed": changed,
        }
    )
    return tuple(controls)


def determine_stage4c_verdict(
    candidate_records: Sequence[CandidateAuditRecord],
) -> str:
    """Aggregate Stage 4C verdict from candidate audit records."""
    any_robust = False
    any_fragile = False

    for record in candidate_records:
        combined_strict_passes = [
            entry
            for entry in record.criteria_profile_results
            if entry["profile"] == "combined_strict" and entry["passed"]
        ]
        multi_step_pass = len(combined_strict_passes) >= 2

        larger_grid_pass = any(
            any(step["passed_combined_strict"] for step in entry["step_outcomes"])
            for entry in record.grid_size_results
            if entry["grid"] == "5x5x1"
        )

        perturb_pass_fractions = [
            entry["perturbation_pass_fraction"]
            for entry in record.perturbation_results
            if entry["perturbation_total"] > 0
        ]
        best_perturb_fraction = max(perturb_pass_fractions) if perturb_pass_fractions else 0.0

        if multi_step_pass and larger_grid_pass and best_perturb_fraction >= 0.5:
            any_robust = True

        for entry in record.perturbation_results:
            if entry.get("unperturbed_passed") and entry["perturbation_pass_fraction"] < 0.5:
                any_fragile = True

        grid_3_pass = any(
            any(step["passed_combined_strict"] for step in entry["step_outcomes"])
            for entry in record.grid_size_results
            if entry["grid"] == "3x3x1"
        )
        grid_5_pass = any(
            any(step["passed_combined_strict"] for step in entry["step_outcomes"])
            for entry in record.grid_size_results
            if entry["grid"] == "5x5x1"
        )
        if grid_3_pass and not grid_5_pass:
            any_fragile = True

        anchors_with_pass = [
            anchor_entry["anchor_name"]
            for anchor_entry in record.anchor_dependence_results
            if any(outcome["passed"] for outcome in anchor_entry["outcomes"])
        ]
        if len(set(anchors_with_pass)) == 1 and anchors_with_pass:
            any_fragile = True

        stage4b_only = any(
            entry["profile"] == "stage4b_original" and entry["passed"]
            for entry in record.criteria_profile_results
        ) and not combined_strict_passes
        if stage4b_only:
            any_fragile = True

    if any_robust:
        return VERDICT_ROBUST_TOY_CANDIDATE
    if any_fragile:
        return VERDICT_FRAGILE_TOY_ARTIFACT
    if all(record.robust_pass_conditions == 0 for record in candidate_records):
        return VERDICT_NEGATIVE_RESULT
    return VERDICT_INCONCLUSIVE


def run_stage4c_fragility_audit(
    baseline_tau: int = DEFAULT_BASELINE_TAU,
    excess_tau: int = DEFAULT_EXCESS_TAU,
    config: FieldEvolutionConfig = DEFAULT_EVOLUTION_CONFIG,
) -> dict[str, Any]:
    """Run full Stage 4C audit and return deterministic summary dict."""
    candidate_records = tuple(
        audit_candidate(seed, rule, baseline_tau, excess_tau, config)
        for seed, rule in STAGE4C_CANDIDATES
    )
    negative_controls = run_negative_controls(baseline_tau, excess_tau, config)
    verdict = determine_stage4c_verdict(candidate_records)

    return {
        "stage": "4C",
        "statement": (
            "Stage 4C audits fragile Stage 4B nontrivial toy labels under stricter, "
            "broader deterministic checks; not particles and not electrons."
        ),
        "input_stage4b_best_result": STAGE4B_BEST_RESULT,
        "audit_config": {
            "baseline_tau": baseline_tau,
            "excess_tau": excess_tau,
            "grid_sizes": [{"name": g[0], "max_N_a": g[1], "max_N_b": g[2], "max_N_c": g[3]} for g in GRID_SIZES],
            "steps": list(STEP_COUNTS),
            "criteria_profiles": list(criteria_profiles().keys()),
            "evolution_config": {
                "threshold": config.threshold,
                "max_transfer_per_edge": config.max_transfer_per_edge,
            },
            "candidates": [list(c) for c in STAGE4C_CANDIDATES],
        },
        "candidate_results": [
            {
                "seed_label": r.seed_label,
                "update_rule_label": r.update_rule_label,
                "fragile_pass_conditions": r.fragile_pass_conditions,
                "robust_pass_conditions": r.robust_pass_conditions,
            }
            for r in candidate_records
        ],
        "grid_size_results": [
            {**entry, "seed_label": r.seed_label, "update_rule_label": r.update_rule_label}
            for r in candidate_records
            for entry in r.grid_size_results
        ],
        "criteria_profile_results": [
            {**entry, "seed_label": r.seed_label, "update_rule_label": r.update_rule_label}
            for r in candidate_records
            for entry in r.criteria_profile_results
        ],
        "perturbation_results": [
            {**entry, "seed_label": r.seed_label, "update_rule_label": r.update_rule_label}
            for r in candidate_records
            for entry in r.perturbation_results
        ],
        "anchor_dependence_results": [
            {**entry, "seed_label": r.seed_label, "update_rule_label": r.update_rule_label}
            for r in candidate_records
            for entry in r.anchor_dependence_results
        ],
        "negative_controls": list(negative_controls),
        "verdict": verdict,
        "limitations": [
            "Cohesion is an arbitrary toy retention rule, not physics.",
            "Audit thresholds are deterministic but not experimentally calibrated.",
            "Negative or fragile outcomes are scientifically acceptable.",
            _LIMITATION,
        ],
        "non_claims": list(_NON_CLAIMS),
        "next_recommended_stage": (
            "Stage 5 exploratory criteria design only if robust toy evidence appears; "
            "otherwise document negative-result boundary and refine search space."
        ),
    }
