from dataclasses import dataclass

import numpy as np
import pandas as pd
from hmmlearn.vhmm import VariationalGaussianHMM
from scipy.special import logsumexp
from scipy.stats import multivariate_normal
from sklearn.decomposition import PCA
from sklearn.preprocessing import RobustScaler

from config import RegimeKellyConfig
from features import apply_winsor, training_winsor_bounds
from regime_model import SEMANTIC_STATES


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

    def _transform(self, features: pd.DataFrame):
        x = apply_winsor(features, self.winsor_lo, self.winsor_hi).dropna()
        z = self.scaler.transform(x)
        f = self.pca.transform(z)
        return x, f

    def posterior(self, features: pd.DataFrame) -> pd.DataFrame:
        """Smoothed posterior for training-only parameter estimation."""
        x, f = self._transform(features)
        gamma = self.model.predict_proba(f)
        raw = pd.DataFrame(gamma, index=x.index, columns=range(self.model.n_components))
        out = pd.DataFrame(0.0, index=x.index, columns=SEMANTIC_STATES)
        for r, semantic in self.raw_to_semantic.items():
            out[semantic] = raw[r]
        return out

    def filtered_posterior(self, features: pd.DataFrame) -> pd.DataFrame:
        """Forward-filtered P(S_t | X_1:t), safe for walk-forward decisions."""
        x, f = self._transform(features)
        k = self.model.n_components
        log_emission = np.empty((len(f), k), dtype=float)
        for s in range(k):
            log_emission[:, s] = multivariate_normal.logpdf(
                f,
                mean=self.model.means_[s],
                cov=self.model.covars_[s],
                allow_singular=True,
            )
        eps = 1e-300
        log_start = np.log(np.maximum(self.model.startprob_, eps))
        log_trans = np.log(np.maximum(self.model.transmat_, eps))
        log_alpha = np.empty_like(log_emission)
        log_alpha[0] = log_start + log_emission[0]
        log_alpha[0] -= logsumexp(log_alpha[0])
        for t in range(1, len(f)):
            pred = np.array([
                logsumexp(log_alpha[t - 1] + log_trans[:, j])
                for j in range(k)
            ])
            log_alpha[t] = pred + log_emission[t]
            log_alpha[t] -= logsumexp(log_alpha[t])
        raw = pd.DataFrame(np.exp(log_alpha), index=x.index, columns=range(k))
        out = pd.DataFrame(0.0, index=x.index, columns=SEMANTIC_STATES)
        for r, semantic in self.raw_to_semantic.items():
            out[semantic] = raw[r]
        return out


def _wmean(series: pd.Series, weights: pd.Series) -> float:
    x = pd.concat([series.rename("x"), weights.rename("w")], axis=1).dropna()
    if x.empty or x["w"].sum() <= 0:
        return 0.0
    return float((x["x"] * x["w"]).sum() / x["w"].sum())


def semantic_mapping_no_dominance(
    gamma: np.ndarray,
    index: pd.Index,
    train_features: pd.DataFrame,
) -> dict[int, str]:
    """Map raw labels using contemporaneous price-only state characteristics."""
    f = train_features.reindex(index)
    stats = []
    for s in range(gamma.shape[1]):
        w = pd.Series(gamma[:, s], index=index)
        stats.append({
            "state": s,
            "btc_trend": _wmean(f["btc_trend"], w),
            "major_breadth": _wmean(f["major_breadth"], w),
            "alt_breadth": _wmean(f["alt_breadth"], w),
            "rel_mean": _wmean(f["rel_strength_mean"], w),
            "drawdown": _wmean(f["btc_drawdown_252"], w),
        })
    st = pd.DataFrame(stats).set_index("state")

    # Weak absolute trend, weak breadth and weak relative strength define Risk-Off.
    risk_score = st["btc_trend"] + 0.45 * st["alt_breadth"] + 0.45 * st["rel_mean"] + 0.15 * st["drawdown"]
    risk_raw = int(risk_score.idxmin())

    remaining = [s for s in st.index if s != risk_raw]
    alt_score = st.loc[remaining, "alt_breadth"] + st.loc[remaining, "rel_mean"]
    alt_raw = int(alt_score.idxmax())

    remaining = [s for s in remaining if s != alt_raw]
    major_score = st.loc[remaining, "major_breadth"] + 0.5 * st.loc[remaining, "rel_mean"]
    major_raw = int(major_score.idxmax())
    btc_lead_raw = int([s for s in remaining if s != major_raw][0])

    return {
        risk_raw: "RISK_OFF",
        btc_lead_raw: "BTC_LEAD",
        major_raw: "MAJOR_ROTATION",
        alt_raw: "ALT_EXPANSION",
    }


def fit_variational_regime_model_nd(
    train_features: pd.DataFrame,
    cfg: RegimeKellyConfig,
    n_factors: int = 4,
) -> VariationalRegimeFitND:
    x = train_features.dropna().copy()
    if len(x) < cfg.min_train_days:
        raise ValueError(f"Insufficient training rows: {len(x)} < {cfg.min_train_days}")

    lo, hi = training_winsor_bounds(x, cfg.winsor_lower, cfg.winsor_upper)
    xw = apply_winsor(x, lo, hi)
    scaler = RobustScaler(quantile_range=(20, 80)).fit(xw)
    z = scaler.transform(xw)
    n_components = min(n_factors, z.shape[1])
    pca = PCA(n_components=n_components, whiten=True, random_state=cfg.random_seed).fit(z)
    factors = pca.transform(z)

    trans_prior = np.full((cfg.n_states, cfg.n_states), cfg.sticky_offdiag_prior, dtype=float)
    np.fill_diagonal(trans_prior, cfg.sticky_diagonal_prior)

    best = None
    for i in range(cfg.hmm_restarts):
        model = VariationalGaussianHMM(
            n_components=cfg.n_states,
            covariance_type="full",
            n_iter=cfg.hmm_iter,
            tol=cfg.hmm_tol,
            random_state=cfg.random_seed + i,
            transmat_prior=trans_prior,
        )
        model.fit(factors)
        ll = float(model.score(factors))
        gamma = model.predict_proba(factors)
        occ = gamma.mean(axis=0)
        collapsed = int((occ < 0.02).sum())
        converged = bool(model.monitor_.converged)
        score = ll - 500.0 * collapsed - (0.0 if converged else 1000.0)
        if best is None or score > best[0]:
            best = (score, model, ll, gamma, occ, converged)

    _, model, ll, gamma, occ, converged = best
    mapping = semantic_mapping_no_dominance(gamma, x.index, x)
    return VariationalRegimeFitND(
        model=model,
        scaler=scaler,
        pca=pca,
        winsor_lo=lo,
        winsor_hi=hi,
        raw_to_semantic=mapping,
        semantic_to_raw={v: k for k, v in mapping.items()},
        training_log_likelihood=ll,
        occupancy={i: float(v) for i, v in enumerate(occ)},
        converged=converged,
    )
