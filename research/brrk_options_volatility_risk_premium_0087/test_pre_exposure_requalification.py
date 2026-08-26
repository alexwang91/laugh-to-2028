from __future__ import annotations

import math

import pytest

from research.brrk_options_volatility_risk_premium_0087.economic_core import (
    OptionsVRPEconomicError,
    executable_day30_option_liability,
    normalized_delta_hedged_short_straddle_pnl,
    source_native_hedge_target_units,
)


def test_source_native_delta_maps_exactly_to_hedge_target() -> None:
    target = source_native_hedge_target_units(
        call_delta=0.61,
        put_delta=-0.39,
        contract_multiplier=2.0,
        delta_unit_scale=0.5,
    )
    assert target == pytest.approx(-0.22)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"call_delta": math.nan, "put_delta": -0.4, "contract_multiplier": 1.0, "delta_unit_scale": 1.0},
        {"call_delta": 0.6, "put_delta": None, "contract_multiplier": 1.0, "delta_unit_scale": 1.0},
        {"call_delta": 0.6, "put_delta": -0.4, "contract_multiplier": 0.0, "delta_unit_scale": 1.0},
        {"call_delta": 0.6, "put_delta": -0.4, "contract_multiplier": 1.0, "delta_unit_scale": 0.0},
    ],
)
def test_source_native_delta_rejects_invalid_or_missing_inputs(kwargs: dict[str, object]) -> None:
    with pytest.raises(OptionsVRPEconomicError):
        source_native_hedge_target_units(**kwargs)  # type: ignore[arg-type]


def test_day30_close_uses_executable_asks() -> None:
    liability = executable_day30_option_liability(
        call_ask=12.0,
        put_ask=9.0,
        contract_multiplier=2.0,
        value_unit_scale=0.25,
    )
    assert liability == pytest.approx(10.5)


@pytest.mark.parametrize("call_ask,put_ask", [(0.0, 1.0), (1.0, 0.0), (math.nan, 1.0), (1.0, math.inf)])
def test_day30_close_rejects_missing_or_invalid_executable_asks(call_ask: float, put_ask: float) -> None:
    with pytest.raises(OptionsVRPEconomicError):
        executable_day30_option_liability(
            call_ask=call_ask,
            put_ask=put_ask,
            contract_multiplier=1.0,
            value_unit_scale=1.0,
        )


def test_terminal_hedge_inventory_is_unwound_at_executable_side() -> None:
    target = source_native_hedge_target_units(
        call_delta=0.70,
        put_delta=-0.20,
        contract_multiplier=1.0,
        delta_unit_scale=1.0,
    )
    pnl = normalized_delta_hedged_short_straddle_pnl(
        entry_premium_value=20.0,
        settlement_payoff_value=5.0,
        hedge_path=[
            {"spot": 100.0, "bid": 99.0, "ask": 101.0, "target_units": target},
            {"spot": 110.0, "bid": 109.0, "ask": 111.0, "target_units": target},
        ],
        friction_bps=0.0,
    )
    # Short 0.5 hedge earns -5 on the move, pays 0.5 spread on entry and
    # 0.5 spread on final buy-to-cover, then option economics contribute +15.
    assert pnl == pytest.approx((15.0 - 6.0) / 20.0)


def test_day30_liability_flows_through_same_numeraire_pnl_core() -> None:
    liability = executable_day30_option_liability(
        call_ask=4.0,
        put_ask=3.0,
        contract_multiplier=1.0,
        value_unit_scale=1.0,
    )
    pnl = normalized_delta_hedged_short_straddle_pnl(
        entry_premium_value=10.0,
        settlement_payoff_value=liability,
        hedge_path=[{"spot": 100.0, "bid": 100.0, "ask": 100.0, "target_units": 0.0}],
        friction_bps=0.0,
    )
    assert pnl == pytest.approx(0.3)
