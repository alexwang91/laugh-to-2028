"""Compare CARRY-PNL-0031 against the risk-free rate over its own window.

CARRY-PNL-0031 is a delta-neutral, fully-collateralized long-spot / short-perp
book at gross 1.0. Its qualification gate `net_economics` tests the net return
against **zero**. For a delta-neutral fully-funded book the economically
meaningful hurdle is cash, because the strategy *is* a synthetic cash
instrument: every dollar it earns has to beat the dollar it displaces.

This script reads the committed 0031 annual returns and prices them against
3-month T-bills (FRED DTB3) over the identical 2020-09-15..2026-07-30 window.

Read-only. Changes no strategy, parameter or committed result.
"""
import io
import json
import subprocess

import numpy as np
import pandas as pd
import requests

FRED = ("https://fred.stlouisfed.org/graph/fredgraph.csv"
        "?id=DTB3&cosd=2020-09-15&coed=2026-07-30")
SUMMARY = "research/results/carry_pnl_0031/summary.json"
CARRY_CAGR = 0.02740          # canonical 5 bps net, from RESULT.md
CARRY_VOL = 0.01904


def committed_annual():
    raw = subprocess.run(["git", "show", f"origin/main:{SUMMARY}"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(raw)["annual_net_5bps"]


def tbill():
    r = requests.get(FRED, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", "rate"]
    df["date"] = pd.to_datetime(df["date"])
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    s = df.dropna().set_index("date")["rate"] / 100.0
    return s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D")).ffill()


def main():
    annual = committed_annual()
    cal = tbill()
    years = (cal.index[-1] - cal.index[0]).days / 365.25
    cash_growth = float(np.prod(1.0 + cal.to_numpy() / 365.0))
    cash_cagr = cash_growth ** (1 / years) - 1

    print(f"window {cal.index[0].date()} .. {cal.index[-1].date()}  ({years:.2f} y)")
    print(f"3M T-bill: mean {cal.mean()*100:.2f}%  median {cal.median()*100:.2f}%\n")

    print(f"{'':<26}{'CAGR':>9}{'$10k ->':>12}")
    print(f"{'CARRY-PNL-0031 (5 bps)':<26}{CARRY_CAGR*100:>8.3f}%"
          f"{10000*(1+CARRY_CAGR)**years:>12,.0f}")
    print(f"{'3M T-bills, same window':<26}{cash_cagr*100:>8.3f}%{10000*cash_growth:>12,.0f}")
    print(f"{'excess over cash':<26}{(CARRY_CAGR-cash_cagr)*100:>+8.3f} pp/yr")
    print(f"{'reported Sharpe':<26}{1.428:>9.3f}")
    print(f"{'Sharpe vs cash':<26}{(CARRY_CAGR-cash_cagr)/CARRY_VOL:>9.3f}   "
          f"(excess return / {CARRY_VOL*100:.3f}% vol)\n")

    # Year-by-year, with partial first and last years handled by day count.
    frac = {"2020": 107 / 366, "2021": 1.0, "2022": 1.0, "2023": 1.0,
            "2024": 1.0, "2025": 1.0, "2026_through_07_30": 211 / 365}
    print(f"{'year':<22}{'carry':>9}{'cash':>9}{'excess':>10}")
    cash_by_year = {}
    for key, f in frac.items():
        y = int(key[:4])
        seg = cal[cal.index.year == y]
        cash_by_year[key] = float(np.prod(1.0 + seg.to_numpy() / 365.0)) - 1.0
        print(f"{key:<22}{annual[key]*100:>8.2f}%{cash_by_year[key]*100:>8.2f}%"
              f"{(annual[key]-cash_by_year[key])*100:>+9.2f}pp")

    post = [k for k in annual if k >= "2022"]
    g = float(np.prod([1 + annual[k] for k in post]))
    c = float(np.prod([1 + cash_by_year[k] for k in post]))
    yrs = sum(frac[k] for k in post)
    print(f"\npost-2021 ({yrs:.2f} y): carry {(g**(1/yrs)-1)*100:+.2f}%/yr  "
          f"cash {(c**(1/yrs)-1)*100:+.2f}%/yr  "
          f"excess {((g**(1/yrs)-1)-(c**(1/yrs)-1))*100:+.2f} pp/yr")

    total = float(np.prod([1 + v for v in annual.values()])) - 1.0
    ex2021 = float(np.prod([1 + v for k, v in annual.items() if k != "2021"])) - 1.0
    print(f"2021 alone: {annual['2021']*100:+.2f}% of the {total*100:+.2f}% cumulative")
    print(f"excluding 2021: {ex2021*100:+.2f}% cumulative over ~4.9 years")


if __name__ == "__main__":
    main()
