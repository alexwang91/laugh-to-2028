import pytest

from beta_bot.account_reconciliation import (
    AccountReconciliationError,
    build_account_reconciliation,
    transition_increases_directional_risk,
)


class FakeLedger:
    def __init__(self, rows=None):
        self.rows = rows or []

    def unresolved_orders(self):
        return list(self.rows)


def _state(position="0.25", equity="2000", margin="100"):
    positions = []
    if position is not None:
        positions = [{"position": {"coin": "BTC", "szi": position}}]
    return {
        "marginSummary": {
            "accountValue": equity,
            "totalMarginUsed": margin,
        },
        "assetPositions": positions,
    }


def _fill():
    return {"coin": "BTC", "oid": 101, "tid": 5001, "sz": "0.1", "px": "60000"}


def _active_local(cloid="0xabc"):
    return {
        "cloid": cloid,
        "asset": "BTC",
        "last_exchange_status": "open",
    }


def test_clean_account_reconciliation_allows_risk_increase():
    report = build_account_reconciliation(
        ledger=FakeLedger([_active_local()]),
        coin="BTC",
        target_position_qty=0.4,
        open_orders=[{"coin": "BTC", "cloid": "0xabc", "oid": 101}],
        fills=[_fill()],
        user_state=_state(),
    )
    assert report.is_clean is True
    assert report.risk_increase_allowed is True
    assert report.actual_position_qty == 0.25
    assert report.target_gap_qty == pytest.approx(0.15)
    assert report.account_equity_usd == 2000.0
    assert report.total_margin_used_usd == 100.0
    assert report.recent_fill_count == 1


def test_exchange_open_order_without_local_active_truth_blocks_risk_increase():
    report = build_account_reconciliation(
        ledger=FakeLedger(),
        coin="BTC",
        target_position_qty=0.4,
        open_orders=[{"coin": "BTC", "cloid": "0xunknown", "oid": 101}],
        fills=[],
        user_state=_state(),
    )
    assert report.risk_increase_allowed is False
    assert "EXCHANGE_OPEN_ORDER_NOT_IN_LOCAL_ACTIVE_LEDGER" in report.blocking_reasons


def test_local_active_order_missing_at_exchange_blocks_risk_increase():
    report = build_account_reconciliation(
        ledger=FakeLedger([_active_local()]),
        coin="BTC",
        target_position_qty=0.4,
        open_orders=[],
        fills=[],
        user_state=_state(),
    )
    assert report.risk_increase_allowed is False
    assert "LOCAL_ACTIVE_ORDER_NOT_OPEN_AT_EXCHANGE" in report.blocking_reasons


def test_persistent_unresolved_truth_is_carried_into_account_gate():
    report = build_account_reconciliation(
        ledger=FakeLedger(),
        coin="BTC",
        target_position_qty=0.4,
        open_orders=[],
        fills=[],
        user_state=_state(),
        persistent_blocking_unresolved=1,
    )
    assert "PERSISTENT_ORDER_RECONCILIATION_UNRESOLVED" in report.blocking_reasons
    assert report.risk_increase_allowed is False


@pytest.mark.parametrize(
    ("current_qty", "target_qty", "expected"),
    [
        (0.25, 0.4, True),
        (0.25, 0.1, False),
        (0.25, 0.0, False),
        (0.25, -0.1, True),
        (0.0, 0.1, True),
        (-0.5, -0.2, False),
        (-0.2, -0.5, True),
    ],
)
def test_directional_risk_classifier(current_qty, target_qty, expected):
    assert transition_increases_directional_risk(current_qty, target_qty) is expected


def test_open_order_without_cloid_becomes_blocking_reason_not_global_failure():
    report = build_account_reconciliation(
        ledger=FakeLedger(),
        coin="BTC",
        target_position_qty=0.1,
        open_orders=[{"coin": "BTC", "oid": 101}],
        fills=[],
        user_state=_state(),
    )
    assert report.risk_increase_allowed is False
    assert "EXCHANGE_OPEN_ORDER_UNCORRELATABLE" in report.blocking_reasons
    assert transition_increases_directional_risk(report.actual_position_qty, 0.1) is False


def test_fill_without_oid_or_tid_becomes_blocking_reason_not_global_failure():
    report = build_account_reconciliation(
        ledger=FakeLedger(),
        coin="BTC",
        target_position_qty=0.1,
        open_orders=[],
        fills=[{"coin": "BTC", "oid": 101}],
        user_state=_state(),
    )
    assert report.risk_increase_allowed is False
    assert report.recent_fill_count == 1
    assert "RECENT_FILL_UNCORRELATABLE" in report.blocking_reasons


def test_malformed_open_order_and_fill_rows_are_auditable_blockers():
    report = build_account_reconciliation(
        ledger=FakeLedger(),
        coin="BTC",
        target_position_qty=0.0,
        open_orders=[None],
        fills=[None],
        user_state=_state(),
    )
    assert report.risk_increase_allowed is False
    assert "EXCHANGE_OPEN_ORDER_UNAUDITABLE" in report.blocking_reasons
    assert "RECENT_FILL_UNAUDITABLE" in report.blocking_reasons


def test_missing_margin_truth_fails_closed():
    with pytest.raises(AccountReconciliationError, match="margin summary"):
        build_account_reconciliation(
            ledger=FakeLedger(),
            coin="BTC",
            target_position_qty=0.0,
            open_orders=[],
            fills=[],
            user_state={"assetPositions": []},
        )
