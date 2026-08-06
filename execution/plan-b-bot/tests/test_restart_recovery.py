import pytest

from beta_bot.order_identity import build_order_identity
from beta_bot.order_ledger import LedgerIntent, OrderLedger
from beta_bot.restart_recovery import (
    OPEN_ORDER_RECOVERED,
    PARTIAL_FILL_RECOVERED,
    STALE_POSITION_OVERRIDDEN,
    UNKNOWN_SUBMIT_BLOCKED,
    UNKNOWN_SUBMIT_RECOVERED,
    recover_cold_start,
)


NOW = 1_785_974_402_000


def _identity():
    return build_order_identity(
        release_id="candidate-p1-7",
        decision_timestamp_ms=1_785_974_400_000,
        asset="BTC",
        side="buy",
        intent="increase",
        target_revision="target_qty:0.25000",
    )


def _intent():
    return LedgerIntent(
        identity=_identity(),
        route_action="increase",
        submitted_quantity=0.25,
        submitted_order_parameters={
            "method": "market_open",
            "coin": "BTC",
            "size": 0.25,
            "position_before_qty": 0.0,
            "target_position_qty": 0.25,
            "position_tracking_source": "pre_trade_exchange_position",
        },
    )


def _order(status="open", remaining="0.25", oid=123):
    return {
        "status": "order",
        "order": {
            "order": {
                "coin": "BTC",
                "oid": oid,
                "sz": remaining,
                "origSz": "0.25",
            },
            "status": status,
            "statusTimestamp": NOW - 500,
        },
    }


def _fill(qty="0.10", tid=9001, oid=123):
    return {
        "coin": "BTC",
        "oid": oid,
        "tid": tid,
        "px": "100000",
        "sz": qty,
        "fee": "0.10",
        "feeToken": "USDC",
        "side": "B",
        "time": NOW - 750,
    }


def _state(position):
    positions = []
    if abs(position) > 1e-12:
        positions = [{"position": {"coin": "BTC", "szi": str(position)}}]
    return {
        "marginSummary": {"accountValue": "2000", "totalMarginUsed": "100"},
        "assetPositions": positions,
    }


def _attempted_ledger(path):
    ledger = OrderLedger(str(path))
    ledger.record_intent(_intent())
    ledger.record_submission_attempt(_identity().cloid, NOW - 2_000)
    return ledger


def test_cold_restart_with_open_order_recovers_and_is_idempotently_blocked(tmp_path):
    path = tmp_path / "orders.sqlite3"
    _attempted_ledger(path)

    restarted = OrderLedger(str(path))
    first = recover_cold_start(
        ledger=restarted,
        coin="BTC",
        user_state=_state(0.0),
        query_order_status=lambda _cloid: _order(status="open", remaining="0.25"),
        fetch_fills_by_time=lambda _start, _end: [],
        now_ms=NOW,
    )
    assert OPEN_ORDER_RECOVERED in first.recovery_cases
    assert first.blocking_unresolved_after == 1
    assert first.risk_increase_allowed is False
    assert restarted.get_order(_identity().cloid)["exchange_oid"] == "123"

    second = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.0),
        query_order_status=lambda _cloid: _order(status="open", remaining="0.25"),
        fetch_fills_by_time=lambda _start, _end: [],
        now_ms=NOW + 1_000,
    )
    assert second.recovery_cases == first.recovery_cases
    assert second.blocking_unresolved_after == 1
    assert len(OrderLedger(str(path)).list_fill_events(_identity().cloid)) == 0


def test_cold_restart_with_partial_fill_recovers_fill_and_resting_remainder(tmp_path):
    path = tmp_path / "orders.sqlite3"
    _attempted_ledger(path)

    first = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.10),
        query_order_status=lambda _cloid: _order(status="open", remaining="0.15"),
        fetch_fills_by_time=lambda _start, _end: [_fill(qty="0.10")],
        now_ms=NOW,
    )
    row = OrderLedger(str(path)).get_order(_identity().cloid)
    assert PARTIAL_FILL_RECOVERED in first.recovery_cases
    assert row["fill_quantity"] == pytest.approx(0.10)
    assert row["remaining_quantity"] == pytest.approx(0.15)
    assert first.actual_position_qty == pytest.approx(0.10)
    assert first.blocking_unresolved_after == 1

    second = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.10),
        query_order_status=lambda _cloid: _order(status="open", remaining="0.15"),
        fetch_fills_by_time=lambda _start, _end: [_fill(qty="0.10")],
        now_ms=NOW + 1_000,
    )
    assert PARTIAL_FILL_RECOVERED in second.recovery_cases
    assert len(OrderLedger(str(path)).list_fill_events(_identity().cloid)) == 1


def test_cold_restart_after_unknown_submit_recovers_when_cloid_becomes_known(tmp_path):
    path = tmp_path / "orders.sqlite3"
    ledger = _attempted_ledger(path)
    ledger.record_submission_unknown(_identity().cloid, TimeoutError("network timeout"))

    report = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.0),
        query_order_status=lambda _cloid: _order(status="open", remaining="0.25", oid=777),
        fetch_fills_by_time=lambda _start, _end: [],
        now_ms=NOW,
    )
    row = OrderLedger(str(path)).get_order(_identity().cloid)
    assert UNKNOWN_SUBMIT_RECOVERED in report.recovery_cases
    assert UNKNOWN_SUBMIT_BLOCKED not in report.recovery_cases
    assert row["exchange_oid"] == "777"
    assert report.blocking_unresolved_after == 1


def test_cold_restart_after_unknown_submit_stays_blocked_without_blind_retry(tmp_path):
    path = tmp_path / "orders.sqlite3"
    ledger = _attempted_ledger(path)
    ledger.record_submission_unknown(_identity().cloid, TimeoutError("network timeout"))
    lookups = []

    def lookup(cloid):
        lookups.append(cloid)
        return {"status": "unknownOid"}

    first = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.0),
        query_order_status=lookup,
        fetch_fills_by_time=lambda _start, _end: [],
        now_ms=NOW,
    )
    second = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.0),
        query_order_status=lookup,
        fetch_fills_by_time=lambda _start, _end: [],
        now_ms=NOW + 1_000,
    )
    assert UNKNOWN_SUBMIT_BLOCKED in first.recovery_cases
    assert UNKNOWN_SUBMIT_BLOCKED in second.recovery_cases
    assert first.risk_increase_allowed is False
    assert second.risk_increase_allowed is False
    assert len(lookups) == 2
    row = OrderLedger(str(path)).get_order(_identity().cloid)
    assert row["exchange_oid"] is None
    assert row["terminal_status"] is None


def test_cold_restart_fresh_position_overrides_stale_local_expectation(tmp_path):
    path = tmp_path / "orders.sqlite3"
    ledger = _attempted_ledger(path)
    ledger.apply_exchange_truth(
        _identity().cloid,
        _order(status="filled", remaining="0", oid=123),
        [_fill(qty="0.25", tid=9002)],
        reconciled_at_ms=NOW - 1_000,
    )

    report = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.40),
        query_order_status=lambda _cloid: (_ for _ in ()).throw(
            AssertionError("terminal order should not be queried on restart")
        ),
        fetch_fills_by_time=lambda _start, _end: (_ for _ in ()).throw(
            AssertionError("terminal order should not fetch fills")
        ),
        now_ms=NOW,
    )
    assert STALE_POSITION_OVERRIDDEN in report.recovery_cases
    assert report.local_position_expectation_qty == pytest.approx(0.25)
    assert report.actual_position_qty == pytest.approx(0.40)
    assert report.position_truth_source == "fresh_clearinghouse_state"
    assert report.risk_increase_allowed is True
    assert report.blocking_unresolved_after == 0

    again = recover_cold_start(
        ledger=OrderLedger(str(path)),
        coin="BTC",
        user_state=_state(0.40),
        query_order_status=lambda _cloid: {"status": "unknownOid"},
        fetch_fills_by_time=lambda _start, _end: [],
        now_ms=NOW + 1_000,
    )
    assert again.recovery_cases == report.recovery_cases
