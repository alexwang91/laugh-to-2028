from dataclasses import dataclass

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from scipy.special import logsumexp
from scipy.stats import multivariate_normal
from sklearn.preprocessing import RobustScaler

from config import RegimeKellyConfig
from features import apply_winsor, training_winsor_bounds


SEMANTIC_STATES = ("RISK_OFF", "BTC_LEAD", "MAJOR_ROTATION", "ALT_EXPANSION")


@dataclass
class RegimeFit:
    model: GaussianHMM
    scaler: RobustScaler
    winsor_lo: pd.Series
    winsor_hi: pd.Series
    raw_to_semantic: dict[int, str]
    semantic_to_raw: dict[str, int]
    training_log_likelihood: float
    occupancy: dict[int, float]

    def posterior(self, features: pd.DataFrame) -> pd.DataFrame:
        """Smoothed posterior, for training diagnostics / state-conditional fitting only."""
        x = apply_winsor(features, self.winsor_lo, self.winsor_hi).dropna()
        z = self.scaler.transform(x)
        gamma = self.model.predict_proba(z)
        raw = pd.DataFrame(gamma, index=x.index, columns=range(self.model.n_components))
        out = pd.DataFrame(0.0, index=x.index, columns=SEMANTIC_STATES)
        for r, semantic in self.raw_to_semantic.items():
            out[semantic] = raw[r]
        return out

    def filtered_posterior(self, features: pd.DataFrame) -> pd.DataFrame:
        """Forward-filtered P(S_t | X_1:t); safe for trading / walk-forward decisions."""
        x = apply_winsor(features, self.winsor_lo, self.winsor_hi).dropna()
        z = self.scaler.transform(x)
        k = self.model.n_components
        log_emission = np.empty((len(z), k), dtype=float)
        for s in range(k):
            log_emission[:, s] = multivariate_normal.logpdf(
                z,
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
        for t in range(1, len(z)):
            pred = np.array([
                logsumexp(log_alpha[t - 1] + log_trans[:, j])
                for j in range(k)
            ])
            log_alpha[t] = pred + log_emission[t]
            log_alpha[t] -= logsumexp(log_alpha[t])

        raw_prob = np.exp(log_alpha)
        raw = pd.DataFrame(raw_prob, index=x.index, columns=range(k))
        out = pd.DataFrame(0.0, index=x.index, columns=SEMANTIC_STATES)
        for r, semantic in self.raw_to_semantic.items():
            out[semantic] = raw[r]
        return out


def _semantic_mapping(
    gamma: np.ndarray,
    index: pd.Index,
    train_features: pd.DataFrame,
    train_forward_returns: pd.DataFrame,
) -> dict[int, str]:
    stats = []
    fwd = train_forward_returns.reindex(index)
    f = train_features.reindex(index)
    for s in range(gamma.shape[1]):
        w = pd.Series(gamma[:, s], index=index)
        def wmean(series: pd.Series) -> float:
            x = pd.concat([series, w], axis=1).dropna()
            if x.empty:
                return 0.0
            ww = x.iloc[:, 1]
            return float((x.iloc[:, 0] * ww).sum() / max(ww.sum(), 1e-12))
        stats.append({
            "state": s,
            "btc_trend": wmean(f["btc_trend"]),
            "major_breadth": wmean(f["major_breadth"]),
            "alt_breadth": wmean(f["alt_breadth"]),
            "rel_mean": wmean(f["rel_strength_mean"]),
            "dom30": wmean(f["btc_dom_30"]),
            "btc_fwd": wmean(fwd["BTC"]) if "BTC" in fwd else 0.0,
        })
    st = pd.DataFrame(stats).set_index("state")

    risk_score = st["btc_trend"] + 0.5 * st["alt_breadth"] + 0.5 * st["btc_fwd"]
    risk_raw = int(risk_score.idxmin())

    remaining = [s for s in st.index if s != risk_raw]
    alt_score = st.loc[remaining, "alt_breadth"] + st.loc[remaining, "rel_mean"] - 0.05 * st.loc[remaining, "dom30"]
    alt_raw = int(alt_score.idxmax())

    remaining = [s for s in remaining if s != alt_raw]
    major_score = st.loc[remaining, "major_breadth"] + st.loc[remaining, "rel_mean"]
    major_raw = int(major_score.idxmax())
    btc_lead_raw = int([s for s in remaining if s != major_raw][0])

    return {
        risk_raw: "RISK_OFF",
        btc_lead_raw: "BTC_LEAD",
        major_raw: "MAJOR_ROTATION",
        alt_raw: "ALT_EXPANSION",
    }


def fit_regime_model(
    train_features: pd.DataFrame,
    train_forward_returns: pd.DataFrame,
    cfg: RegimeKellyConfig,
) -> RegimeFit:
    common = train_features.dropna().index.intersection(train_forward_returns.dropna().index)
    x = train_features.loc[common]
    y = train_forward_returns.loc[common]
    if len(x) < cfg.min_train_days:
        raise ValueError(f"Insufficient training rows: {len(x)} < {cfg.min_train_days}")

    lo, hi = training_winsor_bounds(x, cfg.winsor_lower, cfg.winsor_upper)
    xw = apply_winsor(x, lo, hi)
    scaler = RobustScaler(quantile_range=(20, 80)).fit(xw)
    z = scaler.transform(xw)

    trans_prior = np.full((cfg.n_states, cfg.n_states), cfg.sticky_offdiag_prior, dtype=float)
    np.fill_diagonal(trans_prior, cfg.sticky_diagonal_prior)

    best = None
    for i in range(cfg.hmm_restarts):
        seed = cfg.random_seed + i
        model = GaussianHMM(
            n_components=cfg.n_states,
            covariance_type="full",
            n_iter=cfg.hmm_iter,
            tol=cfg.hmm_tol,
            random_state=seed,
            transmat_prior=trans_prior,
            min_covar=1e-4,
        )
        model.fit(z)
        ll = float(model.score(z))
        gamma = model.predict_proba(z)
        occ = gamma.mean(axis=0)
        collapsed = int((occ < 0.02).sum())
        score = ll - 500.0 * collapsed
        if best is None or score > best[0]:
            best = (score, model, ll, gamma, occ)

    _, model, ll, gamma, occ = best
    mapping = _semantic_mapping(gamma, common, x, y)
    return RegimeFit(
        model=model,
        scaler=scaler,
        winsor_lo=lo,
        winsor_hi=hi,
        raw_to_semantic=mapping,
        semantic_to_raw={v: k for k, v in mapping.items()},
        training_log_likelihood=ll,
        occupancy={i: float(v) for i, v in enumerate(occ)},
    )
