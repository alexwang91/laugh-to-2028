import pytest

from beta_bot.order_identity import build_order_identity
from beta_bot.order_ledger import (
    FILL_LIMIT,
    LedgerIntent,
    LedgerUncertainState,
    OrderLedger,
    reconcile_unresolved_orders,
)


def _identity(cloid: str | None = None):
    identity = build_order_identity(
        release_id="candidate-p1-2",
        decision_timestamp_ms=1_785_974_400_000,
        asset="BTC",
        side="buy",
        intent="increase",
        target_revision="target_qty:0.25000",
    )
    if cloid is None:
        return identity
    return type(identity)(
        schema_version=identity.schema_version,
        release_id=identity.release_id,
        decision_timestamp_ms=identity.decision_timestamp_ms,
        asset=identity.asset,
        side=identity.side,
        intent=identity.intent,
        target_revision=identity.target_revision,
        cloid=cloid,
    )


def _intent(cloid: str | None = None):
    return LedgerIntent(
        identity=_identity(cloid),
        route_action="increase",
        submitted_quantity=0.25,
        submitted_order_parameters={"method": "market_open", "coin": "BTC", "size": 0.25},
    )


def _order_response(status="filled", remaining="0.0", oid=123):
    return {
        "status": "order",
        "order": {
            "order": {"coin": "BTC", "oid": oid, "sz": remaining, "origSz": "0.25"},
            "status": status,
            "statusTimestamp": 1_785_974_401_000,
        },
    }


def _fill(tid=99, qty="0.25", px="100000", fee="0.50", oid=123):
    return {
        "coin": "BTC",
        "oid": oid,
        "tid": tid,
        "px": px,
        "sz": qty,
        "fee": fee,
        "feeToken": "USDC",
        "side": "B",
        "time": 1_785_974_400_500,
    }


def test_sqlite_ledger_survives_reopen_and_cloid_is_unique(tmp_path):
    path = tmp_path / "orders.sqlite3"
    ledger = OrderLedger(str(path))
    first = ledger.record_intent(_intent())
    assert first["cloid"] == _intent().identity.cloid

    reopened = OrderLedger(str(path))
    same = reopened.record_intent(_intent())
    assert same["created_at_ms"] == first["created_at_ms"]

    conflicting = LedgerIntent(
        identity=_identity(),
        route_action="increase",
        submitted_quantity=0.30,
        submitted_order_parameters={"method": "market_open", "coin": "BTC", "size": 0.30},
    )
    with pytest.raises(LedgerUncertainState, match="different economic intent"):
        reopened.record_intent(conflicting)
    history = reopened.list_status_history(_intent().identity.cloid)
    assert any(row["status"] == "cloid_uniqueness_conflict" for row in history)


def test_corrupt_database_fails_closed(tmp_path):
    path = tmp_path / "orders.sqlite3"
    path.write_bytes(b"not a sqlite database")
    with pytest.raises(Exception, match="ledger|SQLite|database"):
        OrderLedger(str(path))


def test_restart_reconciliation_recovers_order_fill_fee_and_terminal_truth(tmp_path):
    path = tmp_path / "orders.sqlite3"
    ledger = OrderLedger(str(path))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    ledger.record_submission_response(
        _intent().identity.cloid,
        {"status": "ok", "response": {"data": {"statuses": [{"filled": {"oid": 123}}]}}},
        "filled",
        exchange_oid=123,
    )

    restarted = OrderLedger(str(path))
    result = reconcile_unresolved_orders(
        restarted,
        query_order_status=lambda _cloid: _order_response(),
        fetch_fills_by_time=lambda _start, _end: [_fill()],
        now_ms=1_785_974_402_000,
    )
    assert result["reconciled"] == 1
    assert result["unresolved_after"] == 0
    row = restarted.get_order(_intent().identity.cloid)
    assert row["exchange_oid"] == "123"
    assert row["fill_quantity"] == pytest.approx(0.25)
    assert row["average_fill_price"] == pytest.approx(100000.0)
    assert row["fees"] == pytest.approx(0.50)
    assert row["remaining_quantity"] == pytest.approx(0.0)
    assert row["terminal_status"] == "filled"
    assert row["last_reconciliation_timestamp_ms"] == 1_785_974_402_000

    again = reconcile_unresolved_orders(
        restarted,
        query_order_status=lambda _cloid: _order_response(),
        fetch_fills_by_time=lambda _start, _end: [_fill()],
        now_ms=1_785_974_403_000,
    )
    assert again["unresolved_before"] == 0
    assert len(restarted.list_fill_events(_intent().identity.cloid)) == 1


def test_unknown_oid_after_durable_attempt_never_retries_blindly(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    with pytest.raises(LedgerUncertainState, match="blind retry is forbidden"):
        reconcile_unresolved_orders(
            ledger,
            query_order_status=lambda _cloid: {"status": "unknownOid"},
            fetch_fills_by_time=lambda _start, _end: [],
        )
    row = ledger.get_order(_intent().identity.cloid)
    assert row["terminal_status"] is None
    assert row["current_status"] == "reconciliation_uncertain"


def test_intent_only_restart_is_safe_to_replay_because_no_attempt_was_persisted(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    result = reconcile_unresolved_orders(
        ledger,
        query_order_status=lambda _cloid: {"status": "unknownOid"},
        fetch_fills_by_time=lambda _start, _end: [],
    )
    assert result["unresolved_after"] == 1
    assert result["blocking_unresolved_after"] == 0
    assert ledger.get_order(_intent().identity.cloid)["submission_attempt_timestamp_ms"] is None


def test_recovered_exchange_open_order_blocks_even_without_local_attempt(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    result = reconcile_unresolved_orders(
        ledger,
        query_order_status=lambda _cloid: _order_response(status="open", remaining="0.25"),
        fetch_fills_by_time=lambda _start, _end: [],
    )
    row = ledger.get_order(_intent().identity.cloid)
    assert row["submission_attempt_timestamp_ms"] is None
    assert row["exchange_oid"] == "123"
    assert row["terminal_status"] is None
    assert result["blocking_unresolved_after"] == 1


def test_filled_without_complete_fill_evidence_stays_unresolved(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    with pytest.raises(LedgerUncertainState, match="fill_events_are_incomplete"):
        reconcile_unresolved_orders(
            ledger,
            query_order_status=lambda _cloid: _order_response(),
            fetch_fills_by_time=lambda _start, _end: [],
        )
    row = ledger.get_order(_intent().identity.cloid)
    assert row["last_exchange_status"] == "filled"
    assert row["terminal_status"] is None
    assert row["current_status"] == "reconciliation_uncertain"
    history = ledger.list_status_history(_intent().identity.cloid)
    assert any(
        "exchange_truth_apply_failed" in row["detail_json"]
        for row in history
        if row["status"] == "reconciliation_uncertain"
    )


def test_exchange_truth_overrides_conflicting_submission_status_with_audit(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    ledger.record_submission_response(
        _intent().identity.cloid, {"status": "ok"}, "filled", exchange_oid=123
    )

    canceled = _order_response(status="canceled", remaining="0.25")
    result = reconcile_unresolved_orders(
        ledger,
        query_order_status=lambda _cloid: canceled,
        fetch_fills_by_time=lambda _start, _end: [],
    )
    assert result["unresolved_after"] == 0
    row = ledger.get_order(_intent().identity.cloid)
    assert row["terminal_status"] == "canceled"
    assert row["cancel_reason"] == "exchange_status:canceled"
    history = ledger.list_status_history(_intent().identity.cloid)
    assert any(row["status"] == "exchange_state_conflict" for row in history)


def test_order_status_lookup_failure_leaves_structured_uncertainty_audit(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())

    def fail_lookup(_cloid):
        raise TimeoutError("info endpoint timed out")

    with pytest.raises(LedgerUncertainState, match="orderStatus lookup failed"):
        reconcile_unresolved_orders(
            ledger,
            query_order_status=fail_lookup,
            fetch_fills_by_time=lambda _start, _end: [],
        )
    row = ledger.get_order(_intent().identity.cloid)
    assert row["current_status"] == "reconciliation_uncertain"
    history = ledger.list_status_history(_intent().identity.cloid)
    assert any(
        "order_status_lookup_failed" in item["detail_json"]
        for item in history
        if item["status"] == "reconciliation_uncertain"
    )


def test_malformed_fill_lookup_leaves_structured_uncertainty_audit(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    with pytest.raises(LedgerUncertainState, match="Malformed userFillsByTime response"):
        reconcile_unresolved_orders(
            ledger,
            query_order_status=lambda _cloid: _order_response(status="open", remaining="0.25"),
            fetch_fills_by_time=lambda _start, _end: {"unexpected": True},
        )
    history = ledger.list_status_history(_intent().identity.cloid)
    assert any(
        "malformed_fill_lookup_response" in item["detail_json"]
        for item in history
        if item["status"] == "reconciliation_uncertain"
    )


def test_unknown_exchange_status_is_uncertain_and_audited(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    with pytest.raises(LedgerUncertainState, match="Unknown Hyperliquid order status"):
        reconcile_unresolved_orders(
            ledger,
            query_order_status=lambda _cloid: _order_response(
                status="new-undocumented-state", remaining="0.25"
            ),
            fetch_fills_by_time=lambda _start, _end: [],
        )
    assert ledger.get_order(_intent().identity.cloid)["current_status"] == "reconciliation_uncertain"


def test_fill_api_limit_is_uncertain_not_silently_complete(tmp_path):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_intent().identity.cloid, 1_785_974_400_100)
    fills = [_fill(tid=i, qty="0.000125") for i in range(FILL_LIMIT)]
    with pytest.raises(LedgerUncertainState, match="reaching the API limit"):
        reconcile_unresolved_orders(
            ledger,
            query_order_status=lambda _cloid: _order_response(),
            fetch_fills_by_time=lambda _start, _end: fills,
        )
    assert ledger.get_order(_intent().identity.cloid)["terminal_status"] is None
