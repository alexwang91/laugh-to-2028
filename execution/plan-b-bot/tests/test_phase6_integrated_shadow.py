from __future__ import annotations

from dataclasses import dataclass
import ast
import hashlib
from pathlib import Path

import pytest

from beta_bot.rebalance_control import REBALANCE_CONTROL_VERSION
from beta_bot.shadow_system import (
    CYCLE_LAYER_STATUS,
    SHADOW_MODE,
    ShadowRouteProjection,
    ShadowSystemError,
    build_integrated_shadow_record,
)


@dataclass
class FakePlan:
    decision_timestamp: str = "2026-08-08T00:00:00+00:00"
    control_version: str = REBALANCE_CONTROL_VERSION
    production_authorized: bool = False
    model_target_weights: dict[str, float] | None = None
    current_position_weights: dict[str, float] | None = None
    current_position_notionals_usd: dict[str, float] | None = None
    post_control_desired_weights: dict[str, float] | None = None
    proposed_delta_notionals_usd: dict[str, float] | None = None
    l1_target_gap: float = 1.0

    def __post_init__(self) -> None:
        if self.model_target_weights is None:
            self.model_target_weights = {"BTC": 0.4, "ETH": 0.3, "SOL": 0.2, "BNB": 0.1}
        if self.current_position_weights is None:
            self.current_position_weights = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0, "BNB": 0.0}
        if self.current_position_notionals_usd is None:
            self.current_position_notionals_usd = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0, "BNB": 0.0}
        if self.post_control_desired_weights is None:
            self.post_control_desired_weights = dict(self.model_target_weights)
        if self.proposed_delta_notionals_usd is None:
            self.proposed_delta_notionals_usd = {"BTC": 400.0, "ETH": 300.0, "SOL": 200.0, "BNB": 100.0}

    def digest(self) -> str:
        return hashlib.sha256(b"phase6-test-plan").hexdigest()


def routes() -> dict[str, ShadowRouteProjection]:
    return {
        "BTC": ShadowRouteProjection("BTC", "spot", "SPOT_VERIFIED_LOWER_COST", "@BTC", 4.0, True),
        "ETH": ShadowRouteProjection("ETH", "spot", "SPOT_VERIFIED_LOWER_COST", "@ETH", 5.0, True),
        "SOL": ShadowRouteProjection("SOL", "perp", "PERP_LOWER_COST", "SOL", 6.0, True),
        "BNB": ShadowRouteProjection("BNB", "perp", "PERP_PRODUCT_POLICY", "BNB", 7.0, True),
    }


def build(plan: FakePlan, **overrides):
    kwargs = dict(
        plan=plan,
        route_projections=routes(),
        offline_reference_target_weights=dict(plan.model_target_weights),
        feature_reference_ok=True,
        data_complete=True,
        instrument_identity_ok=True,
        cost_model_ok=True,
        state_transition_explained=True,
        schedule_ok=True,
        emergency_active=False,
    )
    kwargs.update(overrides)
    return build_integrated_shadow_record(**kwargs)


def test_shadow_happy_path_is_zero_authority_and_preserves_canonical_target() -> None:
    plan = FakePlan()
    record = build(plan)
    assert record.mode == SHADOW_MODE
    assert record.cycle_layer_status == CYCLE_LAYER_STATUS
    assert record.status == "SHADOW_COMPUTED_NO_AUTHORITY"
    assert record.production_authorized is False
    assert record.signature_authorized is False
    assert record.order_submission_authorized is False
    assert record.model_target_weights == plan.model_target_weights
    assert record.target_gross_weight == pytest.approx(1.0)
    assert record.leverage_target == pytest.approx(1.0)
    assert len(record.hypothetical_orders) == 4
    assert all(row.hypothetical_only for row in record.hypothetical_orders)
    assert sum(row.notional_usd for row in record.hypothetical_orders) == pytest.approx(1000.0)
    assert record.offline_reference_l1_drift == pytest.approx(0.0)
    assert record.alerts == ()
    assert len(record.digest()) == 64


def test_reference_or_data_failure_discards_all_hypothetical_orders() -> None:
    record = build(FakePlan(), data_complete=False)
    assert record.status == "BLOCKED_FAIL_CLOSED"
    assert record.hypothetical_orders == ()
    assert "MISSING_OR_INCOMPLETE_DATA" in record.alerts

    record2 = build(
        FakePlan(),
        offline_reference_target_weights={"BTC": 0.39, "ETH": 0.31, "SOL": 0.2, "BNB": 0.1},
    )
    assert record2.status == "BLOCKED_FAIL_CLOSED"
    assert record2.hypothetical_orders == ()
    assert "TARGET_REFERENCE_MISMATCH" in record2.alerts


def test_route_failure_is_atomic_fail_closed_not_partial_plan() -> None:
    bad_routes = routes()
    bad_routes["SOL"] = ShadowRouteProjection(
        "SOL", "no_trade", "NO_TRADE_LIQUIDITY_FAIL", None, None, False
    )
    record = build(FakePlan(), route_projections=bad_routes)
    assert record.status == "BLOCKED_FAIL_CLOSED"
    assert record.hypothetical_orders == ()
    assert "ROUTE_UNAVAILABLE:SOL" in record.alerts


def test_emergency_is_hypothetical_flatten_only() -> None:
    plan = FakePlan(
        model_target_weights={"BTC": 0.4, "ETH": 0.3, "SOL": 0.2, "BNB": 0.1},
        current_position_weights={"BTC": 0.4, "ETH": 0.1, "SOL": 0.0, "BNB": 0.0},
        current_position_notionals_usd={"BTC": 400.0, "ETH": 100.0, "SOL": 0.0, "BNB": 0.0},
        post_control_desired_weights={"BTC": 0.4, "ETH": 0.3, "SOL": 0.2, "BNB": 0.1},
        proposed_delta_notionals_usd={"BTC": 0.0, "ETH": 200.0, "SOL": 200.0, "BNB": 100.0},
        l1_target_gap=0.5,
    )
    record = build(plan, emergency_active=True)
    assert record.emergency_hypothetical_action == "FLATTEN"
    assert record.status == "SHADOW_COMPUTED_NO_AUTHORITY"
    assert {(row.asset, row.side, row.notional_usd) for row in record.hypothetical_orders} == {
        ("BTC", "SELL", 400.0),
        ("ETH", "SELL", 100.0),
    }
    assert record.order_submission_authorized is False


def test_gross_above_one_or_short_target_is_rejected() -> None:
    with pytest.raises(ShadowSystemError, match="gross"):
        build(
            FakePlan(
                model_target_weights={"BTC": 0.6, "ETH": 0.4, "SOL": 0.1, "BNB": 0.0},
                post_control_desired_weights={"BTC": 0.6, "ETH": 0.4, "SOL": 0.1, "BNB": 0.0},
                proposed_delta_notionals_usd={"BTC": 600.0, "ETH": 400.0, "SOL": 100.0, "BNB": 0.0},
                l1_target_gap=1.1,
            )
        )
    with pytest.raises(ShadowSystemError, match="long-only"):
        build(
            FakePlan(
                model_target_weights={"BTC": 0.5, "ETH": 0.3, "SOL": 0.2, "BNB": -0.1},
                post_control_desired_weights={"BTC": 0.5, "ETH": 0.3, "SOL": 0.2, "BNB": -0.1},
                proposed_delta_notionals_usd={"BTC": 500.0, "ETH": 300.0, "SOL": 200.0, "BNB": -100.0},
                l1_target_gap=1.1,
            )
        )


def test_shadow_module_has_no_execution_or_signer_import_path() -> None:
    source_path = Path(__file__).resolve().parents[1] / "beta_bot" / "shadow_system.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    forbidden_import_fragments = {
        "executor",
        "hyperliquid.exchange",
        "eth_account",
        "web3",
    }
    assert not any(any(fragment in name for fragment in forbidden_import_fragments) for name in imports)
    forbidden_calls = {"execute_target_position", "submit_order", "sign_order", "withdraw", "transfer"}
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called.isdisjoint(forbidden_calls)
