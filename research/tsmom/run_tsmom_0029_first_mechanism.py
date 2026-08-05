from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
for path in (RESEARCH, RESEARCH / "core", HERE):
    sys.path.insert(0, str(path))

import crypto_rotation_backtest as bt
from run_tsmom_perp_universe_audit import KLINE_ROOT, classify, prefix_symbols
from run_tsmom_pit_0028_eligibility import (
    DATA_START,
    EVAL_END,
    EVAL_START,
    MAX_WORKERS,
    build_eligibility,
    fetch_symbol,
)

EXPERIMENT_ID = "TSMOM-0029-FIRST-MECHANISM"
HORIZONS = (20, 60, 120, 240)
TREND_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
RV_WINDOW = 30
GROSS_TARGET = 1.0
BAND = 0.05
COST_FAMILY = (5.0, 10.0, 20.0)
BRRK_EQUITY = RESULTS / "pit_disp_0015" / "daily_equity.csv"
OUTPUT = RESULTS / "tsmom_0029"


def trend_score(close: pd.DataFrame) -> pd.DataFrame:
    logp = np.log(close)
    logret = logp.diff()
    score = pd.DataFrame(0.0, index=close.index, columns=close.columns)
    valid_any = pd.DataFrame(False, index=close.index, columns=close.columns)
    for h, weight in zip(HORIZONS, TREND_WEIGHTS):
        mom = logp - logp.shift(h)
        scale = logret.rolling(h, min_periods=h).std() * math.sqrt(h)
        component = np.tanh(mom / scale.replace(0.0, np.nan))
        score = score.add(weight * component.fillna(0.0), fill_value=0.0)
        valid_any |= component.notna()
    return score.where(valid_any)


def normalized_target_weights(close: pd.DataFrame, eligible: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    score = trend_score(close)
    rv30 = close.pct_change(fill_method=None).rolling(RV_WINDOW, min_periods=RV_WINDOW).std()
    raw = score.div(rv30.clip(lower=1e-6))
    e = eligible.reindex(index=close.index, columns=close.columns, fill_value=False)
    raw = raw.where(e, 0.0).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    denom = raw.abs().sum(axis=1).replace(0.0, np.nan)
    target = raw.div(denom, axis=0).fillna(0.0) * GROSS_TARGET
    return target, score, rv30


def actual_held_weights(target: pd.DataFrame, close: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    banded = bt.apply_band(target, BAND)
    proposed = banded.shift(1).fillna(0.0)
    asset_ret = close.pct_change(fill_method=None)
    # If no valid close-to-close return exists on execution/holding date, the
    # contract cannot contribute that day's exposure. Do not reallocate the
    # missing weight using future availability knowledge.
    actual = proposed.where(asset_ret.notna(), 0.0)
    return actual, asset_ret


def return_components(actual: pd.DataFrame, asset_ret: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series, pd.DataFrame]:
    idx = actual.index
    r = asset_ret.reindex(idx).fillna(0.0)
    contribution = actual * r
    gross_price_return = contribution.sum(axis=1)
    turnover = actual.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = actual.iloc[0].abs().sum()
    return gross_price_return.astype(float), turnover.astype(float), actual.abs().sum(axis=1).astype(float), contribution


def metrics(net_ret: pd.Series, turnover: pd.Series, actual: pd.DataFrame) -> dict[str, Any]:
    r = net_ret.dropna().astype(float)
    nav = (1.0 + r).cumprod()
    elapsed = max((r.index[-1] - r.index[0]).days / 365.25, 1.0 / 365.25)
    cagr = float(nav.iloc[-1] ** (1.0 / elapsed) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(r.std(ddof=1))
    long_gross = actual.clip(lower=0.0).sum(axis=1).reindex(r.index)
    short_gross = (-actual.clip(upper=0.0)).sum(axis=1).reindex(r.index)
    net = actual.sum(axis=1).reindex(r.index)
    gross = actual.abs().sum(axis=1).reindex(r.index)
    long_count = (actual > 0).sum(axis=1).reindex(r.index)
    short_count = (actual < 0).sum(axis=1).reindex(r.index)
    return {
        "start": str(r.index[0].date()),
        "end": str(r.index[-1].date()),
        "observations": int(len(r)),
        "final_10k": float(nav.iloc[-1] * 10000.0),
        "cagr": cagr,
        "max_drawdown": float(dd.min()),
        "ann_vol": float(std * math.sqrt(365.0)),
        "sharpe": float(r.mean() / std * math.sqrt(365.0)) if std > 0 else None,
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else None,
        "daily_skew": float(r.skew()),
        "worst_day": float(r.min()),
        "best_day": float(r.max()),
        "turnover_total": float(turnover.reindex(r.index).sum()),
        "turnover_annualized": float(turnover.reindex(r.index).sum() / elapsed),
        "avg_gross": float(gross.mean()),
        "avg_net": float(net.mean()),
        "avg_long_gross": float(long_gross.mean()),
        "avg_short_gross": float(short_gross.mean()),
        "avg_long_contracts": float(long_count.mean()),
        "avg_short_contracts": float(short_count.mean()),
        "max_abs_net": float(net.abs().max()),
    }


def annual_returns(ret: pd.Series) -> dict[str, float]:
    return {str(int(y)): float((1.0 + x).prod() - 1.0) for y, x in ret.groupby(ret.index.year)}


def brkk_returns() -> pd.Series:
    frame = pd.read_csv(BRRK_EQUITY, parse_dates=["date"]).set_index("date")
    nav = frame["BRRK0011_BASELINE"].astype(float)
    return nav.pct_change(fill_method=None).rename("BRRK")


def correlation_report(tsmom: pd.Series, brkk: pd.Series) -> dict[str, Any]:
    common = pd.concat([tsmom.rename("TSMOM"), brkk], axis=1).dropna()
    monthly = (1.0 + common).resample("ME").prod() - 1.0
    neg = monthly[monthly["BRRK"] < 0]
    worst = monthly.nsmallest(min(10, len(monthly)), "BRRK").copy()
    return {
        "common_start": str(common.index[0].date()) if len(common) else None,
        "common_end": str(common.index[-1].date()) if len(common) else None,
        "common_daily_observations": int(len(common)),
        "daily_pearson": float(common.corr(method="pearson").loc["TSMOM", "BRRK"]) if len(common) > 1 else None,
        "daily_spearman": float(common.corr(method="spearman").loc["TSMOM", "BRRK"]) if len(common) > 1 else None,
        "monthly_observations": int(len(monthly)),
        "monthly_pearson": float(monthly.corr(method="pearson").loc["TSMOM", "BRRK"]) if len(monthly) > 1 else None,
        "monthly_spearman": float(monthly.corr(method="spearman").loc["TSMOM", "BRRK"]) if len(monthly) > 1 else None,
        "brkk_negative_months": int(len(neg)),
        "tsmom_mean_return_in_brkk_negative_months": float(neg["TSMOM"].mean()) if len(neg) else None,
        "tsmom_median_return_in_brkk_negative_months": float(neg["TSMOM"].median()) if len(neg) else None,
        "worst_brkk_months": [
            {"month": str(idx.to_period("M")), "BRRK": float(row["BRRK"]), "TSMOM": float(row["TSMOM"])}
            for idx, row in worst.iterrows()
        ],
    }


def load_full_panel() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, dict[str, Any]], dict[str, str]]:
    all_symbols = prefix_symbols(KLINE_ROOT)
    candidates = sorted(s for s in all_symbols if classify(s) == "ordinary_usdt_candidate")
    data: dict[str, pd.DataFrame] = {}
    diagnostics: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_symbol, symbol): symbol for symbol in candidates}
        for i, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]
            try:
                sym, frame, diag = future.result()
                if not frame.empty:
                    data[sym] = frame
                    diagnostics[sym] = diag
            except Exception as exc:
                errors[symbol] = repr(exc)
            if i % 25 == 0 or i == len(futures):
                print(f"panel_progress {i}/{len(futures)} errors={len(errors)}", flush=True)
    if len(errors) / max(len(candidates), 1) > 0.01:
        raise RuntimeError(f"Too many panel failures: {len(errors)}/{len(candidates)}")
    if not data:
        raise RuntimeError("No TSMOM futures data")
    close = pd.concat({s: df["close"] for s, df in data.items()}, axis=1).sort_index()
    qvol = pd.concat({s: df["quote_volume"] for s, df in data.items()}, axis=1).sort_index()
    cols = sorted(set(close.columns) & set(qvol.columns))
    close, qvol = close[cols], qvol[cols]
    eligible = build_eligibility(close, qvol).reindex(index=close.index, columns=cols, fill_value=False)
    return close, qvol, eligible, diagnostics, errors


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    close, qvol, eligible, diagnostics, errors = load_full_panel()
    target, score, rv30 = normalized_target_weights(close, eligible)
    target = target.loc[EVAL_START:EVAL_END]
    close_eval = close.reindex(target.index)
    actual, asset_ret = actual_held_weights(target, close_eval)
    gross_price_return, turnover, gross, contribution = return_components(actual, asset_ret)

    target.to_csv(OUTPUT / "target_weights.csv.gz", compression="gzip", index_label="date")
    actual.to_csv(OUTPUT / "held_weights.csv.gz", compression="gzip", index_label="date")
    pd.DataFrame({
        "gross_price_return": gross_price_return,
        "turnover": turnover,
        "gross": gross,
        "net": actual.sum(axis=1),
        "long_gross": actual.clip(lower=0.0).sum(axis=1),
        "short_gross": (-actual.clip(upper=0.0)).sum(axis=1),
        "long_count": (actual > 0).sum(axis=1),
        "short_count": (actual < 0).sum(axis=1),
    }).to_csv(OUTPUT / "daily_exposure.csv", index_label="date")

    net_returns: dict[float, pd.Series] = {}
    metrics_by_cost: dict[str, dict[str, Any]] = {}
    annual_by_cost: dict[str, dict[str, float]] = {}
    for cost in COST_FAMILY:
        net = (gross_price_return - turnover * cost / 10000.0).astype(float)
        net_returns[cost] = net
        metrics_by_cost[str(cost)] = metrics(net, turnover, actual)
        annual_by_cost[str(cost)] = annual_returns(net)

    canonical = net_returns[5.0]
    brkk = brkk_returns()
    corr = correlation_report(canonical, brkk)

    # Gross price contribution attribution only; fixed turnover cost is reported
    # separately and is not assigned to individual contracts.
    contract_contrib = contribution.sum(axis=0).sort_values(ascending=False)
    contract_abs = contribution.abs().sum(axis=0).sort_values(ascending=False)
    latest_month = pd.Period(EVAL_END, freq="M")
    ended_early = []
    for symbol, diag in diagnostics.items():
        last = diag.get("archive_last_month")
        if last and latest_month.ordinal - pd.Period(last, freq="M").ordinal >= 2:
            ended_early.append(symbol)
    ended_early = sorted(set(ended_early))
    ended_contribution = float(contract_contrib.reindex(ended_early).fillna(0.0).sum())
    total_gross_contribution = float(contract_contrib.sum())

    attribution = pd.DataFrame({
        "gross_price_contribution": contract_contrib,
        "absolute_daily_contribution_sum": contract_abs.reindex(contract_contrib.index),
        "ended_early_contract": [s in set(ended_early) for s in contract_contrib.index],
    })
    attribution.to_csv(OUTPUT / "contract_contribution.csv", index_label="symbol")

    daily_returns = pd.DataFrame({f"TSMOM_COST_{int(cost)}BPS": ret for cost, ret in net_returns.items()})
    daily_returns.to_csv(OUTPUT / "daily_returns.csv", index_label="date")

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "promotion_evidence": False,
        "data_coverage": {
            "symbols_in_panel": int(close.shape[1]),
            "symbol_errors": len(errors),
            "evaluation_days": int(len(target)),
            "ever_eligible_symbols": int((eligible.loc[EVAL_START:EVAL_END].sum(axis=0) > 0).sum()),
        },
        "frozen_mechanism": {
            "trend_horizons": HORIZONS,
            "trend_weights": TREND_WEIGHTS,
            "risk_normalization": "trend_score / rv30; normalize sum(abs(weights)) to 1",
            "gross_target": GROSS_TARGET,
            "l1_band": BAND,
            "timing": "t -> t+1",
            "cost_family_bps": COST_FAMILY,
            "funding_included": False,
        },
        "metrics_by_cost_bps": metrics_by_cost,
        "annual_returns_by_cost_bps": annual_by_cost,
        "correlation_to_BRRK_at_5bps": corr,
        "contribution": {
            "total_gross_price_contribution_sum": total_gross_contribution,
            "ended_early_contract_gross_contribution_sum": ended_contribution,
            "ended_early_contract_count_in_panel": len(ended_early),
            "top_positive": [{"symbol": s, "contribution": float(v)} for s, v in contract_contrib.head(15).items()],
            "top_negative": [{"symbol": s, "contribution": float(v)} for s, v in contract_contrib.tail(15).items()],
            "top_absolute": [{"symbol": s, "abs_contribution": float(v)} for s, v in contract_abs.head(15).items()],
        },
        "interpretation_limit": "Price-return plus fixed transaction-cost mechanism only. Native funding and venue feasibility are not included, so this cannot be treated as deployable PNL. No sleeve stacking or weight optimization is authorized by this experiment.",
        "stopping_rule": "Do not tune horizons, universe, caps, net exposure or rank selection after this result. If economically weak/highly correlated, preserve/reject. If meaningful and diversifying, next gate is funding/implementation attribution before any BRRK stack test."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== TSMOM_0029_REPORT ===")
    printable = dict(report)
    printable["contribution"] = {
        "total_gross_price_contribution_sum": total_gross_contribution,
        "ended_early_contract_gross_contribution_sum": ended_contribution,
        "top_positive": report["contribution"]["top_positive"][:5],
        "top_negative": report["contribution"]["top_negative"][-5:],
    }
    print(json.dumps(printable, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
