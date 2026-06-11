"""Stage 3C Action catalog benchmark and discovery summary."""

from __future__ import annotations

import random
from typing import Any

from tdf_tq.action_metrics import METRIC_DEFINITIONS, compute_action_metrics
from tdf_tq.actions import Action, default_action_catalog, run_action_steps
from tdf_tq.fields import DeltaTauField
from tdf_tq.neighborhoods import spatial_unit_neighbors
from tdf_tq.packets import TemporalPacket
from tdf_tq.patterns import compact_square_field, plus_cross_field, single_peak_field
from tdf_tq.space import SpatialBounds, SpatialSlice

STAGE = "3C"
BRANCH = "feature/stage3c-fundamental-tdf-action-discovery"

VERDICT_PASS = "PASS_ACTION_CATALOG_READY"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE_ACTION_BEHAVIOR"
VERDICT_FAIL = "FAIL"

CLASS_TRIVIAL_CONTROL = "TRIVIAL_CONTROL"
CLASS_SPREADING = "SPREADING_SMOOTHING"
CLASS_LOCALIZED = "LOCALIZED_PERSISTENT_TOY_PATTERN"
CLASS_PROPAGATING = "PROPAGATING_TOY_PATTERN"
CLASS_OSCILLATORY = "OSCILLATORY_TOY_PATTERN"
CLASS_CONSERVED = "CONSERVED_QUANTITY_CANDIDATE"
CLASS_FINITE_SPEED_CLEAN = "FINITE_SPEED_CLEAN"
CLASS_FINITE_SPEED_VIOLATION = "FINITE_SPEED_VIOLATION"
CLASS_INCONCLUSIVE = "INCONCLUSIVE"
CLASS_FAIL = "FAIL"

GRID_SIZES: tuple[tuple[str, int, int, int], ...] = (
    ("3x3x1", 2, 2, 0),
    ("5x5x1", 4, 4, 0),
)

STEP_COUNTS: tuple[int, ...] = (0, 1, 2, 3, 5, 8, 13)

DEFAULT_BASELINE_TAU = 10
DEFAULT_EXCESS_TAU = 10

LOCKED_DEFINITIONS_CHECKED: tuple[str, ...] = (
    "t_q fundamental time quantum",
    "tau = N_t",
    "Delta tau = Delta N_t",
    "larger N_t means slower local passage of time",
    "spatial distance emergent not fundamental",
    "c = l_q / t_q working speed limit",
    "Delta tau does not automatically mean matter",
)

EXPLICIT_NON_CLAIMS: tuple[str, ...] = (
    "No GR derivation.",
    "No QM derivation.",
    "No particle, electron, photon, positron, mass, charge, spin, energy, hbar, or alpha derivation.",
    "No empirical validation or peer-reviewed physics claim.",
    "Metrics are toy diagnostics only—not real energy, curvature, mass, gravity, or quantum phase.",
)

OVERCLAIM_PHRASES: tuple[str, ...] = (
    "derived GR",
    "derived QM",
    "electron discovered",
    "photon discovered",
    "mass derived",
    "charge derived",
    "spin derived",
    "validated physics",
)


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


def _baseline_values(slice_: SpatialSlice, baseline_tau: int) -> dict[tuple[int, int, int], int]:
    return {pos: baseline_tau for pos in _spatial_positions(slice_)}


def ring_shell_field(
    slice_: SpatialSlice,
    center: tuple[int, int, int],
    baseline_tau: int,
    shell_excess_tau: int,
) -> DeltaTauField:
    """Baseline with unit-neighbor ring shell excess around center."""
    values = _baseline_values(slice_, baseline_tau)
    center_packet = TemporalPacket(
        N_a=center[0], N_b=center[1], N_c=center[2], N_t=slice_.N_t
    )
    for neighbor in spatial_unit_neighbors(center_packet):
        if slice_.bounds.contains_packet(neighbor):
            key = (neighbor.N_a, neighbor.N_b, neighbor.N_c)
            values[key] = baseline_tau + shell_excess_tau
    return DeltaTauField(slice=slice_, values=values)


def two_peak_symmetric_field(
    slice_: SpatialSlice,
    baseline_tau: int,
    peak_excess_tau: int,
) -> DeltaTauField:
    """Two symmetric peaks on opposite sides when bounds allow."""
    values = _baseline_values(slice_, baseline_tau)
    b = slice_.bounds
    peak_a = (0, b.max_N_b // 2, 0)
    peak_b = (b.max_N_a, b.max_N_b // 2, 0)
    for peak in (peak_a, peak_b):
        if slice_.bounds.contains_spatial_counts(*peak):
            values[peak] = baseline_tau + peak_excess_tau
    return DeltaTauField(slice=slice_, values=values)


def gradient_slab_field(
    slice_: SpatialSlice,
    baseline_tau: int,
    max_excess_tau: int,
) -> DeltaTauField:
    """Deterministic tau gradient along N_a."""
    values = _baseline_values(slice_, baseline_tau)
    max_a = slice_.bounds.max_N_a
    for n_a in range(max_a + 1):
        for n_b in range(slice_.bounds.max_N_b + 1):
            for n_c in range(slice_.bounds.max_N_c + 1):
                if max_a == 0:
                    excess = max_excess_tau
                else:
                    excess = (max_excess_tau * n_a) // max_a
                values[(n_a, n_b, n_c)] = baseline_tau + excess
    return DeltaTauField(slice=slice_, values=values)


def deterministic_random_field(
    slice_: SpatialSlice,
    baseline_tau: int,
    seed: int,
    max_amplitude: int,
) -> DeltaTauField:
    """Deterministic pseudo-random low/high amplitude excess field."""
    rng = random.Random(seed)
    values = {
        pos: baseline_tau + rng.randint(0, max_amplitude)
        for pos in _spatial_positions(slice_)
    }
    return DeltaTauField(slice=slice_, values=values)


def benchmark_seed_catalog(
    slice_: SpatialSlice,
    baseline_tau: int = DEFAULT_BASELINE_TAU,
    excess_tau: int = DEFAULT_EXCESS_TAU,
) -> tuple[tuple[str, DeltaTauField], ...]:
    """Deterministic benchmark seeds for Action catalog runs."""
    seeds: list[tuple[str, DeltaTauField]] = []
    center = (
        slice_.bounds.max_N_a // 2,
        slice_.bounds.max_N_b // 2,
        slice_.bounds.max_N_c // 2,
    )

    if slice_.bounds.contains_spatial_counts(*center):
        seeds.append(
            (
                "single_peak_center",
                single_peak_field(slice_, center, baseline_tau, excess_tau),
            )
        )
        seeds.append(
            (
                "plus_cross_center",
                plus_cross_field(
                    slice_, center, baseline_tau, excess_tau, max(1, excess_tau // 2)
                ),
            )
        )
        seeds.append(
            (
                "ring_shell",
                ring_shell_field(slice_, center, baseline_tau, max(1, excess_tau // 2)),
            )
        )

    if slice_.bounds.contains_spatial_counts(0, 0, 0):
        try:
            seeds.append(
                (
                    "compact_2x2_corner",
                    compact_square_field(
                        slice_,
                        lower_corner=(0, 0, 0),
                        baseline_tau=baseline_tau,
                        block_excess_tau=excess_tau,
                        size_N_a=2,
                        size_N_b=2,
                        size_N_c=1,
                    ),
                )
            )
        except ValueError:
            pass

    seeds.append(
        (
            "two_peak_symmetric",
            two_peak_symmetric_field(slice_, baseline_tau, excess_tau),
        )
    )
    seeds.append(
        (
            "gradient_slab",
            gradient_slab_field(slice_, baseline_tau, excess_tau),
        )
    )
    seeds.append(
        (
            "random_seeded_low_amplitude",
            deterministic_random_field(slice_, baseline_tau, seed=42, max_amplitude=2),
        )
    )
    seeds.append(
        (
            "random_seeded_high_amplitude",
            deterministic_random_field(slice_, baseline_tau, seed=99, max_amplitude=excess_tau),
        )
    )
    return tuple(seeds)


def classify_action_behavior(
    action_id: str,
    initial_field: DeltaTauField,
    final_field: DeltaTauField,
    history: tuple[DeltaTauField, ...],
    metrics: dict[str, Any],
) -> tuple[str, ...]:
    """Conservative multi-tag behavior classification."""
    tags: list[str] = []
    unchanged = dict(initial_field.values) == dict(final_field.values)

    if action_id == "A0_identity_control" or unchanged:
        tags.append(CLASS_TRIVIAL_CONTROL)

    if metrics["total_tau_change"] == 0:
        tags.append(CLASS_CONSERVED)

    if metrics["spreading_score"] >= 0.05 and metrics["localization_score"] < 0.8:
        tags.append(CLASS_SPREADING)

    if metrics["localization_score"] >= 0.35 and metrics["centroid_drift"] <= 1.5:
        if metrics["active_support_size"] >= 1 and not unchanged:
            tags.append(CLASS_LOCALIZED)

    if metrics["propagation_radius"] >= 1.0 and metrics["centroid_drift"] >= 0.5:
        tags.append(CLASS_PROPAGATING)

    if metrics["oscillation_score"] >= 0.25:
        tags.append(CLASS_OSCILLATORY)

    if action_id == "A4_finite_propagation_delay":
        if metrics["finite_speed_violation_count"] == 0 and not unchanged:
            tags.append(CLASS_FINITE_SPEED_CLEAN)
        elif metrics["finite_speed_violation_count"] > 0:
            tags.append(CLASS_FINITE_SPEED_VIOLATION)
    elif metrics["finite_speed_violation_count"] == 0 and len(history) > 1 and not unchanged:
        tags.append(CLASS_FINITE_SPEED_CLEAN)
    elif metrics["finite_speed_violation_count"] > 0:
        tags.append(CLASS_FINITE_SPEED_VIOLATION)

    if not tags:
        if unchanged and action_id != "A0_identity_control":
            tags.append(CLASS_INCONCLUSIVE)
        elif metrics["total_tau_change"] != 0:
            tags.append(CLASS_FAIL)
        else:
            tags.append(CLASS_INCONCLUSIVE)

    return tuple(dict.fromkeys(tags))


def _action_catalog_metadata(actions: tuple[Action, ...]) -> list[dict[str, Any]]:
    return [
        {
            "action_id": action.spec.action_id,
            "description": action.spec.description,
            "allowed_ingredients": list(action.spec.allowed_ingredients),
            "forbidden_encoded_physics": list(action.spec.forbidden_encoded_physics),
            "parameters": action.spec.parameters,
            "conservation_notes": action.spec.conservation_notes,
            "boundary_notes": action.spec.boundary_notes,
            "maturity_level": action.spec.maturity_level,
        }
        for action in actions
    ]


def run_action_catalog_benchmark(
    actions: tuple[Action, ...] | None = None,
    baseline_tau: int = DEFAULT_BASELINE_TAU,
    excess_tau: int = DEFAULT_EXCESS_TAU,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run full Action x seed x grid x steps benchmark."""
    catalog = actions or default_action_catalog()
    results: list[dict[str, Any]] = []

    for grid_name, max_a, max_b, max_c in GRID_SIZES:
        slice_ = make_slice(max_a, max_b, max_c)
        seeds = benchmark_seed_catalog(slice_, baseline_tau, excess_tau)
        for seed_label, initial_field in seeds:
            for action in catalog:
                for steps in STEP_COUNTS:
                    history = run_action_steps(action, initial_field, steps)
                    final_field = history[-1]
                    metrics = compute_action_metrics(initial_field, final_field, history)
                    tags = classify_action_behavior(
                        action.spec.action_id,
                        initial_field,
                        final_field,
                        history,
                        metrics,
                    )
                    results.append(
                        {
                            "grid": grid_name,
                            "seed_label": seed_label,
                            "action_id": action.spec.action_id,
                            "steps": steps,
                            "classifications": list(tags),
                            "metrics": metrics,
                        }
                    )

    aggregates: dict[str, Any] = {
        "by_action": {},
        "nontrivial_action_ids": [],
    }
    for action in catalog:
        action_id = action.spec.action_id
        subset = [r for r in results if r["action_id"] == action_id]
        nontrivial = [
            r
            for r in subset
            if CLASS_TRIVIAL_CONTROL not in r["classifications"]
            or len(r["classifications"]) > 1
        ]
        nontrivial_tags = {
            tag
            for r in subset
            for tag in r["classifications"]
            if tag not in (CLASS_TRIVIAL_CONTROL, CLASS_INCONCLUSIVE)
        }
        aggregates["by_action"][action_id] = {
            "run_count": len(subset),
            "nontrivial_run_count": len(nontrivial),
            "tags_observed": sorted(nontrivial_tags),
        }
        if nontrivial_tags - {CLASS_CONSERVED}:
            aggregates["nontrivial_action_ids"].append(action_id)

    return results, aggregates


def determine_stage3c_verdict(
    action_results: list[dict[str, Any]],
    aggregates: dict[str, Any],
) -> str:
    """Conservative Stage 3C verdict."""
    nontrivial_ids = aggregates.get("nontrivial_action_ids", [])
    if nontrivial_ids:
        return VERDICT_PASS
    any_change = any(
        CLASS_SPREADING in r["classifications"]
        or CLASS_LOCALIZED in r["classifications"]
        or CLASS_PROPAGATING in r["classifications"]
        for r in action_results
    )
    if any_change:
        return VERDICT_PASS
    return VERDICT_INCONCLUSIVE


def _best_action_candidates(aggregates: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for action_id, info in aggregates["by_action"].items():
        tags = set(info.get("tags_observed", []))
        if not tags:
            continue
        later_stage = "later weak-field proxy testing" if action_id in {
            "A1_pairwise_relaxation",
            "A5_local_curvature_pressure",
        } else "later QM-like exploratory tests" if action_id == "A6_phase_coherence_probe" else "later structure search"
        candidates.append(
            {
                "action_id": action_id,
                "tags_observed": sorted(tags),
                "recommended_for": later_stage,
            }
        )
    return candidates


def run_stage3c_action_discovery() -> dict[str, Any]:
    """Run Stage 3C discovery benchmark and return deterministic summary dict."""
    actions = default_action_catalog()
    action_results, aggregates = run_action_catalog_benchmark(actions)

    conserved = [
        r
        for r in action_results
        if CLASS_CONSERVED in r["classifications"] and r["metrics"]["total_tau_change"] == 0
    ]
    finite_speed = [
        {
            "action_id": r["action_id"],
            "seed_label": r["seed_label"],
            "grid": r["grid"],
            "steps": r["steps"],
            "finite_speed_violation_count": r["metrics"]["finite_speed_violation_count"],
            "classification": [
                c
                for c in r["classifications"]
                if c in (CLASS_FINITE_SPEED_CLEAN, CLASS_FINITE_SPEED_VIOLATION)
            ],
        }
        for r in action_results
        if any(
            c in r["classifications"]
            for c in (CLASS_FINITE_SPEED_CLEAN, CLASS_FINITE_SPEED_VIOLATION)
        )
    ]
    geometry = [
        {
            "action_id": r["action_id"],
            "seed_label": r["seed_label"],
            "effective_geometry_proxy": r["metrics"]["effective_geometry_proxy"],
            "discrete_laplacian_energy_proxy": r["metrics"]["discrete_laplacian_energy_proxy"],
        }
        for r in action_results
        if r["metrics"]["effective_geometry_proxy"] > 0.0 and r["steps"] >= 3
    ]
    phase = [
        {
            "action_id": r["action_id"],
            "seed_label": r["seed_label"],
            "phase_coherence_proxy": r["metrics"]["phase_coherence_proxy"],
            "oscillation_score": r["metrics"]["oscillation_score"],
            "recurrence_score": r["metrics"]["recurrence_score"],
        }
        for r in action_results
        if r["action_id"] == "A6_phase_coherence_probe" or r["metrics"]["phase_coherence_proxy"] < 0.99
    ]

    negative = [
        r
        for r in action_results
        if CLASS_FAIL in r["classifications"]
        or (CLASS_INCONCLUSIVE in r["classifications"] and len(r["classifications"]) == 1)
    ]

    verdict = determine_stage3c_verdict(action_results, aggregates)

    return {
        "stage": STAGE,
        "branch": BRANCH,
        "purpose": (
            "Discover and test minimal conservative temporal Actions from TDF primitives "
            "before particle-like or GR/QM construction; toy-model only."
        ),
        "locked_definitions_checked": list(LOCKED_DEFINITIONS_CHECKED),
        "action_catalog": _action_catalog_metadata(actions),
        "benchmark_config": {
            "grid_sizes": [{"name": g[0], "max_N_a": g[1], "max_N_b": g[2], "max_N_c": g[3]} for g in GRID_SIZES],
            "steps": list(STEP_COUNTS),
            "baseline_tau": DEFAULT_BASELINE_TAU,
            "excess_tau": DEFAULT_EXCESS_TAU,
        },
        "seed_catalog": [
            "single_peak_center",
            "compact_2x2_corner",
            "plus_cross_center",
            "ring_shell",
            "two_peak_symmetric",
            "gradient_slab",
            "random_seeded_low_amplitude",
            "random_seeded_high_amplitude",
        ],
        "metric_definitions": METRIC_DEFINITIONS,
        "action_results": action_results,
        "best_action_candidates_for_later_stages": _best_action_candidates(aggregates),
        "negative_results": {
            "count": len(negative),
            "sample": negative[:12],
        },
        "conserved_quantity_candidates": {
            "count": len(conserved),
            "actions": sorted({r["action_id"] for r in conserved}),
        },
        "finite_speed_results": finite_speed[:24],
        "effective_geometry_proxy_results": geometry[:24],
        "phase_coherence_proxy_results": phase[:24],
        "aggregates": aggregates,
        "verdict": verdict,
        "limitations": [
            "Toy Actions on tiny grids only.",
            "Metrics are diagnostics, not physical observables.",
            "Stage 4B cohesion/structure results are not re-derived here.",
            "No GR, QM, particle, mass, charge, or spin claims.",
        ],
        "explicit_non_claims": list(EXPLICIT_NON_CLAIMS),
        "next_recommended_stage": (
            "Return to Stage 4 structure exploration using Action-informed update rules, "
            "or Stage 8 weak-field proxy tests if geometry candidates persist."
        ),
    }


def scan_for_overclaim_phrases(text: str) -> list[str]:
    """Return forbidden overclaim phrases found in text (case-insensitive)."""
    lowered = text.lower()
    return [phrase for phrase in OVERCLAIM_PHRASES if phrase.lower() in lowered]
