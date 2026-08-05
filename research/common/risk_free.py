"""Shared risk-free rate loading and excess-return metrics.

Two conventions matter here and are easy to confuse; see
`docs/RISK_FREE_METRIC_CONVENTIONS.md` for the full record.

**Quotation basis.** FRED `DTB3` is the 3-month bill secondary-market rate on a
**bank discount basis**, not an investment yield. `load_fred_daily_risk_free`
accrues it as `percent / 100 / 365`, which understates what cash actually earns
by roughly 8 bp over 2020-2026. CARRY-RF-0036R1 froze that conversion, and for
R1 the bias is conservative: it makes cash look *worse*, so the measured carry
shortfall is smaller than the true one and the STOP decision is if anything
understated. **That sign flips for any experiment where a higher risk-free rate
would flatter the result** — notably backlog F27, which puts repo-wide Sharpes
on an excess-return basis. New work should use `investment_basis_rate` /
`load_fred_daily_risk_free_investment_basis`.

**Sharpe denominator.** `compare_to_cash` is frozen as CARRY-RF-0036R1 ran it
and must not change: its `excess_sharpe_over_rf` divides geometric excess CAGR
by the volatility of *excess* returns. `excess_return_metrics` is the function
new code should call — it names every denominator explicitly and refuses to
present a geometric ratio as a Sharpe when the pair is too correlated for that
ratio to mean anything.
"""

from __future__ import annotations

import hashlib
import io
import math
from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests

FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
DEFAULT_SERIES_ID = "DTB3"
DAYS_PER_YEAR = 365.0
BILL_DAYS_TO_MATURITY = 91
DISCOUNT_BASIS_DAY_COUNT = 360.0

# Below this ratio of excess volatility to strategy volatility the two series are
# so close that geometric-excess / volatility ratios stop being interpretable.
# CARRY-STACK-0033 sits at 0.003 and produced a "Sharpe" of -16.21.
MIN_EXCESS_VOL_RATIO_FOR_GEOMETRIC_SHARPE = 0.10


@dataclass(frozen=True)
class RiskFreeLoad:
    daily: pd.DataFrame
    metadata: dict[str, Any]
    raw_csv: str


def _normalize_date(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is not None:
        ts = ts.tz_convert("UTC").tz_localize(None)
    return ts.normalize()


def fred_graph_url(series_id: str, start: Any, end: Any) -> str:
    start_ts = _normalize_date(start)
    end_ts = _normalize_date(end)
    if start_ts > end_ts:
        raise ValueError("risk-free start must be <= end")
    return (
        f"{FRED_GRAPH_URL}?id={series_id}"
        f"&cosd={start_ts.date()}&coed={end_ts.date()}"
    )


def load_fred_daily_risk_free(
    start: Any,
    end: Any,
    *,
    series_id: str = DEFAULT_SERIES_ID,
    timeout_seconds: int = 60,
    session: Any = requests,
) -> RiskFreeLoad:
    """Load a calendar-day risk-free series from FRED.

    F1 freezes DTB3 and the conversion ``percent / 100 / 365``. FRED publishes
    business-day observations, so missing calendar dates are forward-filled from
    the latest observation *inside the requested interval*. The first requested
    day must itself have a valid observation; callers that need a pre-window seed
    in later experiments must preregister and request that lookback explicitly.
    """

    start_ts = _normalize_date(start)
    end_ts = _normalize_date(end)
    url = fred_graph_url(series_id, start_ts, end_ts)
    response = session.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    raw_csv = response.text

    frame = pd.read_csv(io.StringIO(raw_csv))
    if frame.shape[1] < 2:
        raise RuntimeError(f"FRED {series_id}: unexpected CSV shape {frame.shape}")
    date_col = frame.columns[0]
    value_col = series_id if series_id in frame.columns else frame.columns[1]
    frame = frame[[date_col, value_col]].copy()
    frame.columns = ["date", "rate_percent"]
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["rate_percent"] = pd.to_numeric(frame["rate_percent"], errors="coerce")
    frame = frame.dropna(subset=["date"]).sort_values("date")
    frame["date"] = frame["date"].dt.tz_localize(None).dt.normalize()
    frame = frame.drop_duplicates(subset=["date"], keep="last")

    calendar = pd.date_range(start_ts, end_ts, freq="D")
    observed = frame.dropna(subset=["rate_percent"]).set_index("date")["rate_percent"].astype(float)
    observed = observed[(observed.index >= start_ts) & (observed.index <= end_ts)]
    if observed.empty:
        raise RuntimeError(f"FRED {series_id}: no valid observations in requested window")

    rate = observed.reindex(calendar).ffill()
    if pd.isna(rate.iloc[0]):
        raise RuntimeError(
            f"FRED {series_id}: first requested date {start_ts.date()} has no valid rate; "
            "pre-window seeding was not preregistered for this experiment"
        )
    if rate.isna().any():
        raise RuntimeError(f"FRED {series_id}: unresolved calendar-day rate after forward fill")

    source_date = pd.Series(pd.NaT, index=calendar, dtype="datetime64[ns]")
    source_date.loc[observed.index.intersection(calendar)] = observed.index.intersection(calendar)
    source_date = source_date.ffill()

    daily = pd.DataFrame(index=calendar)
    daily.index.name = "date"
    daily["fred_rate_percent"] = rate.astype(float)
    daily["source_observation_date"] = source_date.dt.strftime("%Y-%m-%d")
    daily["rf_daily_return"] = daily["fred_rate_percent"] / 100.0 / DAYS_PER_YEAR

    metadata = {
        "provider": "FRED",
        "series_id": series_id,
        "url": url,
        "requested_start": str(start_ts.date()),
        "requested_end": str(end_ts.date()),
        "calendar_days": int(len(daily)),
        "valid_fred_observations": int(len(observed)),
        "first_valid_observation": str(observed.index.min().date()),
        "last_valid_observation": str(observed.index.max().date()),
        "daily_return_conversion": "rate_percent / 100 / 365.0",
        "calendarization": "calendar daily; forward-fill latest in-window FRED observation",
        "raw_csv_sha256": hashlib.sha256(raw_csv.encode("utf-8")).hexdigest(),
    }
    return RiskFreeLoad(daily=daily, metadata=metadata, raw_csv=raw_csv)


def _aligned(a: pd.Series, b: pd.Series) -> pd.DataFrame:
    frame = pd.concat([a.rename("strategy"), b.rename("benchmark")], axis=1).dropna()
    if frame.empty:
        raise ValueError("no overlapping strategy/benchmark returns")
    if not frame.index.is_monotonic_increasing:
        frame = frame.sort_index()
    return frame.astype(float)


def return_metrics(ret: pd.Series) -> dict[str, Any]:
    ret = ret.dropna().astype(float)
    if ret.empty:
        raise ValueError("empty return series")
    nav = (1.0 + ret).cumprod()
    if (nav <= 0).any():
        raise RuntimeError("nonpositive NAV in risk-free comparison")
    years = max((ret.index[-1] - ret.index[0]).days / 365.25, 1.0 / 365.25)
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0)
    std = float(ret.std(ddof=1))
    return {
        "start": str(ret.index[0].date()),
        "end": str(ret.index[-1].date()),
        "observations": int(len(ret)),
        "final_10k": float(nav.iloc[-1] * 10000.0),
        "cumulative_return": float(nav.iloc[-1] - 1.0),
        "cagr": cagr,
        "ann_vol": float(std * math.sqrt(DAYS_PER_YEAR)),
    }


def compare_to_cash(strategy: pd.Series, benchmark: pd.Series) -> dict[str, Any]:
    """Frozen CARRY-RF-0036R1 metrics. Do not change the returned values.

    ``excess_sharpe_over_rf`` here divides geometric excess CAGR by the
    annualized volatility of *excess* returns. That is the textbook denominator
    for an excess-return series and it is what R1 committed (-0.221582 for
    CARRY-PNL-0031).

    It does **not** reproduce PR #30's -0.223, contrary to what an earlier
    version of this docstring claimed. PR #30 divided by the *strategy's* own
    volatility, taken from CARRY-PNL-0031's published ``RESULT.md``; that was a
    magnitude indicator rather than a proposed convention. CARRY-RF-0036R2
    reported the strategy-volatility variant separately (-0.223151) and left R1
    untouched, so the same field name carries two denominators across the two
    committed artifacts. `docs/RISK_FREE_METRIC_CONVENTIONS.md` maps which
    number lives where.

    New code should call `excess_return_metrics`, which names each denominator.
    This function stays byte-compatible with the R1 evidence on disk.
    """

    frame = _aligned(strategy, benchmark)
    strategy_metrics = return_metrics(frame["strategy"])
    benchmark_metrics = return_metrics(frame["benchmark"])
    excess = frame["strategy"] - frame["benchmark"]
    excess_std = float(excess.std(ddof=1))
    excess_ann_vol = float(excess_std * math.sqrt(DAYS_PER_YEAR))
    excess_cagr = float(strategy_metrics["cagr"] - benchmark_metrics["cagr"])
    geometric_excess_sharpe = (
        float(excess_cagr / excess_ann_vol) if excess_ann_vol > 0 else None
    )
    arithmetic_excess_sharpe = (
        float(excess.mean() / excess_std * math.sqrt(DAYS_PER_YEAR))
        if excess_std > 0
        else None
    )
    return {
        "strategy": strategy_metrics,
        "cash_benchmark": benchmark_metrics,
        "excess_cagr_over_rf": excess_cagr,
        "excess_ann_vol": excess_ann_vol,
        "excess_sharpe_over_rf": geometric_excess_sharpe,
        "arithmetic_excess_sharpe_daily_mean_diagnostic": arithmetic_excess_sharpe,
    }


def investment_basis_rate(
    discount_rate: pd.Series | float,
    days_to_maturity: int = BILL_DAYS_TO_MATURITY,
) -> pd.Series | float:
    """Convert a bank-discount-basis bill rate to a bond-equivalent yield.

    ``BEY = 365 d / (360 - n d)`` for an ``n``-day bill quoted at discount rate
    ``d``. FRED `DTB3` is quoted on the discount basis, so accruing it directly
    understates the return on cash — about 8 bp on average over 2020-2026, and
    roughly 13 bp when the rate is near 5%.
    """
    numerator = DAYS_PER_YEAR * discount_rate
    denominator = DISCOUNT_BASIS_DAY_COUNT - days_to_maturity * discount_rate
    if isinstance(discount_rate, pd.Series):
        if (denominator <= 0).any():
            raise ValueError("discount rate too large for bond-equivalent conversion")
    elif denominator <= 0:
        raise ValueError("discount rate too large for bond-equivalent conversion")
    return numerator / denominator


def load_fred_daily_risk_free_investment_basis(
    start: Any,
    end: Any,
    *,
    series_id: str = DEFAULT_SERIES_ID,
    days_to_maturity: int = BILL_DAYS_TO_MATURITY,
    timeout_seconds: int = 60,
    session: Any = requests,
) -> RiskFreeLoad:
    """Load DTB3 and accrue it on an investment basis rather than a discount basis.

    Use this for any new experiment. `load_fred_daily_risk_free` is retained
    unchanged so CARRY-RF-0036R1 stays exactly reproducible, but its discount-basis
    accrual understates cash and is only safe where that direction is conservative.
    """
    loaded = load_fred_daily_risk_free(
        start, end, series_id=series_id, timeout_seconds=timeout_seconds, session=session
    )
    daily = loaded.daily.copy()
    discount = daily["fred_rate_percent"] / 100.0
    daily["investment_basis_rate"] = investment_basis_rate(discount, days_to_maturity)
    daily["rf_daily_return"] = daily["investment_basis_rate"] / DAYS_PER_YEAR

    metadata = dict(loaded.metadata)
    metadata["quotation_basis"] = "investment (bond-equivalent)"
    metadata["days_to_maturity"] = int(days_to_maturity)
    metadata["daily_return_conversion"] = (
        f"BEY = 365 d / (360 - {days_to_maturity} d), then / 365.0"
    )
    return RiskFreeLoad(daily=daily, metadata=metadata, raw_csv=loaded.raw_csv)


def excess_return_metrics(strategy: pd.Series, benchmark: pd.Series) -> dict[str, Any]:
    """Excess-return statistics with every denominator named.

    Three ratios are reported because the repo already has two of them committed
    under one field name:

    - ``excess_information_ratio`` — arithmetic mean of daily excess returns over
      their standard deviation, annualized. **This is the statistic to quote when
      the strategy and its benchmark are highly correlated**, which is exactly the
      CARRY-STACK-0033 case.
    - ``excess_sharpe_excess_vol_denominator`` — geometric excess CAGR over excess
      volatility. Matches CARRY-RF-0036R1.
    - ``excess_sharpe_strategy_vol_denominator`` — geometric excess CAGR over the
      strategy's own volatility. Matches CARRY-RF-0036R2 and PR #30.

    ``geometric_sharpe_interpretable`` is False when excess volatility is a small
    fraction of strategy volatility. In that regime the geometric ratios divide a
    real return difference by a near-zero denominator and explode:
    CARRY-STACK-0033 returned -16.21, which is not a Sharpe ratio of anything.
    Callers should report the information ratio instead of suppressing the flag.
    """
    frame = _aligned(strategy, benchmark)
    strategy_metrics = return_metrics(frame["strategy"])
    benchmark_metrics = return_metrics(frame["benchmark"])

    excess = frame["strategy"] - frame["benchmark"]
    excess_std = float(excess.std(ddof=1))
    excess_ann_vol = float(excess_std * math.sqrt(DAYS_PER_YEAR))
    strategy_ann_vol = float(strategy_metrics["ann_vol"])
    excess_cagr = float(strategy_metrics["cagr"] - benchmark_metrics["cagr"])

    vol_ratio = (
        float(excess_ann_vol / strategy_ann_vol) if strategy_ann_vol > 0 else None
    )
    interpretable = bool(
        vol_ratio is not None and vol_ratio >= MIN_EXCESS_VOL_RATIO_FOR_GEOMETRIC_SHARPE
    )
    correlation = (
        float(frame["strategy"].corr(frame["benchmark"]))
        if len(frame) > 2
        else None
    )

    return {
        "strategy": strategy_metrics,
        "benchmark": benchmark_metrics,
        "excess_cagr_over_rf": excess_cagr,
        "excess_ann_vol": excess_ann_vol,
        "strategy_ann_vol": strategy_ann_vol,
        "excess_to_strategy_vol_ratio": vol_ratio,
        "strategy_benchmark_daily_correlation": correlation,
        "excess_information_ratio": (
            float(excess.mean() / excess_std * math.sqrt(DAYS_PER_YEAR))
            if excess_std > 0
            else None
        ),
        "excess_sharpe_excess_vol_denominator": (
            float(excess_cagr / excess_ann_vol) if excess_ann_vol > 0 else None
        ),
        "excess_sharpe_strategy_vol_denominator": (
            float(excess_cagr / strategy_ann_vol) if strategy_ann_vol > 0 else None
        ),
        "geometric_sharpe_interpretable": interpretable,
        "preferred_ratio_field": (
            "excess_sharpe_excess_vol_denominator"
            if interpretable
            else "excess_information_ratio"
        ),
    }


def annual_carry_vs_cash(strategy: pd.Series, benchmark: pd.Series) -> list[dict[str, Any]]:
    frame = _aligned(strategy, benchmark)
    rows: list[dict[str, Any]] = []
    for year, group in frame.groupby(frame.index.year):
        strategy_return = float((1.0 + group["strategy"]).prod() - 1.0)
        cash_return = float((1.0 + group["benchmark"]).prod() - 1.0)
        rows.append(
            {
                "year": int(year),
                "start": str(group.index.min().date()),
                "end": str(group.index.max().date()),
                "strategy_return": strategy_return,
                "cash_return": cash_return,
                "excess_percentage_points": float((strategy_return - cash_return) * 100.0),
            }
        )
    return rows
