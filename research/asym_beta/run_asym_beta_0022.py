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
from walkforward_v1_meta import (
    END,
    START,
    RISK_BUDGET,
    build_benchmark_v1,
    fit_state_v1_distribution,
    sample_v1_paths,
)
from corrected_risk import choose_scale_corrected
from raw_state_risk import raw_filtered_posterior, fit_raw_v1_distribution, bad_state_probability
from run_asym_beta_0021 import (
    ASSETS,
    BAND,
    COMMON_END,
    COMMON_START,
    COST_BPS,
    funding_factors_for_weights,
    funding_rate_matrix,
    expected_router_0005_equity_from_persisted_inputs,
    load_frozen_weights,
    metrics,
    monthly_capture,
    portfolio_returns,
    validate_core_weights,
    combine_price_funding,
)

EXPERIMENT_ID = "ASYM-BETA-0022-SEMIVOL"
GROSS_CAP = 1.50
EXTRA_CAP = 0.50
DOWNSIDE_ANCHOR = 0.45
DOWNSIDE_WINDOW = 30
OUTPUT = RESULTS / "asym_beta_0022"


def downside_semivolatility(price: pd.Series, window: int = DOWNSIDE_WINDOW) -> pd.Series:
    """Annualized lower-partial-moment semivolatility about zero log return."""
    log_ret = np.log(price).diff()
    downside = log_ret.clip(upper=0.0)
    return np.sqrt((downside ** 2).rolling(window, min_periods=window).mean()) * math.sqrt(365.0)


def extra_beta_rule(core_scale: float, btc_trend: float, p_bad: float, downside_semivol: float) -> dict:
    core_full = bool(np.isclose(float(core_scale), 1.0, rtol=0.0, atol=1e-10))
    trend_candidate = EXTRA_CAP * max(float(btc_trend), 0.0)
    pbad_adjusted = trend_candidate * (1.0 - float(np.clip(p_bad, 0.0, 1.0)))
    if not np.isfinite(downside_semivol) or downside_semivol < 0:
        downside_scaler = 0.0
    elif downside_semivol == 0.0:
        downside_scaler = 1.0
    else:
        downside_scaler = min(1.0, DOWNSIDE_ANCHOR / float(downside_semivol))
    extra = pbad_adjusted * downside_scaler if core_full else 0.0
    extra = float(np.clip(extra, 0.0, EXTRA_CAP))
    total = float(min(GROSS_CAP, float(core_scale) + extra))
    return {
        "core_full_permission": core_full,
        "trend_candidate_extra": float(trend_candidate),
        "pbad_adjusted_extra": float(pbad_adjusted),
        "downside_semivol30": float(downside_semivol) if np.isfinite(downside_semivol) else None,
        "downside_scaler": float(downside_scaler),
        "extra_scale": extra,
        "total_scale": total,
    }


def annual_returns(ret: pd.Series) -> dict:
    ret = ret.dropna()
    return {
        str(int(year)): float((1.0 + values).prod() - 1.0)
        for year, values in ret.groupby(ret.index.year)
    }


def subperiod_metrics(ret: pd.Series, turnover: pd.Series, gross: pd.Series) -> dict:
    out = {}
    for start in ("2024-01-01", "2025-01-01", "2026-01-01"):
        idx = ret.index >= pd.Timestamp(start)
        if idx.any():
            out[start] = metrics(ret.loc[idx], turnover.loc[idx], gross.loc[idx])
    return out


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
    btc_downside_semivol = downside_semivolatility(prices["BTC"])

    decision_dates: list[pd.Timestamp] = []
    for dt in features.dropna().index:
        if dt <= END and len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("No eligible ASYM-BETA-0022 decisions")

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

        btc_trend = float(features.loc[dt, "btc_trend"])
        semivol = float(btc_downside_semivol.loc[dt])
        rule = extra_beta_rule(cscale, btc_trend, p_bad, semivol)

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
            **rule,
            "hmm_converged": bool(fit.converged),
            "pca_variance": float(fit.pca.explained_variance_ratio_.sum()),
        })
        print(
            dt.date(),
            "core", round(cscale, 4),
            "trend", round(btc_trend, 4),
            "pbad", round(p_bad, 4),
            "dsv", round(semivol, 4),
            "dscale", round(rule["downside_scaler"], 4),
            "extra", round(rule["extra_scale"], 4),
            "total", round(rule["total_scale"], 4),
            flush=True,
        )

    core_scale = core_scale.ffill().fillna(1.0)
    total_scale = total_scale.ffill().fillna(core_scale)

    core_weights = bt.apply_band(v1_raw.mul(core_scale, axis=0), BAND)
    total_weights = bt.apply_band(v1_raw.mul(total_scale, axis=0), BAND)
    core_held = core_weights.shift(1).fillna(0.0)
    total_held = total_weights.shift(1).fillna(0.0)

    _, frozen_core = load_frozen_weights()
    core_weight_error = validate_core_weights(core_held, frozen_core)
    max_gross_all = float(total_held.abs().sum(axis=1).max())
    if max_gross_all > GROSS_CAP + 1e-9:
        raise RuntimeError(f"0022 gross cap violation: {max_gross_all:.12f}")

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

    core_perp = core_held.copy()
    core_perp["BTC"] = 0.0

    strict_total_perp = total_held.copy()
    strict_total_perp["BTC"] = (total_held["BTC"] - core_held["BTC"]).clip(lower=0.0)
    all_perp_total = total_held.copy()

    core_funding_factor = funding_factors_for_weights(rates, core_perp)
    strict_total_factor = funding_factors_for_weights(rates, strict_total_perp)
    all_perp_factor = funding_factors_for_weights(rates, all_perp_total)

    core_strict_ret = combine_price_funding(core_common, core_funding_factor)
    total_strict_ret = combine_price_funding(total_common, strict_total_factor)
    total_all_perp_ret = combine_price_funding(total_common, all_perp_factor)

    persisted_nav = expected_router_0005_equity_from_persisted_inputs().reindex(common_index)
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
        "ASYM_BETA_0022_PRICE_ONLY": total_price_ret,
    })
    daily.loc[common_index, "CORE_STRICT_ROUTER_FUNDING"] = core_strict_ret
    daily.loc[common_index, "ASYM_BETA_0022_STRICT_ROUTER_FUNDING"] = total_strict_ret
    daily.loc[common_index, "ASYM_BETA_0022_ALL_PERP_STRESS"] = total_all_perp_ret
    daily.to_csv(OUTPUT / "daily_returns.csv", index_label="date")

    price_metrics = {
        "BRRK0011_CORE": metrics(core_price_ret, core_turn, core_gross),
        "ASYM_BETA_0022": metrics(total_price_ret, total_turn, total_gross),
    }
    funding_metrics = {
        "BRRK0011_CORE_STRICT_ROUTER": metrics(core_strict_ret, core_turn.reindex(common_index), core_gross.reindex(common_index)),
        "ASYM_BETA_0022_STRICT_ROUTER": metrics(total_strict_ret, total_turn.reindex(common_index), total_gross.reindex(common_index)),
        "ASYM_BETA_0022_ALL_PERP_STRESS": metrics(total_all_perp_ret, total_turn.reindex(common_index), total_gross.reindex(common_index)),
    }

    price_subperiods = {
        "BRRK0011_CORE": subperiod_metrics(core_price_ret, core_turn, core_gross),
        "ASYM_BETA_0022": subperiod_metrics(total_price_ret, total_turn, total_gross),
    }
    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "promotion_evidence": False,
        "design_note": "Same-window architecture test; cannot establish untouched OOS validity or production promotion.",
        "only_structural_change_vs_0021": "Replace absolute total CVaR/CDaR overlay veto with a 30-day BTC downside-semivol scaler using the frozen 45% annualized anchor, applied only to extra beta.",
        "validation": {
            "core_weight_max_abs_error_vs_persisted_BRRK0011": core_weight_error,
            "strict_core_equity_max_abs_error_vs_ROUTER_PNL_0005": router_core_error,
            "max_final_held_gross": max_gross_all,
        },
        "diagnostics": {
            "decision_count": int(len(decisions)),
            "extra_active_decisions": int((decisions["extra_scale"] > 1e-12).sum()),
            "extra_active_fraction": float((decisions["extra_scale"] > 1e-12).mean()),
            "mean_extra_scale_all_decisions": float(decisions["extra_scale"].mean()),
            "mean_extra_scale_when_active": float(decisions.loc[decisions["extra_scale"] > 1e-12, "extra_scale"].mean()) if (decisions["extra_scale"] > 1e-12).any() else 0.0,
            "max_extra_scale": float(decisions["extra_scale"].max()),
            "mean_downside_semivol30": float(decisions["downside_semivol30"].mean()),
            "mean_downside_scaler": float(decisions["downside_scaler"].mean()),
            "fraction_downside_scaler_below_1": float((decisions["downside_scaler"] < 1.0 - 1e-12).mean()),
            "mean_p_bad": float(decisions["p_bad"].mean()),
            "hmm_convergence_rate": float(decisions["hmm_converged"].mean())
        },
        "price_only_metrics": price_metrics,
        "funding_aware_metrics": funding_metrics,
        "capture": {
            "BRRK0011_CORE": monthly_capture(core_price_ret, btc_ret),
            "ASYM_BETA_0022": monthly_capture(total_price_ret, btc_ret)
        },
        "annual_returns": {
            "BRRK0011_CORE": annual_returns(core_price_ret),
            "ASYM_BETA_0022": annual_returns(total_price_ret),
            "BRRK0011_CORE_STRICT_ROUTER": annual_returns(core_strict_ret),
            "ASYM_BETA_0022_STRICT_ROUTER": annual_returns(total_strict_ret)
        },
        "price_only_subperiods": price_subperiods,
        "stopping_rule": "Do not tune downside window, 45% anchor, 0.50 extra cap, 1.50 gross cap, p_bad or trend definition on this historical window. Reject or qualify only for a separately preregistered forward-shadow test."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== ASYM_BETA_0022_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
