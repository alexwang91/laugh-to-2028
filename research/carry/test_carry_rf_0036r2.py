from __future__ import annotations

import unittest

import pandas as pd

from run_carry_rf_0036r2 import review_excess_sharpe


class CarryRf0036R2Tests(unittest.TestCase):
    def test_review_convention_uses_strategy_volatility(self):
        idx = pd.date_range("2026-01-01", periods=5, freq="D")
        strategy = pd.Series([0.01, -0.005, 0.007, -0.002, 0.004], index=idx)
        value = review_excess_sharpe(-0.01, strategy)
        expected = -0.01 / (strategy.std(ddof=1) * (365.0 ** 0.5))
        self.assertAlmostEqual(value, expected, places=15)

    def test_negative_excess_cagr_stays_negative(self):
        idx = pd.date_range("2026-01-01", periods=4, freq="D")
        strategy = pd.Series([0.002, -0.001, 0.001, 0.0], index=idx)
        self.assertLess(review_excess_sharpe(-0.004, strategy), 0.0)


if __name__ == "__main__":
    unittest.main()
