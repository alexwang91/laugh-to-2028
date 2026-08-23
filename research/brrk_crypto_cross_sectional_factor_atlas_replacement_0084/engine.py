"""Deterministic, history-agnostic mechanics for BRRK 0084 Stage4.

This module encodes frozen Stage3 transformations only. It performs no I/O,
network access, or controlled historical payload reads.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from statistics import median
from typing import Iterable, Mapping, Sequence

MIN_CROSS_SECTION = 20
MIN_RESIDUAL_COMPLETE = 30
Q1_Q5_MIN = 4
WINSOR_LO = 0.025
WINSOR_HI = 0.975
DECLARED_TRIALS = 64
HOLM_ALPHA = 0.05
FACTOR_FAMILIES = {
    "PRICE": ("MOM_20", "MOM_60", "REV_5", "DRAWDOWN_60", "RECOVERY_20_FROM_DD", "RESID_MOM_60"),
    "RISK": ("RVOL_20", "RVOL_60", "BETA_60", "DOWNSIDE_BETA_60", "IDIOVOL_60"),
    "MARKET_STRUCTURE": ("VOLUME_SURPRISE_20", "LIQUIDITY_AMIHUD_20", "FUNDING_7D", "PERP_BASIS_1D", "PERP_MOMENTUM_GAP_20"),
}
HORIZONS = (5, 20)
REPRESENTATIONS = ("A", "B")


def _clean(xs: Iterable[float]) -> list[float]:
    return [float(x) for x in xs if x is not None and isfinite(float(x))]


def percentile(values: Sequence[float], q: float) -> float:
    xs = sorted(_clean(values))
    if not xs:
        raise ValueError("empty percentile input")
    if not 0 <= q <= 1:
        raise ValueError("q outside [0,1]")
    if len(xs) == 1:
        return xs[0]
    p = q * (len(xs) - 1)
    lo = int(p)
    hi = min(lo + 1, len(xs) - 1)
    w = p - lo
    return xs[lo] * (1 - w) + xs[hi] * w


def winsorize_cross_section(values: Mapping[str, float]) -> dict[str, float]:
    clean = {k: float(v) for k, v in values.items() if v is not None and isfinite(float(v))}
    if len(clean) < MIN_CROSS_SECTION:
        raise ValueError("insufficient cross section")
    lo = percentile(list(clean.values()), WINSOR_LO)
    hi = percentile(list(clean.values()), WINSOR_HI)
    return {k: min(max(v, lo), hi) for k, v in clean.items()}


def fractional_ranks(values: Mapping[str, float]) -> dict[str, float]:
    clean = {k: float(v) for k, v in values.items() if v is not None and isfinite(float(v))}
    if len(clean) < MIN_CROSS_SECTION:
        raise ValueError("insufficient cross section")
    ordered = sorted(clean.items(), key=lambda kv: (kv[1], kv[0]))
    n = len(ordered)
    out: dict[str, float] = {}
    i = 0
    while i < n:
        j = i + 1
        while j < n and ordered[j][1] == ordered[i][1]:
            j += 1
        frac = ((i + (j - 1)) / 2.0) / (n - 1) if n > 1 else 0.0
        for k, _ in ordered[i:j]:
            out[k] = frac
        i = j
    return out


def preprocess_rank(values: Mapping[str, float]) -> dict[str, float]:
    return fractional_ranks(winsorize_cross_section(values))


def invert_rank(rank: Mapping[str, float]) -> dict[str, float]:
    return {k: 1.0 - float(v) for k, v in rank.items()}


def quintile(rank: float) -> int:
    r = min(max(float(rank), 0.0), 1.0)
    if r < 0.2:
        return 1
    if r < 0.4:
        return 2
    if r < 0.6:
        return 3
    if r < 0.8:
        return 4
    return 5


def q1_q5_supported(ranks: Mapping[str, float]) -> bool:
    counts = {1: 0, 5: 0}
    for r in ranks.values():
        q = quintile(r)
        if q in counts:
            counts[q] += 1
    return counts[1] >= Q1_Q5_MIN and counts[5] >= Q1_Q5_MIN


def forward_return(close_t: float, close_th: float) -> float:
    if close_t <= 0 or close_th <= 0:
        raise ValueError("close must be positive")
    return close_th / close_t - 1.0


def log_return(start: float, end: float) -> float:
    from math import log
    if start <= 0 or end <= 0:
        raise ValueError("price must be positive")
    return log(end / start)


def drawdown_60(closes: Sequence[float]) -> float:
    if len(closes) != 60 or any(x <= 0 for x in closes):
        raise ValueError("drawdown_60 requires 60 positive closes")
    return closes[-1] / max(closes) - 1.0


def recovery_20_from_dd(closes_60: Sequence[float], close_20_ago: float, close_latest: float) -> float:
    dd = drawdown_60(closes_60)
    return log_return(close_20_ago, close_latest) if dd <= -0.20 else 0.0


def sample_std(values: Sequence[float]) -> float:
    xs = _clean(values)
    if len(xs) != len(values) or len(xs) < 2:
        raise ValueError("sample_std requires at least two finite values")
    mean = sum(xs) / len(xs)
    return sqrt(sum((x - mean) ** 2 for x in xs) / (len(xs) - 1))


def realized_volatility(log_returns: Sequence[float], expected_n: int) -> float:
    if len(log_returns) != expected_n:
        raise ValueError(f"expected exactly {expected_n} returns")
    return sample_std(log_returns) * sqrt(365.0)


def ols_beta(asset_returns: Sequence[float], benchmark_returns: Sequence[float], min_pairs: int) -> float:
    if len(asset_returns) != len(benchmark_returns):
        raise ValueError("paired returns must have equal length")
    pairs = [(float(a), float(b)) for a, b in zip(asset_returns, benchmark_returns)
             if isfinite(float(a)) and isfinite(float(b))]
    if len(pairs) < min_pairs:
        raise ValueError("insufficient paired rows")
    bs = [b for _, b in pairs]
    bmean = sum(bs) / len(bs)
    denom = sum((b - bmean) ** 2 for b in bs)
    if denom == 0:
        raise ValueError("benchmark variance is zero")
    amean = sum(a for a, _ in pairs) / len(pairs)
    return sum((a - amean) * (b - bmean) for a, b in pairs) / denom


def beta_60(asset_returns: Sequence[float], benchmark_returns: Sequence[float]) -> float:
    if len(asset_returns) != 60 or len(benchmark_returns) != 60:
        raise ValueError("beta_60 requires 60 observations")
    return ols_beta(asset_returns, benchmark_returns, 45)


def downside_beta_60(asset_returns: Sequence[float], benchmark_returns: Sequence[float]) -> float:
    if len(asset_returns) != 60 or len(benchmark_returns) != 60:
        raise ValueError("downside_beta_60 requires 60 observations")
    downside = [(a, b) for a, b in zip(asset_returns, benchmark_returns) if b < 0]
    if len(downside) < 15:
        raise ValueError("insufficient negative benchmark days")
    return ols_beta([a for a, _ in downside], [b for _, b in downside], 15)


def idiovol_60(asset_returns: Sequence[float], benchmark_returns: Sequence[float]) -> float:
    beta = beta_60(asset_returns, benchmark_returns)
    pairs = [(float(a), float(b)) for a, b in zip(asset_returns, benchmark_returns)
             if isfinite(float(a)) and isfinite(float(b))]
    amean = sum(a for a, _ in pairs) / len(pairs)
    bmean = sum(b for _, b in pairs) / len(pairs)
    alpha = amean - beta * bmean
    residuals = [a - (alpha + beta * b) for a, b in pairs]
    return sample_std(residuals) * sqrt(365.0)


def volume_surprise_20(latest: float, prior_19: Sequence[float]) -> float:
    from math import log
    if latest <= 0 or len(prior_19) != 19 or any(x <= 0 for x in prior_19):
        raise ValueError("positive latest plus 19 positive prior observations required")
    return log(latest / median(prior_19))


def amihud_20(returns: Sequence[float], quote_volumes: Sequence[float]) -> float:
    if len(returns) != 20 or len(quote_volumes) != 20 or any(v <= 0 for v in quote_volumes):
        raise ValueError("20 returns and positive quote volumes required")
    return median(abs(float(r)) / float(v) for r, v in zip(returns, quote_volumes))


def perp_basis_1d(perp_close: float | None, spot_close: float) -> float | None:
    if perp_close is None:
        return None
    if perp_close <= 0 or spot_close <= 0:
        raise ValueError("positive closes required")
    return perp_close / spot_close - 1.0


def funding_7d(observations: Sequence[float] | None, complete_coverage: bool) -> float | None:
    if observations is None or not complete_coverage:
        return None
    vals = _clean(observations)
    if len(vals) != len(observations):
        return None
    return sum(vals)


def perp_momentum_gap_20(perp_start: float | None, perp_end: float | None,
                         spot_start: float, spot_end: float) -> float | None:
    if perp_start is None or perp_end is None:
        return None
    return log_return(perp_start, perp_end) - log_return(spot_start, spot_end)


def spearman(values_x: Mapping[str, float], values_y: Mapping[str, float]) -> float:
    common = sorted(set(values_x) & set(values_y))
    if len(common) < 2:
        raise ValueError("insufficient common observations")
    xr = fractional_ranks({k: values_x[k] for k in common}) if len(common) >= MIN_CROSS_SECTION else _fractional_ranks_any({k: values_x[k] for k in common})
    yr = fractional_ranks({k: values_y[k] for k in common}) if len(common) >= MIN_CROSS_SECTION else _fractional_ranks_any({k: values_y[k] for k in common})
    xs = [xr[k] for k in common]
    ys = [yr[k] for k in common]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    if dx == 0 or dy == 0:
        raise ValueError("undefined Spearman correlation")
    return num / sqrt(dx * dy)


def _fractional_ranks_any(values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(((k, float(v)) for k, v in values.items()), key=lambda kv: (kv[1], kv[0]))
    n = len(ordered)
    if n < 2:
        raise ValueError("at least two observations required")
    out: dict[str, float] = {}
    i = 0
    while i < n:
        j = i + 1
        while j < n and ordered[j][1] == ordered[i][1]:
            j += 1
        frac = ((i + (j - 1)) / 2.0) / (n - 1)
        for k, _ in ordered[i:j]:
            out[k] = frac
        i = j
    return out


def q5_minus_q1(ranks: Mapping[str, float], forward_returns: Mapping[str, float]) -> float:
    common = {k: ranks[k] for k in ranks if k in forward_returns}
    if not q1_q5_supported(common):
        raise ValueError("Q1/Q5 support undefined")
    q1 = [float(forward_returns[k]) for k, r in common.items() if quintile(r) == 1]
    q5 = [float(forward_returns[k]) for k, r in common.items() if quintile(r) == 5]
    return sum(q5) / len(q5) - sum(q1) / len(q1)


def monotonicity_score(ranks: Mapping[str, float], forward_returns: Mapping[str, float]) -> float:
    buckets: dict[int, list[float]] = {i: [] for i in range(1, 6)}
    for k, r in ranks.items():
        if k in forward_returns:
            buckets[quintile(r)].append(float(forward_returns[k]))
    if any(not buckets[i] for i in buckets):
        raise ValueError("all five quintiles must be supported")
    means = {str(i): sum(buckets[i]) / len(buckets[i]) for i in range(1, 6)}
    indices = {str(i): float(i) for i in range(1, 6)}
    return spearman(indices, means)


def trial_manifest() -> tuple[tuple[str, str, int, str], ...]:
    trials: list[tuple[str, str, int, str]] = []
    for family, factors in FACTOR_FAMILIES.items():
        for factor in factors:
            for horizon in HORIZONS:
                for representation in REPRESENTATIONS:
                    trials.append((family, factor, horizon, representation))
    if len(trials) != DECLARED_TRIALS:
        raise AssertionError("declared trial accounting drift")
    return tuple(trials)


def holm_adjust(raw_p: Sequence[float]) -> list[float]:
    m = len(raw_p)
    indexed = sorted(enumerate(float(p) for p in raw_p), key=lambda x: x[1])
    out = [1.0] * m
    running = 0.0
    for rank, (idx, p) in enumerate(indexed):
        if not 0 <= p <= 1:
            raise ValueError("p outside [0,1]")
        adj = min(1.0, (m - rank) * p)
        running = max(running, adj)
        out[idx] = running
    return out


def replacement_fraction(previous: Iterable[str], current: Iterable[str]) -> float:
    a, b = set(previous), set(current)
    if not a and not b:
        return 0.0
    denom = max(len(a), len(b))
    return 1.0 - len(a & b) / denom


@dataclass(frozen=True)
class ExecutionAccounting:
    declared_trials: int
    scientific_engine_calls: int
    scientific_source_network_fetches: int
    identity_valid: bool
    lookahead_valid: bool
    persistence_valid: bool

    def execution_valid(self) -> bool:
        return (
            self.declared_trials == DECLARED_TRIALS
            and self.scientific_engine_calls in (0, 1)
            and self.scientific_source_network_fetches == 0
            and self.identity_valid
            and self.lookahead_valid
            and self.persistence_valid
        )


def terminal_classification(*, accounting: ExecutionAccounting, any_qualified: bool,
                            support_possible: bool, inference_defined: bool) -> str:
    if not accounting.execution_valid():
        return "INVALID_EXECUTION"
    if not support_possible or not inference_defined:
        return "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
    if any_qualified:
        return "PASS"
    return "FAIL_NO_QUALIFIED_FACTOR"
