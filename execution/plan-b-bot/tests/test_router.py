import json

import pytest

from beta_bot.instrument_registry import load_instrument_registry
from beta_bot.route_cost import FeeSchedule, RouteObservation
from beta_bot.router import (
    EconomicExposureRequest,
    RouterDecisionError,
    SpotRuntimeIdentity,
    compare_expected_realized_cost,
    decide_route,
    load_router_policy,
    replay_logged_decision,
    resolve_spot_runtime_identity,
    route_and_log,
)


def request(asset="BTC", *, direction="long", role="base", notional=1000.0, hours=24.0):
    return EconomicExposureRequest(
        decision_timestamp="2026-08-06T00:00:00Z",
        asset=asset,
        direction=direction,
        exposure_role=role,
        notional_usd=notional,
        holding_hours=hours,
        target_revision="target-2026-08-06",
    )


def obs(route, *, asset="BTC", notional=1000.0, hours=24.0, depth=100_000.0, funding=0.0, spread=1.0, slippage=0.5):
    return RouteObservation(
        asset=asset,
        route=route,
        notional_usd=notional,
        holding_hours=hours,
        order_style="taker",
        spread_bps=spread,
        entry_slippage_bps=slippage,
        exit_slippage_bps=slippage,
        live_depth_usd=depth,
        vwap_impact_bps=spread + 2 * slippage,
        funding_bps_per_hour=funding if route == "perp" else 0.0,
        entry_basis_bps=0.0,
        expected_exit_basis_bps=0.0,
        custody_redemption_bps=0.0,
    )


def spot_meta(token="UBTC", pair_name="BTC/USDC", pair_index=42):
    return {
        "tokens": [
            {"name": "USDC", "index": 0, "szDecimals": 2, "weiDecimals": 6, "tokenId": "usdc", "isCanonical": True},
            {"name": token, "index": 1, "szDecimals": 5, "weiDecimals": 8, "tokenId": f"token-{token}", "isCanonical": True},
        ],
        "universe": [
            {"name": pair_name, "tokens": [1, 0], "index": pair_index, "isCanonical": True},
        ],
    }


def btc_runtime(registry):
    return resolve_spot_runtime_identity(registry, "BTC", spot_meta())


def test_policy_preserves_scope_and_no_production_authorization():
    policy = load_router_policy()
    assert policy.base_long_spot_candidates == ("BTC", "ETH", "SOL")
    assert policy.perp_only_assets == {"BNB": "ROUTER-BNB-PERP-ONLY-2026-08-06"}
    assert policy.authorization == "IMPLEMENTATION_PLAN_ONLY_NO_PRODUCTION_AUTHORIZATION"


def test_resolve_spot_runtime_identity_uses_dynamic_pair_index_not_ui_name():
    registry = load_instrument_registry()
    runtime = resolve_spot_runtime_identity(registry, "BTC", spot_meta(pair_name="BTC/USDC", pair_index=77))
    assert runtime.expected_hypercore_token == "UBTC"
    assert runtime.expected_hypercore_pair == "UBTC/USDC"
    assert runtime.runtime_pair_label == "BTC/USDC"
    assert runtime.coin_id == "@77"
    assert runtime.pair_index == 77


def test_resolve_spot_runtime_identity_fails_closed_on_missing_verified_token():
    registry = load_instrument_registry()
    with pytest.raises(RouterDecisionError, match="missing or ambiguous"):
        resolve_spot_runtime_identity(registry, "BTC", spot_meta(token="NOT_BTC"))


def test_base_long_selects_verified_spot_when_lower_cost():
    registry = load_instrument_registry()
    policy = load_router_policy()
    decision = decide_route(
        request(hours=100),
        registry=registry,
        policy=policy,
        spot_observation=obs("spot", hours=100),
        perp_observation=obs("perp", hours=100, funding=0.2),
        spot_runtime_identity=btc_runtime(registry),
    )
    assert decision.selected_route == "spot"
    assert decision.reason_code == "SPOT_VERIFIED_LOWER_COST"
    assert decision.plan.instrument_id == "@42"
    assert decision.plan.display_identity == "BTC/USDC"
    assert decision.plan.hypercore_identity == "UBTC/USDC"


def test_base_long_selects_perp_when_lower_cost():
    registry = load_instrument_registry()
    decision = decide_route(
        request(),
        registry=registry,
        policy=load_router_policy(),
        spot_observation=obs("spot"),
        perp_observation=obs("perp"),
        spot_runtime_identity=btc_runtime(registry),
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_LOWER_COST"
    assert decision.plan.instrument_id == "BTC"


def test_verified_cost_tie_prefers_spot_by_canonical_policy():
    registry = load_instrument_registry()
    zero_fees = FeeSchedule(spot_taker_bps=0, spot_maker_bps=0, perp_taker_bps=0, perp_maker_bps=0, source="test")
    decision = decide_route(
        request(),
        registry=registry,
        policy=load_router_policy(),
        spot_observation=obs("spot"),
        perp_observation=obs("perp"),
        spot_runtime_identity=btc_runtime(registry),
        fees=zero_fees,
    )
    assert decision.selected_route == "spot"
    assert decision.reason_code == "SPOT_VERIFIED_COST_TIE"


def test_bnb_is_perp_only_by_product_policy():
    decision = decide_route(
        request("BNB"),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=obs("perp", asset="BNB"),
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_PRODUCT_POLICY"


def test_bnb_rejects_spot_inputs_instead_of_silently_reopening_policy():
    with pytest.raises(RouterDecisionError, match="perp-only policy"):
        decide_route(
            request("BNB"),
            registry=load_instrument_registry(),
            policy=load_router_policy(),
            spot_observation=obs("spot", asset="BNB"),
            perp_observation=obs("perp", asset="BNB"),
            spot_runtime_identity=None,
        )


def test_short_is_forced_to_perp_without_starting_bear_strategy_logic():
    decision = decide_route(
        request(direction="short"),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=obs("perp"),
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_REQUIRED_FOR_SHORT"


def test_leverage_overlay_is_forced_to_perp_without_selecting_leverage_level():
    decision = decide_route(
        request(role="leverage_overlay"),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=obs("perp"),
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_REQUIRED_FOR_LEVERAGE_OVERLAY"


def test_spot_liquidity_failure_falls_back_to_viable_perp():
    registry = load_instrument_registry()
    decision = decide_route(
        request(),
        registry=registry,
        policy=load_router_policy(),
        spot_observation=obs("spot", depth=500.0),
        perp_observation=obs("perp", depth=100_000.0),
        spot_runtime_identity=btc_runtime(registry),
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_SPOT_LIQUIDITY_FAIL"


def test_both_routes_liquidity_fail_returns_no_trade():
    registry = load_instrument_registry()
    decision = decide_route(
        request(),
        registry=registry,
        policy=load_router_policy(),
        spot_observation=obs("spot", depth=500.0),
        perp_observation=obs("perp", depth=500.0),
        spot_runtime_identity=btc_runtime(registry),
    )
    assert decision.selected_route == "no_trade"
    assert decision.reason_code == "NO_TRADE_LIQUIDITY_FAIL"
    assert decision.plan is None


def test_missing_spot_cost_falls_back_to_perp_with_explicit_reason():
    registry = load_instrument_registry()
    decision = decide_route(
        request(),
        registry=registry,
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=obs("perp"),
        spot_runtime_identity=btc_runtime(registry),
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_SPOT_COST_UNAVAILABLE"


def test_missing_runtime_spot_identity_falls_back_to_perp():
    decision = decide_route(
        request(),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=obs("spot"),
        perp_observation=obs("perp"),
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "perp"
    assert decision.reason_code == "PERP_SPOT_UNVERIFIED"


def test_no_cost_evidence_returns_no_trade_instead_of_guessing():
    decision = decide_route(
        request(),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=None,
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "no_trade"
    assert decision.reason_code == "NO_TRADE_COST_UNAVAILABLE"


def test_zero_exposure_is_no_trade_without_market_observations():
    decision = decide_route(
        request(notional=0.0),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=None,
        spot_runtime_identity=None,
    )
    assert decision.selected_route == "no_trade"
    assert decision.reason_code == "NO_TRADE_ZERO_EXPOSURE"


def test_runtime_identity_mismatch_fails_closed_before_spot_selection():
    registry = load_instrument_registry()
    wrong = SpotRuntimeIdentity(
        asset="ETH",
        expected_hypercore_token="UETH",
        expected_hypercore_pair="UETH/USDC",
        runtime_pair_label="ETH/USDC",
        token_index=1,
        pair_index=12,
        coin_id="@12",
        sz_decimals=4,
        wei_decimals=18,
        token_id="eth",
        token_is_canonical=True,
        pair_is_canonical=True,
    )
    with pytest.raises(RouterDecisionError, match="asset mismatch"):
        decide_route(
            request(hours=100),
            registry=registry,
            policy=load_router_policy(),
            spot_observation=obs("spot", hours=100),
            perp_observation=obs("perp", hours=100, funding=0.2),
            spot_runtime_identity=wrong,
        )


def test_observation_must_match_same_asset_notional_and_horizon():
    registry = load_instrument_registry()
    policy = load_router_policy()
    with pytest.raises(RouterDecisionError, match="asset does not match"):
        decide_route(request(), registry=registry, policy=policy, spot_observation=None, perp_observation=obs("perp", asset="ETH"), spot_runtime_identity=None)
    with pytest.raises(RouterDecisionError, match="notional does not match"):
        decide_route(request(), registry=registry, policy=policy, spot_observation=None, perp_observation=obs("perp", notional=999.0), spot_runtime_identity=None)
    with pytest.raises(RouterDecisionError, match="holding horizon"):
        decide_route(request(), registry=registry, policy=policy, spot_observation=None, perp_observation=obs("perp", hours=12.0), spot_runtime_identity=None)


def test_decision_id_is_deterministic_and_logged_assumptions_replay(tmp_path):
    registry = load_instrument_registry()
    policy = load_router_policy()
    kwargs = dict(
        registry=registry,
        policy=policy,
        spot_observation=obs("spot"),
        perp_observation=obs("perp"),
        spot_runtime_identity=btc_runtime(registry),
    )
    first = decide_route(request(), **kwargs)
    second = decide_route(request(), **kwargs)
    assert first.decision_id == second.decision_id

    path = tmp_path / "router-decisions.jsonl"
    logged = route_and_log(request(), log_path=path, **kwargs)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["decision_id"] == logged.decision_id
    replayed = replay_logged_decision(rows[0], registry=registry, policy=policy)
    assert replayed.to_dict() == logged.to_dict()


def test_replay_rejects_policy_or_decision_tampering():
    registry = load_instrument_registry()
    policy = load_router_policy()
    decision = decide_route(
        request(),
        registry=registry,
        policy=policy,
        spot_observation=obs("spot"),
        perp_observation=obs("perp"),
        spot_runtime_identity=btc_runtime(registry),
    )
    record = decision.to_dict()
    record["policy_id"] = "tampered"
    with pytest.raises(RouterDecisionError, match="policy_id"):
        replay_logged_decision(record, registry=registry, policy=policy)

    record = decision.to_dict()
    record["decision_id"] = "0" * 32
    with pytest.raises(RouterDecisionError, match="not reproducible"):
        replay_logged_decision(record, registry=registry, policy=policy)


def test_expected_vs_realized_cost_attribution_uses_selected_plan():
    decision = decide_route(
        request("BNB"),
        registry=load_instrument_registry(),
        policy=load_router_policy(),
        spot_observation=None,
        perp_observation=obs("perp", asset="BNB"),
        spot_runtime_identity=None,
    )
    comparison = compare_expected_realized_cost(decision, realized_cost_bps=20.0)
    assert comparison.decision_id == decision.decision_id
    assert comparison.route == "perp"
    assert comparison.variance_bps == pytest.approx(20.0 - decision.plan.expected_cost_bps)
    assert comparison.realized_cost_usd == pytest.approx(2.0)
