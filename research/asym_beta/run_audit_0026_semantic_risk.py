from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
for path in (RESEARCH, RESEARCH / "regime_kelly", RESEARCH / "hybrid_meta"):
    sys.path.insert(0, str(path))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from features_no_dominance import build_features_no_dominance
from regime_model_vb_nd import fit_variational_regime_model_nd
from walkforward_v1_meta import END, START

AUDIT_ID = "AUDIT-0026-APRIL-SEMANTIC-RISK"
OUTPUT = RESULTS / "audit_0026_semantic_risk"
LEVELS = (0.25, 0.50, 0.75)
APRIL = (pd.Timestamp("2024-03-01"), pd.Timestamp("2024-05-15"))
JUNE = (pd.Timestamp("2024-06-01"), pd.Timestamp("2024-06-30"))


def first_crossing(frame: pd.DataFrame, level: float) -> dict:
    x = frame[frame["p_riskoff"] >= level]
    if x.empty:
        return {"date": None, "days_after_refit": None}
    row = x.iloc[0]
    return {"date": str(x.index[0].date()), "days_after_refit": int(row["days_after_refit"])}


def episode_summary(daily: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    x = daily.loc[start:end].copy()
    if x.empty:
        return {"start": str(start.date()), "end": str(end.date()), "rows": 0}
    max_idx = x["p_riskoff"].idxmax()
    return {
        "start": str(start.date()),
        "end": str(end.date()),
        "rows": int(len(x)),
        "start_p_riskoff": float(x["p_riskoff"].iloc[0]),
        "max_p_riskoff": float(x["p_riskoff"].max()),
        "max_p_riskoff_date": str(max_idx.date()),
        "mean_p_riskoff": float(x["p_riskoff"].mean()),
        "min_btc_drawdown_252": float(x["btc_drawdown_252"].min()),
        "max_drawdown_magnitude": float(-x["btc_drawdown_252"].min()),
        "first_probability_crossings": {str(level): first_crossing(x, level) for level in LEVELS},
    }


def forward_summary(daily: pd.DataFrame, level: float) -> dict:
    x = daily[daily["p_riskoff"] >= level]
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
    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    bt.START_DATE = START
    bt.END_DATE = str(END.date())

    prices = pd.concat(
        {asset: bt.fetch_daily(asset + "USDT") for asset in ("BTC", "ETH", "SOL", "BNB", "XRP")},
        axis=1,
    ).sort_index().loc[:END].dropna()
    prices.index = pd.DatetimeIndex(prices.index).normalize()
    features = build_features_no_dominance(prices, cfg)

    decision_dates: list[pd.Timestamp] = []
    for dt in features.dropna().index:
        if dt <= END and len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("No eligible monthly fits")

    frames: list[pd.DataFrame] = []
    interval_rows: list[dict] = []
    for j, dt in enumerate(decision_dates):
        next_dt = decision_dates[j + 1] if j + 1 < len(decision_dates) else END + pd.Timedelta(days=1)
        interval_end = next_dt - pd.Timedelta(days=1)
        fit = fit_variational_regime_model_nd(features.loc[:dt], cfg, n_factors=4)
        posterior = fit.filtered_posterior(features.loc[:interval_end])
        if "RISK_OFF" not in posterior.columns:
            raise RuntimeError(f"RISK_OFF absent from semantic posterior at {dt.date()}")
        idx = features.loc[dt:interval_end].dropna().index.intersection(posterior.index)
        if len(idx) == 0:
            continue
        frame = pd.DataFrame(index=idx)
        frame["refit_date"] = dt
        frame["days_after_refit"] = (frame.index - dt).days
        frame["p_riskoff"] = posterior.loc[idx, "RISK_OFF"].astype(float)
        frame["btc_drawdown_252"] = features.loc[idx, "btc_drawdown_252"].astype(float)
        frames.append(frame)

        start_p = float(frame["p_riskoff"].iloc[0])
        max_idx = frame["p_riskoff"].idxmax()
        interval_rows.append({
            "refit_date": str(dt.date()),
            "interval_end": str(interval_end.date()),
            "days": int(len(frame)),
            "start_p_riskoff": start_p,
            "max_p_riskoff": float(frame["p_riskoff"].max()),
            "max_p_riskoff_date": str(max_idx.date()),
            "max_increase": float(frame["p_riskoff"].max() - start_p),
            "min_btc_drawdown_252": float(frame["btc_drawdown_252"].min()),
            "crossings": {str(level): first_crossing(frame, level) for level in LEVELS},
        })
        print(dt.date(), "start", round(start_p,4), "max", round(float(frame["p_riskoff"].max()),4), "maxdd", round(float(frame["btc_drawdown_252"].min()),4), flush=True)

    daily = pd.concat(frames).sort_index()
    # Scheduled intervals are non-overlapping; this is a hard sanity check.
    if daily.index.duplicated().any():
        raise RuntimeError("Duplicate daily semantic rows across monthly intervals")

    btc = prices["BTC"]
    daily["btc_fwd_1d"] = (btc.shift(-1) / btc - 1.0).reindex(daily.index)
    daily["btc_fwd_5d"] = (btc.shift(-5) / btc - 1.0).reindex(daily.index)
    daily["btc_fwd_10d"] = (btc.shift(-10) / btc - 1.0).reindex(daily.index)
    daily.to_csv(OUTPUT / "daily_semantic_risk.csv", index_label="date")
    intervals = pd.DataFrame(interval_rows)
    intervals.to_csv(OUTPUT / "interval_summary.csv", index=False)

    report = {
        "audit_id": AUDIT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "trading_changes": False,
        "decision_count": int(len(intervals)),
        "primary_april_window": episode_summary(daily, *APRIL),
        "june_comparison": episode_summary(daily, *JUNE),
        "full_history": {
            "rows": int(len(daily)),
            "p_riskoff_quantiles": {str(q): float(daily["p_riskoff"].quantile(q)) for q in (0.50,0.75,0.90,0.95,0.99)},
            "forward_by_descriptive_level": {str(level): forward_summary(daily, level) for level in LEVELS},
            "intervals_with_crossing": {
                str(level): int(sum(row["crossings"][str(level)]["date"] is not None for row in interval_rows))
                for level in LEVELS
            },
        },
        "top_interval_increases": intervals.sort_values("max_increase", ascending=False).head(10).to_dict(orient="records"),
        "interpretation_rule": "The 25/50/75% levels are descriptive only. This audit asks whether existing semantic risk information was available before April losses under the frozen monthly model; it does not authorize a probability threshold or trading rule."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print("=== AUDIT_0026_REPORT ===")
    print(json.dumps(report, indent=2, default=str))
    print("=== END ===")


if __name__ == "__main__":
    main()
