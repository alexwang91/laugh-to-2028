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

from run_asym_beta_0021 import expected_router_0005_equity_from_persisted_inputs
from run_carry_pnl_0031 import (
    CANONICAL_COST_BPS,
    FUNDING_END,
    build_price_returns,
    complete_common_index,
    funding_accounting,
    load_price_legs,
    turnover_from_drift,
)

EXPERIMENT_ID = "CARRY-STACK-0033-IDLE-CAPITAL"
WEIGHTS_PATH = RESULTS / "pit_disp_0015" / "daily_weights.csv"
CARRY_RESULT_PATH = RESULTS / "carry_pnl_0031" / "summary.json"
OUTPUT = RESULTS / "carry_stack_0033"
BRRK_COLS = [f"BRRK0011_BASELINE__{asset}" for asset in ("BTC", "ETH", "SOL", "BNB", "XRP")]
COST_RATE = CANONICAL_COST_BPS / 10000.0
PARITY_DOLLARS = 0.01


def metrics(ret: pd.Series) -> dict[str, Any]:
    ret = ret.dropna().astype(float)
    if ret.empty:
        raise ValueError("empty return series")
    nav = (1.0 + ret).cumprod()
    years = max((ret.index[-1] - ret.index[0]).days / 365.25, 1.0 / 365.25)
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(ret.std(ddof=1))
    return {
        "start": str(ret.index[0].date()),
        "end": str(ret.index[-1].date()),
        "observations": int(len(ret)),
        "final_10k": float(nav.iloc[-1] * 10000.0),
        "cagr": cagr,
        "max_drawdown": float(dd.min()),
        "max_drawdown_date": str(dd.idxmin().date()),
        "ann_vol": float(std * math.sqrt(365.0)),
        "sharpe": float(ret.mean() / std * math.sqrt(365.0)) if std > 0 else None,
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else None,
    }


def annual_returns(ret: pd.Series) -> dict[str, float]:
    return {str(int(year)): float(value) for year, value in ((1.0 + ret).groupby(ret.index.year).prod() - 1.0).items()}


def cumulative_return(ret: pd.Series) -> float:
    return float((1.0 + ret.dropna()).prod() - 1.0)


def reconstruct_frozen_carry() -> tuple[pd.Series, dict[str, Any]]:
    spot, perp, repairs = load_price_legs()
    index = complete_common_index(spot, perp)
    first_held = pd.Timestamp(index[1])
    spot_ret, perp_ret, price_component, _ = build_price_returns(spot, perp, index)
    funding_factor, _, funding_diag = funding_accounting(index, first_held)
    pre_factor = (1.0 + price_component) * funding_factor
    pre_return = pre_factor - 1.0
    turnover = turnover_from_drift(spot_ret, perp_ret, pre_factor, first_held)
    eval_index = index[(index >= first_held) & (index <= FUNDING_END)]
    carry = (pre_return - turnover * COST_RATE).reindex(eval_index).astype(float)

    expected = json.loads(CARRY_RESULT_PATH.read_text(encoding="utf-8"))
    expected_final = float(expected["canonical_5bps"]["final_10k"])
    actual_final = float((1.0 + carry).prod() * 10000.0)
    delta = actual_final - expected_final
    parity = {
        "expected_final_10k": expected_final,
        "reconstructed_final_10k": actual_final,
        "absolute_difference_dollars": float(abs(delta)),
        "tolerance_dollars": PARITY_DOLLARS,
        "pass": bool(abs(delta) <= PARITY_DOLLARS),
        "funding_event_coverage_ratio": funding_diag.get("event_coverage_ratio"),
        "remaining_required_price_gaps": int(sum(
            row.get("unresolved_count", 0)
            for side in repairs.values() for row in side.values()
        )),
    }
    if not parity["pass"]:
        raise RuntimeError(f"0031 parity failed: {parity}")
    return carry, parity


def brrk_strict_return() -> pd.Series:
    equity = expected_router_0005_equity_from_persisted_inputs().astype(float)
    return equity.pct_change(fill_method=None).rename("BRRK_STRICT_ROUTER")


def held_brrk_gross() -> pd.Series:
    frame = pd.read_csv(WEIGHTS_PATH, parse_dates=["date"]).set_index("date")
    missing = [column for column in BRRK_COLS if column not in frame.columns]
    if missing:
        raise RuntimeError(f"missing BRRK weight columns: {missing}")
    target_gross = frame[BRRK_COLS].abs().sum(axis=1).astype(float)
    held = target_gross.shift(1).rename("held_brrk_gross")
    return held


def idle_scale_from_gross(gross: pd.Series) -> pd.Series:
    return (1.0 - gross.astype(float)).clip(lower=0.0, upper=1.0).rename("carry_scale")


def combine_idle_stack(
    brrk: pd.Series,
    carry: pd.Series,
    gross: pd.Series,
) -> pd.DataFrame:
    common = brrk.dropna().index.intersection(carry.dropna().index).intersection(gross.dropna().index)
    if common.empty:
        raise RuntimeError("no common BRRK/carry/gross dates")
    common = common.sort_values()
    b = brrk.reindex(common).astype(float)
    c = carry.reindex(common).astype(float)
    g = gross.reindex(common).astype(float)
    scale = idle_scale_from_gross(g)
    combined_gross = g + scale
    if float(combined_gross.max()) > 1.0 + 1e-10:
        raise RuntimeError(f"combined gross breach: {combined_gross.max()}")

    prior_scale = scale.shift(1)
    prior_scale.iloc[0] = 0.0
    scale_change_turnover = (scale - prior_scale).abs()
    scale_change_cost = scale_change_turnover * COST_RATE
    scaled_carry_before_scale_cost = scale * c
    scaled_carry_net = scaled_carry_before_scale_cost - scale_change_cost
    combined = b + scaled_carry_net

    return pd.DataFrame({
        "brrk_return": b,
        "carry_unit_return": c,
        "held_brrk_gross": g,
        "carry_scale": scale,
        "combined_gross": combined_gross,
        "scale_change_turnover": scale_change_turnover,
        "scale_change_cost": scale_change_cost,
        "scaled_carry_before_scale_cost": scaled_carry_before_scale_cost,
        "scaled_carry_net": scaled_carry_net,
        "combined_return": combined,
    }, index=common)


def drawdown_attribution(frame: pd.DataFrame) -> dict[str, Any]:
    bnav = (1.0 + frame["brrk_return"]).cumprod()
    cnav = (1.0 + frame["combined_return"]).cumprod()
    bdd = bnav / bnav.cummax() - 1.0
    cdd = cnav / cnav.cummax() - 1.0
    dates = sorted(set([bdd.idxmin(), cdd.idxmin()]))
    rows = []
    for date in dates:
        window = frame.loc[max(frame.index.min(), date - pd.Timedelta(days=7)):min(frame.index.max(), date + pd.Timedelta(days=7))]
        rows.append({
            "date": str(date.date()),
            "brrk_drawdown": float(bdd.loc[date]),
            "combined_drawdown": float(cdd.loc[date]),
            "carry_scale": float(frame.at[date, "carry_scale"]),
            "scaled_carry_net_return_that_day": float(frame.at[date, "scaled_carry_net"]),
            "scaled_carry_net_compound_plusminus7d": cumulative_return(window["scaled_carry_net"]),
        })
    return {"rows": rows}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    carry, parity = reconstruct_frozen_carry()
    brrk = brrk_strict_return()
    gross = held_brrk_gross()
    frame = combine_idle_stack(brrk, carry, gross)

    baseline_metrics = metrics(frame["brrk_return"])
    combined_metrics = metrics(frame["combined_return"])
    annual_brrk = annual_returns(frame["brrk_return"])
    annual_combined = annual_returns(frame["combined_return"])

    from_2025 = frame.loc[frame.index >= pd.Timestamp("2025-01-01")]
    carry_scale = frame["carry_scale"]
    qualification = {
        "return_improvement": bool(combined_metrics["cagr"] > baseline_metrics["cagr"]),
        "sharpe_improvement": bool(combined_metrics["sharpe"] is not None and baseline_metrics["sharpe"] is not None and combined_metrics["sharpe"] > baseline_metrics["sharpe"]),
        "drawdown_nonworsening": bool(combined_metrics["max_drawdown"] >= baseline_metrics["max_drawdown"]),
        "calmar_improvement": bool(combined_metrics["calmar"] is not None and baseline_metrics["calmar"] is not None and combined_metrics["calmar"] > baseline_metrics["calmar"]),
        "gross_discipline": bool(float(frame["combined_gross"].max()) <= 1.0 + 1e-10),
    }
    qualification["qualified_idle_capital_stack"] = bool(all(qualification.values()))

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_VALID_RUN_COMPLETE",
        "promotion_evidence": False,
        "carry_0031_parity": parity,
        "baseline_strict_router_brrk": baseline_metrics,
        "combined_idle_capital_stack": combined_metrics,
        "incremental": {
            "cagr_percentage_points": float((combined_metrics["cagr"] - baseline_metrics["cagr"]) * 100.0),
            "max_drawdown_percentage_points": float((combined_metrics["max_drawdown"] - baseline_metrics["max_drawdown"]) * 100.0),
            "sharpe": float(combined_metrics["sharpe"] - baseline_metrics["sharpe"]),
            "calmar": float(combined_metrics["calmar"] - baseline_metrics["calmar"]),
            "scaled_carry_before_scale_cost_cumulative": cumulative_return(frame["scaled_carry_before_scale_cost"]),
            "scaled_carry_net_cumulative": cumulative_return(frame["scaled_carry_net"]),
            "scale_change_turnover": float(frame["scale_change_turnover"].sum()),
            "scale_change_cost_additive": float(frame["scale_change_cost"].sum()),
        },
        "capital_usage": {
            "avg_held_brrk_gross": float(frame["held_brrk_gross"].mean()),
            "min_held_brrk_gross": float(frame["held_brrk_gross"].min()),
            "max_held_brrk_gross": float(frame["held_brrk_gross"].max()),
            "avg_carry_scale": float(carry_scale.mean()),
            "min_carry_scale": float(carry_scale.min()),
            "max_carry_scale": float(carry_scale.max()),
            "carry_active_day_share": float((carry_scale > 1e-12).mean()),
            "avg_combined_gross": float(frame["combined_gross"].mean()),
            "max_combined_gross": float(frame["combined_gross"].max()),
        },
        "annual_brrk": annual_brrk,
        "annual_combined": annual_combined,
        "from_2025": {
            "baseline_cumulative_return": cumulative_return(from_2025["brrk_return"]),
            "combined_cumulative_return": cumulative_return(from_2025["combined_return"]),
            "scaled_carry_net_cumulative_return": cumulative_return(from_2025["scaled_carry_net"]),
        },
        "drawdown_attribution": drawdown_attribution(frame),
        "qualification": qualification,
        "stopping_rule": "No scale/weight search. Failure does not authorize reducing BRRK, leveraging carry, changing carry assets, or tuning an idle-cap threshold on this historical window.",
        "implementation_limit": "Capital-accounting evidence only. Hyperliquid spot availability, collateral/netting, fee and execution parity remain separate implementation gates."
    }
    frame.to_csv(OUTPUT / "daily_stack.csv", index_label="date")
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== CARRY_STACK_0033_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
