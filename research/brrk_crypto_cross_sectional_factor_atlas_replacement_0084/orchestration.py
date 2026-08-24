"""Deterministic Stage4 orchestration for BRRK 0084.

This module remains history-agnostic and performs no file I/O or network access.
It validates already-staged, already-decoded records, constructs point-in-time
eligibility and robustness partitions, and applies frozen family-wise Holm
adjustment across the declared trial manifest.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from statistics import median
from typing import Iterable, Mapping, Sequence

from .engine import DECLARED_TRIALS, FACTOR_FAMILIES, HORIZONS, REPRESENTATIONS
from .execution_interface import holm_adjust


@dataclass(frozen=True)
class StagedRow:
    session: date
    symbol: str
    close: float
    volume: float
    source_object: str


@dataclass(frozen=True)
class TrialKey:
    factor: str
    family: str
    horizon: int
    representation: str


def parse_staged_rows(records: Iterable[Mapping[str, object]], authorized_objects: Iterable[str]) -> tuple[StagedRow, ...]:
    """Validate deterministic staged records without opening any payload.

    Stage8 may feed this function only records obtained under the separately
    governed read ledger. Unknown objects, malformed dates, duplicates, and
    non-finite/non-positive market fields fail closed.
    """
    authorized = set(authorized_objects)
    if not authorized:
        raise ValueError("authorized object set is empty")
    rows: list[StagedRow] = []
    seen: set[tuple[date, str, str]] = set()
    for raw in records:
        obj = str(raw["source_object"])
        if obj not in authorized:
            raise ValueError(f"unauthorized staged object: {obj}")
        session = date.fromisoformat(str(raw["session"]))
        symbol = str(raw["symbol"]).strip().upper()
        close = float(raw["close"])
        volume = float(raw["volume"])
        if not symbol:
            raise ValueError("empty symbol")
        if not isfinite(close) or close <= 0:
            raise ValueError("close must be finite and positive")
        if not isfinite(volume) or volume < 0:
            raise ValueError("volume must be finite and nonnegative")
        key = (session, symbol, obj)
        if key in seen:
            raise ValueError(f"duplicate staged row: {key}")
        seen.add(key)
        rows.append(StagedRow(session, symbol, close, volume, obj))
    return tuple(sorted(rows, key=lambda r: (r.session, r.symbol, r.source_object)))


def pit_universe_by_date(rows: Sequence[StagedRow], first_eligible: Mapping[str, date], last_eligible: Mapping[str, date | None]) -> dict[date, tuple[str, ...]]:
    """Construct the exact point-in-time symbol universe for each observed date."""
    observed: dict[date, set[str]] = {}
    for row in rows:
        start = first_eligible.get(row.symbol)
        if start is None:
            continue
        end = last_eligible.get(row.symbol)
        if row.session < start or (end is not None and row.session > end):
            continue
        observed.setdefault(row.session, set()).add(row.symbol)
    return {d: tuple(sorted(symbols)) for d, symbols in sorted(observed.items())}


def declared_trial_manifest() -> tuple[TrialKey, ...]:
    manifest = tuple(
        TrialKey(factor=factor, family=family, horizon=horizon, representation=representation)
        for family, factors in FACTOR_FAMILIES.items()
        for factor in factors
        for horizon in HORIZONS
        for representation in REPRESENTATIONS
    )
    if len(manifest) != DECLARED_TRIALS or len(set(manifest)) != DECLARED_TRIALS:
        raise ValueError("declared trial manifest drift")
    return manifest


def family_holm(raw_p_by_trial: Mapping[TrialKey, float]) -> dict[TrialKey, float]:
    """Apply Holm independently within each frozen factor family."""
    manifest = declared_trial_manifest()
    if set(raw_p_by_trial) != set(manifest):
        missing = sorted(set(manifest) - set(raw_p_by_trial), key=repr)
        extra = sorted(set(raw_p_by_trial) - set(manifest), key=repr)
        raise ValueError(f"trial p-value manifest mismatch: missing={missing!r} extra={extra!r}")
    adjusted: dict[TrialKey, float] = {}
    for family in FACTOR_FAMILIES:
        keys = [key for key in manifest if key.family == family]
        values = [float(raw_p_by_trial[key]) for key in keys]
        adj = holm_adjust(values)
        adjusted.update(zip(keys, adj))
    return adjusted


def trend_partition(market_close: Mapping[date, float], lookback_sessions: int = 60) -> dict[date, str]:
    """Label BULL/BEAR from the strictly-lagged lookback return.

    For decision date t, use only closes through t-1 and compare the latest
    admissible close with the close exactly ``lookback_sessions`` observations
    earlier. This implements the frozen Stage3 market-trend rule and never uses
    the decision-date close itself.
    """
    ordered = sorted((d, float(v)) for d, v in market_close.items())
    if lookback_sessions <= 0:
        raise ValueError("lookback must be positive")
    out: dict[date, str] = {}
    closes: list[float] = []
    for d, close in ordered:
        if not isfinite(close) or close <= 0:
            raise ValueError("market close must be finite and positive")
        if len(closes) >= lookback_sessions + 1:
            start = closes[-(lookback_sessions + 1)]
            end = closes[-1]
            out[d] = "BULL" if end / start - 1.0 >= 0.0 else "BEAR"
        closes.append(close)
    return out


def median_split_partition(values: Mapping[date, float], high_label: str, low_label: str) -> dict[date, str]:
    """Expanding, strictly-lagged median split for volatility/liquidity regimes."""
    history: list[float] = []
    out: dict[date, str] = {}
    for d, value in sorted((d, float(v)) for d, v in values.items()):
        if not isfinite(value):
            raise ValueError("partition value must be finite")
        if history:
            cutoff = float(median(history))
            out[d] = high_label if value >= cutoff else low_label
        history.append(value)
    return out


def calendar_year_partition(dates: Iterable[date]) -> dict[date, str]:
    return {d: str(d.year) for d in sorted(set(dates))}


def leave_one_group_out(groups: Mapping[str, Iterable[str]]) -> dict[str, tuple[str, ...]]:
    """Create deterministic leave-one-size-group-out symbol sets."""
    normalized = {name: set(symbols) for name, symbols in groups.items()}
    if len(normalized) != 3 or any(not symbols for symbols in normalized.values()):
        raise ValueError("exactly three nonempty size groups required")
    all_symbols = set().union(*normalized.values())
    if sum(len(v) for v in normalized.values()) != len(all_symbols):
        raise ValueError("size groups must be disjoint")
    return {name: tuple(sorted(all_symbols - symbols)) for name, symbols in sorted(normalized.items())}
