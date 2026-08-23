"""Synthetic-only qualification helpers for BRRK 0075 Stage4.

These helpers encode frozen Stage3 support, chronology, robustness, and
cross-sectional mechanics without reading historical payloads or performing I/O.
"""
from __future__ import annotations

from math import isfinite
from statistics import median
from typing import Mapping, Sequence

from .engine import MIN_CROSS_SECTION, MIN_RESIDUAL_COMPLETE, forward_return


def point_in_time_eligible(*, listing_age_days: int, recent_closes: Sequence[float],
                           trailing_quote_volumes: Sequence[float],
                           trailing_notional_volumes: Sequence[float],
                           latest_close_is_t_minus_1: bool) -> bool:
    """Frozen Stage3 universe gate using only information available by t-1."""
    if listing_age_days < 180 or not latest_close_is_t_minus_1:
        return False
    if len(recent_closes) != 60 or any((not isfinite(float(x)) or x <= 0) for x in recent_closes):
        return False
    if len(trailing_quote_volumes) != 30 or any((not isfinite(float(x)) or x <= 0) for x in trailing_quote_volumes):
        return False
    if len(trailing_notional_volumes) != 30 or any((not isfinite(float(x)) or x <= 0) for x in trailing_notional_volumes):
        return False
    return median(float(x) for x in trailing_quote_volumes) >= 1_000_000


def historical_membership(*, eligible_by_t_minus_1: bool, has_valid_observation: bool,
                          future_survival: bool | None = None) -> bool:
    """Future survival is deliberately ignored; delisting cannot rewrite history."""
    _ = future_survival
    return bool(eligible_by_t_minus_1 and has_valid_observation)


def matured_forward_return(closes_from_t: Sequence[float], horizon: int) -> float | None:
    """Return None for an unmatured tail; never impute missing future endpoints."""
    if horizon not in (5, 20):
        raise ValueError("horizon must be 5 or 20")
    if len(closes_from_t) <= horizon:
        return None
    return forward_return(float(closes_from_t[0]), float(closes_from_t[horizon]))


def _solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    aug = [list(map(float, a[i])) + [float(b[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("singular residualization controls")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        p = aug[col][col]
        aug[col] = [v / p for v in aug[col]]
        for row in range(n):
            if row == col:
                continue
            f = aug[row][col]
            aug[row] = [aug[row][j] - f * aug[col][j] for j in range(n + 1)]
    return [aug[i][-1] for i in range(n)]


def residualize_cross_section(y: Mapping[str, float], controls: Mapping[str, Sequence[float]]) -> dict[str, float]:
    """Date-wise OLS with intercept; requires >=30 complete symbols."""
    keys = [k for k, v in y.items() if v is not None and isfinite(float(v))]
    complete: list[str] = []
    width: int | None = None
    for k in keys:
        row = controls.get(k)
        if row is None:
            continue
        vals = [float(x) for x in row]
        if any(not isfinite(x) for x in vals):
            continue
        if width is None:
            width = len(vals)
        if len(vals) != width:
            raise ValueError("inconsistent control width")
        complete.append(k)
    if len(complete) < MIN_RESIDUAL_COMPLETE or width is None:
        raise ValueError("insufficient complete symbols for residualization")

    x = [[1.0] + [float(v) for v in controls[k]] for k in complete]
    yy = [float(y[k]) for k in complete]
    p = width + 1
    xtx = [[sum(row[i] * row[j] for row in x) for j in range(p)] for i in range(p)]
    xty = [sum(row[i] * target for row, target in zip(x, yy)) for i in range(p)]
    beta = _solve_linear_system(xtx, xty)
    return {k: yy[i] - sum(x[i][j] * beta[j] for j in range(p)) for i, k in enumerate(complete)}


def spearman_from_ranks(rank_x: Mapping[str, float], rank_y: Mapping[str, float]) -> float:
    common = sorted(set(rank_x) & set(rank_y))
    if len(common) < MIN_CROSS_SECTION:
        raise ValueError("insufficient cross section")
    xs = [float(rank_x[k]) for k in common]
    ys = [float(rank_y[k]) for k in common]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    if dx <= 0 or dy <= 0:
        raise ValueError("undefined rank correlation")
    return num / (dx * dy) ** 0.5


def sign_retained(full_sample_ic: float, partition_ics: Sequence[float]) -> bool:
    if full_sample_ic == 0 or not partition_ics:
        return False
    return all(v != 0 and (v > 0) == (full_sample_ic > 0) for v in partition_ics)


def leave_year_robust(full_sample_ic: float, omission_ics: Sequence[float]) -> bool:
    """G9: every omission keeps sign and median absolute IC retention >= 0.50."""
    if len(omission_ics) < 3 or not sign_retained(full_sample_ic, omission_ics):
        return False
    retention = [abs(v) / abs(full_sample_ic) for v in omission_ics]
    return median(retention) >= 0.50


def leave_size_bucket_robust(full_sample_ic: float, omission_ics: Sequence[float]) -> bool:
    """G10: exactly three size-bucket omissions, all retaining sign."""
    return len(omission_ics) == 3 and sign_retained(full_sample_ic, omission_ics)
