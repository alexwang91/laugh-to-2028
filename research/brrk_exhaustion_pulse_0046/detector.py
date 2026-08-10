from __future__ import annotations

"""Pure frozen detector mathematics for BRRK-EXHAUSTION-PULSE-0046.

This module has no market-data loader, event taxonomy, portfolio translation,
signer, order-submission path, or production authority.
"""

import math
from dataclasses import dataclass

import numpy as np

BASELINE_LENGTH = 64
MIN_CHANGE_AGE = 3
MAX_CHANGE_AGE = 32
AXIS_COUNT = 4
VAR_FLOOR = 1e-8
SUBSET_COUNT = 15

_Q = np.arange(1.0, BASELINE_LENGTH + 1.0, dtype=np.float64)
_Q_BAR = float(_Q.mean())
_Q_SXX = float(np.square(_Q - _Q_BAR).sum())
_LOG_SUBSET_COUNT = math.log(float(SUBSET_COUNT))


class DetectorInvalid(ValueError):
    pass


@dataclass(frozen=True)
class DetectorOutput:
    score: np.ndarray
    selected_age: np.ndarray
    selected_axis_contributions: np.ndarray


def _as_batch(values: np.ndarray) -> tuple[np.ndarray, bool]:
    x = np.asarray(values, dtype=np.float64)
    squeeze = False
    if x.ndim == 2:
        x = x[None, ...]
        squeeze = True
    if x.ndim != 3 or x.shape[2] != AXIS_COUNT:
        raise DetectorInvalid(f"expected (T,4) or (B,T,4), got {x.shape}")
    if x.shape[1] < BASELINE_LENGTH + MIN_CHANGE_AGE:
        raise DetectorInvalid("path too short for frozen 64-session baseline plus age-3 scan")
    if not np.isfinite(x).all():
        raise DetectorInvalid("detector input must be finite; trim only the initial predictor warm-up before calling")
    return x, squeeze


def _prefix_moments(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    batch, sessions, axes = values.shape
    zeros = np.zeros((batch, 1, axes), dtype=np.float64)
    i = np.arange(sessions, dtype=np.float64)
    prefix_x = np.concatenate([zeros, np.cumsum(values, axis=1)], axis=1)
    prefix_x2 = np.concatenate([zeros, np.cumsum(np.square(values), axis=1)], axis=1)
    prefix_ix = np.concatenate([zeros, np.cumsum(values * i[None, :, None], axis=1)], axis=1)
    return prefix_x, prefix_x2, prefix_ix


def _rolling_ols_from_prefix(
    prefix_x: np.ndarray,
    prefix_x2: np.ndarray,
    prefix_ix: np.ndarray,
    sessions: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact OLS intercept/slope/residual sigma for every 64-session window.

    The implementation uses algebraic rolling moments rather than materializing a
    batch x time x axis x 64 residual tensor. It is the same q=1..64 OLS fit.
    """
    k = np.arange(BASELINE_LENGTH - 1, sessions, dtype=np.int64)
    l = k - (BASELINE_LENGTH - 1)
    sum_y = prefix_x[:, k + 1, :] - prefix_x[:, l, :]
    sum_y2 = prefix_x2[:, k + 1, :] - prefix_x2[:, l, :]
    sum_iy = prefix_ix[:, k + 1, :] - prefix_ix[:, l, :]
    # Within each baseline q = i-l+1, so sum(q*y)=sum(i*y)+(1-l)*sum(y).
    sum_qy = sum_iy + (1.0 - l[None, :, None]) * sum_y
    ybar = sum_y / float(BASELINE_LENGTH)
    slope = (sum_qy - _Q_BAR * sum_y) / _Q_SXX
    intercept = ybar - slope * _Q_BAR
    sst = sum_y2 - float(BASELINE_LENGTH) * np.square(ybar)
    rss = np.maximum(sst - np.square(slope) * _Q_SXX, 0.0)
    variance = np.maximum(rss / float(BASELINE_LENGTH - 2), VAR_FLOOR)
    sigma = np.sqrt(variance)
    return intercept, slope, sigma


def subset_mixture_logscore(axis_ell: np.ndarray) -> np.ndarray:
    """Exact equal mixture over all 15 non-empty subsets, evaluated stably.

    sum_{A nonempty} exp(sum_{j in A} ell_j) = prod_j(1+exp(ell_j)) - 1.
    """
    ell = np.asarray(axis_ell, dtype=np.float64)
    if ell.shape[-1] != AXIS_COUNT:
        raise DetectorInvalid("axis contribution array must end in four axes")
    softplus_sum = np.logaddexp(0.0, ell).sum(axis=-1)
    log_nonempty_sum = np.empty_like(softplus_sum)
    small = softplus_sum < 50.0
    log_nonempty_sum[small] = np.log(np.expm1(softplus_sum[small]))
    s = softplus_sum[~small]
    log_nonempty_sum[~small] = s + np.log1p(-np.exp(-s))
    return log_nonempty_sum - _LOG_SUBSET_COUNT


def subset_mixture_logscore_explicit(axis_ell: np.ndarray) -> np.ndarray:
    """Reference enumeration used by contract tests, not the fast path."""
    ell = np.asarray(axis_ell, dtype=np.float64)
    pieces = []
    for mask in range(1, 1 << AXIS_COUNT):
        idx = [j for j in range(AXIS_COUNT) if mask & (1 << j)]
        pieces.append(ell[..., idx].sum(axis=-1))
    stack = np.stack(pieces, axis=-1)
    m = stack.max(axis=-1)
    return m + np.log(np.exp(stack - m[..., None]).mean(axis=-1))


def compute_detector(values: np.ndarray, *, details: bool = True) -> DetectorOutput | np.ndarray:
    """Apply the frozen detector to one path or a batch of paths.

    Ages are visited ascending and replacement occurs only on a strictly larger
    score, so an exact multiscale tie retains the smallest tau.
    """
    x, squeeze = _as_batch(values)
    batch, sessions, axes = x.shape
    prefix_x, prefix_x2, prefix_ix = _prefix_moments(x)
    intercept, slope, sigma = _rolling_ols_from_prefix(prefix_x, prefix_x2, prefix_ix, sessions)

    score = np.full((batch, sessions), np.nan, dtype=np.float64)
    if details:
        selected_age = np.full((batch, sessions), -1, dtype=np.int16)
        selected_ell = np.full((batch, sessions, axes), np.nan, dtype=np.float64)

    for tau in range(MIN_CHANGE_AGE, MAX_CHANGE_AGE + 1):
        k = np.arange(BASELINE_LENGTH - 1, sessions - tau, dtype=np.int64)
        if not len(k):
            continue
        t = k + tau
        l = k + 1
        r = k + tau
        sum_x = prefix_x[:, r + 1, :] - prefix_x[:, l, :]
        sum_ix = prefix_ix[:, r + 1, :] - prefix_ix[:, l, :]
        weighted_post = sum_ix - k[None, :, None] * sum_x

        base_idx = k - (BASELINE_LENGTH - 1)
        a = intercept[:, base_idx, :]
        b = slope[:, base_idx, :]
        sig = sigma[:, base_idx, :]

        r1 = float(tau * (tau + 1) / 2)
        r_sq = float(tau * (tau + 1) * (2 * tau + 1) / 6)
        r2 = float(BASELINE_LENGTH) * r1 + r_sq
        numerator = weighted_post - r1 * a - r2 * b
        u = numerator / (sig * math.sqrt(r_sq))
        ell = 0.5 * np.square(np.maximum(u, 0.0))
        g = subset_mixture_logscore(ell)

        current = score[:, t]
        update = np.isnan(current) | (g > current)
        score[:, t] = np.where(update, g, current)
        if details:
            selected_age[:, t] = np.where(update, tau, selected_age[:, t])
            selected_ell[:, t, :] = np.where(update[..., None], ell, selected_ell[:, t, :])

    if not details:
        return score[0] if squeeze else score
    return DetectorOutput(
        score=score[0] if squeeze else score,
        selected_age=selected_age[0] if squeeze else selected_age,
        selected_axis_contributions=selected_ell[0] if squeeze else selected_ell,
    )


def raw_alarm_and_pulse(score: np.ndarray, threshold: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = np.asarray(score, dtype=np.float64)
    if s.ndim != 1:
        raise DetectorInvalid("pulse semantics require one score path")
    if not np.isfinite(threshold):
        raise DetectorInvalid("threshold must be finite")
    eligible = np.isfinite(s)
    alarm = eligible & (s >= float(threshold))
    pulse = np.zeros(len(s), dtype=bool)
    valid_positions = np.flatnonzero(eligible)
    if len(valid_positions) > 1:
        for pos in valid_positions[1:]:
            prev = pos - 1
            if eligible[prev] and alarm[pos] and not alarm[prev]:
                pulse[pos] = True
    return eligible, alarm, pulse


def alarm_spell_lengths(alarm: np.ndarray, eligible: np.ndarray | None = None) -> list[int]:
    a = np.asarray(alarm, dtype=bool)
    e = np.ones(len(a), dtype=bool) if eligible is None else np.asarray(eligible, dtype=bool)
    if a.ndim != 1 or e.shape != a.shape:
        raise DetectorInvalid("alarm/eligible arrays must be matching one-dimensional paths")
    spells: list[int] = []
    run = 0
    for is_eligible, is_alarm in zip(e, a):
        if not is_eligible:
            if run:
                spells.append(run)
                run = 0
            continue
        if is_alarm:
            run += 1
        elif run:
            spells.append(run)
            run = 0
    if run:
        spells.append(run)
    return spells


def empirical_nearest_rank(values: list[int] | np.ndarray, q: float) -> float | None:
    arr = np.sort(np.asarray(values, dtype=np.float64))
    if not len(arr):
        return None
    if not 0.0 < q <= 1.0:
        raise DetectorInvalid("nearest-rank q must be in (0,1]")
    rank = int(math.ceil(q * len(arr)))
    return float(arr[rank - 1])
