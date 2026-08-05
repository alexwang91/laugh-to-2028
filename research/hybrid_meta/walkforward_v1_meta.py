import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
REGIME = RESEARCH / "regime_kelly"
RISKFIX = RESEARCH / "risk_metric_fix"
sys.path.insert(0, str(RESEARCH))
sys.path.insert(0, str(REGIME))
sys.path.insert(0, str(RISKFIX))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from corrected_risk import choose_scale_corrected
from daily_distribution import semantic_transition_matrix
from features_no_dominance import build_features_no_dominance
from regime_model import SEMANTIC_STATES
from regime_model_vb_nd import fit_variational_regime_model_nd

# Backlog F13 / docs/CODE_REVIEW_2026-08-04.md section 2.3: this file used to
# define its own path_tail_risk/safe_max_scale/expected_log_terminal/
# choose_scale, which computed path drawdown without including decision-time
# wealth=1 as the initial running peak -- understating drawdown on paths that
# lose money on their very first simulated day. research/risk_metric_fix/
# corrected_risk.py fixes this (see
# research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md) and is what every
# other caller of this module (run_dispersion_overlay.py, run_asym_beta_0021/
# 0022/0024.py, run_audit_0023/0026.py) already uses for its own risk-scaling
# -- none of them ever imported the uncorrected functions that used to live
# here. Only this file's own main() (BRRK-MVP-0005-V1-META, which has no
# published results directory) called the uncorrected version, so this switch
# restates nothing that is cited anywhere in this repo. main() now calls
# choose_scale_corrected directly; the local duplicates are deleted rather
# than kept as unreachable dead code.


EXPERIMENT_ID = "BRRK-MVP-0005-V1-META"
END = pd.Timestamp("2026-08-02")
START = "2020-08-01"
COST_BPS = 5.0
RISK_BUDGET = 0.20
DF = 5.0


def metrics(ret: pd.Series, turnover: pd.Series, gross: pd.Series) -> dict:
    ret = ret.dropna()
    nav = (1.0 + ret).cumprod()
    if len(nav) == 0:
        return {}
    years = len(ret) / 365.25
    cagr = float(nav.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")
    dd = nav / nav.cummax() - 1
    vol = float(ret.std() * math.sqrt(365))
    sharpe = float(ret.mean() / ret.std() * math.sqrt(365)) if ret.std() > 0 else float("nan")
    losses = -ret
    q95 = float(losses.quantile(0.95))
    cvar95 = float(losses[losses >= q95].mean()) if (losses >= q95).any() else q95
    qdd = float(dd.quantile(0.05))
    cdar95 = float(-dd[dd <= qdd].mean()) if (dd <= qdd).any() else float(-qdd)
    return {
        "end_multiple": float(nav.iloc[-1]),
        "final_10k": float(nav.iloc[-1] * 10000),
        "cagr": cagr,
        "max_drawdown": float(dd.min()),
        "ann_vol": vol,
        "sharpe": sharpe,
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else float("nan"),
        "daily_cvar95": cvar95,
        "cdar95_path": cdar95,
        "turnover": float(turnover.sum()),
        "avg_gross_exposure": float(gross.mean()),
    }


def monthly_capture(strategy_ret: pd.Series, btc_ret: pd.Series) -> dict:
    s = (1.0 + strategy_ret).resample("ME").prod() - 1.0
    b = (1.0 + btc_ret).resample("ME").prod() - 1.0
    x = pd.concat([s.rename("s"), b.rename("b")], axis=1).dropna()
    up = x[x.b > 0]
    down = x[x.b < 0]
    return {
        "upside_capture": float(up.s.sum() / up.b.sum()) if len(up) and up.b.sum() != 0 else float("nan"),
        "downside_capture": float(down.s.sum() / down.b.sum()) if len(down) and down.b.sum() != 0 else float("nan"),
        "up_months": int(len(up)),
        "down_months": int(len(down)),
    }


def build_benchmark_v1(prices: pd.DataFrame) -> pd.DataFrame:
    p4 = prices[["BTC", "ETH", "SOL", "BNB"]].dropna()
    w4, _ = bt.build_rotation_weights(p4)
    gross = w4.abs().sum(axis=1)
    scale = pd.Series(1.0, index=w4.index)
    scale[gross > 1.0] = 1.0 / gross[gross > 1.0]
    w4 = w4.mul(scale, axis=0)
    out = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    out.loc[w4.index, w4.columns] = w4
    return out


def portfolio_returns_full(prices: pd.DataFrame, target_weights: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    held = target_weights.shift(1).fillna(0.0)
    ret_assets = prices.pct_change(fill_method=None).fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = held.abs().sum(axis=1)
    ret = (held * ret_assets).sum(axis=1) - turnover * COST_BPS / 10000.0
    return ret, turnover, gross


def daily_portfolio(prices: pd.DataFrame, target_weights: pd.DataFrame, start: pd.Timestamp):
    ret, turnover, gross = portfolio_returns_full(prices, target_weights)
    return ret.loc[start:END], turnover.loc[start:END], gross.loc[start:END]


def posterior_entropy(posterior: pd.Series) -> float:
    p = posterior.to_numpy(float)
    p = p[p > 0]
    return float(-(p * np.log(p)).sum()) if len(p) else 0.0


def fit_state_v1_distribution(
    v1_returns: pd.Series,
    train_features: pd.DataFrame,
    fit,
    cfg: RegimeKellyConfig,
) -> dict:
    common = v1_returns.dropna().index.intersection(train_features.dropna().index)
    y = v1_returns.loc[common].astype(float)
    posterior = fit.posterior(train_features.loc[common]).reindex(common)
    common = y.index.intersection(posterior.dropna().index)
    y = y.loc[common]
    posterior = posterior.loc[common]

    global_mu = float(y.mean())
    global_var = float(y.var(ddof=0))
    global_var = max(global_var, 1e-10)
    out = {
        "global_mean": global_mu,
        "global_var": global_var,
        "means": {},
        "variances": {},
        "effective_n": {},
    }

    arr = y.to_numpy(float)
    for state in SEMANTIC_STATES:
        w = np.maximum(posterior[state].to_numpy(float), 0.0)
        if w.sum() <= 0:
            mu_raw = global_mu
            var_raw = global_var
            n_eff = 1.0
        else:
            w = w / w.sum()
            mu_raw = float(np.sum(arr * w))
            var_raw = float(np.sum(((arr - mu_raw) ** 2) * w))
            n_eff = float(1.0 / np.sum(w ** 2))
        shrink = n_eff / (n_eff + cfg.shrinkage_strength)
        mu = shrink * mu_raw + (1.0 - shrink) * global_mu
        var = shrink * max(var_raw, 1e-10) + (1.0 - shrink) * global_var
        out["means"][state] = float(mu)
        out["variances"][state] = float(max(var, 1e-10))
        out["effective_n"][state] = float(n_eff)
    return out


def sample_v1_paths(current_posterior: pd.Series, fit, dist: dict, cfg: RegimeKellyConfig, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    p = np.array([max(float(current_posterior.get(s, 0.0)), 0.0) for s in SEMANTIC_STATES], dtype=float)
    p /= max(p.sum(), 1e-12)
    trans = semantic_transition_matrix(fit)
    n = cfg.scenario_count
    horizon = cfg.forecast_horizon_days
    current_state = rng.choice(len(SEMANTIC_STATES), size=n, p=p)
    paths = np.zeros((n, horizon), dtype=float)

    for day in range(horizon):
        next_state = np.empty(n, dtype=int)
        for s in range(len(SEMANTIC_STATES)):
            loc = np.where(current_state == s)[0]
            if len(loc):
                next_state[loc] = rng.choice(len(SEMANTIC_STATES), size=len(loc), p=trans[s])
        current_state = next_state

        for s_idx, state in enumerate(SEMANTIC_STATES):
            loc = np.where(current_state == s_idx)[0]
            if len(loc) == 0:
                continue
            mu = float(dist["means"][state])
            var = float(dist["variances"][state])
            scale = math.sqrt(max(var * (DF - 2.0) / DF, 1e-12))
            paths[loc, day] = mu + rng.standard_t(DF, size=len(loc)) * scale

    return np.maximum(paths, -0.999)


def main():
    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    bt.START_DATE = START
    bt.END_DATE = str(END.date())

    prices = pd.concat({a: bt.fetch_daily(a + "USDT") for a in cfg.assets}, axis=1).sort_index().loc[:END]
    prices = prices.dropna()
    features = build_features_no_dominance(prices, cfg)
    v1_raw = build_benchmark_v1(prices)
    v1_banded = bt.apply_band(v1_raw, 0.05)
    v1_returns, _, _ = portfolio_returns_full(prices, v1_banded)

    decision_dates = []
    for dt in features.dropna().index:
        if dt > END:
            break
        if len(features.loc[:dt].dropna()) >= cfg.min_train_days:
            if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
                decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("No eligible BRRK-MVP-0005-V1-META walk-forward decision dates")

    eval_start = decision_dates[0] + pd.Timedelta(days=1)
    print(
        f"{EXPERIMENT_ID} decisions={len(decision_dates)} first={decision_dates[0].date()} "
        f"eval_start={eval_start.date()} end={END.date()}",
        flush=True,
    )

    scale_series = pd.Series(np.nan, index=prices.index, dtype=float)
    decisions = []

    for j, dt in enumerate(decision_dates):
        train_features = features.loc[:dt]
        fit = fit_variational_regime_model_nd(train_features, cfg, n_factors=4)
        posterior = fit.filtered_posterior(features.loc[:dt]).iloc[-1]
        dist = fit_state_v1_distribution(v1_returns.loc[:dt], train_features, fit, cfg)
        paths = sample_v1_paths(
            posterior,
            fit,
            dist,
            cfg,
            seed=cfg.random_seed + int(dt.strftime("%Y%m%d")),
        )
        alloc = choose_scale_corrected(paths, RISK_BUDGET)
        scale = float(alloc["scale"])

        next_dt = decision_dates[j + 1] if j + 1 < len(decision_dates) else END + pd.Timedelta(days=1)
        active_idx = prices.loc[dt:next_dt - pd.Timedelta(days=1)].index
        scale_series.loc[active_idx] = scale

        decisions.append({
            "date": str(dt.date()),
            "posterior": {k: float(v) for k, v in posterior.items()},
            "posterior_entropy": posterior_entropy(posterior),
            "scale": scale,
            "safe_max_scale": float(alloc["safe_max"]),
            "expected_log20": float(alloc["expected_log20"]),
            "scenario_cvar95": float(alloc["scenario_cvar95"]),
            "scenario_cdar95": float(alloc["scenario_cdar95"]),
            "full_scale_cvar95": float(alloc["full_scale_cvar95"]),
            "full_scale_cdar95": float(alloc["full_scale_cdar95"]),
            "global_v1_daily_mean": float(dist["global_mean"]),
            "state_v1_daily_mean": {k: float(v) for k, v in dist["means"].items()},
            "state_v1_daily_vol": {k: float(math.sqrt(v)) for k, v in dist["variances"].items()},
            "state_effective_n": {k: float(v) for k, v in dist["effective_n"].items()},
            "converged": bool(fit.converged),
            "pca_variance": float(fit.pca.explained_variance_ratio_.sum()),
        })
        print(
            j + 1,
            dt.date(),
            "p", {k: round(float(v), 3) for k, v in posterior.items()},
            "scale", round(scale, 3),
            "safe", round(float(alloc["safe_max"]), 3),
            "elog20", round(float(alloc["expected_log20"]), 4),
            "cvar1", round(float(alloc["full_scale_cvar95"]), 3),
            "cdar1", round(float(alloc["full_scale_cdar95"]), 3),
            flush=True,
        )

    scale_series = scale_series.ffill().fillna(1.0)
    hybrid_raw = v1_raw.mul(scale_series, axis=0)
    hybrid = bt.apply_band(hybrid_raw, 0.05)

    rh, th, gh = daily_portfolio(prices, hybrid, eval_start)
    rv1, tv1, gv1 = daily_portfolio(prices, v1_banded, eval_start)

    beta, _, _ = bt.btc_last_drop_beta(prices["BTC"])
    wb = pd.DataFrame(0.0, index=prices.index, columns=cfg.assets)
    wb["BTC"] = beta.clip(upper=1.0)
    wb = bt.apply_band(wb, 0.05)
    rb, tb, gb = daily_portfolio(prices, wb, eval_start)

    btc_ret = prices["BTC"].pct_change(fill_method=None).loc[eval_start:END].fillna(0.0)
    scales = np.array([d["scale"] for d in decisions], dtype=float)
    safe_scales = np.array([d["safe_max_scale"] for d in decisions], dtype=float)

    report = {
        "experiment_id": EXPERIMENT_ID,
        "methodology": {
            "alpha_layer": "Frozen V1 daily rotation strategy unchanged",
            "meta_target": "daily net return of frozen V1 after its own band and 5 bps turnover cost",
            "state_model": "price-only RobustScaler -> PCA4 whitened -> sticky VariationalGaussianHMM",
            "return_model": "state-conditioned V1 daily mean/variance with n_eff shrinkage toward expanding global V1 mean/variance",
            "scenario_engine": "20 sequential Markov state days with df=5 Student-t scalar V1 returns",
            "allocator": "one-dimensional exposure scalar s in [0,1], maximize expected 20d log terminal wealth subject to terminal CVaR95 and path CDaR95 <=20%",
            "decision_frequency_days": cfg.refit_every_days,
            "minimum_training_feature_days": cfg.min_train_days,
            "scenario_count": cfg.scenario_count,
            "cost_bps_per_abs_weight_change": COST_BPS,
            "first_decision": str(decision_dates[0].date()),
            "evaluation_start": str(eval_start.date()),
            "evaluation_end": str(END.date()),
            "oos_decisions": len(decision_dates),
        },
        "metrics": {
            "BRRK_0005_V1_META": metrics(rh, th, gh),
            "V1_ROTATION_GROSS_1_0": metrics(rv1, tv1, gv1),
            "BTC_DYNAMIC_GROSS_1_0": metrics(rb, tb, gb),
        },
        "capture": {
            "BRRK_0005_V1_META": monthly_capture(rh, btc_ret),
            "V1_ROTATION_GROSS_1_0": monthly_capture(rv1, btc_ret),
            "BTC_DYNAMIC_GROSS_1_0": monthly_capture(rb, btc_ret),
        },
        "diagnostics": {
            "convergence_rate": float(np.mean([d["converged"] for d in decisions])),
            "mean_pca_variance": float(np.mean([d["pca_variance"] for d in decisions])),
            "mean_posterior_entropy": float(np.mean([d["posterior_entropy"] for d in decisions])),
            "mean_selected_scale": float(scales.mean()),
            "min_selected_scale": float(scales.min()),
            "mean_safe_max_scale": float(safe_scales.mean()),
            "decisions_scale_eq_1": int(np.sum(scales > 0.999)),
            "decisions_scale_eq_0": int(np.sum(scales < 0.001)),
            "decisions_scale_between": int(np.sum((scales >= 0.001) & (scales <= 0.999))),
        },
        "current": decisions[-1],
        "decisions": decisions,
        "warning": "Preregistered first OOS run. No hyperparameter change after observing this result without a new experiment ID.",
    }

    out = HERE / "walkforward_v1_meta_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== BRRK_0005_V1_META_REPORT ===")
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "methodology": report["methodology"],
        "metrics": report["metrics"],
        "capture": report["capture"],
        "diagnostics": report["diagnostics"],
        "current": report["current"],
    }, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
