import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
REGIME = RESEARCH / "regime_kelly"
HYBRID = RESEARCH / "hybrid_meta"
RISKFIX = RESEARCH / "risk_metric_fix"
for p in (RESEARCH, REGIME, HYBRID, RISKFIX):
    sys.path.insert(0, str(p))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from features_no_dominance import build_features_no_dominance
from regime_model_vb_nd import fit_variational_regime_model_nd
from walkforward_v1_meta import (
    COST_BPS,
    END,
    RISK_BUDGET,
    START,
    build_benchmark_v1,
    daily_portfolio,
    fit_state_v1_distribution,
    metrics,
    monthly_capture,
    portfolio_returns_full,
    sample_v1_paths,
)
from corrected_risk import choose_scale_corrected

EXPERIMENT_ID = "DISP-0013-ALT-RELIABILITY"
DISPERSION_ASSETS = ["ETH", "SOL", "BNB", "XRP"]
V1_ALTS = ["ETH", "SOL", "BNB"]
PRIMARY_TAIL_START = 0.90
SENSITIVITY_TAIL_STARTS = (0.80, 0.95)


def expanding_percentile(series: pd.Series) -> pd.Series:
    """Empirical percentile of x_t against strictly earlier finite observations."""
    x = series.to_numpy(float)
    out = np.full(len(x), np.nan, dtype=float)
    hist = []
    for i, val in enumerate(x):
        if np.isfinite(val) and hist:
            arr = np.asarray(hist, dtype=float)
            out[i] = float(np.mean(arr <= val))
        if np.isfinite(val):
            hist.append(float(val))
    return pd.Series(out, index=series.index, dtype=float)


def dispersion_state(prices: pd.DataFrame, tail_start: float) -> tuple[pd.Series, pd.Series, pd.Series]:
    log_ret20 = np.log(prices[DISPERSION_ASSETS] / prices[DISPERSION_ASSETS].shift(20))
    dispersion = log_ret20.std(axis=1, ddof=1, skipna=False)
    percentile = expanding_percentile(dispersion)
    gate = pd.Series(1.0, index=prices.index, dtype=float)
    active = percentile > tail_start
    gate.loc[active] = ((1.0 - percentile.loc[active]) / (1.0 - tail_start)).clip(0.0, 1.0)
    gate.loc[percentile.isna()] = 1.0
    return dispersion, percentile, gate


def apply_dispersion_to_v1(v1_raw: pd.DataFrame, gate: pd.Series) -> pd.DataFrame:
    """Reduce only the V1 alt sleeve and transfer all released weight to BTC."""
    out = v1_raw.copy()
    g = gate.reindex(out.index).fillna(1.0)
    original_alt = out[V1_ALTS].sum(axis=1)
    out[V1_ALTS] = out[V1_ALTS].mul(g, axis=0)
    adjusted_alt = out[V1_ALTS].sum(axis=1)
    out["BTC"] = out["BTC"] + (original_alt - adjusted_alt)
    return out


def build_brrk0011_scale(prices: pd.DataFrame, features: pd.DataFrame, v1_returns: pd.Series, cfg: RegimeKellyConfig):
    decision_dates = []
    for dt in features.dropna().index:
        if dt > END:
            break
        if len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("No eligible BRRK decision dates")

    final_scale = pd.Series(np.nan, index=prices.index, dtype=float)
    decisions = []
    for j, dt in enumerate(decision_dates):
        train = features.loc[:dt]
        fit = fit_variational_regime_model_nd(train, cfg, n_factors=4)
        posterior = fit.filtered_posterior(features.loc[:dt]).iloc[-1]
        dist = fit_state_v1_distribution(v1_returns.loc[:dt], train, fit, cfg)
        paths = sample_v1_paths(
            posterior,
            fit,
            dist,
            cfg,
            seed=cfg.random_seed + int(dt.strftime("%Y%m%d")),
        )
        alloc = choose_scale_corrected(paths, RISK_BUDGET)
        meta = float(alloc["scale"])
        p_ro = float(np.clip(posterior.get("RISK_OFF", 0.0), 0.0, 1.0))
        scale = float(1.0 - p_ro * (1.0 - meta))
        next_dt = decision_dates[j + 1] if j + 1 < len(decision_dates) else END + pd.Timedelta(days=1)
        active_idx = prices.loc[dt:next_dt - pd.Timedelta(days=1)].index
        final_scale.loc[active_idx] = scale
        decisions.append({
            "date": str(dt.date()),
            "riskoff_probability": p_ro,
            "meta_scale": meta,
            "final_scale": scale,
            "full_scale_cvar95": float(alloc["full_scale_cvar95"]),
            "full_scale_cdar95_corrected": float(alloc["full_scale_cdar95"]),
        })
    return final_scale.ffill().fillna(1.0), decision_dates, decisions


def annual_returns(ret: pd.Series) -> dict:
    out = {}
    for year, s in ret.groupby(ret.index.year):
        out[str(int(year))] = float((1.0 + s).prod() - 1.0)
    return out


def subperiod_metrics(ret, turn, gross) -> dict:
    out = {}
    for start in ["2023-01-01", "2024-01-01", "2025-01-01", "2026-01-01"]:
        idx = ret.index >= pd.Timestamp(start)
        out[start] = metrics(ret.loc[idx], turn.loc[idx], gross.loc[idx])
    return out


def evaluate(prices, raw_weights, eval_start):
    banded = bt.apply_band(raw_weights, 0.05)
    ret, turn, gross = daily_portfolio(prices, banded, eval_start)
    return {
        "return": ret,
        "turnover": turn,
        "gross": gross,
        "metrics": metrics(ret, turn, gross),
        "annual_returns": annual_returns(ret),
        "subperiods": subperiod_metrics(ret, turn, gross),
    }


def main():
    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    bt.START_DATE = START
    bt.END_DATE = str(END.date())

    prices = pd.concat({a: bt.fetch_daily(a + "USDT") for a in cfg.assets}, axis=1).sort_index().loc[:END].dropna()
    features = build_features_no_dominance(prices, cfg)
    v1_raw = build_benchmark_v1(prices)
    v1_banded_for_model = bt.apply_band(v1_raw, 0.05)
    v1_returns_model, _, _ = portfolio_returns_full(prices, v1_banded_for_model)

    brrk_scale, decision_dates, decisions = build_brrk0011_scale(prices, features, v1_returns_model, cfg)
    eval_start = decision_dates[0] + pd.Timedelta(days=1)

    btc_ret = prices["BTC"].pct_change(fill_method=None).loc[eval_start:END].fillna(0.0)
    primary_disp, primary_pct, primary_gate = dispersion_state(prices, PRIMARY_TAIL_START)
    v1_disp_raw = apply_dispersion_to_v1(v1_raw, primary_gate)

    candidates = {
        "V1_ROTATION_GROSS_1_0": v1_raw,
        "V1_PLUS_DISPERSION_PRIMARY": v1_disp_raw,
        "BRRK_0011_BASELINE": v1_raw.mul(brrk_scale, axis=0),
        "BRRK_0011_PLUS_DISPERSION_PRIMARY": v1_disp_raw.mul(brrk_scale, axis=0),
    }

    evaluated = {name: evaluate(prices, w, eval_start) for name, w in candidates.items()}

    sensitivity = {}
    for tail_start in SENSITIVITY_TAIL_STARTS:
        _, pct, gate = dispersion_state(prices, tail_start)
        adj = apply_dispersion_to_v1(v1_raw, gate)
        key = f"tail_start_{int(tail_start*100)}pct"
        ev_v1 = evaluate(prices, adj, eval_start)
        ev_brrk = evaluate(prices, adj.mul(brrk_scale, axis=0), eval_start)
        sensitivity[key] = {
            "tail_start": tail_start,
            "V1": ev_v1["metrics"],
            "BRRK_0011": ev_brrk["metrics"],
            "active_day_fraction": float((gate.loc[eval_start:END] < 0.999999).mean()),
            "mean_gate": float(gate.loc[eval_start:END].mean()),
        }

    metrics_report = {name: ev["metrics"] for name, ev in evaluated.items()}
    annual_report = {name: ev["annual_returns"] for name, ev in evaluated.items()}
    subperiod_report = {name: ev["subperiods"] for name, ev in evaluated.items()}
    capture_report = {name: monthly_capture(ev["return"], btc_ret) for name, ev in evaluated.items()}

    idx = primary_gate.loc[eval_start:END].index
    base_alt = v1_raw.loc[idx, V1_ALTS].sum(axis=1)
    adj_alt = v1_disp_raw.loc[idx, V1_ALTS].sum(axis=1)
    active = primary_gate.loc[idx] < 0.999999
    current_dt = prices.index[-1]

    report = {
        "experiment_id": EXPERIMENT_ID,
        "methodology": {
            "evaluation_start": str(eval_start.date()),
            "evaluation_end": str(END.date()),
            "dispersion_assets": DISPERSION_ASSETS,
            "dispersion_signal": "cross-sectional sample std of trailing 20-day log returns",
            "percentile_reference": "strictly earlier expanding observations only",
            "primary_upper_tail_start": PRIMARY_TAIL_START,
            "primary_gate": "1 below 90th percentile; linearly decays from 1 to 0 between the 90th and 100th expanding percentiles",
            "weight_action": "scale ETH/SOL/BNB V1 sleeve only; transfer removed alt weight to BTC; gross preserved before BRRK scaling",
            "BRRK": "frozen PCA4 BRRK-0006 authority structure with BRRK-0011 corrected CDaR; BRRK scale estimated from frozen V1, not reoptimized on the dispersion portfolio",
            "transaction_cost_bps": COST_BPS,
            "rebalance_band_l1": 0.05,
            "lookahead": "none; prior-day target held over next-day return",
            "fixed_universe_warning": "This is a mechanism test on a fixed present-day mega-cap panel. Positive results remain provisional pending point-in-time universe validation."
        },
        "metrics": metrics_report,
        "capture": capture_report,
        "annual_returns": annual_report,
        "subperiods": subperiod_report,
        "primary_diagnostics": {
            "active_day_fraction": float(active.mean()),
            "severe_gate_below_0_5_fraction": float((primary_gate.loc[idx] < 0.5).mean()),
            "mean_gate": float(primary_gate.loc[idx].mean()),
            "median_gate": float(primary_gate.loc[idx].median()),
            "mean_base_alt_weight": float(base_alt.mean()),
            "mean_adjusted_alt_weight": float(adj_alt.mean()),
            "mean_alt_weight_reduction_when_active": float((base_alt[active] - adj_alt[active]).mean()) if active.any() else 0.0,
            "current_date": str(current_dt.date()),
            "current_dispersion": float(primary_disp.loc[current_dt]),
            "current_expanding_percentile": float(primary_pct.loc[current_dt]),
            "current_gate": float(primary_gate.loc[current_dt]),
        },
        "sensitivity": sensitivity,
        "brrk_decision_count": len(decisions),
        "current_brrk": decisions[-1],
        "decision": "No automatic promotion. Interpret only after full family and subperiod results are visible; no posthoc threshold tuning is permitted.",
    }

    (HERE / "dispersion_overlay_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== DISP_0013_REPORT ===")
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "methodology": report["methodology"],
        "metrics": report["metrics"],
        "capture": report["capture"],
        "primary_diagnostics": report["primary_diagnostics"],
        "sensitivity": report["sensitivity"],
        "current_brrk": report["current_brrk"],
    }, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
