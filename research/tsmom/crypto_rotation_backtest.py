from __future__ import annotations

import pandas as pd


def apply_band(weights: pd.DataFrame, band: float) -> pd.DataFrame:
    """Apply the project's portfolio-level L1 rebalance band deterministically."""
    if weights.empty:
        return weights.copy()
    out = pd.DataFrame(0.0, index=weights.index, columns=weights.columns)
    current = pd.Series(0.0, index=weights.columns, dtype=float)
    for dt, target in weights.iterrows():
        target = target.fillna(0.0).astype(float)
        if float((target - current).abs().sum()) >= float(band):
            current = target.copy()
        out.loc[dt] = current
    return out.astype(float)
