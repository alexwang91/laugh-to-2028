"""`forward_log_returns` used to live here (deleted, backlog F14): its only
caller was `regime_model.fit_regime_model`, which was itself deleted for
having no callers of its own anywhere in the repo. See
`regime_model.py`'s module docstring for the leakage risk that combination
carried."""
import math

import numpy as np
import pandas as pd

from config import FEATURE_COLUMNS, RegimeKellyConfig


HORIZONS = (20, 60, 120, 240)
TREND_WEIGHTS = (0.15, 0.25, 0.30, 0.30)


def trend_score(price: pd.Series) -> pd.Series:
    lr = np.log(price).diff()
    out = pd.Series(0.0, index=price.index, dtype=float)
    valid = pd.Series(True, index=price.index)
    for h, w in zip(HORIZONS, TREND_WEIGHTS):
        mom = np.log(price / price.shift(h))
        scale = lr.rolling(h).std() * math.sqrt(h)
        z = mom / scale.replace(0, np.nan)
        comp = np.tanh(z)
        out = out + w * comp
        valid &= comp.notna()
    return out.where(valid)


def rv30(price: pd.Series) -> pd.Series:
    return np.log(price).diff().rolling(30).std() * math.sqrt(365)


def build_features(prices: pd.DataFrame, btc_dominance: pd.Series, cfg: RegimeKellyConfig) -> pd.DataFrame:
    prices = prices.loc[:, list(cfg.assets)].copy().sort_index()
    btc = prices["BTC"]
    dom = btc_dominance.reindex(prices.index).ffill()

    abs_trend = {a: trend_score(prices[a]) for a in cfg.assets}
    rel_trend = {a: trend_score(prices[a] / btc) for a in cfg.alts}

    positive_rel = pd.DataFrame({
        a: ((abs_trend[a] > 0) & (rel_trend[a] > 0)).astype(float)
        for a in cfg.alts
    })
    rel_df = pd.DataFrame(rel_trend)

    returns = prices.pct_change()
    corr_to_btc = pd.DataFrame(index=prices.index)
    for a in cfg.alts:
        corr_to_btc[a] = returns[a].rolling(30).corr(returns["BTC"])

    f = pd.DataFrame(index=prices.index)
    f["btc_trend"] = abs_trend["BTC"]
    f["log_btc_rv30"] = np.log(rv30(btc).clip(lower=1e-6))
    f["btc_drawdown_252"] = btc / btc.rolling(252).max() - 1.0
    f["btc_dom_30"] = dom - dom.shift(30)
    f["btc_dom_90"] = dom - dom.shift(90)
    f["major_breadth"] = positive_rel[list(cfg.majors)].mean(axis=1)
    f["alt_breadth"] = positive_rel[list(cfg.alts)].mean(axis=1)
    f["rel_strength_mean"] = rel_df.mean(axis=1)
    f["rel_strength_dispersion"] = rel_df.std(axis=1)
    f["avg_corr30_btc"] = corr_to_btc.mean(axis=1)

    return f.loc[:, FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)


def training_winsor_bounds(x: pd.DataFrame, lower: float, upper: float) -> tuple[pd.Series, pd.Series]:
    return x.quantile(lower), x.quantile(upper)


def apply_winsor(x: pd.DataFrame, lo: pd.Series, hi: pd.Series) -> pd.DataFrame:
    return x.clip(lower=lo, upper=hi, axis=1)
