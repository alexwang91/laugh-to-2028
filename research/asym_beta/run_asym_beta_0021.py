from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROOT = RESEARCH.parent
RESULTS = RESEARCH / "results"
for path in (RESEARCH, RESEARCH / "regime_kelly", RESEARCH / "hybrid_meta", RESEARCH / "risk_metric_fix", HERE):
    sys.path.insert(0, str(path))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from features_no_dominance import build_features_no_dominance
from regime_model_vb_nd import fit_variational_regime_model_nd
from walkforward_v1_meta import (
    END,
    START,
    RISK_BUDGET,
    build_benchmark_v1,
    fit_state_v1_distribution,
    sample_v1_paths,
)
from corrected_risk import choose_scale_corrected, path_tail_risk_corrected
from raw_state_risk import raw_filtered_posterior, fit_raw_v1_distribution, bad_state_probability

EXPERIMENT_ID = "ASYM-BETA-0021"
ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
COST_BPS = 5.0
BAND = 0.05
TOTAL_SCALE_CAP = 1.50
EXTRA_SCALE_CAP = 0.50
COMMON_START = pd.Timestamp("2023-06-18")
COMMON_END = pd.Timestamp("2026-07-31")
CORE_WEIGHT_PATH = RESULTS / "pit_disp_0015" / "daily_weights.csv"
ROUTER_0005_PATH = RESULTS / "router_pnl_0005" / "daily_equity.csv"
FUNDING_PATH = RESULTS / "funding_pnl_0003" / "block_asset_funding_attribution.csv"
OUTPUT = RESULTS / "asym_beta_0021"


def safe_total_scale(paths: np.ndarray, budget: float, upper: float = TOTAL_SCALE_CAP) -> dict:
    """Largest total V1 scale in [0, upper] satisfying existing CVaR/CDaR budget."""
    cvar_upper, cdar_upper = path_tail_risk_corrected(paths, upper)
    if cvar_upper <= budget and cdar_upper <= budget:
        return {"safe_total_scale": float(upper), "cvar95": float(cvar_upper), "cdar95": float(cdar_upper)}
    lo, hi = 0.0, float(upper)
    for _ in range(32):
        mid = 0.5 * (lo + hi)
        cvar, cdar = path_tail_risk_corrected(paths, mid)
        if cvar <= budget and cdar <= budget:
            lo = mid
        else:
            hi = mid
    cvar, cdar = path_tail_risk_corrected(paths, lo)
    return {"safe_total_scale": float(lo), "cvar95": float(cvar), "cdar95": float(cdar)}


def extra_beta_rule(
    core_scale: float,
    btc_trend: float,
    p_bad: float,
    safe_total: float,
) -> dict:
    """
    ASYM-BETA-0021 authority structure.

    Extra beta exists only above an exactly full BRRK core. If BRRK has actively
    de-risked below 1x V1, the new sleeve has no authority to add exposure.
    """
    core_full = bool(np.isclose(core_scale, 1.0, rtol=0.0, atol=1e-10))
    trend_candidate = EXTRA_SCALE_CAP * max(float(btc_trend), 0.0)
    pbad_adjusted = trend_candidate * (1.0 - float(np.clip(p_bad, 0.0, 1.0)))
    risk_capacity = max(0.0, min(float(safe_total), TOTAL_SCALE_CAP) - 1.0)
    extra = min(EXTRA_SCALE_CAP, pbad_adjusted, risk_capacity) if core_full else 0.0
    total = float(core_scale + extra)
    return {
        "core_full_permission": core_full,
        "trend_candidate_extra": float(trend_candidate),
        "pbad_adjusted_extra": float(pbad_adjusted),
        "risk_extra_capacity": float(risk_capacity),
        "extra_scale": float(extra),
        "total_scale": total,
    }


def portfolio_returns(prices: pd.DataFrame, target_weights: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    held = target_weights.shift(1).fillna(0.0)
    asset_ret = prices.pct_change(fill_method=None).fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = held.abs().sum(axis=1)
    ret = (held * asset_ret).sum(axis=1) - turnover * COST_BPS / 10000.0
    return ret.astype(float), turnover.astype(float), gross.astype(float)


def metrics(ret: pd.Series, turnover: pd.Series | None = None, gross: pd.Series | None = None) -> dict:
    ret = ret.dropna().astype(float)
    nav = (1.0 + ret).cumprod()
    if ret.empty:
        raise ValueError("empty return series")
    elapsed_years = max((ret.index[-1] - ret.index[0]).days / 365.25, 1.0 / 365.25)
    cagr = float(nav.iloc[-1] ** (1.0 / elapsed_years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(ret.std(ddof=1))
    sharpe = float(ret.mean() / std * math.sqrt(365.0)) if std > 0 else None
    out = {
        "start": str(ret.index[0].date()),
        "end": str(ret.index[-1].date()),
        "observations": int(len(ret)),
        "final_multiple": float(nav.iloc[-1]),
        "final_10k": float(nav.iloc[-1] * 10000.0),
        "cagr": cagr,
        "max_drawdown": float(dd.min()),
        "ann_vol": float(std * math.sqrt(365.0)),
        "sharpe": sharpe,
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else None,
    }
    if turnover is not None:
        out["turnover"] = float(turnover.reindex(ret.index).fillna(0.0).sum())
    if gross is not None:
        out["avg_gross"] = float(gross.reindex(ret.index).mean())
        out["max_gross"] = float(gross.reindex(ret.index).max())
    return out


def monthly_capture(strategy_ret: pd.Series, btc_ret: pd.Series) -> dict:
    s = (1.0 + strategy_ret).resample("ME").prod() - 1.0
    b = (1.0 + btc_ret).resample("ME").prod() - 1.0
    x = pd.concat([s.rename("s"), b.rename("b")], axis=1).dropna()
    up = x[x["b"] > 0]
    down = x[x["b"] < 0]
    return {
        "upside_capture": float(up["s"].sum() / up["b"].sum()) if len(up) and up["b"].sum() != 0 else None,
        "downside_capture": float(down["s"].sum() / down["b"].sum()) if len(down) and down["b"].sum() != 0 else None,
        "up_months": int(len(up)),
        "down_months": int(len(down)),
    }


def load_frozen_weights() -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(CORE_WEIGHT_PATH, parse_dates=["date"]).set_index("date")
    v1 = frame[[f"V1_BASELINE__{a}" for a in ASSETS]].copy()
    v1.columns = list(ASSETS)
    core = frame[[f"BRRK0011_BASELINE__{a}" for a in ASSETS]].copy()
    core.columns = list(ASSETS)
    return v1.astype(float), core.astype(float)


def validate_core_weights(rebuilt: pd.DataFrame, frozen: pd.DataFrame) -> float:
    common = rebuilt.index.intersection(frozen.index)
    if common.empty:
        raise RuntimeError("No overlap with frozen BRRK0011 weights")
    error = float((rebuilt.loc[common, list(ASSETS)] - frozen.loc[common, list(ASSETS)]).abs().to_numpy().max())
    if error > 1e-5:
        raise RuntimeError(f"Corrected BRRK core reconstruction mismatch: max_abs_weight_error={error:.12g}")
    return error


def funding_rate_matrix() -> pd.DataFrame:
    frame = pd.read_csv(FUNDING_PATH, parse_dates=["block", "date"])
    frame = frame[frame["source"] == "HYPERLIQUID_COMMON"].copy()
    if frame.empty:
        raise RuntimeError("No HYPERLIQUID_COMMON funding attribution rows")
    wide = frame.pivot(index="block", columns="asset", values="rate").sort_index()
    missing = set(ASSETS) - set(wide.columns)
    if missing:
        raise RuntimeError(f"Missing Hyperliquid funding assets: {sorted(missing)}")
    return wide[list(ASSETS)].astype(float)


def funding_factors_for_weights(
    rates: pd.DataFrame,
    daily_weights: pd.DataFrame,
) -> pd.Series:
    block_dates = pd.DatetimeIndex(rates.index).tz_convert("UTC").tz_localize(None).normalize()
    missing = block_dates.difference(daily_weights.index)
    if len(missing):
        raise RuntimeError(f"Funding dates absent from weights: {missing[:5].tolist()}")
    block_weights = daily_weights.loc[block_dates, list(ASSETS)].copy()
    block_weights.index = rates.index
    block_return = (-block_weights * rates).sum(axis=1)
    if (1.0 + block_return <= 0).any():
        raise RuntimeError("Impossible funding block return <= -100%")
    date_index = pd.DatetimeIndex(rates.index).tz_convert("UTC").tz_localize(None).normalize()
    return (1.0 + block_return).groupby(date_index).prod().astype(float)


def combine_price_funding(price_ret: pd.Series, funding_factor: pd.Series) -> pd.Series:
    f = funding_factor.reindex(price_ret.index)
    if f.isna().any():
        raise RuntimeError(f"Missing funding factor on {f.index[f.isna()][:5].tolist()}")
    return ((1.0 + price_ret) * f - 1.0).astype(float)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    bt.START_DATE = START
    bt.END_DATE = str(END.date())

    prices = pd.concat(
        {asset: bt.fetch_daily(asset + "USDT") for asset in ASSETS},
        axis=1,
    ).sort_index().loc[:END].dropna()
    prices.index = pd.DatetimeIndex(prices.index).normalize()

    features = build_features_no_dominance(prices, cfg)
    v1_raw = build_benchmark_v1(prices)
    v1_banded = bt.apply_band(v1_raw, BAND)
    v1_ret, _, _ = portfolio_returns(prices, v1_banded)

    decision_dates: list[pd.Timestamp] = []
    for dt in features.dropna().index:
        if dt <= END and len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("No eligible ASYM-BETA-0021 decisions")

    core_scale = pd.Series(np.nan, index=prices.index, dtype=float)
    total_scale = pd.Series(np.nan, index=prices.index, dtype=float)
    decision_rows: list[dict] = []

    for j, dt in enumerate(decision_dates):
        train = features.loc[:dt]
        fit = fit_variational_regime_model_nd(train, cfg, n_factors=4)
        semantic_post = fit.filtered_posterior(features.loc[:dt]).iloc[-1]
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
        cscale = float(1.0 - p_riskoff * (1.0 - float(meta["scale"])))

        raw_post = raw_filtered_posterior(fit, features.loc[:dt])
        raw_dist = fit_raw_v1_distribution(v1_ret.loc[:dt], train, fit, cfg)
        p_bad = bad_state_probability(raw_post, raw_dist)

        safe = safe_total_scale(semantic_paths, RISK_BUDGET, TOTAL_SCALE_CAP)
        btc_trend = float(features.loc[dt, "btc_trend"])
        rule = extra_beta_rule(cscale, btc_trend, p_bad, safe["safe_total_scale"])

        next_dt = decision_dates[j + 1] if j + 1 < len(decision_dates) else END + pd.Timedelta(days=1)
        active = prices.loc[dt:next_dt - pd.Timedelta(days=1)].index
        core_scale.loc[active] = cscale
        total_scale.loc[active] = rule["total_scale"]

        decision_rows.append({
            "date": str(dt.date()),
            "btc_trend": btc_trend,
            "p_riskoff": p_riskoff,
            "p_bad": p_bad,
            "core_meta_scale": float(meta["scale"]),
            "core_scale": cscale,
            "full_scale_cvar95": float(meta["full_scale_cvar95"]),
            "full_scale_cdar95": float(meta["full_scale_cdar95"]),
            "safe_total_scale": float(safe["safe_total_scale"]),
            "safe_total_cvar95": float(safe["cvar95"]),
            "safe_total_cdar95": float(safe["cdar95"]),
            **rule,
            "hmm_converged": bool(fit.converged),
            "pca_variance": float(fit.pca.explained_variance_ratio_.sum()),
        })
        print(
            dt.date(),
            "core", round(cscale, 4),
            "trend", round(btc_trend, 4),
            "pbad", round(p_bad, 4),
            "safe", round(safe["safe_total_scale"], 4),
            "extra", round(rule["extra_scale"], 4),
            "total", round(rule["total_scale"], 4),
            flush=True,
        )

    core_scale = core_scale.ffill().fillna(1.0)
    total_scale = total_scale.ffill().fillna(core_scale)

    core_weights = bt.apply_band(v1_raw.mul(core_scale, axis=0), BAND)
    total_weights = bt.apply_band(v1_raw.mul(total_scale, axis=0), BAND)

    _, frozen_core = load_frozen_weights()
    core_weight_error = validate_core_weights(core_weights, frozen_core)

    eval_start = decision_dates[0] + pd.Timedelta(days=1)
    core_price_ret, core_turn, core_gross = portfolio_returns(prices, core_weights)
    total_price_ret, total_turn, total_gross = portfolio_returns(prices, total_weights)
    btc_ret = prices["BTC"].pct_change(fill_method=None).fillna(0.0)

    core_price_ret = core_price_ret.loc[eval_start:END]
    total_price_ret = total_price_ret.loc[eval_start:END]
    core_turn = core_turn.loc[eval_start:END]
    total_turn = total_turn.loc[eval_start:END]
    core_gross = core_gross.loc[eval_start:END]
    total_gross = total_gross.loc[eval_start:END]
    btc_ret = btc_ret.loc[eval_start:END]

    rates = funding_rate_matrix()
    common_index = total_price_ret.loc[COMMON_START:COMMON_END].index
    core_common = core_price_ret.reindex(common_index)
    total_common = total_price_ret.reindex(common_index)

    core_perp_weights = core_weights.copy()
    core_perp_weights["BTC"] = 0.0

    strict_total_perp = total_weights.copy()
    strict_total_perp["BTC"] = (total_weights["BTC"] - core_weights["BTC"]).clip(lower=0.0)

    all_perp_total = total_weights.copy()

    core_funding_factor = funding_factors_for_weights(rates, core_perp_weights)
    strict_total_funding_factor = funding_factors_for_weights(rates, strict_total_perp)
    all_perp_total_factor = funding_factors_for_weights(rates, all_perp_total)

    core_strict_ret = combine_price_funding(core_common, core_funding_factor)
    total_strict_ret = combine_price_funding(total_common, strict_total_funding_factor)
    total_all_perp_ret = combine_price_funding(total_common, all_perp_total_factor)

    persisted_0005 = pd.read_csv(ROUTER_0005_PATH, parse_dates=["date"]).set_index("date")
    persisted_nav = persisted_0005["STRICT_VERIFIED_SPOT"].reindex(common_index)
    rebuilt_nav = 10000.0 * (1.0 + core_strict_ret).cumprod()
    router_core_error = float((rebuilt_nav - persisted_nav).abs().max())
    if not np.isfinite(router_core_error) or router_core_error > 0.05:
        raise RuntimeError(
            f"ROUTER-PNL-0005 strict-core reconstruction mismatch: max_abs_equity_error={router_core_error:.8f}"
        )

    decisions = pd.DataFrame(decision_rows)
    decisions.to_csv(OUTPUT / "decisions.csv", index=False)

    daily = pd.DataFrame({
        "CORE_PRICE_ONLY": core_price_ret,
        "ASYM_BETA_PRICE_ONLY": total_price_ret,
    })
    daily.loc[common_index, "CORE_STRICT_ROUTER_FUNDING"] = core_strict_ret
    daily.loc[common_index, "ASYM_BETA_STRICT_ROUTER_FUNDING"] = total_strict_ret
    daily.loc[common_index, "ASYM_BETA_ALL_PERP_STRESS"] = total_all_perp_ret
    daily.to_csv(OUTPUT / "daily_returns.csv", index_label="date")

    price_metrics = {
        "BRRK0011_CORE": metrics(core_price_ret, core_turn, core_gross),
        "ASYM_BETA_0021": metrics(total_price_ret, total_turn, total_gross),
    }
    funding_metrics = {
        "BRRK0011_CORE_STRICT_ROUTER": metrics(
            core_strict_ret,
            core_turn.reindex(common_index),
            core_gross.reindex(common_index),
        ),
        "ASYM_BETA_0021_STRICT_ROUTER": metrics(
            total_strict_ret,
            total_turn.reindex(common_index),
            total_gross.reindex(common_index),
        ),
        "ASYM_BETA_0021_ALL_PERP_STRESS": metrics(
            total_all_perp_ret,
            total_turn.reindex(common_index),
            total_gross.reindex(common_index),
        ),
    }
    capture = {
        "BRRK0011_CORE": monthly_capture(core_price_ret, btc_ret),
        "ASYM_BETA_0021": monthly_capture(total_price_ret, btc_ret),
    }

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "promotion_evidence": False,
        "design_note": (
            "Architecture was specified after prior BRRK results on this same historical window. "
            "This run can reject the structure or qualify it for separately registered forward shadow only."
        ),
        "frozen_elements": {
            "BRRK0011_core": True,
            "V1_asset_selection_and_weights": True,
            "trend_horizons_and_weights": True,
            "state_model": True,
            "p_bad_definition": "exact migrated BRRK-0009 raw-state P(mu<0) diagnostic",
            "risk_budget": RISK_BUDGET,
            "cost_bps_per_absolute_weight_change": COST_BPS,
        },
        "only_structural_change": (
            "Allow a uniform 0..0.5 V1-scale extra-beta sleeve above an exactly full BRRK core. "
            "The sleeve is generated by positive BTC trend and may only be reduced by p_bad and the existing "
            "20-day CVaR95/CDaR95 budget. No asset-specific tilt is allowed."
        ),
        "gross_cap": TOTAL_SCALE_CAP,
        "common_funding_window": {
            "start": str(COMMON_START.date()),
            "end": str(COMMON_END.date()),
            "router_rule": (
                "BTC core spot; ETH/SOL/BNB/XRP core perp; every incremental exposure above core perp. "
                "No historical spot fee/basis/slippage series is invented."
            ),
        },
        "validation": {
            "core_weight_max_abs_error_vs_persisted_BRRK0011": core_weight_error,
            "strict_core_equity_max_abs_error_vs_ROUTER_PNL_0005": router_core_error,
        },
        "diagnostics": {
            "decision_count": int(len(decisions)),
            "extra_active_decisions": int((decisions["extra_scale"] > 1e-12).sum()),
            "mean_extra_scale": float(decisions["extra_scale"].mean()),
            "max_extra_scale": float(decisions["extra_scale"].max()),
            "mean_total_scale": float(decisions["total_scale"].mean()),
            "max_total_scale": float(decisions["total_scale"].max()),
            "mean_p_bad": float(decisions["p_bad"].mean()),
            "mean_safe_total_scale": float(decisions["safe_total_scale"].mean()),
            "hmm_convergence_rate": float(decisions["hmm_converged"].mean()),
        },
        "price_only_metrics": price_metrics,
        "funding_aware_metrics": funding_metrics,
        "capture": capture,
        "decision_rule_after_result": (
            "Do not tune 0.5, p_bad, risk budget, trend definition or gross cap on this window. "
            "Reject if funding-aware economics or left-tail risk are materially worse. "
            "If economically promising, the only authorized continuation is a separately registered forward-shadow test."
        ),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== ASYM_BETA_0021_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
