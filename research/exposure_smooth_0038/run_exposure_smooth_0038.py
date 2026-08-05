"""EXPOSURE-SMOOTH-0038: test a single continuous beta(t, vol) function.

Preregistration: EXPOSURE-SMOOTH-0038.json (written and committed before this
script was ever run against real data).

This file changes exactly ONE thing relative to the frozen
research/core/crypto_rotation_backtest.py: btc_last_drop_beta's two-branch,
discontinuous exposure formula is replaced by a single continuous linear
function of trend, scaled by the SAME volatility multiplier across its full
domain. No new free parameters. See the preregistration for the full
derivation and the constants-reused table.

Everything else -- trend_score, rv30, asset eligibility/scoring/caps inside
build_rotation_weights, the hard trend-sign alt-inclusion switch, cost model,
band, execution timing -- is byte-identical to the frozen backtest.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
sys.path.insert(0, str(RESEARCH / "core"))
sys.path.insert(0, str(RESEARCH))

import crypto_rotation_backtest as bt  # noqa: E402

EXPERIMENT_ID = "EXPOSURE-SMOOTH-0038-CONTINUOUS-BETA"
OUTPUT = RESEARCH / "results" / "exposure_smooth_0038"
COST_BPS = 5.0
BAND = 0.05

# All four constants below are reused verbatim from the existing frozen
# btc_last_drop_beta negative branch and downstream budget cap. None are new.
SLOPE = 0.65
FLOOR = 0.18
CEILING = 1.30


def vol_multiplier(vol: pd.Series) -> pd.Series:
    """Byte-identical to the existing negative-branch vm in crypto_rotation_backtest.py."""
    vm = pd.Series(1.0, index=vol.index)
    vm[(vol >= 0.35) & (vol < 0.50)] = 0.90
    vm[(vol >= 0.50) & (vol < 0.70)] = 0.75
    vm[vol >= 0.70] = 0.60
    return vm


def btc_smooth_beta(price: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Single continuous replacement for bt.btc_last_drop_beta.

    raw = (0.65 + 0.65 * t) * vm(vol); beta = clip(raw, 0.18, 1.30)

    At t=1, vol<0.35 (vm=1.0): raw = 1.30, matching the old positive-branch
    ceiling exactly. At t=0: raw = 0.65*vm, matching the old negative-branch
    value at t=0 exactly. No branch, no discontinuity anywhere.
    """
    t = bt.trend_score(price)
    vol = bt.rv30(price)
    vm = vol_multiplier(vol)
    raw = (SLOPE + SLOPE * t) * vm
    beta = raw.clip(lower=FLOOR, upper=CEILING)
    beta = beta.where(t.notna() & vol.notna())
    return beta, t, vol


def build_rotation_weights_smooth(prices: pd.DataFrame):
    """Copy of bt.build_rotation_weights with btc_last_drop_beta -> btc_smooth_beta.

    Every other line -- alt scoring, eligibility, inverse-vol allocation,
    per-asset caps, and the trend-sign alt-inclusion switch -- is unchanged
    from the frozen function, per the preregistration's explicit scope.
    """
    btc = prices["BTC"]
    beta, btc_t, btc_vol = btc_smooth_beta(btc)

    t = {c: bt.trend_score(prices[c]) for c in prices.columns}
    ratio_t = {c: bt.trend_score(prices[c] / btc) for c in ["ETH", "SOL"]}
    bnb_t_slow = bt.trend_score(prices["BNB"], bt.SLOW_WEIGHTS)
    bnb_ratio_slow = bt.trend_score(prices["BNB"] / btc, bt.SLOW_WEIGHTS)
    vols = {c: bt.rv30(prices[c]) for c in prices.columns}

    w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    scores = pd.DataFrame(np.nan, index=prices.index, columns=["ETH", "SOL", "BNB"])
    scores["ETH"] = 0.60 * t["ETH"] + 0.40 * ratio_t["ETH"]
    scores["SOL"] = 0.50 * t["SOL"] + 0.50 * ratio_t["SOL"]
    scores["BNB"] = 0.60 * bnb_t_slow + 0.40 * bnb_ratio_slow

    for dt in prices.index:
        if pd.isna(beta.loc[dt]) or pd.isna(btc_t.loc[dt]):
            continue
        budget = float(min(beta.loc[dt], 1.30))
        if btc_t.loc[dt] < 0:
            w.loc[dt, "BTC"] = budget
            continue

        eligible = []
        if (
            pd.notna(scores.loc[dt, "ETH"]) and scores.loc[dt, "ETH"] > 0
            and pd.notna(t["ETH"].loc[dt]) and t["ETH"].loc[dt] > 0
            and pd.notna(ratio_t["ETH"].loc[dt]) and ratio_t["ETH"].loc[dt] > 0
        ):
            eligible.append("ETH")
        if (
            pd.notna(scores.loc[dt, "SOL"]) and scores.loc[dt, "SOL"] > 0
            and pd.notna(t["SOL"].loc[dt]) and t["SOL"].loc[dt] > 0
            and pd.notna(ratio_t["SOL"].loc[dt]) and ratio_t["SOL"].loc[dt] > 0
        ):
            eligible.append("SOL")
        if (
            pd.notna(scores.loc[dt, "BNB"]) and scores.loc[dt, "BNB"] > 0
            and pd.notna(bnb_t_slow.loc[dt]) and bnb_t_slow.loc[dt] > 0
            and pd.notna(bnb_ratio_slow.loc[dt]) and bnb_ratio_slow.loc[dt] > 0
        ):
            eligible.append("BNB")

        eligible = sorted(eligible, key=lambda c: scores.loc[dt, c], reverse=True)
        if len(eligible) == 0:
            w.loc[dt, "BTC"] = budget
            continue
        if len(eligible) == 1:
            w.loc[dt, "BTC"] = 0.50 * budget
            w.loc[dt, eligible[0]] = 0.50 * budget
            continue

        chosen = eligible[:2]
        w.loc[dt, "BTC"] = 0.25 * budget
        remaining = 0.75 * budget
        raw = {}
        for c in chosen:
            v = float(vols[c].loc[dt]) if pd.notna(vols[c].loc[dt]) else np.nan
            raw[c] = max(float(scores.loc[dt, c]), 0.0) / max(v, 1e-6) if np.isfinite(v) else 0.0
        total_raw = sum(raw.values())
        if total_raw <= 0:
            w.loc[dt, "BTC"] = budget
            continue
        for c in chosen:
            w.loc[dt, c] = remaining * raw[c] / total_raw

        caps = {"ETH": 0.50 * budget, "SOL": 0.35 * budget, "BNB": 0.25 * budget}
        overflow = 0.0
        for c in chosen:
            if w.loc[dt, c] > caps[c]:
                overflow += w.loc[dt, c] - caps[c]
                w.loc[dt, c] = caps[c]
        w.loc[dt, "BTC"] += overflow

    diagnostics = {"beta": beta, "btc_trend": btc_t, "btc_vol": btc_vol, "scores": scores}
    return w, diagnostics


def gross_cap_to_one(w: pd.DataFrame) -> pd.DataFrame:
    """Identical to walkforward_v1_meta.build_benchmark_v1's post-hoc renormalization."""
    gross = w.abs().sum(axis=1)
    scale = pd.Series(1.0, index=w.index)
    scale[gross > 1.0] = 1.0 / gross[gross > 1.0]
    return w.mul(scale, axis=0)


def whipsaw_diagnostics(btc_trend: pd.Series, held: pd.DataFrame, start: str, end: str) -> dict:
    seg_trend = btc_trend.loc[start:end]
    crossings = int(((seg_trend > 0) != (seg_trend > 0).shift(1)).sum())
    seg_turnover = held.loc[start:end].diff().abs().sum(axis=1)
    return {
        "window": f"{start}..{end}",
        "days": int(len(seg_trend)),
        "trend_sign_crossings": crossings,
        "cumulative_turnover": float(seg_turnover.sum()),
        "mean_daily_turnover": float(seg_turnover.mean()),
    }


def gross_diagnostics(beta: pd.Series, btc_vol: pd.Series, start: str, end: str) -> dict:
    b = beta.loc[start:end]
    v = btc_vol.loc[start:end]
    return {
        "window": f"{start}..{end}",
        "beta_min": float(b.min()),
        "beta_max": float(b.max()),
        "beta_std": float(b.std()),
        "vol_min": float(v.min()),
        "vol_max": float(v.max()),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    close = {}
    for sym in bt.SYMBOLS:
        print(f"Fetching {sym}...", flush=True)
        close[sym.replace("USDT", "")] = bt.fetch_daily(sym)
    prices = pd.concat(close, axis=1).dropna()

    raw_start = prices.index.min()
    eval_start = max(pd.Timestamp("2021-05-01"), raw_start + pd.Timedelta(days=260))
    eval_end = min(prices.index.max(), pd.Timestamp(bt.END_DATE))

    # Frozen baseline, unmodified.
    old_w, old_diag = bt.build_rotation_weights(prices)
    old_v1 = gross_cap_to_one(old_w)

    # Single structural change under test.
    new_w, new_diag = build_rotation_weights_smooth(prices)
    new_v1 = gross_cap_to_one(new_w)

    variants = {
        "V1_FROZEN_BASELINE": old_v1,
        "V1_SMOOTH_BETA_0038": new_v1,
    }

    report: dict = {
        "experiment_id": EXPERIMENT_ID,
        "preregistration": "research/exposure_smooth_0038/EXPOSURE-SMOOTH-0038.json",
        "promotion_evidence": False,
        "trading_changes": False,
        "methodology": {
            "data": "Binance spot UTC daily closes via public market-data REST endpoint",
            "raw_common_start": str(raw_start.date()),
            "evaluation_start": str(eval_start.date()),
            "evaluation_end": str(eval_end.date()),
            "cost_bps": COST_BPS,
            "band": BAND,
            "single_structural_change": "btc_last_drop_beta -> continuous (0.65+0.65t)*vm(vol), clipped [0.18,1.30]; no other change",
        },
        "metrics": {},
        "annual_returns": {},
        "whipsaw_2021_05_15_to_06_30": {},
        "gross_response_2021_05_15_to_06_30": {},
    }

    daily_equity = {}
    for name, w in variants.items():
        res, held = bt.run_portfolio(prices, w, eval_start, eval_end, band=BAND, cost_bps=COST_BPS)
        report["metrics"][name] = bt.metrics(res)
        report["annual_returns"][name] = bt.annual_returns(res["return"])
        daily_equity[name] = res["nav"] * 10000.0

    report["whipsaw_2021_05_15_to_06_30"]["V1_FROZEN_BASELINE"] = whipsaw_diagnostics(
        old_diag["btc_trend"], bt.apply_band(old_v1, BAND).shift(1).fillna(0.0), "2021-05-15", "2021-06-30"
    )
    report["whipsaw_2021_05_15_to_06_30"]["V1_SMOOTH_BETA_0038"] = whipsaw_diagnostics(
        new_diag["btc_trend"], bt.apply_band(new_v1, BAND).shift(1).fillna(0.0), "2021-05-15", "2021-06-30"
    )
    report["gross_response_2021_05_15_to_06_30"]["V1_FROZEN_BASELINE"] = gross_diagnostics(
        old_diag["beta"], old_diag["btc_vol"], "2021-05-15", "2021-06-30"
    )
    report["gross_response_2021_05_15_to_06_30"]["V1_SMOOTH_BETA_0038"] = gross_diagnostics(
        new_diag["beta"], new_diag["btc_vol"], "2021-05-15", "2021-06-30"
    )

    # Sub-windows: the 2021-05 crash segment, the published 3.65-year window, and every
    # existing stress window already defined in the frozen backtest module.
    # crypto_rotation_backtest.py defines its stress windows inline inside main(), not as
    # a module-level constant, so they are reproduced here verbatim rather than imported.
    sub_windows = {
        "2021_05_crash": ("2021-05-01", "2021-08-01"),
        "published_3_65y_window": ("2022-12-10", str(eval_end.date())),
        "2021_2022_bear": ("2021-11-10", "2022-11-21"),
        "2023_2024_bull": ("2023-01-01", "2024-03-31"),
        "2024_2025_period": ("2024-04-01", "2025-12-31"),
    }

    report["sub_windows"] = {}
    for label, (s, e) in sub_windows.items():
        report["sub_windows"][label] = {}
        for name, w in variants.items():
            res, _ = bt.run_portfolio(prices, w, pd.Timestamp(s), min(pd.Timestamp(e), eval_end), band=BAND, cost_bps=COST_BPS)
            report["sub_windows"][label][name] = bt.metrics(res)

    equity_frame = pd.DataFrame(daily_equity)
    equity_frame.index.name = "date"
    equity_frame.to_csv(OUTPUT / "daily_equity.csv", float_format="%.6f")

    beta_frame = pd.DataFrame({
        "old_beta": old_diag["beta"],
        "new_beta": new_diag["beta"],
        "btc_trend": old_diag["btc_trend"],
        "btc_vol": old_diag["btc_vol"],
    })
    beta_frame.to_csv(OUTPUT / "beta_series.csv", float_format="%.6f")

    (OUTPUT / "exposure_smooth_0038_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== EXPOSURE_SMOOTH_0038_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
