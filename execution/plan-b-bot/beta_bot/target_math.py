from __future__ import annotations

"""Product-owned frozen BRRK-0011 target mathematics.

This module is intentionally independent from ``research/``.  It reproduces the
frozen V1 rotation + BRRK-0011 defensive-scale chain inside the runtime package
so live target calculation cannot drift through imports from experimental code.

P3.2 boundary: target calculation only.  The 5% band appears here solely because
BRRK-0011 historically calibrated its state-conditioned V1 return distribution
on the frozen *banded* V1 return series.  It is not applied to the target emitted
by P3.2 and therefore is not a P3.3 rebalance/turnover policy.
"""

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd
from hmmlearn.vhmm import VariationalGaussianHMM
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp
from scipy.stats import multivariate_normal
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler


TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")
FEATURE_ONLY_ASSETS = ("XRP",)
SIGNAL_ASSETS = TARGET_ASSETS + FEATURE_ONLY_ASSETS
SEMANTIC_STATES = ("RISK_OFF", "BTC_LEAD", "MAJOR_ROTATION", "ALT_EXPANSION")
NO_DOM_FEATURE_COLUMNS = (
    "btc_trend",
    "log_btc_rv30",
    "btc_drawdown_252",
    "major_breadth",
    "alt_breadth",
    "rel_strength_mean",
    "rel_strength_dispersion",
    "avg_corr30_btc",
)
FAST_HORIZONS = (20, 60, 120, 240)
FAST_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
SLOW_WEIGHTS = (0.10, 0.20, 0.30, 0.40)
INTERNAL_V1_BAND = 0.05
INTERNAL_V1_COST_BPS = 5.0
RISK_BUDGET = 0.20
STUDENT_T_DF = 5.0


class TargetMathError(RuntimeError):
    pass


@dataclass(frozen=True)
class FrozenBRRKConfig:
    assets: tuple[str, ...] = SIGNAL_ASSETS
    majors: tuple[str, ...] = ("ETH", "BNB", "XRP")
    alts: tuple[str, ...] = ("ETH", "SOL", "BNB", "XRP")
    n_states: int = 4
    forecast_horizon_days: int = 20
    min_train_days: int = 600
    refit_every_days: int = 30
    scenario_count: int = 5000
    random_seed: int = 20260804
    winsor_lower: float = 0.01
    winsor_upper: float = 0.99
    # Frozen effective BRRK-0011 caller values, not RegimeKellyConfig defaults.
    hmm_iter: int = 250
    hmm_tol: float = 1e-4
    hmm_restarts: int = 3
    sticky_diagonal_prior: float = 12.0
    sticky_offdiag_prior: float = 1.0
    shrinkage_strength: float = 20.0


@dataclass
class VariationalRegimeFitND:
    model: VariationalGaussianHMM
    scaler: RobustScaler
    pca: PCA
    winsor_lo: pd.Series
    winsor_hi: pd.Series
    raw_to_semantic: dict[int, str]
    semantic_to_raw: dict[str, int]
    training_log_likelihood: float
    occupancy: dict[int, float]
    converged: bool

    def _transform(self, features: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
        x = apply_winsor(features, self.winsor_lo, self.winsor_hi).dropna()
        if x.empty:
            raise TargetMathError("No finite regime features available after preprocessing")
        z = self.scaler.transform(x)
        return x, self.pca.transform(z)

    def posterior(self, features: pd.DataFrame) -> pd.DataFrame:
        """Smoothed posterior, used only for expanding state-return estimation."""
        x, factors = self._transform(features)
        gamma = self.model.predict_proba(factors)
        raw = pd.DataFrame(gamma, index=x.index, columns=range(self.model.n_components))
        out = pd.DataFrame(0.0, index=x.index, columns=SEMANTIC_STATES)
        for raw_state, semantic in self.raw_to_semantic.items():
            out[semantic] = raw[raw_state]
        return out

    def filtered_posterior(self, features: pd.DataFrame) -> pd.DataFrame:
        """Forward-filtered P(S_t | X_1:t), safe for a decision at t close."""
        x, factors = self._transform(features)
        k = self.model.n_components
        log_emission = np.empty((len(factors), k), dtype=float)
        for state in range(k):
            log_emission[:, state] = multivariate_normal.logpdf(
                factors,
                mean=self.model.means_[state],
                cov=self.model.covars_[state],
                allow_singular=True,
            )

        eps = 1e-300
        log_start = np.log(np.maximum(self.model.startprob_, eps))
        log_trans = np.log(np.maximum(self.model.transmat_, eps))
        log_alpha = np.empty_like(log_emission)
        log_alpha[0] = log_start + log_emission[0]
        log_alpha[0] -= logsumexp(log_alpha[0])
        for t in range(1, len(factors)):
            pred = np.array(
                [logsumexp(log_alpha[t - 1] + log_trans[:, j]) for j in range(k)]
            )
            log_alpha[t] = pred + log_emission[t]
            log_alpha[t] -= logsumexp(log_alpha[t])

        raw = pd.DataFrame(np.exp(log_alpha), index=x.index, columns=range(k))
        out = pd.DataFrame(0.0, index=x.index, columns=SEMANTIC_STATES)
        for raw_state, semantic in self.raw_to_semantic.items():
            out[semantic] = raw[raw_state]
        return out


def trend_score(price: pd.Series, weights: tuple[float, ...] = FAST_WEIGHTS) -> pd.Series:
    log_return = np.log(price).diff()
    out = pd.Series(0.0, index=price.index, dtype=float)
    valid = pd.Series(True, index=price.index)
    for horizon, weight in zip(FAST_HORIZONS, weights):
        momentum = np.log(price / price.shift(horizon))
        scale = log_return.rolling(horizon).std() * math.sqrt(horizon)
        component = np.tanh(momentum / scale.replace(0.0, np.nan))
        out = out + weight * component
        valid &= component.notna()
    return out.where(valid)


def rv30(price: pd.Series) -> pd.Series:
    return np.log(price).diff().rolling(30).std() * math.sqrt(365)


def btc_last_drop_beta(price: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    trend = trend_score(price)
    vol = rv30(price)
    positive_scaler = (0.45 / vol).clip(upper=1.0)
    beta = pd.Series(np.nan, index=price.index, dtype=float)
    positive = trend >= 0
    beta.loc[positive] = 1.0 + 0.5 * trend.loc[positive] * positive_scaler.loc[positive]

    vol_multiplier = pd.Series(1.0, index=price.index, dtype=float)
    vol_multiplier[(vol >= 0.35) & (vol < 0.50)] = 0.90
    vol_multiplier[(vol >= 0.50) & (vol < 0.70)] = 0.75
    vol_multiplier[vol >= 0.70] = 0.60
    negative = (
        (0.65 + 0.65 * trend).clip(lower=0.18, upper=0.65) * vol_multiplier
    ).clip(lower=0.18, upper=0.65)
    beta.loc[~positive] = negative.loc[~positive]
    return beta, trend, vol


def build_rotation_weights(prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    prices = prices.loc[:, list(TARGET_ASSETS)].copy().sort_index()
    btc = prices["BTC"]
    beta, btc_trend, btc_vol = btc_last_drop_beta(btc)

    trends = {asset: trend_score(prices[asset]) for asset in TARGET_ASSETS}
    ratio_trends = {
        asset: trend_score(prices[asset] / btc) for asset in ("ETH", "SOL")
    }
    bnb_trend_slow = trend_score(prices["BNB"], SLOW_WEIGHTS)
    bnb_ratio_slow = trend_score(prices["BNB"] / btc, SLOW_WEIGHTS)
    vols = {asset: rv30(prices[asset]) for asset in TARGET_ASSETS}

    weights = pd.DataFrame(0.0, index=prices.index, columns=TARGET_ASSETS)
    scores = pd.DataFrame(np.nan, index=prices.index, columns=("ETH", "SOL", "BNB"))
    scores["ETH"] = 0.60 * trends["ETH"] + 0.40 * ratio_trends["ETH"]
    scores["SOL"] = 0.50 * trends["SOL"] + 0.50 * ratio_trends["SOL"]
    scores["BNB"] = 0.60 * bnb_trend_slow + 0.40 * bnb_ratio_slow

    for dt in prices.index:
        if pd.isna(beta.loc[dt]) or pd.isna(btc_trend.loc[dt]):
            continue
        budget = float(min(beta.loc[dt], 1.30))
        if btc_trend.loc[dt] < 0:
            weights.loc[dt, "BTC"] = budget
            continue

        eligible: list[str] = []
        if (
            pd.notna(scores.loc[dt, "ETH"])
            and scores.loc[dt, "ETH"] > 0
            and pd.notna(trends["ETH"].loc[dt])
            and trends["ETH"].loc[dt] > 0
            and pd.notna(ratio_trends["ETH"].loc[dt])
            and ratio_trends["ETH"].loc[dt] > 0
        ):
            eligible.append("ETH")
        if (
            pd.notna(scores.loc[dt, "SOL"])
            and scores.loc[dt, "SOL"] > 0
            and pd.notna(trends["SOL"].loc[dt])
            and trends["SOL"].loc[dt] > 0
            and pd.notna(ratio_trends["SOL"].loc[dt])
            and ratio_trends["SOL"].loc[dt] > 0
        ):
            eligible.append("SOL")
        if (
            pd.notna(scores.loc[dt, "BNB"])
            and scores.loc[dt, "BNB"] > 0
            and pd.notna(bnb_trend_slow.loc[dt])
            and bnb_trend_slow.loc[dt] > 0
            and pd.notna(bnb_ratio_slow.loc[dt])
            and bnb_ratio_slow.loc[dt] > 0
        ):
            eligible.append("BNB")

        eligible = sorted(eligible, key=lambda asset: scores.loc[dt, asset], reverse=True)
        if not eligible:
            weights.loc[dt, "BTC"] = budget
            continue
        if len(eligible) == 1:
            weights.loc[dt, "BTC"] = 0.50 * budget
            weights.loc[dt, eligible[0]] = 0.50 * budget
            continue

        chosen = eligible[:2]
        weights.loc[dt, "BTC"] = 0.25 * budget
        remaining = 0.75 * budget
        raw: dict[str, float] = {}
        for asset in chosen:
            vol = float(vols[asset].loc[dt]) if pd.notna(vols[asset].loc[dt]) else np.nan
            raw[asset] = (
                max(float(scores.loc[dt, asset]), 0.0) / max(vol, 1e-6)
                if np.isfinite(vol)
                else 0.0
            )
        raw_total = sum(raw.values())
        if raw_total <= 0:
            weights.loc[dt, "BTC"] = budget
            continue
        for asset in chosen:
            weights.loc[dt, asset] = remaining * raw[asset] / raw_total

        caps = {"ETH": 0.50 * budget, "SOL": 0.35 * budget, "BNB": 0.25 * budget}
        overflow = 0.0
        for asset in chosen:
            if weights.loc[dt, asset] > caps[asset]:
                overflow += weights.loc[dt, asset] - caps[asset]
                weights.loc[dt, asset] = caps[asset]
        weights.loc[dt, "BTC"] += overflow

    return weights, {
        "beta": beta,
        "btc_trend": btc_trend,
        "btc_vol": btc_vol,
        "scores": scores,
        "trend": trends,
        "ratio_trend": ratio_trends,
        "bnb_trend_slow": bnb_trend_slow,
        "bnb_ratio_slow": bnb_ratio_slow,
    }


def build_v1_raw(prices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Frozen four-asset V1 with the P3.2 no-leverage normalization."""
    four = prices.loc[:, list(TARGET_ASSETS)].dropna()
    weights, diagnostics = build_rotation_weights(four)
    gross = weights.abs().sum(axis=1)
    normalizer = pd.Series(1.0, index=weights.index, dtype=float)
    over = gross > 1.0
    normalizer.loc[over] = 1.0 / gross.loc[over]
    weights = weights.mul(normalizer, axis=0)
    return weights, diagnostics


def apply_internal_v1_band(target_weights: pd.DataFrame, band: float = INTERNAL_V1_BAND) -> pd.DataFrame:
    held = pd.Series(0.0, index=target_weights.columns, dtype=float)
    out = pd.DataFrame(0.0, index=target_weights.index, columns=target_weights.columns)
    for dt, row in target_weights.iterrows():
        if float((row - held).abs().sum()) >= band:
            held = row.copy()
        out.loc[dt] = held
    return out


def portfolio_returns_full(
    prices: pd.DataFrame,
    target_weights: pd.DataFrame,
    *,
    cost_bps: float = INTERNAL_V1_COST_BPS,
) -> pd.Series:
    target_prices = prices.loc[:, list(TARGET_ASSETS)]
    held = target_weights.loc[:, list(TARGET_ASSETS)].shift(1).fillna(0.0)
    returns = target_prices.pct_change(fill_method=None).fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    return (held * returns).sum(axis=1) - turnover * cost_bps / 10000.0


def build_features_no_dominance(
    prices: pd.DataFrame,
    cfg: FrozenBRRKConfig,
) -> pd.DataFrame:
    prices = prices.loc[:, list(cfg.assets)].copy().sort_index()
    btc = prices["BTC"]
    absolute_trend = {asset: trend_score(prices[asset]) for asset in cfg.assets}
    relative_trend = {asset: trend_score(prices[asset] / btc) for asset in cfg.alts}
    relative_df = pd.DataFrame(relative_trend)

    positive_relative = pd.DataFrame(index=prices.index)
    for asset in cfg.alts:
        valid = absolute_trend[asset].notna() & relative_trend[asset].notna()
        value = ((absolute_trend[asset] > 0) & (relative_trend[asset] > 0)).astype(float)
        positive_relative[asset] = value.where(valid)

    returns = prices.pct_change(fill_method=None)
    corr_to_btc = pd.DataFrame(index=prices.index)
    for asset in cfg.alts:
        corr_to_btc[asset] = returns[asset].rolling(30).corr(returns["BTC"])

    features = pd.DataFrame(index=prices.index)
    features["btc_trend"] = absolute_trend["BTC"]
    features["log_btc_rv30"] = np.log(rv30(btc).clip(lower=1e-6))
    features["btc_drawdown_252"] = btc / btc.rolling(252).max() - 1.0
    features["major_breadth"] = positive_relative[list(cfg.majors)].mean(axis=1)
    features["alt_breadth"] = positive_relative[list(cfg.alts)].mean(axis=1)
    features["rel_strength_mean"] = relative_df.mean(axis=1)
    features["rel_strength_dispersion"] = relative_df.std(axis=1)
    features["avg_corr30_btc"] = corr_to_btc.mean(axis=1)
    return features.loc[:, NO_DOM_FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)


def training_winsor_bounds(
    features: pd.DataFrame,
    lower: float,
    upper: float,
) -> tuple[pd.Series, pd.Series]:
    return features.quantile(lower), features.quantile(upper)


def apply_winsor(features: pd.DataFrame, lo: pd.Series, hi: pd.Series) -> pd.DataFrame:
    return features.clip(lower=lo, upper=hi, axis=1)


def _weighted_mean(series: pd.Series, weights: pd.Series) -> float:
    frame = pd.concat([series.rename("x"), weights.rename("w")], axis=1).dropna()
    if frame.empty or frame["w"].sum() <= 0:
        return 0.0
    return float((frame["x"] * frame["w"]).sum() / frame["w"].sum())


def semantic_mapping_no_dominance(
    gamma: np.ndarray,
    index: pd.Index,
    train_features: pd.DataFrame,
) -> dict[int, str]:
    features = train_features.reindex(index)
    stats: list[dict[str, float | int]] = []
    for state in range(gamma.shape[1]):
        weight = pd.Series(gamma[:, state], index=index)
        stats.append(
            {
                "state": state,
                "btc_trend": _weighted_mean(features["btc_trend"], weight),
                "major_breadth": _weighted_mean(features["major_breadth"], weight),
                "alt_breadth": _weighted_mean(features["alt_breadth"], weight),
                "rel_mean": _weighted_mean(features["rel_strength_mean"], weight),
                "drawdown": _weighted_mean(features["btc_drawdown_252"], weight),
            }
        )
    table = pd.DataFrame(stats).set_index("state")
    risk_score = (
        table["btc_trend"]
        + 0.45 * table["alt_breadth"]
        + 0.45 * table["rel_mean"]
        + 0.15 * table["drawdown"]
    )
    risk_raw = int(risk_score.idxmin())
    remaining = [state for state in table.index if state != risk_raw]
    alt_score = table.loc[remaining, "alt_breadth"] + table.loc[remaining, "rel_mean"]
    alt_raw = int(alt_score.idxmax())
    remaining = [state for state in remaining if state != alt_raw]
    major_score = table.loc[remaining, "major_breadth"] + 0.5 * table.loc[remaining, "rel_mean"]
    major_raw = int(major_score.idxmax())
    btc_lead_raw = int([state for state in remaining if state != major_raw][0])
    return {
        risk_raw: "RISK_OFF",
        btc_lead_raw: "BTC_LEAD",
        major_raw: "MAJOR_ROTATION",
        alt_raw: "ALT_EXPANSION",
    }


def fit_variational_regime_model_nd(
    train_features: pd.DataFrame,
    cfg: FrozenBRRKConfig,
    *,
    n_factors: int = 4,
) -> VariationalRegimeFitND:
    x = train_features.dropna().copy()
    if len(x) < cfg.min_train_days:
        raise TargetMathError(f"Insufficient training rows: {len(x)} < {cfg.min_train_days}")

    lo, hi = training_winsor_bounds(x, cfg.winsor_lower, cfg.winsor_upper)
    winsorized = apply_winsor(x, lo, hi)
    scaler = RobustScaler(quantile_range=(20, 80)).fit(winsorized)
    standardized = scaler.transform(winsorized)
    n_components = min(n_factors, standardized.shape[1])
    pca = PCA(
        n_components=n_components,
        whiten=True,
        random_state=cfg.random_seed,
    ).fit(standardized)
    factors = pca.transform(standardized)

    transition_prior = np.full(
        (cfg.n_states, cfg.n_states),
        cfg.sticky_offdiag_prior,
        dtype=float,
    )
    np.fill_diagonal(transition_prior, cfg.sticky_diagonal_prior)

    best: tuple[float, VariationalGaussianHMM, float, np.ndarray, np.ndarray, bool] | None = None
    for restart in range(cfg.hmm_restarts):
        model = VariationalGaussianHMM(
            n_components=cfg.n_states,
            covariance_type="full",
            n_iter=cfg.hmm_iter,
            tol=cfg.hmm_tol,
            random_state=cfg.random_seed + restart,
            transmat_prior=transition_prior,
        )
        model.fit(factors)
        log_likelihood = float(model.score(factors))
        gamma = model.predict_proba(factors)
        occupancy = gamma.mean(axis=0)
        collapsed = int((occupancy < 0.02).sum())
        converged = bool(model.monitor_.converged)
        score = log_likelihood - 500.0 * collapsed - (0.0 if converged else 1000.0)
        candidate = (score, model, log_likelihood, gamma, occupancy, converged)
        if best is None or score > best[0]:
            best = candidate

    if best is None:
        raise TargetMathError("No HMM fit candidate was produced")
    _, model, log_likelihood, gamma, occupancy, converged = best
    mapping = semantic_mapping_no_dominance(gamma, x.index, x)
    return VariationalRegimeFitND(
        model=model,
        scaler=scaler,
        pca=pca,
        winsor_lo=lo,
        winsor_hi=hi,
        raw_to_semantic=mapping,
        semantic_to_raw={semantic: raw for raw, semantic in mapping.items()},
        training_log_likelihood=log_likelihood,
        occupancy={state: float(value) for state, value in enumerate(occupancy)},
        converged=converged,
    )


def semantic_transition_matrix(fit: VariationalRegimeFitND) -> np.ndarray:
    matrix = np.zeros((len(SEMANTIC_STATES), len(SEMANTIC_STATES)), dtype=float)
    raw = fit.model.transmat_
    for i, source in enumerate(SEMANTIC_STATES):
        raw_source = fit.semantic_to_raw[source]
        for j, destination in enumerate(SEMANTIC_STATES):
            raw_destination = fit.semantic_to_raw[destination]
            matrix[i, j] = float(raw[raw_source, raw_destination])
    row_sum = matrix.sum(axis=1, keepdims=True)
    return np.divide(matrix, row_sum, out=np.full_like(matrix, 0.25), where=row_sum > 0)


def fit_state_v1_distribution(
    v1_returns: pd.Series,
    train_features: pd.DataFrame,
    fit: VariationalRegimeFitND,
    cfg: FrozenBRRKConfig,
) -> dict[str, object]:
    common = v1_returns.dropna().index.intersection(train_features.dropna().index)
    y = v1_returns.loc[common].astype(float)
    posterior = fit.posterior(train_features.loc[common]).reindex(common)
    common = y.index.intersection(posterior.dropna().index)
    y = y.loc[common]
    posterior = posterior.loc[common]
    if y.empty:
        raise TargetMathError("No common V1 return and regime rows for state distribution")

    global_mean = float(y.mean())
    global_var = max(float(y.var(ddof=0)), 1e-10)
    result: dict[str, object] = {
        "global_mean": global_mean,
        "global_var": global_var,
        "means": {},
        "variances": {},
        "effective_n": {},
    }
    values = y.to_numpy(float)
    means = result["means"]
    variances = result["variances"]
    effective_n = result["effective_n"]
    assert isinstance(means, dict) and isinstance(variances, dict) and isinstance(effective_n, dict)

    for state in SEMANTIC_STATES:
        weights = np.maximum(posterior[state].to_numpy(float), 0.0)
        if weights.sum() <= 0:
            raw_mean = global_mean
            raw_var = global_var
            n_eff = 1.0
        else:
            weights = weights / weights.sum()
            raw_mean = float(np.sum(values * weights))
            raw_var = float(np.sum(((values - raw_mean) ** 2) * weights))
            n_eff = float(1.0 / np.sum(weights**2))
        shrink = n_eff / (n_eff + cfg.shrinkage_strength)
        mean = shrink * raw_mean + (1.0 - shrink) * global_mean
        variance = shrink * max(raw_var, 1e-10) + (1.0 - shrink) * global_var
        means[state] = float(mean)
        variances[state] = float(max(variance, 1e-10))
        effective_n[state] = float(n_eff)
    return result


def sample_v1_paths(
    current_posterior: pd.Series,
    fit: VariationalRegimeFitND,
    distribution: dict[str, object],
    cfg: FrozenBRRKConfig,
    *,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    probabilities = np.array(
        [max(float(current_posterior.get(state, 0.0)), 0.0) for state in SEMANTIC_STATES],
        dtype=float,
    )
    probabilities /= max(probabilities.sum(), 1e-12)
    transition = semantic_transition_matrix(fit)
    current_state = rng.choice(len(SEMANTIC_STATES), size=cfg.scenario_count, p=probabilities)
    paths = np.zeros((cfg.scenario_count, cfg.forecast_horizon_days), dtype=float)

    means = distribution["means"]
    variances = distribution["variances"]
    if not isinstance(means, dict) or not isinstance(variances, dict):
        raise TargetMathError("Invalid state-conditioned return distribution")

    for day in range(cfg.forecast_horizon_days):
        next_state = np.empty(cfg.scenario_count, dtype=int)
        for state_index in range(len(SEMANTIC_STATES)):
            loc = np.where(current_state == state_index)[0]
            if len(loc):
                next_state[loc] = rng.choice(
                    len(SEMANTIC_STATES),
                    size=len(loc),
                    p=transition[state_index],
                )
        current_state = next_state

        for state_index, state in enumerate(SEMANTIC_STATES):
            loc = np.where(current_state == state_index)[0]
            if not len(loc):
                continue
            mean = float(means[state])
            variance = float(variances[state])
            scale = math.sqrt(max(variance * (STUDENT_T_DF - 2.0) / STUDENT_T_DF, 1e-12))
            paths[loc, day] = mean + rng.standard_t(STUDENT_T_DF, size=len(loc)) * scale
    return np.maximum(paths, -0.999)


def path_tail_risk_corrected(v1_paths: np.ndarray, scale: float) -> tuple[float, float]:
    portfolio = scale * v1_paths
    nav = np.cumprod(np.maximum(1.0 + portfolio, 1e-12), axis=1)
    terminal = nav[:, -1] - 1.0
    losses = -terminal
    quantile = float(np.quantile(losses, 0.95))
    tail = losses[losses >= quantile]
    cvar95 = float(tail.mean()) if len(tail) else quantile

    nav_with_origin = np.concatenate([np.ones((len(nav), 1)), nav], axis=1)
    peaks = np.maximum.accumulate(nav_with_origin, axis=1)
    drawdown = nav_with_origin / np.maximum(peaks, 1e-12) - 1.0
    max_drawdown = drawdown.min(axis=1)
    drawdown_quantile = float(np.quantile(max_drawdown, 0.05))
    drawdown_tail = max_drawdown[max_drawdown <= drawdown_quantile]
    cdar95 = (
        float(-drawdown_tail.mean()) if len(drawdown_tail) else float(-drawdown_quantile)
    )
    return cvar95, cdar95


def expected_log_terminal(v1_paths: np.ndarray, scale: float) -> float:
    wealth = np.maximum(1.0 + scale * v1_paths, 1e-12)
    return float(np.mean(np.log(wealth).sum(axis=1)))


def safe_max_scale_corrected(v1_paths: np.ndarray, budget: float) -> tuple[float, float, float]:
    cvar_full, cdar_full = path_tail_risk_corrected(v1_paths, 1.0)
    if cvar_full <= budget and cdar_full <= budget:
        return 1.0, cvar_full, cdar_full
    low, high = 0.0, 1.0
    for _ in range(28):
        midpoint = 0.5 * (low + high)
        cvar, cdar = path_tail_risk_corrected(v1_paths, midpoint)
        if cvar <= budget and cdar <= budget:
            low = midpoint
        else:
            high = midpoint
    cvar, cdar = path_tail_risk_corrected(v1_paths, low)
    return float(low), float(cvar), float(cdar)


def choose_scale_corrected(v1_paths: np.ndarray, budget: float = RISK_BUDGET) -> dict[str, float]:
    safe_max, safe_cvar, safe_cdar = safe_max_scale_corrected(v1_paths, budget)
    cvar_full, cdar_full = path_tail_risk_corrected(v1_paths, 1.0)
    if safe_max <= 1e-8:
        return {
            "scale": 0.0,
            "safe_max": 0.0,
            "expected_log20": 0.0,
            "scenario_cvar95": 0.0,
            "scenario_cdar95": 0.0,
            "full_scale_cvar95": cvar_full,
            "full_scale_cdar95": cdar_full,
        }

    optimized = minimize_scalar(
        lambda value: -expected_log_terminal(v1_paths, float(value)),
        bounds=(0.0, safe_max),
        method="bounded",
        options={"xatol": 1e-4},
    )
    candidates = [0.0, float(safe_max)]
    if optimized.success and np.isfinite(optimized.x):
        candidates.append(float(np.clip(optimized.x, 0.0, safe_max)))
    scores = [expected_log_terminal(v1_paths, value) for value in candidates]
    chosen = float(candidates[int(np.argmax(scores))])
    cvar, cdar = path_tail_risk_corrected(v1_paths, chosen)
    return {
        "scale": chosen,
        "safe_max": float(safe_max),
        "expected_log20": float(max(scores)),
        "scenario_cvar95": float(cvar),
        "scenario_cdar95": float(cdar),
        "full_scale_cvar95": float(cvar_full),
        "full_scale_cdar95": float(cdar_full),
    }


def eligible_refit_dates(features: pd.DataFrame, cfg: FrozenBRRKConfig) -> list[pd.Timestamp]:
    clean = features.dropna()
    dates: list[pd.Timestamp] = []
    for dt in clean.index:
        if len(clean.loc[:dt]) < cfg.min_train_days:
            continue
        if not dates or (dt - dates[-1]).days >= cfg.refit_every_days:
            dates.append(pd.Timestamp(dt))
    return dates


def current_defensive_state(
    prices: pd.DataFrame,
    features: pd.DataFrame,
    v1_returns: pd.Series,
    cfg: FrozenBRRKConfig,
) -> dict[str, object]:
    """Return the BRRK-0011 defensive state active on the latest signal session."""
    dates = eligible_refit_dates(features, cfg)
    if not dates:
        raise TargetMathError("No eligible BRRK-0011 regime refit date")
    refit_date = dates[-1]
    train_features = features.loc[:refit_date]
    fit = fit_variational_regime_model_nd(train_features, cfg, n_factors=4)
    posterior = fit.filtered_posterior(features.loc[:refit_date]).iloc[-1]
    distribution = fit_state_v1_distribution(
        v1_returns.loc[:refit_date],
        train_features,
        fit,
        cfg,
    )
    paths = sample_v1_paths(
        posterior,
        fit,
        distribution,
        cfg,
        seed=cfg.random_seed + int(refit_date.strftime("%Y%m%d")),
    )
    allocation = choose_scale_corrected(paths, RISK_BUDGET)
    meta_scale = float(allocation["scale"])
    riskoff_probability = float(np.clip(posterior.get("RISK_OFF", 0.0), 0.0, 1.0))
    defensive_scale = float(1.0 - riskoff_probability * (1.0 - meta_scale))
    defensive_scale = float(np.clip(defensive_scale, 0.0, 1.0))
    risk_state = str(posterior.astype(float).idxmax())
    return {
        "refit_date": refit_date,
        "posterior": {state: float(posterior[state]) for state in SEMANTIC_STATES},
        "risk_state": risk_state,
        "riskoff_probability": riskoff_probability,
        "meta_scale": meta_scale,
        "defensive_scale": defensive_scale,
        "allocation": allocation,
        "converged": bool(fit.converged),
        "pca_variance": float(fit.pca.explained_variance_ratio_.sum()),
        "feature_snapshot": {
            name: float(features.loc[refit_date, name]) for name in NO_DOM_FEATURE_COLUMNS
        },
    }
