import numpy as np
import pandas as pd

from config import RegimeKellyConfig
from features import rv30, trend_score


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


def build_features_no_dominance(prices: pd.DataFrame, cfg: RegimeKellyConfig) -> pd.DataFrame:
    """Price-only state features. All inputs are observable by the close of day t."""
    prices = prices.loc[:, list(cfg.assets)].copy().sort_index()
    btc = prices["BTC"]

    abs_trend = {a: trend_score(prices[a]) for a in cfg.assets}
    rel_trend = {a: trend_score(prices[a] / btc) for a in cfg.alts}
    rel_df = pd.DataFrame(rel_trend)

    positive_rel = pd.DataFrame(index=prices.index)
    for a in cfg.alts:
        valid = abs_trend[a].notna() & rel_trend[a].notna()
        x = ((abs_trend[a] > 0) & (rel_trend[a] > 0)).astype(float)
        positive_rel[a] = x.where(valid)

    returns = prices.pct_change(fill_method=None)
    corr_to_btc = pd.DataFrame(index=prices.index)
    for a in cfg.alts:
        corr_to_btc[a] = returns[a].rolling(30).corr(returns["BTC"])

    f = pd.DataFrame(index=prices.index)
    f["btc_trend"] = abs_trend["BTC"]
    f["log_btc_rv30"] = np.log(rv30(btc).clip(lower=1e-6))
    f["btc_drawdown_252"] = btc / btc.rolling(252).max() - 1.0
    f["major_breadth"] = positive_rel[list(cfg.majors)].mean(axis=1)
    f["alt_breadth"] = positive_rel[list(cfg.alts)].mean(axis=1)
    f["rel_strength_mean"] = rel_df.mean(axis=1)
    f["rel_strength_dispersion"] = rel_df.std(axis=1)
    f["avg_corr30_btc"] = corr_to_btc.mean(axis=1)

    return f.loc[:, NO_DOM_FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)


def daily_log_returns(prices: pd.DataFrame, cfg: RegimeKellyConfig) -> pd.DataFrame:
    return np.log(prices.loc[:, list(cfg.assets)] / prices.loc[:, list(cfg.assets)].shift(1))
