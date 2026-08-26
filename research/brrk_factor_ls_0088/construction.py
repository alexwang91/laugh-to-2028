from __future__ import annotations

from datetime import datetime, time, timezone
from math import isfinite, log
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
    return {symbol: {str(row["date"]): i for i, row in enumerate(rows)} for symbol, rows in panel.items()}


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
    composite = {symbol: sum(factor_ranks[name][i] for name in SIGNS) / 3.0 for i, symbol in enumerate(symbols)}
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


def _decision_capacity(panel: Mapping[str, list[dict[str, Any]]], day: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for symbol, rows in panel.items():
        index = {str(row["date"]): i for i, row in enumerate(rows)}.get(day)
        if index is None or index < 29:
            continue
        values = [float(rows[j]["quote_volume"]) for j in range(index - 29, index + 1)]
        value = median(values)
        if isfinite(value) and value > 0:
            out[symbol] = value
    return out


def build_weekly_records(panel: Mapping[str, list[dict[str, Any]]], funding: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[dict[str, Any]]:
    """Bridge normalized post-marker source rows into the frozen weekly evaluator."""
    if "BTCUSDT" not in panel:
        raise FactorLSExecutionError("MISSING_BTCUSDT_PANEL")
    btc = panel["BTCUSDT"]
    btc_index = {str(row["date"]): i for i, row in enumerate(btc)}
    indices = _indices(panel)
    records: list[dict[str, Any]] = []
    for btc_i, btc_row in enumerate(btc):
        day = str(btc_row["date"])
        try:
            weekday = datetime.fromisoformat(day).weekday()
        except ValueError as exc:
            raise FactorLSExecutionError("INVALID_DECISION_DATE") from exc
        if weekday != 0 or btc_i < MIN_HISTORY - 1 or btc_i + FWD >= len(btc):
            continue
        try:
            built = construct_target(panel, day)
            target = dict(built["target"])
            exit_day = str(btc[btc_i + FWD]["date"])
            asset_returns: dict[str, float] = {}
            portfolio_beta = 0.0
            for symbol, weight in target.items():
                i = indices[symbol].get(day)
                if i is None or i + FWD >= len(panel[symbol]) or str(panel[symbol][i + FWD]["date"]) != exit_day:
                    raise FactorLSExecutionError(f"MISSING_FWD5_SUPPORT:{symbol}:{day}")
                entry = float(panel[symbol][i]["close"])
                exit_close = float(panel[symbol][i + FWD]["close"])
                ret = exit_close / entry - 1.0
                if not isfinite(ret):
                    raise FactorLSExecutionError("NONFINITE_FWD5_RETURN")
                asset_returns[symbol] = ret
                if weight != 0:
                    portfolio_beta += weight * trailing_beta(panel[symbol], btc, day)
            fpnl = funding_pnl(target, funding, day, exit_day)
            btc_state = "BTC_UP" if log(float(btc[btc_i]["close"]) / float(btc[btc_i - 60]["close"])) > 0 else "BTC_NONUP"
            records.append({
                "date": day,
                "support": True,
                "target": target,
                "asset_returns": asset_returns,
                "funding_pnl": fpnl,
                "portfolio_beta": portfolio_beta,
                "btc_state": btc_state,
                "median_quote_volume": _decision_capacity(panel, day),
            })
        except FactorLSExecutionError:
            records.append({"date": day, "support": False})
    return records
