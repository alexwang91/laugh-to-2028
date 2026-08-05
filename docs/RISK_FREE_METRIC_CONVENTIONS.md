# Risk-free and excess-return metric conventions

Record of two conventions that are easy to confuse and are already committed in
two different forms. Written as a follow-up to the PR #31 review; it restates
nothing and changes no committed experiment result.

Code: [`research/common/risk_free.py`](../research/common/risk_free.py).

---

## 1. Which committed number uses which Sharpe denominator

CARRY-RF-0036R1 and R2 both publish a field called `excess_sharpe_over_rf`, and
the two do **not** mean the same thing. Both are correct arithmetic; only the
shared name is a problem.

| Artifact | Denominator | CARRY-PNL-0031 value |
|---|---|---:|
| `research/results/carry_rf_0036r1/` | volatility of **excess** returns | **-0.221582** |
| `research/results/carry_rf_0036r2/` | volatility of the **strategy** | **-0.223151** |

Neither is wrong, but the R1 denominator is the textbook one: the Sharpe ratio
of an excess-return series conventionally divides by that series' own
volatility.

R2 exists because PR #30 reported `-0.223`, and R2 was registered to reproduce
it exactly. That was unnecessary. PR #30 computed
`(carry_cagr − cash_cagr) / CARRY_VOL`, taking `CARRY_VOL = 0.01904` straight
out of CARRY-PNL-0031's published `RESULT.md` — a magnitude indicator, not a
proposed convention. The gap between the two is 0.0016 and neither changes the
`net_economics` gate, which is decided on **excess CAGR**, not on either ratio.

The lesson worth keeping: **an external review number is a cross-check, not a
target.** The right response to the discrepancy was a one-line note in R1, not a
new experiment.

Going forward, `excess_return_metrics()` names every denominator explicitly:
`excess_sharpe_excess_vol_denominator`, `excess_sharpe_strategy_vol_denominator`
and `excess_information_ratio`. `compare_to_cash()` is frozen exactly as R1 ran
it and must not be modified — the committed R1 evidence depends on its output
contract, which `test_compare_to_cash_contract_is_frozen` now pins.

## 2. When a geometric excess ratio stops being a Sharpe ratio

`research/results/carry_rf_0036r1/CARRY-STACK-0033-RF-RESTATEMENT.json` records
`excess_sharpe_over_rf = -16.21`. That is not a Sharpe ratio of anything.

The 0033 comparison is the combined stack against `BRRK + idle cash`, and those
two series are **99.99995% correlated daily**. The excess series therefore has
almost no volatility, so dividing a real geometric return difference by it
explodes:

| | value |
|---|---:|
| excess CAGR | -2.187% |
| excess annualized volatility | 0.135% |
| strategy annualized volatility | 44.16% |
| excess / strategy volatility ratio | **0.0031** |
| daily correlation to benchmark | **0.9999953** |
| `excess_sharpe_over_rf`, R1 (excess-vol denominator) | **-16.21** |
| `excess_sharpe_over_rf`, R2 (strategy-vol denominator) | **-0.0495** |
| **information ratio** (arithmetic, annualized) | **-10.31** |

R2's -0.0495 is not better — it divides by a volatility the excess series does
not have. **The correct statistic for a highly correlated pair is the
information ratio**, `mean(daily excess) / std(daily excess) × √365`, which here
is **-10.31**: the stack underperforms BRRK-plus-idle-cash with near certainty.
That is a *stronger and more interpretable* statement than either published
ratio, and it is what should have been quoted.

`excess_return_metrics()` now computes all three and sets
`geometric_sharpe_interpretable = False` whenever excess volatility falls below
10% of strategy volatility, pointing callers at `preferred_ratio_field`. The
0033 shape is covered by
`test_near_identical_series_flag_geometric_ratio_as_uninterpretable`.

**No decision changes.** Both 0033 gates fail on excess CAGR, and the carry line
is stopped either way. The committed R1 and R2 files stay exactly as they are;
this section exists so the -16.21 is not quoted later as if it were a Sharpe.

## 3. DTB3 is a discount-basis rate

FRED `DTB3` is the 3-month bill secondary-market rate quoted on a **bank
discount basis**. `load_fred_daily_risk_free` accrues it as
`percent / 100 / 365`, which treats a discount rate as an investment yield and
understates what cash actually earns.

Converting properly with `BEY = 365 d / (360 − 91 d)`:

| Basis | cash CAGR, 2020-09-15..2026-07-30 | CARRY-PNL-0031 excess |
|---|---:|---:|
| discount (as CARRY-RF-0036R1 froze it) | 3.1653% | -0.4249 pp/yr |
| investment (bond-equivalent) | 3.2469% | **-0.5065 pp/yr** |

The understatement averages **0.082 pp** over this window, and about 13 bp when
the rate is near 5%.

**For CARRY-RF-0036R1 this bias is conservative.** It makes cash look worse than
it is, so the measured carry shortfall is *smaller* than the true one and the
STOP decision is understated rather than overstated. R1 is therefore left
unchanged and un-restated.

**The sign flips wherever a higher risk-free rate would flatter a result.** That
includes backlog **F27**, which credits idle cash at the risk-free rate across
the repo and reports Sharpe on excess returns: there, understating cash inflates
both the credited carry and the excess Sharpe. F27 must use
`load_fred_daily_risk_free_investment_basis` (or `DGS3MO`, which FRED already
quotes on an investment basis).

---

## Rules for new work

1. Call `excess_return_metrics()`, not `compare_to_cash()`. The latter is frozen
   R1 evidence.
2. Quote `preferred_ratio_field`. If `geometric_sharpe_interpretable` is False,
   report the information ratio and say why — do not suppress the flag.
3. Use `load_fred_daily_risk_free_investment_basis()` unless an experiment has
   preregistered the discount basis and the bias direction is conservative for
   its conclusion.
4. When an external review disagrees with an internal number, first establish
   which definition each side used. Reproducing someone else's rounding is not a
   research result.
