import pytest

from beta_bot.fill_transition import FillTransitionError, build_fill_transition
from beta_bot.order_identity import build_order_identity
from beta_bot.order_ledger import LedgerIntent, OrderLedger


def _identity(*, side="buy", intent="increase"):
    return build_order_identity(
        release_id="candidate-p1-3",
        decision_timestamp_ms=1_785_974_400_000,
        asset="BTC",
        side=side,
        intent=intent,
        target_revision="target_qty:0.25000",
    )


def _intent(*, side="buy", before=0.0, target=0.25, quantity=0.25):
    return LedgerIntent(
        identity=_identity(side=side, intent="increase" if side == "buy" else "reduce"),
        route_action="increase" if side == "buy" else "reduce",
        submitted_quantity=quantity,
        submitted_order_parameters={
            "method": "market_open" if side == "buy" else "market_close",
            "coin": "BTC",
            "size": quantity,
            "position_before_qty": before,
            "target_position_qty": target,
            "position_tracking_source": "pre_trade_exchange_position",
        },
    )


def _order_response(*, status, remaining, orig="0.25", oid=123):
    return {
        "status": "order",
        "order": {
            "order": {"coin": "BTC", "oid": oid, "sz": remaining, "origSz": orig},
            "status": status,
            "statusTimestamp": 1_785_974_401_000,
        },
    }


def _fill(*, qty, side="B", oid=123, tid=99):
    return {
        "coin": "BTC",
        "oid": oid,
        "tid": tid,
        "px": "100000",
        "sz": qty,
        "fee": "0.25",
        "feeToken": "USDC",
        "side": side,
        "time": 1_785_974_400_500,
    }


def _reconciled_transition(tmp_path, *, intent, status, remaining, fills):
    ledger = OrderLedger(str(tmp_path / "orders.sqlite3"))
    ledger.record_intent(intent)
    row = ledger.apply_exchange_truth(
        intent.identity.cloid,
        _order_response(status=status, remaining=remaining),
        fills,
        reconciled_at_ms=1_785_974_402_000,
    )
    return build_fill_transition(row)


def test_zero_fill_keeps_actual_at_baseline_and_exposes_resting_remainder(tmp_path):
    transition = _reconciled_transition(
        tmp_path,
        intent=_intent(before=0.10, target=0.35),
        status="open",
        remaining="0.25",
        fills=[],
    )
    assert transition.fill_state == "zero_fill"
    assert transition.signed_fill_quantity == pytest.approx(0.0)
    assert transition.actual_position_qty_from_fills == pytest.approx(0.10)
    assert transition.target_gap_qty == pytest.approx(0.25)
    assert transition.resting_remaining_quantity == pytest.approx(0.25)
    assert transition.unfilled_quantity == pytest.approx(0.25)


def test_partial_fill_advances_position_only_by_actual_fill_and_keeps_gap_visible(tmp_path):
    transition = _reconciled_transition(
        tmp_path,
        intent=_intent(before=0.10, target=0.35),
        status="open",
        remaining="0.15",
        fills=[_fill(qty="0.10")],
    )
    assert transition.fill_state == "partial_fill"
    assert transition.fill_quantity == pytest.approx(0.10)
    assert transition.actual_position_qty_from_fills == pytest.approx(0.20)
    assert transition.target_gap_qty == pytest.approx(0.15)
    assert transition.resting_remaining_quantity == pytest.approx(0.15)
    assert transition.unfilled_quantity == pytest.approx(0.15)


def test_full_fill_reaches_target_without_using_requested_notional_as_truth(tmp_path):
    transition = _reconciled_transition(
        tmp_path,
        intent=_intent(before=0.10, target=0.35),
        status="filled",
        remaining="0.0",
        fills=[_fill(qty="0.25")],
    )
    assert transition.fill_state == "full_fill"
    assert transition.actual_position_qty_from_fills == pytest.approx(0.35)
    assert transition.target_gap_qty == pytest.approx(0.0)
    assert transition.resting_remaining_quantity == pytest.approx(0.0)
    assert transition.unfilled_quantity == pytest.approx(0.0)


def test_sell_fill_moves_position_negative_by_actual_fill(tmp_path):
    transition = _reconciled_transition(
        tmp_path,
        intent=_intent(side="sell", before=0.40, target=0.15),
        status="open",
        remaining="0.15",
        fills=[_fill(qty="0.10", side="A")],
    )
    assert transition.signed_fill_quantity == pytest.approx(-0.10)
    assert transition.actual_position_qty_from_fills == pytest.approx(0.30)
    assert transition.target_gap_qty == pytest.approx(-0.15)


def test_canceled_unfilled_quantity_is_not_reported_as_resting(tmp_path):
    transition = _reconciled_transition(
        tmp_path,
        intent=_intent(before=0.10, target=0.35),
        status="canceled",
        remaining="0.15",
        fills=[_fill(qty="0.10")],
    )
    assert transition.fill_state == "partial_fill"
    assert transition.exchange_remaining_quantity == pytest.approx(0.15)
    assert transition.resting_remaining_quantity == pytest.approx(0.0)
    assert transition.unfilled_quantity == pytest.approx(0.15)


def test_reversal_open_leg_can_expose_fill_truth_without_inventing_position_baseline():
    order = {
        "cloid": "0x" + "1" * 32,
        "asset": "BTC",
        "side": "sell",
        "economic_intent": "increase",
        "route_action": "open_reversal",
        "submitted_quantity": 0.25,
        "fill_quantity": 0.10,
        "remaining_quantity": 0.15,
        "last_exchange_status": "open",
        "terminal_status": None,
        "submitted_order_parameters_json": (
            '{"position_before_qty":null,"target_position_qty":-0.25,'
            '"position_tracking_source":"requires_p1_4_reversal_reconciliation"}'
        ),
    }
    transition = build_fill_transition(order)
    assert transition.fill_state == "partial_fill"
    assert transition.signed_fill_quantity == pytest.approx(-0.10)
    assert transition.position_tracking_status == "baseline_unavailable"
    assert transition.actual_position_qty_from_fills is None
    assert transition.target_gap_qty is None


def test_fill_larger_than_submitted_fails_closed():
    order = {
        "cloid": "0x" + "2" * 32,
        "asset": "BTC",
        "side": "buy",
        "economic_intent": "increase",
        "route_action": "increase",
        "submitted_quantity": 0.25,
        "fill_quantity": 0.30,
        "remaining_quantity": 0.0,
        "last_exchange_status": "filled",
        "terminal_status": "filled",
        "submitted_order_parameters_json": (
            '{"position_before_qty":0.0,"target_position_qty":0.25,'
            '"position_tracking_source":"pre_trade_exchange_position"}'
        ),
    }
    with pytest.raises(FillTransitionError, match="exceeds submitted_quantity"):
        build_fill_transition(order)
