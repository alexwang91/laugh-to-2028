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
from raw_state_risk import fit_raw_v1_distribution
from run_audit_0023_latency import raw_posterior_path, daily_pbad
from run_asym_beta_0021 import (
    ASSETS,
    BAND,
    COMMON_END,
    COMMON_START,
    COST_BPS,
    combine_price_funding,
    expected_router_0005_equity_from_persisted_inputs,
    funding_factors_for_weights,
    funding_rate_matrix,
    load_frozen_weights,
    metrics,
    monthly_capture,
    portfolio_returns,
    validate_core_weights,
)
from run_asym_beta_0022 import downside_semivolatility, extra_beta_rule, annual_returns

EXPERIMENT_ID = "ASYM-BETA-0024-DAILY-CAP"
OUTPUT = RESULTS / "asym_beta_0024"
PERSISTED_0022 = RESULTS / "asym_beta_0022" / "summary.json"
GROSS_CAP = 1.50


def daily_cap(monthly_approved_extra: float, daily_implied_extra: float) -> float:
    return float(max(0.0, min(float(monthly_approved_extra), float(daily_implied_extra))))


def drawdown_info(ret: pd.Series) -> dict:
    r = ret.dropna().astype(float)
    nav = (1.0 + r).cumprod()
    peak = nav.cummax()
    dd = nav / peak - 1.0
    trough = dd.idxmin()
    peak_date = nav.loc[:trough].idxmax()
    peak_nav = float(nav.loc[peak_date])
    recovery = nav.loc[trough:][nav.loc[trough:] >= peak_nav]
    return {
        "peak": str(peak_date.date()),
        "trough": str(trough.date()),
        "mdd": float(dd.loc[trough]),
        "recovery": str(recovery.index[0].date()) if len(recovery) else None,
    }


def monthly_period_return(ret: pd.Series, month: str) -> float:
    p = pd.Period(month, freq="M")
    x = ret[(ret.index.year == p.year) & (ret.index.month == p.month)].dropna()
    return float((1.0 + x).prod() - 1.0) if len(x) else float("nan")


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
    btc_downside = downside_semivolatility(prices["BTC"])

    decision_dates: list[pd.Timestamp] = []
    for dt in features.dropna().index:
        if dt <= END and len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("No eligible ASYM-BETA-0024 decisions")

    core_scale = pd.Series(np.nan, index=prices.index, dtype=float)
    monthly_0022_scale = pd.Series(np.nan, index=prices.index, dtype=float)
    daily_cap_scale = pd.Series(np.nan, index=prices.index, dtype=float)
    daily_diag_rows: list[dict] = []
    monthly_rows: list[dict] = []

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
        cscale = float(1.0 - p_riskoff * (1.0 - float(meta["scale"])))

        frozen_raw_dist = fit_raw_v1_distribution(v1_ret.loc[:dt], train, fit, cfg)
        raw_path = raw_posterior_path(fit, features.loc[:interval_end])
        pbad_path = daily_pbad(raw_path, frozen_raw_dist)
        interval_index = features.loc[dt:interval_end].dropna().index.intersection(raw_path.index)
        if len(interval_index) == 0:
            continue

        monthly_rule = extra_beta_rule(
            cscale,
            float(features.loc[dt, "btc_trend"]),
            float(pbad_path.loc[dt]),
            float(btc_downside.loc[dt]),
        )
        monthly_extra = float(monthly_rule["extra_scale"])
        monthly_total = float(min(GROSS_CAP, cscale + monthly_extra))

        for day in interval_index:
            daily_rule = extra_beta_rule(
                cscale,
                float(features.loc[day, "btc_trend"]),
                float(pbad_path.loc[day]),
                float(btc_downside.loc[day]),
            )
            implied = float(daily_rule["extra_scale"])
            actual_extra = daily_cap(monthly_extra, implied)
            actual_total = float(min(GROSS_CAP, cscale + actual_extra))
            core_scale.loc[day] = cscale
            monthly_0022_scale.loc[day] = monthly_total
            daily_cap_scale.loc[day] = actual_total
            daily_diag_rows.append({
                "date": day,
                "refit_date": dt,
                "monthly_core_scale": cscale,
                "monthly_approved_extra": monthly_extra,
                "daily_implied_extra": implied,
                "daily_actual_extra": actual_extra,
                "daily_cap_binding": bool(actual_extra < monthly_extra - 1e-12),
                "daily_reduction_vs_monthly": float(monthly_extra - actual_extra),
                "daily_total_scale": actual_total,
                "daily_btc_trend": float(features.loc[day, "btc_trend"]),
                "daily_p_bad": float(pbad_path.loc[day]),
                "daily_downside_semivol30": float(btc_downside.loc[day]),
                "daily_downside_scaler": float(daily_rule["downside_scaler"]),
            })

        interval_diag = pd.DataFrame([x for x in daily_diag_rows if x["refit_date"] == dt])
        monthly_rows.append({
            "refit_date": str(dt.date()),
            "monthly_core_scale": cscale,
            "monthly_approved_extra": monthly_extra,
            "monthly_total_scale": monthly_total,
            "days": int(len(interval_diag)),
            "binding_days": int(interval_diag["daily_cap_binding"].sum()),
            "binding_fraction": float(interval_diag["daily_cap_binding"].mean()),
            "mean_actual_extra": float(interval_diag["daily_actual_extra"].mean()),
            "min_actual_extra": float(interval_diag["daily_actual_extra"].min()),
            "mean_reduction": float(interval_diag["daily_reduction_vs_monthly"].mean()),
            "max_reduction": float(interval_diag["daily_reduction_vs_monthly"].max()),
        })
        print(
            dt.date(),
            "approved", round(monthly_extra, 4),
            "bind", int(interval_diag["daily_cap_binding"].sum()),
            "mean_actual", round(float(interval_diag["daily_actual_extra"].mean()), 4),
            flush=True,
        )

    core_scale = core_scale.ffill().fillna(1.0)
    monthly_0022_scale = monthly_0022_scale.ffill().fillna(core_scale)
    daily_cap_scale = daily_cap_scale.ffill().fillna(core_scale)

    core_weights = bt.apply_band(v1_raw.mul(core_scale, axis=0), BAND)
    monthly_weights = bt.apply_band(v1_raw.mul(monthly_0022_scale, axis=0), BAND)
    daily_weights = bt.apply_band(v1_raw.mul(daily_cap_scale, axis=0), BAND)
    core_held = core_weights.shift(1).fillna(0.0)
    monthly_held = monthly_weights.shift(1).fillna(0.0)
    daily_held = daily_weights.shift(1).fillna(0.0)

    _, frozen_core = load_frozen_weights()
    core_weight_error = validate_core_weights(core_held, frozen_core)
    max_gross = float(daily_held.abs().sum(axis=1).max())
    if max_gross > GROSS_CAP + 1e-9:
        raise RuntimeError(f"0024 gross cap violation: {max_gross:.12f}")

    eval_start = decision_dates[0] + pd.Timedelta(days=1)
    core_ret, core_turn, core_gross = portfolio_returns(prices, core_weights)
    monthly_ret, monthly_turn, monthly_gross = portfolio_returns(prices, monthly_weights)
    daily_ret, daily_turn, daily_gross = portfolio_returns(prices, daily_weights)
    btc_ret = prices["BTC"].pct_change(fill_method=None).fillna(0.0)

    core_ret = core_ret.loc[eval_start:END]
    monthly_ret = monthly_ret.loc[eval_start:END]
    daily_ret = daily_ret.loc[eval_start:END]
    core_turn = core_turn.loc[eval_start:END]
    monthly_turn = monthly_turn.loc[eval_start:END]
    daily_turn = daily_turn.loc[eval_start:END]
    core_gross = core_gross.loc[eval_start:END]
    monthly_gross = monthly_gross.loc[eval_start:END]
    daily_gross = daily_gross.loc[eval_start:END]
    btc_ret = btc_ret.loc[eval_start:END]

    persisted_0022 = json.loads(PERSISTED_0022.read_text(encoding="utf-8"))
    monthly_price_final = metrics(monthly_ret, monthly_turn, monthly_gross)["final_10k"]
    price_0022_error = abs(monthly_price_final - float(persisted_0022["price_only_metrics"]["ASYM_BETA_0022"]["final_10k"]))
    if price_0022_error > 0.05:
        raise RuntimeError(f"0022 price reconstruction mismatch: ${price_0022_error:.8f}")

    rates = funding_rate_matrix()
    common_index = daily_ret.loc[COMMON_START:COMMON_END].index
    core_common = core_ret.reindex(common_index)
    monthly_common = monthly_ret.reindex(common_index)
    daily_common = daily_ret.reindex(common_index)

    def strict_perp_weights(total_held: pd.DataFrame) -> pd.DataFrame:
        out = total_held.copy()
        out["BTC"] = (total_held["BTC"] - core_held["BTC"]).clip(lower=0.0)
        return out

    core_perp = core_held.copy()
    core_perp["BTC"] = 0.0
    monthly_perp = strict_perp_weights(monthly_held)
    daily_perp = strict_perp_weights(daily_held)

    core_strict = combine_price_funding(core_common, funding_factors_for_weights(rates, core_perp))
    monthly_strict = combine_price_funding(monthly_common, funding_factors_for_weights(rates, monthly_perp))
    daily_strict = combine_price_funding(daily_common, funding_factors_for_weights(rates, daily_perp))
    daily_all_perp = combine_price_funding(daily_common, funding_factors_for_weights(rates, daily_held))

    persisted_nav = expected_router_0005_equity_from_persisted_inputs().reindex(common_index)
    rebuilt_core_nav = 10000.0 * (1.0 + core_strict).cumprod()
    router_core_error = float((rebuilt_core_nav - persisted_nav).abs().max())
    if router_core_error > 0.05:
        raise RuntimeError(f"ROUTER core reconstruction mismatch: ${router_core_error:.8f}")

    monthly_strict_final = metrics(monthly_strict, monthly_turn.reindex(common_index), monthly_gross.reindex(common_index))["final_10k"]
    strict_0022_error = abs(monthly_strict_final - float(persisted_0022["funding_aware_metrics"]["ASYM_BETA_0022_STRICT_ROUTER"]["final_10k"]))
    if strict_0022_error > 0.05:
        raise RuntimeError(f"0022 strict reconstruction mismatch: ${strict_0022_error:.8f}")

    diagnostics = pd.DataFrame(daily_diag_rows).set_index("date").sort_index()
    monthly_diagnostics = pd.DataFrame(monthly_rows)
    diagnostics.to_csv(OUTPUT / "daily_cap_diagnostics.csv", index_label="date")
    monthly_diagnostics.to_csv(OUTPUT / "monthly_cap_summary.csv", index=False)

    daily_out = pd.DataFrame({
        "CORE_PRICE_ONLY": core_ret,
        "ASYM_BETA_0022_PRICE_ONLY": monthly_ret,
        "ASYM_BETA_0024_PRICE_ONLY": daily_ret,
    })
    daily_out.loc[common_index, "CORE_STRICT_ROUTER"] = core_strict
    daily_out.loc[common_index, "ASYM_BETA_0022_STRICT_ROUTER"] = monthly_strict
    daily_out.loc[common_index, "ASYM_BETA_0024_STRICT_ROUTER"] = daily_strict
    daily_out.loc[common_index, "ASYM_BETA_0024_ALL_PERP_STRESS"] = daily_all_perp
    daily_out.to_csv(OUTPUT / "daily_returns.csv", index_label="date")

    price_metrics = {
        "BRRK0011_CORE": metrics(core_ret, core_turn, core_gross),
        "ASYM_BETA_0022_MONTHLY": metrics(monthly_ret, monthly_turn, monthly_gross),
        "ASYM_BETA_0024_DAILY_CAP": metrics(daily_ret, daily_turn, daily_gross),
    }
    funding_metrics = {
        "BRRK0011_CORE_STRICT_ROUTER": metrics(core_strict, core_turn.reindex(common_index), core_gross.reindex(common_index)),
        "ASYM_BETA_0022_STRICT_ROUTER": metrics(monthly_strict, monthly_turn.reindex(common_index), monthly_gross.reindex(common_index)),
        "ASYM_BETA_0024_STRICT_ROUTER": metrics(daily_strict, daily_turn.reindex(common_index), daily_gross.reindex(common_index)),
        "ASYM_BETA_0024_ALL_PERP_STRESS": metrics(daily_all_perp, daily_turn.reindex(common_index), daily_gross.reindex(common_index)),
    }

    binding = diagnostics[diagnostics["monthly_approved_extra"] > 1e-12]
    binding_only = binding[binding["daily_cap_binding"]]
    monthly_attribution = {}
    for month in ("2024-04", "2024-06"):
        monthly_attribution[month] = {
            "core_strict_return": monthly_period_return(core_strict, month),
            "0022_strict_return": monthly_period_return(monthly_strict, month),
            "0024_strict_return": monthly_period_return(daily_strict, month),
        }

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "promotion_evidence": False,
        "validation": {
            "core_weight_max_abs_error": core_weight_error,
            "router_core_equity_max_abs_error": router_core_error,
            "reconstructed_0022_price_final_10k_error": price_0022_error,
            "reconstructed_0022_strict_final_10k_error": strict_0022_error,
            "max_final_held_gross": max_gross,
        },
        "daily_cap_behavior": {
            "active_daily_rows": int(len(binding)),
            "binding_days": int(len(binding_only)),
            "binding_fraction_of_active_days": float(len(binding_only) / len(binding)) if len(binding) else 0.0,
            "mean_reduction_when_binding": float(binding_only["daily_reduction_vs_monthly"].mean()) if len(binding_only) else 0.0,
            "max_reduction": float(binding["daily_reduction_vs_monthly"].max()) if len(binding) else 0.0,
            "mean_actual_extra_on_active_days": float(binding["daily_actual_extra"].mean()) if len(binding) else 0.0,
            "mean_monthly_approved_extra_on_active_days": float(binding["monthly_approved_extra"].mean()) if len(binding) else 0.0,
        },
        "price_only_metrics": price_metrics,
        "funding_aware_metrics": funding_metrics,
        "capture": {
            "BRRK0011_CORE": monthly_capture(core_ret, btc_ret),
            "ASYM_BETA_0022_MONTHLY": monthly_capture(monthly_ret, btc_ret),
            "ASYM_BETA_0024_DAILY_CAP": monthly_capture(daily_ret, btc_ret),
        },
        "annual_returns": {
            "BRRK0011_CORE": annual_returns(core_ret),
            "ASYM_BETA_0022_MONTHLY": annual_returns(monthly_ret),
            "ASYM_BETA_0024_DAILY_CAP": annual_returns(daily_ret),
            "ASYM_BETA_0024_STRICT_ROUTER": annual_returns(daily_strict),
        },
        "drawdown": {
            "BRRK0011_CORE_STRICT": drawdown_info(core_strict),
            "ASYM_BETA_0022_STRICT": drawdown_info(monthly_strict),
            "ASYM_BETA_0024_STRICT": drawdown_info(daily_strict),
        },
        "known_month_attribution": monthly_attribution,
        "stopping_rule": "No tuning. If latency improvement is insufficient and April remains dominant, preserve 0024 and return to no-trading-change attribution before adding any new risk variable."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== ASYM_BETA_0024_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
