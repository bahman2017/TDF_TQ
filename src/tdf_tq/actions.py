"""Stage 3C deterministic Action abstraction for toy temporal evolution rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from tdf_tq.dynamics import (
    FieldEvolutionConfig,
    conservative_pairwise_relaxation_step,
    identity_step,
    spatial_edges,
)
from tdf_tq.fields import DeltaTauField
from tdf_tq.gravity_proxy import laplacian_proxy
from tdf_tq.packets import TemporalPacket
from tdf_tq.space import SpatialSlice


@dataclass(frozen=True)
class ActionSpec:
    """Metadata for a toy Action derived from TDF temporal primitives."""

    action_id: str
    description: str
    allowed_ingredients: tuple[str, ...]
    forbidden_encoded_physics: tuple[str, ...]
    parameters: dict[str, Any]
    conservation_notes: str
    boundary_notes: str
    maturity_level: str = "C"


@dataclass
class ActionEvolutionState:
    """Optional per-run state for memory-dependent Actions."""

    previous_field: DeltaTauField | None = None


class Action(Protocol):
    """Deterministic Action operating on DeltaTauField primitives."""

    spec: ActionSpec

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField: ...


def _spatial_positions(slice_: SpatialSlice) -> tuple[tuple[int, int, int], ...]:
    positions: list[tuple[int, int, int]] = []
    for n_a in range(slice_.bounds.max_N_a + 1):
        for n_b in range(slice_.bounds.max_N_b + 1):
            for n_c in range(slice_.bounds.max_N_c + 1):
                positions.append((n_a, n_b, n_c))
    return tuple(positions)


@dataclass(frozen=True)
class IdentityControlAction:
    """A0: no update; trivial-stability control only."""

    spec: ActionSpec = field(
        default_factory=lambda: ActionSpec(
            action_id="A0_identity_control",
            description="No field update; trivial-stability control only.",
            allowed_ingredients=("DeltaTauField", "SpatialSlice"),
            forbidden_encoded_physics=(
                "particles",
                "force",
                "gravity",
                "charge",
                "spin",
                "QM amplitudes",
            ),
            parameters={},
            conservation_notes="Total tau unchanged by construction.",
            boundary_notes="Must never be interpreted as structure evidence.",
            maturity_level="C",
        )
    )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        return identity_step(field)


@dataclass(frozen=True)
class PairwiseRelaxationAction:
    """A1: conservative pairwise relaxation (local smoothing)."""

    config: FieldEvolutionConfig = field(default_factory=FieldEvolutionConfig)
    spec: ActionSpec = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "spec",
            ActionSpec(
                action_id="A1_pairwise_relaxation",
                description="Local conservative pairwise tau smoothing on count lattice.",
                allowed_ingredients=(
                    "DeltaTauField",
                    "spatial edges",
                    "threshold transfer",
                ),
                forbidden_encoded_physics=(
                    "Newtonian gravity",
                    "Einstein equations",
                    "charge",
                    "mass",
                    "QM",
                ),
                parameters={
                    "threshold": self.config.threshold,
                    "max_transfer_per_edge": self.config.max_transfer_per_edge,
                },
                conservation_notes="Total tau conserved exactly per step.",
                boundary_notes="Expected spreading/smoothing; not physical diffusion.",
                maturity_level="C",
            ),
        )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        return conservative_pairwise_relaxation_step(field, self.config)


@dataclass(frozen=True)
class ThresholdRelaxationAction:
    """A2: threshold-gated relaxation."""

    config: FieldEvolutionConfig = field(
        default_factory=lambda: FieldEvolutionConfig(threshold=4, max_transfer_per_edge=1)
    )
    spec: ActionSpec = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "spec",
            ActionSpec(
                action_id="A2_threshold_relaxation",
                description="Pairwise relaxation active only above a tau mismatch threshold.",
                allowed_ingredients=(
                    "DeltaTauField",
                    "threshold gate",
                    "spatial edges",
                ),
                forbidden_encoded_physics=(
                    "particles",
                    "gravity",
                    "force laws",
                    "QM",
                ),
                parameters={
                    "threshold": self.config.threshold,
                    "max_transfer_per_edge": self.config.max_transfer_per_edge,
                },
                conservation_notes="Total tau conserved when transfers occur.",
                boundary_notes="Tests finite mismatch threshold effects only.",
                maturity_level="C",
            ),
        )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        return conservative_pairwise_relaxation_step(field, self.config)


@dataclass(frozen=True)
class MemoryWeightedRelaxationAction:
    """A3: relaxation with one-step deterministic memory term."""

    config: FieldEvolutionConfig = field(default_factory=FieldEvolutionConfig)
    memory_weight: int = 1
    spec: ActionSpec = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "spec",
            ActionSpec(
                action_id="A3_memory_weighted_relaxation",
                description="Pairwise relaxation using current tau plus previous-step memory.",
                allowed_ingredients=(
                    "DeltaTauField",
                    "one-step memory",
                    "spatial edges",
                ),
                forbidden_encoded_physics=(
                    "particle memory",
                    "QM state vector",
                    "hbar",
                    "mass",
                ),
                parameters={
                    "threshold": self.config.threshold,
                    "max_transfer_per_edge": self.config.max_transfer_per_edge,
                    "memory_weight": self.memory_weight,
                },
                conservation_notes="Total tau conserved; memory affects transfer direction only.",
                boundary_notes="Generic memory term, not tuned for particle creation.",
                maturity_level="C",
            ),
        )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        working: dict[tuple[int, int, int], int] = dict(field.values)
        prev = (
            dict(state.previous_field.values)
            if state is not None and state.previous_field is not None
            else dict(field.values)
        )

        for a, b in spatial_edges(field.slice):
            mem_a = self.memory_weight * (working[a] - prev.get(a, working[a]))
            mem_b = self.memory_weight * (working[b] - prev.get(b, working[b]))
            eff_a = working[a] + mem_a
            eff_b = working[b] + mem_b
            diff = eff_a - eff_b
            if diff >= self.config.threshold:
                transfer = min(self.config.max_transfer_per_edge, diff)
                working[a] -= transfer
                working[b] += transfer
            elif -diff >= self.config.threshold:
                transfer = min(self.config.max_transfer_per_edge, -diff)
                working[a] += transfer
                working[b] -= transfer

        return DeltaTauField(slice=field.slice, values=working)


@dataclass(frozen=True)
class FinitePropagationDelayAction:
    """A4: at most one unit-neighbor transfer per step (toy speed limit)."""

    config: FieldEvolutionConfig = field(default_factory=FieldEvolutionConfig)
    spec: ActionSpec = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "spec",
            ActionSpec(
                action_id="A4_finite_propagation_delay",
                description="At most one spatial-neighbor transfer per step; toy c = l_q / t_q limit.",
                allowed_ingredients=(
                    "DeltaTauField",
                    "unit-neighbor edges",
                    "single transfer cap",
                ),
                forbidden_encoded_physics=(
                    "relativity equations",
                    "Lorentz transforms",
                    "photon",
                    "light cone physics",
                ),
                parameters={
                    "threshold": self.config.threshold,
                    "max_transfer_per_edge": self.config.max_transfer_per_edge,
                    "max_transfers_per_step": 1,
                },
                conservation_notes="Total tau conserved when a transfer occurs.",
                boundary_notes="Toy finite-speed scaffold only; not GR or SR.",
                maturity_level="C",
            ),
        )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        working: dict[tuple[int, int, int], int] = dict(field.values)
        for a, b in spatial_edges(field.slice):
            tau_a = working[a]
            tau_b = working[b]
            diff = tau_a - tau_b
            if diff >= self.config.threshold:
                transfer = min(self.config.max_transfer_per_edge, diff)
                working[a] = tau_a - transfer
                working[b] = tau_b + transfer
                return DeltaTauField(slice=field.slice, values=working)
            if -diff >= self.config.threshold:
                transfer = min(self.config.max_transfer_per_edge, -diff)
                working[a] = tau_a + transfer
                working[b] = tau_b - transfer
                return DeltaTauField(slice=field.slice, values=working)
        return DeltaTauField(slice=field.slice, values=working)


@dataclass(frozen=True)
class LocalCurvaturePressureAction:
    """A5: discrete Laplacian pressure proxy smoothing."""

    config: FieldEvolutionConfig = field(default_factory=FieldEvolutionConfig)
    spec: ActionSpec = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "spec",
            ActionSpec(
                action_id="A5_local_curvature_pressure",
                description="Conservative transfers driven by discrete Laplacian roughness proxy.",
                allowed_ingredients=(
                    "DeltaTauField",
                    "discrete Laplacian proxy",
                    "neighbor differences",
                ),
                forbidden_encoded_physics=(
                    "Einstein equations",
                    "Newtonian gravity",
                    "physical curvature",
                    "force laws",
                ),
                parameters={
                    "threshold": self.config.threshold,
                    "max_transfer_per_edge": self.config.max_transfer_per_edge,
                },
                conservation_notes="Total tau conserved per accepted transfer.",
                boundary_notes="Curvature-like diagnostic only; not GR recovery.",
                maturity_level="C",
            ),
        )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        working: dict[tuple[int, int, int], int] = dict(field.values)
        for site in _spatial_positions(field.slice):
            temp_field = DeltaTauField(slice=field.slice, values=dict(working))
            lap = laplacian_proxy(temp_field, site)
            if abs(lap) < self.config.threshold:
                continue
            center_packet = TemporalPacket(
                N_a=site[0], N_b=site[1], N_c=site[2], N_t=field.slice.N_t
            )
            neighbors = field.slice.neighbors_within_bounds(center_packet)
            if not neighbors:
                continue
            if lap > 0:
                target = min(
                    neighbors,
                    key=lambda p: working[(p.N_a, p.N_b, p.N_c)],
                )
                transfer = min(
                    self.config.max_transfer_per_edge,
                    int(lap),
                    working[site],
                )
                if transfer <= 0:
                    continue
                dst = (target.N_a, target.N_b, target.N_c)
                working[site] -= transfer
                working[dst] += transfer
            else:
                source = max(
                    neighbors,
                    key=lambda p: working[(p.N_a, p.N_b, p.N_c)],
                )
                transfer = min(
                    self.config.max_transfer_per_edge,
                    int(-lap),
                    working[(source.N_a, source.N_b, source.N_c)] - field.min_tau(),
                )
                if transfer <= 0:
                    continue
                src = (source.N_a, source.N_b, source.N_c)
                working[src] -= transfer
                working[site] += transfer
            return DeltaTauField(slice=field.slice, values=working)
        return DeltaTauField(slice=field.slice, values=working)


@dataclass(frozen=True)
class PhaseCoherenceProbeAction:
    """A6: identity evolution with phase-coherence diagnostics only."""

    spec: ActionSpec = field(
        default_factory=lambda: ActionSpec(
            action_id="A6_phase_coherence_probe",
            description="No field update; phase-coherence diagnostics from tau differences only.",
            allowed_ingredients=(
                "DeltaTauField",
                "bounded phase-coherence proxy",
            ),
            forbidden_encoded_physics=(
                "Schrödinger equation",
                "wavefunction postulate",
                "QM derivation",
                "hbar",
                "complex probability amplitudes as physics",
            ),
            parameters={"evolution": "identity"},
            conservation_notes="Field unchanged; total tau conserved.",
            boundary_notes="QM-like exploratory proxy only; not QM recovery.",
            maturity_level="C",
        )
    )

    def step(
        self,
        field: DeltaTauField,
        *,
        state: ActionEvolutionState | None = None,
    ) -> DeltaTauField:
        return identity_step(field)


def run_action_steps(
    action: Action,
    initial_field: DeltaTauField,
    steps: int,
) -> tuple[DeltaTauField, ...]:
    """Run deterministic Action evolution; index 0 is the initial field."""
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 0:
        raise ValueError("steps must be a non-negative integer")
    history: list[DeltaTauField] = [initial_field]
    state = ActionEvolutionState()
    current = initial_field
    for _ in range(steps):
        current = action.step(current, state=state)
        state.previous_field = history[-1]
        history.append(current)
    return tuple(history)


def default_action_catalog() -> tuple[Action, ...]:
    """Return the Stage 3C conservative Action catalog in deterministic order."""
    return (
        IdentityControlAction(),
        PairwiseRelaxationAction(),
        ThresholdRelaxationAction(),
        MemoryWeightedRelaxationAction(),
        FinitePropagationDelayAction(),
        LocalCurvaturePressureAction(),
        PhaseCoherenceProbeAction(),
    )
