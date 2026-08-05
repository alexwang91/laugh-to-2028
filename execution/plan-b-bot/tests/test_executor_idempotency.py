import pytest

from beta_bot.executor import _submit_once
from beta_bot.order_identity import build_order_identity


class FakeInfo:
    def __init__(self):
        self.orders: dict[str, str] = {}
        self.lookup_calls: list[str] = []
        self.malformed = False

    def query_order_by_cloid(self, _address, cloid):
        raw = cloid.to_raw()
        self.lookup_calls.append(raw)
        if self.malformed:
            return {"unexpected": True}
        if raw not in self.orders:
            return {"status": "unknownOid"}
        return {"status": "order", "order": {"status": self.orders[raw]}}


class FakeExchange:
    def __init__(self):
        self.info = FakeInfo()


def _identity(target_revision: str = "target_qty:0.25000"):
    return build_order_identity(
        release_id="candidate-p1-1",
        decision_timestamp_ms=1_785_974_400_000,
        asset="BTC",
        side="buy",
        intent="increase",
        target_revision=target_revision,
    )


def test_replay_queries_exchange_and_does_not_submit_same_economic_order_twice():
    exchange = FakeExchange()
    submissions: list[str] = []
    first_identity = _identity()

    def submit(cloid):
        raw = cloid.to_raw()
        submissions.append(raw)
        exchange.info.orders[raw] = "filled"
        return {
            "status": "ok",
            "response": {"data": {"statuses": [{"filled": {"totalSz": "0.25"}}]}},
        }

    first_status, first_existing = _submit_once(
        exchange=exchange,
        account_address="0x0000000000000000000000000000000000000001",
        identity=first_identity,
        submit=submit,
    )

    # Simulate a fresh process reconstructing identity only from durable decision inputs.
    replay_identity = _identity()
    replay_status, replay_existing = _submit_once(
        exchange=exchange,
        account_address="0x0000000000000000000000000000000000000001",
        identity=replay_identity,
        submit=submit,
    )

    assert first_status == "filled"
    assert first_existing is None
    assert replay_status == "duplicate_suppressed"
    assert replay_existing == "filled"
    assert submissions == [first_identity.cloid]
    assert exchange.info.lookup_calls == [first_identity.cloid, first_identity.cloid]


def test_new_target_revision_is_a_new_economic_order_identity():
    exchange = FakeExchange()
    submissions: list[str] = []

    def submit(cloid):
        raw = cloid.to_raw()
        submissions.append(raw)
        exchange.info.orders[raw] = "filled"
        return {
            "status": "ok",
            "response": {"data": {"statuses": [{"filled": {"totalSz": "0.25"}}]}},
        }

    for identity in (_identity("target_qty:0.25000"), _identity("target_qty:0.30000")):
        status, existing = _submit_once(
            exchange=exchange,
            account_address="0x0000000000000000000000000000000000000001",
            identity=identity,
            submit=submit,
        )
        assert status == "filled"
        assert existing is None

    assert len(submissions) == 2
    assert submissions[0] != submissions[1]


def test_unknown_lookup_response_fails_closed_before_submission():
    exchange = FakeExchange()
    exchange.info.malformed = True
    submitted = False

    def submit(_cloid):
        nonlocal submitted
        submitted = True
        raise AssertionError("submit must not be reached")

    with pytest.raises(RuntimeError, match="Unexpected Hyperliquid orderStatus response"):
        _submit_once(
            exchange=exchange,
            account_address="0x0000000000000000000000000000000000000001",
            identity=_identity(),
            submit=submit,
        )

    assert submitted is False
