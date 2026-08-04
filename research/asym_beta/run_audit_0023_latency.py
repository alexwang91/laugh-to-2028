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
for path in (RESEARCH, RESEARCH / "regime_kelly", RESEARCH / "hybrid_meta", RESEARCH / "risk_metric_fix", HERE):
    sys.path.insert(0, str(path))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from features_no_dominance import build_features_no_dominance
from regime_model_vb_nd import fit_variational_regime_model_nd
from walkforward_v1_meta import END, START, RISK_BUDGET, build_benchmark_v1, fit_state_v1_distribution, sample_v1_paths
from corrected_risk import choose_scale_corrected
from raw_state_risk import _raw_forward_filter, fit_raw_v1_distribution
from run_asym_beta_0021 import portfolio_returns
from run_asym_beta_0022 import downside_semivolatility, extra_beta_rule

AUDIT_ID = "AUDIT-0023-LATENCY"
RATIO_LEVELS = (0.75, 0.50, 0.25)
OUTPUT = RESULTS / "audit_0023_latency"
KNOWN_EPISODES = {
    "APRIL_2024": (pd.Timestamp("2024-04-01"), pd.Timestamp("2024-04-30")),
    "JUNE_2024": (pd.Timestamp("2024-06-01"), pd.Timestamp("2024-06-30")),
}


def raw_posterior_path(fit, features: pd.DataFrame) -> pd.DataFrame:
    x, factors = fit._transform(features)
    gamma = _raw_forward_filter(fit.model, factors)
    return pd.DataFrame(gamma, index=x.index, columns=range(fit.model.n_components))


def daily_pbad(raw_posterior: pd.DataFrame, frozen_dist: dict) -> pd.Series:
    badness = np.array(
        [frozen_dist["negative_mean_probability"][raw] for raw in raw_posterior.columns],
        dtype=float,
    )
    values = np.clip(raw_posterior.to_numpy(float) @ badness, 0.0, 1.0)
    return pd.Series(values, index=raw_posterior.index, name="daily_p_bad")


def first_crossing(frame: pd.DataFrame, ratio_level: float) -> dict:
    eligible = frame[(frame["monthly_held_extra"] > 1e-12) & (frame["implied_to_held_ratio"] <= ratio_level)]
    if eligible.empty:
        return {"date": None, "days_after_refit": None}
    row = eligible.iloc[0]
    return {
        "date": str(eligible.index[0].date()),
        "days_after_refit": int(row["days_after_refit"]),
    }


def interval_summary(frame: pd.DataFrame) -> dict:
    held = float(frame["monthly_held_extra"].iloc[0])
    active = held > 1e-12
    out = {
        "refit_date": str(frame["refit_date"].iloc[0].date()),
        "interval_end": str(frame.index[-1].date()),
        "days": int(len(frame)),
        "monthly_held_extra": held,
        "active": active,
        "monthly_core_scale": float(frame["monthly_core_scale"].iloc[0]),
        "start_trend": float(frame["daily_btc_trend"].iloc[0]),
        "start_p_bad": float(frame["daily_p_bad"].iloc[0]),
        "start_downside_semivol": float(frame["daily_downside_semivol30"].iloc[0]),
    }
    if not active:
        out.update({
            "mean_daily_implied_extra": 0.0,
            "min_daily_implied_extra": 0.0,
            "min_implied_ratio": None,
            "average_gap": 0.0,
            "max_gap": 0.0,
            "excess_exposure_days": 0.0,
            "negative_btc_day_excess_exposure_days": 0.0,
            "first_crossings": {str(level): {"date": None, "days_after_refit": None} for level in RATIO_LEVELS},
        })
        return out

    ratio = frame["implied_to_held_ratio"]
    gap = frame["held_minus_implied_gap"].clip(lower=0.0)
    min_idx = ratio.idxmin()
    out.update({
        "mean_daily_implied_extra": float(frame["daily_implied_extra"].mean()),
        "min_daily_implied_extra": float(frame["daily_implied_extra"].min()),
        "min_implied_ratio": float(ratio.min()),
        "min_ratio_date": str(min_idx.date()),
        "average_gap": float(gap.mean()),
        "max_gap": float(gap.max()),
        "excess_exposure_days": float(gap.sum()),
        "negative_btc_day_excess_exposure_days": float(gap[frame["btc_return"] < 0].sum()),
        "first_crossings": {str(level): first_crossing(frame, level) for level in RATIO_LEVELS},
        "min_daily_trend": float(frame["daily_btc_trend"].min()),
        "max_daily_p_bad": float(frame["daily_p_bad"].max()),
        "max_daily_downside_semivol": float(frame["daily_downside_semivol30"].max()),
    })
    return out


def episode_summary(daily: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> dict:
    frame = daily.loc[start:end].copy()
    if frame.empty:
        return {"start": str(start.date()), "end": str(end.date()), "rows": 0}
    active = frame[frame["monthly_held_extra"] > 1e-12]
    gap = active["held_minus_implied_gap"].clip(lower=0.0) if not active.empty else pd.Series(dtype=float)
    return {
        "start": str(start.date()),
        "end": str(end.date()),
        "rows": int(len(frame)),
        "active_rows": int(len(active)),
        "mean_monthly_held_extra": float(active["monthly_held_extra"].mean()) if len(active) else 0.0,
        "mean_daily_implied_extra": float(active["daily_implied_extra"].mean()) if len(active) else 0.0,
        "mean_implied_to_held_ratio": float(active["implied_to_held_ratio"].mean()) if len(active) else None,
        "min_implied_to_held_ratio": float(active["implied_to_held_ratio"].min()) if len(active) else None,
        "excess_exposure_days": float(gap.sum()) if len(gap) else 0.0,
        "negative_btc_day_excess_exposure_days": float(gap[active["btc_return"] < 0].sum()) if len(gap) else 0.0,
        "min_trend": float(frame["daily_btc_trend"].min()),
        "max_p_bad": float(frame["daily_p_bad"].max()),
        "max_downside_semivol": float(frame["daily_downside_semivol30"].max()),
        "date_min_ratio": str(active["implied_to_held_ratio"].idxmin().date()) if len(active) else None,
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
    v1_raw = build_benchmark_v1(prices)
    v1_banded = bt.apply_band(v1_raw, 0.05)
    v1_ret, _, _ = portfolio_returns(prices, v1_banded)
    btc_downside = downside_semivolatility(prices["BTC"])
    btc_return = prices["BTC"].pct_change(fill_method=None)

    decision_dates: list[pd.Timestamp] = []
    for dt in features.dropna().index:
        if dt <= END and len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)

    daily_frames = []
    monthly_reference_rows = []

    for j, dt in enumerate(decision_dates):
        next_dt = decision_dates[j + 1] if j + 1 < len(decision_dates) else END + pd.Timedelta(days=1)
        interval_end = next_dt - pd.Timedelta(days=1)
        train = features.loc[:dt]
        fit = fit_variational_regime_model_nd(train, cfg, n_factors=4)

        semantic_post = fit.filtered_posterior(train).iloc[-1]
        semantic_dist = fit_state_v1_distribution(v1_ret.loc[:dt], train, fit, cfg)
        semantic_paths = sample_v1_paths(
            semantic_post,
            fit,
            semantic_dist,
            cfg,
            seed=cfg.random_seed + int(dt.strftime("%Y%m%d")),
        )
        meta = choose_scale_corrected(semantic_paths, RISK_BUDGET)
        p_riskoff = float(np.clip(semantic_post.get("RISK_OFF", 0.0), 0.0, 1.0))
        core_scale = float(1.0 - p_riskoff * (1.0 - float(meta["scale"])))

        frozen_raw_dist = fit_raw_v1_distribution(v1_ret.loc[:dt], train, fit, cfg)
        through_interval = features.loc[:interval_end]
        raw_path = raw_posterior_path(fit, through_interval)
        pbad_path = daily_pbad(raw_path, frozen_raw_dist)

        interval_index = features.loc[dt:interval_end].dropna().index.intersection(raw_path.index)
        if len(interval_index) == 0:
            continue

        monthly_rule = extra_beta_rule(
            core_scale,
            float(features.loc[dt, "btc_trend"]),
            float(pbad_path.loc[dt]),
            float(btc_downside.loc[dt]),
        )
        held_extra = float(monthly_rule["extra_scale"])

        rows = []
        for day in interval_index:
            rule = extra_beta_rule(
                core_scale,
                float(features.loc[day, "btc_trend"]),
                float(pbad_path.loc[day]),
                float(btc_downside.loc[day]),
            )
            implied = float(rule["extra_scale"])
            ratio = implied / held_extra if held_extra > 1e-12 else np.nan
            rows.append({
                "date": day,
                "refit_date": dt,
                "days_after_refit": int((day - dt).days),
                "monthly_core_scale": core_scale,
                "monthly_held_extra": held_extra,
                "daily_implied_extra": implied,
                "implied_to_held_ratio": ratio,
                "held_minus_implied_gap": held_extra - implied,
                "daily_btc_trend": float(features.loc[day, "btc_trend"]),
                "daily_p_bad": float(pbad_path.loc[day]),
                "daily_downside_semivol30": float(btc_downside.loc[day]),
                "daily_downside_scaler": float(rule["downside_scaler"]),
                "btc_return": float(btc_return.loc[day]) if pd.notna(btc_return.loc[day]) else 0.0,
            })
        interval_frame = pd.DataFrame(rows).set_index("date")
        daily_frames.append(interval_frame)
        monthly_reference_rows.append(interval_summary(interval_frame))

        print(
            dt.date(),
            "held", round(held_extra, 4),
            "min_ratio", None if held_extra <= 1e-12 else round(float(interval_frame["implied_to_held_ratio"].min()), 4),
            "gap_days", round(float(interval_frame["held_minus_implied_gap"].clip(lower=0.0).sum()), 4),
            flush=True,
        )

    daily = pd.concat(daily_frames).sort_index()
    monthly = pd.DataFrame(monthly_reference_rows)
    daily.to_csv(OUTPUT / "daily_latency_diagnostics.csv", index_label="date")
    monthly.to_csv(OUTPUT / "interval_summary.csv", index=False)

    active = daily[daily["monthly_held_extra"] > 1e-12].copy()
    active_gap = active["held_minus_implied_gap"].clip(lower=0.0)
    active_monthly = monthly[monthly["active"]].copy()
    ranked = active_monthly.sort_values(["excess_exposure_days", "max_gap"], ascending=False)
    ranked.to_csv(OUTPUT / "active_intervals_ranked.csv", index=False)

    episodes = {
        name: episode_summary(daily, start, end)
        for name, (start, end) in KNOWN_EPISODES.items()
    }

    crossing_counts = {}
    crossing_median_days = {}
    for level in RATIO_LEVELS:
        key = str(level)
        days = [
            row["first_crossings"][key]["days_after_refit"]
            for row in monthly_reference_rows
            if row["active"] and row["first_crossings"][key]["days_after_refit"] is not None
        ]
        crossing_counts[key] = int(len(days))
        crossing_median_days[key] = float(np.median(days)) if days else None

    report = {
        "audit_id": AUDIT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "trading_changes": False,
        "decision_count": int(len(monthly)),
        "active_intervals": int(len(active_monthly)),
        "active_daily_rows": int(len(active)),
        "aggregate": {
            "mean_monthly_held_extra_on_active_days": float(active["monthly_held_extra"].mean()) if len(active) else 0.0,
            "mean_daily_implied_extra_on_active_days": float(active["daily_implied_extra"].mean()) if len(active) else 0.0,
            "mean_implied_to_held_ratio": float(active["implied_to_held_ratio"].mean()) if len(active) else None,
            "median_implied_to_held_ratio": float(active["implied_to_held_ratio"].median()) if len(active) else None,
            "fraction_active_days_daily_implied_below_monthly": float((active["daily_implied_extra"] < active["monthly_held_extra"] - 1e-12).mean()) if len(active) else 0.0,
            "excess_exposure_days": float(active_gap.sum()) if len(active_gap) else 0.0,
            "negative_btc_day_excess_exposure_days": float(active_gap[active["btc_return"] < 0].sum()) if len(active_gap) else 0.0,
            "ratio_crossing_interval_count": crossing_counts,
            "median_days_after_refit_to_ratio_crossing": crossing_median_days,
        },
        "known_damage_episodes": episodes,
        "top_latency_intervals": ranked.head(10).to_dict(orient="records"),
        "interpretation_rule": "This audit does not authorize thresholds. A faster overlay-risk refresh is structurally justified only if already-defined daily implied extra materially falls below the monthly-held extra inside the known loss windows before the next scheduled refit.",
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print("=== AUDIT_0023_REPORT ===")
    print(json.dumps(report, indent=2, default=str))
    print("=== END ===")


if __name__ == "__main__":
    main()
