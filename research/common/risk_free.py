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
    """Return F1's frozen geometric-excess metrics.

    ``excess_sharpe_over_rf`` intentionally uses geometric excess CAGR divided
    by annualized volatility of daily excess returns. This matches the independent
    PR #30 verification convention and is therefore not silently replaced by the
    arithmetic daily-mean Sharpe convention.
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
