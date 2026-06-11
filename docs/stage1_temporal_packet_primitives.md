# Stage 1 — Temporal Packet Primitives

## Purpose

Stage 1 extends the Stage 0 `TemporalPacket` scaffold with **deterministic count-level relations**: signed packet deltas, translation with non-negativity guards, spatial/temporal equality checks, and **spatial unit neighbors** on the emergent count lattice.

These primitives prepare the repository for Stage 2 (emergent space toy model) without introducing dynamics, fields, or physical calibration.

## Relation to Stage 0

| Stage 0 | Stage 1 |
|---------|---------|
| Frozen `TemporalPacket` with validation | Unchanged immutability and validation rules |
| `delta_tau`, emergent Euclidean distance | Complemented by `PacketDelta`, `packet_delta`, `translate_packet` |
| Static packets only | Adjacency on spatial counts at fixed `N_t` |

Locked definitions (`tau = N_t`, `Δτ = ΔN_t`, emergent spatial distance, `c = l_q / t_q`) are preserved. **Δτ does not automatically mean matter.**

## Definitions

### PacketDelta

A frozen dataclass of signed integer differences `(dN_a, dN_b, dN_c, dN_t)` between two packets. Properties:

- `spatial_delta` → `(dN_a, dN_b, dN_c)`
- `delta_tau` → `dN_t`

`packet_delta(a, b)` returns `b - a` component-wise. `translate_packet(packet, delta)` applies a delta and rejects negative resulting counts.

### Spatial unit neighbors

At a fixed `N_t`, two packets are **spatial unit neighbors** when exactly one of `N_a`, `N_b`, `N_c` differs by ±1 and the others are equal. `spatial_unit_neighbors(packet)` lists all valid neighbors (omitting directions that would cross below zero).

These are **graph/count primitives**: adjacency on non-negative integer labels, not an assertion of physical space or a fundamental metric.

## What this stage is not

- **Not dynamics** — no temporal evolution rules or simulation steps.
- **Not gravity** — no `Δτ`-induced forces or effective gravity.
- **Not QM** — no Hilbert space, operators, or quantum postulates.
- **Not particle candidates** — neighbors are combinatorial adjacency, not electrons or photons.
- **Not derived physical constants** — no mass, charge, spin, **ħ**, **α**, or calibrated `t_q` / `l_q`.

## Next stage

Stage 2 will use these neighborhood relations to build an emergent-space toy model while keeping claims at maturity levels A–C.
