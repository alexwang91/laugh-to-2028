from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import pandas as pd

YEAR_DAYS = 365.25
YIELD_REALIZATIONS = (0.25, 0.50, 0.75, 1.00)
SWEEP_FRICTION_BPS = (0, 5, 10, 20)
PRIMARY = (0.50, 10)
CORE_YIELDS = (0.50, 0.75, 1.00)
CORE_FRICTIONS = (0, 5, 10)
MBB_BLOCK_LENGTH = 60
MBB_REPS = 4000
MBB_SEED = 630063
FROZEN_CELL_COUNT = 16


class MeasurementError(RuntimeError):
    pass


def _finite_1d(x: Sequence[float], name: str) -> np.ndarray:
    a = np.asarray(x, dtype=float)
    if a.ndim != 1 or len(a) == 0 or not np.isfinite(a).all():
        raise MeasurementError(f"{name} must be non-empty finite 1d")
    return a


def _strict_dates(values: Sequence, name: str) -> pd.DatetimeIndex:
    d = pd.DatetimeIndex(pd.to_datetime(values))
    if len(d) == 0 or not d.is_monotonic_increasing or d.has_duplicates:
        raise MeasurementError(f"{name} must be non-empty, unique, strictly increasing")
    return d


def reconstruct_returns(equity: Sequence[float], starting_capital: float = 10000.0) -> np.ndarray:
    e = _finite_1d(equity, "equity")
    if not math.isfinite(float(starting_capital)) or starting_capital <= 0 or np.any(e <= 0):
        raise MeasurementError("capital/equity must be positive finite")
    out = np.empty_like(e)
    out[0] = e[0] / float(starting_capital) - 1.0
    out[1:] = e[1:] / e[:-1] - 1.0
    if np.any(out <= -1.0) or not np.isfinite(out).all():
        raise MeasurementError("invalid reconstructed return")
    return out


def gross_from_weights(weights: np.ndarray) -> np.ndarray:
    w = np.asarray(weights, dtype=float)
    if w.ndim != 2 or w.shape[0] == 0 or w.shape[1] == 0 or not np.isfinite(w).all():
        raise MeasurementError("weights must be non-empty finite 2d")
    return np.abs(w).sum(axis=1)


def idle_cash_from_gross(gross: Sequence[float]) -> np.ndarray:
    g = _finite_1d(gross, "gross")
    return np.clip(1.0 - g, 0.0, 1.0)


def dtb3_percent_to_daily_return(dtb3_percent: Sequence[float]) -> np.ndarray:
    p = _finite_1d(dtb3_percent, "dtb3_percent")
    d = p / 100.0
    denominator = 360.0 - 91.0 * d
    if np.any(denominator <= 0.0):
        raise MeasurementError("invalid DTB3 discount denominator")
    bey = 365.0 * d / denominator
    rf = bey / 365.0
    if not np.isfinite(rf).all():
        raise MeasurementError("non-finite daily rate")
    return rf


def causal_align_rates(
    strategy_dates: Sequence,
    source_dates: Sequence,
    source_values: Sequence[float],
) -> np.ndarray:
    sdates = _strict_dates(strategy_dates, "strategy_dates")
    rdates = _strict_dates(source_dates, "source_dates")
    vals = _finite_1d(source_values, "source_values")
    if len(rdates) != len(vals):
        raise MeasurementError("source date/value length mismatch")
    source = pd.Series(vals, index=rdates)
    aligned = source.reindex(source.index.union(sdates).sort_values()).ffill().reindex(sdates)
    if aligned.isna().any():
        raise MeasurementError("missing preceding DTB3 observation")
    return aligned.to_numpy(dtype=float)


def candidate_returns(
    baseline_returns: Sequence[float],
    idle_cash: Sequence[float],
    rf_daily: Sequence[float],
    yield_realization: float,
    sweep_friction_bps: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    baseline = _finite_1d(baseline_returns, "baseline_returns")
    cash = _finite_1d(idle_cash, "idle_cash")
    rf = _finite_1d(rf_daily, "rf_daily")
    if not (len(baseline) == len(cash) == len(rf)):
        raise MeasurementError("series length mismatch")
    if yield_realization not in YIELD_REALIZATIONS or sweep_friction_bps not in SWEEP_FRICTION_BPS:
        raise MeasurementError("cell outside frozen grid")
    turnover = np.empty_like(cash)
    turnover[0] = 0.0
    turnover[1:] = np.abs(np.diff(cash))
    carry = cash * float(yield_realization) * rf
    friction = (float(sweep_friction_bps) / 10000.0) * turnover
    candidate = baseline + carry - friction
    if not np.isfinite(candidate).all() or np.any(candidate <= -1.0):
        raise MeasurementError("invalid candidate return")
    return candidate, turnover, carry, friction


def nav_from_returns(returns: Sequence[float], starting_capital: float = 10000.0) -> np.ndarray:
    r = _finite_1d(returns, "returns")
    if np.any(r <= -1.0) or not math.isfinite(float(starting_capital)) or starting_capital <= 0:
        raise MeasurementError("invalid returns/starting capital")
    return float(starting_capital) * np.cumprod(1.0 + r)


def max_drawdown(returns: Sequence[float]) -> float:
    nav = nav_from_returns(returns, 1.0)
    peak = np.maximum.accumulate(nav)
    return float(np.min(nav / peak - 1.0))


def calendar_cagr(returns: Sequence[float], dates: Sequence) -> float:
    r = _finite_1d(returns, "returns")
    d = _strict_dates(dates, "dates")
    if len(d) != len(r) or len(d) < 2:
        raise MeasurementError("date/return support mismatch")
    elapsed_days = int((d[-1] - d[0]).days)
    if elapsed_days <= 0:
        raise MeasurementError("nonpositive calendar span")
    multiple = float(np.prod(1.0 + r))
    if multiple <= 0.0:
        raise MeasurementError("nonpositive terminal multiple")
    return multiple ** (1.0 / (elapsed_days / YEAR_DAYS)) - 1.0


def relative_log_increment(candidate: Sequence[float], baseline: Sequence[float]) -> np.ndarray:
    c = _finite_1d(candidate, "candidate")
    b = _finite_1d(baseline, "baseline")
    if len(c) != len(b) or np.any(c <= -1.0) or np.any(b <= -1.0):
        raise MeasurementError("invalid paired returns")
    return np.log1p(c) - np.log1p(b)


def count_balanced_blocks(n: int, k: int = 4) -> np.ndarray:
    if k <= 0 or n < k:
        raise MeasurementError("insufficient rows for blocks")
    base, remainder = divmod(n, k)
    sizes = [base + (1 if i < remainder else 0) for i in range(k)]
    return np.repeat(np.arange(k, dtype=int), sizes)


def type7_quantile(x: Sequence[float], q: float) -> float:
    a = np.sort(_finite_1d(x, "quantile_input"))
    if not 0.0 <= q <= 1.0:
        raise MeasurementError("q outside [0,1]")
    if len(a) == 1:
        return float(a[0])
    h = (len(a) - 1) * q
    lo = int(math.floor(h))
    hi = int(math.ceil(h))
    frac = h - lo
    return float(a[lo] * (1.0 - frac) + a[hi] * frac)


def mbb_lcb(
    d: Sequence[float],
    block_length: int = MBB_BLOCK_LENGTH,
    reps: int = MBB_REPS,
    seed: int = MBB_SEED,
) -> dict:
    x = _finite_1d(d, "d")
    n = len(x)
    if block_length <= 0 or block_length > n or reps <= 0:
        raise MeasurementError("invalid bootstrap dimensions")
    starts_max = n - block_length
    blocks_needed = math.ceil(n / block_length)
    rng = np.random.default_rng(seed)
    mu_obs = float(np.mean(x))
    errors = np.empty(reps, dtype=float)
    for b in range(reps):
        starts = rng.integers(0, starts_max + 1, size=blocks_needed)
        sampled = np.concatenate([x[s : s + block_length] for s in starts])[:n]
        errors[b] = mu_obs - float(np.mean(sampled))
    q95 = type7_quantile(errors, 0.95)
    return {
        "mu_obs": mu_obs,
        "q95": q95,
        "lcb": mu_obs - q95,
        "block_length": block_length,
        "replicates": reps,
        "seed": seed,
    }


def cell_key(yield_realization: float, sweep_friction_bps: int) -> str:
    if yield_realization not in YIELD_REALIZATIONS or sweep_friction_bps not in SWEEP_FRICTION_BPS:
        raise MeasurementError("cell outside frozen grid")
    return f"a{int(round(yield_realization * 100)):03d}_f{sweep_friction_bps:02d}bps"


def evaluate(
    dates: Sequence,
    equity: Sequence[float],
    weights: np.ndarray,
    source_rate_dates: Sequence,
    source_dtb3_percent: Sequence[float],
    starting_capital: float = 10000.0,
) -> dict:
    """Evaluate the frozen 16-cell measurement after external G0/G1 identity checks.

    This module performs no file or network I/O. The controlled runner owns
    Git/hash identity and exact baseline-anchor validation.
    """
    dates_idx = _strict_dates(dates, "dates")
    baseline = reconstruct_returns(equity, starting_capital)
    gross = gross_from_weights(weights)
    if len(dates_idx) != len(baseline) or len(gross) != len(baseline):
        raise MeasurementError("common-support length mismatch")
    if np.max(gross) > 1.000001:
        raise MeasurementError("gross upper-bound failure")
    idle_cash = idle_cash_from_gross(gross)
    aligned_percent = causal_align_rates(dates_idx, source_rate_dates, source_dtb3_percent)
    rf_daily = dtb3_percent_to_daily_return(aligned_percent)

    baseline_tw = float(nav_from_returns(baseline, starting_capital)[-1])
    baseline_cagr = float(calendar_cagr(baseline, dates_idx))
    baseline_mdd = float(max_drawdown(baseline))
    block_ids = count_balanced_blocks(len(baseline), 4)

    cells: dict[str, dict] = {}
    for a in YIELD_REALIZATIONS:
        for f in SWEEP_FRICTION_BPS:
            candidate, turnover, carry, friction = candidate_returns(baseline, idle_cash, rf_daily, a, f)
            relative = relative_log_increment(candidate, baseline)
            key = cell_key(a, f)
            cells[key] = {
                "yield_realization": a,
                "sweep_friction_bps": f,
                "terminal_wealth": float(nav_from_returns(candidate, starting_capital)[-1]),
                "cagr": float(calendar_cagr(candidate, dates_idx)),
                "max_drawdown": float(max_drawdown(candidate)),
                "relative_terminal_log_growth": float(np.sum(relative)),
                "cash_sweep_turnover": float(np.sum(turnover)),
                "total_carry_return_units": float(np.sum(carry)),
                "total_sweep_friction_return_units": float(np.sum(friction)),
                "block_relative_log_growth": [float(np.sum(relative[block_ids == i])) for i in range(4)],
            }

    if len(cells) != FROZEN_CELL_COUNT:
        raise MeasurementError("frozen cell-count mismatch")

    primary_key = cell_key(*PRIMARY)
    primary = cells[primary_key]
    primary_returns, _, _, _ = candidate_returns(baseline, idle_cash, rf_daily, *PRIMARY)
    primary_relative = relative_log_increment(primary_returns, baseline)
    bootstrap = mbb_lcb(primary_relative)

    g2 = primary["terminal_wealth"] > baseline_tw and primary["cagr"] > baseline_cagr
    g3 = primary["max_drawdown"] >= baseline_mdd - 1e-12
    positive_blocks = sum(x > 0.0 for x in primary["block_relative_log_growth"])
    g4 = positive_blocks >= 3
    g5 = bootstrap["lcb"] > 0.0
    core_keys = [cell_key(a, f) for a in CORE_YIELDS for f in CORE_FRICTIONS]
    g6 = all(cells[k]["relative_terminal_log_growth"] > 0.0 for k in core_keys)

    gates = {
        "G2_PRIMARY_NET_TERMINAL_WEALTH_AND_CAGR": g2,
        "G3_PRIMARY_MAX_DRAWDOWN_NONINFERIORITY": g3,
        "G4_TEMPORAL_RECURRENCE": g4,
        "G5_DEPENDENCE_AWARE_MBB_LCB": g5,
        "G6_CORE_STRESS_ROBUSTNESS": g6,
    }
    if not g2:
        classification = "FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS"
    elif not g3:
        classification = "FAIL_IDLE_CASH_SWEEP_DRAWDOWN"
    elif not g4:
        classification = "FAIL_IDLE_CASH_SWEEP_TEMPORAL_ROBUSTNESS"
    elif not g5:
        classification = "FAIL_IDLE_CASH_SWEEP_DEPENDENCE_ROBUSTNESS"
    elif not g6:
        classification = "FAIL_IDLE_CASH_SWEEP_STRESS_ROBUSTNESS"
    else:
        classification = "PASS_IDLE_CASH_SWEEP_ROBUSTNESS"

    return {
        "candidate_cell_count": len(cells),
        "baseline": {
            "terminal_wealth": baseline_tw,
            "cagr": baseline_cagr,
            "max_drawdown": baseline_mdd,
        },
        "primary_cell_key": primary_key,
        "primary": primary,
        "positive_chronological_blocks": positive_blocks,
        "chronological_block_sizes": [int(np.sum(block_ids == i)) for i in range(4)],
        "bootstrap": bootstrap,
        "gates_after_G1": gates,
        "core_stress_cell_keys": core_keys,
        "classification_after_G1": classification,
        "cells": cells,
    }
