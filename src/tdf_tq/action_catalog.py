"""Stage 4D minimal temporal Action catalog, diagnostics, and integration summary."""

from __future__ import annotations

import random
from typing import Any

from tdf_tq.actions import (
    ActionEvolutionState,
    TemporalAction,
    minimal_action_catalog,
    run_action_steps,
    validate_action_boundary,
)
from tdf_tq.fields import DeltaTauField
from tdf_tq.metrics import emergent_manhattan_distance
from tdf_tq.neighborhoods import spatial_unit_neighbors
from tdf_tq.packets import TemporalPacket
from tdf_tq.patterns import compact_square_field, plus_cross_field, single_peak_field
from tdf_tq.space import SpatialBounds, SpatialSlice
from tdf_tq.structure import (
    active_center_of_excess_tau,
    active_localization_ratio,
    active_support_size_above_baseline,
    packet_structure_from_field,
)

STAGE = "4D"
BRANCH = "feature/stage4d-minimal-temporal-action-catalog"

VERDICT_READY = "ACTION_CATALOG_READY"
VERDICT_INCOMPLETE = "ACTION_CATALOG_INCOMPLETE"
VERDICT_BOUNDARY_FAIL = "BOUNDARY_FAIL"
VERDICT_TEST_FAIL = "TEST_FAIL"

DEFAULT_BASELINE = 10
DEFAULT_EXCESS = 10
BENCHMARK_STEPS: tuple[int, ...] = (0, 1, 2, 3, 5, 8)

MERGED_STAGE4C_REFERENCE = {
    "integration_commit": "60126f1",
    "stage4c_verdict": "FRAGILE_TOY_ARTIFACT",
    "stage4b_best_seed": "compact_2x2_corner",
    "stage4b_best_rule": "conservative_centered_cohesion",
    "stage4b_robustness_ratio": 0.07692307692307693,
    "interpretation": (
        "Stage 4B nontrivial labels fail stricter Stage 4C stress; "
        "cohesion is fragile toy artifact, not robust structure."
    ),
}

ROADMAP_CORRECTION = {
    "corrected_stages": [
        "Stage 3 — Fundamental Temporal Actions",
        "Stage 4 — Emergent Structure Survey",
        "Stage 5 — Emergent Geometry",
        "Stage 6 — Stable Localized Structures",
        "Stage 7 — Conserved Quantities",
        "Stage 8 — QM Exploratory Layer",
        "Stage 9 — Physics Recovery Tests",
        "Stage 10 — Documentation and Zenodo Drafts",
    ],
    "deferred_legacy_wording": [
        "electron-like candidate criteria",
        "photon-like candidate",
        "near-term derived particle targets",
    ],
}

NON_CLAIMS = (
    "No GR, QM, particle, electron, photon, mass, charge, spin, energy, hbar, alpha, or validated physics.",
    "conservative_centered_cohesion is arbitrary toy retention, not physical binding.",
    "Stage 4D produces catalog and diagnostics only; no stable candidate search.",
)


def make_slice(max_n_a: int = 2, max_n_b: int = 2, max_n_c: int = 0) -> SpatialSlice:
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


def ring_shell_field(
    slice_: SpatialSlice,
    center: tuple[int, int, int],
    baseline_tau: int,
    shell_excess: int,
) -> DeltaTauField:
    """Ring-like shell excess around center; neutral seed only."""
    values = {pos: baseline_tau for pos in _spatial_positions(slice_)}
    center_packet = TemporalPacket(
        N_a=center[0], N_b=center[1], N_c=center[2], N_t=slice_.N_t
    )
    for neighbor in spatial_unit_neighbors(center_packet):
        if slice_.bounds.contains_packet(neighbor):
            key = (neighbor.N_a, neighbor.N_b, neighbor.N_c)
            values[key] = baseline_tau + shell_excess
    return DeltaTauField(slice=slice_, values=values)


def deterministic_shuffled_field(
    field: DeltaTauField,
    seed: int = 7,
) -> DeltaTauField:
    """Deterministic shuffled-excess control field."""
    baseline = field.min_tau()
    active = sorted(key for key, tau in field.values.items() if tau > baseline)
    if len(active) < 2:
        return DeltaTauField(slice=field.slice, values=dict(field.values))
    excesses = [field.values[key] - baseline for key in active]
    rng = random.Random(seed)
    rng.shuffle(excesses)
    values = dict(field.values)
    for key, excess in zip(active, excesses):
        values[key] = baseline + excess
    return DeltaTauField(slice=field.slice, values=values)


def neutral_seed_catalog(
    slice_: SpatialSlice,
    baseline: int = DEFAULT_BASELINE,
    excess: int = DEFAULT_EXCESS,
) -> tuple[tuple[str, DeltaTauField], ...]:
    """Neutral deterministic seeds for Stage 4D catalog diagnostics."""
    center = (
        slice_.bounds.max_N_a // 2,
        slice_.bounds.max_N_b // 2,
        slice_.bounds.max_N_c // 2,
    )
    seeds: list[tuple[str, DeltaTauField]] = [
        (
            "single_excess",
            single_peak_field(slice_, center, baseline, excess),
        ),
        (
            "plus_cross",
            plus_cross_field(slice_, center, baseline, excess, max(1, excess // 2)),
        ),
        (
            "ring_shell",
            ring_shell_field(slice_, center, baseline, max(1, excess // 2)),
        ),
    ]
    if slice_.bounds.contains_spatial_counts(0, 0, 0):
        try:
            seeds.append(
                (
                    "compact_2x2",
                    compact_square_field(
                        slice_,
                        lower_corner=(0, 0, 0),
                        baseline_tau=baseline,
                        block_excess_tau=excess,
                        size_N_a=2,
                        size_N_b=2,
                        size_N_c=1,
                    ),
                )
            )
        except ValueError:
            pass
    peak = single_peak_field(slice_, center, baseline, excess)
    seeds.append(
        (
            "deterministic_shuffled_control",
            deterministic_shuffled_field(peak, seed=7),
        )
    )
    return tuple(seeds)


def _total_tau(field: DeltaTauField) -> int:
    return sum(field.values.values())


def _max_local_tau_change(
    before: DeltaTauField,
    after: DeltaTauField,
) -> int:
    keys = set(before.values) | set(after.values)
    return max(abs(after.values.get(k, 0) - before.values.get(k, 0)) for k in keys)


def _propagation_radius(field: DeltaTauField, baseline: int) -> float:
    structure = packet_structure_from_field(field)
    centroid = active_center_of_excess_tau(structure, baseline)
    if centroid is None:
        return 0.0
    cx, cy, cz = centroid
    center = TemporalPacket(
        N_a=int(round(cx)), N_b=int(round(cy)), N_c=int(round(cz)), N_t=field.slice.N_t
    )
    active = [k for k, tau in field.values.items() if tau > baseline]
    if not active:
        return 0.0
    return max(
        float(
            emergent_manhattan_distance(
                center,
                TemporalPacket(N_a=k[0], N_b=k[1], N_c=k[2], N_t=field.slice.N_t),
            )
        )
        for k in active
    )


def _oscillation_indicator(history: tuple[DeltaTauField, ...]) -> float:
    if len(history) < 3:
        return 0.0
    totals = [_total_tau(f) for f in history]
    if all(t == totals[0] for t in totals):
        diffs = []
        for i in range(1, len(history)):
            keys = set(history[i - 1].values) | set(history[i].values)
            diffs.append(
                sum(abs(history[i].values.get(k, 0) - history[i - 1].values.get(k, 0)) for k in keys)
            )
        sign_changes = sum(
            1
            for i in range(1, len(diffs))
            if diffs[i] < diffs[i - 1] and diffs[i - 1] > 0
        )
        return sign_changes / max(len(diffs) - 1, 1)
    return 0.0


def compute_action_diagnostics(
    action: TemporalAction,
    initial_field: DeltaTauField,
    steps: int,
) -> dict[str, Any]:
    """Run Action and collect Stage 4D diagnostics."""
    history = run_action_steps(action, initial_field, steps)
    final = history[-1]
    baseline = initial_field.min_tau()
    initial_structure = packet_structure_from_field(initial_field)
    final_structure = packet_structure_from_field(final)

    initial_centroid = active_center_of_excess_tau(initial_structure, baseline)
    final_centroid = active_center_of_excess_tau(final_structure, baseline)
    if initial_centroid and final_centroid:
        centroid_drift = sum(abs(a - b) for a, b in zip(initial_centroid, final_centroid))
    else:
        centroid_drift = 0.0

    max_step_change = max(
        (_max_local_tau_change(history[i - 1], history[i]) for i in range(1, len(history))),
        default=0,
    )
    support_sizes = [
        active_support_size_above_baseline(packet_structure_from_field(f), baseline)
        for f in history
    ]

    unchanged_history = all(
        dict(history[i - 1].values) == dict(history[i].values) for i in range(1, len(history))
    )

    return {
        "action_id": action.action_id,
        "steps": steps,
        "total_tau_before": _total_tau(initial_field),
        "total_tau_after": _total_tau(final),
        "total_tau_change": _total_tau(final) - _total_tau(initial_field),
        "max_local_tau_change_per_step": max_step_change,
        "support_size_over_time": support_sizes,
        "final_support_size": support_sizes[-1],
        "centroid_drift": centroid_drift,
        "localization_ratio": active_localization_ratio(final_structure, baseline),
        "propagation_radius": _propagation_radius(final, baseline),
        "oscillation_indicator": _oscillation_indicator(history),
        "unchanged_history": unchanged_history,
        "uses_global_anchor": action.uses_global_anchor,
        "is_trivial_control": action.action_id == "A0_identity_control",
    }


def run_boundary_checks(actions: tuple[TemporalAction, ...]) -> dict[str, Any]:
    """Validate all Actions against Stage 4D scientific boundaries."""
    per_action: list[dict[str, Any]] = []
    all_pass = True
    for action in actions:
        violations = validate_action_boundary(action)
        if action.is_legacy and "anchor_counts" in action.allowed_ingredients:
            if not action.legacy_warning:
                violations.append("legacy cohesion missing warning")
        if violations:
            all_pass = False
        per_action.append(
            {
                "action_id": action.action_id,
                "passed": len(violations) == 0,
                "violations": violations,
                "uses_global_anchor": action.uses_global_anchor,
                "is_legacy": action.is_legacy,
            }
        )
    non_legacy_with_anchor = [
        a.action_id for a in actions if a.uses_global_anchor and not a.is_legacy
    ]
    if non_legacy_with_anchor:
        all_pass = False
    return {
        "passed": all_pass,
        "per_action": per_action,
        "non_legacy_anchor_violations": non_legacy_with_anchor,
    }


def run_conservation_checks(
    actions: tuple[TemporalAction, ...],
    slice_: SpatialSlice,
) -> list[dict[str, Any]]:
    """Check total tau conservation for catalog Actions on a neutral seed."""
    seeds = neutral_seed_catalog(slice_)
    field = seeds[0][1]
    results: list[dict[str, Any]] = []
    for action in actions:
        if action.action_id == "A0_identity_control":
            continue
        diag = compute_action_diagnostics(action, field, steps=3)
        conserved = diag["total_tau_change"] == 0
        results.append(
            {
                "action_id": action.action_id,
                "conserved_total_tau": conserved,
                "total_tau_change": diag["total_tau_change"],
                "marked_non_conserved": "total_tau" not in action.conserved_quantities,
            }
        )
    return results


def run_stage4d_catalog_diagnostics(
    actions: tuple[TemporalAction, ...] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run full seed x action diagnostic matrix."""
    catalog = actions or minimal_action_catalog()
    slice_ = make_slice()
    seeds = neutral_seed_catalog(slice_)
    diagnostics: list[dict[str, Any]] = []
    for seed_label, field in seeds:
        for action in catalog:
            if action.is_legacy:
                continue
            for steps in BENCHMARK_STEPS:
                diag = compute_action_diagnostics(action, field, steps)
                diag["seed_label"] = seed_label
                diagnostics.append(diag)
    summary: dict[str, Any] = {
        "primary_actions": [a.action_id for a in catalog if not a.is_legacy],
        "legacy_excluded_from_benchmark": [
            a.action_id for a in catalog if a.is_legacy
        ],
        "run_count": len(diagnostics),
    }
    return diagnostics, summary


def determine_stage4d_verdict(
    boundary_results: dict[str, Any],
    diagnostics: list[dict[str, Any]],
    catalog_complete: bool,
) -> str:
    if not boundary_results.get("passed", False):
        return VERDICT_BOUNDARY_FAIL
    if not catalog_complete:
        return VERDICT_INCOMPLETE
    if not diagnostics:
        return VERDICT_INCOMPLETE
    return VERDICT_READY


def run_stage4d_minimal_action_catalog() -> dict[str, Any]:
    """Build deterministic Stage 4D summary JSON."""
    actions = minimal_action_catalog()
    boundary_results = run_boundary_checks(actions)
    conservation_results = run_conservation_checks(actions, make_slice())
    diagnostics, diag_summary = run_stage4d_catalog_diagnostics(actions)

    legacy_status = [
        {
            "action_id": a.action_id,
            "included_in_primary_catalog": False,
            "legacy_warning": a.legacy_warning,
            "stage4c_verdict_reference": "FRAGILE_TOY_ARTIFACT",
            "note": "Not a preferred physical candidate; arbitrary retention heuristic only.",
        }
        for a in actions
        if a.is_legacy
    ]

    catalog_complete = len([a for a in actions if not a.is_legacy]) >= 5
    verdict = determine_stage4d_verdict(boundary_results, diagnostics, catalog_complete)

    return {
        "stage": STAGE,
        "statement": (
            "Stage 4D integrates Stage 4C negative/fragility results and defines a minimal "
            "temporal Action catalog with diagnostics only; not particles or electrons."
        ),
        "merged_stage4c_reference": MERGED_STAGE4C_REFERENCE,
        "action_catalog": [a.to_metadata_dict() for a in actions],
        "action_diagnostics": diagnostics,
        "diagnostics_summary": diag_summary,
        "conservation_results": conservation_results,
        "boundary_check_results": boundary_results,
        "legacy_rule_status": legacy_status,
        "roadmap_correction": ROADMAP_CORRECTION,
        "verdict": verdict,
        "limitations": [
            "Catalog and diagnostics only; no stable candidate search.",
            "Tiny 3x3 grid benchmark; not calibrated physics.",
            "Legacy cohesion retained for audit continuity, not promotion.",
        ],
        "non_claims": list(NON_CLAIMS),
        "next_recommended_stage": (
            "Stage 4 Emergent Structure Survey using primary Actions A0–A4 only; "
            "do not tune legacy cohesion for positive structure outcomes."
        ),
    }
