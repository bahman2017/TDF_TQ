"""Symbolic constants and toy-model defaults for TDF_TQ."""

T_Q_SYMBOL = "t_q"
L_Q_SYMBOL = "l_q"
C_SYMBOL = "c"


def working_speed_limit(l_q: float, t_q: float) -> float:
    """Return the working speed limit c = l_q / t_q.

    Parameters
    ----------
    l_q:
        Minimal spatial step (toy default units; not a measured physical value).
    t_q:
        Fundamental time quantum. Must be strictly positive.

    Returns
    -------
    float
        l_q / t_q

    Raises
    ------
    ValueError
        If t_q is not strictly positive.
    """
    if t_q <= 0:
        raise ValueError("t_q must be strictly positive")
    return l_q / t_q
