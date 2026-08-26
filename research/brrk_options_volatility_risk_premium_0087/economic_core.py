from __future__ import annotations

from math import isfinite
from typing import Any, Mapping, Sequence


class OptionsVRPEconomicError(RuntimeError):
    pass


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise OptionsVRPEconomicError(f"INVALID_{label}") from exc
    if not isfinite(out):
        raise OptionsVRPEconomicError(f"NONFINITE_{label}")
    return out


def source_native_hedge_target_units(
    *,
    call_delta: float,
    put_delta: float,
    contract_multiplier: float,
    delta_unit_scale: float,
) -> float:
    """Convert frozen source-native option deltas into underlying hedge units.

    ARM must bind the exact source-native Deribit delta fields, contract
    multiplier, and delta-unit/numeraire scale before any controlled value read.
    BUILD only validates the deterministic transformation and rejects missing,
    non-finite, or non-positive mapping parameters. No model delta fallback is
    permitted.
    """
    call = _finite(call_delta, "CALL_DELTA")
    put = _finite(put_delta, "PUT_DELTA")
    multiplier = _finite(contract_multiplier, "CONTRACT_MULTIPLIER")
    scale = _finite(delta_unit_scale, "DELTA_UNIT_SCALE")
    if multiplier <= 0 or scale <= 0:
        raise OptionsVRPEconomicError("INVALID_DELTA_MAPPING")
    target = -(call + put) * multiplier * scale
    if not isfinite(target):
        raise OptionsVRPEconomicError("NONFINITE_TARGET_UNITS")
    return target


def executable_day30_option_liability(
    *,
    call_ask: float,
    put_ask: float,
    contract_multiplier: float,
    value_unit_scale: float,
) -> float:
    """Value a still-live short straddle at day 30 using executable asks only.

    ARM must bind the exact terminal UTC timestamp, quote identities, contract
    multiplier, and common accounting numeraire before controlled exposure.
    Midpoint, mark, interpolation, later quotes, and model values are forbidden.
    """
    call = _finite(call_ask, "DAY30_CALL_ASK")
    put = _finite(put_ask, "DAY30_PUT_ASK")
    multiplier = _finite(contract_multiplier, "CONTRACT_MULTIPLIER")
    scale = _finite(value_unit_scale, "VALUE_UNIT_SCALE")
    if call <= 0 or put <= 0 or multiplier <= 0 or scale <= 0:
        raise OptionsVRPEconomicError("INVALID_DAY30_EXECUTABLE_CLOSE")
    liability = (call + put) * multiplier * scale
    if not isfinite(liability) or liability <= 0:
        raise OptionsVRPEconomicError("INVALID_DAY30_EXECUTABLE_CLOSE")
    return liability


def normalized_delta_hedged_short_straddle_pnl(
    *,
    entry_premium_value: float,
    settlement_payoff_value: float,
    hedge_path: Sequence[Mapping[str, Any]],
    friction_bps: float,
) -> float:
    """Unit-neutral frozen PnL core.

    ARM must bind one source-native settlement convention and one common frozen
    numeraire before controlled exposure. `entry_premium_value`,
    `settlement_payoff_value`, and all hedge quote values must already be in that
    same numeraire. For contracts still alive at day 30,
    `settlement_payoff_value` is the executable ask-side liability returned by
    `executable_day30_option_liability`. BUILD does not assume linear USD option
    payout for Deribit contracts.

    Each hedge row contains `spot`, executable `bid`/`ask`, and `target_units`.
    `target_units` must come from the frozen source-native delta transformation
    above. The final row is the frozen terminal hedge timestamp; residual hedge
    inventory is unwound at its executable side.
    """
    premium = _finite(entry_premium_value, "ENTRY_PREMIUM")
    payoff = _finite(settlement_payoff_value, "SETTLEMENT_PAYOFF")
    bps = _finite(friction_bps, "FRICTION_BPS")
    if premium <= 0 or payoff < 0 or bps < 0:
        raise OptionsVRPEconomicError("INVALID_ECONOMIC_INPUT")
    if not hedge_path:
        raise OptionsVRPEconomicError("EMPTY_HEDGE_PATH")

    hedge_pnl = 0.0
    previous_spot: float | None = None
    units = 0.0
    last_bid = last_ask = last_spot = 0.0

    for raw in hedge_path:
        spot = _finite(raw.get("spot"), "HEDGE_SPOT")
        bid = _finite(raw.get("bid"), "HEDGE_BID")
        ask = _finite(raw.get("ask"), "HEDGE_ASK")
        target = _finite(raw.get("target_units"), "TARGET_UNITS")
        if spot <= 0 or bid <= 0 or ask <= 0 or ask < bid:
            raise OptionsVRPEconomicError("INVALID_HEDGE_QUOTE")

        if previous_spot is not None:
            hedge_pnl += units * (spot - previous_spot)

        trade = target - units
        if trade > 0:
            hedge_pnl -= trade * (ask - spot)
        elif trade < 0:
            hedge_pnl -= (-trade) * (spot - bid)
        hedge_pnl -= abs(trade) * spot * bps / 10_000.0

        units = target
        previous_spot = spot
        last_bid, last_ask, last_spot = bid, ask, spot

    unwind = -units
    if unwind > 0:
        hedge_pnl -= unwind * (last_ask - last_spot)
    elif unwind < 0:
        hedge_pnl -= (-unwind) * (last_spot - last_bid)
    hedge_pnl -= abs(unwind) * last_spot * bps / 10_000.0

    normalized = (premium - payoff + hedge_pnl) / premium
    if not isfinite(normalized):
        raise OptionsVRPEconomicError("NONFINITE_NORMALIZED_PNL")
    return normalized


def economic_cost_panels(
    *,
    entry_premium_value: float,
    settlement_payoff_value: float,
    hedge_path: Sequence[Mapping[str, Any]],
) -> Mapping[str, float]:
    return {
        "pnl_c1": normalized_delta_hedged_short_straddle_pnl(
            entry_premium_value=entry_premium_value,
            settlement_payoff_value=settlement_payoff_value,
            hedge_path=hedge_path,
            friction_bps=5.0,
        ),
        "pnl_c2": normalized_delta_hedged_short_straddle_pnl(
            entry_premium_value=entry_premium_value,
            settlement_payoff_value=settlement_payoff_value,
            hedge_path=hedge_path,
            friction_bps=15.0,
        ),
    }
