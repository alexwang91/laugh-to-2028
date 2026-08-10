from __future__ import annotations

"""Pre-calibration materialization of the exact frozen 0044 S1-S4 path.

This module may read the raw causal inputs required to reconstruct S1-S4, but it
never calls event detection/classification. Calibration does not import this
module; it consumes only the serialized predictor artifact from predictor_io.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from research.governance import brrk_exhaustion_event_study as e0043

from .predictor_io import PRIMARY_AXES, write_predictor_artifact

FROZEN_EVAL_END = pd.Timestamp("2026-08-02")
AXIS_FEATURES = {
    "S1_MOMENTUM_DECELERATION": ("f1_trend_decay7", "f1_macd_hist_decay5"),
    "S2_TREND_DISAGREEMENT": ("f7_slow_fast_disagreement", "f7_disagreement_persistence"),
    "S3_PRICE_STRUCTURE": ("f2_prior_peak_shortfall", "f2_days_since_high60", "f2_ma20_slope10"),
    "S4_VOL_DOWNSIDE": ("f4_rv10_vs_rv30", "f4_down_up_semivol", "f4_pnl_dd_duration_interaction"),
}


class StateInputInvalid(RuntimeError):
    pass


def build_axes_from_0043_scores(scores_0043: pd.DataFrame) -> pd.DataFrame:
    z = scores_0043.attrs.get("z_features")
    if not isinstance(z, pd.DataFrame):
        raise StateInputInvalid("0043 causal z_features missing")
    state = pd.DataFrame(index=z.index)
    for axis in PRIMARY_AXES:
        cols = AXIS_FEATURES[axis]
        missing = [c for c in cols if c not in z.columns]
        if missing:
            raise StateInputInvalid(f"missing frozen feature(s) for {axis}: {missing}")
        state[axis] = z[list(cols)].mean(axis=1, skipna=True)
    return state[list(PRIMARY_AXES)]


def finite_contiguous_suffix(state: pd.DataFrame) -> pd.DataFrame:
    values = state[list(PRIMARY_AXES)].to_numpy(dtype=float)
    complete = np.isfinite(values).all(axis=1)
    positions = np.flatnonzero(complete)
    if not len(positions):
        raise StateInputInvalid("no complete S1-S4 predictor sessions")
    first = int(positions[0])
    if not bool(complete[first:].all()):
        bad = np.flatnonzero(~complete[first:]) + first
        raise StateInputInvalid(f"interior missing S1-S4 predictor session(s): {bad[:10].tolist()}")
    return state.iloc[first:].copy()


def build_predictor_state() -> pd.DataFrame:
    """Recompute only causal predictor state; no taxonomy function is invoked."""
    if e0043.EVAL_END != FROZEN_EVAL_END:
        raise StateInputInvalid(f"0043 EVAL_END drifted: {e0043.EVAL_END}")
    market = e0043.load_market()
    nav, defensive_scale = e0043.load_canonical()
    nav = nav.loc[nav.index <= FROZEN_EVAL_END].sort_index()
    defensive_scale = defensive_scale.loc[defensive_scale.index <= FROZEN_EVAL_END].sort_index()
    scores, _ = e0043.build_features(market, nav, defensive_scale)
    return finite_contiguous_suffix(build_axes_from_0043_scores(scores))


def materialize_predictor_artifact(path: Path) -> dict[str, object]:
    return write_predictor_artifact(path, build_predictor_state())
