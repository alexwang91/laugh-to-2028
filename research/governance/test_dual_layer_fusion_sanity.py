from __future__ import annotations

import math
import unittest

from research.governance.dual_layer_fusion_sanity import (
    DualLayerFusionError,
    apply_external_gross_cap,
    classify_external_state,
    relative_weights,
)


class DualLayerFusionSanityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.target = {"BTC": 0.30, "ETH": 0.25, "SOL": 0.15, "BNB": 0.10}

    def test_state_rule_is_fixed(self) -> None:
        self.assertEqual(classify_external_state(0.01, 0.02).state, "SUPPORTIVE")
        self.assertEqual(classify_external_state(-0.01, -0.02).state, "RESTRICTIVE")
        self.assertEqual(classify_external_state(0.01, -0.02).state, "NEUTRAL")
        self.assertEqual(classify_external_state(-0.01, 0.02).state, "NEUTRAL")

    def test_supportive_is_identity_at_gross_below_one(self) -> None:
        state = classify_external_state(0.01, 0.02)
        self.assertEqual(apply_external_gross_cap(self.target, state), self.target)

    def test_neutral_caps_gross_without_ranking_change(self) -> None:
        full = {"BTC": 0.40, "ETH": 0.30, "SOL": 0.20, "BNB": 0.10}
        state = classify_external_state(0.01, -0.02)
        fused = apply_external_gross_cap(full, state)
        self.assertTrue(math.isclose(sum(fused.values()), 0.8, abs_tol=1e-12))
        self.assertEqual(relative_weights(fused), relative_weights(full))

    def test_restrictive_caps_gross_without_ranking_change(self) -> None:
        full = {"BTC": 0.40, "ETH": 0.30, "SOL": 0.20, "BNB": 0.10}
        state = classify_external_state(-0.01, -0.02)
        fused = apply_external_gross_cap(full, state)
        self.assertTrue(math.isclose(sum(fused.values()), 0.6, abs_tol=1e-12))
        self.assertEqual(relative_weights(fused), relative_weights(full))

    def test_external_layer_never_increases_low_internal_gross(self) -> None:
        low = {"BTC": 0.20, "ETH": 0.10, "SOL": 0.05, "BNB": 0.05}
        restrictive = classify_external_state(-0.01, -0.02)
        self.assertEqual(apply_external_gross_cap(low, restrictive), low)

    def test_short_or_unknown_asset_fails_closed(self) -> None:
        restrictive = classify_external_state(-0.01, -0.02)
        with self.assertRaises(DualLayerFusionError):
            apply_external_gross_cap({"BTC": -0.1, "ETH": 0.2, "SOL": 0.1, "BNB": 0.1}, restrictive)
        with self.assertRaises(DualLayerFusionError):
            apply_external_gross_cap({"BTC": 0.1, "ETH": 0.2, "SOL": 0.1, "DOGE": 0.1}, restrictive)


if __name__ == "__main__":
    unittest.main()
