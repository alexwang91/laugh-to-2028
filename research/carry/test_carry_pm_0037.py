import json
import unittest
from unittest.mock import patch

import requests

from run_carry_pm_0037 import (
    OUTCOME_CONSUMES,
    OUTCOME_INCONCLUSIVE,
    OUTCOME_RELEASES,
    compare_snapshots,
    post_info,
)


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = {} if payload is None else payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def json(self):
        return self._payload


def snapshot(
    label,
    *,
    observed_at,
    ubtc_qty,
    ubtc_mid=64000.0,
    perp_mid=64000.0,
    short_notional=0.0,
    short_szi=0.0,
    available=500.0,
    pm_ratio=0.10,
):
    spot_notional = ubtc_qty * ubtc_mid
    mismatch = None
    if spot_notional > 0 and short_notional > 0:
        mismatch = abs(spot_notional - short_notional) / max(spot_notional, short_notional)
    return {
        "label": label,
        "observed_at_utc": observed_at,
        "read_only": True,
        "account_fingerprint": "abc123",
        "user_abstraction": "portfolioMargin",
        "spot": {
            "portfolioMarginEnabled": True,
            "portfolioMarginRatio": pm_ratio,
            "tokenToAvailableAfterMaintenance": {"0": available},
            "ubtc": {"total": ubtc_qty},
        },
        "borrow_lend": {"total_borrow_value": 0.0, "health": "healthy", "healthFactor": None},
        "perp": {"btc_position": {"szi": short_szi}, "other_positions": []},
        "market": {"ubtc_spot_mid": ubtc_mid, "btc_perp_mid": perp_mid},
        "derived": {
            "ubtc_spot_notional": spot_notional,
            "btc_short_notional": short_notional,
            "match_mismatch_fraction": mismatch,
            "has_ubtc_spot": ubtc_qty > 0,
            "has_btc_short": short_szi < 0,
            "has_other_perp_positions": False,
        },
    }


def clean_four(*, matched_available, matched_mid=64010.0, matched_time="2026-08-05T10:01:00+00:00"):
    cash = snapshot(
        "cash",
        observed_at="2026-08-05T09:59:00+00:00",
        ubtc_qty=0.0,
        available=500.0,
    )
    spot = snapshot(
        "spot",
        observed_at="2026-08-05T10:00:00+00:00",
        ubtc_qty=0.0075,
        ubtc_mid=64000.0,
        perp_mid=64000.0,
        available=400.0,
    )
    matched = snapshot(
        "matched",
        observed_at=matched_time,
        ubtc_qty=0.0075,
        ubtc_mid=matched_mid,
        perp_mid=matched_mid,
        short_notional=480.0,
        short_szi=-0.0075,
        available=matched_available,
        pm_ratio=0.10,
    )
    matched["derived"]["match_mismatch_fraction"] = abs(
        matched["derived"]["ubtc_spot_notional"] - 480.0
    ) / max(matched["derived"]["ubtc_spot_notional"], 480.0)
    closed = snapshot(
        "closed",
        observed_at="2026-08-05T10:02:00+00:00",
        ubtc_qty=0.0,
        available=499.0,
    )
    return cash, spot, matched, closed


class CarryPm0037Tests(unittest.TestCase):
    def test_negative_raw_change_is_explicit_margin_release(self):
        cash, spot, matched, closed = clean_four(matched_available=420.0)
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["outcome_state"], OUTCOME_RELEASES)
        self.assertEqual(out["measurements"]["raw_available_after_maintenance_change_usdc"], -20.0)
        self.assertEqual(out["measurements"]["released_margin_usdc"], 20.0)
        self.assertEqual(out["measurements"]["consumed_margin_usdc"], 0.0)
        self.assertTrue(out["checks"]["snapshot_gap_within_bound"])
        self.assertTrue(out["checks"]["mid_drift_within_bound"])
        self.assertEqual(out["status"], "PASS_PM_ACCOUNT_BEHAVIOR")

    def test_positive_raw_change_is_explicit_margin_consumption(self):
        cash, spot, matched, closed = clean_four(matched_available=380.0)
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["outcome_state"], OUTCOME_CONSUMES)
        self.assertEqual(out["measurements"]["consumed_margin_usdc"], 20.0)
        self.assertAlmostEqual(
            out["measurements"]["consumed_margin_fraction_of_short_notional"],
            20.0 / 480.0,
        )
        self.assertTrue(out["checks"]["capital_efficiency_gate"])
        self.assertEqual(out["status"], "PASS_PM_ACCOUNT_BEHAVIOR")

    def test_mid_drift_over_25bps_is_inconclusive_and_cannot_pass(self):
        cash, spot, matched, closed = clean_four(
            matched_available=420.0,
            matched_mid=64640.0,
        )
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["outcome_state"], OUTCOME_INCONCLUSIVE)
        self.assertFalse(out["checks"]["mid_drift_within_bound"])
        self.assertFalse(out["checks"]["measurement_outcome_conclusive"])
        self.assertEqual(out["status"], "FAIL_OR_INCONCLUSIVE_PM_ACCOUNT_BEHAVIOR")

    def test_snapshot_gap_over_300_seconds_is_inconclusive(self):
        cash, spot, matched, closed = clean_four(
            matched_available=420.0,
            matched_time="2026-08-05T10:06:00+00:00",
        )
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["outcome_state"], OUTCOME_INCONCLUSIVE)
        self.assertFalse(out["checks"]["snapshot_gap_within_bound"])
        self.assertEqual(out["status"], "FAIL_OR_INCONCLUSIVE_PM_ACCOUNT_BEHAVIOR")

    def test_exact_zero_raw_change_is_inconclusive_not_release(self):
        cash, spot, matched, closed = clean_four(matched_available=400.0)
        out = compare_snapshots(cash, spot, matched, closed)
        self.assertEqual(out["outcome_state"], OUTCOME_INCONCLUSIVE)
        self.assertIn("raw_available_change_exactly_zero", out["measurement_inconclusive_reasons"])
        self.assertFalse(out["checks"]["capital_efficiency_gate"])

    def test_bounded_retry_succeeds_after_retryable_responses(self):
        responses = [
            FakeResponse(500),
            FakeResponse(429),
            FakeResponse(200, {"ok": True}),
        ]
        with patch("run_carry_pm_0037.requests.post", side_effect=responses) as post, patch(
            "run_carry_pm_0037.time.sleep"
        ) as sleep:
            out = post_info({"type": "allMids"})
        self.assertEqual(out, {"ok": True})
        self.assertEqual(post.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.5, 1.0])

    def test_nonretryable_400_fails_immediately(self):
        with patch(
            "run_carry_pm_0037.requests.post", return_value=FakeResponse(400)
        ) as post, patch("run_carry_pm_0037.time.sleep") as sleep:
            with self.assertRaises(requests.HTTPError):
                post_info({"type": "allMids"})
        self.assertEqual(post.call_count, 1)
        sleep.assert_not_called()

    def test_report_contains_no_full_address_field(self):
        cash, spot, matched, closed = clean_four(matched_available=420.0)
        out = compare_snapshots(cash, spot, matched, closed)
        encoded = json.dumps(out)
        self.assertNotIn("0x1111111111111111111111111111111111111111", encoded)
        self.assertTrue(out["read_only"])
        self.assertIn("account_fingerprint", out)


if __name__ == "__main__":
    unittest.main()
