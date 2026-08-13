from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
import pandas as pd

RID = "BRRK-BTC-RISK-SIGNAL-ATLAS-0062"
ASSETS = ("BTC", "ETH", "SOL")
REQUIRED_FIELDS = ("open", "high", "low", "close", "volume", "quote_volume", "trades")
DIRECTIONAL_FAMILIES = (
    "F01_TREND_LEVEL_DIRECTION", "F02_TREND_SPREAD_DISAGREEMENT",
    "F03_TREND_ACCELERATION_DECELERATION", "F04_TREND_CROSS_TRANSITION",
    "F05_VOL_ADJUSTED_TREND_GUARDS", "F06_MOMENTUM_LEVEL",
    "F07_OVERBOUGHT_STRETCH", "F08_BEARISH_DIVERGENCE_EXHAUSTION",
    "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE", "F12_VOLUME_FLOW_CONFIRMATION",
    "F13_CROSS_CRYPTO_BREADTH", "F14_RELATIVE_CRYPTO_LEADERSHIP",
    "F21_SEQUENTIAL_CHANGE_DETECTION", "F23_MULTI_TIMESCALE_DISAGREEMENT",
    "F24_FIXED_LOW_ORDER_INTERACTIONS",
)
RISK_FAMILIES = ("F10_VOLATILITY_REGIME", "F11_DOWNSIDE_ASYMMETRY_TAIL")
BASE_FAMILIES = tuple(x for x in DIRECTIONAL_FAMILIES + RISK_FAMILIES if x != "F24_FIXED_LOW_ORDER_INTERACTIONS")
ALL_FAMILIES = DIRECTIONAL_FAMILIES + RISK_FAMILIES

FORMULA_CONTRACT = {
    "ema": "pandas ewm(span=L, adjust=False, min_periods=L)",
    "wilder_rma": "pandas ewm(alpha=1/L, adjust=False, min_periods=L)",
    "atr": "Wilder RMA of max(high-low, abs(high-prev_close), abs(low-prev_close))",
    "rsi": "100-100/(1+Wilder(gain)/Wilder(loss)); both zero -> 50; loss zero -> 100",
    "ppo": "100*(EMA_fast/EMA_slow-1); signal=EMA_signal(PPO); histogram=PPO-signal",
    "supertrend": "recursive final upper/lower bands from HL2 +/- multiplier*WilderATR; signed risk=(supertrend-close)/ATR",
    "chandelier": "rolling_high_L - multiplier*WilderATR_L; signed risk=(exit-close)/ATR",
    "divergence": "difference between within-window standardized OLS slopes of log-price and oscillator",
    "mfi": "typical-price raw money flow, sign from typical-price change, rolling positive/(positive+negative)*100",
    "cmf": "rolling sum((((close-low)-(high-close))/(high-low))*volume)/rolling sum(volume)",
    "causal_z": "trailing 252 observations including t, minimum 60, ddof=1, clipped [-3,3]; zero variance -> missing",
    "spearman": "Pearson correlation of average-tie ranks",
    "bootstrap": "fixed full-panel average-tie rank scores; aligned moving blocks, no per-resample reranking",
}


@dataclass(frozen=True)
class CellMeta:
    family: str
    representation: str
    cell_id: str


def _finite_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).astype(float)


def _validate_frames(frames: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    missing_assets = [a for a in ASSETS if a not in frames]
    if missing_assets:
        raise ValueError(f"missing assets: {missing_assets}")
    out: dict[str, pd.DataFrame] = {}
    common: pd.Index | None = None
    for asset in ASSETS:
        frame = frames[asset].copy()
        missing = [c for c in REQUIRED_FIELDS if c not in frame.columns]
        if missing:
            raise ValueError(f"{asset} missing fields: {missing}")
        if not frame.index.is_monotonic_increasing or frame.index.has_duplicates:
            raise ValueError(f"{asset} index must be sorted unique")
        frame = frame.loc[:, REQUIRED_FIELDS].apply(pd.to_numeric, errors="coerce").astype(float)
        if (frame[["open", "high", "low", "close"]] <= 0).any().any():
            raise ValueError(f"{asset} has non-positive OHLC")
        common = frame.index if common is None else common.intersection(frame.index)
        out[asset] = frame
    assert common is not None
    common = common.sort_values()
    if len(common) < 300:
        raise ValueError("insufficient aligned rows")
    for asset in ASSETS:
        out[asset] = out[asset].loc[common].copy()
    return out


def _ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=int(span), adjust=False, min_periods=int(span)).mean()


def _rma(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / int(n), adjust=False, min_periods=int(n)).mean()


def _true_range(f: pd.DataFrame) -> pd.Series:
    prev = f["close"].shift(1)
    return pd.concat([(f["high"] - f["low"]), (f["high"] - prev).abs(), (f["low"] - prev).abs()], axis=1).max(axis=1)


def _atr(f: pd.DataFrame, n: int) -> pd.Series:
    return _rma(_true_range(f), n)


def _rsi(close: pd.Series, n: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    ag = _rma(gain, n)
    al = _rma(loss, n)
    rs = ag / al.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    both_zero = (ag == 0.0) & (al == 0.0)
    out = out.mask((al == 0.0) & (ag > 0.0), 100.0)
    return out.mask(both_zero, 50.0)


def _cmo(close: pd.Series, n: int) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0.0).rolling(n, min_periods=n).sum()
    dn = (-d.clip(upper=0.0)).rolling(n, min_periods=n).sum()
    den = up + dn
    return 100.0 * (up - dn) / den.replace(0.0, np.nan)


def _ppo(close: pd.Series, fast: int, slow: int, signal: int) -> tuple[pd.Series, pd.Series]:
    ppo = 100.0 * (_ema(close, fast) / _ema(close, slow) - 1.0)
    sig = _ema(ppo, signal)
    return ppo, ppo - sig


def _rolling_standardized_slope(s: pd.Series, n: int) -> pd.Series:
    n = int(n)
    x = np.arange(n, dtype=float)
    xc = x - x.mean()
    denom_x = float(np.dot(xc, xc))

    def one(a: np.ndarray) -> float:
        if not np.isfinite(a).all():
            return np.nan
        sd = a.std(ddof=1)
        if not np.isfinite(sd) or sd <= 0:
            return np.nan
        z = (a - a.mean()) / sd
        return float(np.dot(xc, z) / denom_x)

    return s.rolling(n, min_periods=n).apply(one, raw=True)


def _rolling_slope_tstat(s: pd.Series, n: int) -> pd.Series:
    n = int(n)
    x = np.arange(n, dtype=float)
    xc = x - x.mean()
    sxx = float(np.dot(xc, xc))

    def one(a: np.ndarray) -> float:
        if not np.isfinite(a).all():
            return np.nan
        yc = a - a.mean()
        beta = float(np.dot(xc, yc) / sxx)
        resid = yc - beta * xc
        s2 = float(np.dot(resid, resid) / (n - 2))
        if s2 <= 0:
            return 0.0
        se = math.sqrt(s2 / sxx)
        return beta / se if se > 0 else np.nan

    return s.rolling(n, min_periods=n).apply(one, raw=True)


def _cross_recency(x: pd.Series, half_life: int) -> pd.Series:
    event = (x.shift(1) >= 0.0) & (x < 0.0)
    values = np.zeros(len(x), dtype=float)
    age: int | None = None
    decay = math.log(2.0) / float(half_life)
    xv = x.to_numpy(dtype=float)
    ev = event.fillna(False).to_numpy(dtype=bool)
    for i in range(len(values)):
        if not np.isfinite(xv[i]):
            values[i] = np.nan
            continue
        if ev[i]:
            age = 0
        elif age is not None:
            age += 1
        values[i] = 0.0 if age is None else math.exp(-decay * age)
    return pd.Series(values, index=x.index, dtype=float)


def _supertrend_risk(f: pd.DataFrame, n: int, mult: float) -> pd.Series:
    atr = _atr(f, n)
    hl2 = (f["high"] + f["low"]) / 2.0
    bu = hl2 + float(mult) * atr
    bl = hl2 - float(mult) * atr
    fu, fl = bu.copy(), bl.copy()
    st = pd.Series(np.nan, index=f.index, dtype=float)
    c = f["close"]
    first = atr.first_valid_index()
    if first is None:
        return st
    start = f.index.get_loc(first)
    fu.iloc[start], fl.iloc[start] = bu.iloc[start], bl.iloc[start]
    st.iloc[start] = fu.iloc[start] if c.iloc[start] <= hl2.iloc[start] else fl.iloc[start]
    for i in range(start + 1, len(f)):
        if not np.isfinite(atr.iloc[i]):
            continue
        prev_fu, prev_fl, prev_close = fu.iloc[i - 1], fl.iloc[i - 1], c.iloc[i - 1]
        fu.iloc[i] = bu.iloc[i] if (bu.iloc[i] < prev_fu or prev_close > prev_fu) else prev_fu
        fl.iloc[i] = bl.iloc[i] if (bl.iloc[i] > prev_fl or prev_close < prev_fl) else prev_fl
        prev_st = st.iloc[i - 1]
        if not np.isfinite(prev_st):
            st.iloc[i] = fu.iloc[i] if c.iloc[i] <= hl2.iloc[i] else fl.iloc[i]
        elif np.isclose(prev_st, prev_fu, rtol=0.0, atol=1e-12):
            st.iloc[i] = fu.iloc[i] if c.iloc[i] <= fu.iloc[i] else fl.iloc[i]
        else:
            st.iloc[i] = fl.iloc[i] if c.iloc[i] >= fl.iloc[i] else fu.iloc[i]
    return (st - c) / atr.replace(0.0, np.nan)


def _stochastic(f: pd.DataFrame, n: int) -> pd.Series:
    lo = f["low"].rolling(n, min_periods=n).min()
    hi = f["high"].rolling(n, min_periods=n).max()
    return 100.0 * (f["close"] - lo) / (hi - lo).replace(0.0, np.nan)


def _williams_r(f: pd.DataFrame, n: int) -> pd.Series:
    lo = f["low"].rolling(n, min_periods=n).min()
    hi = f["high"].rolling(n, min_periods=n).max()
    return -100.0 * (hi - f["close"]) / (hi - lo).replace(0.0, np.nan)


def _bollinger_percent_b(close: pd.Series, n: int, k: float = 2.0) -> pd.Series:
    m = close.rolling(n, min_periods=n).mean()
    sd = close.rolling(n, min_periods=n).std(ddof=1)
    return (close - (m - k * sd)) / (2.0 * k * sd).replace(0.0, np.nan)


def _mfi(f: pd.DataFrame, n: int) -> pd.Series:
    tp = (f["high"] + f["low"] + f["close"]) / 3.0
    money = tp * f["volume"]
    direction = tp.diff()
    pos = money.where(direction > 0.0, 0.0).rolling(n, min_periods=n).sum()
    neg = money.where(direction < 0.0, 0.0).rolling(n, min_periods=n).sum()
    total = pos + neg
    return (100.0 * pos / total.replace(0.0, np.nan)).mask(total == 0.0, 50.0)


def _cmf(f: pd.DataFrame, n: int) -> pd.Series:
    span = (f["high"] - f["low"]).replace(0.0, np.nan)
    mult = ((f["close"] - f["low"]) - (f["high"] - f["close"])) / span
    mfv = mult * f["volume"]
    return mfv.rolling(n, min_periods=n).sum() / f["volume"].rolling(n, min_periods=n).sum().replace(0.0, np.nan)


def _obv(f: pd.DataFrame) -> pd.Series:
    sign = np.sign(f["close"].diff()).fillna(0.0)
    return (sign * f["volume"]).cumsum()


def _semivol_ratio(ret: pd.Series, n: int) -> pd.Series:
    dn = ret.clip(upper=0.0).pow(2).rolling(n, min_periods=n).mean().pow(0.5)
    up = ret.clip(lower=0.0).pow(2).rolling(n, min_periods=n).mean().pow(0.5)
    return np.log(dn.replace(0.0, np.nan) / up.replace(0.0, np.nan))


def _causal_z(s: pd.Series, window: int = 252, min_periods: int = 60) -> pd.Series:
    s = _finite_series(s)
    m = s.rolling(window, min_periods=min_periods).mean()
    sd = s.rolling(window, min_periods=min_periods).std(ddof=1)
    return ((s - m) / sd.replace(0.0, np.nan)).clip(-3.0, 3.0)


def _family_score(cells: pd.DataFrame) -> pd.Series:
    need = int(math.ceil(0.60 * cells.shape[1]))
    count = cells.notna().sum(axis=1)
    return cells.mean(axis=1, skipna=True).where(count >= need)


def _add(raw: dict[str, pd.Series], meta: dict[str, CellMeta], family: str, representation: str, suffix: str, series: pd.Series) -> None:
    cid = f"{family}|{representation}|{suffix}"
    if cid in raw:
        raise RuntimeError(f"duplicate cell id: {cid}")
    raw[cid] = _finite_series(series)
    meta[cid] = CellMeta(family, representation, cid)


def _build_base_raw_cells(frames: Mapping[str, pd.DataFrame]) -> tuple[pd.DataFrame, dict[str, CellMeta]]:
    fs = _validate_frames(frames)
    btc, c = fs["BTC"], fs["BTC"]["close"]
    logc, ret = np.log(c), np.log(c).diff()
    raw: dict[str, pd.Series] = {}
    meta: dict[str, CellMeta] = {}

    for L in (10, 20, 40, 80, 160):
        _add(raw, meta, "F01_TREND_LEVEL_DIRECTION", "NEG_LOG_PRICE_OVER_EMA", f"L={L}", -np.log(c / _ema(c, L)))
    for L in (10, 20, 40, 80):
        _add(raw, meta, "F01_TREND_LEVEL_DIRECTION", "NEG_ROLLING_LOG_PRICE_SLOPE_TSTAT", f"L={L}", -_rolling_slope_tstat(logc, L))

    for fast, slow in ((5, 20), (10, 40), (20, 80), (40, 160)):
        _add(raw, meta, "F02_TREND_SPREAD_DISAGREEMENT", "NEG_LOG_EMA_FAST_OVER_SLOW", f"fast={fast};slow={slow}", -np.log(_ema(c, fast) / _ema(c, slow)))

    ppo_cache: dict[tuple[int, int, int], tuple[pd.Series, pd.Series]] = {}
    for fast, slow, sig in ((6, 18, 5), (8, 24, 6), (12, 26, 9), (16, 48, 12)):
        ppo, hist = _ppo(c, fast, slow, sig)
        ppo_cache[(fast, slow, sig)] = (ppo, hist)
        suffix = f"fast={fast};slow={slow};signal={sig}"
        _add(raw, meta, "F03_TREND_ACCELERATION_DECELERATION", "NEG_PPO_HISTOGRAM_LEVEL", suffix, -hist)
        _add(raw, meta, "F03_TREND_ACCELERATION_DECELERATION", "NEG_PPO_HISTOGRAM_5D_CHANGE", suffix, -hist.diff(5))

    for fast, slow, sig in ((6, 18, 5), (8, 24, 6), (12, 26, 9), (16, 48, 12)):
        ppo = ppo_cache[(fast, slow, sig)][0]
        for hl in (5, 20):
            _add(raw, meta, "F04_TREND_CROSS_TRANSITION", "BEARISH_PPO_ZERO_CROSS_RECENCY", f"fast={fast};slow={slow};signal={sig};half_life={hl}", _cross_recency(ppo, hl))
    for L in (10, 20, 40, 80):
        x = np.log(c / _ema(c, L))
        for hl in (5, 20):
            _add(raw, meta, "F04_TREND_CROSS_TRANSITION", "BEARISH_PRICE_EMA_CROSS_RECENCY", f"L={L};half_life={hl}", _cross_recency(x, hl))

    for L in (7, 10, 14, 21):
        for mult in (1.5, 2.0, 3.0, 4.0):
            _add(raw, meta, "F05_VOL_ADJUSTED_TREND_GUARDS", "SUPERTREND_BEARISH_DISTANCE", f"atr={L};mult={mult:g}", _supertrend_risk(btc, L, mult))
    for L in (10, 20, 40):
        atr = _atr(btc, L)
        hi = btc["high"].rolling(L, min_periods=L).max()
        for mult in (2.0, 3.0, 4.0):
            _add(raw, meta, "F05_VOL_ADJUSTED_TREND_GUARDS", "CHANDELIER_BEARISH_DISTANCE", f"L={L};mult={mult:g}", (hi - mult * atr - c) / atr.replace(0.0, np.nan))

    rsi_cache: dict[int, pd.Series] = {}
    for L in (5, 7, 10, 14, 21, 28):
        r = _rsi(c, L)
        rsi_cache[L] = r
        _add(raw, meta, "F06_MOMENTUM_LEVEL", "NEG_RSI_CENTERED", f"L={L}", 50.0 - r)
    for L in (5, 10, 20, 40):
        _add(raw, meta, "F06_MOMENTUM_LEVEL", "NEG_LOG_ROC", f"L={L}", -np.log(c / c.shift(L)))
        _add(raw, meta, "F06_MOMENTUM_LEVEL", "NEG_CMO", f"L={L}", -_cmo(c, L))

    for L in (5, 7, 10, 14, 21, 28):
        _add(raw, meta, "F07_OVERBOUGHT_STRETCH", "RSI_UPPER_TAIL", f"L={L}", rsi_cache[L] - 50.0)
    for L in (7, 14, 28):
        _add(raw, meta, "F07_OVERBOUGHT_STRETCH", "STOCHASTIC_UPPER_TAIL", f"L={L}", _stochastic(btc, L) - 50.0)
        _add(raw, meta, "F07_OVERBOUGHT_STRETCH", "WILLIAMS_R_UPPER_TAIL", f"L={L}", _williams_r(btc, L) + 50.0)
    for L in (10, 20, 40):
        _add(raw, meta, "F07_OVERBOUGHT_STRETCH", "BOLLINGER_PERCENT_B_UPPER_TAIL", f"L={L};std=2", _bollinger_percent_b(c, L, 2.0) - 0.5)

    for L in (10, 20, 40, 80):
        rsi = _rsi(c, L)
        div = _rolling_standardized_slope(logc, L) - _rolling_standardized_slope(rsi, L)
        _add(raw, meta, "F08_BEARISH_DIVERGENCE_EXHAUSTION", "PRICE_MINUS_RSI_MOMENTUM_DIVERGENCE", f"L={L}", div)
    for fast, slow, sig in ((6, 18, 5), (8, 24, 6), (12, 26, 9), (16, 48, 12)):
        ppo = ppo_cache[(fast, slow, sig)][0]
        div = _rolling_standardized_slope(logc, 20) - _rolling_standardized_slope(ppo, 20)
        _add(raw, meta, "F08_BEARISH_DIVERGENCE_EXHAUSTION", "PRICE_MINUS_PPO_MOMENTUM_DIVERGENCE", f"fast={fast};slow={slow};signal={sig};div_window=20", div)

    for L in (10, 20, 40, 80):
        lo = btc["low"].rolling(L, min_periods=L).min()
        hi = btc["high"].rolling(L, min_periods=L).max()
        _add(raw, meta, "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE", "NEG_DONCHIAN_RANGE_LOCATION", f"L={L}", -(c - lo) / (hi - lo).replace(0.0, np.nan))
    for L in (20, 60, 120):
        hi = btc["high"].rolling(L, min_periods=L).max()
        _add(raw, meta, "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE", "LOG_RECENT_HIGH_OVER_CLOSE", f"L={L}", np.log(hi / c))
    for L in (10, 20, 40, 80):
        pre_break_hi = btc["high"].shift(2).rolling(L, min_periods=L).max()
        failed = (c.shift(1) > pre_break_hi) & (c <= pre_break_hi)
        _add(raw, meta, "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE", "FAILED_UP_BREAK_RETURN_INSIDE_RANGE", f"L={L}", failed.astype(float))

    for short, long in ((5, 20), (10, 40), (20, 80), (40, 160)):
        rs = ret.pow(2).rolling(short, min_periods=short).mean().pow(0.5)
        rl = ret.pow(2).rolling(long, min_periods=long).mean().pow(0.5)
        _add(raw, meta, "F10_VOLATILITY_REGIME", "LOG_RV_SHORT_OVER_LONG", f"short={short};long={long}", np.log(rs.replace(0, np.nan) / rl.replace(0, np.nan)))
    for L in (7, 14, 28):
        _add(raw, meta, "F10_VOLATILITY_REGIME", "ATR_OVER_CLOSE", f"L={L}", _atr(btc, L) / c)
    rv10 = ret.pow(2).rolling(10, min_periods=10).mean().pow(0.5)
    for L in (10, 20, 40):
        vov = rv10.rolling(L, min_periods=L).std(ddof=1) / rv10.rolling(L, min_periods=L).mean().replace(0, np.nan)
        _add(raw, meta, "F10_VOLATILITY_REGIME", "VOL_OF_VOL", f"rv=10;outer={L}", vov)

    for L in (10, 20, 40):
        _add(raw, meta, "F11_DOWNSIDE_ASYMMETRY_TAIL", "LOG_DOWNSIDE_OVER_UPSIDE_SEMIVOL", f"L={L}", _semivol_ratio(ret, L))
        _add(raw, meta, "F11_DOWNSIDE_ASYMMETRY_TAIL", "NEGATIVE_RETURN_SHARE", f"L={L}", (ret < 0).astype(float).rolling(L, min_periods=L).mean())
    for L in (5, 10, 20):
        hi = c.rolling(L, min_periods=L).max()
        _add(raw, meta, "F11_DOWNSIDE_ASYMMETRY_TAIL", "DRAWDOWN_VELOCITY", f"L={L}", np.log(hi / c) / float(L))

    vol = btc["volume"]
    for short, long in ((5, 20), (10, 40), (20, 80), (40, 160)):
        vs = vol.rolling(short, min_periods=short).mean()
        vl = vol.rolling(long, min_periods=long).mean()
        _add(raw, meta, "F12_VOLUME_FLOW_CONFIRMATION", "LOG_VOLUME_SHORT_OVER_LONG", f"short={short};long={long}", np.log(vs.replace(0, np.nan) / vl.replace(0, np.nan)))
    obv = _obv(btc)
    for L in (5, 10, 20, 40):
        _add(raw, meta, "F12_VOLUME_FLOW_CONFIRMATION", "NEG_OBV_SLOPE", f"L={L}", -_rolling_standardized_slope(obv, L))
    for L in (7, 14, 28):
        _add(raw, meta, "F12_VOLUME_FLOW_CONFIRMATION", "NEG_MFI_CENTERED", f"L={L}", 50.0 - _mfi(btc, L))
    for L in (10, 20, 40):
        _add(raw, meta, "F12_VOLUME_FLOW_CONFIRMATION", "NEG_CMF", f"L={L}", -_cmf(btc, L))

    closes = pd.DataFrame({a: fs[a]["close"] for a in ASSETS})
    log_closes = np.log(closes)
    daily = log_closes.diff()
    for L in (10, 20, 40, 80):
        emas = {a: _ema(fs[a]["close"], L) for a in ASSETS}
        above = pd.DataFrame({a: (fs[a]["close"] > emas[a]).astype(float) for a in ASSETS})
        valid = pd.DataFrame({a: emas[a].notna() for a in ASSETS})
        _add(raw, meta, "F13_CROSS_CRYPTO_BREADTH", "ONE_MINUS_FRACTION_ABOVE_EMA", f"L={L}", 1.0 - above.where(valid).mean(axis=1))
    for L in (5, 10, 20):
        mom = log_closes - log_closes.shift(L)
        _add(raw, meta, "F13_CROSS_CRYPTO_BREADTH", "NEG_BREADTH_MOMENTUM", f"L={L}", -mom.mean(axis=1))
        _add(raw, meta, "F13_CROSS_CRYPTO_BREADTH", "RETURN_DISPERSION", f"L={L}", mom.std(axis=1, ddof=1))
    for L in (10, 20, 40):
        pair_corrs = [daily[a].rolling(L, min_periods=L).corr(daily[b]) for a, b in (("BTC", "ETH"), ("BTC", "SOL"), ("ETH", "SOL"))]
        _add(raw, meta, "F13_CROSS_CRYPTO_BREADTH", "CORRELATION_CONCENTRATION", f"L={L}", pd.concat(pair_corrs, axis=1).mean(axis=1))

    for asset in ("ETH", "SOL"):
        ratio = np.log(fs[asset]["close"] / fs["BTC"]["close"])
        rep = "NEG_ETH_BTC_LOG_MOMENTUM" if asset == "ETH" else "NEG_SOL_BTC_LOG_MOMENTUM"
        for L in (5, 10, 20, 40, 80):
            _add(raw, meta, "F14_RELATIVE_CRYPTO_LEADERSHIP", rep, f"L={L}", -(ratio - ratio.shift(L)))
    for L in (5, 10, 20, 40, 80):
        rels = []
        for asset in ("ETH", "SOL"):
            ratio = np.log(fs[asset]["close"] / fs["BTC"]["close"])
            rels.append((ratio - ratio.shift(L) < 0).astype(float).where(ratio.shift(L).notna()))
        _add(raw, meta, "F14_RELATIVE_CRYPTO_LEADERSHIP", "BETA_WEAKNESS_BREADTH", f"L={L}", pd.concat(rels, axis=1).mean(axis=1))

    for short, long in ((5, 20), (10, 40), (20, 80), (40, 160)):
        ms = ret.rolling(short, min_periods=short).mean()
        ml = ret.rolling(long, min_periods=long).mean()
        sd = ret.rolling(long, min_periods=long).std(ddof=1)
        _add(raw, meta, "F21_SEQUENTIAL_CHANGE_DETECTION", "NEG_STANDARDIZED_RETURN_MEAN_SHIFT", f"short={short};long={long}", -(ms - ml) / sd.replace(0, np.nan))

    for fast, slow in ((5, 20), (10, 40), (20, 80), (40, 160)):
        _add(raw, meta, "F23_MULTI_TIMESCALE_DISAGREEMENT", "FAST_BEARISH_MINUS_SLOW_BEARISH_TREND", f"fast={fast};slow={slow}", -np.log(_ema(c, fast) / _ema(c, slow)))

    return pd.DataFrame(raw, index=c.index), meta


def build_signal_atlas(frames: Mapping[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, CellMeta]]:
    """Build all 185 causal cell scores and 17 family scores. No future targets are read."""
    base_raw, meta = _build_base_raw_cells(frames)
    if base_raw.shape[1] != 179:
        raise RuntimeError(f"base candidate count drift: {base_raw.shape[1]} != 179")
    base_z = pd.DataFrame({c: _causal_z(base_raw[c]) for c in base_raw.columns}, index=base_raw.index)
    family_scores: dict[str, pd.Series] = {}
    for family in BASE_FAMILIES:
        cols = [c for c, m in meta.items() if m.family == family]
        family_scores[family] = _family_score(base_z[cols])

    raw_interactions: dict[str, pd.Series] = {}
    interaction_meta: dict[str, CellMeta] = {}
    pairs = (
        ("F01_TREND_LEVEL_DIRECTION", "F10_VOLATILITY_REGIME"),
        ("F06_MOMENTUM_LEVEL", "F10_VOLATILITY_REGIME"),
        ("F13_CROSS_CRYPTO_BREADTH", "F10_VOLATILITY_REGIME"),
        ("F14_RELATIVE_CRYPTO_LEADERSHIP", "F01_TREND_LEVEL_DIRECTION"),
        ("F05_VOL_ADJUSTED_TREND_GUARDS", "F10_VOLATILITY_REGIME"),
        ("F08_BEARISH_DIVERGENCE_EXHAUSTION", "F07_OVERBOUGHT_STRETCH"),
    )
    for a, b in pairs:
        s = family_scores[a].clip(lower=0.0) * family_scores[b].clip(lower=0.0)
        _add(raw_interactions, interaction_meta, "F24_FIXED_LOW_ORDER_INTERACTIONS", "POSITIVE_PART_PRODUCT", f"{a}*{b}", s)
    int_raw = pd.DataFrame(raw_interactions, index=base_raw.index)
    int_z = pd.DataFrame({c: _causal_z(int_raw[c]) for c in int_raw.columns}, index=base_raw.index)
    family_scores["F24_FIXED_LOW_ORDER_INTERACTIONS"] = _family_score(int_z)
    cells = pd.concat([base_z, int_z], axis=1)
    meta.update(interaction_meta)
    families = pd.DataFrame({f: family_scores[f] for f in ALL_FAMILIES}, index=cells.index)
    if cells.shape[1] != 185 or families.shape[1] != 17:
        raise RuntimeError(f"atlas dimension drift: cells={cells.shape[1]} families={families.shape[1]}")
    return cells, families, meta


def build_targets(btc_close: pd.Series) -> pd.DataFrame:
    close = _finite_series(btc_close)
    logc = np.log(close)
    ret = logc.diff()
    out: dict[str, pd.Series] = {}
    for h in (5, 10, 20, 40):
        out[f"T1_CASH_ADVANTAGE@{h}"] = -np.log(close.shift(-h) / close)
        excursion = pd.concat([(-np.log(close.shift(-j) / close)).clip(lower=0.0) for j in range(1, h + 1)], axis=1).max(axis=1)
        out[f"T2_MAX_ADVERSE_EXCURSION@{h}"] = excursion.where(close.shift(-h).notna())
        fwd = pd.concat([ret.shift(-j) for j in range(1, h + 1)], axis=1)
        out[f"T3_FORWARD_REALIZED_VOL@{h}"] = math.sqrt(365.0) * fwd.pow(2).mean(axis=1).pow(0.5).where(fwd.notna().all(axis=1))
        down = fwd.clip(upper=0.0)
        out[f"T3_FORWARD_DOWNSIDE_SEMIVOL@{h}"] = math.sqrt(365.0) * down.pow(2).mean(axis=1).pow(0.5).where(fwd.notna().all(axis=1))
    return pd.DataFrame(out, index=close.index)


def _average_rank_z(s: pd.Series) -> np.ndarray:
    r = s.rank(method="average").to_numpy(dtype=float)
    sd = float(np.std(r, ddof=0))
    return (r - float(np.mean(r))) / sd if np.isfinite(sd) and sd > 0 else np.full_like(r, np.nan)


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return float("nan")
    xx, yy = x[mask], y[mask]
    xx, yy = xx - xx.mean(), yy - yy.mean()
    den = math.sqrt(float(np.dot(xx, xx) * np.dot(yy, yy)))
    return float(np.dot(xx, yy) / den) if den > 0 else float("nan")


def _spearman(x: pd.Series, y: pd.Series) -> float:
    joined = pd.concat([x, y], axis=1).dropna()
    return _corr(_average_rank_z(joined.iloc[:, 0]), _average_rank_z(joined.iloc[:, 1])) if len(joined) >= 3 else float("nan")


def _track_defs() -> dict[str, tuple[str, tuple[str, ...]]]:
    dshort = ("T1_CASH_ADVANTAGE@5", "T2_MAX_ADVERSE_EXCURSION@5", "T1_CASH_ADVANTAGE@10", "T2_MAX_ADVERSE_EXCURSION@10")
    dsw = ("T1_CASH_ADVANTAGE@20", "T2_MAX_ADVERSE_EXCURSION@20", "T1_CASH_ADVANTAGE@40", "T2_MAX_ADVERSE_EXCURSION@40")
    rshort = ("T3_FORWARD_REALIZED_VOL@5", "T3_FORWARD_DOWNSIDE_SEMIVOL@5", "T3_FORWARD_REALIZED_VOL@10", "T3_FORWARD_DOWNSIDE_SEMIVOL@10")
    rsw = ("T3_FORWARD_REALIZED_VOL@20", "T3_FORWARD_DOWNSIDE_SEMIVOL@20", "T3_FORWARD_REALIZED_VOL@40", "T3_FORWARD_DOWNSIDE_SEMIVOL@40")
    out: dict[str, tuple[str, tuple[str, ...]]] = {}
    for f in DIRECTIONAL_FAMILIES:
        out[f"{f}|D_SHORT"] = (f, dshort)
        out[f"{f}|D_SWING"] = (f, dsw)
    for f in RISK_FAMILIES:
        out[f"{f}|R_SHORT"] = (f, rshort)
        out[f"{f}|R_SWING"] = (f, rsw)
    if len(out) != 34:
        raise RuntimeError("track count drift")
    return out


def _count_balanced_blocks(n: int, k: int = 4) -> np.ndarray:
    if n < k:
        raise ValueError("too few rows for blocks")
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    return np.concatenate([np.full(size, i, dtype=int) for i, size in enumerate(sizes)])


def _bootstrap_global_lcb(families: pd.DataFrame, targets: pd.DataFrame, track_defs: Mapping[str, tuple[str, tuple[str, ...]]], observed_min: Mapping[str, float], *, block_length: int = 60, replicates: int = 4000, seed: int = 620062) -> tuple[float, dict[str, float]]:
    n = len(families)
    if n < block_length:
        raise ValueError("bootstrap panel shorter than block length")
    fam_names, target_names = list(families.columns), list(targets.columns)
    X = np.column_stack([_average_rank_z(families[c]) for c in fam_names])
    Y = np.column_stack([_average_rank_z(targets[c]) for c in target_names])
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError("fixed rank panel contains non-finite values")
    fi, yi = {x: i for i, x in enumerate(fam_names)}, {x: i for i, x in enumerate(target_names)}
    unique: list[tuple[int, int]] = []
    for _, (f, ts) in track_defs.items():
        for t in ts:
            p = (fi[f], yi[t])
            if p not in unique:
                unique.append(p)
    p_index = {p: i for i, p in enumerate(unique)}
    A = np.concatenate([X, Y, X * X, Y * Y], axis=1)
    cross = np.column_stack([X[:, a] * Y[:, b] for a, b in unique])
    pref = np.vstack([np.zeros((1, A.shape[1])), np.cumsum(A, axis=0)])
    pref_cross = np.vstack([np.zeros((1, len(unique))), np.cumsum(cross, axis=0)])
    fullA, fullC = pref[block_length:] - pref[:-block_length], pref_cross[block_length:] - pref_cross[:-block_length]
    k = int(math.ceil(n / block_length))
    rem = n - (k - 1) * block_length
    partA, partC = (fullA, fullC) if rem == block_length else (pref[rem:] - pref[:-rem], pref_cross[rem:] - pref_cross[:-rem])
    rng = np.random.default_rng(seed)
    obs = np.array([observed_min[key] for key in track_defs], dtype=float)
    maxdiff = np.empty(replicates, dtype=float)
    starts_count = n - block_length + 1
    for r in range(replicates):
        starts = rng.integers(0, starts_count, size=k)
        sums = fullA[starts[:-1]].sum(axis=0) if k > 1 else np.zeros(A.shape[1])
        crosses = fullC[starts[:-1]].sum(axis=0) if k > 1 else np.zeros(len(unique))
        sums, crosses = sums + partA[int(starts[-1])], crosses + partC[int(starts[-1])]
        px, py = X.shape[1], Y.shape[1]
        sx, sy = sums[:px], sums[px:px + py]
        sx2, sy2 = sums[px + py:px + py + px], sums[px + py + px:]
        bootmins = []
        for _, (f, ts) in track_defs.items():
            vals = []
            a = fi[f]
            for t in ts:
                b = yi[t]
                num = crosses[p_index[(a, b)]] - sx[a] * sy[b] / n
                vx, vy = sx2[a] - sx[a] * sx[a] / n, sy2[b] - sy[b] * sy[b] / n
                den = math.sqrt(max(vx, 0.0) * max(vy, 0.0))
                vals.append(num / den if den > 0 else np.nan)
            bootmins.append(float(np.nanmin(vals)))
        boot = np.asarray(bootmins)
        if not np.isfinite(boot).all():
            raise ValueError("non-finite bootstrap track statistic")
        maxdiff[r] = float(np.max(obs - boot))
    q95 = float(np.quantile(maxdiff, 0.95, method="linear"))
    return q95, {key: float(observed_min[key] - q95) for key in track_defs}


def evaluate_atlas(frames: Mapping[str, pd.DataFrame], *, minimum_origins: int = 1200, minimum_per_block: int = 250, bootstrap_replicates: int = 4000, bootstrap_seed: int = 620062, bootstrap_block_length: int = 60) -> dict[str, Any]:
    """Single deterministic scientific engine call. Performs no I/O and no network access."""
    cells, families, meta = build_signal_atlas(frames)
    btc = _validate_frames(frames)["BTC"]
    targets = build_targets(btc["close"])
    tracks = _track_defs()
    required = pd.concat([families, targets], axis=1).notna().all(axis=1)
    idx = required[required].index
    F, T, C = families.loc[idx].copy(), targets.loc[idx].copy(), cells.loc[idx].copy()
    n = len(idx)
    block_ids = _count_balanced_blocks(n, 4) if n >= 4 else np.array([], dtype=int)
    block_sizes = [int((block_ids == b).sum()) for b in range(4)] if n >= 4 else []
    primary: dict[str, Any] = {
        "schema_version": 1, "research_id": RID, "candidate_cell_count": int(cells.shape[1]),
        "family_count": int(families.shape[1]), "family_track_hypothesis_count": len(tracks),
        "common_origin_count": n, "common_origin_start": str(idx[0]) if n else None,
        "common_origin_end": str(idx[-1]) if n else None, "chronological_block_sizes": block_sizes,
        "gates": {}, "family_tracks": {},
        "data_unavailable": {
            "F15_DERIVATIVES_LEVERAGE_CROWDING": "DATA_UNAVAILABLE", "F16_OPTIONS_IMPLIED_RISK": "DATA_UNAVAILABLE",
            "F17_ONCHAIN_HOLDER_STATE": "DATA_UNAVAILABLE", "F18_CRYPTO_LIQUIDITY_STABLECOIN_DEPTH": "DATA_UNAVAILABLE",
            "F19_CROSS_ASSET_MACRO": "DATA_UNAVAILABLE", "F20_SENTIMENT_ATTENTION_FLOW": "DATA_UNAVAILABLE",
            "F22_LATENT_REGIME_STATE_SPACE": "NOT_EVALUATED",
        },
    }
    g0 = cells.shape[1] == 185 and families.shape[1] == 17 and len(tracks) == 34
    primary["gates"]["G0_CONTRACT_AND_DATA_IDENTITY"] = {"pass": bool(g0)}
    if not g0:
        primary["classification"] = "INVALID_EXECUTION"
        return {"primary_result": primary, "evidence": {}}
    g1 = n >= minimum_origins and len(block_sizes) == 4 and min(block_sizes) >= minimum_per_block
    primary["gates"]["G1_COMMON_SUPPORT"] = {"pass": bool(g1), "minimum_origins": minimum_origins, "minimum_per_block": minimum_per_block}
    evidence: dict[str, Any] = {
        "common_origins": [str(x) for x in idx], "block_ids": block_ids.tolist(),
        "family_scores": {c: [None if not np.isfinite(v) else float(v) for v in F[c].to_numpy()] for c in F.columns},
        "target_values": {c: [None if not np.isfinite(v) else float(v) for v in T[c].to_numpy()] for c in T.columns},
        "cell_target_associations": {}, "family_target_associations": {},
    }
    if not g1:
        primary["classification"] = "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT"
        return {"primary_result": primary, "evidence": evidence}

    family_assoc: dict[str, Any] = {}
    cell_assoc: dict[str, Any] = {}
    for key, (family, ts) in tracks.items():
        family_assoc[key] = {t: _spearman(F[family], T[t]) for t in ts}
        cols = [c for c, m in meta.items() if m.family == family]
        cell_assoc[key] = {c: {t: _spearman(C[c], T[t]) for t in ts} for c in cols}
    evidence["family_target_associations"] = family_assoc
    evidence["cell_target_associations"] = cell_assoc

    block_assoc: dict[str, Any] = {}
    for key, (family, ts) in tracks.items():
        block_assoc[key] = {}
        for b in range(4):
            positions = np.where(block_ids == b)[0]
            block_assoc[key][str(b)] = {t: _spearman(F.iloc[positions][family], T.iloc[positions][t]) for t in ts}
    evidence["block_family_target_associations"] = block_assoc

    observed_min: dict[str, float] = {}
    for key, (family, ts) in tracks.items():
        vals = [family_assoc[key][t] for t in ts]
        observed_min[key] = float(min(vals))
        g2 = all(np.isfinite(v) and v > 0.0 for v in vals)
        good_blocks = sum(all(np.isfinite(block_assoc[key][str(b)][t]) and block_assoc[key][str(b)][t] > 0.0 for t in ts) for b in range(4))
        rows = cell_assoc[key]
        favorable = {cid: all(np.isfinite(rows[cid][t]) and rows[cid][t] > 0.0 for t in ts) for cid in rows}
        frac = float(np.mean(list(favorable.values()))) if favorable else 0.0
        by_rep: dict[str, list[bool]] = {}
        for cid, ok in favorable.items():
            by_rep.setdefault(meta[cid].representation, []).append(bool(ok))
        rep_fracs = {rep: float(np.mean(v)) for rep, v in by_rep.items()}
        class_ok = sum(v >= 0.40 for v in rep_fracs.values()) >= 2 if len(rep_fracs) >= 2 else True
        g4 = frac >= 0.50 and class_ok
        primary["family_tracks"][key] = {
            "family": family, "targets": list(ts), "full_sample_rhos": {t: float(family_assoc[key][t]) for t in ts},
            "observed_track_min": observed_min[key], "G2_full_sample_sign": bool(g2), "positive_blocks": int(good_blocks),
            "G3_temporal_recurrence": bool(good_blocks >= 3), "favorable_cell_fraction": frac,
            "representation_favorable_fractions": rep_fracs, "G4_parameter_plateau": bool(g4),
        }

    q95, lcbs = _bootstrap_global_lcb(F, T, tracks, observed_min, block_length=bootstrap_block_length, replicates=bootstrap_replicates, seed=bootstrap_seed)
    evidence["bootstrap"] = {"replicates": bootstrap_replicates, "seed": bootstrap_seed, "block_length": bootstrap_block_length, "global_q95": q95, "simultaneous_lcbs": lcbs}
    any_pass = False
    gate_counts = {"G2": 0, "G3": 0, "G4": 0, "G5": 0}
    for key in tracks:
        row = primary["family_tracks"][key]
        row["simultaneous_lcb"] = float(lcbs[key])
        row["G5_simultaneous_lcb"] = bool(lcbs[key] > 0.0)
        row["passes_all_information_gates"] = bool(row["G2_full_sample_sign"] and row["G3_temporal_recurrence"] and row["G4_parameter_plateau"] and row["G5_simultaneous_lcb"])
        any_pass |= row["passes_all_information_gates"]
        gate_counts["G2"] += int(row["G2_full_sample_sign"])
        gate_counts["G3"] += int(row["G3_temporal_recurrence"])
        gate_counts["G4"] += int(row["G4_parameter_plateau"])
        gate_counts["G5"] += int(row["G5_simultaneous_lcb"])
    primary["gates"]["G2_FULL_SAMPLE_SIGN_COHERENCE"] = {"track_pass_count": gate_counts["G2"]}
    primary["gates"]["G3_TEMPORAL_RECURRENCE"] = {"track_pass_count": gate_counts["G3"]}
    primary["gates"]["G4_PARAMETER_PLATEAU"] = {"track_pass_count": gate_counts["G4"]}
    primary["gates"]["G5_SIMULTANEOUS_DEPENDENCE_AWARE_LCB"] = {"track_pass_count": gate_counts["G5"], "global_q95": q95}
    primary["passing_family_tracks"] = [k for k, v in primary["family_tracks"].items() if v["passes_all_information_gates"]]
    primary["classification"] = "PASS_SIGNAL_ATLAS_FAMILY_INFORMATION" if any_pass else "FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION"
    return {"primary_result": primary, "evidence": evidence}
