import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
START_DATE = "2020-08-01"
END_DATE = "2026-08-03"
COST_BPS = 5.0
HORIZONS = [20, 60, 120, 240]
FAST_WEIGHTS = [0.15, 0.25, 0.30, 0.30]
SLOW_WEIGHTS = [0.10, 0.20, 0.30, 0.40]
API_BASES = [
    "https://data-api.binance.vision/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
]


def ms(ts):
    return int(pd.Timestamp(ts, tz="UTC").timestamp() * 1000)


def fetch_daily(symbol):
    start = ms(START_DATE)
    end = ms(END_DATE)
    rows = []
    last_err = None
    while start < end:
        payload = None
        for base in API_BASES:
            try:
                r = requests.get(
                    base,
                    params={"symbol": symbol, "interval": "1d", "startTime": start, "endTime": end, "limit": 1000},
                    timeout=30,
                )
                r.raise_for_status()
                payload = r.json()
                break
            except Exception as exc:
                last_err = exc
                time.sleep(1)
        if payload is None:
            raise RuntimeError(f"Could not fetch {symbol}: {last_err}")
        if not payload:
            break
        rows.extend(payload)
        nxt = int(payload[-1][0]) + 86_400_000
        if nxt <= start:
            break
        start = nxt
        time.sleep(0.08)
    if not rows:
        raise RuntimeError(f"No data for {symbol}")
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trades", "taker_base", "taker_quote", "ignore"
    ])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    df["close"] = df["close"].astype(float)
    return df.drop_duplicates("date").set_index("date")["close"].sort_index()


def trend_score(price, weights=FAST_WEIGHTS):
    lr = np.log(price).diff()
    out = pd.Series(0.0, index=price.index)
    valid = pd.Series(True, index=price.index)
    for h, w in zip(HORIZONS, weights):
        mom = np.log(price / price.shift(h))
        scale = lr.rolling(h).std() * math.sqrt(h)
        comp = np.tanh(mom / scale)
        out = out + w * comp
        valid &= comp.notna()
    return out.where(valid)


def rv30(price):
    return np.log(price).diff().rolling(30).std() * math.sqrt(365)


def btc_last_drop_beta(price):
    t = trend_score(price)
    vol = rv30(price)
    positive_scaler = (0.45 / vol).clip(upper=1.0)
    beta = pd.Series(np.nan, index=price.index)
    pos = t >= 0
    beta.loc[pos] = 1.0 + 0.5 * t.loc[pos] * positive_scaler.loc[pos]

    vm = pd.Series(1.0, index=price.index)
    vm[(vol >= 0.35) & (vol < 0.50)] = 0.90
    vm[(vol >= 0.50) & (vol < 0.70)] = 0.75
    vm[vol >= 0.70] = 0.60
    neg = ((0.65 + 0.65 * t).clip(lower=0.18, upper=0.65) * vm).clip(lower=0.18, upper=0.65)
    beta.loc[~pos] = neg.loc[~pos]
    return beta, t, vol


def efficiency_ratio(price, n=60):
    net = (price - price.shift(n)).abs()
    path = price.diff().abs().rolling(n).sum()
    return (net / path).clip(0, 1)


def build_rotation_weights(prices):
    btc = prices["BTC"]
    beta, btc_t, btc_vol = btc_last_drop_beta(btc)

    t = {c: trend_score(prices[c]) for c in prices.columns}
    ratio_t = {c: trend_score(prices[c] / btc) for c in ["ETH", "SOL"]}
    bnb_t_slow = trend_score(prices["BNB"], SLOW_WEIGHTS)
    bnb_ratio_slow = trend_score(prices["BNB"] / btc, SLOW_WEIGHTS)
    vols = {c: rv30(prices[c]) for c in prices.columns}

    # Diagnostics only; ER is deliberately NOT used for allocation in this first frozen test.
    ers = {c: efficiency_ratio(prices[c], 60) for c in prices.columns}

    w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    scores = pd.DataFrame(np.nan, index=prices.index, columns=["ETH", "SOL", "BNB"])

    scores["ETH"] = 0.60 * t["ETH"] + 0.40 * ratio_t["ETH"]
    scores["SOL"] = 0.50 * t["SOL"] + 0.50 * ratio_t["SOL"]
    scores["BNB"] = 0.60 * bnb_t_slow + 0.40 * bnb_ratio_slow

    for dt in prices.index:
        if pd.isna(beta.loc[dt]) or pd.isna(btc_t.loc[dt]):
            continue
        budget = float(min(beta.loc[dt], 1.30))
        if btc_t.loc[dt] < 0:
            w.loc[dt, "BTC"] = budget
            continue

        eligible = []
        if (
            pd.notna(scores.loc[dt, "ETH"]) and scores.loc[dt, "ETH"] > 0
            and pd.notna(t["ETH"].loc[dt]) and t["ETH"].loc[dt] > 0
            and pd.notna(ratio_t["ETH"].loc[dt]) and ratio_t["ETH"].loc[dt] > 0
        ):
            eligible.append("ETH")
        if (
            pd.notna(scores.loc[dt, "SOL"]) and scores.loc[dt, "SOL"] > 0
            and pd.notna(t["SOL"].loc[dt]) and t["SOL"].loc[dt] > 0
            and pd.notna(ratio_t["SOL"].loc[dt]) and ratio_t["SOL"].loc[dt] > 0
        ):
            eligible.append("SOL")
        if (
            pd.notna(scores.loc[dt, "BNB"]) and scores.loc[dt, "BNB"] > 0
            and pd.notna(bnb_t_slow.loc[dt]) and bnb_t_slow.loc[dt] > 0
            and pd.notna(bnb_ratio_slow.loc[dt]) and bnb_ratio_slow.loc[dt] > 0
        ):
            eligible.append("BNB")

        eligible = sorted(eligible, key=lambda c: scores.loc[dt, c], reverse=True)
        if len(eligible) == 0:
            w.loc[dt, "BTC"] = budget
            continue
        if len(eligible) == 1:
            w.loc[dt, "BTC"] = 0.50 * budget
            w.loc[dt, eligible[0]] = 0.50 * budget
            continue

        chosen = eligible[:2]
        w.loc[dt, "BTC"] = 0.25 * budget
        remaining = 0.75 * budget
        raw = {}
        for c in chosen:
            v = float(vols[c].loc[dt]) if pd.notna(vols[c].loc[dt]) else np.nan
            raw[c] = max(float(scores.loc[dt, c]), 0.0) / max(v, 1e-6) if np.isfinite(v) else 0.0
        total_raw = sum(raw.values())
        if total_raw <= 0:
            w.loc[dt, "BTC"] = budget
            continue
        for c in chosen:
            w.loc[dt, c] = remaining * raw[c] / total_raw

        # Asset-specific concentration caps, fixed ex ante.
        caps = {"ETH": 0.50 * budget, "SOL": 0.35 * budget, "BNB": 0.25 * budget}
        overflow = 0.0
        for c in chosen:
            if w.loc[dt, c] > caps[c]:
                overflow += w.loc[dt, c] - caps[c]
                w.loc[dt, c] = caps[c]
        w.loc[dt, "BTC"] += overflow

    diagnostics = {
        "beta": beta,
        "btc_trend": btc_t,
        "btc_vol": btc_vol,
        "scores": scores,
        "trend": t,
        "ratio_trend": ratio_t,
        "er": ers,
    }
    return w, diagnostics


def apply_band(target_weights, band=0.05):
    held = pd.Series(0.0, index=target_weights.columns)
    out = pd.DataFrame(0.0, index=target_weights.index, columns=target_weights.columns)
    for dt, row in target_weights.iterrows():
        # Rebalance only if total target-vs-held L1 change is at least the band.
        if float((row - held).abs().sum()) >= band:
            held = row.copy()
        out.loc[dt] = held
    return out


def run_portfolio(prices, target_weights, start, end, band=None, cost_bps=COST_BPS):
    rets = prices.pct_change()
    tw = target_weights.copy()
    if band is not None:
        tw = apply_band(tw, band)
    # No lookahead: yesterday's target is today's held weight.
    held = tw.shift(1).fillna(0.0)
    dates = prices.loc[start:end].index
    held = held.loc[dates]
    rets = rets.loc[dates].fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = (held * rets).sum(axis=1)
    net = gross - turnover * cost_bps / 10_000.0
    nav = (1.0 + net).cumprod()
    return pd.DataFrame({"return": net, "nav": nav, "turnover": turnover, "gross_exposure": held.abs().sum(axis=1)}, index=dates), held


def metrics(result):
    r = result["return"].dropna()
    nav = result["nav"].dropna()
    years = len(r) / 365.25
    if len(nav) == 0:
        return {}
    cagr = nav.iloc[-1] ** (1 / years) - 1 if years > 0 else np.nan
    dd = nav / nav.cummax() - 1
    vol = r.std() * math.sqrt(365)
    sharpe = (r.mean() / r.std()) * math.sqrt(365) if r.std() > 0 else np.nan
    return {
        "end_multiple": float(nav.iloc[-1]),
        "final_10k": float(nav.iloc[-1] * 10000),
        "cagr": float(cagr),
        "max_drawdown": float(dd.min()),
        "ann_vol": float(vol),
        "sharpe": float(sharpe),
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else np.nan,
        "turnover": float(result["turnover"].sum()),
        "avg_gross_exposure": float(result["gross_exposure"].mean()),
    }


def monthly_capture(strategy_ret, btc_ret):
    s = (1 + strategy_ret).resample("ME").prod() - 1
    b = (1 + btc_ret).resample("ME").prod() - 1
    x = pd.concat([s.rename("s"), b.rename("b")], axis=1).dropna()
    up = x[x.b > 0]
    down = x[x.b < 0]
    return {
        "up_months": int(len(up)),
        "down_months": int(len(down)),
        "upside_capture_avg_month": float(up.s.mean() / up.b.mean()) if len(up) and up.b.mean() else np.nan,
        "downside_capture_avg_month": float(down.s.mean() / down.b.mean()) if len(down) and down.b.mean() else np.nan,
    }


def annual_returns(ret):
    vals = (1 + ret).groupby(ret.index.year).prod() - 1
    return {str(int(y)): float(v) for y, v in vals.items()}


def rolling_outperformance(a_ret, b_ret, window_days=730, step=30):
    df = pd.concat([a_ret.rename("a"), b_ret.rename("b")], axis=1).dropna()
    rows = []
    for i in range(0, len(df) - window_days + 1, step):
        x = df.iloc[i:i + window_days]
        ar = (1 + x.a).prod() - 1
        br = (1 + x.b).prod() - 1
        rows.append((ar, br))
    if not rows:
        return {"windows": 0, "win_rate": np.nan, "median_excess_return": np.nan}
    excess = [a - b for a, b in rows]
    return {
        "windows": len(rows),
        "win_rate": float(np.mean([e > 0 for e in excess])),
        "median_excess_return": float(np.median(excess)),
    }


def main():
    close = {}
    for sym in SYMBOLS:
        print(f"Fetching {sym}...", flush=True)
        close[sym.replace("USDT", "")] = fetch_daily(sym)

    prices = pd.concat(close, axis=1).dropna()
    # Strict 240d warm-up on the common SOL-inclusive history.
    raw_start = prices.index.min()
    eval_start = max(pd.Timestamp("2021-05-01"), raw_start + pd.Timedelta(days=260))
    eval_end = min(prices.index.max(), pd.Timestamp(END_DATE))

    rotation_w, diag = build_rotation_weights(prices)
    btc_beta = diag["beta"].clip(upper=1.50)
    a_w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    a_w["BTC"] = btc_beta

    hold_w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    hold_w["BTC"] = 1.0

    # Equal-weight benchmark, rebalanced when aggregate deviation reaches 5%.
    eq_w = pd.DataFrame(0.25, index=prices.index, columns=prices.columns)

    strategies = {}
    helds = {}
    for name, weights, band in [
        ("BTC_HOLD", hold_w, None),
        ("FOUR_COIN_EQUAL_25", eq_w, 0.05),
        ("A_BTC_DYNAMIC_CORE", a_w, None),
        ("A_BTC_DYNAMIC_BAND05", a_w, 0.05),
        ("B_ROTATION_CORE", rotation_w, None),
        ("B_ROTATION_BAND05", rotation_w, 0.05),
    ]:
        res, held = run_portfolio(prices, weights, eval_start, eval_end, band=band)
        strategies[name] = res
        helds[name] = held

    btc_daily = prices["BTC"].pct_change().loc[eval_start:eval_end].fillna(0.0)
    report = {
        "methodology": {
            "data": "Binance spot UTC daily closes via public market-data REST endpoint",
            "raw_common_start": str(raw_start.date()),
            "evaluation_start": str(eval_start.date()),
            "evaluation_end": str(eval_end.date()),
            "transaction_cost_bps_per_abs_weight_change": COST_BPS,
            "funding_included": False,
            "lookahead": "none; prior-day signal/weight applied to next daily return",
            "rotation_rule": "BTC regime; risk-off BTC only; risk-on BTC core plus top-2 eligible ETH/SOL/BNB by own+relative trend, inverse-vol allocation, SOL/BNB/ETH caps",
        },
        "metrics": {},
        "monthly_capture_vs_btc": {},
        "annual_returns": {},
        "rolling_2y_vs_btc_hold": {},
        "rotation_diagnostics": {},
    }

    for name, res in strategies.items():
        report["metrics"][name] = metrics(res)
        report["monthly_capture_vs_btc"][name] = monthly_capture(res["return"], btc_daily)
        report["annual_returns"][name] = annual_returns(res["return"])
        report["rolling_2y_vs_btc_hold"][name] = rolling_outperformance(res["return"], strategies["BTC_HOLD"]["return"])

    bheld = helds["B_ROTATION_BAND05"]
    report["rotation_diagnostics"] = {
        "average_weights": {c: float(bheld[c].mean()) for c in bheld.columns},
        "days_weight_positive_pct": {c: float((bheld[c] > 1e-8).mean()) for c in bheld.columns},
        "average_gross": float(bheld.abs().sum(axis=1).mean()),
        "days_gross_gt_1_pct": float((bheld.abs().sum(axis=1) > 1.0).mean()),
        "btc_negative_trend_days_pct": float((diag["btc_trend"].loc[eval_start:eval_end] < 0).mean()),
        "current_target_weights": {c: float(rotation_w.loc[:eval_end].iloc[-1][c]) for c in prices.columns},
        "current_btc_trend": float(diag["btc_trend"].loc[:eval_end].iloc[-1]),
        "current_btc_beta_budget": float(min(diag["beta"].loc[:eval_end].iloc[-1], 1.30)),
    }

    # Stress windows are fixed historical episodes, not optimized dates.
    stress_windows = {
        "2021_2022_bear": ("2021-11-10", "2022-11-21"),
        "2023_2024_bull": ("2023-01-01", "2024-03-31"),
        "2024_2025_period": ("2024-04-01", "2025-12-31"),
    }
    report["stress_windows"] = {}
    for label, (s, e) in stress_windows.items():
        report["stress_windows"][label] = {}
        for name, res in strategies.items():
            seg = res.loc[s:e]
            if len(seg):
                rr = (1 + seg["return"]).prod() - 1
                n = (1 + seg["return"]).cumprod()
                dd = (n / n.cummax() - 1).min()
                report["stress_windows"][label][name] = {"return": float(rr), "max_drawdown": float(dd)}

    Path("research/results").mkdir(parents=True, exist_ok=True)
    Path("research/results/crypto_rotation_backtest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== BACKTEST_REPORT_JSON ===")
    print(json.dumps(report, indent=2))
    print("=== END_BACKTEST_REPORT_JSON ===")


if __name__ == "__main__":
    main()
