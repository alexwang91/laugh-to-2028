from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from research.core.crypto_rotation_backtest import (  # noqa: E402
    COST_BPS,
    apply_band,
    fetch_daily,
    trend_score,
)
from research.funding_router.run_frozen_holdings_funding_pnl import (  # noqa: E402
    COMMON_END,
    COMMON_START,
    funding_accounting,
    load_common_blocks,
)

EXPERIMENT_ID = "TSMOM-0027-PRETEST"
ASSETS = ("BTC", "ETH", "SOL", "BNB")
SYMBOLS = {asset: f"{asset}USDT" for asset in ASSETS}
BAND = 0.05
STARTING_NAV = 10_000.0
RESULTS_DIR = ROOT / "research/results/tsmom_0027_pretest"
BRRK_EQUITY_PATH = ROOT / "research/results/pit_disp_0015/daily_equity.csv"

# Frozen before seeing results. No parameter search, no leverage, no relative ranking.
PASS_CRITERIA = {
    "standalone_sharpe_min": 1.00,
    "corr_vs_brrk_max": 0.40,
    "drawdown_corr_vs_brrk_max": 0.40,
    "combined_sharpe_uplift_min": 0.15,
    "combined_mdd_extra_loss_max": 0.02,
    "combined_calmar_not_below_brrk": True,
}
STRONG_CRITERIA = {
    "standalone_sharpe_min": 1.20,
    "corr_vs_brrk_max": 0.25,
    "drawdown_corr_vs_brrk_max": 0.20,
    "combined_sharpe_uplift_min": 0.25,
    "combined_mdd_not_worse": True,
    "combined_calmar_min": 2.00,
    "post_2024_total_return_positive": True,
}


def metrics_from_returns(returns: pd.Series) -> dict:
    r = returns.dropna().astype(float)
    nav = (1.0 + r).cumprod()
    years = len(r) / 365.25
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else np.nan
    dd = nav / nav.cummax() - 1.0
    std = float(r.std(ddof=1))
    ann_vol = std * math.sqrt(365.0)
    sharpe = float(r.mean() / std * math.sqrt(365.0)) if std > 0 else np.nan
    mdd = float(dd.min())
    return {
        "start": str(r.index[0].date()),
        "end": str(r.index[-1].date()),
        "observations": int(len(r)),
        "final_multiple": float(nav.iloc[-1]),
        "final_10k": float(nav.iloc[-1] * STARTING_NAV),
        "cagr": cagr,
        "max_drawdown": mdd,
        "ann_vol": float(ann_vol),
        "sharpe": sharpe,
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else np.nan,
    }


def annual_returns(returns: pd.Series) -> dict:
    return {
        str(int(year)): float((1.0 + group).prod() - 1.0)
        for year, group in returns.groupby(returns.index.year)
    }


def run_from_target(
    prices: pd.DataFrame,
    target: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    target = target.copy()
    target = apply_band(target, BAND)
    held = target.shift(1).fillna(0.0)
    dates = prices.loc[start:end].index
    held = held.loc[dates]
    rets = prices.pct_change().loc[dates].fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = (held * rets).sum(axis=1)
    net = gross - turnover * COST_BPS / 10_000.0
    gross_exposure = held.abs().sum(axis=1)
    return net, held, turnover, gross_exposure


def build_equal_active_tsmom(prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    trends = {asset: trend_score(prices[asset]) for asset in ASSETS}
    active = pd.DataFrame({asset: (trends[asset] > 0).astype(float) for asset in ASSETS}, index=prices.index)
    count = active.sum(axis=1)
    target = active.div(count.replace(0.0, np.nan), axis=0).fillna(0.0)
    return target, trends


def load_brrk_returns() -> pd.Series:
    frame = pd.read_csv(BRRK_EQUITY_PATH, parse_dates=["date"]).set_index("date")
    equity = frame["BRRK0011_BASELINE"].astype(float)
    ret = equity.pct_change(fill_method=None)
    ret.iloc[0] = equity.iloc[0] / STARTING_NAV - 1.0
    return ret.rename("BRRK0011_BASELINE")


def aligned_corr(a: pd.Series, b: pd.Series, mask: pd.Series | None = None) -> float:
    x = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    if mask is not None:
        m = mask.reindex(x.index).fillna(False).astype(bool)
        x = x.loc[m]
    return float(x.a.corr(x.b)) if len(x) >= 3 else np.nan


def correlation_diagnostics(tsmom: pd.Series, brrk: pd.Series) -> dict:
    x = pd.concat([tsmom.rename("tsmom"), brrk.rename("brrk")], axis=1).dropna()
    bnav = (1.0 + x.brrk).cumprod()
    bdd = bnav / bnav.cummax() - 1.0
    drawdown_mask = bdd < 0
    negative_mask = x.brrk < 0
    q10 = x.brrk.quantile(0.10)
    worst_decile_mask = x.brrk <= q10
    monthly = (1.0 + x).resample("ME").prod() - 1.0
    return {
        "daily_full": float(x.tsmom.corr(x.brrk)),
        "daily_when_brrk_in_drawdown": float(x.loc[drawdown_mask, "tsmom"].corr(x.loc[drawdown_mask, "brrk"])),
        "daily_when_brrk_negative": float(x.loc[negative_mask, "tsmom"].corr(x.loc[negative_mask, "brrk"])),
        "daily_brrk_worst_decile": float(x.loc[worst_decile_mask, "tsmom"].corr(x.loc[worst_decile_mask, "brrk"])),
        "monthly_full": float(monthly.tsmom.corr(monthly.brrk)),
        "drawdown_days": int(drawdown_mask.sum()),
        "negative_brrk_days": int(negative_mask.sum()),
        "worst_decile_cutoff": float(q10),
    }


def sleeve_matrix(sleeve_returns: dict[str, pd.Series]) -> dict:
    frame = pd.DataFrame(sleeve_returns).dropna()
    corr = frame.corr()
    return {
        "daily_return_correlation": {
            row: {col: float(corr.loc[row, col]) for col in corr.columns}
            for row in corr.index
        },
        "mean_off_diagonal_corr": float(
            corr.to_numpy()[np.triu_indices_from(corr.to_numpy(), k=1)].mean()
        ),
    }


def funding_sensitivity(tsmom_return: pd.Series, held: pd.DataFrame) -> dict:
    _, hyper = load_common_blocks()
    start_date = COMMON_START.tz_convert("UTC").tz_localize(None).normalize()
    end_date = COMMON_END.tz_convert("UTC").tz_localize(None).normalize()
    common_return = tsmom_return.loc[start_date:end_date].copy()

    fw = held.loc[start_date:end_date, list(ASSETS)].copy()
    fw["XRP"] = 0.0

    all_perp = funding_accounting(hyper, fw, "compounded_rate", "TSMOM_HL_ALL_PERP")
    all_perp_factor = all_perp["daily_factor"].reindex(common_return.index)
    all_perp_ret = (1.0 + common_return) * all_perp_factor - 1.0

    # Current strict-router economic sensitivity: BTC is the only verified strict spot leg.
    # ETH/SOL/BNB retain native-perp funding here. This is NOT a full fee/slippage router backtest.
    non_btc = fw.copy()
    non_btc["BTC"] = 0.0
    btc_spot = funding_accounting(hyper, non_btc, "compounded_rate", "TSMOM_BTC_SPOT_OTHERS_HL_PERP")
    btc_spot_factor = btc_spot["daily_factor"].reindex(common_return.index)
    btc_spot_ret = (1.0 + common_return) * btc_spot_factor - 1.0

    return {
        "window": {"start": str(start_date.date()), "end": str(end_date.date())},
        "price_only": metrics_from_returns(common_return),
        "hyperliquid_all_perp": metrics_from_returns(all_perp_ret),
        "btc_spot_others_hyperliquid_perp_funding_sensitivity": metrics_from_returns(btc_spot_ret),
        "funding_only": {
            "all_perp_compounded": float(all_perp_factor.prod() - 1.0),
            "btc_spot_others_perp_compounded": float(btc_spot_factor.prod() - 1.0),
        },
        "note": "Funding sensitivity only; venue-specific trading fees/slippage are not re-priced here.",
    }


def evaluate_gate(tsmom_m: dict, brrk_m: dict, combo_m: dict, corr: dict, post_2024: float) -> dict:
    uplift = combo_m["sharpe"] - brrk_m["sharpe"]
    pass_checks = {
        "standalone_sharpe": tsmom_m["sharpe"] >= PASS_CRITERIA["standalone_sharpe_min"],
        "corr_vs_brrk": corr["daily_full"] <= PASS_CRITERIA["corr_vs_brrk_max"],
        "drawdown_corr_vs_brrk": corr["daily_when_brrk_in_drawdown"] <= PASS_CRITERIA["drawdown_corr_vs_brrk_max"],
        "combined_sharpe_uplift": uplift >= PASS_CRITERIA["combined_sharpe_uplift_min"],
        "combined_mdd": combo_m["max_drawdown"] >= brrk_m["max_drawdown"] - PASS_CRITERIA["combined_mdd_extra_loss_max"],
        "combined_calmar": combo_m["calmar"] >= brrk_m["calmar"],
    }
    strong_checks = {
        "standalone_sharpe": tsmom_m["sharpe"] >= STRONG_CRITERIA["standalone_sharpe_min"],
        "corr_vs_brrk": corr["daily_full"] <= STRONG_CRITERIA["corr_vs_brrk_max"],
        "drawdown_corr_vs_brrk": corr["daily_when_brrk_in_drawdown"] <= STRONG_CRITERIA["drawdown_corr_vs_brrk_max"],
        "combined_sharpe_uplift": uplift >= STRONG_CRITERIA["combined_sharpe_uplift_min"],
        "combined_mdd": combo_m["max_drawdown"] >= brrk_m["max_drawdown"],
        "combined_calmar": combo_m["calmar"] >= STRONG_CRITERIA["combined_calmar_min"],
        "post_2024_total_return": post_2024 > 0,
    }
    return {
        "sharpe_uplift": float(uplift),
        "pass_checks": pass_checks,
        "pass_all": bool(all(pass_checks.values())),
        "strong_checks": strong_checks,
        "strong_all": bool(all(strong_checks.values())),
    }


def pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    close = {}
    for asset, symbol in SYMBOLS.items():
        print(f"fetching {symbol}", flush=True)
        close[asset] = fetch_daily(symbol)
    prices = pd.concat(close, axis=1).dropna()

    brrk = load_brrk_returns()
    eval_start = max(prices.index.min(), brrk.index.min())
    eval_end = min(prices.index.max(), brrk.index.max())

    target, trends = build_equal_active_tsmom(prices)
    tsmom_ret, held, turnover, gross_exposure = run_from_target(prices, target, eval_start, eval_end)

    aligned = pd.concat([tsmom_ret.rename("tsmom"), brrk.rename("brrk")], axis=1).dropna()
    tsmom_ret = aligned.tsmom
    brrk_ret = aligned.brrk

    # Fixed 50/50 sleeve blend. This is a diversification diagnostic, not a new optimized allocator.
    combo_ret = 0.5 * brrk_ret + 0.5 * tsmom_ret

    tsmom_m = metrics_from_returns(tsmom_ret)
    brrk_m = metrics_from_returns(brrk_ret)
    combo_m = metrics_from_returns(combo_ret)
    corr = correlation_diagnostics(tsmom_ret, brrk_ret)

    sleeve_returns = {}
    sleeve_metrics = {}
    for asset in ASSETS:
        sleeve_target = pd.DataFrame(0.0, index=prices.index, columns=ASSETS)
        sleeve_target[asset] = (trends[asset] > 0).astype(float)
        ret, _, _, _ = run_from_target(prices, sleeve_target, eval_start, eval_end)
        ret = ret.reindex(aligned.index)
        sleeve_returns[asset] = ret
        sleeve_metrics[asset] = metrics_from_returns(ret)

    active_count = (held.abs() > 1e-12).sum(axis=1)
    active_distribution = {
        str(int(k)): int(v) for k, v in active_count.value_counts().sort_index().items()
    }
    annual = {
        "brrk": annual_returns(brrk_ret),
        "tsmom": annual_returns(tsmom_ret),
        "blend_50_50": annual_returns(combo_ret),
    }
    post_2024_ret = float((1.0 + tsmom_ret.loc["2025-01-01":]).prod() - 1.0)

    gate = evaluate_gate(tsmom_m, brrk_m, combo_m, corr, post_2024_ret)
    funding = funding_sensitivity(tsmom_ret, held)

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "PRETEST_ONLY_NO_TRADING_CHANGE",
        "frozen_method": {
            "assets": list(ASSETS),
            "signal": "existing own-price trend_score using 20/60/120/240d horizons and frozen FAST_WEIGHTS",
            "eligibility": "trend_score > 0 => long; otherwise flat",
            "allocation": "equal weight across active assets; zero active => cash",
            "relative_ranking": False,
            "leverage": False,
            "max_gross": 1.0,
            "execution": "target at t, held t+1",
            "l1_band": BAND,
            "cost_bps_per_absolute_weight_change": COST_BPS,
            "parameter_search": False,
            "blend": "fixed 50/50 BRRK0011 + TSMOM return blend, diagnostic only",
        },
        "pass_criteria": PASS_CRITERIA,
        "strong_criteria": STRONG_CRITERIA,
        "metrics": {
            "brrk0011": brrk_m,
            "tsmom_equal_active": tsmom_m,
            "blend_50_50": combo_m,
        },
        "correlation": corr,
        "sleeves": sleeve_metrics,
        "sleeve_correlation": sleeve_matrix(sleeve_returns),
        "exposure": {
            "avg_gross": float(gross_exposure.reindex(aligned.index).mean()),
            "max_gross": float(gross_exposure.reindex(aligned.index).max()),
            "cash_day_fraction": float((gross_exposure.reindex(aligned.index) < 1e-12).mean()),
            "total_turnover": float(turnover.reindex(aligned.index).sum()),
            "active_asset_count_days": active_distribution,
        },
        "annual_returns": annual,
        "post_2024_tsmom_total_return": post_2024_ret,
        "funding_sensitivity": funding,
        "gate": gate,
    }

    (RESULTS_DIR / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    pd.DataFrame({"BRRK0011": brrk_ret, "TSMOM": tsmom_ret, "BLEND_50_50": combo_ret}).to_csv(
        RESULTS_DIR / "daily_returns.csv", index_label="date"
    )
    held.reindex(aligned.index).to_csv(RESULTS_DIR / "tsmom_held_weights.csv", index_label="date")

    rows = [
        "# TSMOM-0027 Pretest",
        "",
        "**PRETEST ONLY / NO TRADING CHANGE / NO PARAMETER SEARCH.**",
        "",
        "| Strategy | CAGR | MDD | Ann vol | Sharpe | Calmar |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, m in [("BRRK-0011", brrk_m), ("Equal-active TSMOM", tsmom_m), ("50/50 diagnostic blend", combo_m)]:
        rows.append(
            f"| {label} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {pct(m['ann_vol'])} | {m['sharpe']:.3f} | {m['calmar']:.3f} |"
        )
    rows += [
        "",
        "## Diversification",
        "",
        f"- Daily corr(TSMOM, BRRK): **{corr['daily_full']:.3f}**",
        f"- Corr while BRRK is in drawdown: **{corr['daily_when_brrk_in_drawdown']:.3f}**",
        f"- Monthly corr: **{corr['monthly_full']:.3f}**",
        f"- 50/50 Sharpe uplift: **{gate['sharpe_uplift']:+.3f}**",
        f"- Pass-all: **{gate['pass_all']}**",
        f"- Strong-pass-all: **{gate['strong_all']}**",
        "",
        "## Exposure",
        "",
        f"- Average gross: **{report['exposure']['avg_gross']:.3f}x**",
        f"- Maximum gross: **{report['exposure']['max_gross']:.3f}x**",
        f"- Cash-day fraction: **{pct(report['exposure']['cash_day_fraction'])}**",
        f"- Total turnover: **{report['exposure']['total_turnover']:.2f}**",
        "",
        "## Funding sensitivity (2023-06-18 to 2026-07-31)",
        "",
        "This section changes only funding accounting. It is not a full strict-router fee/slippage simulation.",
        "",
        "| Scenario | CAGR | MDD | Sharpe | Calmar |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, key in [
        ("Price only", "price_only"),
        ("Hyperliquid all-perp", "hyperliquid_all_perp"),
        ("BTC spot; ETH/SOL/BNB HL-perp funding sensitivity", "btc_spot_others_hyperliquid_perp_funding_sensitivity"),
    ]:
        m = funding[key]
        rows.append(f"| {label} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['sharpe']:.3f} | {m['calmar']:.3f} |")

    (RESULTS_DIR / "RESULT.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
