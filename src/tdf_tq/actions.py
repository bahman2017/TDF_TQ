"""Stage 4D minimal temporal Action abstraction.

Toy Actions derived from TDF primitives only—not particles, forces, or validated physics.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from tdf_tq.dynamics import (
    FieldEvolutionConfig,
    conservative_centered_cohesion_step,
    conservative_pairwise_relaxation_step,
    identity_step,
    spatial_edges,
)
from tdf_tq.fields import DeltaTauField
from tdf_tq.robustness import anchor_counts_from_field

DEFAULT_CONFIG = FieldEvolutionConfig(threshold=2, max_transfer_per_edge=1)

FORBIDDEN_INGREDIENT_TOKENS: frozenset[str] = frozenset(
    {
        "electron",
        "photon",
        "positron",
        "particle_identity",
        "charge",
        "spin",
        "mass",
        "gravity",
        "qm_amplitude",
        "hand_built_stable_object",
        "force_carrier",
    }
)


@dataclass
class ActionEvolutionState:
    """Per-run state for memory- or inertia-dependent Actions."""

    previous_field: DeltaTauField | None = None


ActionStepFn = Callable[[DeltaTauField, ActionEvolutionState | None], DeltaTauField]


@dataclass(frozen=True)
class TemporalAction:
    """Metadata and step binding for a minimal temporal Action."""

    action_id: str
    label: str
    allowed_ingredients: tuple[str, ...]
    conserved_quantities: tuple[str, ...]
    forbidden_ingredients: tuple[str, ...]
    update_function_name: str
    scientific_status: str
    limitations: str
    step_fn: ActionStepFn = field(repr=False, compare=False, hash=False)
    uses_global_anchor: bool = False
    is_legacy: bool = False
    legacy_warning: str = ""

    def to_metadata_dict(self) -> dict[str, Any]:
        """JSON-serializable metadata without the step callable."""
        data: dict[str, Any] = {
            "action_id": self.action_id,
            "label": self.label,
            "allowed_ingredients": list(self.allowed_ingredients),
            "conserved_quantities": list(self.conserved_quantities),
            "forbidden_ingredients": list(self.forbidden_ingredients),
            "update_function_name": self.update_function_name,
            "scientific_status": self.scientific_status,
            "limitations": self.limitations,
            "uses_global_anchor": self.uses_global_anchor,
            "is_legacy": self.is_legacy,
        }
        if self.legacy_warning:
            data["legacy_warning"] = self.legacy_warning
        return data


def _identity_step(
    field: DeltaTauField,
    state: ActionEvolutionState | None = None,
) -> DeltaTauField:
    return identity_step(field)


def _pairwise_relaxation_step(
    field: DeltaTauField,
    state: ActionEvolutionState | None = None,
    config: FieldEvolutionConfig = DEFAULT_CONFIG,
) -> DeltaTauField:
    return conservative_pairwise_relaxation_step(field, config)


def _thresholded_relaxation_memory_step(
    field: DeltaTauField,
    state: ActionEvolutionState | None = None,
    config: FieldEvolutionConfig = DEFAULT_CONFIG,
    memory_weight: int = 1,
) -> DeltaTauField:
    """Local relaxation with one-step memory; conserves total tau."""
    working: dict[tuple[int, int, int], int] = dict(field.values)
    prev = (
        dict(state.previous_field.values)
        if state is not None and state.previous_field is not None
        else dict(field.values)
    )
    for a, b in spatial_edges(field.slice):
        mem_a = memory_weight * (working[a] - prev.get(a, working[a]))
        mem_b = memory_weight * (working[b] - prev.get(b, working[b]))
        eff_a = working[a] + mem_a
        eff_b = working[b] + mem_b
        diff = eff_a - eff_b
        if diff >= config.threshold:
            transfer = min(config.max_transfer_per_edge, diff)
            working[a] -= transfer
            working[b] += transfer
        elif -diff >= config.threshold:
            transfer = min(config.max_transfer_per_edge, -diff)
            working[a] += transfer
            working[b] -= transfer
    return DeltaTauField(slice=field.slice, values=working)


def _local_temporal_inertia_step(
    field: DeltaTauField,
    state: ActionEvolutionState | None = None,
    config: FieldEvolutionConfig = DEFAULT_CONFIG,
) -> DeltaTauField:
    """Resist rapid local tau changes using previous state; no anchor."""
    prev = (
        state.previous_field
        if state is not None and state.previous_field is not None
        else field
    )
    prev_values = dict(prev.values)
    working: dict[tuple[int, int, int], int] = dict(field.values)
    for a, b in spatial_edges(field.slice):
        inertia_a = abs(working[a] - prev_values.get(a, working[a]))
        inertia_b = abs(working[b] - prev_values.get(b, working[b]))
        effective_threshold = config.threshold + inertia_a + inertia_b
        tau_a = working[a]
        tau_b = working[b]
        diff = tau_a - tau_b
        if diff >= effective_threshold:
            transfer = min(config.max_transfer_per_edge, diff)
            working[a] = tau_a - transfer
            working[b] = tau_b + transfer
        elif -diff >= effective_threshold:
            transfer = min(config.max_transfer_per_edge, -diff)
            working[a] = tau_a + transfer
            working[b] = tau_b - transfer
    return DeltaTauField(slice=field.slice, values=working)


def _finite_propagation_limited_diffusion_step(
    field: DeltaTauField,
    state: ActionEvolutionState | None = None,
    config: FieldEvolutionConfig = DEFAULT_CONFIG,
) -> DeltaTauField:
    """At most one unit-neighbor transfer per step; toy finite-speed diffusion."""
    working: dict[tuple[int, int, int], int] = dict(field.values)
    for a, b in spatial_edges(field.slice):
        tau_a = working[a]
        tau_b = working[b]
        diff = tau_a - tau_b
        if diff >= config.threshold:
            transfer = min(config.max_transfer_per_edge, diff)
            working[a] = tau_a - transfer
            working[b] = tau_b + transfer
            return DeltaTauField(slice=field.slice, values=working)
        if -diff >= config.threshold:
            transfer = min(config.max_transfer_per_edge, -diff)
            working[a] = tau_a + transfer
            working[b] = tau_b - transfer
            return DeltaTauField(slice=field.slice, values=working)
    return DeltaTauField(slice=field.slice, values=working)


def _legacy_cohesion_step(
    field: DeltaTauField,
    state: ActionEvolutionState | None = None,
    config: FieldEvolutionConfig = DEFAULT_CONFIG,
) -> DeltaTauField:
    anchor = anchor_counts_from_field(field)
    return conservative_centered_cohesion_step(field, anchor, config)


def run_action_steps(
    action: TemporalAction,
    initial_field: DeltaTauField,
    steps: int,
) -> tuple[DeltaTauField, ...]:
    """Deterministic Action evolution; index 0 is initial field."""
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 0:
        raise ValueError("steps must be a non-negative integer")
    history: list[DeltaTauField] = [initial_field]
    state = ActionEvolutionState()
    current = initial_field
    for _ in range(steps):
        current = action.step_fn(current, state)
        state.previous_field = history[-1]
        history.append(current)
    return tuple(history)


def minimal_action_catalog(
    config: FieldEvolutionConfig = DEFAULT_CONFIG,
) -> tuple[TemporalAction, ...]:
    """Stage 4D minimal catalog plus legacy cohesion warning entry."""
    return (
        TemporalAction(
            action_id="A0_identity_control",
            label="Identity control",
            allowed_ingredients=("local_tau", "DeltaTauField"),
            conserved_quantities=("total_tau",),
            forbidden_ingredients=("target_center", "particle_identity", "attraction"),
            update_function_name="identity_step",
            scientific_status="trivial_control",
            limitations="No update; must never be interpreted as structure evidence.",
            step_fn=_identity_step,
        ),
        TemporalAction(
            action_id="A1_pairwise_relaxation",
            label="Pairwise relaxation",
            allowed_ingredients=(
                "local_tau",
                "Delta_tau",
                "nearest_neighbor_relations",
                "integer_conservation",
            ),
            conserved_quantities=("total_tau",),
            forbidden_ingredients=("target_center", "particle_identity", "gravity", "charge"),
            update_function_name="conservative_pairwise_relaxation_step",
            scientific_status="spreading_smoothing_baseline",
            limitations="Toy local smoothing only; expected spreading, not binding.",
            step_fn=lambda f, s=None: _pairwise_relaxation_step(f, s, config),
        ),
        TemporalAction(
            action_id="A2_thresholded_relaxation_memory",
            label="Thresholded relaxation with memory",
            allowed_ingredients=(
                "local_tau",
                "Delta_tau",
                "nearest_neighbor_relations",
                "one_step_temporal_memory",
                "integer_conservation",
            ),
            conserved_quantities=("total_tau",),
            forbidden_ingredients=("target_center", "particle_identity", "attraction"),
            update_function_name="thresholded_relaxation_memory_step",
            scientific_status="memory_weighted_smoothing",
            limitations="Generic one-step memory; not tuned for particle creation.",
            step_fn=lambda f, s=None: _thresholded_relaxation_memory_step(f, s, config),
        ),
        TemporalAction(
            action_id="A3_local_temporal_inertia",
            label="Local temporal inertia",
            allowed_ingredients=(
                "local_tau",
                "Delta_tau",
                "nearest_neighbor_relations",
                "one_step_temporal_memory",
                "integer_conservation",
            ),
            conserved_quantities=("total_tau",),
            forbidden_ingredients=(
                "target_center",
                "global_anchor",
                "center_seeking",
                "particle_identity",
            ),
            update_function_name="local_temporal_inertia_step",
            scientific_status="inertia_damped_smoothing",
            limitations="Resists rapid local change; no object retention anchor.",
            step_fn=lambda f, s=None: _local_temporal_inertia_step(f, s, config),
        ),
        TemporalAction(
            action_id="A4_finite_propagation_limited_diffusion",
            label="Finite-propagation limited diffusion",
            allowed_ingredients=(
                "local_tau",
                "Delta_tau",
                "nearest_neighbor_relations",
                "finite_propagation",
                "integer_conservation",
            ),
            conserved_quantities=("total_tau",),
            forbidden_ingredients=("global_information", "target_center", "particle_identity"),
            update_function_name="finite_propagation_limited_diffusion_step",
            scientific_status="finite_speed_diffusion_toy",
            limitations="Max one neighbor transfer per step; toy c = l_q / t_q scaffold.",
            step_fn=lambda f, s=None: _finite_propagation_limited_diffusion_step(f, s, config),
        ),
        TemporalAction(
            action_id="LEGACY_conservative_centered_cohesion",
            label="Legacy centered cohesion (Stage 4B/4C)",
            allowed_ingredients=("local_tau", "nearest_neighbor_relations", "anchor_counts"),
            conserved_quantities=("total_tau",),
            forbidden_ingredients=("target_center", "particle_identity", "charge", "spin", "mass"),
            update_function_name="conservative_centered_cohesion_step",
            scientific_status="legacy_arbitrary_retention",
            limitations="Arbitrary retention heuristic; not physical binding.",
            uses_global_anchor=True,
            is_legacy=True,
            legacy_warning=(
                "Arbitrary retention heuristic from Stage 4B/4C; not physical binding. "
                "Stage 4C verdict FRAGILE_TOY_ARTIFACT."
            ),
            step_fn=lambda f, s=None: _legacy_cohesion_step(f, s, config),
        ),
    )


def validate_action_boundary(action: TemporalAction) -> list[str]:
    """Return boundary violation messages for an Action metadata record."""
    violations: list[str] = []
    searchable = " ".join(
        [
            action.action_id,
            action.label,
            action.scientific_status,
            action.limitations,
            action.legacy_warning,
        ]
    ).lower()
    claim_tokens = ("electron discovered", "photon discovered", "mass derived", "charge derived", "spin derived")
    for phrase in claim_tokens:
        if phrase in searchable:
            violations.append(f"overclaim phrase: {phrase}")
    for token in ("electron", "photon", "positron"):
        if token in searchable and "legacy" not in action.action_id.lower():
            if token in action.label.lower() or token in action.scientific_status.lower():
                violations.append(f"forbidden label token: {token}")
    if action.uses_global_anchor and not action.is_legacy:
        violations.append("non-legacy action uses global anchor")
    if action.is_legacy and not action.legacy_warning:
        violations.append("legacy action missing legacy_warning")
    required_forbidden = {"target_center", "particle_identity"}
    if action.uses_global_anchor and "anchor" in " ".join(action.allowed_ingredients):
        if "target_center" not in action.forbidden_ingredients:
            violations.append("anchor action must forbid target_center")
    for req in required_forbidden:
        if req not in action.forbidden_ingredients and not action.is_legacy:
            if action.action_id != "A0_identity_control":
                pass
    return violations
