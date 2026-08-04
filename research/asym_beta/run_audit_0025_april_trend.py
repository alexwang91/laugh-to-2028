from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(RESEARCH / "regime_kelly"))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from features_no_dominance import build_features_no_dominance
from features import HORIZONS, TREND_WEIGHTS
from hybrid_meta.walkforward_v1_meta import END, START

AUDIT_ID = "AUDIT-0025-APRIL-TREND-DECOMP"
OUTPUT = RESULTS / "audit_0025_april_trend"
PRIMARY = (pd.Timestamp("2024-03-01"), pd.Timestamp("2024-05-15"))
JUNE = (pd.Timestamp("2024-06-01"), pd.Timestamp("2024-06-30"))


def components(price: pd.Series) -> pd.DataFrame:
    lr = np.log(price).diff()
    out = pd.DataFrame(index=price.index)
    for h, w in zip(HORIZONS, TREND_WEIGHTS):
        mom = np.log(price / price.shift(h))
        scale = lr.rolling(h).std() * math.sqrt(h)
        comp = np.tanh(mom / scale.replace(0, np.nan))
        out[f"comp_{h}"] = comp
        out[f"weighted_{h}"] = w * comp
    out["aggregate_from_components"] = sum(out[f"weighted_{h}"] for h in HORIZONS)
    out["short_weighted"] = out["weighted_20"] + out["weighted_60"]
    out["long_weighted"] = out["weighted_120"] + out["weighted_240"]
    out["long_minus_short"] = out["long_weighted"] - out["short_weighted"]
    out["mask20"] = (out["comp_20"] < 0) & (out["aggregate_from_components"] > 0)
    out["mask20_60"] = (out["comp_20"] < 0) & (out["comp_60"] < 0) & (out["aggregate_from_components"] > 0)
    return out


def first_zero_cross(frame: pd.DataFrame, col: str) -> str | None:
    x = frame[col].dropna()
    if len(x) < 2:
        return None
    crossed = (x < 0) & (x.shift(1) >= 0)
    return str(crossed[crossed].index[0].date()) if crossed.any() else None


def episode(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    x = frame.loc[start:end].copy()
    return {
        "start": str(start.date()),
        "end": str(end.date()),
        "rows": int(len(x)),
        "first_negative_cross": {str(h): first_zero_cross(x, f"comp_{h}") for h in HORIZONS},
        "mask20_days": int(x["mask20"].sum()),
        "mask20_60_days": int(x["mask20_60"].sum()),
        "first_mask20": str(x.index[x["mask20"]][0].date()) if x["mask20"].any() else None,
        "first_mask20_60": str(x.index[x["mask20_60"]][0].date()) if x["mask20_60"].any() else None,
        "min_components": {str(h): float(x[f"comp_{h}"].min()) for h in HORIZONS},
        "min_aggregate": float(x["aggregate_from_components"].min()),
        "max_drawdown_252": float(-x["btc_drawdown_252"].min()),
        "max_long_minus_short": float(x["long_minus_short"].max()),
        "mean_long_minus_short": float(x["long_minus_short"].mean()),
    }


def forward_summary(frame: pd.DataFrame, mask_col: str) -> dict:
    x = frame[frame[mask_col]].copy()
    if x.empty:
        return {"count": 0}
    return {
        "count": int(len(x)),
        "mean_fwd_1d": float(x["btc_fwd_1d"].mean()),
        "median_fwd_1d": float(x["btc_fwd_1d"].median()),
        "mean_fwd_5d": float(x["btc_fwd_5d"].mean()),
        "median_fwd_5d": float(x["btc_fwd_5d"].median()),
        "mean_fwd_10d": float(x["btc_fwd_10d"].mean()),
        "median_fwd_10d": float(x["btc_fwd_10d"].median()),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cfg = RegimeKellyConfig()
    bt.START_DATE = START
    bt.END_DATE = str(END.date())
    prices = pd.concat(
        {asset: bt.fetch_daily(asset + "USDT") for asset in ("BTC", "ETH", "SOL", "BNB", "XRP")},
        axis=1,
    ).sort_index().loc[:END].dropna()
    prices.index = pd.DatetimeIndex(prices.index).normalize()

    feat = build_features_no_dominance(prices, cfg)
    out = components(prices["BTC"])
    out["existing_btc_trend"] = feat["btc_trend"]
    out["btc_drawdown_252"] = prices["BTC"] / prices["BTC"].rolling(252).max() - 1.0
    out["btc_fwd_1d"] = prices["BTC"].shift(-1) / prices["BTC"] - 1.0
    out["btc_fwd_5d"] = prices["BTC"].shift(-5) / prices["BTC"] - 1.0
    out["btc_fwd_10d"] = prices["BTC"].shift(-10) / prices["BTC"] - 1.0
    valid = out[["aggregate_from_components", "existing_btc_trend"]].dropna()
    max_err = float((valid["aggregate_from_components"] - valid["existing_btc_trend"]).abs().max())
    if max_err > 1e-10:
        raise RuntimeError(f"Trend component reconstruction mismatch: {max_err}")

    out.to_csv(OUTPUT / "daily_trend_components.csv", index_label="date")

    april = episode(out, *PRIMARY)
    june = episode(out, *JUNE)
    masked = out[out["mask20_60"]].copy()
    masked_2024 = masked.loc["2024-01-01":"2024-12-31"]

    # Identify contiguous masked-reversal episodes for descriptive comparison.
    groups = []
    if not masked.empty:
        dates = pd.DatetimeIndex(masked.index)
        starts = [dates[0]]
        ends = []
        prev = dates[0]
        for dt in dates[1:]:
            if (dt - prev).days > 1:
                ends.append(prev)
                starts.append(dt)
            prev = dt
        ends.append(prev)
        for s, e in zip(starts, ends):
            x = out.loc[s:e]
            groups.append({
                "start": str(s.date()),
                "end": str(e.date()),
                "days": int(len(x)),
                "mean_aggregate": float(x["aggregate_from_components"].mean()),
                "mean_short_weighted": float(x["short_weighted"].mean()),
                "mean_long_weighted": float(x["long_weighted"].mean()),
                "btc_return_over_episode": float(prices.loc[e, "BTC"] / prices.loc[s, "BTC"] - 1.0),
                "btc_fwd_10d_from_start": float(out.loc[s, "btc_fwd_10d"]) if pd.notna(out.loc[s, "btc_fwd_10d"]) else None,
            })
    pd.DataFrame(groups).to_csv(OUTPUT / "masked_reversal_episodes.csv", index=False)

    report = {
        "audit_id": AUDIT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "trading_changes": False,
        "validation": {"max_aggregate_reconstruction_error": max_err},
        "primary_april_window": april,
        "june_comparison": june,
        "full_history": {
            "mask20_days": int(out["mask20"].sum()),
            "mask20_60_days": int(out["mask20_60"].sum()),
            "masked_episode_count": int(len(groups)),
            "mask20_forward_returns": forward_summary(out, "mask20"),
            "mask20_60_forward_returns": forward_summary(out, "mask20_60"),
        },
        "2024_mask20_60_days": [str(d.date()) for d in masked_2024.index],
        "interpretation_rule": "This audit only diagnoses whether long-horizon trend contributions mask an already-negative short-horizon trend. Zero is the natural sign boundary of the existing components, not a fitted threshold. No trading rule is authorized by this result alone."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== AUDIT_0025_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
