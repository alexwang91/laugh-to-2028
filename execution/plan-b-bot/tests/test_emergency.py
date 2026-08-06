from __future__ import annotations

from types import SimpleNamespace

import pytest

from beta_bot.emergency import (
    EmergencyController,
    EmergencyPathError,
    NewRiskKillSwitch,
    normal_new_risk_disabled,
)


OK = {"status": "ok", "response": {"data": {"statuses": [{"resting": {"oid": 1}}]}}}
META = {
    "universe": [
        {"name": "BTC", "szDecimals": 5},
        {"name": "ETH", "szDecimals": 4},
    ]
}


class DummySettings:
    api_url = "https://example.invalid"
    account_address = "0xabc"
    coin = "BTC"
    request_timeout_seconds = 1.0
    max_slippage_bps = 15.0
    order_ledger_path = "/tmp/p1-8-orders.sqlite3"
    new_risk_kill_switch_path = None
    can_trade = True


class FakeExchange:
    def __init__(self):
        self.cancel_calls = []
        self.close_calls = []
        self.cancel_response = OK
        self.close_response = OK

    def cancel(self, coin, oid):
        self.cancel_calls.append((coin, oid))
        return self.cancel_response

    def market_close(self, coin, *, sz, slippage):
        self.close_calls.append((coin, sz, slippage))
        return self.close_response


def _state(*positions):
    return {
        "assetPositions": [
            {"position": {"coin": coin, "szi": str(qty)}} for coin, qty in positions
        ]
    }


def test_cancel_all_uses_exchange_open_order_truth_without_target_engine():
    exchange = FakeExchange()
    controller = EmergencyController(
        DummySettings(),
        exchange=exchange,
        fetch_open_orders_fn=lambda *_args: [
            {"coin": "BTC", "oid": 11},
            {"coin": "ETH", "oid": 22},
        ],
    )

    actions = controller.cancel_all()

    assert exchange.cancel_calls == [("BTC", 11), ("ETH", 22)]
    assert [item.status for item in actions] == ["accepted", "accepted"]


def test_reduce_only_close_uses_fresh_position_and_never_opens():
    exchange = FakeExchange()
    controller = EmergencyController(
        DummySettings(),
        exchange=exchange,
        fetch_user_state_fn=lambda *_args: _state(("BTC", 0.123456)),
        fetch_perp_metadata_fn=lambda *_args: META,
    )

    actions = controller.reduce_only_close()

    assert exchange.close_calls == [("BTC", 0.12345, pytest.approx(0.0015))]
    assert actions[0].detail["reduce_only_semantics"] is True


def test_emergency_flat_cancels_then_closes_all_positions_and_verifies_flat():
    exchange = FakeExchange()
    states = iter([
        _state(("BTC", 0.2), ("ETH", -1.25)),
        _state(),
    ])
    controller = EmergencyController(
        DummySettings(),
        exchange=exchange,
        fetch_open_orders_fn=lambda *_args: [{"coin": "BTC", "oid": 7}],
        fetch_user_state_fn=lambda *_args: next(states),
        fetch_perp_metadata_fn=lambda *_args: META,
    )

    actions = controller.emergency_flat()

    assert exchange.cancel_calls == [("BTC", 7)]
    assert exchange.close_calls == [
        ("BTC", 0.2, pytest.approx(0.0015)),
        ("ETH", 1.25, pytest.approx(0.0015)),
    ]
    assert actions[-1].status == "verified_flat"


def test_emergency_flat_fails_if_fresh_verification_still_has_position():
    exchange = FakeExchange()
    states = iter([_state(("BTC", 0.2)), _state(("BTC", 0.01))])
    controller = EmergencyController(
        DummySettings(),
        exchange=exchange,
        fetch_open_orders_fn=lambda *_args: [],
        fetch_user_state_fn=lambda *_args: next(states),
        fetch_perp_metadata_fn=lambda *_args: META,
    )

    with pytest.raises(EmergencyPathError, match="not yet verified"):
        controller.emergency_flat()


def test_explicit_exchange_rejection_is_never_reported_as_success():
    exchange = FakeExchange()
    exchange.close_response = {
        "status": "ok",
        "response": {"data": {"statuses": [{"error": "margin failure"}]}},
    }
    controller = EmergencyController(
        DummySettings(),
        exchange=exchange,
        fetch_user_state_fn=lambda *_args: _state(("BTC", 0.2)),
        fetch_perp_metadata_fn=lambda *_args: META,
    )

    with pytest.raises(EmergencyPathError, match="rejected"):
        controller.reduce_only_close()


def test_disable_new_risk_switch_persists_and_malformed_state_fails_closed(tmp_path):
    path = tmp_path / "new-risk-disabled.json"
    switch = NewRiskKillSwitch(str(path))
    state = switch.disable(reason="controlled_test")

    assert state["disabled"] is True
    assert NewRiskKillSwitch(str(path)).new_risk_disabled is True

    path.write_text("not-json", encoding="utf-8")
    settings = SimpleNamespace(
        new_risk_kill_switch_path=str(path),
        order_ledger_path=None,
        can_trade=True,
    )
    assert normal_new_risk_disabled(settings) is True
