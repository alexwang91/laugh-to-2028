from __future__ import annotations

import pytest

from beta_bot.rebalance_control import (
    REBALANCE_CONTROL_VERSION,
    RebalanceControlError,
    calculate_rebalance_control,
    load_rebalance_policy,
)
from beta_bot.target_engine import TargetCalculationResult


ASSETS = ("BTC", "ETH", "SOL", "BNB")


def _target(weights: dict[str, float], *, equity: float = 10_000.0) -> TargetCalculationResult:
    normalized = {asset: float(weights.get(asset, 0.0)) for asset in ASSETS}
    gross = sum(normalized.values())
    relative = (
        {asset: normalized[asset] / gross for asset in ASSETS}
        if gross > 0
        else {asset: 0.0 for asset in ASSETS}
    )
    return TargetCalculationResult(
        decision_timestamp="2026-08-08T00:00:00Z",
        target_session="2026-08-07",
        target_weights=normalized,
        relative_weights=relative,
        cash_share=1.0 - gross,
        base_gross_target=gross,
        risk_state="BTC_LEAD",
        risk_state_probabilities={
            "RISK_OFF": 0.1,
            "BTC_LEAD": 0.7,
            "MAJOR_ROTATION": 0.1,
            "ALT_EXPANSION": 0.1,
        },
        riskoff_probability=0.1,
        meta_scale=0.8,
        defensive_scale=0.98,
        regime_refit_session="2026-07-21",
        feature_snapshot={"fixture": True},
        account_equity_usd=equity,
        current_positions_notional_usd={asset: 0.0 for asset in ASSETS},
        data_contract_schema=2,
        data_contract_id="BRRK-DATA-CONTRACT-P3.1-R1-2026-08-06",
        data_digest="fixture-data-digest",
        approved_product_id="BRRK-PLAN-B",
        approved_config_model_version="BRRK-0011",
    )


def _notionals(weights: dict[str, float], equity: float = 10_000.0) -> dict[str, float]:
    return {asset: float(weights.get(asset, 0.0)) * equity for asset in ASSETS}


def test_registered_policy_migrates_legacy_execution_band_not_min_trade_gate():
    policy = load_rebalance_policy()
    assert policy.policy_id == REBALANCE_CONTROL_VERSION == "P3.3-L1-BAND-V1"
    assert policy.rebalance_band == 0.05
    assert policy.target_gap_metric == "L1_ABSOLUTE_WEIGHT_GAP"
    assert policy.boundary_rule == "REBALANCE_WHEN_L1_GAP_GTE_BAND"
    assert policy.minimum_trade_notional_role == (
        "DOWNSTREAM_ORDER_FEASIBILITY_ONLY_NOT_P3_3_PORTFOLIO_GATE"
    )


def test_exact_target_is_noop_but_deviation_fields_remain_explicit():
    target = _target({"BTC": 0.40, "ETH": 0.20})
    current = _notionals({"BTC": 0.40, "ETH": 0.20})
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert plan.l1_target_gap == pytest.approx(0.0)
    assert not plan.should_rebalance
    assert plan.rebalance_reason == "inside_l1_target_gap_band"
    assert plan.theoretical_gap_weights == pytest.approx({asset: 0.0 for asset in ASSETS})
    assert plan.proposed_delta_weights == pytest.approx({asset: 0.0 for asset in ASSETS})
    assert plan.control_turnover_weight == pytest.approx(0.0)
    assert plan.upstream_target_digest == target.digest()
    assert plan.upstream_target_engine_version == target.target_engine_version


def test_inside_band_suppresses_churn_without_hiding_theoretical_gap():
    target = _target({"BTC": 0.40, "ETH": 0.20})
    current = _notionals({"BTC": 0.38, "ETH": 0.20})
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert plan.l1_target_gap == pytest.approx(0.02)
    assert plan.theoretical_turnover_weight == pytest.approx(0.02)
    assert not plan.should_rebalance
    assert plan.theoretical_gap_weights["BTC"] == pytest.approx(0.02)
    assert plan.theoretical_gap_notionals_usd["BTC"] == pytest.approx(200.0)
    assert plan.suppressed_gap_weights["BTC"] == pytest.approx(0.02)
    assert plan.post_control_desired_notionals_usd == pytest.approx(current)
    assert plan.control_turnover_weight == pytest.approx(0.0)


def test_exact_band_boundary_rebalances_to_full_p3_2_target():
    target = _target({"BTC": 0.40})
    current = _notionals({"BTC": 0.35})
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert plan.l1_target_gap == pytest.approx(0.05)
    assert plan.should_rebalance
    assert plan.rebalance_reason == "outside_or_at_l1_target_gap_band"
    assert plan.post_control_desired_weights == pytest.approx(target.target_weights)
    assert plan.proposed_delta_notionals_usd["BTC"] == pytest.approx(500.0)
    assert plan.control_turnover_weight == pytest.approx(0.05)


def test_aggregate_l1_gap_triggers_even_when_each_asset_gap_is_below_band():
    target = _target({"BTC": 0.40, "ETH": 0.30, "SOL": 0.10})
    current = _notionals({"BTC": 0.38, "ETH": 0.32, "SOL": 0.09})
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert all(abs(value) < 0.05 for value in plan.theoretical_gap_weights.values())
    assert plan.l1_target_gap == pytest.approx(0.05)
    assert plan.should_rebalance
    assert plan.control_turnover_weight == pytest.approx(0.05)


def test_legacy_100_usd_min_trade_does_not_act_as_p3_3_portfolio_gate():
    equity = 1_000.0
    target = _target({"BTC": 0.10}, equity=equity)
    current = _notionals({"BTC": 0.04}, equity=equity)
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=equity,
        current_positions_notional_usd=current,
    )
    assert plan.l1_target_gap == pytest.approx(0.06)
    assert abs(plan.theoretical_gap_notionals_usd["BTC"]) == pytest.approx(60.0)
    assert plan.should_rebalance
    assert plan.proposed_delta_notionals_usd["BTC"] == pytest.approx(60.0)
    assert "DOWNSTREAM_ORDER_FEASIBILITY" in plan.minimum_trade_notional_role


def test_current_short_position_bypasses_band_to_restore_long_only_boundary():
    target = _target({"BTC": 0.02})
    current = _notionals({"BTC": -0.01})
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert plan.l1_target_gap == pytest.approx(0.03)
    assert plan.l1_target_gap < plan.rebalance_band
    assert plan.should_rebalance
    assert plan.rebalance_reason == "safety_override_to_p3_2_target"
    assert plan.safety_override_reasons == ("current_short_position",)
    assert plan.post_control_desired_weights == pytest.approx(target.target_weights)


def test_current_gross_above_one_bypasses_band_to_restore_pre_p4_boundary():
    target = _target({"BTC": 0.98})
    current = _notionals({"BTC": 1.01})
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert plan.l1_target_gap == pytest.approx(0.03)
    assert plan.l1_target_gap < plan.rebalance_band
    assert plan.current_gross_weight == pytest.approx(1.01)
    assert plan.should_rebalance
    assert plan.safety_override_reasons == ("current_gross_above_one",)
    assert plan.post_control_desired_weights == pytest.approx(target.target_weights)


def test_unknown_position_asset_fails_closed_instead_of_being_ignored():
    target = _target({"BTC": 0.40})
    with pytest.raises(RebalanceControlError, match="outside the P3.2 target universe"):
        calculate_rebalance_control(
            target=target,
            account_equity_usd=10_000.0,
            current_positions_notional_usd={"BTC": 4_000.0, "XRP": 10.0},
        )


def test_upstream_target_is_carried_unchanged_and_control_is_not_authorization():
    target = _target({"BTC": 0.25, "ETH": 0.25, "SOL": 0.10})
    current = _notionals({"BTC": 0.10, "ETH": 0.20, "SOL": 0.05})
    before = dict(target.target_weights)
    plan = calculate_rebalance_control(
        target=target,
        account_equity_usd=10_000.0,
        current_positions_notional_usd=current,
    )
    assert target.target_weights == before
    assert plan.model_target_weights == before
    assert plan.target_gross_weight == pytest.approx(target.base_gross_target)
    assert plan.production_authorized is False
    assert plan.control_version == REBALANCE_CONTROL_VERSION
