from __future__ import annotations

from datetime import date
from math import isfinite, log, sqrt
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


class TrendVolTargetEngine:
    """Pure deterministic 0085 engine; the common runner owns exactly-once I/O."""

    def execute(self, context: Any) -> Mapping[str, Any]:
        try:
            return run_from_sources(context.sources)
        except Exception as exc:
            return {
                "classification": "INVALID_EXECUTION",
                "execution_valid": False,
                "error": f"{type(exc).__name__}:{exc}",
            }


def _load_json(raw: bytes, name: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise TrendExecutionError(f"INVALID_JSON:{name}") from exc


def _iso_date(value: Any) -> str:
    if not isinstance(value, str):
        raise TrendExecutionError("INVALID_DATE")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise TrendExecutionError("INVALID_DATE") from exc


def _parse_prices(raw: bytes, name: str) -> dict[str, float]:
    rows = _load_json(raw, name)
    if not isinstance(rows, list) or len(rows) < 2:
        raise TrendExecutionError(f"INVALID_PRICE_ROWS:{name}")
    out: dict[str, float] = {}
    previous: str | None = None
    for row in rows:
        if not isinstance(row, dict):
            raise TrendExecutionError(f"INVALID_PRICE_ROW:{name}")
        d = _iso_date(row.get("date"))
        try:
            px = float(row.get("close"))
        except (TypeError, ValueError) as exc:
            raise TrendExecutionError(f"INVALID_PRICE:{name}") from exc
        if not isfinite(px) or px <= 0:
            raise TrendExecutionError(f"INVALID_PRICE:{name}")
        if previous is not None and d <= previous:
            raise TrendExecutionError(f"NON_INCREASING_DATE:{name}")
        previous = d
        out[d] = px
    return out


def _parse_returns(raw: bytes, name: str) -> dict[str, float]:
    rows = _load_json(raw, name)
    if not isinstance(rows, list):
        raise TrendExecutionError(f"INVALID_RETURN_ROWS:{name}")
    out: dict[str, float] = {}
    previous: str | None = None
    for row in rows:
        if not isinstance(row, dict):
            raise TrendExecutionError(f"INVALID_RETURN_ROW:{name}")
        d = _iso_date(row.get("date"))
        try:
            ret = float(row.get("return"))
        except (TypeError, ValueError) as exc:
            raise TrendExecutionError(f"INVALID_RETURN:{name}") from exc
        if not isfinite(ret) or ret <= -1:
            raise TrendExecutionError(f"INVALID_RETURN:{name}")
        if previous is not None and d <= previous:
            raise TrendExecutionError(f"NON_INCREASING_DATE:{name}")
        previous = d
        out[d] = ret
    return out


def _annualized_sample_vol(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")
    value = stdev(values) * sqrt(ANNUALIZATION)
    return value if isfinite(value) and value > 0 else float("nan")


def _metrics(returns: list[float], risk_free: list[float] | None = None) -> dict[str, float | int]:
    n = len(returns)
    if risk_free is None:
        risk_free = [0.0] * n
    if len(risk_free) != n:
        raise TrendExecutionError("RISK_FREE_SUPPORT_MISMATCH")
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
    for ret in returns:
        wealth *= 1.0 + ret
        peak = max(peak, wealth)
        max_dd = min(max_dd, wealth / peak - 1.0)

    years = n / ANNUALIZATION
    cagr = wealth ** (1.0 / years) - 1.0 if wealth > 0 and years > 0 else -1.0
    ann_vol = stdev(returns) * sqrt(ANNUALIZATION) if n >= 2 else 0.0
    excess = [ret - rf for ret, rf in zip(returns, risk_free)]
    excess_vol = stdev(excess) * sqrt(ANNUALIZATION) if n >= 2 else 0.0
    excess_mean = sum(excess) / n * ANNUALIZATION
    sharpe = excess_mean / excess_vol if excess_vol > 0 else 0.0
    calmar = cagr / abs(max_dd) if max_dd < 0 else (float("inf") if cagr > 0 else 0.0)
    return {
        "sessions": n,
        "cagr": cagr,
        "annualized_volatility": ann_vol,
        "sharpe": sharpe,
        "maximum_drawdown": max_dd,
        "calmar": calmar,
        "terminal_wealth_multiple": wealth,
    }


def _corr(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    ml = sum(left) / len(left)
    mr = sum(right) / len(right)
    dl = [x - ml for x in left]
    dr = [x - mr for x in right]
    vl = sum(x * x for x in dl)
    vr = sum(x * x for x in dr)
    if vl <= 0 or vr <= 0:
        return None
    return sum(x * y for x, y in zip(dl, dr)) / sqrt(vl * vr)


def _blocks(values: list[float]) -> list[list[float]]:
    n = len(values)
    bounds = [round(i * n / 4) for i in range(5)]
    return [values[bounds[i] : bounds[i + 1]] for i in range(4)]


def run_from_sources(sources: Mapping[str, bytes]) -> Mapping[str, Any]:
    names = set(sources)
    required = set(PRICE_FILES.values())
    unknown = names - ALLOWED_SOURCE_NAMES
    if unknown:
        raise TrendExecutionError(f"UNKNOWN_SOURCE:{sorted(unknown)}")
    if not required.issubset(names):
        raise TrendExecutionError(f"MISSING_REQUIRED_SOURCE:{sorted(required - names)}")

    price_maps = {asset: _parse_prices(sources[name], name) for asset, name in PRICE_FILES.items()}
    common_dates = sorted(set.intersection(*(set(series) for series in price_maps.values())))
    if len(common_dates) < 2:
        raise TrendExecutionError("NO_COMMON_PRICE_SUPPORT")
    closes = {asset: [price_maps[asset][d] for d in common_dates] for asset in ASSETS}
    log_returns = {
        asset: [log(closes[asset][i] / closes[asset][i - 1]) for i in range(1, len(common_dates))]
        for asset in ASSETS
    }
    simple_returns = {
        asset: [closes[asset][i] / closes[asset][i - 1] - 1.0 for i in range(1, len(common_dates))]
        for asset in ASSETS
    }

    cash_bound = "cash_daily.json" in sources
    cash_map = _parse_returns(sources["cash_daily.json"], "cash_daily.json") if cash_bound else {}
    canonical_bound = "canonical_brrk_daily.json" in sources
    canonical_map = (
        _parse_returns(sources["canonical_brrk_daily.json"], "canonical_brrk_daily.json")
        if canonical_bound
        else {}
    )

    start_i = max(HORIZONS)
    weights_by_decision: list[dict[str, float]] = []
    for i in range(start_i, len(common_dates) - 1):
        active: list[str] = []
        vols: dict[str, float] = {}
        for asset in ASSETS:
            positive = sum(1 for h in HORIZONS if log(closes[asset][i] / closes[asset][i - h]) > 0)
            vol20 = _annualized_sample_vol(log_returns[asset][i - VOL_WINDOW : i])
            if positive >= 3 and isfinite(vol20) and vol20 > 0:
                active.append(asset)
                vols[asset] = vol20

        if not active:
            weights = {asset: 0.0 for asset in ASSETS}
        else:
            inverse = {asset: 1.0 / vols[asset] for asset in active}
            total_inverse = sum(inverse.values())
            normalized = {asset: inverse[asset] / total_inverse for asset in active}
            portfolio_history = [
                sum(normalized[asset] * log_returns[asset][j] for asset in active)
                for j in range(i - VOL_WINDOW, i)
            ]
            portfolio_vol = _annualized_sample_vol(portfolio_history)
            scaler = min(1.0, VOL_TARGET / portfolio_vol) if isfinite(portfolio_vol) and portfolio_vol > 0 else 0.0
            weights = {asset: normalized.get(asset, 0.0) * scaler for asset in ASSETS}

        gross = sum(weights.values())
        if gross < -1e-12 or gross > 1.0 + 1e-12 or any(weight < -1e-12 for weight in weights.values()):
            raise TrendExecutionError("GROSS_OR_SHORT_VIOLATION")
        weights_by_decision.append(weights)

    candidate_by_cost = {bps: [] for bps in COST_BPS}
    benchmark_ew: list[float] = []
    benchmark_btc: list[float] = []
    cash_reference: list[float] = []
    candidate_dates: list[str] = []
    gross_series: list[float] = []
    turnover_series: list[float] = []
    exposure_sums = {asset: 0.0 for asset in ASSETS}
    previous = {asset: 0.0 for asset in ASSETS}

    for offset, weights in enumerate(weights_by_decision):
        i = start_i + offset
        return_date = common_dates[i + 1]
        if cash_bound and return_date not in cash_map:
            raise TrendExecutionError(f"MISSING_BOUND_CASH_RETURN:{return_date}")
        asset_next = {asset: simple_returns[asset][i] for asset in ASSETS}
        gross = sum(weights.values())
        cash_return = cash_map[return_date] if cash_bound else 0.0
        gross_return = sum(weights[asset] * asset_next[asset] for asset in ASSETS) + (1.0 - gross) * cash_return
        turnover = sum(abs(weights[asset] - previous[asset]) for asset in ASSETS)
        for bps in COST_BPS:
            candidate_by_cost[bps].append(gross_return - turnover * bps / 10000.0)
        benchmark_ew.append(sum(asset_next.values()) / 3.0)
        benchmark_btc.append(asset_next["BTC"])
        cash_reference.append(cash_return)
        candidate_dates.append(return_date)
        gross_series.append(gross)
        turnover_series.append(turnover)
        for asset in ASSETS:
            exposure_sums[asset] += weights[asset]
        previous = weights

    support = len(candidate_dates)
    metrics = {bps: _metrics(candidate_by_cost[bps], cash_reference) for bps in COST_BPS}
    ew_metrics = _metrics(benchmark_ew, cash_reference)
    btc_metrics = _metrics(benchmark_btc, cash_reference)
    primary = candidate_by_cost[10]

    block_cagrs = [float(_metrics(block)["cagr"]) for block in _blocks(primary)]
    positive_blocks = sum(value > 0 for value in block_cagrs)

    monthly_log_growth: dict[str, float] = {}
    for d, ret in zip(candidate_dates, primary):
        monthly_log_growth[d[:7]] = monthly_log_growth.get(d[:7], 0.0) + log(1.0 + ret)
    positive_months = [value for value in monthly_log_growth.values() if value > 0]
    total_positive_growth = sum(positive_months)
    best5_share = (
        sum(sorted(positive_months, reverse=True)[:5]) / total_positive_growth
        if total_positive_growth > 0
        else None
    )

    canonical_candidate: list[float] = []
    canonical_returns: list[float] = []
    for d, ret in zip(candidate_dates, primary):
        if d in canonical_map:
            canonical_candidate.append(ret)
            canonical_returns.append(canonical_map[d])
    canonical_corr = _corr(canonical_candidate, canonical_returns) if canonical_bound else None
    required_benchmark_measurement_ok = (not canonical_bound) or canonical_corr is not None

    avg_gross = sum(gross_series) / support if support else 0.0
    annualized_turnover = sum(turnover_series) / support * ANNUALIZATION if support else 0.0
    zero_gross_pct = sum(abs(value) <= 1e-15 for value in gross_series) / support if support else 0.0
    asset_avg = {asset: exposure_sums[asset] / support if support else 0.0 for asset in ASSETS}
    cost_drag = {bps: sum(turnover_series) * bps / 10000.0 for bps in COST_BPS}

    if support < MIN_SUPPORT or not required_benchmark_measurement_ok:
        classification = "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
        gates = {
            "minimum_support": support >= MIN_SUPPORT,
            "required_benchmark_measurement": required_benchmark_measurement_ok,
        }
    else:
        p10 = metrics[10]
        p20 = metrics[20]
        p30 = metrics[30]
        candidate_mdd = abs(float(p10["maximum_drawdown"]))
        ew_mdd = abs(float(ew_metrics["maximum_drawdown"]))
        gates = {
            "minimum_support": True,
            "required_benchmark_measurement": True,
            "primary_cagr_positive": float(p10["cagr"]) > 0,
            "primary_sharpe_ge_0_80": float(p10["sharpe"]) >= 0.80,
            "primary_calmar_ge_1_00": float(p10["calmar"]) >= 1.00,
            "primary_mdd_le_35pct": candidate_mdd <= 0.35,
            "stress20_sharpe_ge_0_65": float(p20["sharpe"]) >= 0.65,
            "severe30_cagr_positive": float(p30["cagr"]) > 0,
            "positive_blocks_ge_3": positive_blocks >= 3,
            "wealth_ge_85pct_equal_weight": float(p10["terminal_wealth_multiple"])
            >= 0.85 * float(ew_metrics["terminal_wealth_multiple"]),
            "drawdown_improvement": candidate_mdd <= ew_mdd if ew_mdd < 0.20 else candidate_mdd <= ew_mdd - 0.05,
            "gross_cap_and_no_short": all(0.0 <= gross <= 1.0 + 1e-12 for gross in gross_series),
        }
        classification = (
            "PASS_TREND_SLEEVE_DEVELOPMENT_SUPPORT"
            if all(gates.values())
            else "FAIL_NO_ROBUST_TREND_SLEEVE_VALUE"
        )

    if classification not in CLASSIFICATIONS:
        raise TrendExecutionError("BAD_CLASSIFICATION")

    return {
        "classification": classification,
        "execution_valid": True,
        "support_sessions": support,
        "cost_panels_bps": {str(bps): metrics[bps] for bps in COST_BPS},
        "benchmarks": {
            "equal_weight_btc_eth_sol": ew_metrics,
            "btc_buy_and_hold": btc_metrics,
        },
        "primary_diagnostics": {
            "average_risky_gross_exposure": avg_gross,
            "annualized_turnover": annualized_turnover,
            "cost_drag": {str(bps): value for bps, value in cost_drag.items()},
            "zero_risky_gross_session_pct": zero_gross_pct,
            "asset_average_exposure": asset_avg,
            "chronological_block_cagr": block_cagrs,
            "worst_block_cagr": min(block_cagrs) if block_cagrs else None,
            "best_five_month_positive_log_growth_share": best5_share,
            "correlation_equal_weight": _corr(primary, benchmark_ew),
            "correlation_canonical_brrk": canonical_corr,
        },
        "gates": gates,
        "cash_rule": "ARM_BOUND_CASH_DAILY" if cash_bound else "ZERO_CASH_RETURN",
        "canonical_brrk_present": canonical_bound,
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
