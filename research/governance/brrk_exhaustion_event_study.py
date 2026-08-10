from __future__ import annotations

"""Read-only BRRK exhaustion event study.

The study mechanically separates genuine exhaustion tops from pullbacks that
resume to fresh highs, then measures whether frozen deterioration families carry
7-14 day warning information.  It never changes BRRK targets or portfolio gross.
"""

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from sklearn.metrics import roc_auc_score

AUDIT_ID = "BRRK-EXHAUSTION-EVENT-STUDY-0043"
ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")
API_BASES = (
    "https://data-api.binance.vision/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
)
START_DATE = "2020-08-01"
END_DATE = "2026-08-03"
EVAL_END = pd.Timestamp("2026-08-02")
TREND_HORIZONS = (20, 60, 120, 240)
TREND_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
DOWNSIDE_PANELS = (0.10, 0.15, 0.20)
PRIMARY_DOWNSIDE = 0.15
FRESH_HIGH = 0.02
ANCHORS = (
    "2023-12-25",
    "2024-03-31",
    "2024-11-24",
    "2025-01-26",
    "2025-10-06",
)


class AuditError(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ms(date: str) -> int:
    return int(pd.Timestamp(date, tz="UTC").timestamp() * 1000)


def fetch_daily_ohlcv(symbol: str) -> pd.DataFrame:
    start = _ms(START_DATE)
    end = _ms(END_DATE)
    rows: list[list[object]] = []
    last_error: Exception | None = None
    while start < end:
        payload = None
        for base in API_BASES:
            try:
                response = requests.get(
                    base,
                    params={
                        "symbol": symbol,
                        "interval": "1d",
                        "startTime": start,
                        "endTime": end,
                        "limit": 1000,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:  # pragma: no cover - network fallback
                last_error = exc
                time.sleep(0.5)
        if payload is None:
            raise AuditError(f"could not fetch {symbol}: {last_error}")
        if not payload:
            break
        rows.extend(payload)
        nxt = int(payload[-1][0]) + 86_400_000
        if nxt <= start:
            break
        start = nxt
        time.sleep(0.03)
    if not rows:
        raise AuditError(f"no OHLCV rows for {symbol}")
    frame = pd.DataFrame(
        rows,
        columns=[
            "open_time", "open", "high", "low", "close", "volume", "close_time",
            "quote_volume", "trades", "taker_base", "taker_quote", "ignore",
        ],
    )
    frame["date"] = pd.to_datetime(frame["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    for col in ("open", "high", "low", "close", "volume", "quote_volume"):
        frame[col] = frame[col].astype(float)
    return frame.drop_duplicates("date").set_index("date").sort_index()


def load_market() -> dict[str, pd.DataFrame]:
    return {asset: fetch_daily_ohlcv(f"{asset}USDT") for asset in ASSETS}


def load_canonical() -> tuple[pd.Series, pd.Series]:
    root = repo_root()
    equity = pd.read_csv(root / "research/results/pit_disp_0015/daily_equity.csv", parse_dates=["date"]).set_index("date")
    weights = pd.read_csv(root / "research/results/pit_disp_0015/daily_weights.csv", parse_dates=["date"]).set_index("date")
    nav = equity["BRRK0011_BASELINE"].astype(float).sort_index()
    v1_cols = [f"V1_BASELINE__{a}" for a in TARGET_ASSETS]
    brrk_cols = [f"BRRK0011_BASELINE__{a}" for a in TARGET_ASSETS]
    v1_gross = weights[v1_cols].abs().sum(axis=1).astype(float)
    brrk_gross = weights[brrk_cols].abs().sum(axis=1).astype(float)
    scale = (brrk_gross / v1_gross.where(v1_gross > 1e-10)).clip(lower=0.0, upper=1.05)
    return nav, scale


def rsi(close: pd.Series, n: int) -> pd.Series:
    diff = close.diff()
    up = diff.clip(lower=0.0)
    down = -diff.clip(upper=0.0)
    avg_up = up.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    avg_down = down.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    rs = avg_up / avg_down.replace(0.0, np.nan)
    return 100.0 - 100.0 / (1.0 + rs)


def trend_components(close: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    lr = np.log(close).diff()
    comps = pd.DataFrame(index=close.index)
    agg = pd.Series(0.0, index=close.index, dtype=float)
    valid = pd.Series(True, index=close.index)
    for h, w in zip(TREND_HORIZONS, TREND_WEIGHTS):
        momentum = np.log(close / close.shift(h))
        scale = lr.rolling(h).std() * math.sqrt(h)
        comp = np.tanh(momentum / scale.replace(0.0, np.nan))
        comps[f"trend_{h}"] = comp
        agg = agg + w * comp
        valid &= comp.notna()
    return comps, agg.where(valid)


def realized_vol(close: pd.Series, n: int) -> pd.Series:
    return np.log(close).diff().rolling(n).std() * math.sqrt(365.0)


def days_since_rolling_high(close: pd.Series, n: int) -> pd.Series:
    out = pd.Series(np.nan, index=close.index, dtype=float)
    values = close.to_numpy(dtype=float)
    for i in range(n - 1, len(close)):
        segment = values[i - n + 1 : i + 1]
        j = int(np.nanargmax(segment))
        out.iloc[i] = float(n - 1 - j)
    return out


def downside_upside_semivol(ret: pd.Series, n: int) -> pd.Series:
    down2 = ret.where(ret < 0.0, 0.0).pow(2).rolling(n).mean()
    up2 = ret.where(ret > 0.0, 0.0).pow(2).rolling(n).mean()
    return np.sqrt(down2) / np.sqrt(up2).replace(0.0, np.nan)


def consecutive_true(flag: pd.Series) -> pd.Series:
    vals = flag.fillna(False).astype(bool).to_numpy()
    out = np.zeros(len(vals), dtype=float)
    count = 0
    for i, value in enumerate(vals):
        count = count + 1 if value else 0
        out[i] = count
    return pd.Series(out, index=flag.index)


def rolling_negative_beta(asset_ret: pd.Series, btc_ret: pd.Series, n: int = 30) -> pd.Series:
    out = pd.Series(np.nan, index=btc_ret.index, dtype=float)
    a = asset_ret.to_numpy(dtype=float)
    b = btc_ret.to_numpy(dtype=float)
    for i in range(n - 1, len(out)):
        aa = a[i - n + 1 : i + 1]
        bb = b[i - n + 1 : i + 1]
        mask = np.isfinite(aa) & np.isfinite(bb) & (bb < 0.0)
        if int(mask.sum()) < 5:
            continue
        var = float(np.var(bb[mask], ddof=1))
        if var <= 0:
            continue
        out.iloc[i] = float(np.cov(aa[mask], bb[mask], ddof=1)[0, 1] / var)
    return out


def causal_z(series: pd.Series) -> pd.Series:
    mean = series.rolling(252, min_periods=60).mean()
    std = series.rolling(252, min_periods=60).std().replace(0.0, np.nan)
    return ((series - mean) / std).clip(-3.0, 3.0)


def _family(frame: pd.DataFrame, names: list[str]) -> pd.Series:
    return frame[names].mean(axis=1, skipna=True)


def build_features(market: dict[str, pd.DataFrame], nav: pd.Series, defensive_scale: pd.Series) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    common = nav.index
    for asset in ASSETS:
        common = common.intersection(market[asset].index)
    common = common[common <= EVAL_END]
    close = pd.DataFrame({a: market[a].loc[common, "close"] for a in ASSETS}, index=common)
    volume = pd.DataFrame({a: market[a].loc[common, "volume"] for a in ASSETS}, index=common)
    high = pd.DataFrame({a: market[a].loc[common, "high"] for a in ASSETS}, index=common)
    low = pd.DataFrame({a: market[a].loc[common, "low"] for a in ASSETS}, index=common)
    ret = close.pct_change(fill_method=None)
    logret = np.log(close).diff()
    nav = nav.reindex(common).astype(float)
    defensive_scale = defensive_scale.reindex(common).astype(float)

    raw = pd.DataFrame(index=common)
    families: dict[str, list[str]] = {}

    # F1 momentum decay: higher oriented value = more deterioration.
    btc = close["BTC"]
    r14, r28 = rsi(btc, 14), rsi(btc, 28)
    ema12 = btc.ewm(span=12, adjust=False).mean()
    ema26 = btc.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = (macd - signal) / btc
    btc_comps, btc_trend = trend_components(btc)
    fast = 0.375 * btc_comps["trend_20"] + 0.625 * btc_comps["trend_60"]
    slow = 0.5 * btc_comps["trend_120"] + 0.5 * btc_comps["trend_240"]
    raw["f1_rsi14_decay7"] = -r14.diff(7) / 20.0
    raw["f1_rsi28_decay7"] = -r28.diff(7) / 20.0
    raw["f1_rsi_high_falling"] = ((r14 - 50.0) / 20.0).clip(lower=0.0) * (-r14.diff(7) / 20.0).clip(lower=0.0)
    raw["f1_macd_hist_weak"] = -hist
    raw["f1_macd_hist_decay5"] = -hist.diff(5)
    raw["f1_fast_below_slow"] = slow - fast
    raw["f1_trend_decay7"] = -btc_trend.diff(7)
    raw["f1_trend_accel7"] = -btc_trend.diff(7).diff(7)
    families["F1_MOMENTUM_DECAY"] = [c for c in raw.columns if c.startswith("f1_")]

    # F2 price structure.
    for n in (30, 60, 120):
        raw[f"f2_dist_high_{n}"] = -(btc / btc.rolling(n).max() - 1.0)
    raw["f2_days_since_high60"] = days_since_rolling_high(btc, 60) / 60.0
    ma20, ma60 = btc.rolling(20).mean(), btc.rolling(60).mean()
    raw["f2_below_ma20"] = -(btc / ma20 - 1.0)
    raw["f2_below_ma60"] = -(btc / ma60 - 1.0)
    raw["f2_ma20_slope10"] = -ma20.pct_change(10)
    raw["f2_ma60_slope10"] = -ma60.pct_change(10)
    recent_peak = btc.rolling(7).max()
    prior_peak = btc.shift(7).rolling(60).max()
    raw["f2_prior_peak_shortfall"] = -(recent_peak / prior_peak - 1.0)
    families["F2_PRICE_STRUCTURE"] = [c for c in raw.columns if c.startswith("f2_")]

    # F3 volume / price-volume.
    v = volume["BTC"]
    vm = v.rolling(20).mean()
    vs = v.rolling(20).std().replace(0.0, np.nan)
    raw["f3_downmove_volume_shock"] = (-ret["BTC"]).clip(lower=0.0) * ((v - vm) / vs).clip(lower=0.0)
    upv = v.where(ret["BTC"] > 0.0, 0.0).rolling(20).sum()
    dnv = v.where(ret["BTC"] < 0.0, 0.0).rolling(20).sum()
    raw["f3_down_up_volume_ratio"] = dnv / upv.replace(0.0, np.nan)
    signed = np.sign(ret["BTC"].fillna(0.0)) * v
    obv = signed.cumsum()
    raw["f3_obv_slope20"] = -obv.diff(20) / (vm * 20.0).replace(0.0, np.nan)
    raw["f3_price_obv_divergence20"] = btc.pct_change(20) - obv.diff(20) / (vm * 20.0).replace(0.0, np.nan)
    neg_mean_v = v.where(ret["BTC"] < 0.0).rolling(20, min_periods=8).mean()
    pos_mean_v = v.where(ret["BTC"] > 0.0).rolling(20, min_periods=8).mean()
    raw["f3_selloff_volume_expansion"] = neg_mean_v / pos_mean_v.replace(0.0, np.nan)
    families["F3_VOLUME_CONFIRMATION"] = [c for c in raw.columns if c.startswith("f3_")]

    # F4 volatility/downside asymmetry and known-at-time PNL stress.
    rv10, rv30, rv60 = realized_vol(btc, 10), realized_vol(btc, 30), realized_vol(btc, 60)
    raw["f4_rv10"] = rv10
    raw["f4_rv30"] = rv30
    raw["f4_rv60"] = rv60
    raw["f4_rv10_accel"] = rv10 / rv10.shift(7) - 1.0
    raw["f4_rv10_vs_rv30"] = rv10 / rv30 - 1.0
    raw["f4_down_up_semivol"] = downside_upside_semivol(ret["BTC"], 20)
    raw["f4_negative_share20"] = (ret["BTC"] < 0.0).astype(float).rolling(20).mean()
    true_range = pd.concat(
        [high["BTC"] - low["BTC"], (high["BTC"] - btc.shift(1)).abs(), (low["BTC"] - btc.shift(1)).abs()],
        axis=1,
    ).max(axis=1)
    raw["f4_atr20_normalized"] = true_range.rolling(20).mean() / btc
    running_high = nav.cummax()
    pnl_dd = nav / running_high - 1.0
    pnl_duration = days_since_rolling_high(nav, min(120, max(20, len(nav))))
    raw["f4_pnl_drawdown"] = -pnl_dd
    raw["f4_pnl_dd_duration_interaction"] = (-pnl_dd) * (pnl_duration / 120.0)
    families["F4_VOL_DOWNSIDE"] = [c for c in raw.columns if c.startswith("f4_")]

    # F5 breadth/relative strength.
    roc20 = close.pct_change(20)
    roc60 = close.pct_change(60)
    breadth20 = (roc20 > 0.0).astype(float).mean(axis=1)
    breadth60 = (roc60 > 0.0).astype(float).mean(axis=1)
    raw["f5_breadth20_weak"] = 1.0 - breadth20
    raw["f5_breadth60_weak"] = 1.0 - breadth60
    raw["f5_breadth_decay7"] = -breadth20.diff(7)
    rel20 = pd.DataFrame({a: close[a].pct_change(20) - close["BTC"].pct_change(20) for a in ASSETS if a != "BTC"})
    raw["f5_alt_rel20_weak"] = -rel20.mean(axis=1)
    raw["f5_cross_section_mean20_weak"] = -roc20.mean(axis=1)
    raw["f5_cross_section_dispersion20"] = roc20.std(axis=1)
    sorted_roc = np.sort(roc20.to_numpy(dtype=float), axis=1)
    top = pd.Series(sorted_roc[:, -1], index=common)
    second = pd.Series(sorted_roc[:, -2], index=common)
    raw["f5_top_second_compression"] = -(top - second)
    families["F5_BREADTH_RELATIVE"] = [c for c in raw.columns if c.startswith("f5_")]

    # F6 correlation/systemic risk.
    pair_corrs: list[pd.Series] = []
    for i, a in enumerate(ASSETS):
        for b in ASSETS[i + 1 :]:
            pair_corrs.append(ret[a].rolling(30).corr(ret[b]))
    pair_corr = pd.concat(pair_corrs, axis=1).mean(axis=1)
    alt_btc_corr = pd.concat([ret[a].rolling(30).corr(ret["BTC"]) for a in ASSETS if a != "BTC"], axis=1).mean(axis=1)
    raw["f6_pair_corr"] = pair_corr
    raw["f6_alt_btc_corr"] = alt_btc_corr
    raw["f6_corr_accel7"] = pair_corr.diff(7)
    betas = pd.concat([rolling_negative_beta(ret[a], ret["BTC"], 30) for a in ASSETS if a != "BTC"], axis=1)
    raw["f6_negative_btc_beta"] = betas.mean(axis=1)
    families["F6_CORRELATION_STRESS"] = [c for c in raw.columns if c.startswith("f6_")]

    # F7 BRRK internal deterioration/disagreement.
    raw["f7_scale_reduction"] = 1.0 - defensive_scale
    raw["f7_scale_decay7"] = -defensive_scale.diff(7)
    raw["f7_slow_fast_disagreement"] = slow - fast
    trend20 = roc20
    trend120 = close.pct_change(120)
    raw["f7_long_positive_short_negative_fraction"] = ((trend120 > 0.0) & (trend20 < 0.0)).astype(float).mean(axis=1)
    raw["f7_disagreement_persistence"] = consecutive_true(fast < slow) / 30.0
    families["F7_BRRK_DISAGREEMENT"] = [c for c in raw.columns if c.startswith("f7_")]

    z = pd.DataFrame(index=raw.index)
    for col in raw.columns:
        z[col] = causal_z(raw[col].replace([np.inf, -np.inf], np.nan))
    scores = pd.DataFrame(index=z.index)
    for family_name, cols in families.items():
        scores[family_name] = _family(z, cols)
    scores["EXHAUSTION_SCORE"] = scores[list(families)].mean(axis=1, skipna=True)

    # Keep raw/z data for correlation diagnostics without leaking it into labels.
    scores.attrs["z_features"] = z
    scores.attrs["breadth20"] = breadth20
    return scores, families


def detect_candidates(nav: pd.Series) -> list[pd.Timestamp]:
    nav = nav.dropna().sort_index()
    values = nav.to_numpy(dtype=float)
    dates = nav.index
    candidates: list[pd.Timestamp] = []
    for i in range(30, len(nav) - 60):
        if values[i] < np.nanmax(values[i - 7 : i + 8]) - 1e-9:
            continue
        if values[i] / values[i - 30] - 1.0 < 0.05:
            continue
        if np.nanmin(values[i + 1 : i + 15]) / values[i] - 1.0 > -0.05:
            continue
        candidates.append(pd.Timestamp(dates[i]))
    if not candidates:
        return []

    clusters: list[list[pd.Timestamp]] = [[candidates[0]]]
    for date in candidates[1:]:
        if (date - clusters[-1][-1]).days <= 21:
            clusters[-1].append(date)
        else:
            clusters.append([date])
    return [max(cluster, key=lambda d: float(nav.loc[d])) for cluster in clusters]


def classify_event(nav: pd.Series, peak: pd.Timestamp, downside: float) -> dict[str, object]:
    loc = nav.index.get_loc(peak)
    future = nav.iloc[loc + 1 : loc + 61]
    peak_nav = float(nav.loc[peak])
    ratio = future / peak_nav - 1.0
    down_hits = ratio.index[ratio <= -downside]
    up_hits = ratio.index[ratio >= FRESH_HIGH]
    down_date = pd.Timestamp(down_hits[0]) if len(down_hits) else None
    up_date = pd.Timestamp(up_hits[0]) if len(up_hits) else None
    if down_date is not None and (up_date is None or down_date < up_date):
        label = "TRUE_EXHAUSTION"
    elif up_date is not None and (down_date is None or up_date < down_date):
        label = "CONTINUATION_FALSE_TOP"
    else:
        label = "AMBIGUOUS"
    return {
        "label": label,
        "down_date": str(down_date.date()) if down_date is not None else None,
        "fresh_high_date": str(up_date.date()) if up_date is not None else None,
        "min_60d_return": float(ratio.min()) if len(ratio) else None,
        "max_60d_return": float(ratio.max()) if len(ratio) else None,
    }


def window_mean(series: pd.Series, peak: pd.Timestamp, start_days: int, end_days: int) -> float | None:
    segment = series.loc[peak + pd.Timedelta(days=start_days) : peak + pd.Timedelta(days=end_days)].dropna()
    return float(segment.mean()) if len(segment) else None


def _auc(rows: list[dict[str, object]], score_key: str) -> dict[str, object]:
    usable = [r for r in rows if r["label"] in {"TRUE_EXHAUSTION", "CONTINUATION_FALSE_TOP"} and r.get(score_key) is not None]
    true_values = [float(r[score_key]) for r in usable if r["label"] == "TRUE_EXHAUSTION"]
    cont_values = [float(r[score_key]) for r in usable if r["label"] == "CONTINUATION_FALSE_TOP"]
    if not true_values or not cont_values:
        auc = None
    else:
        y = [1 if r["label"] == "TRUE_EXHAUSTION" else 0 for r in usable]
        x = [float(r[score_key]) for r in usable]
        auc = float(roc_auc_score(y, x))
    return {
        "auc": auc,
        "true_median": float(np.median(true_values)) if true_values else None,
        "continuation_median": float(np.median(cont_values)) if cont_values else None,
        "median_gap_true_minus_continuation": float(np.median(true_values) - np.median(cont_values)) if true_values and cont_values else None,
        "n_true": len(true_values),
        "n_continuation": len(cont_values),
    }


def warning_panel(scores: pd.DataFrame, events: list[dict[str, object]], q: float) -> dict[str, object]:
    score = scores["EXHAUSTION_SCORE"]
    threshold = score.shift(1).rolling(252, min_periods=60).quantile(q)
    above = (score >= threshold) & score.notna() & threshold.notna()
    trigger = above.astype(int).rolling(3).sum().eq(3)
    true_hits: list[int] = []
    cont_hits = 0
    n_true = 0
    n_cont = 0
    for event in events:
        label = event["label"]
        peak = pd.Timestamp(str(event["peak_date"]))
        if label not in {"TRUE_EXHAUSTION", "CONTINUATION_FALSE_TOP"}:
            continue
        dates = trigger.loc[peak - pd.Timedelta(days=21) : peak - pd.Timedelta(days=1)]
        hits = list(dates.index[dates])
        if label == "TRUE_EXHAUSTION":
            n_true += 1
            if hits:
                true_hits.append(int((peak - pd.Timestamp(hits[0])).days))
        else:
            n_cont += 1
            if hits:
                cont_hits += 1
    return {
        "quantile": q,
        "persistence_days": 3,
        "true_event_hit_rate_pre21": float(len(true_hits) / n_true) if n_true else None,
        "continuation_false_trigger_rate_pre21": float(cont_hits / n_cont) if n_cont else None,
        "median_true_lead_days": float(np.median(true_hits)) if true_hits else None,
        "true_lead_days": true_hits,
        "n_true": n_true,
        "n_continuation": n_cont,
    }


def event_rows(nav: pd.Series, scores: pd.DataFrame, peaks: list[pd.Timestamp], downside: float) -> list[dict[str, object]]:
    windows = {
        "PRE14_7": (-14, -7),
        "PRE7_0": (-7, 0),
        "POST0_7": (0, 7),
    }
    rows: list[dict[str, object]] = []
    for peak in peaks:
        outcome = classify_event(nav, peak, downside)
        row: dict[str, object] = {
            "peak_date": str(peak.date()),
            "peak_nav": float(nav.loc[peak]),
            **outcome,
        }
        for window_name, bounds in windows.items():
            for col in scores.columns:
                row[f"{window_name}__{col}"] = window_mean(scores[col], peak, bounds[0], bounds[1])
        rows.append(row)
    return rows


def correlation_summary(scores: pd.DataFrame) -> dict[str, object]:
    z: pd.DataFrame = scores.attrs["z_features"]
    corr = z.corr(min_periods=60)
    pairs: list[dict[str, object]] = []
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            value = corr.loc[a, b]
            if pd.notna(value) and abs(float(value)) >= 0.85:
                pairs.append({"a": a, "b": b, "corr": float(value)})
    eig = np.linalg.eigvalsh(corr.fillna(0.0).to_numpy(dtype=float)) if len(cols) else np.array([])
    eig = np.clip(eig, 0.0, None)
    effective_rank = float(eig.sum() ** 2 / np.square(eig).sum()) if len(eig) and np.square(eig).sum() > 0 else None
    return {
        "raw_oriented_feature_count": len(cols),
        "abs_corr_ge_0_85_pair_count": len(pairs),
        "high_corr_pairs": sorted(pairs, key=lambda x: abs(float(x["corr"])), reverse=True)[:30],
        "effective_rank_participation_ratio": effective_rank,
    }


def anchor_map(peaks: list[pd.Timestamp], primary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_peak = {str(row["peak_date"]): row for row in primary_rows}
    out: list[dict[str, object]] = []
    for text in ANCHORS:
        anchor = pd.Timestamp(text)
        if not peaks:
            out.append({"anchor": text, "nearest_peak": None})
            continue
        nearest = min(peaks, key=lambda d: abs((d - anchor).days))
        delta = int((nearest - anchor).days)
        if abs(delta) > 21:
            out.append({"anchor": text, "nearest_peak": None, "nearest_delta_days": delta})
            continue
        row = by_peak[str(nearest.date())]
        out.append({
            "anchor": text,
            "nearest_peak": str(nearest.date()),
            "nearest_delta_days": delta,
            "primary_label": row["label"],
            "min_60d_return": row["min_60d_return"],
        })
    return out


def recovery_summary(nav: pd.Series, scores: pd.DataFrame, primary_rows: list[dict[str, object]]) -> dict[str, object]:
    breadth = scores.attrs["breadth20"]
    rows: list[dict[str, object]] = []
    for event in primary_rows:
        peak = pd.Timestamp(str(event["peak_date"]))
        loc = nav.index.get_loc(peak)
        future = nav.iloc[loc + 1 : loc + 61]
        reclaim = future.index[future >= float(event["peak_nav"])]
        days = int((pd.Timestamp(reclaim[0]) - peak).days) if len(reclaim) else None
        before = breadth.loc[peak - pd.Timedelta(days=7) : peak].mean()
        after = breadth.loc[peak : peak + pd.Timedelta(days=30)]
        breadth_recovery = after.index[after >= before] if pd.notna(before) else []
        bdays = int((pd.Timestamp(breadth_recovery[0]) - peak).days) if len(breadth_recovery) else None
        rows.append({"peak_date": str(peak.date()), "label": event["label"], "days_to_reclaim_peak": days, "days_to_breadth_recovery": bdays})
    return {"events": rows}


def run() -> dict[str, object]:
    nav, scale = load_canonical()
    market = load_market()
    common = nav.index
    for asset in ASSETS:
        common = common.intersection(market[asset].index)
    common = common[common <= EVAL_END]
    nav = nav.reindex(common).dropna()
    scale = scale.reindex(nav.index)
    market = {a: frame.reindex(nav.index) for a, frame in market.items()}

    scores, families = build_features(market, nav, scale)
    peaks = detect_candidates(nav)
    panels: dict[str, object] = {}
    primary_rows: list[dict[str, object]] = []
    for downside in DOWNSIDE_PANELS:
        rows = event_rows(nav, scores, peaks, downside)
        if math.isclose(downside, PRIMARY_DOWNSIDE):
            primary_rows = rows
        windows: dict[str, object] = {}
        for window in ("PRE14_7", "PRE7_0", "POST0_7"):
            metrics: dict[str, object] = {}
            for col in (*families.keys(), "EXHAUSTION_SCORE"):
                metrics[col] = _auc(rows, f"{window}__{col}")
            windows[window] = metrics
        counts = {label: sum(1 for r in rows if r["label"] == label) for label in ("TRUE_EXHAUSTION", "CONTINUATION_FALSE_TOP", "AMBIGUOUS")}
        panels[f"down_{int(downside * 100)}pct"] = {"counts": counts, "windows": windows, "events": rows}

    warning = [warning_panel(scores, primary_rows, q) for q in (0.70, 0.80, 0.90)]
    return {
        "audit_id": AUDIT_ID,
        "status": "DIAGNOSTIC_ONLY_NO_PROMOTION_AUTHORITY",
        "window": {"start": str(nav.index.min().date()), "end": str(nav.index.max().date()), "sessions": len(nav)},
        "event_taxonomy": {
            "centered_local_peak_half_window_days": 7,
            "prior_gain_window_sessions": 30,
            "prior_gain_min": 0.05,
            "pullback_window_sessions": 14,
            "candidate_pullback_min": -0.05,
            "decluster_days": 21,
            "outcome_window_sessions": 60,
            "fresh_high_barrier": FRESH_HIGH,
            "downside_panels": list(DOWNSIDE_PANELS),
            "primary_downside": PRIMARY_DOWNSIDE,
            "candidate_peak_count": len(peaks),
        },
        "feature_families": {k: v for k, v in families.items()},
        "normalization": "TRAILING_252_SESSION_ZSCORE_MIN60_CLIP_3_EQUAL_WEIGHT_WITHIN_FAMILY_EQUAL_WEIGHT_ACROSS_F1_F7",
        "panels": panels,
        "warning_threshold_panel_primary_15pct": warning,
        "correlation_summary": correlation_summary(scores),
        "anchor_sanity_checks_primary_15pct": anchor_map(peaks, primary_rows),
        "recovery_hysteresis_descriptive_primary_15pct": recovery_summary(nav, scores, primary_rows),
        "data_semantics": {
            "pnl_source": "research/results/pit_disp_0015/daily_equity.csv::BRRK0011_BASELINE",
            "weights_source": "research/results/pit_disp_0015/daily_weights.csv",
            "ohlcv_source": "BINANCE_SPOT_UTC_DAILY_KLINES_RESEARCHER_EXPOSED_DEVELOPMENT_DIAGNOSTIC",
            "future_data_used_only_for_retrospective_event_labels": True,
            "predictor_features_causal_at_timestamp": True,
        },
        "authority": {
            "canonical_strategy_changed": False,
            "phase6_observation_changed": False,
            "portfolio_economics_executed": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, sort_keys=True, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print("BRRK_EXHAUSTION_AUDIT_JSON=" + json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
