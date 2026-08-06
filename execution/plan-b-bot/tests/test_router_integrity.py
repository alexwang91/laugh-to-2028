import pytest

from beta_bot.instrument_registry import load_instrument_registry
from beta_bot.route_cost import RouteObservation
from beta_bot.router import (
    EconomicExposureRequest,
    RouterDecisionError,
    decide_route,
    load_router_policy,
    replay_logged_decision,
    resolve_spot_runtime_identity,
)


def request(*, notional=1000.0):
    return EconomicExposureRequest(
        decision_timestamp="2026-08-06T00:00:00Z",
        asset="BTC",
        direction="long",
        exposure_role="base",
        notional_usd=notional,
        holding_hours=24.0,
        target_revision="target-2026-08-06",
    )


def obs(route, *, notional=1000.0):
    return RouteObservation(
        asset="BTC",
        route=route,
        notional_usd=notional,
        holding_hours=24.0,
        order_style="taker",
        spread_bps=1.0,
        entry_slippage_bps=0.5,
        exit_slippage_bps=0.5,
        live_depth_usd=100_000.0,
        vwap_impact_bps=2.0,
        funding_bps_per_hour=0.0,
        entry_basis_bps=0.0,
        expected_exit_basis_bps=0.0,
        custody_redemption_bps=0.0,
    )


def runtime(registry):
    return resolve_spot_runtime_identity(
        registry,
        "BTC",
        {
            "tokens": [
                {"name": "USDC", "index": 0, "szDecimals": 2, "weiDecimals": 6, "tokenId": "usdc", "isCanonical": True},
                {"name": "UBTC", "index": 1, "szDecimals": 5, "weiDecimals": 8, "tokenId": "ubtc", "isCanonical": True},
            ],
            "universe": [
                {"name": "BTC/USDC", "tokens": [1, 0], "index": 42, "isCanonical": True},
            ],
        },
    )


def canonical_decision():
    registry = load_instrument_registry()
    policy = load_router_policy()
    decision = decide_route(
        request(),
        registry=registry,
        policy=policy,
        spot_observation=obs("spot"),
        perp_observation=obs("perp"),
        spot_runtime_identity=runtime(registry),
    )
    return registry, policy, decision


def test_zero_exposure_short_circuits_before_market_observation_validation():
    decision = decide_route(
        request(notional=0.0),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=obs("spot", notional=0.0),
        perp_observation=obs("perp", notional=0.0),
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "no_trade"
    assert decision.reason_code == "NO_TRADE_ZERO_EXPOSURE"
    assert decision.spot_candidate is None
    assert decision.perp_candidate is None


@pytest.mark.parametrize("field", ["reason_code", "plan", "spot_candidate", "perp_candidate"])
def test_replay_rejects_tampered_derived_fields_even_when_decision_id_is_unchanged(field):
    registry, policy, decision = canonical_decision()
    record = decision.to_dict()

    if field == "reason_code":
        record[field] = "SPOT_VERIFIED_LOWER_COST"
    elif field == "plan":
        record[field]["expected_cost_bps"] += 1.0
    else:
        record[field]["estimate"]["total_cost_bps"] += 1.0

    with pytest.raises(RouterDecisionError, match="modified or contains non-reproducible"):
        replay_logged_decision(record, registry=registry, policy=policy)


def test_replay_rejects_unrecognized_extra_fields():
    registry, policy, decision = canonical_decision()
    record = decision.to_dict()
    record["unlogged_override"] = "should-not-exist"
    with pytest.raises(RouterDecisionError, match="modified or contains non-reproducible"):
        replay_logged_decision(record, registry=registry, policy=policy)
