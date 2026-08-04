from __future__ import annotations

import math
import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import multivariate_normal, norm


def _raw_forward_filter(model, factors: np.ndarray) -> np.ndarray:
    """Strict causal forward-filtered raw-state probabilities."""
    k = model.n_components
    log_emission = np.empty((len(factors), k), dtype=float)
    for s in range(k):
        log_emission[:, s] = multivariate_normal.logpdf(
            factors,
            mean=model.means_[s],
            cov=model.covars_[s],
            allow_singular=True,
        )
    eps = 1e-300
    log_start = np.log(np.maximum(model.startprob_, eps))
    log_trans = np.log(np.maximum(model.transmat_, eps))
    log_alpha = np.empty_like(log_emission)
    log_alpha[0] = log_start + log_emission[0]
    log_alpha[0] -= logsumexp(log_alpha[0])
    for t in range(1, len(factors)):
        pred = np.array([
            logsumexp(log_alpha[t - 1] + log_trans[:, j])
            for j in range(k)
        ])
        log_alpha[t] = pred + log_emission[t]
        log_alpha[t] -= logsumexp(log_alpha[t])
    return np.exp(log_alpha)


def raw_filtered_posterior(fit, features: pd.DataFrame) -> np.ndarray:
    _, factors = fit._transform(features)
    return _raw_forward_filter(fit.model, factors)[-1].astype(float)


def fit_raw_v1_distribution(v1_returns: pd.Series, train_features: pd.DataFrame, fit, cfg) -> dict:
    x, factors = fit._transform(train_features)
    gamma = fit.model.predict_proba(factors)
    gamma_df = pd.DataFrame(gamma, index=x.index, columns=range(fit.model.n_components))
    common = v1_returns.dropna().index.intersection(gamma_df.index)
    y = v1_returns.loc[common].astype(float).to_numpy()
    g = gamma_df.loc[common].to_numpy(float)

    global_mu = float(np.mean(y))
    global_var = float(np.var(y))
    global_var = max(global_var, 1e-10)
    means, variances, effective_n, negative_mean_probability = {}, {}, {}, {}

    for raw in range(fit.model.n_components):
        w = np.maximum(g[:, raw], 0.0)
        if w.sum() <= 0:
            mu_raw, var_raw, n_eff = global_mu, global_var, 1.0
        else:
            w = w / w.sum()
            mu_raw = float(np.sum(y * w))
            var_raw = float(np.sum(((y - mu_raw) ** 2) * w))
            n_eff = float(1.0 / np.sum(w ** 2))
        shrink = n_eff / (n_eff + cfg.shrinkage_strength)
        mu = float(shrink * mu_raw + (1.0 - shrink) * global_mu)
        var = float(shrink * max(var_raw, 1e-10) + (1.0 - shrink) * global_var)
        se = math.sqrt(max(var, 1e-12) / max(n_eff, 1.0))
        p_negative = float(norm.cdf((0.0 - mu) / max(se, 1e-12)))
        means[raw] = mu
        variances[raw] = max(var, 1e-10)
        effective_n[raw] = n_eff
        negative_mean_probability[raw] = p_negative

    return {
        "global_mean": global_mu,
        "global_var": global_var,
        "means": means,
        "variances": variances,
        "effective_n": effective_n,
        "negative_mean_probability": negative_mean_probability,
    }


def bad_state_probability(raw_posterior: np.ndarray, dist: dict) -> float:
    p = np.maximum(np.asarray(raw_posterior, dtype=float), 0.0)
    p = p / max(float(p.sum()), 1e-12)
    badness = np.array(
        [dist["negative_mean_probability"][raw] for raw in range(len(p))],
        dtype=float,
    )
    return float(np.clip(np.dot(p, badness), 0.0, 1.0))
