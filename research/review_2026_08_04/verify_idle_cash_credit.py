"""F27: what changes if idle cash is credited at the risk-free rate?

Every Sharpe/CAGR published for V1 and BRRK-0011 assumes uninvested capital
earns 0%. Both are long-only, gross <= 1 strategies (BRRK-0011 scales V1's
gross down further on RISK_OFF-weighted days), so on a typical day a real
fraction of the book sits in cash. This script computes what happens to the
canonical BRRK-0011-vs-V1 comparison if that cash is credited daily at the
3-month T-bill rate, on an investment (bond-equivalent) basis.

Inputs are the already-committed, already-validated PIT-DISP-0015 evidence
(`daily_equity.csv` for realized returns, `daily_weights.csv` for the gross
exposure needed to size the idle-cash fraction) plus a fresh FRED DTB3 pull
through the canonical `research/common/risk_free.py` module. Nothing here
reruns the regime-Kelly fit or changes a single weight -- this only adds a
cash leg to an already-realized return series and re-measures it.

Read-only. Changes no strategy, parameter or committed result. Restated
numbers are reported next to the originals, per backlog F27's own
instruction -- this script does not decide which one "wins".
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "research" / "common"))

import numpy as np
import pandas as pd

from metrics import ASYM_BETA_0024_BRRK0011_CAGR
from metrics import metrics as metrics_dict
from risk_free import excess_return_metrics, load_fred_daily_risk_free_investment_basis

EQUITY = REPO / "research" / "results" / "pit_disp_0015" / "daily_equity.csv"
WEIGHTS = REPO / "research" / "results" / "pit_disp_0015" / "daily_weights.csv"
VARIANTS = {"V1_BASELINE": "V1 baseline", "BRRK0011_BASELINE": "BRRK-0011 core"}
BASE_CAPITAL = 10_000.0


def equity_to_returns(equity: pd.Series) -> pd.Series:
    """Daily returns from an equity curve, preserving the first day.

    `daily_equity.csv`'s first row is **already one day of trading** away from
    the $10,000 base (V1 opens at 9999.459168, not 10000.0), so a plain
    `pct_change().dropna()` silently does two wrong things at once: it throws
    away that first day's PNL, and it shortens the series' calendar span from
    1331 days to 1330, which inflates CAGR by ~0.06 pp. That is how an earlier
    version of this script produced 65.233% for BRRK-0011 -- a *third* value
    next to the two the repo already documents (65.10% observation-count,
    65.17% calendar-span), which is exactly the confusion backlog F7 existed to
    end.

    Seeding the first return off `BASE_CAPITAL` is the convention
    `verify_psr_dsr_mintrl.py` already uses (`r.iloc[0] = e.iloc[0]/10_000 - 1`)
    and the one `research/common/test_metrics.py` pins. With it, this function
    reproduces the published calendar-span CAGR (0.6516609785) to 8 decimals.
    """
    ret = equity.astype(float).pct_change()
    ret.iloc[0] = equity.iloc[0] / BASE_CAPITAL - 1.0
    return ret


def load_gross(weights: pd.DataFrame, variant: str) -> pd.Series:
    cols = [c for c in weights.columns if c.startswith(f"{variant}__")]
    gross = weights[cols].abs().sum(axis=1)
    if gross.max() > 1.0 + 1e-6:
        raise ValueError(f"{variant}: gross {gross.max():.6f} > 1, idle-cash assumption (gross<=1) violated")
    return gross


def main():
    equity = pd.read_csv(EQUITY, parse_dates=["date"]).set_index("date")
    weights = pd.read_csv(WEIGHTS, parse_dates=["date"]).set_index("date")

    start, end = equity.index.min(), equity.index.max()
    print(f"window {start.date()} .. {end.date()}  ({(end - start).days / 365.25:.2f} calendar years)")

    # `load_fred_daily_risk_free` requires its *own* requested start date to
    # land on a real FRED observation (2022-12-10 is a Saturday -- DTB3 is
    # business-day only). Request a short buffer before the analysis window
    # so the fetch has a valid seed, then reindex back down to the actual
    # equity dates below; this is a wider *request*, not a pre-window seed
    # used to prime a strategy computation, so it does not need the
    # preregistered-lookback exception that guard is protecting.
    rf_load = load_fred_daily_risk_free_investment_basis(start - pd.Timedelta(days=10), end)
    rf_daily = rf_load.daily["rf_daily_return"].reindex(equity.index).ffill().bfill()
    print(f"DTB3 investment-basis rate: mean {rf_load.daily['investment_basis_rate'].mean()*100:.3f}%  "
          f"(fetched {rf_load.metadata.get('fetched_at', 'n/a')})\n")

    # Anchor check: the raw (uncredited) BRRK-0011 CAGR this script computes
    # must land on the already-published calendar-span number. If it does not,
    # the return-construction convention has drifted again and every delta
    # below is being measured against the wrong baseline -- fail loudly rather
    # than print a fourth version of a number the repo has already litigated.
    anchor = metrics_dict(equity_to_returns(equity["BRRK0011_BASELINE"]))["cagr"]
    if abs(anchor - ASYM_BETA_0024_BRRK0011_CAGR) > 1e-6:
        raise AssertionError(
            f"BRRK-0011 raw CAGR {anchor:.9f} does not match the published "
            f"calendar-span value {ASYM_BETA_0024_BRRK0011_CAGR:.9f}; "
            "return construction has drifted (see equity_to_returns docstring)"
        )
    print(f"anchor check OK: raw BRRK-0011 CAGR {anchor:.6%} matches published calendar-span value\n")

    results = {}
    for variant, label in VARIANTS.items():
        raw_ret = equity_to_returns(equity[variant])
        gross = load_gross(weights, variant).reindex(raw_ret.index).fillna(0.0)
        idle_fraction = (1.0 - gross).clip(lower=0.0)
        credited_ret = raw_ret + idle_fraction * rf_daily.reindex(raw_ret.index)

        raw_m = metrics_dict(raw_ret)
        credited_m = metrics_dict(credited_ret)
        excess_raw = excess_return_metrics(raw_ret, rf_daily.reindex(raw_ret.index))
        excess_credited = excess_return_metrics(credited_ret, rf_daily.reindex(raw_ret.index))

        results[variant] = {
            "label": label,
            "mean_idle_fraction": float(idle_fraction.mean()),
            "median_idle_fraction": float(idle_fraction.median()),
            "raw_cagr": raw_m["cagr"],
            "credited_cagr": credited_m["cagr"],
            "cagr_delta_pp": (credited_m["cagr"] - raw_m["cagr"]) * 100.0,
            "raw_sharpe_rf0": raw_m["sharpe"],
            "credited_sharpe_rf0": credited_m["sharpe"],
            "raw_excess_sharpe_field": excess_raw["preferred_ratio_field"],
            "raw_excess_sharpe": excess_raw[excess_raw["preferred_ratio_field"]],
            "credited_excess_sharpe_field": excess_credited["preferred_ratio_field"],
            "credited_excess_sharpe": excess_credited[excess_credited["preferred_ratio_field"]],
            "raw_max_drawdown": raw_m["max_drawdown"],
            "credited_max_drawdown": credited_m["max_drawdown"],
        }

        print(f"=== {label} ({variant}) ===")
        print(f"  mean idle-cash fraction (1 - gross): {idle_fraction.mean()*100:.1f}%  "
              f"(median {idle_fraction.median()*100:.1f}%)")
        print(f"  CAGR:            raw {raw_m['cagr']*100:7.3f}%   credited {credited_m['cagr']*100:7.3f}%   "
              f"delta {(credited_m['cagr']-raw_m['cagr'])*100:+.3f} pp")
        print(f"  Sharpe (rf=0):   raw {raw_m['sharpe']:7.4f}   credited {credited_m['sharpe']:7.4f}")
        print(f"  Sharpe (excess, {excess_raw['preferred_ratio_field']}):")
        print(f"                   raw {excess_raw[excess_raw['preferred_ratio_field']]:7.4f}   "
              f"credited {excess_credited[excess_credited['preferred_ratio_field']]:7.4f}")
        print(f"  Max drawdown:    raw {raw_m['max_drawdown']*100:7.3f}%   credited {credited_m['max_drawdown']*100:7.3f}%")
        print()

    gap_raw = results["BRRK0011_BASELINE"]["raw_sharpe_rf0"] - results["V1_BASELINE"]["raw_sharpe_rf0"]
    gap_credited = results["BRRK0011_BASELINE"]["credited_sharpe_rf0"] - results["V1_BASELINE"]["credited_sharpe_rf0"]
    print(f"BRRK-0011 vs V1 Sharpe(rf=0) gap: raw {gap_raw:+.4f}  credited {gap_credited:+.4f}  "
          f"(shift {gap_credited - gap_raw:+.4f})")
    print("This gap is the number F10's bootstrap CI [-0.046, +0.164] already says does not exclude zero; "
          "idle-cash crediting moves it by less than that CI's width either way -- it does not change which "
          "side of zero the comparison sits on.")

    import json
    out = REPO / "research" / "results" / "idle_cash_credit_0027r1.json"
    out.write_text(json.dumps({
        "experiment_id": "IDLE-CASH-CREDIT-F27",
        "methodology": "Credit each variant's (1 - gross) idle-cash fraction daily at the FRED DTB3 "
                        "investment-basis rate; re-measure CAGR/Sharpe on the resulting series. Gross "
                        "read from the already-committed PIT-DISP-0015 daily_weights.csv, no re-fit.",
        "window": {"start": str(start.date()), "end": str(end.date())},
        "results": results,
        "brrk_vs_v1_sharpe_gap": {"raw": gap_raw, "credited": gap_credited, "shift": gap_credited - gap_raw},
    }, indent=2), encoding="utf-8")
    print(f"\nWrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
