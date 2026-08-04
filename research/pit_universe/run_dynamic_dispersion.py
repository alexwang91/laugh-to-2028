import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
REGIME = RESEARCH / "regime_kelly"
HYBRID = RESEARCH / "hybrid_meta"
RISKFIX = RESEARCH / "risk_metric_fix"
DISP = RESEARCH / "dispersion_overlay"
for p in (HERE, RESEARCH, REGIME, HYBRID, RISKFIX, DISP):
    sys.path.insert(0, str(p))

import crypto_rotation_backtest as bt
from config import RegimeKellyConfig
from features_no_dominance import build_features_no_dominance
from walkforward_v1_meta import END, START, build_benchmark_v1, monthly_capture, portfolio_returns_full
from run_archive_discovery import DATA_API, archive_symbols
from run_dispersion_overlay import build_brrk0011_scale, evaluate

EXPERIMENT_ID = "PIT-DISP-0015-DYNAMIC-UNIVERSE"
START_FETCH = pd.Timestamp("2019-01-01")
END_FETCH = END
MIN_DAYS = 240
QVOL_FLOOR = 25_000_000.0
MIN_CROSS_SECTION = 5
MIN_SCALE = 0.10
SMOOTHING = 0.80
MAX_WORKERS = 8

# Mechanical, non-PnL exclusions. These are stable/fiat-like bases rather than directional crypto risk assets.
STABLE_OR_FIAT_BASES = {
    "USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "UST", "USTC", "PAX", "SUSD",
    "USDS", "USDSB", "USD1", "RLUSD", "EUR", "AEUR", "EURR", "TRY", "BIDR", "IDRT",
    "BKRW", "NGN", "UAH", "BRL", "ZAR", "GBP", "AUD", "RUB"
}
LEVERAGED_SUFFIXES = ("UP", "DOWN", "BULL", "BEAR")
FIXED_MAP = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "SOLUSDT": "SOL", "BNBUSDT": "BNB", "XRPUSDT": "XRP"}


def ordinary_symbol(symbol: str) -> bool:
    if not symbol.endswith("USDT"):
        return False
    base = symbol[:-4]
    if base in STABLE_OR_FIAT_BASES:
        return False
    # Exclude both exact leveraged-token names (BULL/BEAR) and suffixed variants (ETHBULL, BTCUP, ...).
    if base in LEVERAGED_SUFFIXES or any(base.endswith(suf) and len(base) > len(suf) for suf in LEVERAGED_SUFFIXES):
        return False
    return True


def fetch_daily_history(symbol: str):
    start_ms = int(START_FETCH.tz_localize("UTC").timestamp() * 1000)
    end_ms = int((END_FETCH + pd.Timedelta(days=1)).tz_localize("UTC").timestamp() * 1000) - 1
    rows = []
    cursor = start_ms
    calls = 0
    while cursor <= end_ms:
        params = {"symbol": symbol, "interval": "1d", "startTime": cursor, "endTime": end_ms, "limit": 1000}
        payload = None
        last_err = None
        for attempt in range(6):
            try:
                r = requests.get(f"{DATA_API}/api/v3/klines", params=params, timeout=45)
                calls += 1
                if r.status_code in (418, 429) or r.status_code >= 500:
                    last_err = f"HTTP {r.status_code}: {r.text[:200]}"
                    time.sleep(min(20.0, 1.5 ** attempt))
                    continue
                r.raise_for_status()
                payload = r.json()
                break
            except Exception as e:
                last_err = repr(e)
                time.sleep(min(20.0, 1.5 ** attempt))
        if payload is None:
            raise RuntimeError(f"{symbol} failed after retries: {last_err}")
        if not isinstance(payload, list) or not payload:
            break
        rows.extend(payload)
        last_open = int(payload[-1][0])
        next_cursor = last_open + 86_400_000
        if next_cursor <= cursor:
            raise RuntimeError(f"{symbol}: non-advancing API cursor")
        cursor = next_cursor
        if len(payload) < 1000:
            break
    if not rows:
        return symbol, pd.DataFrame(columns=["close", "quote_volume"]), calls
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "n_trades", "taker_base", "taker_quote", "ignore"
    ])
    dt = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True).dt.tz_localize(None).dt.normalize()
    out = pd.DataFrame({
        "close": pd.to_numeric(df["close"], errors="coerce").to_numpy(float),
        "quote_volume": pd.to_numeric(df["quote_volume"], errors="coerce").to_numpy(float),
    }, index=dt)
    out = out[~out.index.duplicated(keep="last")].sort_index().loc[:END_FETCH]
    return symbol, out, calls


def load_panel(symbols):
    data = {}
    errors = {}
    api_calls = 0
    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(fetch_daily_history, s): s for s in symbols}
        for fut in as_completed(futs):
            s = futs[fut]
            try:
                sym, df, calls = fut.result()
                data[sym] = df
                api_calls += calls
            except Exception as e:
                errors[s] = repr(e)
            completed += 1
            if completed % 50 == 0 or completed == len(symbols):
                print(f"data_progress {completed}/{len(symbols)} errors={len(errors)} calls={api_calls}", flush=True)
    close = pd.concat({s: df["close"] for s, df in data.items() if not df.empty}, axis=1).sort_index()
    qvol = pd.concat({s: df["quote_volume"] for s, df in data.items() if not df.empty}, axis=1).sort_index()
    return close, qvol, errors, api_calls


def scale_from_dispersion(dispersion: pd.Series):
    target = dispersion.shift(1).expanding(min_periods=1).median()
    raw = (target / dispersion).clip(lower=MIN_SCALE, upper=1.0)
    raw = raw.where(dispersion.notna() & target.notna(), 1.0)
    smooth = pd.Series(index=dispersion.index, dtype=float)
    prev = 1.0
    for dt in dispersion.index:
        r = float(raw.loc[dt]) if pd.notna(raw.loc[dt]) else 1.0
        prev = SMOOTHING * prev + (1.0 - SMOOTHING) * r
        smooth.loc[dt] = prev
    return target, raw, smooth


def fixed_panel_dispersion(fixed_prices: pd.DataFrame):
    ret20 = np.log(fixed_prices / fixed_prices.shift(20))
    d = ret20.std(axis=1, ddof=1, skipna=False)
    return d


def dynamic_dispersion(close: pd.DataFrame, qvol: pd.DataFrame):
    # "240 completed daily observations" is enforced as a contiguous recent 240-calendar-day block,
    # preventing a stale/delisted/relisted ticker from qualifying merely because it accumulated 240 rows long ago.
    full_recent_history = close.notna().rolling(MIN_DAYS, min_periods=MIN_DAYS).sum() >= MIN_DAYS
    ret20 = np.log(close / close.shift(20))
    eligible = full_recent_history & (qvol >= QVOL_FLOOR) & ret20.notna()
    n = eligible.sum(axis=1)
    d = ret20.where(eligible).std(axis=1, ddof=1)
    d = d.where(n >= MIN_CROSS_SECTION)
    return d, eligible, n, ret20


def annual(ret: pd.Series):
    return {str(int(y)): float((1.0 + s).prod() - 1.0) for y, s in ret.groupby(ret.index.year)}


def main():
    bt.START_DATE = START
    bt.END_DATE = str(END.date())

    symbols = sorted(s for s in archive_symbols() if ordinary_symbol(s))
    print(f"candidate_symbols={len(symbols)}")
    close, qvol, errors, api_calls = load_panel(symbols)

    missing_core = [s for s in FIXED_MAP if s not in close.columns]
    if missing_core:
        raise RuntimeError(f"Missing fixed V1 core symbols: {missing_core}")
    if len(errors) > max(10, int(0.05 * len(symbols))):
        raise RuntimeError(f"Too many symbol fetch errors: {len(errors)}/{len(symbols)}")

    fixed_prices = close[list(FIXED_MAP)].rename(columns=FIXED_MAP).dropna()
    fixed_prices = fixed_prices.loc[:END]
    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    features = build_features_no_dominance(fixed_prices, cfg)
    v1_raw = build_benchmark_v1(fixed_prices)
    v1_model = bt.apply_band(v1_raw, 0.05)
    v1_model_ret, _, _ = portfolio_returns_full(fixed_prices, v1_model)
    brrk_scale, decision_dates, decisions = build_brrk0011_scale(fixed_prices, features, v1_model_ret, cfg)
    eval_start = decision_dates[0] + pd.Timedelta(days=1)

    fixed_d = fixed_panel_dispersion(fixed_prices)
    _, fixed_raw_scale, fixed_scale = scale_from_dispersion(fixed_d)

    close = close.reindex(fixed_prices.index)
    qvol = qvol.reindex(fixed_prices.index)
    dyn_d, eligible, universe_n, ret20 = dynamic_dispersion(close, qvol)
    dyn_target, dyn_raw_scale, dyn_scale = scale_from_dispersion(dyn_d)

    candidates = {
        "V1_BASELINE": v1_raw,
        "V1_PLUS_FIXED_PANEL_DISP0014": v1_raw.mul(fixed_scale, axis=0),
        "V1_PLUS_DYNAMIC_UNIVERSE_DISP0015": v1_raw.mul(dyn_scale, axis=0),
        "BRRK0011_BASELINE": v1_raw.mul(brrk_scale, axis=0),
        "BRRK0011_PLUS_FIXED_PANEL_DISP0014": v1_raw.mul(brrk_scale * fixed_scale, axis=0),
        "BRRK0011_PLUS_DYNAMIC_UNIVERSE_DISP0015": v1_raw.mul(brrk_scale * dyn_scale, axis=0),
    }
    evaluated = {name: evaluate(fixed_prices, raw, eval_start) for name, raw in candidates.items()}
    btc_ret = fixed_prices["BTC"].pct_change(fill_method=None).loc[eval_start:END].fillna(0.0)

    eval_idx = fixed_prices.loc[eval_start:END].index
    current = eval_idx[-1]
    status = requests.get(f"{DATA_API}/api/v3/exchangeInfo", timeout=45).json()
    status_map = {x["symbol"]: x.get("status") for x in status.get("symbols", [])}
    inactive_cols = [s for s in eligible.columns if status_map.get(s) != "TRADING"]
    inactive_eligible_days = eligible[inactive_cols].sum(axis=0) if inactive_cols else pd.Series(dtype=float)
    inactive_ever = inactive_eligible_days[inactive_eligible_days > 0].sort_values(ascending=False)

    snapshots = {}
    for ds in ["2023-01-01", "2024-01-01", "2024-12-01", "2025-01-01", "2026-01-01", str(current.date())]:
        dt = pd.Timestamp(ds)
        avail = eligible.index[eligible.index <= dt]
        if len(avail) == 0:
            continue
        d = avail[-1]
        syms = eligible.columns[eligible.loc[d]].tolist()
        top = sorted(syms, key=lambda s: float(qvol.loc[d, s]), reverse=True)[:20]
        snapshots[str(d.date())] = {
            "eligible_count": int(universe_n.loc[d]),
            "dispersion": float(dyn_d.loc[d]) if pd.notna(dyn_d.loc[d]) else None,
            "raw_scale": float(dyn_raw_scale.loc[d]),
            "smoothed_scale": float(dyn_scale.loc[d]),
            "top_20_by_same_day_quote_volume": [{"symbol": s, "quote_volume": float(qvol.loc[d, s])} for s in top],
        }

    report = {
        "experiment_id": EXPERIMENT_ID,
        "data": {
            "historical_candidate_symbol_count": len(symbols),
            "symbols_fetched_with_rows": int(close.notna().any().sum()),
            "fetch_error_count": len(errors),
            "fetch_errors": errors,
            "api_call_count": api_calls,
            "first_panel_date": str(close.index.min().date()),
            "last_panel_date": str(close.index.max().date()),
        },
        "methodology": {
            "eligibility": f"{MIN_DAYS} consecutive completed daily rows ending at t and completed-day quote volume >= ${QVOL_FLOOR:,.0f}",
            "minimum_cross_section": MIN_CROSS_SECTION,
            "dispersion": "sample std of 20-day cumulative log returns across eligible point-in-time symbols",
            "scale": "expanding-prior-median/current clipped [0.10,1], recursively smoothed lambda=0.80",
            "execution": "scale entire frozen V1 gross exposure to cash, 0.05 band, 5bps per absolute weight change, t signal held over t+1",
            "scope": "validates risk signal only; V1 alpha asset set remains fixed"
        },
        "metrics": {name: ev["metrics"] for name, ev in evaluated.items()},
        "capture": {name: monthly_capture(ev["return"], btc_ret) for name, ev in evaluated.items()},
        "annual_returns": {name: annual(ev["return"]) for name, ev in evaluated.items()},
        "subperiods": {name: ev["subperiods"] for name, ev in evaluated.items()},
        "dynamic_universe_diagnostics": {
            "evaluation_mean_eligible_count": float(universe_n.loc[eval_idx].mean()),
            "evaluation_median_eligible_count": float(universe_n.loc[eval_idx].median()),
            "evaluation_min_eligible_count": int(universe_n.loc[eval_idx].min()),
            "evaluation_max_eligible_count": int(universe_n.loc[eval_idx].max()),
            "mean_dynamic_smoothed_scale": float(dyn_scale.loc[eval_idx].mean()),
            "median_dynamic_smoothed_scale": float(dyn_scale.loc[eval_idx].median()),
            "fraction_dynamic_scale_below_0_9": float((dyn_scale.loc[eval_idx] < 0.90).mean()),
            "fraction_dynamic_scale_below_0_5": float((dyn_scale.loc[eval_idx] < 0.50).mean()),
            "min_dynamic_scale": float(dyn_scale.loc[eval_idx].min()),
            "inactive_or_nontrading_symbols_ever_eligible_count": int(len(inactive_ever)),
            "top_inactive_symbols_by_eligible_days": [
                {"symbol": s, "eligible_days": int(v), "current_status": status_map.get(s, "MISSING")}
                for s, v in inactive_ever.head(30).items()
            ],
            "snapshots": snapshots,
        },
        "current": {
            "date": str(current.date()),
            "dynamic_universe_count": int(universe_n.loc[current]),
            "dynamic_dispersion": float(dyn_d.loc[current]) if pd.notna(dyn_d.loc[current]) else None,
            "dynamic_target_median": float(dyn_target.loc[current]) if pd.notna(dyn_target.loc[current]) else None,
            "dynamic_raw_scale": float(dyn_raw_scale.loc[current]),
            "dynamic_smoothed_scale": float(dyn_scale.loc[current]),
            "fixed_panel_smoothed_scale": float(fixed_scale.loc[current]),
            "BRRK_final_scale": float(brrk_scale.loc[current]),
        },
        "decision": "No parameter tuning is allowed. Interpret dynamic-universe overlay versus both baseline and fixed-panel DISP0014; frozen BRRK0011 remains baseline unless survivorship-aware evidence is sufficiently strong."
    }
    (HERE / "dynamic_dispersion_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== PIT_DISP_0015_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
