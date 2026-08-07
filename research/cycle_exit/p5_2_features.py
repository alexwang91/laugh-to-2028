from __future__ import annotations

import math
from typing import Mapping

import numpy as np
import pandas as pd


DAILY_ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
AVAILABLE_FEATURES = (
    "btc_log_return_20d",
    "btc_log_return_40d",
    "btc_log_slope_20d_ann",
    "btc_log_slope_40d_ann",
    "btc_kama_gap",
    "btc_kama_slope_10d",
    "btc_distance_from_90d_high",
    "btc_consolidation_duration_5pct",
    "btc_rv20_ann",
    "btc_rv20_to_rv60",
    "btc_daily_rsi14",
    "btc_daily_rsi28",
    "btc_4h_rsi14",
    "btc_4h_rsi28",
    "btc_price_rsi_rank_divergence_20d",
    "btc_rsi14_extreme_persistence_14d",
    "btc_rsi14_failure_from_14d_max",
    "eth_btc_log_return_20d",
    "sol_btc_log_return_20d",
    "bnb_btc_log_return_20d",
    "eth_btc_log_return_40d",
    "sol_btc_log_return_40d",
    "bnb_btc_log_return_40d",
    "brkk_return_dispersion_20d",
    "alt_outperformance_breadth_20d",
    "canonical5_outperformance_breadth_20d",
    "high_beta_participation_20d",
    "breadth_acceleration_10d",
    "breadth_contraction_from_10d_max",
)


def _require_daily_panel(prices: pd.DataFrame) -> pd.DataFrame:
    if tuple(prices.columns) != DAILY_ASSETS:
        raise ValueError(f"daily columns must be exactly {DAILY_ASSETS}")
    out = prices.astype(float).sort_index()
    if out.index.has_duplicates:
        raise ValueError("daily index contains duplicates")
    if not isinstance(out.index, pd.DatetimeIndex):
        raise ValueError("daily index must be DatetimeIndex")
    if out.isna().any().any():
        raise ValueError("daily price panel contains missing values")
    if (out <= 0).any().any():
        raise ValueError("daily price panel contains non-positive values")
    if len(out) > 1:
        expected = pd.date_range(out.index.min(), out.index.max(), freq="D")
        if not out.index.equals(expected):
            raise ValueError("daily price panel must be contiguous UTC calendar days")
    return out


def wilder_rsi(series: pd.Series, n: int) -> pd.Series:
    diff = series.diff()
    gain = diff.clip(lower=0.0)
    loss = (-diff.clip(upper=0.0))
    avg_gain = gain.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    avg_loss = loss.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + rs)
    rsi = rsi.where(avg_loss > 0.0, 100.0)
    both_zero = (avg_gain == 0.0) & (avg_loss == 0.0)
    return rsi.where(~both_zero, 50.0)


def rolling_log_slope_ann(series: pd.Series, n: int) -> pd.Series:
    x = np.arange(n, dtype=float)
    x_centered = x - x.mean()
    denominator = float(np.dot(x_centered, x_centered))

    def slope(window: np.ndarray) -> float:
        y = np.log(np.asarray(window, dtype=float))
        return float(np.dot(x_centered, y - y.mean()) / denominator * 365.0)

    return series.rolling(n, min_periods=n).apply(slope, raw=True)


def kaufman_adaptive_moving_average(
    series: pd.Series, er_window: int = 10, fast: int = 2, slow: int = 30
) -> pd.Series:
    change = (series - series.shift(er_window)).abs()
    volatility = series.diff().abs().rolling(er_window, min_periods=er_window).sum()
    er = (change / volatility.replace(0.0, np.nan)).clip(0.0, 1.0).fillna(0.0)
    fast_sc = 2.0 / (fast + 1.0)
    slow_sc = 2.0 / (slow + 1.0)
    smoothing = (er * (fast_sc - slow_sc) + slow_sc) ** 2

    values = series.astype(float).to_numpy()
    sc = smoothing.to_numpy()
    out = np.full(len(series), np.nan, dtype=float)
    if len(series) == 0:
        return pd.Series(out, index=series.index)
    out[0] = values[0]
    for i in range(1, len(values)):
        if not np.isfinite(values[i]):
            continue
        prev = out[i - 1] if np.isfinite(out[i - 1]) else values[i - 1]
        out[i] = prev + sc[i] * (values[i] - prev)
    return pd.Series(out, index=series.index, name="kama")


def rolling_current_percentile_rank(series: pd.Series, n: int) -> pd.Series:
    def rank(window: np.ndarray) -> float:
        values = np.asarray(window, dtype=float)
        current = values[-1]
        # Mid-rank for ties keeps the metric deterministic and bounded [0,1].
        less = float(np.sum(values < current))
        equal = float(np.sum(values == current))
        return (less + 0.5 * equal) / len(values)

    return series.rolling(n, min_periods=n).apply(rank, raw=True)


def consecutive_true_duration(mask: pd.Series) -> pd.Series:
    values = mask.fillna(False).astype(bool).to_numpy()
    out = np.zeros(len(values), dtype=float)
    run = 0
    for i, flag in enumerate(values):
        run = run + 1 if flag else 0
        out[i] = run
    return pd.Series(out, index=mask.index)


def _aligned_4h_rsi(btc_4h_close: pd.Series, daily_index: pd.DatetimeIndex, n: int) -> pd.Series:
    s = btc_4h_close.astype(float).sort_index()
    if s.index.has_duplicates:
        raise ValueError("BTC 4h index contains duplicates")
    if (s <= 0).any():
        raise ValueError("BTC 4h close contains non-positive values")
    rsi = wilder_rsi(s, n)
    # The 4h series is indexed by the bar-completion boundary. Exact reindex at
    # daily 00:00 UTC therefore excludes the new bar opening at that boundary.
    return rsi.reindex(daily_index)


def build_feature_panel(daily_prices: pd.DataFrame, btc_4h_close: pd.Series) -> pd.DataFrame:
    prices = _require_daily_panel(daily_prices)
    btc = prices["BTC"]
    log_price = np.log(prices)
    log_returns = log_price.diff()

    features = pd.DataFrame(index=prices.index)

    features["btc_log_return_20d"] = np.log(btc / btc.shift(20))
    features["btc_log_return_40d"] = np.log(btc / btc.shift(40))
    features["btc_log_slope_20d_ann"] = rolling_log_slope_ann(btc, 20)
    features["btc_log_slope_40d_ann"] = rolling_log_slope_ann(btc, 40)

    kama = kaufman_adaptive_moving_average(btc, 10, 2, 30)
    features["btc_kama_gap"] = btc / kama - 1.0
    features["btc_kama_slope_10d"] = kama / kama.shift(10) - 1.0

    high90 = btc.rolling(90, min_periods=90).max()
    features["btc_distance_from_90d_high"] = btc / high90 - 1.0
    features["btc_consolidation_duration_5pct"] = consecutive_true_duration(
        btc >= 0.95 * high90
    )

    rv20 = log_returns["BTC"].rolling(20, min_periods=20).std() * math.sqrt(365.0)
    rv60 = log_returns["BTC"].rolling(60, min_periods=60).std() * math.sqrt(365.0)
    features["btc_rv20_ann"] = rv20
    features["btc_rv20_to_rv60"] = rv20 / rv60.replace(0.0, np.nan)

    rsi14 = wilder_rsi(btc, 14)
    rsi28 = wilder_rsi(btc, 28)
    features["btc_daily_rsi14"] = rsi14
    features["btc_daily_rsi28"] = rsi28
    features["btc_4h_rsi14"] = _aligned_4h_rsi(btc_4h_close, prices.index, 14)
    features["btc_4h_rsi28"] = _aligned_4h_rsi(btc_4h_close, prices.index, 28)

    price_rank = rolling_current_percentile_rank(btc, 20)
    rsi_rank = rolling_current_percentile_rank(rsi14, 20)
    features["btc_price_rsi_rank_divergence_20d"] = price_rank - rsi_rank
    features["btc_rsi14_extreme_persistence_14d"] = (
        (rsi14 >= 70.0).astype(float).rolling(14, min_periods=14).mean()
    )
    features["btc_rsi14_failure_from_14d_max"] = (
        rsi14.rolling(14, min_periods=14).max() - rsi14
    )

    for asset in ("ETH", "SOL", "BNB"):
        ratio = prices[asset] / btc
        prefix = asset.lower()
        features[f"{prefix}_btc_log_return_20d"] = np.log(ratio / ratio.shift(20))
        features[f"{prefix}_btc_log_return_40d"] = np.log(ratio / ratio.shift(40))

    ret20 = np.log(prices / prices.shift(20))
    features["brkk_return_dispersion_20d"] = ret20[["BTC", "ETH", "SOL", "BNB"]].std(
        axis=1, ddof=0
    )

    btc20 = ret20["BTC"]
    features["alt_outperformance_breadth_20d"] = (
        ret20[["ETH", "SOL", "BNB"]].gt(btc20, axis=0).mean(axis=1)
    )
    features["canonical5_outperformance_breadth_20d"] = (
        ret20[["ETH", "SOL", "BNB", "XRP"]].gt(btc20, axis=0).mean(axis=1)
    )
    features["high_beta_participation_20d"] = (
        ret20[["SOL", "BNB"]].gt(btc20, axis=0).mean(axis=1)
    )
    breadth = features["canonical5_outperformance_breadth_20d"]
    features["breadth_acceleration_10d"] = breadth - breadth.rolling(10, min_periods=10).mean()
    features["breadth_contraction_from_10d_max"] = breadth.rolling(
        10, min_periods=10
    ).max() - breadth

    missing = set(AVAILABLE_FEATURES) - set(features.columns)
    extra = set(features.columns) - set(AVAILABLE_FEATURES)
    if missing or extra:
        raise RuntimeError(f"feature contract mismatch missing={sorted(missing)} extra={sorted(extra)}")
    return features.loc[:, list(AVAILABLE_FEATURES)]


def family_map(contract: Mapping) -> dict[str, str]:
    out: dict[str, str] = {}
    for family, payload in contract["feature_families"].items():
        for spec in payload.get("features", []):
            out[spec["id"]] = family
    return out
