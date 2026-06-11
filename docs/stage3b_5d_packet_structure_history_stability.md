# Stage 3B — 5D Packet-Structure History and Stability Primitives

## Purpose

Stage 3B upgrades Stage 3A from **static field analysis** to **history-based diagnostics** over full packet structures `E = (N_a, N_b, N_c, N_t)`. Stability is measured across a discrete update series—not from a single snapshot.

> **Stable localized structures have not been found yet; this stage only creates tools to search for them.**

## Relation to Stage 3A

| Stage 3A | Stage 3B |
|----------|----------|
| Static `DeltaTauField` | Field evolution + structure histories |
| Gradient/Laplacian proxies | Persistence, localization, quasi-stability diagnostics |
| Single-time-slice tau | Full packet state + update index `k` |

## 5D toy state-space

**Not physical 5D spacetime.** In this repo:

- **Four packet counts:** `(N_a, N_b, N_c, N_t)` with **tau = N_t**
- **Fifth analysis direction:** discrete update/history index `k` over a sequence of structures

## Why full packets and history?

- A candidate structure must involve the **full packet state**, not only distributed `N_t`.
- **Stability** requires persistence across an update series—single-step snapshots are insufficient.

## PacketStructure

Labeled set of `TemporalPacket`s with unique spatial supports. Diagnostics include:

- `total_tau`, excess above baseline, localization ratio
- `center_of_excess_tau` (weighted count centroid)

## StructureHistory

Sequence of `PacketStructure` instances indexed by toy update step `k`. Tracks tau totals, localization, support overlap, and profile L1 changes between steps.

## Conservative pairwise relaxation

Toy integer rule: transfer tau across spatial edges when difference ≥ threshold. **Total tau is conserved exactly**—this is toy bookkeeping, **not physical energy conservation**.

## Localization and persistence

- **Localization ratio:** max excess / total excess
- **Persistence score:** combines tau conservation, support overlap, and inverse profile step change
- **Quasi-stable pass:** threshold-based toy diagnostic only

## Explicit statement

**Distributed Δτ is being tested as a possible effective-gravity precursor, not asserted as gravity.**

## Explicit non-claims

- No electron-like candidate yet.
- No charge, spin, mass, **ħ**, or **α**.
- No QM, GR, or Newtonian recovery.
- No physical energy conservation.
- No physical 5D spacetime claim.
- No validated physics.

## Next stage

**Stage 4A — Stable localized Δτ packet-structure search** (particle **candidates** only).
