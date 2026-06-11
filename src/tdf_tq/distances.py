"""Emergent distance and temporal mismatch utilities.

Note
----
``emergent_euclidean_distance`` is a provisional Euclidean toy limit based on
differences in spatial packet counts. It is **not** a curved-space metric and
does not represent validated spacetime geometry.
"""

import math

from tdf_tq.packets import TemporalPacket


def delta_tau(packet_a: TemporalPacket, packet_b: TemporalPacket) -> int:
    """Temporal mismatch Delta tau = Delta N_t between two packets."""
    return packet_b.N_t - packet_a.N_t


def spatial_count_delta(
    packet_a: TemporalPacket, packet_b: TemporalPacket
) -> tuple[int, int, int]:
    """Component-wise differences in spatial packet counts."""
    return (
        packet_b.N_a - packet_a.N_a,
        packet_b.N_b - packet_a.N_b,
        packet_b.N_c - packet_a.N_c,
    )


def emergent_euclidean_distance(
    packet_a: TemporalPacket,
    packet_b: TemporalPacket,
    l_q: float = 1.0,
) -> float:
    """Provisional Euclidean distance from spatial count differences.

  This is a toy-model scaffold: distance emerges from differences between
  neighboring spatial packet states scaled by minimal step ``l_q``. It does
  not assert a fundamental spatial metric or GR-compatible geometry.

  Parameters
  ----------
  packet_a, packet_b:
      Packets to compare.
  l_q:
      Minimal spatial step (toy default 1.0).

  Returns
  -------
  float
      l_q * sqrt(delta_Na^2 + delta_Nb^2 + delta_Nc^2)
    """
    d_na, d_nb, d_nc = spatial_count_delta(packet_a, packet_b)
    return l_q * math.sqrt(d_na**2 + d_nb**2 + d_nc**2)
