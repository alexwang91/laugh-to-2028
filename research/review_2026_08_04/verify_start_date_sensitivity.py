"""Check how much of the headline result is the 2022-12-10 start date.

README reports V1 = 61.26% CAGR / -37.64% MDD and BRRK-0011 = 65.10% / -33.72%.
validated_summary.json shows those are measured on 2022-12-10 .. 2026-08-02,
which begins ~3 weeks after the 2022-11-21 cycle low. This runs the *same*
gross<=1 V1 weight construction over alternative start dates.
"""
import math
import sys
import time

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, "/home/user/laugh-to-2028/research/core")
import crypto_rotation_backtest as bt  # noqa: E402

COST_BPS = 5.0


def fetch(symbol, start="2020-08-01", end="2026-08-03"):
    ms = lambda t: int(pd.Timestamp(t, tz="UTC").timestamp() * 1000)
    start_ms, end_ms = ms(start), ms(end)
    rows, cur = [], start_ms
    while cur < end_ms:
        r = requests.get("https://data-api.binance.vision/api/v3/klines",
                         params={"symbol": symbol, "interval": "1d", "startTime": cur,
                                 "endTime": end_ms, "limit": 1000}, timeout=45)
        r.raise_for_status()
        p = r.json()
        if not p:
            break
        rows.extend(p)
        nxt = int(p[-1][0]) + 86_400_000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.05)
    df = pd.DataFrame(rows, columns=["open_time", "o", "h", "l", "close", "v", "ct",
                                     "qv", "n", "tb", "tq", "ig"])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    df["close"] = df["close"].astype(float)
    return df.drop_duplicates("date").set_index("date")["close"].sort_index()


def v1_gross_capped(prices):
    """research/hybrid_meta/walkforward_v1_meta.build_benchmark_v1"""
    w, _ = bt.build_rotation_weights(prices)
    g = w.abs().sum(axis=1)
    s = pd.Series(1.0, index=w.index)
    s[g > 1.0] = 1.0 / g[g > 1.0]
    return w.mul(s, axis=0)


def run(prices, target_w, start, end, band=0.05, rf_annual=0.0):
    tw = bt.apply_band(target_w, band)
    held = tw.shift(1).fillna(0.0)
    rets = prices.pct_change().fillna(0.0)
    idx = prices.loc[start:end].index
    held, rets = held.loc[idx], rets.loc[idx]
    turn = held.diff().abs().sum(axis=1)
    turn.iloc[0] = held.iloc[0].abs().sum()
    cash = (1.0 - held.sum(axis=1)).clip(lower=0.0)
    net = (held * rets).sum(axis=1) - turn * COST_BPS / 10_000.0 \
        + cash * (rf_annual / 365.0)
    return net


def metrics(r, rf_annual=0.0):
    r = r.dropna()
    nav = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    dd = nav / nav.cummax() - 1
    cagr = float(nav.iloc[-1] ** (1 / yrs) - 1)
    ex = r - rf_annual / 365.0
    return dict(days=len(r), years=round(yrs, 2), final=float(nav.iloc[-1] * 10000),
                cagr=cagr, mdd=float(dd.min()),
                sharpe=float(r.mean() / r.std() * math.sqrt(365)),
                sharpe_ex=float(ex.mean() / ex.std() * math.sqrt(365)),
                calmar=cagr / abs(float(dd.min())))


def main():
    close = {s.replace("USDT", ""): fetch(s)
             for s in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]}
    prices = pd.concat(close, axis=1).dropna()
    print("panel", prices.index.min().date(), "->", prices.index.max().date())

    w = v1_gross_capped(prices)
    end = pd.Timestamp("2026-08-02")

    print("\n=== SAME gross<=1 V1 construction, different start dates ===")
    hdr = f"{'start':<12}{'yrs':>6}{'final$10k':>12}{'CAGR':>9}{'MDD':>9}{'Sharpe':>8}{'Calmar':>8}"
    print(hdr)
    print("-" * len(hdr))
    for start in ["2021-05-01", "2021-11-10", "2022-01-01", "2022-06-01",
                  "2022-12-10", "2023-06-18", "2024-01-01"]:
        r = run(prices, w, pd.Timestamp(start), end)
        m = metrics(r)
        star = "  <- README window" if start == "2022-12-10" else ""
        print(f"{start:<12}{m['years']:>6}{m['final']:>12,.0f}{m['cagr']*100:>8.2f}%"
              f"{m['mdd']*100:>8.2f}%{m['sharpe']:>8.3f}{m['calmar']:>8.3f}{star}")

    print("\n=== rolling 3.65y windows (README window length), monthly steps ===")
    r_full = run(prices, w, pd.Timestamp("2021-05-01"), end)
    win = int(3.65 * 365)
    rows = []
    for i in range(0, len(r_full) - win + 1, 30):
        seg = r_full.iloc[i:i + win]
        nav = (1 + seg).cumprod()
        dd = float((nav / nav.cummax() - 1).min())
        rows.append((seg.index[0].date(),
                     float(nav.iloc[-1] ** (365.25 / len(seg)) - 1), dd))
    cagrs = np.array([x[1] for x in rows])
    mdds = np.array([x[2] for x in rows])
    print(f"windows={len(rows)}  CAGR  min {cagrs.min()*100:.1f}%  median "
          f"{np.median(cagrs)*100:.1f}%  max {cagrs.max()*100:.1f}%")
    print(f"                MDD   worst {mdds.min()*100:.1f}%  median "
          f"{np.median(mdds)*100:.1f}%  best {mdds.max()*100:.1f}%")
    pct = float((cagrs < 0.6125).mean())
    print(f"README's 61.25% CAGR sits at the {pct*100:.0f}th percentile of "
          f"same-length windows")
    pctd = float((mdds < -0.3763).mean())
    print(f"README's -37.63% MDD is *better* than {(1-pctd)*100:.0f}% of "
          f"same-length windows")

    print("\n=== effect of crediting cash at a T-bill rate (2022-12-10 window) ===")
    for rf in [0.0, 0.03, 0.045]:
        r = run(prices, w, pd.Timestamp("2022-12-10"), end, rf_annual=rf)
        m = metrics(r, rf_annual=rf)
        avg_cash = float((1.0 - bt.apply_band(w, 0.05).shift(1).fillna(0.0)
                          .loc[pd.Timestamp("2022-12-10"):end].sum(axis=1))
                         .clip(lower=0).mean())
        print(f"  rf={rf*100:4.1f}%  CAGR {m['cagr']*100:6.2f}%  "
              f"Sharpe(raw) {m['sharpe']:.3f}  Sharpe(excess) {m['sharpe_ex']:.3f}  "
              f"mean idle cash {avg_cash*100:.1f}%")


if __name__ == "__main__":
    main()
