"""Probabilistic / Deflated Sharpe on the repo's own committed BRRK-0011 series.

Bailey & Lopez de Prado (2014), "The Deflated Sharpe Ratio".
  PSR(SR*) = Phi[ (SR_hat - SR*) sqrt(N-1) / sqrt(1 - g3 SR_hat + (g4-1)/4 SR_hat^2) ]
  MinTRL   = 1 + [1 - g3 SR_hat + (g4-1)/4 SR_hat^2] (z_a / (SR_hat - SR*))^2
  SR*      = sqrt(V[SR_trials]) [ (1-g) Phi^-1(1 - 1/K) + g Phi^-1(1 - 1/(K e)) ]

All Sharpes below are per-day; annualised figures use sqrt(365).
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

RES = Path("/home/user/laugh-to-2028/research/results")
EULER = 0.5772156649015329


def series(col):
    eq = pd.read_csv(RES / "pit_disp_0015/daily_equity.csv", parse_dates=["date"]).set_index("date")
    e = eq[col].astype(float)
    r = e.pct_change()
    r.iloc[0] = e.iloc[0] / 10_000.0 - 1.0
    return r


def psr(sr_hat, sr_star, n, g3, g4):
    denom = math.sqrt(max(1.0 - g3 * sr_hat + (g4 - 1.0) / 4.0 * sr_hat ** 2, 1e-12))
    return float(norm.cdf((sr_hat - sr_star) * math.sqrt(n - 1) / denom))


def mintrl(sr_hat, sr_star, g3, g4, alpha=0.95):
    if sr_hat <= sr_star:
        return float("inf")
    z = norm.ppf(alpha)
    return 1.0 + (1.0 - g3 * sr_hat + (g4 - 1.0) / 4.0 * sr_hat ** 2) * (z / (sr_hat - sr_star)) ** 2


def expected_max_sr(k, var_trials):
    if k < 2:
        return 0.0
    a = norm.ppf(1.0 - 1.0 / k)
    b = norm.ppf(1.0 - 1.0 / (k * math.e))
    return math.sqrt(var_trials) * ((1.0 - EULER) * a + EULER * b)


def main():
    summary = json.loads((RES / "pit_disp_0015/validated_summary.json").read_text())
    sharpes_ann = np.array([v["sharpe"] for v in summary["metrics"].values()])
    var_trials_daily = float(np.var(sharpes_ann / math.sqrt(365.0), ddof=1))

    print("=== inputs taken from the repo's own committed results ===")
    print(f"variants in validated_summary.json : {len(sharpes_ann)}  "
          f"annualised Sharpes {np.round(sharpes_ann,3).tolist()}")
    print(f"V[SR] across those variants (daily): {var_trials_daily:.3e}\n")

    for col in ["BRRK0011_BASELINE", "V1_BASELINE"]:
        r = series(col).dropna()
        n = len(r)
        sr_d = float(r.mean() / r.std(ddof=1))
        sr_a = sr_d * math.sqrt(365)
        g3 = float(r.skew())
        g4 = float(r.kurtosis() + 3.0)          # pandas gives excess kurtosis

        print(f"--- {col} ---")
        print(f"  N={n} days ({n/365.25:.2f} y)   annualised Sharpe {sr_a:.3f}   "
              f"skew {g3:+.3f}   kurtosis {g4:.2f}")
        print(f"  PSR(SR*=0)   = {psr(sr_d, 0.0, n, g3, g4)*100:6.2f}%   "
              f"(prob. true Sharpe > 0)")
        for star_a in [0.5, 1.0]:
            p = psr(sr_d, star_a / math.sqrt(365), n, g3, g4)
            print(f"  PSR(SR*={star_a:.1f}) = {p*100:6.2f}%   "
                  f"(prob. true annual Sharpe > {star_a:.1f})")
        m = mintrl(sr_d, 1.0 / math.sqrt(365), g3, g4)
        print(f"  MinTRL to call annual Sharpe > 1.0 at 95%: {m:,.0f} days "
              f"({m/365.25:.2f} y)  -- have {n/365.25:.2f} y")

        print("  Deflated Sharpe vs number of effective trials K:")
        for k in [1, 6, 12, 20, 50, 100]:
            sr_star = expected_max_sr(k, var_trials_daily)
            d = psr(sr_d, sr_star, n, g3, g4)
            print(f"     K={k:>4}  SR*(ann)={sr_star*math.sqrt(365):5.3f}  "
                  f"DSR={d*100:6.2f}%")
        print()

    print("=== how many configurations has this project actually tried? ===")
    reg = json.loads((Path("/home/user/laugh-to-2028/research/regime_kelly")
                      / "experiment_registry.json").read_text())
    def count(x):
        if isinstance(x, dict):
            return sum(count(v) for v in x.values()) + (1 if "experiment_id" in x else 0)
        if isinstance(x, list):
            return sum(count(v) for v in x)
        return 0
    print(f"  experiment_registry.json declares ~{count(reg)} registered experiment records")
    print("  README/docs additionally reference BRRK-0004..0011, DISP-0013/0014,")
    print("  PIT-DISP-0015, PIT-ALPHA-0016/0018, AUDIT-0010/0012/0013/0017,")
    print("  FUNDING-0001/0002/0003, ROUTER-0004/0005 -> K is plainly >= 20.")


if __name__ == "__main__":
    main()
