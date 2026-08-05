import pytest

from beta_bot.executor import _submit_once
from beta_bot.order_identity import build_order_identity
from beta_bot.order_ledger import LedgerIntent, LedgerUncertainState, OrderLedger


class FakeInfo:
    def __init__(self):
        self.orders: dict[str, dict] = {}
        self.lookup_calls: list[str] = []
        self.malformed = False

    def query_order_by_cloid(self, _address, cloid):
        raw = cloid.to_raw()
        self.lookup_calls.append(raw)
        if self.malformed:
            return {"unexpected": True}
        return self.orders.get(raw, {"status": "unknownOid"})


class FakeExchange:
    def __init__(self):
        self.info = FakeInfo()


def _identity(target_revision: str = "target_qty:0.25000"):
    return build_order_identity(
        release_id="candidate-p1-2",
        decision_timestamp_ms=1_785_974_400_000,
        asset="BTC",
        side="buy",
        intent="increase",
        target_revision=target_revision,
    )


def _intent(target_revision: str = "target_qty:0.25000"):
    identity = _identity(target_revision)
    quantity = 0.25 if target_revision.endswith("0.25000") else 0.30
    return LedgerIntent(
        identity=identity,
        route_action="increase",
        submitted_quantity=quantity,
        submitted_order_parameters={"method": "market_open", "coin": "BTC", "size": quantity},
    )


def _exchange_order(status: str = "filled", oid: int = 123):
    return {
        "status": "order",
        "order": {
            "order": {"coin": "BTC", "oid": oid, "sz": "0", "origSz": "0.25"},
            "status": status,
            "statusTimestamp": 1_785_974_401_000,
        },
    }


def test_intent_and_attempt_are_durable_before_network_submit(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    exchange = FakeExchange()
    submissions: list[str] = []
    order_intent = _intent()

    def submit(cloid):
        row = ledger.get_order(order_intent.identity.cloid)
        assert row is not None
        assert row["submission_attempt_timestamp_ms"] is not None
        raw = cloid.to_raw()
        submissions.append(raw)
        exchange.info.orders[raw] = _exchange_order()
        return {
            "status": "ok",
            "response": {"data": {"statuses": [{"filled": {"oid": 123, "totalSz": "0.25"}}]}},
        }

    status, existing = _submit_once(
        exchange=exchange,
        account_address="0x0000000000000000000000000000000000000001",
        ledger=ledger,
        intent=order_intent,
        submit=submit,
    )

    assert status == "filled"
    assert existing is None
    assert submissions == [order_intent.identity.cloid]
    row = ledger.get_order(order_intent.identity.cloid)
    assert row["submission_response_status"] == "filled"
    assert row["exchange_oid"] == "123"
    assert row["terminal_status"] is None


def test_replay_known_cloid_is_suppressed_and_persisted(tmp_path):
    ledger_path = str(tmp_path / "orders.sqlite3")
    ledger = OrderLedger(ledger_path)
    exchange = FakeExchange()
    order_intent = _intent()
    exchange.info.orders[order_intent.identity.cloid] = _exchange_order(status="filled", oid=456)
    submitted = False

    def submit(_cloid):
        nonlocal submitted
        submitted = True
        raise AssertionError("duplicate must not submit")

    status, existing = _submit_once(
        exchange=exchange,
        account_address="0x0000000000000000000000000000000000000001",
        ledger=ledger,
        intent=order_intent,
        submit=submit,
    )

    assert status == "duplicate_suppressed"
    assert existing == "filled"
    assert submitted is False
    row = OrderLedger(ledger_path).get_order(order_intent.identity.cloid)
    assert row["exchange_oid"] == "456"
    assert row["last_exchange_status"] == "filled"
    assert row["terminal_status"] is None


def test_timeout_then_unknown_oid_on_restart_never_submits_twice(tmp_path):
    ledger_path = str(tmp_path / "orders.sqlite3")
    exchange = FakeExchange()
    order_intent = _intent()
    submissions = 0

    def timeout_submit(_cloid):
        nonlocal submissions
        submissions += 1
        raise TimeoutError("network timeout")

    with pytest.raises(TimeoutError):
        _submit_once(
            exchange=exchange,
            account_address="0x0000000000000000000000000000000000000001",
            ledger=OrderLedger(ledger_path),
            intent=order_intent,
            submit=timeout_submit,
        )

    def must_not_submit(_cloid):
        nonlocal submissions
        submissions += 1
        raise AssertionError("blind retry must not happen")

    with pytest.raises(LedgerUncertainState, match="blind retry is forbidden"):
        _submit_once(
            exchange=exchange,
            account_address="0x0000000000000000000000000000000000000001",
            ledger=OrderLedger(ledger_path),
            intent=order_intent,
            submit=must_not_submit,
        )

    assert submissions == 1
    row = OrderLedger(ledger_path).get_order(order_intent.identity.cloid)
    assert row["terminal_status"] is None
    assert row["current_status"] == "reconciliation_uncertain"


def test_new_target_revision_is_a_new_economic_order_identity(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    exchange = FakeExchange()
    submissions: list[str] = []

    def submit(cloid):
        raw = cloid.to_raw()
        submissions.append(raw)
        exchange.info.orders[raw] = _exchange_order(oid=100 + len(submissions))
        return {
            "status": "ok",
            "response": {"data": {"statuses": [{"filled": {"oid": 100 + len(submissions)}}]}},
        }

    for order_intent in (_intent("target_qty:0.25000"), _intent("target_qty:0.30000")):
        status, existing = _submit_once(
            exchange=exchange,
            account_address="0x0000000000000000000000000000000000000001",
            ledger=ledger,
            intent=order_intent,
            submit=submit,
        )
        assert status == "filled"
        assert existing is None

    assert len(submissions) == 2
    assert submissions[0] != submissions[1]


def test_unknown_lookup_response_fails_closed_after_intent_persistence(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    exchange = FakeExchange()
    exchange.info.malformed = True
    order_intent = _intent()
    submitted = False

    def submit(_cloid):
        nonlocal submitted
        submitted = True
        raise AssertionError("submit must not be reached")

    with pytest.raises(RuntimeError, match="Unexpected Hyperliquid orderStatus response"):
        _submit_once(
            exchange=exchange,
            account_address="0x0000000000000000000000000000000000000001",
            ledger=ledger,
            intent=order_intent,
            submit=submit,
        )

    assert submitted is False
    row = ledger.get_order(order_intent.identity.cloid)
    assert row is not None
    assert row["submission_attempt_timestamp_ms"] is None
    assert row["current_status"] == "reconciliation_uncertain"
