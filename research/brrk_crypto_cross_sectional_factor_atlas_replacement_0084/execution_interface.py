"""Frozen Stage4 execution helpers for BRRK 0084.

This module is intentionally history-agnostic. It performs no file I/O, no
network access, and no controlled historical reads. It implements mechanics
that Stage5 can qualify with synthetic fixtures before any Stage8 attempt.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random
from statistics import median
from typing import Iterable, Mapping, Sequence

BLOCK_LENGTH = 20
BOOTSTRAP_REPLICATES = 4000
BOOTSTRAP_SEED = 750075
HOLM_ALPHA = 0.05
MIN_VALID_DATES = 252
MIN_MEDIAN_UNIVERSE = 30
MIN_PARTITION_DATES = 63
MAX_REPLACEMENT_FRACTION = 0.75


@dataclass(frozen=True)
class ReadLedger:
    authorized_objects: tuple[str, ...]
    read_counts: Mapping[str, int]

    def validate(self) -> bool:
        authorized = set(self.authorized_objects)
        if len(authorized) != len(self.authorized_objects):
            return False
        if set(self.read_counts) - authorized:
            return False
        return all(int(v) in (0, 1) for v in self.read_counts.values())


@dataclass(frozen=True)
class TrialEvidence:
    valid_dates: int
    median_universe: float
    mean_ic: float
    mean_spread: float
    holm_ic_p: float
    holm_spread_p: float
    declared_direction: int
    calendar_year_ics: Mapping[str, float]
    bull_ic: float | None
    bull_dates: int
    bear_ic: float | None
    bear_dates: int
    high_vol_ic: float | None
    high_vol_dates: int
    low_vol_ic: float | None
    low_vol_dates: int
    high_liquidity_ic: float | None
    high_liquidity_dates: int
    low_liquidity_ic: float | None
    low_liquidity_dates: int
    leave_year_out_ics: Mapping[str, float]
    leave_size_out_ics: Mapping[str, float]
    median_q1_count: float
    median_q5_count: float
    median_replacement_fraction: float


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def residualize_cross_section(
    target: Mapping[str, float],
    controls: Mapping[str, Sequence[float]],
) -> dict[str, float]:
    """OLS residuals with intercept, requiring >=30 complete symbols.

    Controls must have identical dimensionality for every complete row. The
    implementation uses deterministic Gaussian elimination and fails closed on
    singular designs rather than selecting or dropping controls.
    """
    keys = sorted(set(target) & set(controls))
    rows: list[tuple[str, float, list[float]]] = []
    width: int | None = None
    for key in keys:
        y = float(target[key])
        xs = [float(v) for v in controls[key]]
        if not isfinite(y) or any(not isfinite(v) for v in xs):
            continue
        if width is None:
            width = len(xs)
        if len(xs) != width:
            raise ValueError("control width drift")
        rows.append((key, y, [1.0, *xs]))
    if len(rows) < 30:
        raise ValueError("residualization requires at least 30 complete symbols")
    p = len(rows[0][2])
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    for _, y, x in rows:
        for i in range(p):
            xty[i] += x[i] * y
            for j in range(p):
                xtx[i][j] += x[i] * x[j]
    beta = _solve_linear_system(xtx, xty)
    return {key: y - sum(b * x for b, x in zip(beta, row)) for key, y, row in rows}


def _solve_linear_system(a: Sequence[Sequence[float]], b: Sequence[float]) -> list[float]:
    n = len(b)
    if len(a) != n or any(len(row) != n for row in a):
        raise ValueError("square system required")
    m = [list(map(float, row)) + [float(rhs)] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) <= 1e-12:
            raise ValueError("singular residualization design")
        m[col], m[pivot] = m[pivot], m[col]
        scale = m[col][col]
        m[col] = [v / scale for v in m[col]]
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            if factor == 0:
                continue
            m[r] = [rv - factor * cv for rv, cv in zip(m[r], m[col])]
    return [m[i][-1] for i in range(n)]


def moving_block_bootstrap_means(values: Sequence[float]) -> tuple[float, ...]:
    """Frozen MBB: L=20, 4000 reps, seed=750075, circular blocks."""
    xs = [float(v) for v in values]
    if len(xs) < BLOCK_LENGTH or any(not isfinite(v) for v in xs):
        raise ValueError("bootstrap requires at least one full finite block")
    rng = Random(BOOTSTRAP_SEED)
    n = len(xs)
    blocks_needed = (n + BLOCK_LENGTH - 1) // BLOCK_LENGTH
    out: list[float] = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample: list[float] = []
        for _ in range(blocks_needed):
            start = rng.randrange(n)
            sample.extend(xs[(start + k) % n] for k in range(BLOCK_LENGTH))
        sample = sample[:n]
        out.append(sum(sample) / n)
    return tuple(out)


def two_sided_bootstrap_p(values: Sequence[float]) -> float:
    """Two-sided centered-null bootstrap p-value for the sample mean."""
    xs = [float(v) for v in values]
    if not xs:
        raise ValueError("empty bootstrap input")
    observed = sum(xs) / len(xs)
    centered = [v - observed for v in xs]
    null_means = moving_block_bootstrap_means(centered)
    extreme = sum(abs(v) >= abs(observed) for v in null_means)
    return (extreme + 1.0) / (BOOTSTRAP_REPLICATES + 1.0)


def holm_adjust(raw_p: Sequence[float]) -> list[float]:
    m = len(raw_p)
    indexed = sorted(enumerate(float(p) for p in raw_p), key=lambda item: item[1])
    adjusted = [1.0] * m
    running = 0.0
    for rank, (idx, p) in enumerate(indexed):
        if not 0.0 <= p <= 1.0:
            raise ValueError("p outside [0,1]")
        running = max(running, min(1.0, (m - rank) * p))
        adjusted[idx] = running
    return adjusted


def replacement_fraction(previous: Iterable[str], current: Iterable[str]) -> float:
    a, b = set(previous), set(current)
    if not a and not b:
        return 0.0
    return 1.0 - len(a & b) / max(len(a), len(b))


def median_replacement_fraction(constituents_by_date: Sequence[Iterable[str]]) -> float:
    if len(constituents_by_date) < 2:
        raise ValueError("at least two rebalance dates required")
    vals = [
        replacement_fraction(constituents_by_date[i - 1], constituents_by_date[i])
        for i in range(1, len(constituents_by_date))
    ]
    return float(median(vals))


def _supported_partition_retains_sign(value: float | None, dates: int, full_sign: int) -> bool:
    if dates < MIN_PARTITION_DATES:
        return True
    if value is None or not isfinite(float(value)):
        return False
    return _sign(float(value)) == full_sign


def evaluate_gates(e: TrialEvidence, execution_valid: bool) -> dict[str, bool]:
    full_sign = _sign(e.mean_ic)
    spread_sign = _sign(e.mean_spread)
    supported_years = [float(v) for v in e.calendar_year_ics.values() if isfinite(float(v))]
    same_year_sign = sum(_sign(v) == full_sign for v in supported_years)

    g0 = bool(execution_valid)
    g1 = e.valid_dates >= MIN_VALID_DATES and e.median_universe >= MIN_MEDIAN_UNIVERSE
    g2 = 0.0 <= e.holm_ic_p <= HOLM_ALPHA
    g3 = 0.0 <= e.holm_spread_p <= HOLM_ALPHA
    g4 = full_sign != 0 and full_sign == spread_sign == int(e.declared_direction)
    g5 = bool(supported_years) and same_year_sign / len(supported_years) >= 0.60
    g6 = _supported_partition_retains_sign(e.bull_ic, e.bull_dates, full_sign) and _supported_partition_retains_sign(e.bear_ic, e.bear_dates, full_sign)
    g7 = _supported_partition_retains_sign(e.high_vol_ic, e.high_vol_dates, full_sign) and _supported_partition_retains_sign(e.low_vol_ic, e.low_vol_dates, full_sign)
    g8 = _supported_partition_retains_sign(e.high_liquidity_ic, e.high_liquidity_dates, full_sign) and _supported_partition_retains_sign(e.low_liquidity_ic, e.low_liquidity_dates, full_sign)

    lyo = [float(v) for v in e.leave_year_out_ics.values() if isfinite(float(v))]
    if len(supported_years) >= 3 and lyo:
        retains = all(_sign(v) == full_sign for v in lyo)
        retention = median(abs(v) / abs(e.mean_ic) for v in lyo) if e.mean_ic != 0 else 0.0
        g9 = retains and retention >= 0.50
    else:
        g9 = False

    size_vals = [float(v) for v in e.leave_size_out_ics.values() if isfinite(float(v))]
    g10 = len(size_vals) == 3 and all(_sign(v) == full_sign for v in size_vals)
    g11 = (
        e.median_q1_count >= 4
        and e.median_q5_count >= 4
        and e.median_replacement_fraction <= MAX_REPLACEMENT_FRACTION
    )
    return {f"G{i}": v for i, v in enumerate((g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11))}


def trial_qualifies(e: TrialEvidence, execution_valid: bool) -> bool:
    return all(evaluate_gates(e, execution_valid).values())


def create_only_guard(existing_paths: Iterable[str], required_new_paths: Iterable[str]) -> None:
    existing = set(existing_paths)
    new = list(required_new_paths)
    if len(new) != len(set(new)):
        raise ValueError("duplicate create-only output path")
    collision = existing.intersection(new)
    if collision:
        raise FileExistsError(f"create-only persistence collision: {sorted(collision)}")
