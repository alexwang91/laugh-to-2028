import unittest

import numpy as np
import pandas as pd

from run_frozen_holdings_funding_pnl import (
    combine_price_and_funding,
    funding_accounting,
    metrics,
)


class FrozenHoldingsFundingPnlTests(unittest.TestCase):
    def test_positive_rate_costs_long_and_negative_rate_pays_long(self):
        weights = pd.DataFrame(
            {"BTC": [0.5], "ETH": [0.0], "SOL": [0.0], "BNB": [0.0], "XRP": [0.0]},
            index=pd.to_datetime(["2026-01-01"]),
        )
        positive = pd.DataFrame({
            "asset": ["BTC", "ETH", "SOL", "BNB", "XRP"],
            "block": pd.to_datetime(["2026-01-01 00:00:00Z"] * 5),
            "additive_rate": [0.01, 0.0, 0.0, 0.0, 0.0],
        })
        negative = positive.copy()
        negative["additive_rate"] = [-0.01, 0.0, 0.0, 0.0, 0.0]

        positive_result = funding_accounting(positive, weights, "additive_rate", "positive")
        negative_result = funding_accounting(negative, weights, "additive_rate", "negative")

        self.assertAlmostEqual(float(positive_result["block_return"].iloc[0]), -0.005)
        self.assertAlmostEqual(float(negative_result["block_return"].iloc[0]), 0.005)

    def test_daily_funding_factor_compounds_blocks(self):
        weights = pd.DataFrame(
            {"BTC": [1.0], "ETH": [0.0], "SOL": [0.0], "BNB": [0.0], "XRP": [0.0]},
            index=pd.to_datetime(["2026-01-01"]),
        )
        rows = []
        for block_time, rate in [
            ("2026-01-01 00:00:00Z", 0.01),
            ("2026-01-01 08:00:00Z", 0.02),
        ]:
            for asset in ["BTC", "ETH", "SOL", "BNB", "XRP"]:
                rows.append({
                    "asset": asset,
                    "block": pd.Timestamp(block_time),
                    "additive_rate": rate if asset == "BTC" else 0.0,
                })
        result = funding_accounting(pd.DataFrame(rows), weights, "additive_rate", "compound")
        expected = (1.0 - 0.01) * (1.0 - 0.02)
        self.assertAlmostEqual(float(result["daily_factor"].iloc[0]), expected)

    def test_price_and_funding_are_combined_multiplicatively(self):
        dates = pd.to_datetime(["2026-01-01", "2026-01-02"])
        price = pd.Series([0.10, -0.05], index=dates)
        factor = pd.Series([0.99, 1.01], index=dates)
        combined = combine_price_and_funding(price, factor)
        self.assertAlmostEqual(float(combined.iloc[0]), 1.10 * 0.99 - 1.0)
        self.assertAlmostEqual(float(combined.iloc[1]), 0.95 * 1.01 - 1.0)

    def test_zero_exposure_has_zero_funding_effect(self):
        weights = pd.DataFrame(
            np.zeros((1, 5)),
            columns=["BTC", "ETH", "SOL", "BNB", "XRP"],
            index=pd.to_datetime(["2026-01-01"]),
        )
        blocks = pd.DataFrame({
            "asset": ["BTC", "ETH", "SOL", "BNB", "XRP"],
            "block": pd.to_datetime(["2026-01-01 00:00:00Z"] * 5),
            "additive_rate": [0.01, -0.02, 0.03, -0.04, 0.05],
        })
        result = funding_accounting(blocks, weights, "additive_rate", "zero")
        self.assertAlmostEqual(float(result["daily_factor"].iloc[0]), 1.0)
        self.assertAlmostEqual(float(result["daily_additive"].iloc[0]), 0.0)

    def test_metrics_use_full_return_path(self):
        returns = pd.Series(
            [0.10, -0.05, 0.02],
            index=pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
        )
        result = metrics(returns)
        self.assertAlmostEqual(result["final_multiple"], 1.10 * 0.95 * 1.02)
        self.assertLess(result["max_drawdown"], 0.0)


if __name__ == "__main__":
    unittest.main()
