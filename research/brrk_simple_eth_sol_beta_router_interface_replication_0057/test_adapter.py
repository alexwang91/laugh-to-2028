from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from research.brrk_simple_eth_sol_beta_router_interface_replication_0057 import adapter


class InterfaceAdapterContractTests(unittest.TestCase):
    @staticmethod
    def _frames(n: int = 80, start: str = "2020-01-01") -> dict[str, pd.DataFrame]:
        index = pd.date_range(start, periods=n, freq="D")
        t = np.arange(n, dtype=float)
        return {
            "ETH": pd.DataFrame({"close": np.exp(4.0 + 0.001 * t)}, index=index),
            "SOL": pd.DataFrame({"close": np.exp(4.3 + 0.0013 * t + 0.01 * np.sin(t / 7.0))}, index=index),
        }

    @staticmethod
    def _frozen_synthetic_frames() -> dict[str, pd.DataFrame]:
        index = pd.date_range("2020-08-11", "2026-08-02", freq="D")
        t = np.arange(len(index), dtype=float)
        eth_log = 4.5 + 0.00045 * t + 0.025 * np.sin(t / 47.0) + 0.011 * np.cos(t / 13.0)
        rel_step = 0.00006 + 0.0012 * np.sin(t / 37.0) + 0.00055 * np.cos(t / 19.0)
        z = 0.4 + np.cumsum(rel_step)
        sol_log = eth_log + z
        return {
            "ETH": pd.DataFrame({"close": np.exp(eth_log)}, index=index),
            "SOL": pd.DataFrame({"close": np.exp(sol_log)}, index=index),
        }

    def test_adapter_localizes_only_and_preserves_source(self) -> None:
        source = self._frames()
        source_indexes = {a: source[a].index.copy() for a in adapter.ASSETS}
        source_close = {a: source[a]["close"].to_numpy(copy=True) for a in adapter.ASSETS}
        out = adapter.adapt_source_frames(source)
        for asset in adapter.ASSETS:
            self.assertIsNone(source[asset].index.tz)
            self.assertTrue(source[asset].index.equals(source_indexes[asset]))
            np.testing.assert_array_equal(source[asset]["close"].to_numpy(), source_close[asset])
            self.assertEqual(str(out[asset].index.tz), "UTC")
            self.assertTrue(out[asset].index.tz_localize(None).equals(source_indexes[asset]))
            np.testing.assert_array_equal(out[asset]["close"].to_numpy(), source_close[asset])
            self.assertIsNot(out[asset], source[asset])

    def test_rejects_tz_aware_source(self) -> None:
        frames = self._frames()
        for asset in adapter.ASSETS:
            frames[asset].index = frames[asset].index.tz_localize("UTC")
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.adapt_source_frames(frames)

    def test_rejects_mismatched_indexes(self) -> None:
        frames = self._frames()
        frames["SOL"] = frames["SOL"].iloc[1:].copy()
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.adapt_source_frames(frames)

    def test_rejects_duplicate_and_non_midnight_indexes(self) -> None:
        duplicate = self._frames()
        idx = duplicate["ETH"].index.to_list()
        idx[2] = idx[1]
        duplicate["ETH"].index = pd.DatetimeIndex(idx)
        duplicate["SOL"].index = pd.DatetimeIndex(idx)
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.adapt_source_frames(duplicate)

        intraday = self._frames()
        shifted = intraday["ETH"].index + pd.Timedelta(hours=1)
        intraday["ETH"].index = shifted
        intraday["SOL"].index = shifted
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.adapt_source_frames(intraday)

    def test_rejects_bad_assets_and_prices(self) -> None:
        frames = self._frames()
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.adapt_source_frames({"ETH": frames["ETH"]})
        frames = self._frames()
        frames["SOL"].iloc[3, 0] = 0.0
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.adapt_source_frames(frames)

    def test_wrong_payload_identity_fails_before_delegate(self) -> None:
        with self.assertRaises(adapter.InterfaceAdapterError):
            adapter.evaluate_frozen_contract(self._frames(), "0" * 64)

    def test_full_synthetic_frozen_contract_delegates_without_scientific_authority(self) -> None:
        result = adapter.evaluate_frozen_contract(
            self._frozen_synthetic_frames(),
            adapter.EXPECTED_PAYLOAD_SHA256,
        )
        self.assertEqual(result["research_id"], adapter.RESEARCH_ID)
        self.assertEqual(result["actual_variants_evaluated"], 1)
        self.assertIn(result["classification"], adapter.frozen_0056_engine.ALLOWED_CLASSIFICATIONS)
        self.assertEqual(
            result["delegated_scientific_engine"]["git_blob_sha"],
            adapter.BOUND_0056_ENGINE_BLOB_SHA,
        )
        self.assertFalse(result["delegated_scientific_engine"]["portfolio_outputs_modified_by_0057_adapter"])
        self.assertFalse(result["source_interface_adapter"]["calendar_order_rowcount_close_values_changed"])
        self.assertEqual(len(result["targets"]), 2122)


if __name__ == "__main__":
    unittest.main()
