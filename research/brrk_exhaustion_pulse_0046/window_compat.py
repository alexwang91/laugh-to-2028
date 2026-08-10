from __future__ import annotations

"""Exact 0045-compatible session-window semantics for 0046 evaluation repair.

This module contains no detector, calibration, threshold, taxonomy, gate or
portfolio logic. It exists only because the first post-lock 0046 evaluation
exposed that evaluation.py raised on a frozen peak outside the complete S1-S4
index, while the preregistration explicitly freezes the exact 0045 window
semantics. Missing peaks therefore yield an empty window and boundary windows
are clipped to the available index, exactly as immutable 0045 did.
"""

import numpy as np
import pandas as pd


def window_positions(index: pd.Index, peak: pd.Timestamp, bounds: tuple[int, int]) -> list[int]:
    if peak not in index:
        return []
    pos = int(index.get_loc(peak))
    lo = max(0, pos + bounds[0])
    hi = min(len(index) - 1, pos + bounds[1])
    if lo > hi:
        return []
    return list(range(lo, hi + 1))


def earliest_pulse(
    pulse: np.ndarray,
    index: pd.Index,
    peak: pd.Timestamp,
    bounds: tuple[int, int],
) -> tuple[str | None, int | None]:
    positions = window_positions(index, peak, bounds)
    if not positions:
        return None, None
    peak_pos = int(index.get_loc(peak))
    for pos in positions:
        if bool(pulse[pos]):
            return str(pd.Timestamp(index[pos]).date()), int(peak_pos - pos)
    return None, None
