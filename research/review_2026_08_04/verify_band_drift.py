"""Quantify the weight-drift turnover that the repo's backtester never charges.

The repo's run_portfolio()/evaluate_array() treat `held` as a constant weight
vector between band-triggered rebalances and compute turnover as
|held_t - held_{t-1}|.  Holding a *constant weight vector* while prices move
requires daily trading back to target, which is never charged.  This script
reconstructs the same BRRK-0011 / V1 weight paths and measures the true
implementable turnover under two consistent conventions.
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
    rows = []
    cur = start_ms
    while cur < end_ms:
        r = requests.get(
            "https://data-api.binance.vision/api/v3/klines",
            params={"symbol": symbol, "interval": "1d", "startTime": cur,
                    "endTime": end_ms, "limit": 1000}, timeout=45)
        r.raise_for_status()
        payload = r.json()
        if not payload:
            break
        rows.extend(payload)
        nxt = int(payload[-1][0]) + 86_400_000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.05)
    df = pd.DataFrame(rows, columns=["open_time", "o", "h", "l", "close", "v", "ct",
                                     "qv", "n", "tb", "tq", "ig"])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    df["close"] = df["close"].astype(float)
    return df.drop_duplicates("date").set_index("date")["close"].sort_index()


def repo_convention(prices, target_w, band, cost_bps=COST_BPS):
    """Exactly what research/core/crypto_rotation_backtest.run_portfolio does."""
    tw = bt.apply_band(target_w, band)
    held = tw.shift(1).fillna(0.0)
    rets = prices.pct_change().fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = (held * rets).sum(axis=1)
    net = gross - turnover * cost_bps / 10_000.0
    return net, turnover


def drift_consistent(prices, target_w, band, cost_bps=COST_BPS):
    """Same signal, but weights actually drift and trades are actually costed.

    On each date the previous day's post-return actual weights are compared
    with the standing target.  The band decides whether to trade; if it does
    not, the drifted weights are carried (that is what 'not trading' means).
    """
    rets = prices.pct_change().fillna(0.0).to_numpy(float)
    tgt = target_w.to_numpy(float)
    n, k = tgt.shape

    actual = np.zeros(k)          # weights carried into the day
    standing = np.zeros(k)        # last adopted target
    net = np.zeros(n)
    turn = np.zeros(n)

    for i in range(n):
        if i > 0:
            want = tgt[i - 1]
            if not np.all(np.isfinite(want)):
                want = standing
            # Band is evaluated against what we really hold, not against the
            # previously adopted target.
            if np.abs(want - actual).sum() >= band:
                traded = np.abs(want - actual).sum()
                actual = want.copy()
                standing = want.copy()
            else:
                traded = 0.0
            turn[i] = traded
            r = rets[i]
            port = float(actual @ r)
            net[i] = port - traded * cost_bps / 10_000.0
            # Weights drift with realised returns; cash sleeve is 1-gross.
            actual = actual * (1.0 + r) / (1.0 + port)
    return pd.Series(net, index=target_w.index), pd.Series(turn, index=target_w.index)


def metrics(r):
    r = r.dropna()
    nav = (1 + r).cumprod()
    yrs = len(r) / 365.25
    dd = nav / nav.cummax() - 1
    return {
        "final_10k": float(nav.iloc[-1] * 10000),
        "cagr": float(nav.iloc[-1] ** (1 / yrs) - 1),
        "mdd": float(dd.min()),
        "sharpe": float(r.mean() / r.std() * math.sqrt(365)),
    }


def main():
    close = {}
    for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]:
        close[sym.replace("USDT", "")] = fetch(sym)
        print("fetched", sym, flush=True)
    prices = pd.concat(close, axis=1).dropna()

    rot_w, diag = bt.build_rotation_weights(prices)
    eval_start = max(pd.Timestamp("2021-05-01"), prices.index.min() + pd.Timedelta(days=260))
    eval_end = min(prices.index.max(), pd.Timestamp("2026-08-03"))
    idx = prices.loc[eval_start:eval_end].index

    a_w = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    a_w["BTC"] = diag["beta"].clip(upper=1.50)

    print(f"\nevaluation window {idx[0].date()} .. {idx[-1].date()}  ({len(idx)} days)\n")

    for name, w in [("B_ROTATION_BAND05", rot_w), ("A_BTC_DYNAMIC_BAND05", a_w)]:
        r_repo, t_repo = repo_convention(prices, w, 0.05)
        r_true, t_true = drift_consistent(prices, w, 0.05)
        r_repo, t_repo = r_repo.loc[idx], t_repo.loc[idx]
        r_true, t_true = r_true.loc[idx], t_true.loc[idx]

        m_repo, m_true = metrics(r_repo), metrics(r_true)
        print(f"--- {name} ---")
        print(f"  turnover  repo-convention : {t_repo.sum():8.2f}   "
              f"({t_repo.sum()/(len(idx)/365.25):6.2f} x/yr)")
        print(f"  turnover  drift-consistent: {t_true.sum():8.2f}   "
              f"({t_true.sum()/(len(idx)/365.25):6.2f} x/yr)")
        print(f"  CAGR      repo   : {m_repo['cagr']*100:7.2f}%   "
              f"final ${m_repo['final_10k']:,.0f}   MDD {m_repo['mdd']*100:6.2f}%  "
              f"Sharpe {m_repo['sharpe']:.3f}")
        print(f"  CAGR      drift  : {m_true['cagr']*100:7.2f}%   "
              f"final ${m_true['final_10k']:,.0f}   MDD {m_true['mdd']*100:6.2f}%  "
              f"Sharpe {m_true['sharpe']:.3f}")
        print(f"  CAGR delta       : {(m_true['cagr']-m_repo['cagr'])*100:+.2f} pp\n")

    # How much daily rebalancing the repo silently assumes but never charges.
    tw = bt.apply_band(rot_w, 0.05)
    held = tw.shift(1).fillna(0.0).loc[idx]
    rets = prices.pct_change().fillna(0.0).loc[idx]
    port = (held * rets).sum(axis=1)
    drifted = held.mul(1 + rets).div((1 + port), axis=0)
    implied = (held.shift(-1).fillna(0.0) - drifted).abs().sum(axis=1)
    print(f"implied daily reset trading the repo performs for free: "
          f"{implied.sum():.2f} total, {implied.mean()*10000:.2f} bps/day of notional")
    print(f"unbilled cost at 5 bps: {implied.sum()*COST_BPS/10000*100:.2f}% of NAV "
          f"cumulative (arithmetic), ~{implied.mean()*365*COST_BPS/10000*100:.2f}%/yr")


if __name__ == "__main__":
    main()
