from __future__ import annotations

from datetime import datetime, time, timezone
from math import isfinite
from statistics import median
from typing import Any, Mapping, Sequence

from research.brrk_cross_sectional_factor_atlas_0086.engine import _average_ranks, _factor_values
from .engine import FactorLSExecutionError

SIGNS = {"MOM60_RAW": -1.0, "RVOL20_RAW": -1.0, "LIQ30_RAW": 1.0}
MIN_HISTORY = 120
TOP_N = 30
MIN_ASSETS = 21
FWD = 5


def _indices(panel: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, dict[str, int]]:
    out = {}
    for symbol, rows in panel.items():
        out[symbol] = {str(row["date"]): i for i, row in enumerate(rows)}
    return out


def construct_target(panel: Mapping[str, list[dict[str, Any]]], day: str) -> Mapping[str, Any]:
    """Frozen PIT top-30 -> signed percentile composite -> deterministic terciles."""
    idx = _indices(panel)
    eligible = []
    for symbol, rows in panel.items():
        i = idx[symbol].get(day)
        if i is None or i < MIN_HISTORY - 1 or i + FWD >= len(rows):
            continue
        qv = [float(rows[j]["quote_volume"]) for j in range(i - 29, i + 1)]
        liq = median(qv)
        if not isfinite(liq) or liq <= 0:
            continue
        try:
            factors = _factor_values(rows, i)
        except Exception:
            continue
        if not all(isfinite(float(v)) for v in factors.values()):
            continue
        eligible.append((liq, symbol, i, factors))
    eligible.sort(key=lambda x: (-x[0], x[1]))
    selected = eligible[:TOP_N]
    if len(selected) < MIN_ASSETS:
        raise FactorLSExecutionError("INSUFFICIENT_PIT_UNIVERSE")

    symbols = [x[1] for x in selected]
    factor_ranks: dict[str, list[float]] = {}
    n = len(symbols)
    for name in SIGNS:
        values = [float(x[3][name]) for x in selected]
        ranks = _average_ranks(values)
        factor_ranks[name] = [SIGNS[name] * ((r - 1.0) / (n - 1.0) - 0.5) for r in ranks]
    composite = {
        symbol: sum(factor_ranks[name][i] for name in SIGNS) / 3.0
        for i, symbol in enumerate(symbols)
    }
    k = n // 3
    bottom = [s for s, _ in sorted(composite.items(), key=lambda x: (x[1], x[0]))[:k]]
    top = [s for s, _ in sorted(composite.items(), key=lambda x: (-x[1], x[0]))[:k]]
    target = {s: 0.0 for s in symbols}
    for s in top:
        target[s] = 1.0 / k
    for s in bottom:
        target[s] = -1.0 / k
    return {"symbols": symbols, "composite": composite, "target": target, "top": top, "bottom": bottom}


def trailing_beta(asset_rows: Sequence[Mapping[str, Any]], btc_rows: Sequence[Mapping[str, Any]], day: str) -> float:
    ai = {str(r["date"]): i for i, r in enumerate(asset_rows)}.get(day)
    bi = {str(r["date"]): i for i, r in enumerate(btc_rows)}.get(day)
    if ai is None or bi is None or ai < 60 or bi < 60:
        raise FactorLSExecutionError("INSUFFICIENT_BETA_HISTORY")
    asset_by_day = {str(r["date"]): float(r["close"]) for r in asset_rows}
    btc_slice = btc_rows[bi - 60 : bi + 1]
    dates = [str(r["date"]) for r in btc_slice]
    if any(d not in asset_by_day for d in dates):
        raise FactorLSExecutionError("MISSING_PAIRED_BETA_DATE")
    ar, br = [], []
    for j in range(1, len(dates)):
        ar.append(asset_by_day[dates[j]] / asset_by_day[dates[j - 1]] - 1.0)
        br.append(float(btc_slice[j]["close"]) / float(btc_slice[j - 1]["close"]) - 1.0)
    mb = sum(br) / len(br)
    ma = sum(ar) / len(ar)
    var = sum((x - mb) ** 2 for x in br)
    if var <= 0:
        raise FactorLSExecutionError("ZERO_BTC_BETA_VARIANCE")
    beta = sum((a - ma) * (b - mb) for a, b in zip(ar, br)) / var
    if not isfinite(beta):
        raise FactorLSExecutionError("NONFINITE_BETA")
    return beta


def funding_pnl(target: Mapping[str, float], events: Mapping[str, Sequence[Mapping[str, Any]]], decision_day: str, exit_day: str) -> float:
    """Entry-notional funding convention, strictly after decision close and <= exit close."""
    start = datetime.combine(datetime.fromisoformat(decision_day).date(), time.max, tzinfo=timezone.utc)
    end = datetime.combine(datetime.fromisoformat(exit_day).date(), time.max, tzinfo=timezone.utc)
    total = 0.0
    for symbol, weight in target.items():
        if weight == 0:
            continue
        if symbol not in events:
            raise FactorLSExecutionError(f"MISSING_FUNDING_SUPPORT:{symbol}")
        for event in events[symbol]:
            stamp = datetime.fromisoformat(str(event["timestamp"]).replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise FactorLSExecutionError("NAIVE_FUNDING_TIMESTAMP")
            rate = float(event["rate"])
            if not isfinite(rate):
                raise FactorLSExecutionError("NONFINITE_FUNDING_RATE")
            if start < stamp <= end:
                total += -weight * rate
    return total
