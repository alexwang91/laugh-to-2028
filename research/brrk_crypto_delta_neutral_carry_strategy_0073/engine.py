from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence
import math
import numpy as np

RID = "BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073"
ASSETS = ("BTC", "ETH", "SOL")
CANDIDATES = (
    "C1_LONG_SPOT_SHORT_PERPETUAL",
    "C2_LONG_SPOT_SHORT_DATED_FUTURE",
    "C3_CROSS_VENUE_SAME_UNDERLYING_HEDGE",
)
STRESSES = (
    "FUNDING_FLIP",
    "BASIS_COMPRESSION",
    "VOL_SPIKE",
    "SPREAD_BLOWOUT",
    "VENUE_OUTAGE",
    "COLLATERAL_HAIRCUT",
    "STABLECOIN_DEPEG",
    "MARGIN_STRESS",
)
BOOTSTRAP_BLOCK = 20
BOOTSTRAP_REPS = 4000
BOOTSTRAP_SEED = 730073
DSR_TRIALS = 3
MIN_ELIGIBLE_DAYS = 365
PBO_MIN_DAYS = 504
MAX_RESIDUAL_DELTA = 0.02
REBALANCE_TRIGGER = 0.01
MAX_NEUTRALITY_BREACH_RATE = 0.01
MAX_GROSS_EXPOSURE = 1.00
MIN_MARGIN_RESERVE = 0.20


@dataclass(frozen=True)
class CostRegime:
    spot_fee_bps: float = 6.0
    derivative_fee_bps: float = 5.0
    spot_spread_slippage_bps: float = 4.0
    derivative_spread_slippage_bps: float = 3.0
    dated_roll_extra_bps: float = 4.0
    cross_venue_monthly_bps: float = 5.0
    multiplier: float = 1.0

    def one_way_cost(self, spot_notional: float, derivative_notional: float, *, roll: bool = False, cross_venue: bool = False) -> float:
        bps = 1e-4 * self.multiplier
        cost = abs(spot_notional) * (self.spot_fee_bps + self.spot_spread_slippage_bps) * bps
        cost += abs(derivative_notional) * (self.derivative_fee_bps + self.derivative_spread_slippage_bps) * bps
        if roll:
            cost += abs(derivative_notional) * self.dated_roll_extra_bps * bps
        if cross_venue:
            cost += (abs(spot_notional) + abs(derivative_notional)) * (self.cross_venue_monthly_bps / 30.0) * bps
        return cost


C1_REALISTIC = CostRegime()
C2_STRESSED = CostRegime(multiplier=2.0)


def enforce_same_underlying(long_asset: str, short_asset: str) -> None:
    if long_asset not in ASSETS or short_asset not in ASSETS or long_asset != short_asset:
        raise ValueError("same-underlying hedge required")


def target_pair_nav(nav: float) -> tuple[float, float]:
    if not math.isfinite(nav) or nav <= 0:
        raise ValueError("nav must be positive and finite")
    return 0.50 * nav, -0.50 * nav


def residual_delta(long_delta_nav: float, short_delta_nav: float) -> float:
    return float(long_delta_nav + short_delta_nav)


def rebalance_required(residual_delta_nav: float, *, roll_due: bool = False, eligibility_changed: bool = False) -> bool:
    return abs(residual_delta_nav) > REBALANCE_TRIGGER or roll_due or eligibility_changed


def exposure_and_reserve_valid(gross_exposure_nav: float, reserve_nav: float) -> bool:
    return gross_exposure_nav <= MAX_GROSS_EXPOSURE + 1e-12 and reserve_nav >= MIN_MARGIN_RESERVE - 1e-12


def nearest_eligible_dated_future(contracts: Sequence[tuple[str, int]]) -> str | None:
    eligible = [(symbol, dte) for symbol, dte in contracts if 21 <= dte <= 120]
    if not eligible:
        return None
    return min(eligible, key=lambda x: (x[1], x[0]))[0]


def neutrality_breach_rate(residuals: Iterable[float]) -> float:
    vals = [abs(float(x)) for x in residuals]
    if not vals:
        return math.nan
    return sum(x > MAX_RESIDUAL_DELTA for x in vals) / len(vals)


def synchronized_moving_block_bootstrap(returns: Sequence[float], *, reps: int = BOOTSTRAP_REPS, block: int = BOOTSTRAP_BLOCK, seed: int = BOOTSTRAP_SEED) -> np.ndarray:
    x = np.asarray(returns, dtype=float)
    if reps != BOOTSTRAP_REPS or block != BOOTSTRAP_BLOCK or seed != BOOTSTRAP_SEED:
        raise ValueError("frozen bootstrap contract violation")
    if x.ndim != 1 or len(x) < block or not np.isfinite(x).all():
        raise ValueError("invalid return series")
    starts = np.arange(0, len(x) - block + 1)
    rng = np.random.Generator(np.random.PCG64(seed))
    out = np.empty(reps, dtype=float)
    blocks_needed = math.ceil(len(x) / block)
    for i in range(reps):
        idx = rng.choice(starts, size=blocks_needed, replace=True)
        sample = np.concatenate([x[j:j + block] for j in idx])[: len(x)]
        out[i] = sample.mean() * 365.0
    return out


def bootstrap_p05_annualized_return(returns: Sequence[float]) -> float:
    return float(np.percentile(synchronized_moving_block_bootstrap(returns), 5.0))


def candidate_pass(*, eligible_days: int, c1_cagr: float, c2_cagr: float, c1_sharpe: float, c2_sharpe: float, c1_max_drawdown: float, bootstrap_p05: float, dsr: float | None, cost_break_even_bps: float, neutrality_rate: float, exposure_ok: bool, stresses_terminal_wealth_gt_one: bool, concentration_ok: bool, capacity_ok_or_not_required: bool, identity_accounting_valid: bool = True) -> bool:
    if eligible_days < MIN_ELIGIBLE_DAYS or not identity_accounting_valid:
        return False
    dsr_ok = dsr is None or dsr >= 0.95
    return all((
        c1_cagr > 0,
        c2_cagr > 0,
        c1_sharpe > 0.50,
        c2_sharpe > 0.25,
        c1_max_drawdown > -0.35,
        bootstrap_p05 > 0,
        dsr_ok,
        cost_break_even_bps >= 20,
        neutrality_rate <= MAX_NEUTRALITY_BREACH_RATE,
        exposure_ok,
        stresses_terminal_wealth_gt_one,
        concentration_ok,
        capacity_ok_or_not_required,
    ))


def terminal_classification(*, execution_valid: bool, decision_complete: bool, any_candidate_passes: bool) -> str:
    if not execution_valid:
        return "INVALID_EXECUTION"
    if not decision_complete:
        return "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
    return "PASS" if any_candidate_passes else "FAIL"


def assert_stage4_zero_history(*, controlled_history_reads: int = 0, source_network_fetches: int = 0, scientific_engine_calls: int = 0, stage8_attempt_consumed: int = 0) -> None:
    if (controlled_history_reads, source_network_fetches, scientific_engine_calls, stage8_attempt_consumed) != (0, 0, 0, 0):
        raise RuntimeError("Stage 4 must remain zero-history and pre-attempt")
