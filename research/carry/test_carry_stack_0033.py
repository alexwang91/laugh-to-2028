import unittest

import pandas as pd

from run_carry_stack_0033 import COST_RATE, combine_idle_stack, idle_scale_from_gross


class CarryStack0033Tests(unittest.TestCase):
    def test_idle_scale_fills_only_capital_below_one(self):
        idx = pd.date_range("2024-01-01", periods=4, freq="D")
        gross = pd.Series([0.0, 0.25, 1.0, 1.10], index=idx)
        scale = idle_scale_from_gross(gross)
        self.assertEqual(list(scale.round(12)), [1.0, 0.75, 0.0, 0.0])

    def test_combined_gross_fills_valid_brrk_gross_to_one(self):
        idx = pd.date_range("2024-01-01", periods=4, freq="D")
        brrk = pd.Series([0.01, -0.02, 0.03, 0.0], index=idx)
        carry = pd.Series([0.001, 0.001, 0.001, 0.001], index=idx)
        gross = pd.Series([0.2, 0.6, 1.0, 0.85], index=idx)
        frame = combine_idle_stack(brrk, carry, gross)
        self.assertLessEqual(float(frame["combined_gross"].max()), 1.0 + 1e-12)
        self.assertEqual(list(frame["carry_scale"].round(12)), [0.8, 0.4, 0.0, 0.15])
        self.assertTrue((frame["combined_gross"].round(12) == 1.0).all())

    def test_brrk_gross_above_one_hard_fails_in_conservative_stack(self):
        idx = pd.date_range("2024-01-01", periods=2, freq="D")
        brrk = pd.Series([0.01, 0.01], index=idx)
        carry = pd.Series([0.001, 0.001], index=idx)
        gross = pd.Series([0.9, 1.2], index=idx)
        with self.assertRaises(RuntimeError):
            combine_idle_stack(brrk, carry, gross)

    def test_scale_change_cost_and_combined_return_are_exact(self):
        idx = pd.date_range("2024-01-01", periods=3, freq="D")
        brrk = pd.Series([0.01, 0.02, -0.01], index=idx)
        carry = pd.Series([0.002, 0.002, 0.002], index=idx)
        gross = pd.Series([0.5, 0.5, 0.75], index=idx)
        frame = combine_idle_stack(brrk, carry, gross)

        # First day opens 0.5 carry allocation from zero; second unchanged; third falls 0.5 -> 0.25.
        self.assertAlmostEqual(float(frame.loc[idx[0], "scale_change_turnover"]), 0.5, places=12)
        self.assertAlmostEqual(float(frame.loc[idx[1], "scale_change_turnover"]), 0.0, places=12)
        self.assertAlmostEqual(float(frame.loc[idx[2], "scale_change_turnover"]), 0.25, places=12)
        self.assertAlmostEqual(float(frame.loc[idx[0], "scale_change_cost"]), 0.5 * COST_RATE, places=12)
        self.assertAlmostEqual(float(frame.loc[idx[2], "scale_change_cost"]), 0.25 * COST_RATE, places=12)

        expected0 = 0.01 + 0.5 * 0.002 - 0.5 * COST_RATE
        expected1 = 0.02 + 0.5 * 0.002
        expected2 = -0.01 + 0.25 * 0.002 - 0.25 * COST_RATE
        self.assertAlmostEqual(float(frame.loc[idx[0], "combined_return"]), expected0, places=12)
        self.assertAlmostEqual(float(frame.loc[idx[1], "combined_return"]), expected1, places=12)
        self.assertAlmostEqual(float(frame.loc[idx[2], "combined_return"]), expected2, places=12)

    def test_carry_never_reduces_brrk_directional_return_directly(self):
        idx = pd.date_range("2024-01-01", periods=2, freq="D")
        brrk = pd.Series([0.03, -0.03], index=idx)
        carry = pd.Series([0.0, 0.0], index=idx)
        gross = pd.Series([1.0, 1.0], index=idx)
        frame = combine_idle_stack(brrk, carry, gross)
        self.assertTrue((frame["carry_scale"] == 0.0).all())
        self.assertTrue((frame["combined_return"] == brrk).all())


if __name__ == "__main__":
    unittest.main()
