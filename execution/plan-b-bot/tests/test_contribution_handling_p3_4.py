from __future__ import annotations

from dataclasses import replace

import pytest

import beta_bot.contribution_handling as contribution_module
from beta_bot.contribution_handling import (
    CONTRIBUTION_HANDLING_VERSION,
    ContributionHandlingError,
    apply_at_daily_decision,
    load_contribution_policy,
    observe_equity_change,
)
from beta_bot.data_contract import CanonicalDailyDataset
from beta_bot.product_config import load_product_config
from beta_bot.rebalance_control import REBALANCE_CONTROL_VERSION
from beta_bot.target_engine import TARGET_ENGINE_VERSION, TargetCalculationResult


ASSETS = ("BTC", "ETH", "SOL", "BNB")


def _dataset(decision_timestamp: str) -> CanonicalDailyDataset:
    return CanonicalDailyDataset(
        schema_version=2,
        contract_id="BRRK-DATA-CONTRACT-P3.1-R1-2026-08-06",
        decision_timestamp=decision_timestamp,
        common_start_ms=0,
        latest_session_open_ms=0,
        closes_by_asset={},
    )


def _target(*, equity: float, current_positions: dict[str, float]) -> TargetCalculationResult:
    weights = {"BTC": 0.40, "ETH": 0.20, "SOL": 0.0, "BNB": 0.0}
    gross = sum(weights.values())
    relative = {asset: weights[asset] / gross for asset in ASSETS}
    return TargetCalculationResult(
        decision_timestamp="2026-08-08T00:00:00Z",
        target_session="2026-08-07",
        target_weights=weights,
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
        current_positions_notional_usd={asset: float(current_positions.get(asset, 0.0)) for asset in ASSETS},
        data_contract_schema=2,
        data_contract_id="BRRK-DATA-CONTRACT-P3.1-R1-2026-08-06",
        data_digest="fixture-data-digest",
        approved_product_id="BRRK-PLAN-B",
        approved_config_model_version="BRRK-0011",
    )


def test_registered_p3_4_policy_freezes_daily_only_same_chain_semantics():
    policy = load_contribution_policy()
    assert policy.policy_id == CONTRIBUTION_HANDLING_VERSION
    assert policy.daily_decision_timezone == "UTC"
    assert policy.daily_decision_time == "00:00:00"
    assert policy.intraday_action == "RECORD_ONLY_NO_TARGET_RECALCULATION_NO_RISK_INCREASE"
    assert policy.daily_allocation_path == (TARGET_ENGINE_VERSION, REBALANCE_CONTROL_VERSION)
    assert policy.weekly_contribution_amount_role == (
        "PRODUCT_ASSUMPTION_ONLY_NOT_DETECTION_THRESHOLD_NOT_SCHEDULE_TRIGGER"
    )


def test_p3_4_v1_policy_cannot_silently_change_timing_or_allocation_path():
    policy = load_contribution_policy()
    with pytest.raises(ContributionHandlingError, match="policy drift"):
        replace(policy, daily_decision_time="12:00:00").validate()
    with pytest.raises(ContributionHandlingError, match="policy drift"):
        replace(policy, daily_allocation_path=(TARGET_ENGINE_VERSION,)).validate()


def test_intraday_positive_equity_change_is_record_only_until_next_utc_midnight():
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T13:45:12Z",
        observed_equity_usd=2_100.0,
    )
    assert observation.equity_change_usd == pytest.approx(100.0)
    assert observation.positive_equity_change_candidate_usd == pytest.approx(100.0)
    assert observation.contribution_candidate_pending
    assert observation.scheduled_daily_decision_timestamp == "2026-08-08T00:00:00Z"
    assert not observation.observed_at_daily_boundary
    assert not observation.requires_intraday_action
    assert not observation.intraday_target_recalculation_allowed
    assert not observation.intraday_risk_increase_allowed
    assert observation.source_attributed is False


def test_weekly_100_usd_assumption_is_not_a_detection_threshold():
    small = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T10:00:00Z",
        observed_equity_usd=2_037.0,
    )
    large = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T10:00:00Z",
        observed_equity_usd=2_250.0,
    )
    assert small.positive_equity_change_candidate_usd == pytest.approx(37.0)
    assert large.positive_equity_change_candidate_usd == pytest.approx(250.0)
    assert small.contribution_candidate_pending
    assert large.contribution_candidate_pending


def test_negative_equity_change_is_not_classified_as_contribution():
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T16:00:00Z",
        observed_equity_usd=1_950.0,
    )
    assert observation.equity_change_usd == pytest.approx(-50.0)
    assert observation.positive_equity_change_candidate_usd == pytest.approx(0.0)
    assert not observation.contribution_candidate_pending
    assert observation.change_classification == "NEGATIVE_EQUITY_CHANGE_NOT_CONTRIBUTION"
    assert not observation.intraday_risk_increase_allowed


def test_observation_at_exact_daily_boundary_is_eligible_for_that_boundary():
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-08T00:00:00Z",
        observed_equity_usd=2_100.0,
    )
    assert observation.observed_at_daily_boundary
    assert observation.scheduled_daily_decision_timestamp == "2026-08-08T00:00:00Z"
    assert not observation.intraday_target_recalculation_allowed


def test_observation_digest_is_deterministic_and_sensitive_to_equity_change():
    kwargs = dict(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T12:00:00Z",
    )
    first = observe_equity_change(observed_equity_usd=2_100.0, **kwargs)
    second = observe_equity_change(observed_equity_usd=2_100.0, **kwargs)
    changed = observe_equity_change(observed_equity_usd=2_101.0, **kwargs)
    assert first.canonical_json() == second.canonical_json()
    assert first.digest() == second.digest()
    assert len(first.digest()) == 64
    assert first.digest() != changed.digest()


def test_daily_application_rejects_unscheduled_intraday_or_wrong_boundary():
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T13:00:00Z",
        observed_equity_usd=2_100.0,
    )
    with pytest.raises(ContributionHandlingError, match="scheduled daily decision"):
        apply_at_daily_decision(
            observation=observation,
            daily_dataset=_dataset("2026-08-07T13:01:00Z"),
            account_equity_usd=2_100.0,
            current_positions_notional_usd={},
            approved_config=load_product_config(),
        )
    with pytest.raises(ContributionHandlingError, match="scheduled daily decision"):
        apply_at_daily_decision(
            observation=observation,
            daily_dataset=_dataset("2026-08-09T00:00:00Z"),
            account_equity_usd=2_100.0,
            current_positions_notional_usd={},
            approved_config=load_product_config(),
        )


def test_next_daily_decision_uses_fresh_full_equity_through_same_p3_2_then_p3_3_chain(monkeypatch):
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T13:00:00Z",
        observed_equity_usd=2_100.0,
    )
    calls = []
    current_positions = {"BTC": 600.0, "ETH": 200.0, "SOL": 0.0, "BNB": 0.0}

    def fake_calculate_target(*, daily_dataset, account_equity_usd, current_positions, approved_config):
        calls.append(
            {
                "decision": daily_dataset.decision_timestamp,
                "equity": account_equity_usd,
                "positions": dict(current_positions),
                "product_id": approved_config.product_id,
            }
        )
        return _target(equity=float(account_equity_usd), current_positions=dict(current_positions))

    monkeypatch.setattr(contribution_module, "calculate_target", fake_calculate_target)

    decision = apply_at_daily_decision(
        observation=observation,
        daily_dataset=_dataset("2026-08-08T00:00:00Z"),
        account_equity_usd=2_135.0,
        current_positions_notional_usd=current_positions,
        approved_config=load_product_config(),
    )

    assert calls == [
        {
            "decision": "2026-08-08T00:00:00Z",
            "equity": 2_135.0,
            "positions": current_positions,
            "product_id": "BRRK-PLAN-B",
        }
    ]
    assert decision.contribution_candidate_usd == pytest.approx(100.0)
    assert decision.decision_account_equity_usd == pytest.approx(2_135.0)
    assert decision.target_engine_version == TARGET_ENGINE_VERSION
    assert decision.rebalance_control_version == REBALANCE_CONTROL_VERSION
    assert decision.target.account_equity_usd == pytest.approx(2_135.0)
    assert decision.rebalance_control.account_equity_usd == pytest.approx(2_135.0)
    assert decision.rebalance_control.model_target_notionals_usd["BTC"] == pytest.approx(0.40 * 2_135.0)
    assert decision.rebalance_control.model_target_notionals_usd["ETH"] == pytest.approx(0.20 * 2_135.0)
    assert decision.target_digest == decision.target.digest()
    assert decision.rebalance_control_digest == decision.rebalance_control.digest()
    assert decision.contribution_candidate_included
    assert decision.production_authorized is False


def test_contribution_decision_digest_is_deterministic(monkeypatch):
    observation = observe_equity_change(
        baseline_decision_timestamp="2026-08-07T00:00:00Z",
        baseline_equity_usd=2_000.0,
        observed_at="2026-08-07T13:00:00Z",
        observed_equity_usd=2_100.0,
    )

    def fake_calculate_target(*, daily_dataset, account_equity_usd, current_positions, approved_config):
        return _target(equity=float(account_equity_usd), current_positions=dict(current_positions))

    monkeypatch.setattr(contribution_module, "calculate_target", fake_calculate_target)
    kwargs = dict(
        observation=observation,
        daily_dataset=_dataset("2026-08-08T00:00:00Z"),
        account_equity_usd=2_135.0,
        current_positions_notional_usd={"BTC": 600.0, "ETH": 200.0},
        approved_config=load_product_config(),
    )
    first = apply_at_daily_decision(**kwargs)
    second = apply_at_daily_decision(**kwargs)
    assert first.canonical_json() == second.canonical_json()
    assert first.digest() == second.digest()
    assert len(first.digest()) == 64
