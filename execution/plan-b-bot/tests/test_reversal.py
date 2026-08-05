import pytest

from beta_bot.reversal import ReversalSafetyError, position_qty_from_user_state, verify_reversal_flat


def _state(qty: float):
    return {"assetPositions": [{"position": {"coin": "BTC", "szi": str(qty)}}]}


def test_position_qty_reads_exchange_state():
    assert position_qty_from_user_state(_state(0.25), "BTC") == 0.25
    assert position_qty_from_user_state({"assetPositions": []}, "BTC") == 0.0


def test_reversal_allows_open_only_after_fresh_flat():
    result = verify_reversal_flat(_state(0.0), coin="BTC", previous_position_qty=0.5)
    assert result.safe_to_open_new_direction is True
    assert result.observed_position_qty == 0.0


def test_partial_close_blocks_new_direction():
    with pytest.raises(ReversalSafetyError, match="close is incomplete"):
        verify_reversal_flat(_state(0.2), coin="BTC", previous_position_qty=0.5)


def test_unexpected_cross_through_flat_blocks_new_direction():
    with pytest.raises(ReversalSafetyError, match="already crossed through flat"):
        verify_reversal_flat(_state(-0.1), coin="BTC", previous_position_qty=0.5)


def test_short_to_long_partial_close_blocks():
    with pytest.raises(ReversalSafetyError, match="close is incomplete"):
        verify_reversal_flat(_state(-0.2), coin="BTC", previous_position_qty=-0.5)


def test_malformed_exchange_state_fails_closed():
    with pytest.raises(ReversalSafetyError, match="missing or malformed"):
        verify_reversal_flat({}, coin="BTC", previous_position_qty=0.5)
