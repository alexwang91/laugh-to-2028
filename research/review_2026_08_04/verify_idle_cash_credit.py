"""F27 R2 measurement correction: credit idle cash at the risk-free rate.

The original F27 overlay (`idle_cash_credit_0027r1.json`) converted committed
equity curves with ``equity.pct_change().dropna()``. That was a measurement
bug: `daily_equity.csv`'s first row is already the first realized strategy day
relative to the known $10,000 base, not an initial-capital placeholder. R1
therefore discarded a real first-day PnL observation and shortened the calendar
span by one day.

R2 changes only that return reconstruction. Strategy weights, BRRK/V1 logic,
risk-free methodology, evaluation window, and every economic decision remain
unchanged. R1 is preserved as superseded evidence; this script writes the R2
measurement next to it.
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
R1_RESULT = REPO / "research" / "results" / "idle_cash_credit_0027r1.json"
R2_RESULT = REPO / "research" / "results" / "idle_cash_credit_0027r2.json"
VARIANTS = {"V1_BASELINE": "V1 baseline", "BRRK0011_BASELINE": "BRRK-0011 core"}
BASE_CAPITAL = 10_000.0


def equity_to_returns(equity: pd.Series) -> pd.Series:
    """Convert a realized equity curve to returns without losing day one.

    The committed PIT-DISP-0015 curve begins after the first realized day, so
    the first return is `equity.iloc[0] / 10_000 - 1`, not NaN. Keeping that
    row also preserves the true 1331-day calendar span of the 1332-row series.
    """
    if equity.empty:
        raise ValueError("equity series must not be empty")
    ret = equity.astype(float).pct_change()
    ret.iloc[0] = float(equity.iloc[0]) / BASE_CAPITAL - 1.0
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

    # `load_fred_daily_risk_free` requires its own requested start date to land
    # on a real FRED observation. Request a short buffer and then reindex to the
    # exact committed equity dates. This does not seed any strategy feature.
    rf_load = load_fred_daily_risk_free_investment_basis(start - pd.Timedelta(days=10), end)
    rf_daily = rf_load.daily["rf_daily_return"].reindex(equity.index).ffill().bfill()
    print(
        f"DTB3 investment-basis rate: mean {rf_load.daily['investment_basis_rate'].mean()*100:.3f}%  "
        f"(fetched {rf_load.metadata.get('fetched_at', 'n/a')})\n"
    )

    # F7 already froze the calendar-span BRRK-0011 value. Refuse to emit a new
    # F27 measurement if return construction cannot reproduce that anchor.
    anchor = metrics_dict(equity_to_returns(equity["BRRK0011_BASELINE"]))["cagr"]
    if abs(anchor - ASYM_BETA_0024_BRRK0011_CAGR) > 1e-6:
        raise AssertionError(
            f"BRRK-0011 raw CAGR {anchor:.9f} does not match published calendar-span "
            f"anchor {ASYM_BETA_0024_BRRK0011_CAGR:.9f}; return construction drifted"
        )
    print(f"anchor check OK: BRRK-0011 raw CAGR {anchor:.6%}\n")

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
        print(
            f"  mean idle-cash fraction (1 - gross): {idle_fraction.mean()*100:.1f}%  "
            f"(median {idle_fraction.median()*100:.1f}%)"
        )
        print(
            f"  CAGR:            raw {raw_m['cagr']*100:7.3f}%   credited {credited_m['cagr']*100:7.3f}%   "
            f"delta {(credited_m['cagr']-raw_m['cagr'])*100:+.3f} pp"
        )
        print(f"  Sharpe (rf=0):   raw {raw_m['sharpe']:7.4f}   credited {credited_m['sharpe']:7.4f}")
        print(f"  Sharpe (excess, {excess_raw['preferred_ratio_field']}):")
        print(
            f"                   raw {excess_raw[excess_raw['preferred_ratio_field']]:7.4f}   "
            f"credited {excess_credited[excess_credited['preferred_ratio_field']]:7.4f}"
        )
        print(
            f"  Max drawdown:    raw {raw_m['max_drawdown']*100:7.3f}%   "
            f"credited {credited_m['max_drawdown']*100:7.3f}%"
        )
        print()

    gap_raw = results["BRRK0011_BASELINE"]["raw_sharpe_rf0"] - results["V1_BASELINE"]["raw_sharpe_rf0"]
    gap_credited = (
        results["BRRK0011_BASELINE"]["credited_sharpe_rf0"]
        - results["V1_BASELINE"]["credited_sharpe_rf0"]
    )
    print(
        f"BRRK-0011 vs V1 Sharpe(rf=0) gap: raw {gap_raw:+.4f}  credited {gap_credited:+.4f}  "
        f"(shift {gap_credited - gap_raw:+.4f})"
    )

    import json

    output = {
        "experiment_id": "IDLE-CASH-CREDIT-F27-R2-MEASUREMENT-FIX",
        "status": "MEASUREMENT_FIX",
        "supersedes_measurement": "research/results/idle_cash_credit_0027r1.json",
        "decision": (
            "R1 dropped the first realized equity observation. R2 preserves day-one PnL from the known "
            "$10,000 base. Absolute metrics are restated; the qualitative F27 conclusion is unchanged."
        ),
        "methodology": (
            "Credit each variant's (1 - gross) idle-cash fraction daily at the FRED DTB3 investment-basis "
            "rate; reconstruct returns from committed PIT-DISP-0015 equity with day one seeded from the known "
            "$10,000 base; no strategy re-fit or weight change."
        ),
        "window": {"start": str(start.date()), "end": str(end.date())},
        "results": results,
        "brrk_vs_v1_sharpe_gap": {
            "raw": gap_raw,
            "credited": gap_credited,
            "shift": gap_credited - gap_raw,
        },
        "r1_preserved_at": str(R1_RESULT.relative_to(REPO)),
    }
    R2_RESULT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {R2_RESULT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
