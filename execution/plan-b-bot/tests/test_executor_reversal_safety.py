import pytest

import beta_bot.executor as executor
from beta_bot.config import Settings
from beta_bot.reversal import ReversalSafetyError


class DummyLedger:
    pass


class FakeExchange:
    def __init__(self, *_args, **_kwargs):
        self.open_calls = 0
        self.close_calls = 0

    def set_expires_after(self, _value):
        pass

    def update_leverage(self, *_args):
        pass

    def market_close(self, *_args, **_kwargs):
        self.close_calls += 1
        return {"status": "ok", "response": {"data": {"statuses": [{"filled": {"oid": 1}}]}}}

    def market_open(self, *_args, **_kwargs):
        self.open_calls += 1
        return {"status": "ok", "response": {"data": {"statuses": [{"filled": {"oid": 2}}]}}}


def _settings(tmp_path):
    return Settings(
        network="testnet",
        trading_mode="trade",
        coin="BTC",
        master_address="0x0000000000000000000000000000000000000001",
        vault_address=None,
        api_private_key="0x" + "11" * 32,
        external_spot_btc_qty=0.0,
        external_cash_usd=0.0,
        rebalance_band=0.05,
        min_trade_usd=100.0,
        normal_beta_cap=1.0,
        hard_beta_cap=1.5,
        allow_strong_beta=False,
        max_platform_leverage=2,
        max_slippage_bps=15.0,
        request_timeout_seconds=15.0,
        candle_lookback_days=450,
        cron_secret=None,
        live_trading_confirmation=None,
        telegram_bot_token=None,
        telegram_chat_id=None,
        order_ledger_path=str(tmp_path / "orders.sqlite3"),
        order_ledger_durable_storage=True,
        running_on_vercel=False,
    )


def _install_common(monkeypatch):
    exchange = FakeExchange()
    monkeypatch.setattr(executor.Account, "from_key", lambda _key: object())
    monkeypatch.setattr(executor, "Exchange", lambda *_args, **_kwargs: exchange)
    monkeypatch.setattr(executor, "_open_ledger", lambda _settings: DummyLedger())
    monkeypatch.setattr(
        executor,
        "fetch_perp_metadata",
        lambda *_args, **_kwargs: {"universe": [{"name": "BTC", "szDecimals": 5}]},
    )

    submitted = []

    def fake_submit_once(*, intent, submit, **_kwargs):
        submitted.append(intent)
        submit(object())
        return "filled", None

    monkeypatch.setattr(executor, "_submit_once", fake_submit_once)
    return exchange, submitted


def test_reversal_opens_only_after_fresh_exchange_flat(monkeypatch, tmp_path):
    exchange, submitted = _install_common(monkeypatch)
    monkeypatch.setattr(
        executor,
        "fetch_user_state",
        lambda *_args, **_kwargs: {"assetPositions": []},
    )

    actions = executor.execute_target_position(
        _settings(tmp_path),
        current_qty=0.5,
        target_qty=-0.3,
        release_id="candidate-p1-4",
        decision_timestamp_ms=1_785_974_400_000,
    )

    assert [item["action"] for item in actions] == ["close_for_reversal", "open_reversal"]
    assert exchange.close_calls == 1
    assert exchange.open_calls == 1
    assert submitted[0].route_action == "close_for_reversal"
    assert submitted[0].submitted_order_parameters["reduce_only_semantics"] is True
    assert submitted[0].submitted_order_parameters["sz_decimals"] == 5
    assert submitted[1].route_action == "open_reversal"
    assert submitted[1].submitted_order_parameters["position_before_qty"] == 0.0
    assert submitted[1].submitted_order_parameters["reversal_flat_verified"] is True
    assert actions[1]["fresh_position_before_open"] == 0.0


def test_partial_close_blocks_new_direction_open(monkeypatch, tmp_path):
    exchange, submitted = _install_common(monkeypatch)
    monkeypatch.setattr(
        executor,
        "fetch_user_state",
        lambda *_args, **_kwargs: {
            "assetPositions": [{"position": {"coin": "BTC", "szi": "0.2"}}]
        },
    )

    with pytest.raises(ReversalSafetyError, match="close is incomplete"):
        executor.execute_target_position(
            _settings(tmp_path),
            current_qty=0.5,
            target_qty=-0.3,
            release_id="candidate-p1-4",
            decision_timestamp_ms=1_785_974_400_000,
        )

    assert exchange.close_calls == 1
    assert exchange.open_calls == 0
    assert [item.route_action for item in submitted] == ["close_for_reversal"]


def test_unexpected_cross_through_blocks_new_direction_open(monkeypatch, tmp_path):
    exchange, submitted = _install_common(monkeypatch)
    monkeypatch.setattr(
        executor,
        "fetch_user_state",
        lambda *_args, **_kwargs: {
            "assetPositions": [{"position": {"coin": "BTC", "szi": "-0.05"}}]
        },
    )

    with pytest.raises(ReversalSafetyError, match="already crossed through flat"):
        executor.execute_target_position(
            _settings(tmp_path),
            current_qty=0.5,
            target_qty=-0.3,
            release_id="candidate-p1-4",
            decision_timestamp_ms=1_785_974_400_000,
        )

    assert exchange.open_calls == 0
    assert [item.route_action for item in submitted] == ["close_for_reversal"]


def test_fresh_state_read_failure_blocks_new_direction_open(monkeypatch, tmp_path):
    exchange, submitted = _install_common(monkeypatch)

    def fail_state(*_args, **_kwargs):
        raise TimeoutError("account state timeout")

    monkeypatch.setattr(executor, "fetch_user_state", fail_state)

    with pytest.raises(ReversalSafetyError, match="Fresh reversal position verification failed"):
        executor.execute_target_position(
            _settings(tmp_path),
            current_qty=-0.4,
            target_qty=0.25,
            release_id="candidate-p1-4",
            decision_timestamp_ms=1_785_974_400_000,
        )

    assert exchange.close_calls == 1
    assert exchange.open_calls == 0
    assert [item.route_action for item in submitted] == ["close_for_reversal"]
