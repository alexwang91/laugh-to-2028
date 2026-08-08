from __future__ import annotations

"""Evaluator for DUAL-LAYER-FUSION-ARCH-SANITY-V1.

This is intentionally a deterministic offline diagnostic.  It consumes a daily
canonical BRRK target path plus daily asset returns and the already-exposed
Stablecoin history, applies the pre-frozen external state/cap rule, and reports
matched baseline/candidate economics.  It is not a production or promotion
entrypoint.
"""

import math
from typing import Iterable

import numpy as np
import pandas as pd

from research.governance.dual_layer_fusion_sanity import (
    ASSETS,
    apply_external_gross_cap,
    classify_external_state,
)


COST_BPS = 5.0


def stablecoin_external_states(total_supply: pd.Series) -> pd.DataFrame:
    x = total_supply.astype(float).sort_index()
    if x.index.has_duplicates:
        raise ValueError("stablecoin history contains duplicate dates")
    if (x <= 0).any() or not np.isfinite(x.to_numpy()).all():
        raise ValueError("stablecoin total supply must be finite and positive")
    log_x = np.log(x)
    # Frozen PIT convention for a decision at D: values dated D-2, D-22, D-42.
    g20 = log_x.shift(2) - log_x.shift(22)
    prev20 = log_x.shift(22) - log_x.shift(42)
    accel = g20 - prev20
    states = []
    caps = []
    for g, a in zip(g20.to_numpy(), accel.to_numpy()):
        if not np.isfinite(g) or not np.isfinite(a):
            states.append(None)
            caps.append(np.nan)
        else:
            s = classify_external_state(float(g), float(a))
            states.append(s.state)
            caps.append(s.gross_cap)
    return pd.DataFrame(
        {"growth_20d": g20, "growth_acceleration_20d": accel, "external_state": states, "external_gross_cap": caps},
        index=x.index,
    )


def apply_state_path(targets: pd.DataFrame, external: pd.DataFrame) -> pd.DataFrame:
    t = targets.loc[:, list(ASSETS)].astype(float).sort_index()
    x = external.reindex(t.index)
    if x[["external_state", "external_gross_cap"]].isna().any().any():
        raise ValueError("external state coverage is incomplete on target dates")
    rows = []
    for dt, row in t.iterrows():
        state_name = str(x.at[dt, "external_state"])
        g = float(x.at[dt, "growth_20d"])
        a = float(x.at[dt, "growth_acceleration_20d"])
        state = classify_external_state(g, a)
        if state.state != state_name:
            raise ValueError("external state mismatch")
        rows.append(apply_external_gross_cap(row.to_dict(), state))
    return pd.DataFrame(rows, index=t.index, columns=list(ASSETS), dtype=float)


def economic_returns(asset_returns: pd.DataFrame, target_weights: pd.DataFrame, *, cost_bps: float = COST_BPS) -> tuple[pd.Series, pd.Series, pd.Series]:
    r = asset_returns.loc[:, list(ASSETS)].astype(float).sort_index()
    w = target_weights.loc[:, list(ASSETS)].astype(float).reindex(r.index)
    if w.isna().any().any():
        raise ValueError("target path missing on return dates")
    held = w.shift(1).fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = held.abs().sum(axis=1)
    ret = (held * r).sum(axis=1) - turnover * float(cost_bps) / 10000.0
    return ret, turnover, gross


def metrics(ret: pd.Series, turnover: pd.Series, gross: pd.Series) -> dict[str, float]:
    ret = ret.dropna().astype(float)
    if ret.empty or (ret <= -1.0).any():
        raise ValueError("invalid return path")
    nav = (1.0 + ret).cumprod()
    years = len(ret) / 365.25
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    sd = float(ret.std())
    sharpe = float(ret.mean() / sd * math.sqrt(365.25)) if sd > 0 else float("nan")
    mdd = float(dd.min())
    return {
        "cagr": cagr,
        "max_drawdown": mdd,
        "sharpe": sharpe,
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else float("nan"),
        "turnover": float(turnover.reindex(ret.index).sum()),
        "average_gross": float(gross.reindex(ret.index).mean()),
        "end_multiple": float(nav.iloc[-1]),
        "observations": float(len(ret)),
    }


def compare_paths(asset_returns: pd.DataFrame, canonical_targets: pd.DataFrame, stablecoin_total_supply: pd.Series) -> dict[str, object]:
    external = stablecoin_external_states(stablecoin_total_supply)
    common = canonical_targets.index.intersection(asset_returns.index).intersection(external.dropna().index)
    if len(common) < 365:
        raise ValueError("matched diagnostic history is too short")
    targets = canonical_targets.loc[common, list(ASSETS)]
    returns = asset_returns.loc[common, list(ASSETS)]
    ext = external.loc[common]
    fused = apply_state_path(targets, ext)
    rb, tb, gb = economic_returns(returns, targets)
    rf, tf, gf = economic_returns(returns, fused)
    base = metrics(rb, tb, gb)
    cand = metrics(rf, tf, gf)
    counts = {str(k): int(v) for k, v in ext["external_state"].value_counts().sort_index().items()}
    return {
        "classification": "NON_PROMOTABLE_ARCHITECTURE_DIAGNOSTIC",
        "dates": {"start": str(common.min().date()), "end": str(common.max().date()), "count": int(len(common))},
        "state_counts": counts,
        "baseline": base,
        "fused": cand,
        "delta": {key: float(cand[key] - base[key]) for key in ("cagr", "max_drawdown", "sharpe", "calmar", "turnover", "average_gross", "end_multiple")},
        "promotion_eligible": False,
    }
