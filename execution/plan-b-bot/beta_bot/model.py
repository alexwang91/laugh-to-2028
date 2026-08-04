from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass
from typing import Sequence


@dataclass(frozen=True)
class Signal:
    trend_score: float
    realized_vol_30: float
    raw_beta: float
    target_beta: float
    funding_apr: float
    funding_adjustment: str
    completed_candles: int

    def to_dict(self) -> dict:
        return asdict(self)


def _sample_std(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def compute_trend_score(closes: Sequence[float]) -> tuple[float, float]:
    """Return the frozen multi-horizon trend score and 30-day annualized volatility.

    The formula matches the backtested model:
    - horizons: 20, 60, 120, 240 days
    - weights: 0.15, 0.25, 0.30, 0.30
    - momentum normalized by horizon volatility
    """
    if len(closes) < 242:
        raise ValueError("At least 242 completed daily closes are required")
    if any(value <= 0 for value in closes):
        raise ValueError("All close prices must be positive")

    log_returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    horizons = (20, 60, 120, 240)
    weights = (0.15, 0.25, 0.30, 0.30)

    trend = 0.0
    last = closes[-1]
    for horizon, weight in zip(horizons, weights):
        momentum = math.log(last / closes[-1 - horizon])
        horizon_returns = log_returns[-horizon:]
        scale = _sample_std(horizon_returns) * math.sqrt(horizon)
        component = 0.0 if scale <= 0 else math.tanh(momentum / scale)
        trend += weight * component

    realized_vol_30 = _sample_std(log_returns[-30:]) * math.sqrt(365)
    return max(-1.0, min(1.0, trend)), realized_vol_30


def negative_vol_multiplier(realized_vol_30: float) -> float:
    if realized_vol_30 < 0.35:
        return 1.00
    if realized_vol_30 < 0.50:
        return 0.90
    if realized_vol_30 < 0.70:
        return 0.75
    return 0.60


def compute_raw_beta(
    trend_score: float,
    realized_vol_30: float,
    normal_cap: float = 1.30,
    hard_cap: float = 1.50,
    allow_strong_beta: bool = False,
) -> float:
    """Compute the frozen asymmetric beta curve used in the latest backtest."""
    if trend_score < 0:
        beta = (0.65 + 0.65 * trend_score) * negative_vol_multiplier(realized_vol_30)
        return max(0.18, min(0.65, beta))

    vol_scaler = 1.0 if realized_vol_30 <= 0 else min(1.0, 0.45 / realized_vol_30)
    candidate = 1.0 + 0.5 * trend_score * vol_scaler

    strong_trend = trend_score >= 0.70 and realized_vol_30 <= 0.45
    cap = hard_cap if allow_strong_beta and strong_trend else normal_cap
    return min(cap, candidate)


def apply_funding_filter(raw_beta: float, funding_apr: float) -> tuple[float, str]:
    """Reduce only leveraged long exposure when positive funding is expensive."""
    if raw_beta <= 1.0 or funding_apr <= 0.10:
        return raw_beta, "none"
    if funding_apr <= 0.15:
        return min(raw_beta, 1.30), "cap_1_30"
    if funding_apr <= 0.25:
        return 1.0 + (raw_beta - 1.0) * 0.5, "halve_extra_beta"
    return 1.0, "disable_extra_beta"


def build_signal(
    closes: Sequence[float],
    funding_apr: float,
    normal_cap: float = 1.30,
    hard_cap: float = 1.50,
    allow_strong_beta: bool = False,
) -> Signal:
    trend_score, realized_vol_30 = compute_trend_score(closes)
    raw_beta = compute_raw_beta(
        trend_score,
        realized_vol_30,
        normal_cap=normal_cap,
        hard_cap=hard_cap,
        allow_strong_beta=allow_strong_beta,
    )
    target_beta, funding_adjustment = apply_funding_filter(raw_beta, funding_apr)
    target_beta = max(0.18, min(hard_cap, target_beta))
    return Signal(
        trend_score=trend_score,
        realized_vol_30=realized_vol_30,
        raw_beta=raw_beta,
        target_beta=target_beta,
        funding_apr=funding_apr,
        funding_adjustment=funding_adjustment,
        completed_candles=len(closes),
    )
