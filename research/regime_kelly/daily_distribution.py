from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

from config import RegimeKellyConfig
from regime_model import SEMANTIC_STATES
from regime_model_vb_nd import VariationalRegimeFitND


@dataclass
class DailyConditionalDistribution:
    assets: tuple[str, ...]
    means: dict[str, np.ndarray]
    covariances: dict[str, np.ndarray]
    effective_n: dict[str, float]
    mean_uncertainty: dict[str, np.ndarray]


def _nearest_psd(cov: np.ndarray, floor: float = 1e-10) -> np.ndarray:
    cov = 0.5 * (cov + cov.T)
    vals, vecs = np.linalg.eigh(cov)
    vals = np.maximum(vals, floor)
    return (vecs * vals) @ vecs.T


def _weighted_mean_cov(x: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    mask = np.isfinite(x).all(axis=1) & np.isfinite(w)
    x = x[mask]
    w = np.maximum(w[mask], 0.0)
    if len(x) == 0 or w.sum() <= 0:
        raise ValueError("No weighted observations")
    w = w / w.sum()
    mu = np.sum(x * w[:, None], axis=0)
    xc = x - mu
    cov = (xc * w[:, None]).T @ xc
    n_eff = float(1.0 / np.sum(w ** 2))
    return mu, _nearest_psd(cov), n_eff


def fit_daily_conditional_distribution(
    daily_log_returns: pd.DataFrame,
    train_features: pd.DataFrame,
    regime_fit: VariationalRegimeFitND,
    cfg: RegimeKellyConfig,
) -> DailyConditionalDistribution:
    common = daily_log_returns.dropna().index.intersection(train_features.dropna().index)
    y = daily_log_returns.loc[common, list(cfg.assets)]
    posterior = regime_fit.posterior(train_features.loc[common]).reindex(common)
    common = y.index.intersection(posterior.dropna().index)
    y = y.loc[common]
    posterior = posterior.loc[common]
    arr = y.to_numpy(float)

    global_cov = _nearest_psd(LedoitWolf().fit(arr).covariance_)
    means, covs, eff, unc = {}, {}, {}, {}
    for state in SEMANTIC_STATES:
        mu_raw, cov_raw, n_eff = _weighted_mean_cov(arr, posterior[state].to_numpy(float))
        shrink = n_eff / (n_eff + cfg.shrinkage_strength)
        mu = shrink * mu_raw
        cov = _nearest_psd(shrink * cov_raw + (1.0 - shrink) * global_cov)
        means[state] = mu
        covs[state] = cov
        eff[state] = n_eff
        unc[state] = np.sqrt(np.maximum(np.diag(cov), 1e-12) / max(n_eff, 1.0))

    return DailyConditionalDistribution(
        assets=cfg.assets,
        means=means,
        covariances=covs,
        effective_n=eff,
        mean_uncertainty=unc,
    )


def semantic_transition_matrix(regime_fit: VariationalRegimeFitND) -> np.ndarray:
    k = len(SEMANTIC_STATES)
    out = np.zeros((k, k), dtype=float)
    for i, s1 in enumerate(SEMANTIC_STATES):
        r1 = regime_fit.semantic_to_raw[s1]
        for j, s2 in enumerate(SEMANTIC_STATES):
            r2 = regime_fit.semantic_to_raw[s2]
            out[i, j] = float(regime_fit.model.transmat_[r1, r2])
        out[i] = out[i] / max(out[i].sum(), 1e-12)
    return out


def expected_state_mix(
    current_posterior: pd.Series,
    regime_fit: VariationalRegimeFitND,
    horizon: int,
) -> np.ndarray:
    p = np.array([max(float(current_posterior.get(s, 0.0)), 0.0) for s in SEMANTIC_STATES], dtype=float)
    p = p / max(p.sum(), 1e-12)
    trans = semantic_transition_matrix(regime_fit)
    acc = np.zeros_like(p)
    q = p.copy()
    for _ in range(horizon):
        q = q @ trans
        acc += q
    return acc / max(horizon, 1)


def markov_mean_uncertainty(
    current_posterior: pd.Series,
    regime_fit: VariationalRegimeFitND,
    distribution: DailyConditionalDistribution,
    horizon: int,
) -> np.ndarray:
    mix = expected_state_mix(current_posterior, regime_fit, horizon)
    out = np.zeros(len(distribution.assets), dtype=float)
    for i, state in enumerate(SEMANTIC_STATES):
        out += mix[i] * distribution.mean_uncertainty[state] * np.sqrt(horizon)
    return out


def sample_markov_paths(
    current_posterior: pd.Series,
    regime_fit: VariationalRegimeFitND,
    distribution: DailyConditionalDistribution,
    cfg: RegimeKellyConfig,
    seed: int | None = None,
    horizon: int | None = None,
    df: float = 5.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Return terminal simple returns and daily simple-return paths.

    State at t is sampled from the filtered posterior. Each future day first
    transitions to S_{t+1}, then draws that state's multivariate daily return.
    """
    horizon = cfg.forecast_horizon_days if horizon is None else horizon
    rng = np.random.default_rng(cfg.random_seed if seed is None else seed)
    p = np.array([max(float(current_posterior.get(s, 0.0)), 0.0) for s in SEMANTIC_STATES], dtype=float)
    if p.sum() <= 0:
        raise ValueError("Posterior probabilities sum to zero")
    p /= p.sum()
    trans = semantic_transition_matrix(regime_fit)

    n = cfg.scenario_count
    a = len(distribution.assets)
    current_state = rng.choice(len(SEMANTIC_STATES), size=n, p=p)
    log_paths = np.zeros((n, horizon, a), dtype=float)

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
            mu = distribution.means[state]
            cov = distribution.covariances[state]
            scale = _nearest_psd(cov * (df - 2.0) / df)
            z = rng.multivariate_normal(np.zeros(a), scale, size=len(loc))
            chi = rng.chisquare(df, size=len(loc))
            tdraw = z / np.sqrt(chi[:, None] / df)
            log_paths[loc, day, :] = mu + tdraw

    terminal_simple = np.expm1(log_paths.sum(axis=1))
    daily_simple = np.expm1(log_paths)
    return terminal_simple, daily_simple


def portfolio_path_cdar95(daily_simple_paths: np.ndarray, weights: pd.Series) -> float:
    w = weights.to_numpy(float)
    port = daily_simple_paths @ w
    nav = np.cumprod(1.0 + port, axis=1)
    peaks = np.maximum.accumulate(nav, axis=1)
    dd = nav / np.maximum(peaks, 1e-12) - 1.0
    max_dd = dd.min(axis=1)
    q = np.quantile(max_dd, 0.05)
    tail = max_dd[max_dd <= q]
    return float(-tail.mean()) if len(tail) else float(-q)
