from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import stdev
from typing import Iterable, Sequence

ASSET_CAP = 1.0 / 3.0
GROSS_CAP = 1.0
VOL_TARGET = 0.20
VOL_FLOOR = 0.05
ANN = math.sqrt(365.0)


def sign(x: float) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0


def equal_vote(votes: Iterable[int]) -> int:
    return sign(sum(votes))


def past_return_vote(closes: Sequence[float], lookback: int) -> int:
    if len(closes) <= lookback or closes[-1] <= 0 or closes[-1 - lookback] <= 0:
        return 0
    return sign(math.log(closes[-1] / closes[-1 - lookback]))


def sma_vote(closes: Sequence[float], short: int, long: int) -> int:
    if len(closes) < long:
        return 0
    s = sum(closes[-short:]) / short
    l = sum(closes[-long:]) / long
    return sign(s - l)


def breakout_vote(closes: Sequence[float], lookback: int) -> int:
    if len(closes) <= lookback:
        return 0
    current = closes[-1]
    prior = closes[-1 - lookback:-1]
    if current > max(prior):
        return 1
    if current < min(prior):
        return -1
    return 0


def lagged_ann_vol(executable_log_returns: Sequence[float]) -> float | None:
    if len(executable_log_returns) < 20:
        return None
    window = executable_log_returns[-20:]
    return stdev(window) * ANN


def risk_scale(lagged_vol: float | None) -> float:
    if lagged_vol is None or not math.isfinite(lagged_vol):
        return 0.0
    return min(1.0, VOL_TARGET / max(lagged_vol, VOL_FLOOR))


def target_weight(signal: int, lagged_vol: float | None) -> float:
    raw = sign(signal) * risk_scale(lagged_vol) / 3.0
    return max(-ASSET_CAP, min(ASSET_CAP, raw))


def cap_portfolio(weights: Sequence[float]) -> tuple[float, ...]:
    gross = sum(abs(w) for w in weights)
    if gross <= GROSS_CAP or gross == 0:
        return tuple(weights)
    scale = GROSS_CAP / gross
    return tuple(w * scale for w in weights)


def turnover(previous: Sequence[float], current: Sequence[float]) -> float:
    if len(previous) != len(current):
        raise ValueError("weight vectors must have equal length")
    return sum(abs(a - b) for a, b in zip(current, previous))


def turnover_cost(turnover_value: float, bps_one_way: float) -> float:
    if turnover_value < 0 or bps_one_way < 0:
        raise ValueError("turnover and bps must be nonnegative")
    return turnover_value * bps_one_way / 10_000.0


def funding_contribution(position_notional: float, funding_rate: float) -> float:
    return -position_notional * funding_rate


@dataclass(frozen=True)
class CandidateSignals:
    past_return: int
    moving_average: int
    breakout: int


def candidate_signals(closes: Sequence[float]) -> CandidateSignals:
    past = equal_vote(past_return_vote(closes, L) for L in (20, 60, 180))
    ma = equal_vote(sma_vote(closes, s, l) for s, l in ((10, 40), (20, 80), (60, 240)))
    brk = equal_vote(breakout_vote(closes, L) for L in (20, 60, 180))
    return CandidateSignals(past, ma, brk)


def executable_interval_weight(signal_at_close_t: int, returns_through_t: Sequence[float]) -> float:
    """Weight decided at close t for the t->t+1 interval; never uses t+1 return."""
    return target_weight(signal_at_close_t, lagged_ann_vol(returns_through_t))
