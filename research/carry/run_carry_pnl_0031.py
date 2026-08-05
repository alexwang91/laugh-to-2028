from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
for path in (HERE, RESEARCH, RESEARCH / "asym_beta"):
    sys.path.insert(0, str(path))

from run_carry_data_0030 import (
    ASSETS,
    SPOT_ROOT,
    PERP_ROOT,
    FUNDING_ROOT,
    distribution,
    download_key,
    list_month_objects,
    parse_funding_payload,
    parse_kline_payload,
)
from run_asym_beta_0021 import expected_router_0005_equity_from_persisted_inputs

EXPERIMENT_ID = "CARRY-PNL-0031"
WEIGHT = 0.10
COSTS_BPS = (5.0, 10.0, 20.0)
CANONICAL_COST_BPS = 5.0
FUNDING_END = pd.Timestamp("2026-07-30")
OUTPUT = RESULTS / "carry_pnl_0031"
BRRK_EQUITY_PATH = RESULTS / "pit_disp_0015" / "daily_equity.csv"
EPS = 1e-12


def daily_key(root: str, symbol: str, date: pd.Timestamp) -> str:
    date_text = str(pd.Timestamp(date).date())
    return f"{root.replace('/monthly/', '/daily/')}{symbol}/1d/{symbol}-1d-{date_text}.zip"


def load_monthly_kline_history(root: str, symbol: str, kind: str) -> pd.DataFrame:
    objects = list_month_objects(root, symbol, kind)
    if not objects:
        raise RuntimeError(f"{kind} {symbol}: no monthly objects")
    frames: list[pd.DataFrame] = []
    for row in objects:
        frames.append(parse_kline_payload(download_key(row["key"])))
    history = pd.concat(frames).sort_index()
    return history[~history.index.duplicated(keep="last")]


def repair_internal_daily_gaps(root: str, symbol: str, history: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    if history.empty:
        return history, {"symbol": symbol, "detected": 0, "repaired": 0, "unresolved": []}
    expected = pd.date_range(history.index.min(), history.index.max(), freq="D")
    missing = expected.difference(history.index)
    repaired_rows: list[pd.DataFrame] = []
    repaired_dates: list[str] = []
    unresolved: list[str] = []
    for date in missing:
        key = daily_key(root, symbol, pd.Timestamp(date))
        try:
            frame = parse_kline_payload(download_key(key))
            exact = frame.loc[frame.index == pd.Timestamp(date)]
            if len(exact) != 1:
                raise RuntimeError(f"daily fallback did not contain exactly requested date {date}")
            repaired_rows.append(exact)
            repaired_dates.append(str(pd.Timestamp(date).date()))
        except Exception:
            unresolved.append(str(pd.Timestamp(date).date()))
    out = history.copy()
    if repaired_rows:
        out = pd.concat([out] + repaired_rows).sort_index()
        out = out[~out.index.duplicated(keep="last")]
    return out, {
        "symbol": symbol,
        "detected": int(len(missing)),
        "repaired": int(len(repaired_dates)),
        "unresolved_count": int(len(unresolved)),
        "repaired_dates": repaired_dates,
        "unresolved_dates": unresolved,
    }


def load_price_legs() -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, Any]]:
    spot: dict[str, pd.DataFrame] = {}
    perp: dict[str, pd.DataFrame] = {}
    repairs: dict[str, Any] = {"spot": {}, "perp": {}}
    for symbol in ASSETS:
        s = load_monthly_kline_history(SPOT_ROOT, symbol, "spot")
        p = load_monthly_kline_history(PERP_ROOT, symbol, "perp")
        s, sdiag = repair_internal_daily_gaps(SPOT_ROOT, symbol, s)
        p, pdiag = repair_internal_daily_gaps(PERP_ROOT, symbol, p)
        spot[symbol] = s
        perp[symbol] = p
        repairs["spot"][symbol] = sdiag
        repairs["perp"][symbol] = pdiag
    return spot, perp, repairs


def complete_common_index(spot: dict[str, pd.DataFrame], perp: dict[str, pd.DataFrame]) -> pd.DatetimeIndex:
    first = max([frame.index.min() for frame in spot.values()] + [frame.index.min() for frame in perp.values()])
    last = min([frame.index.max() for frame in spot.values()] + [frame.index.max() for frame in perp.values()] + [FUNDING_END])
    expected = pd.date_range(pd.Timestamp(first), pd.Timestamp(last), freq="D")
    missing: list[tuple[str, str, str]] = []
    for kind, panel in (("spot", spot), ("perp", perp)):
        for symbol, frame in panel.items():
            for date in expected.difference(frame.index):
                missing.append((kind, symbol, str(pd.Timestamp(date).date())))
    if missing:
        raise RuntimeError(f"Required carry leg dates unresolved after official daily fallback: count={len(missing)} examples={missing[:20]}")
    if len(expected) < 2:
        raise RuntimeError("Insufficient common carry history")
    return expected


def load_funding(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    objects = list_month_objects(FUNDING_ROOT, symbol, "funding")
    if not objects:
        raise RuntimeError(f"{symbol}: no funding archive")
    start_period = (pd.Timestamp(start) - pd.Timedelta(days=1)).to_period("M")
    end_period = (pd.Timestamp(end) + pd.Timedelta(days=1)).to_period("M")
    frames: list[pd.DataFrame] = []
    for row in objects:
        period = pd.Period(row["month"], freq="M")
        if start_period <= period <= end_period:
            frames.append(parse_funding_payload(download_key(row["key"])))
    if not frames:
        raise RuntimeError(f"{symbol}: no funding objects in evaluation window")
    out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")
    lower = pd.Timestamp(start - pd.Timedelta(days=1), tz="UTC")
    upper = pd.Timestamp(end + pd.Timedelta(days=1, hours=1), tz="UTC")
    return out[(out["timestamp"] >= lower) & (out["timestamp"] <= upper)].copy()


def event_pnl_date(timestamp: pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(timestamp).tz_convert("UTC")
    day = ts.tz_localize(None).normalize()
    if ts.hour == 0 and ts.minute == 0 and ts.second == 0:
        return day - pd.Timedelta(days=1)
    return day


def funding_accounting(index: pd.DatetimeIndex, first_held: pd.Timestamp) -> tuple[pd.Series, pd.DataFrame, dict[str, Any]]:
    factor = pd.Series(1.0, index=index, dtype=float)
    events: list[dict[str, Any]] = []
    by_asset: list[dict[str, Any]] = []
    total_possible_symbol_days = 0
    covered_symbol_days = 0
    no_event_rows: list[tuple[str, str]] = []

    for symbol in ASSETS:
        frame = load_funding(symbol, first_held, pd.Timestamp(index.max()))
        active_dates = pd.DatetimeIndex(index[index >= first_held])
        total_possible_symbol_days += int(len(active_dates))
        covered_dates: set[pd.Timestamp] = set()
        additive = 0.0
        event_count = 0
        for row in frame.itertuples(index=False):
            ts = pd.Timestamp(row.timestamp)
            pnl_date = event_pnl_date(ts)
            if pnl_date not in index or pnl_date < first_held:
                continue
            rate = float(row.rate)
            contribution = -(-WEIGHT) * rate
            events.append({"timestamp": ts, "pnl_date": pnl_date, "symbol": symbol, "rate": rate, "contribution": contribution})
            covered_dates.add(pd.Timestamp(pnl_date))
            additive += contribution
            event_count += 1
        missing = active_dates.difference(pd.DatetimeIndex(sorted(covered_dates)))
        covered_symbol_days += int(len(active_dates) - len(missing))
        no_event_rows.extend((symbol, str(pd.Timestamp(date).date())) for date in missing)
        by_asset.append({
            "symbol": symbol,
            "funding_event_count": event_count,
            "additive_funding_contribution": float(additive),
            "active_days": int(len(active_dates)),
            "active_days_without_recorded_event": int(len(missing)),
        })

    event_frame = pd.DataFrame(events)
    if not event_frame.empty:
        grouped = event_frame.groupby(["pnl_date", "timestamp"], sort=True)["contribution"].sum()
        if (1.0 + grouped <= 0).any():
            raise RuntimeError("Impossible funding event portfolio loss <= -100%")
        daily_factor = (1.0 + grouped).groupby(level=0).prod()
        factor.loc[daily_factor.index.intersection(factor.index)] = daily_factor.reindex(factor.index).dropna()
    asset_frame = pd.DataFrame(by_asset)
    diag = {
        "event_rows_used": int(len(event_frame)),
        "active_symbol_days": int(total_possible_symbol_days),
        "active_symbol_days_with_recorded_event": int(covered_symbol_days),
        "active_symbol_days_without_recorded_event": int(len(no_event_rows)),
        "event_coverage_ratio": float(covered_symbol_days / total_possible_symbol_days) if total_possible_symbol_days else None,
        "no_event_examples": [{"symbol": s, "date": d} for s, d in no_event_rows[:50]],
        "cumulative_additive_recorded_funding_contribution": float(asset_frame["additive_funding_contribution"].sum()),
    }
    return factor, asset_frame, diag


def build_price_returns(spot: dict[str, pd.DataFrame], perp: dict[str, pd.DataFrame], index: pd.DatetimeIndex) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.DataFrame]:
    spot_ret = pd.DataFrame(index=index, columns=ASSETS, dtype=float)
    perp_ret = pd.DataFrame(index=index, columns=ASSETS, dtype=float)
    for symbol in ASSETS:
        spot_close = spot[symbol].reindex(index)["close"].astype(float)
        perp_close = perp[symbol].reindex(index)["close"].astype(float)
        spot_ret[symbol] = spot_close.pct_change(fill_method=None)
        perp_ret[symbol] = perp_close.pct_change(fill_method=None)
    first_held = index[1]
    required = index[index >= first_held]
    if spot_ret.loc[required].isna().any().any() or perp_ret.loc[required].isna().any().any():
        raise RuntimeError("Missing required carry leg return after repair")
    contribution = WEIGHT * spot_ret - WEIGHT * perp_ret
    price_component = contribution.sum(axis=1).fillna(0.0)
    return spot_ret, perp_ret, price_component, contribution


def turnover_from_drift(
    spot_ret: pd.DataFrame,
    perp_ret: pd.DataFrame,
    pre_factor: pd.Series,
    first_held: pd.Timestamp,
) -> pd.Series:
    turnover = pd.Series(0.0, index=pre_factor.index, dtype=float)
    for date in pre_factor.index:
        if date < first_held:
            continue
        f = float(pre_factor.loc[date])
        drift = 0.0
        for symbol in ASSETS:
            rs = float(spot_ret.at[date, symbol])
            rp = float(perp_ret.at[date, symbol])
            drift += abs(WEIGHT * f - WEIGHT * (1.0 + rs))
            drift += abs((-WEIGHT) * f - (-WEIGHT) * (1.0 + rp))
        turnover.loc[date] = drift
    turnover.loc[first_held] += 1.0
    return turnover


def metrics(ret: pd.Series, turnover: pd.Series | None = None) -> dict[str, Any]:
    ret = ret.dropna().astype(float)
    if ret.empty:
        raise ValueError("empty return series")
    nav = (1.0 + ret).cumprod()
    elapsed_years = max((ret.index[-1] - ret.index[0]).days / 365.25, 1.0 / 365.25)
    cagr = float(nav.iloc[-1] ** (1.0 / elapsed_years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(ret.std(ddof=1))
    out = {
        "start": str(ret.index[0].date()),
        "end": str(ret.index[-1].date()),
        "observations": int(len(ret)),
        "final_10k": float(nav.iloc[-1] * 10000.0),
        "cagr": cagr,
        "max_drawdown": float(dd.min()),
        "ann_vol": float(std * math.sqrt(365.0)),
        "sharpe": float(ret.mean() / std * math.sqrt(365.0)) if std > 0 else None,
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else None,
    }
    if turnover is not None:
        out["turnover"] = float(turnover.reindex(ret.index).fillna(0.0).sum())
    return out


def annual_returns(ret: pd.Series) -> dict[str, float]:
    return {str(int(year)): float(value) for year, value in ((1.0 + ret).groupby(ret.index.year).prod() - 1.0).items()}


def correlation(a: pd.Series, b: pd.Series) -> dict[str, Any]:
    x = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    if len(x) < 2:
        return {"daily_observations": int(len(x)), "daily_correlation": None, "monthly_correlation": None}
    monthly = (1.0 + x).resample("ME").prod() - 1.0
    return {
        "start": str(x.index[0].date()),
        "end": str(x.index[-1].date()),
        "daily_observations": int(len(x)),
        "daily_correlation": float(x["a"].corr(x["b"])),
        "monthly_observations": int(len(monthly)),
        "monthly_correlation": float(monthly["a"].corr(monthly["b"])) if len(monthly) >= 2 else None,
    }


def crisis_alpha(carry: pd.Series, brrk: pd.Series) -> dict[str, Any]:
    x = pd.concat([carry.rename("carry"), brrk.rename("brrk")], axis=1).dropna()
    if x.empty:
        return {}
    cutoff = float(x["brrk"].quantile(0.10))
    tail = x[x["brrk"] <= cutoff]
    worst20 = x.nsmallest(min(20, len(x)), "brrk")
    return {
        "brrk_daily_10pct_cutoff": cutoff,
        "tail_day_count": int(len(tail)),
        "mean_carry_return_on_brrk_worst_decile_days": float(tail["carry"].mean()) if len(tail) else None,
        "compound_carry_return_on_brrk_worst_decile_days": float((1.0 + tail["carry"]).prod() - 1.0) if len(tail) else None,
        "worst20_brrk_days_mean_carry": float(worst20["carry"].mean()) if len(worst20) else None,
        "worst20_brrk_days_compound_carry": float((1.0 + worst20["carry"]).prod() - 1.0) if len(worst20) else None,
    }


def load_brrk_price_return() -> pd.Series:
    frame = pd.read_csv(BRRK_EQUITY_PATH, parse_dates=["date"]).set_index("date")
    equity = frame["BRRK0011_BASELINE"].astype(float)
    return equity.pct_change(fill_method=None).rename("BRRK_PRICE_ONLY")


def load_brrk_strict_return() -> pd.Series:
    equity = expected_router_0005_equity_from_persisted_inputs().astype(float)
    return equity.pct_change(fill_method=None).rename("BRRK_STRICT_ROUTER")


def basis_diagnostics(spot: dict[str, pd.DataFrame], perp: dict[str, pd.DataFrame], index: pd.DatetimeIndex) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for symbol in ASSETS:
        s = spot[symbol].reindex(index)["close"].astype(float)
        p = perp[symbol].reindex(index)["close"].astype(float)
        basis = p / s - 1.0
        out[symbol] = distribution(basis)
    return out


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    spot, perp, repairs = load_price_legs()
    index = complete_common_index(spot, perp)
    first_decision = pd.Timestamp(index[0])
    first_held = pd.Timestamp(index[1])

    spot_ret, perp_ret, price_component, asset_price_contrib = build_price_returns(spot, perp, index)
    funding_factor, funding_by_asset, funding_diag = funding_accounting(index, first_held)
    pre_factor = (1.0 + price_component) * funding_factor
    pre_return = pre_factor - 1.0
    turnover = turnover_from_drift(spot_ret, perp_ret, pre_factor, first_held)

    eval_index = index[(index >= first_held) & (index <= FUNDING_END)]
    net_by_cost: dict[float, pd.Series] = {}
    for cost in COSTS_BPS:
        net_by_cost[cost] = (pre_return - turnover * cost / 10000.0).reindex(eval_index).astype(float)

    canonical = net_by_cost[CANONICAL_COST_BPS]
    price_only_no_funding = price_component.reindex(eval_index)
    funding_only = (funding_factor - 1.0).reindex(eval_index)

    brrk_price = load_brrk_price_return()
    brrk_strict = load_brrk_strict_return()
    corr_price = correlation(canonical, brrk_price)
    corr_strict = correlation(canonical, brrk_strict)
    crisis = crisis_alpha(canonical, brrk_price)

    metrics_by_cost = {str(int(cost)): metrics(ret, turnover.reindex(eval_index)) for cost, ret in net_by_cost.items()}
    canonical_metrics = metrics_by_cost[str(int(CANONICAL_COST_BPS))]
    funding_positive = bool(funding_diag["cumulative_additive_recorded_funding_contribution"] > 0)
    qualification = {
        "net_economics": bool(canonical_metrics["cagr"] > 0 and canonical_metrics["sharpe"] is not None and canonical_metrics["sharpe"] > 0),
        "funding_mechanism": funding_positive,
        "daily_correlation_below_0_50": bool(corr_price.get("daily_correlation") is not None and corr_price["daily_correlation"] < 0.50),
        "nonnegative_brrk_worst_decile_day_alpha": bool(
            crisis.get("mean_carry_return_on_brrk_worst_decile_days") is not None
            and crisis["mean_carry_return_on_brrk_worst_decile_days"] >= 0
        ),
    }
    qualification["qualified_for_stack_test"] = bool(all(qualification.values()))

    terminal_liquidation_cost = 1.0 * CANONICAL_COST_BPS / 10000.0
    canonical_nav = (1.0 + canonical).cumprod()
    liquidatable_final_10k = float(canonical_nav.iloc[-1] * (1.0 - terminal_liquidation_cost) * 10000.0)

    daily = pd.DataFrame(index=eval_index)
    daily["price_spread_component"] = price_component.reindex(eval_index)
    daily["funding_factor"] = funding_factor.reindex(eval_index)
    daily["funding_only_return"] = funding_only
    daily["pre_cost_return"] = pre_return.reindex(eval_index)
    daily["turnover"] = turnover.reindex(eval_index)
    for cost, ret in net_by_cost.items():
        daily[f"net_{int(cost)}bps"] = ret
    daily.to_csv(OUTPUT / "daily_returns.csv", index_label="date")

    price_asset_rows = []
    for symbol in ASSETS:
        price_asset_rows.append({
            "symbol": symbol,
            "spot_weight": WEIGHT,
            "perp_weight": -WEIGHT,
            "cumulative_additive_price_spread_contribution": float(asset_price_contrib[symbol].reindex(eval_index).sum()),
        })
    price_asset_frame = pd.DataFrame(price_asset_rows)
    per_asset = price_asset_frame.merge(funding_by_asset, on="symbol", how="left")
    per_asset.to_csv(OUTPUT / "per_asset_contributions.csv", index=False)

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_VALID_RUN_COMPLETE",
        "promotion_evidence": False,
        "execution": {
            "first_completed_common_day": str(first_decision.date()),
            "first_held_day": str(first_held.date()),
            "end": str(eval_index[-1].date()),
            "spot_weight_each": WEIGHT,
            "perp_weight_each": -WEIGHT,
            "gross": 1.0,
            "net_at_rebalance": 0.0,
            "initial_entry_turnover": 1.0,
            "canonical_cost_bps": CANONICAL_COST_BPS,
        },
        "price_repairs": repairs,
        "metrics_by_cost_bps": metrics_by_cost,
        "canonical_5bps": canonical_metrics,
        "diagnostic_components": {
            "price_spread_only_no_cost": metrics(price_only_no_funding),
            "funding_only_no_cost": metrics(funding_only),
            "cumulative_additive_price_spread_component": float(price_component.reindex(eval_index).sum()),
            "cumulative_additive_recorded_funding_contribution": funding_diag["cumulative_additive_recorded_funding_contribution"],
            "total_turnover": float(turnover.reindex(eval_index).sum()),
            "liquidatable_terminal_final_10k_after_extra_5bps_gross_exit": liquidatable_final_10k,
        },
        "funding": funding_diag,
        "per_asset": per_asset.to_dict(orient="records"),
        "basis": basis_diagnostics(spot, perp, eval_index),
        "annual_net_5bps": annual_returns(canonical),
        "correlation_vs_brrk_price_only": corr_price,
        "correlation_vs_brrk_strict_router": corr_strict,
        "crisis_alpha_vs_brrk_price_only": crisis,
        "qualification": qualification,
        "stopping_rule": (
            "Freeze this first valid result. No same-window funding threshold, asset removal, Top-K, basis threshold, leverage, or dynamic-weight rescue. "
            "Any later conditioned or cross-venue carry requires separate mechanism motivation and preregistration."
        ),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== CARRY_PNL_0031_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
