from hyperliquid.utils.types import Cloid

from beta_bot.order_identity import build_order_identity, canonical_target_revision
from beta_bot.service import DAY_MS, _canonical_decision_timestamp_ms


BASE = {
    "release_id": "release-2026-08-05",
    "decision_timestamp_ms": 1_785_974_400_000,
    "asset": "BTC",
    "side": "buy",
    "intent": "increase",
    "target_revision": "target_qty:0.12345",
}


def test_identity_has_stable_golden_cloid_across_replays_and_restarts():
    first = build_order_identity(**BASE)
    reconstructed = build_order_identity(**dict(BASE))

    assert first == reconstructed
    assert first.cloid == "0x8ddedcbc7bed81add8a8727030591033"
    assert len(first.cloid) == 34
    assert Cloid.from_str(first.cloid).to_raw() == first.cloid


def test_identity_changes_for_each_economic_identity_component():
    baseline = build_order_identity(**BASE).cloid

    changes = [
        {"release_id": "release-2026-08-06"},
        {"decision_timestamp_ms": BASE["decision_timestamp_ms"] + DAY_MS},
        {"asset": "ETH"},
        {"side": "sell"},
        {"intent": "reduce"},
        {"target_revision": "target_qty:0.12346"},
    ]

    for change in changes:
        candidate = dict(BASE)
        candidate.update(change)
        assert build_order_identity(**candidate).cloid != baseline


def test_reversal_legs_have_distinct_ids_for_same_target_revision():
    close_fields = dict(BASE, side="sell", intent="close_for_reversal", target_revision="target_qty:-0.10000")
    open_fields = dict(BASE, side="sell", intent="open_reversal", target_revision="target_qty:-0.10000")

    assert build_order_identity(**close_fields).cloid != build_order_identity(**open_fields).cloid


def test_target_revision_is_based_on_executable_target_not_float_noise():
    assert canonical_target_revision(1.234561) == "target_qty:1.23456"
    assert canonical_target_revision(1.234559) == "target_qty:1.23456"
    assert canonical_target_revision(-0.0) == "target_qty:0.00000"
    assert canonical_target_revision(-1.234561) == "target_qty:-1.23456"


def test_canonical_decision_timestamp_is_next_utc_daily_boundary():
    candle_start_ms = 1_785_888_000_000
    assert _canonical_decision_timestamp_ms(candle_start_ms) == candle_start_ms + DAY_MS
