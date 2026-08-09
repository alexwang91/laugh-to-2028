from __future__ import annotations

import unittest

from research.governance.phase6_live_source_adapters import (
    HYPERLIQUID_FUNDING_SLOT_JITTER_TOLERANCE_MS,
    normalize_hyperliquid_funding_records,
)


HOUR_MS = 3_600_000


class Phase6LiveSourceAdapterTests(unittest.TestCase):
    def test_small_hyperliquid_transport_jitter_maps_to_exact_hour(self) -> None:
        slot = 1_786_280_400_000
        rows = [
            {"time": slot + 1, "fundingRate": "0.00001"},
            {"time": slot + 66, "fundingRate": "0.00002"},
        ]
        normalized = normalize_hyperliquid_funding_records(rows)
        self.assertEqual([row["time"] for row in normalized], [slot, slot])
        self.assertEqual(rows[0]["time"], slot + 1)

    def test_jitter_outside_one_second_fails_closed(self) -> None:
        slot = 1_786_280_400_000
        with self.assertRaises(Exception):
            normalize_hyperliquid_funding_records(
                [
                    {
                        "time": slot + HYPERLIQUID_FUNDING_SLOT_JITTER_TOLERANCE_MS + 1,
                        "fundingRate": "0.00001",
                    }
                ]
            )

    def test_nearest_hour_mapping_handles_small_early_jitter(self) -> None:
        slot = 1_786_280_400_000
        normalized = normalize_hyperliquid_funding_records(
            [{"time": slot - 25, "fundingRate": "0.00001"}]
        )
        self.assertEqual(normalized[0]["time"], slot)


if __name__ == "__main__":
    unittest.main()
