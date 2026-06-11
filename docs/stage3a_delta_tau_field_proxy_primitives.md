# Stage 3A — Delta Tau Field Proxy Primitives

## Purpose

Stage 3A is the first engineering step toward Stage 3. It represents **distributed tau = N_t values** on the Stage 2 spatial count lattice and computes deterministic finite-difference **toy quantities**: gradients, Laplacian-like roughness, and a conservative **gravity-like direction proxy**.

This is a **field-analysis layer only**—not derived gravity.

## Relation to Stage 0–2

| Stage | Role |
|-------|------|
| **0** | Locked definitions: tau = N_t, Δτ = ΔN_t, emergent spatial distance |
| **1** | Spatial unit neighbors, packet deltas |
| **2** | `SpatialSlice`, graph metrics, finite regions |
| **3A** | `DeltaTauField` — tau assigned per spatial site; finite-difference proxies |

### Packet N_t vs field-assigned tau

A `TemporalPacket` carries its own `N_t`. A `DeltaTauField` assigns **local tau at each spatial triple** `(N_a, N_b, N_c)` independently. `slice.N_t` is a **reference layer label** for neighbor lookups; field values may differ site by site.

> **Distributed Δτ is being tested as a possible effective-gravity precursor, not asserted as gravity.**

## DeltaTauField

- Keys: `(N_a, N_b, N_c)` inside `SpatialBounds`
- Values: non-negative integer tau counts
- Must cover every spatial site in the slice exactly once

Constructors: `uniform_delta_tau_field`, `radial_delta_tau_field` (Manhattan profile—toy only).

## Proxy definitions

| Proxy | Definition |
|-------|------------|
| **Gradient** | Finite differences of tau w.r.t. count indices (central / forward / backward) |
| **Laplacian proxy** | Sum of `(neighbor_tau - center_tau)` over in-bounds unit neighbors |
| **Direction proxy** | `-grad(tau)` — force-**like** only, no mass or G |
| **Normalized direction** | Unit vector, or `(0,0,0)` if magnitude is zero |

None of these are physical acceleration, GR curvature, or Newtonian force.

## Explicit non-claims

- No GR derivation.
- No Newtonian recovery yet.
- No physical mass or energy.
- No particles.
- No QM.
- No curvature tensor.
- No physical constants derived.
- No experimental validation.

Δτ does **not** automatically mean matter.

## Next stage

Stage 3B/3 may compare proxies to Newtonian/GR-like effective limits—still conservative language, still not validated physics.
