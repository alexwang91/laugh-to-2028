from __future__ import annotations

from datetime import date, timedelta
from math import log

import pytest

from research.brrk_options_volatility_risk_premium_0087.economic_core import (
    economic_cost_panels,
    normalized_delta_hedged_short_straddle_pnl,
)
from research.brrk_options_volatility_risk_premium_0087.engine import (
    BOOTSTRAP_BLOCK,
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    HAC_LAG,
    OptionsVRPExecutionError,
    analyze_weekly_observations,
    atm_ivar30,
    realized_variance_30,
    select_atm_pair,
)


def _chain():
    return [
        {"strike": 90, "kind": "C", "bid": 4.0, "ask": 4.4, "iv": 0.62},
        {"strike": 90, "kind": "P", "bid": 1.0, "ask": 1.1, "iv": 0.61},
        {"strike": 100, "kind": "C", "bid": 2.0, "ask": 2.2, "iv": 0.60},
        {"strike": 100, "kind": "P", "bid": 2.1, "ask": 2.3, "iv": 0.58},
        {"strike": 110, "kind": "C", "bid": 1.0, "ask": 1.1, "iv": 0.57},
        {"strike": 110, "kind": "P", "bid": 4.0, "ask": 4.4, "iv": 0.59},
    ]


def _rows(level: float = 0.08, c1: float = 0.03, c2: float = 0.01, weeks: int = 60):
    rows = []
    start = date(2024, 1, 1)
    for i in range(weeks):
        stamp = start + timedelta(days=7 * i)
        week = stamp.isoformat()
        year = stamp.year
        wobble = ((i % 5) - 2) * 0.001
        for underlying, offset in (("BTC", 0.002), ("ETH", -0.001)):
            rows.append(
                {
                    "underlying": underlying,
                    "week": week,
                    "year": year,
                    "vrp30": level + offset + wobble,
                    "pnl_c1": c1 + 0.5 * wobble,
                    "pnl_c2": c2 + 0.25 * wobble,
                }
            )
    return rows


def test_frozen_inference_constants():
    assert BOOTSTRAP_BLOCK == 8
    assert BOOTSTRAP_REPLICATES == 4_000
    assert BOOTSTRAP_SEED == 870087
    assert HAC_LAG == 8


def test_atm_same_strike_selection_and_ivar():
    call, put = select_atm_pair(_chain(), spot=101.0, dte=30)
    assert call["strike"] == put["strike"] == 100
    assert atm_ivar30(call, put) == pytest.approx(((0.60 + 0.58) / 2) ** 2)


def test_spread_gate_fails_closed():
    chain = [
        {"strike": 100, "kind": "C", "bid": 1.0, "ask": 2.0, "iv": 0.6},
        {"strike": 100, "kind": "P", "bid": 1.0, "ask": 2.0, "iv": 0.6},
    ]
    with pytest.raises(OptionsVRPExecutionError, match="UNSUPPORTED_ATM_PAIR"):
        select_atm_pair(chain, spot=100.0, dte=30)


def test_rv30_exact_30_returns():
    closes = [100.0 * (1.001**i) for i in range(31)]
    value = realized_variance_30(closes)
    assert value == pytest.approx(365.0 * log(1.001) ** 2)
    with pytest.raises(OptionsVRPExecutionError, match="RV30_REQUIRES_31_CLOSES"):
        realized_variance_30(closes[:-1])


def test_delta_hedged_short_straddle_pure_economic_core():
    hedge_path = [
        {"spot": 100.0, "bid": 100.0, "ask": 100.0, "target_units": 0.0},
        {"spot": 100.0, "bid": 100.0, "ask": 100.0, "target_units": 0.0},
    ]
    assert normalized_delta_hedged_short_straddle_pnl(
        entry_premium_value=20.0,
        settlement_payoff_value=0.0,
        hedge_path=hedge_path,
        friction_bps=5.0,
    ) == pytest.approx(1.0)
    panels = economic_cost_panels(
        entry_premium_value=20.0,
        settlement_payoff_value=0.0,
        hedge_path=hedge_path,
    )
    assert panels == pytest.approx({"pnl_c1": 1.0, "pnl_c2": 1.0})


def test_hedge_execution_costs_are_monotone_under_stress():
    hedge_path = [
        {"spot": 100.0, "bid": 99.9, "ask": 100.1, "target_units": 0.40},
        {"spot": 102.0, "bid": 101.9, "ask": 102.1, "target_units": 0.60},
        {"spot": 102.0, "bid": 101.9, "ask": 102.1, "target_units": 0.60},
    ]
    panels = economic_cost_panels(
        entry_premium_value=20.0,
        settlement_payoff_value=2.0,
        hedge_path=hedge_path,
    )
    assert panels["pnl_c2"] < panels["pnl_c1"]


def test_settlement_core_does_not_assume_linear_quote_payoff():
    hedge_path = [{"spot": 100.0, "bid": 100.0, "ask": 100.0, "target_units": 0.0}]
    low_payoff = normalized_delta_hedged_short_straddle_pnl(
        entry_premium_value=2.0,
        settlement_payoff_value=0.25,
        hedge_path=hedge_path,
        friction_bps=5.0,
    )
    high_payoff = normalized_delta_hedged_short_straddle_pnl(
        entry_premium_value=2.0,
        settlement_payoff_value=1.25,
        hedge_path=hedge_path,
        friction_bps=5.0,
    )
    assert low_payoff > high_payoff


def test_support_counts_distinct_weeks_not_underlying_rows():
    result = analyze_weekly_observations(_rows(weeks=40))
    assert result["classification"] == "INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT"
    assert result["support"]["total_weeks"] == 40
    assert result["support"]["BTC"] == 40
    assert result["support"]["ETH"] == 40


def test_insufficient_support_is_valid_inconclusive():
    result = analyze_weekly_observations(_rows(weeks=20))
    assert result["execution_valid"] is True
    assert result["classification"] == "INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT"
    assert result["candidate_count"] == 1


def test_full_synthetic_pass_has_exact_gates():
    result = analyze_weekly_observations(_rows())
    assert result["classification"] == "PASS_OPTIONS_VRP_STRUCTURE"
    assert result["candidate_count"] == 1
    assert set(result["gates"]) == {
        "G1_MEAN_VRP_POSITIVE",
        "G2_HAC_P_LT_0_05",
        "G3_BOOTSTRAP_CI_POSITIVE",
        "G4_BTC_ETH_MEANS_POSITIVE",
        "G5_VRP_CHRONOLOGY",
        "G6_C1_MEAN_PNL_POSITIVE",
        "G7_C2_MEAN_PNL_NONNEGATIVE",
        "G8_C1_CHRONOLOGY",
    }
    assert all(result["gates"].values())


def test_adequate_support_can_fail_scientifically():
    result = analyze_weekly_observations(_rows(level=-0.02, c1=-0.01, c2=-0.02))
    assert result["classification"] == "FAIL_NO_ROBUST_OPTIONS_VRP"
    assert result["execution_valid"] is True


def test_duplicate_underlying_week_is_execution_error():
    rows = _rows()
    rows.append(dict(rows[0]))
    with pytest.raises(OptionsVRPExecutionError, match="DUPLICATE_UNDERLYING_WEEK"):
        analyze_weekly_observations(rows)
