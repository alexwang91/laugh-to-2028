"""Canonical performance-metric definitions for new experiments.

Backlog F7: `research/results/pit_disp_0015/validated_summary.json` reports
BRRK-0011's CAGR as 0.6510389, while `research/results/asym_beta_0024/summary.json`
reports the same strategy (identical `final_10k` = 62247.3823) as 0.6516610.
The 0.07pp gap is not a data or strategy difference -- it is two independent
`metrics()` implementations using two different year-count conventions:

- `research/core/crypto_rotation_backtest.py::metrics` and
  `research/hybrid_meta/walkforward_v1_meta.py::metrics` (which the
  pit_disp_0015 chain uses) divide by `len(returns) / 365.25` -- an
  **observation-count** year length. For the BRRK-0011 series that is
  1332 / 365.25.
- `research/asym_beta/run_asym_beta_0021.py::metrics` (which the asym_beta and
  carry chains use) divides by `(last_date - first_date).days / 365.25` -- a
  **calendar-span** year length. For the same series that is 1331 / 365.25.

Both are internally consistent and neither is a bug in isolation; they simply
answer "how many years is this" two different ways, and observation-count and
calendar-span agree only when the series has no gaps and someone doesn't
introduce an off-by-one at the boundary (this repo's series don't have gaps,
so the entire 0.07pp gap here is exactly that boundary rounding).

**This module standardizes on the calendar-span convention** for new work,
because it stays correct if a future series ever has a gap (a delisting, a
missing observation) where observation-count would silently understate the
elapsed time and inflate CAGR. `crypto_rotation_backtest.py` is frozen
strategy foundation and is not modified by this change; `walkforward_v1_meta.py`
is depended on by many already-published reports (dispersion overlay,
PIT-DISP-0015, and everything built on top of them) and is also left
unmodified, so that no committed number is silently restated. New experiments
should import from here instead of writing a fourth `metrics()` variant.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

DAYS_PER_YEAR = 365.25
TRADING_DAYS_PER_YEAR = 365.0


def elapsed_years(index: pd.Index) -> float:
    """Calendar-span year count: (last - first).days / 365.25.

    Floored at 1 day so a single-observation series doesn't divide by zero.

    **Caller trap, found the hard way 2026-08-06.** This measures the span of
    the index it is handed, so it is only right if that index covers the
    strategy's whole life. Deriving returns from an equity curve with
    ``equity.pct_change().dropna()`` silently drops the first row, which both
    discards a day of PNL and shortens the span by one day — on the 1331-day
    BRRK-0011 window that alone inflates CAGR by ~0.06 pp and produced a third
    published CAGR next to the two this module exists to reconcile. When
    converting an equity curve, seed the first return off the known base
    capital instead::

        ret = equity.pct_change()
        ret.iloc[0] = equity.iloc[0] / BASE_CAPITAL - 1.0

    That is the convention ``verify_psr_dsr_mintrl.py`` and
    ``verify_idle_cash_credit.py`` use, and ``test_metrics.py`` pins.
    """
    if len(index) < 2:
        return 1.0 / DAYS_PER_YEAR
    span_days = (index[-1] - index[0]).days
    return max(span_days, 1) / DAYS_PER_YEAR


def cagr_from_returns(ret: pd.Series) -> float:
    ret = ret.dropna()
    if len(ret) == 0:
        return float("nan")
    nav = (1.0 + ret).cumprod()
    years = elapsed_years(ret.index)
    return float(nav.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else float("nan")


def max_drawdown(nav: pd.Series) -> float:
    dd = nav / nav.cummax() - 1.0
    return float(dd.min())


def sharpe_ratio(ret: pd.Series) -> float:
    ret = ret.dropna()
    std = float(ret.std(ddof=1))
    # A near-constant series can produce a std on the order of 1e-19 from
    # floating-point cancellation in pandas' variance computation, rather
    # than exact 0.0 -- an `std <= 0` guard alone misses that and divides by
    # noise, producing a meaningless Sharpe on the order of 1e16.
    if not np.isfinite(std) or std <= 1e-12:
        return float("nan")
    return float(ret.mean() / std * math.sqrt(TRADING_DAYS_PER_YEAR))


def metrics(
    ret: pd.Series,
    turnover: pd.Series | None = None,
    gross: pd.Series | None = None,
) -> dict[str, Any]:
    """Canonical metrics dict for new experiments. Calendar-span CAGR."""
    ret = ret.dropna()
    if len(ret) == 0:
        return {}
    nav = (1.0 + ret).cumprod()
    years = elapsed_years(ret.index)
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else float("nan")
    dd = max_drawdown(nav)
    sharpe = sharpe_ratio(ret)
    calmar = float(cagr / abs(dd)) if dd < 0 else float("nan")
    out: dict[str, Any] = {
        "start": str(ret.index[0].date()),
        "end": str(ret.index[-1].date()),
        "observations": int(len(ret)),
        "elapsed_years": float(years),
        "end_multiple": float(nav.iloc[-1]),
        "final_10k": float(nav.iloc[-1] * 10_000.0),
        "cagr": cagr,
        "max_drawdown": dd,
        "ann_vol": float(ret.std(ddof=1) * math.sqrt(TRADING_DAYS_PER_YEAR)),
        "sharpe": sharpe,
        "calmar": calmar,
    }
    if turnover is not None:
        out["turnover"] = float(turnover.reindex(ret.index).fillna(0.0).sum())
    if gross is not None:
        out["avg_gross_exposure"] = float(gross.reindex(ret.index).mean())
    return out


# --- Frozen historical values, pinned by test_metrics.py -------------------
# These constants exist so a reader can see, without re-deriving it, exactly
# what each already-published BRRK-0011 CAGR is and why the two differ. They
# are not used by any runtime code path.
PIT_DISP_0015_BRRK0011_CAGR = 0.6510389          # observation-count, n=1332
ASYM_BETA_0024_BRRK0011_CAGR = 0.6516609785339953  # calendar-span, span=1331 days
PIT_DISP_0015_BRRK0011_FINAL_10K = 62247.3823
ASYM_BETA_0024_BRRK0011_FINAL_10K = 62247.38231294191
