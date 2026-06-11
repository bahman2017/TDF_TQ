"""Temporal packet primitives."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TemporalPacket:
    """A temporal packet with spatial count components and local progression count.

    Attributes
    ----------
    N_a, N_b, N_c:
        Non-negative integer spatial packet counts (emergent spatial indices).
    N_t:
        Local temporal progression count (tau = N_t). Larger N_t means slower
        local passage of time.
    """

    N_a: int
    N_b: int
    N_c: int
    N_t: int

    def __post_init__(self) -> None:
        for name, value in (
            ("N_a", self.N_a),
            ("N_b", self.N_b),
            ("N_c", self.N_c),
            ("N_t", self.N_t),
        ):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer, got {type(value).__name__}")
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")

    @property
    def tau(self) -> int:
        """Local temporal progression count."""
        return self.N_t

    @property
    def spatial_counts(self) -> tuple[int, int, int]:
        """Spatial packet counts as (N_a, N_b, N_c)."""
        return (self.N_a, self.N_b, self.N_c)
