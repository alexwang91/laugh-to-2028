import unittest

import numpy as np
import pandas as pd

from run_crossvenue_funding_audit import (
    build_paired,
    comparison_metrics,
    compound_rates,
    to_blocks,
)


class CrossVenueFundingAuditTests(unittest.TestCase):
    def test_hourly_events_are_aggregated_into_utc_eight_hour_blocks(self):
        timestamps = pd.to_datetime([
            "2026-01-01 00:00:00Z",
            "2026-01-01 01:00:00Z",
            "2026-01-01 07:00:00Z",
            "2026-01-01 08:00:00Z",
        ])
        events = pd.DataFrame({
            "asset": ["BTC"] * 4,
            "venue": ["hyperliquid"] * 4,
            "timestamp": timestamps,
            "rate": [0.01, 0.02, -0.01, 0.03],
        })
        blocks = to_blocks(events)
        first = blocks.iloc[0]
        second = blocks.iloc[1]
        self.assertEqual(first["event_count"], 3)
        self.assertAlmostEqual(first["additive_rate"], 0.02)
        self.assertAlmostEqual(first["compounded_rate"], (1.01 * 1.02 * 0.99) - 1.0)
        self.assertEqual(second["event_count"], 1)
        self.assertAlmostEqual(second["additive_rate"], 0.03)

    def test_paired_blocks_use_intersection_only(self):
        event_time = pd.Timestamp("2026-01-01 00:00:00", tz="UTC")
        blocks = pd.DataFrame({
            "asset": ["BTC", "BTC", "BTC"],
            "venue": ["binance", "hyperliquid", "binance"],
            "block": pd.to_datetime([
                "2026-01-01 00:00:00Z",
                "2026-01-01 00:00:00Z",
                "2026-01-01 08:00:00Z",
            ]),
            "additive_rate": [0.01, 0.02, 0.03],
            "compounded_rate": [0.01, 0.02, 0.03],
            "event_count": [1, 3, 1],
            "first_event": [event_time] * 3,
            "last_event": [event_time] * 3,
        })
        paired = build_paired(blocks)
        self.assertEqual(len(paired), 1)
        self.assertAlmostEqual(paired.iloc[0]["binance_additive"], 0.01)
        self.assertAlmostEqual(paired.iloc[0]["hyperliquid_additive"], 0.02)

    def test_metrics_sign_and_bias(self):
        frame = pd.DataFrame({
            "binance_additive": [0.01, -0.02, 0.03],
            "hyperliquid_additive": [0.02, -0.01, 0.04],
            "binance_compounded": [0.01, -0.02, 0.03],
            "hyperliquid_compounded": [0.02, -0.01, 0.04],
        })
        metrics = comparison_metrics(frame)
        self.assertEqual(metrics["paired_blocks"], 3)
        self.assertAlmostEqual(metrics["sign_agreement"], 1.0)
        self.assertAlmostEqual(metrics["mean_bias_hl_minus_binance"], 0.01)
        self.assertGreater(metrics["pearson"], 0.9)

    def test_compound_rates(self):
        self.assertAlmostEqual(
            compound_rates(pd.Series([0.01, -0.02])),
            1.01 * 0.98 - 1.0,
        )


if __name__ == "__main__":
    unittest.main()
