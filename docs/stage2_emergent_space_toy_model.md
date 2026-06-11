# Stage 2 — Emergent Space Toy Model

## Purpose

Stage 2 connects Stage 1 neighborhood primitives into a **finite count-lattice toy model** of emergent spatial structure. It defines bounded spatial regions (`SpatialSlice`), graph adjacency within bounds, and provisional spatial metrics that depend on `(N_a, N_b, N_c)` only.

## Relation to Stage 0 and Stage 1

| Stage | Contribution |
|-------|----------------|
| **0** | `TemporalPacket`, emergent Euclidean toy distance, locked definitions |
| **1** | `PacketDelta`, spatial unit neighbors, count-level relations |
| **2** | `SpatialBounds` / `SpatialSlice`, Manhattan/graph metrics, deterministic paths |

`N_t` remains **tau** (local temporal progression count). Spatial metrics **do not** use `N_t`.

> **A change in N_t alone produces temporal mismatch, not spatial separation.**

## Finite SpatialSlice

A `SpatialSlice` fixes `N_t` and a rectangular `SpatialBounds` region:

- `0 <= N_a <= max_N_a` (similarly for `N_b`, `N_c`)
- `packets()` enumerates all lattice sites in the region
- `neighbors_within_bounds(packet)` applies Stage 1 unit neighbors and filters to the slice

This is a **graph on integer counts**, not physical space.

## Graph adjacency

Two packets are adjacent when they are **spatial unit neighbors** (Stage 1) at the same `N_t`. `spatial_graph_distance_steps` equals the L1 count distance—the shortest number of unit edges in this graph. `deterministic_spatial_path` walks axis-by-axis in order `N_a`, `N_b`, `N_c`.

Paths are **combinatorial graph paths**, not trajectories, motion, or dynamics.

## Euclidean vs Manhattan toy distance

| Metric | Formula (spatial counts only) |
|--------|------------------------------|
| **Euclidean** (Stage 0) | `l_q * sqrt(ΔN_a² + ΔN_b² + ΔN_c²)` — provisional flat toy limit |
| **Manhattan** (Stage 2) | `l_q * (|ΔN_a| + |ΔN_b| + |ΔN_c|)` — graph step count scaled by `l_q` |
| **Unit edge** | `l_q` iff packets are spatial unit neighbors at same `N_t` |

Neither metric asserts GR geometry, a fundamental spatial metric, or experimental validation.

## Explicit non-claims

- No physical space derived yet.
- No GR geometry yet.
- No gravity yet.
- No temporal evolution yet.
- No particles yet.
- No QM yet.
- No mass, charge, spin, **ħ**, **α**, or other constants derived.

## Next stage

Stage 3 may introduce a **Δτ gravity proxy**—still conservative language, still not validated physics.
