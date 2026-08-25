from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import exp, isfinite, log, sqrt
from statistics import stdev
from typing import Any, Mapping
import json

ALLOWED_SOURCE_NAMES = {
    "btc_daily.json",
    "eth_daily.json",
    "sol_daily.json",
    "cash_daily.json",
    "canonical_brrk_daily.json",
}
ASSETS = ("BTC", "ETH", "SOL")
PRICE_FILES = {
    "BTC": "btc_daily.json",
    "ETH": "eth_daily.json",
    "SOL": "sol_daily.json",
}
HORIZONS = (20, 60, 120, 240)
VOL_WINDOW = 20
VOL_TARGET = 0.25
ANNUALIZATION = 365.0
COST_BPS = (10, 20, 30)
MIN_SUPPORT = 730
CLASSIFICATIONS = {
    "PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT",
    "FAIL_NO_ROBUST_TREND_SLEEVE_VALUE",
    "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
    "INVALID_EXECUTION",
}


class TrendExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class Series:
    dates: tuple[str, ...]
    values: tuple[float, ...]


class TrendVolTargetEngine:
    """Pure deterministic 0085 engine. The common runner owns read/once semantics."""

    def execute(self, context: Any) -> Mapping[str, Any]:
        try:
            return run_from_sources(context.sources)
        except Exception as exc:
            return {
                "classification": "INVALID_EXECUTION",
                "execution_valid": False,
                "error": f"{type(exc).__name__}:{exc}",
            }


def _json(raw: bytes, name: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise TrendExecutionError(f"INVALID_JSON:{name}") from exc


def _validate_date(text: Any) -> str:
    if not isinstance(text, str):
        raise TrendExecutionError("INVALID_DATE")
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise TrendExecutionError("INVALID_DATE") from exc
    return parsed.isoformat()


def _price_series(raw: bytes, name: str) -> Series:
    rows = _json(raw, name)
    if not isinstance(rows, list) or len(rows) < 2:
        raise TrendExecutionError(f"INVALID_PRICE_ROWS:{name}")
    dates: list[str] = []
    vals: list[float] = []
    previous: str | None = None
    for row in rows:
        if not isinstance(row, dict):
            raise TrendExecutionError(f"INVALID_PRICE_ROW:{name}")
        d = _validate_date(row.get("date"))
        try:
            v = float(row.get("close"))
        except (TypeError, ValueError) as exc:
            raise TrendExecutionError(f"INVALID_PRICE:{name}") from exc
        if not isfinite(v) or v <= 0:
            raise TrendExecutionError(f"INVALID_PRICE:{name}")
        if previous is not None and d <= previous:
            raise TrendExecutionError(f"NON_INCREASING_DATE:{name}")
        previous = d
        dates.append(d)
        vals.append(v)
    return Series(tuple(dates), tuple(vals))


def _return_series(raw: bytes, name: str) -> dict[str, float]:
    rows = _json(raw, name)
    if not isinstance(rows, list):
        raise TrendExecutionError(f"INVALID_RETURN_ROWS:{name}")
    out: dict[str, float] = {}
    previous: str | None = None
    for row in rows:
        if not isinstance(row, dict):
            raise TrendExecutionError(f"INVALID_RETURN_ROW:{name}")
        d = _validate_date(row.get("date"))
        try:
            v = float(row.get("return"))
        except (TypeError, ValueError) as exc:
            raise TrendExecutionError(f"INVALID_RETURN:{name}") from exc
        if not isfinite(v) or v <= -1:
            raise TrendExecutionError(f"INVALID_RETURN:{name}")
        if previous is not None and d <= previous:
            raise TrendExecutionError(f"NON_INCREASING_DATE:{name}")
        if d in out:
            raise TrendExecutionError(f"DUPLICATE_DATE:{name}")
        previous = d
        out[d] = v
    return out


def _sample_vol(xs: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    v = stdev(xs) * sqrt(ANNUALIZATION)
    return v if isfinite(v) and v > 0 else float("nan")


def _metric_bundle(returns: list[float]) -> dict[str, float | int]:
    n = len(returns)
    if n == 0:
        return {
            "sessions": 0,
            "cagr": 0.0,
            "annualized_volatility": 0.0,
            "sharpe": 0.0,
            "maximum_drawdown": 0.0,
            "calmar": 0.0,
            "terminal_wealth_multiple": 1.0,
        }
    wealth = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        wealth *= 1.0 + r
        peak = max(peak, wealth)
        if peak > 0:
            max_dd = min(max_dd, wealth / peak - 1.0)
    years = n / ANNUALIZATION
    cagr = wealth ** (1.0 / years) - 1.0 if wealth > 0 and years > 0 else -1.0
    vol = stdev(returns) * sqrt(ANNUALIZATION) if n >= 2 else 0.0
    mean_ann = sum(returns) / n * ANNUALIZATION
    sharpe = mean_ann / vol if vol > 0 else 0.0
    calmar = cagr / abs(max_dd) if max_dd < 0 else (float("inf") if cagr > 0 else 0.0)
    return {
        "sessions": n,
        "cagr": cagr,
        "annualized_volatility": vol,
        "sharpe": sharpe,
        "maximum_drawdown": max_dd,
        "calmar": calmar,
        "terminal_wealth_multiple": wealth,
    }


def _corr(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b) or len(a) < 2:
        return None
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    va = sum(x * x for x in da)
    vb = sum(x * x for x in db)
    if va <= 0 or vb <= 0:
        return None
    return sum(x * y for x, y in zip(da, db)) / sqrt(va * vb)


def _chronological_blocks(returns: list[float]) -> list[list[float]]:
    n = len(returns)
    bounds = [round(i * n / 4) for i in range(5)]
    return [returns[bounds[i]:bounds[i + 1]] for i in range(4)]


def _month_key(d: str) -> str:
    return d[:7]


def run_from_sources(sources: Mapping[str, bytes]) -> Mapping[str, Any]:
    names = set(sources)
    unknown = names - ALLOWED_SOURCE_NAMES
    required = set(PRICE_FILES.values())
    if unknown:
        raise TrendExecutionError(f"UNKNOWN_SOURCE:{sorted(unknown)}")
    if not required.issubset(names):
        raise TrendExecutionError(f"MISSING_REQUIRED_SOURCE:{sorted(required - names)}")

    px = {asset: _price_series(sources[fname], fname) for asset, fname in PRICE_FILES.items()}
    maps = {asset: dict(zip(series.dates, series.values)) for asset, series in px.items()}
    common_dates = sorted(set.intersection(*(set(m) for m in maps.values())))
    if len(common_dates) < 2:
        raise TrendExecutionError("NO_COMMON_PRICE_SUPPORT")

    closes = {asset: [maps[asset][d] for d in common_dates] for asset in ASSETS}
    logrets = {asset: [log(closes[asset][i] / closes[asset][i - 1]) for i in range(1, len(common_dates))] for asset in ASSETS}
    simple_rets = {asset: [closes[asset][i] / closes[asset][i - 1] - 1.0 for i in range(1, len(common_dates))] for asset in ASSETS}

    cash_map = _return_series(sources["cash_daily.json"], "cash_daily.json") if "cash_daily.json" in sources else {}
    canonical_map = _return_series(sources["canonical_brrk_daily.json"], "canonical_brrk_daily.json") if "canonical_brrk_daily.json" in sources else {}

    target_weights: list[dict[str, float]] = []
    target_dates: list[str] = []
    start_i = max(HORIZONS)
    for i in range(start_i, len(common_dates) - 1):
        active: list[str] = []
        vols: dict[str, float] = {}
        for asset in ASSETS:
            signs = []
            for h in HORIZONS:
                lr = log(closes[asset][i] / closes[asset][i - h])
                signs.append(1 if lr > 0 else 0)
            vol20 = _sample_vol(logrets[asset][i - VOL_WINDOW:i])
            if sum(signs) >= 3 and isfinite(vol20) and vol20 > 0:
                active.append(asset)
                vols[asset] = vol20
        if not active:
            weights = {asset: 0.0 for asset in ASSETS}
        else:
            raw = {asset: 1.0 / vols[asset] for asset in active}
            raw_total = sum(raw.values())
            normalized = {asset: raw[asset] / raw_total for asset in active}
            weighted_hist = []
            for j in range(i - VOL_WINDOW, i):
                weighted_hist.append(sum(normalized[a] * logrets[a][j] for a in active))
            pvol = _sample_vol(weighted_hist)
            scaler = min(1.0, VOL_TARGET / pvol) if isfinite(pvol) and pvol > 0 else 0.0
            weights = {asset: normalized.get(asset, 0.0) * scaler for asset in ASSETS}
        gross = sum(weights.values())
        if gross < -1e-12 or gross > 1.0 + 1e-12 or any(v < -1e-12 for v in weights.values()):
            raise TrendExecutionError("GROSS_OR_SHORT_VIOLATION")
        target_dates.append(common_dates[i])
        target_weights.append(weights)

    candidate_by_cost: dict[int, list[float]] = {bps: [] for bps in COST_BPS}
    benchmark_ew: list[float] = []
    benchmark_btc: list[float] = []
    candidate_dates: list[str] = []
    gross_series: list[float] = []
    turnover_series: list[float] = []
    exposure_sums = {a: 0.0 for a in ASSETS}
    previous = {a: 0.0 for a in ASSETS}

    for k, weights in enumerate(target_weights):
        i = start_i + k
        ret_date = common_dates[i + 1]
        asset_next = {a: simple_rets[a][i] for a in ASSETS}
        risky = sum(weights[a] * asset_next[a] for a in ASSETS)
        gross = sum(weights.values())
        cash_weight = max(0.0, 1.0 - gross)
        cash_ret = cash_map.get(ret_date, 0.0)
        gross_ret = risky + cash_weight * cash_ret
        turnover = sum(abs(weights[a] - previous[a]) for a in ASSETS)
        for bps in COST_BPS:
            candidate_by_cost[bps].append(gross_ret - turnover * bps / 10000.0)
        benchmark_ew.append(sum(asset_next.values()) / 3.0)
        benchmark_btc.append(asset_next["BTC"])
        candidate_dates.append(ret_date)
        gross_series.append(gross)
        turnover_series.append(turnover)
        for a in ASSETS:
            exposure_sums[a] += weights[a]
        previous = weights

    support = len(candidate_dates)
    metrics = {bps: _metric_bundle(candidate_by_cost[bps]) for bps in COST_BPS}
    ew_metrics = _metric_bundle(benchmark_ew)
    btc_metrics = _metric_bundle(benchmark_btc)

    primary = candidate_by_cost[10]
    blocks = _chronological_blocks(primary)
    block_cagrs = [float(_metric_bundle(block)["cagr"]) for block in blocks]
    positive_blocks = sum(1 for x in block_cagrs if x > 0)

    monthly_growth: dict[str, float] = {}
    for d, r in zip(candidate_dates, primary):
        monthly_growth[_month_key(d)] = monthly_growth.get(_month_key(d), 0.0) + log(1.0 + r)
    positive_growth = [x for x in monthly_growth.values() if x > 0]
    total_positive = sum(positive_growth)
    best5_share = sum(sorted(positive_growth, reverse=True)[:5]) / total_positive if total_positive > 0 else None

    canonical_common_candidate: list[float] = []
    canonical_common: list[float] = []
    for d, r in zip(candidate_dates, primary):
        if d in canonical_map:
            canonical_common_candidate.append(r)
            canonical_common.append(canonical_map[d])

    avg_gross = sum(gross_series) / support if support else 0.0
    annualized_turnover = sum(turnover_series) / support * ANNUALIZATION if support else 0.0
    cost_drag = {bps: sum(turnover_series) * bps / 10000.0 for bps in COST_BPS}
    zero_gross_pct = sum(1 for x in gross_series if abs(x) <= 1e-15) / support if support else 0.0
    asset_avg = {a: exposure_sums[a] / support if support else 0.0 for a in ASSETS}

    if support < MIN_SUPPORT:
        classification = "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
        gates = {"minimum_support": False}
    else:
        p10 = metrics[10]
        p20 = metrics[20]
        p30 = metrics[30]
        candidate_mdd = abs(float(p10["maximum_drawdown"]))
        ew_mdd = abs(float(ew_metrics["maximum_drawdown"]))
        wealth_gate = float(p10["terminal_wealth_multiple"]) >= 0.85 * float(ew_metrics["terminal_wealth_multiple"])
        dd_gate = candidate_mdd <= ew_mdd if ew_mdd < 0.20 else candidate_mdd <= ew_mdd - 0.05
        gates = {
            "minimum_support": True,
            "primary_cagr_positive": float(p10["cagr"]) > 0,
            "primary_sharpe_ge_0_80": float(p10["sharpe"]) >= 0.80,
            "primary_calmar_ge_1_00": float(p10["calmar"]) >= 1.00,
            "primary_mdd_le_35pct": candidate_mdd <= 0.35,
            "stress20_sharpe_ge_0_65": float(p20["sharpe"]) >= 0.65,
            "severe30_cagr_positive": float(p30["cagr"]) > 0,
            "positive_blocks_ge_3": positive_blocks >= 3,
            "wealth_ge_85pct_equal_weight": wealth_gate,
            "drawdown_improvement": dd_gate,
            "gross_cap_and_no_short": all(0.0 <= x <= 1.0 + 1e-12 for x in gross_series),
        }
        classification = "PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT" if all(gates.values()) else "FAIL_NO_ROBUST_TREND_SLEEVE_VALUE"

    if classification not in CLASSIFICATIONS:
        raise TrendExecutionError("BAD_CLASSIFICATION")

    return {
        "classification": classification,
        "execution_valid": True,
        "support_sessions": support,
        "cost_panels_bps": {str(b): metrics[b] for b in COST_BPS},
        "benchmarks": {
            "equal_weight_btc_eth_sol": ew_metrics,
            "btc_buy_and_hold": btc_metrics,
        },
        "primary_diagnostics": {
            "average_risky_gross_exposure": avg_gross,
            "annualized_turnover": annualized_turnover,
            "cost_drag": {str(k): v for k, v in cost_drag.items()},
            "zero_risky_gross_session_pct": zero_gross_pct,
            "asset_average_exposure": asset_avg,
            "chronological_block_cagr": block_cagrs,
            "worst_block_cagr": min(block_cagrs) if block_cagrs else None,
            "best_five_month_positive_log_growth_share": best5_share,
            "correlation_equal_weight": _corr(primary, benchmark_ew),
            "correlation_canonical_brrk": _corr(canonical_common_candidate, canonical_common),
        },
        "gates": gates,
        "cash_rule": "ARM_BOUND_CASH_DAILY" if "cash_daily.json" in sources else "ZERO_CASH_RETURN",
        "canonical_brrk_present": "canonical_brrk_daily.json" in sources,
        "frozen_parameters": {
            "assets": list(ASSETS),
            "horizons": list(HORIZONS),
            "active_threshold": "3_of_4_positive",
            "vol_window_sessions": VOL_WINDOW,
            "annualization": 365,
            "portfolio_vol_target": VOL_TARGET,
            "gross_cap": 1.0,
            "cost_bps": list(COST_BPS),
            "minimum_support": MIN_SUPPORT,
        },
    }
