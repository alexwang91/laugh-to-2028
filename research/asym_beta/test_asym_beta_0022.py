import math
import unittest

import numpy as np
import pandas as pd

from run_asym_beta_0022 import downside_semivolatility, extra_beta_rule


class SemivolTests(unittest.TestCase):
    def test_all_up_returns_have_zero_downside_semivol(self):
        idx = pd.date_range("2026-01-01", periods=40, freq="D")
        price = pd.Series(np.exp(np.arange(40) * 0.01), index=idx)
        semivol = downside_semivolatility(price)
        self.assertAlmostEqual(float(semivol.iloc[-1]), 0.0, places=12)

    def test_manual_downside_semivol(self):
        returns = np.array([0.01, -0.02, 0.03, -0.04] * 8, dtype=float)
        log_price = np.concatenate([[0.0], np.cumsum(returns)])
        idx = pd.date_range("2026-01-01", periods=len(log_price), freq="D")
        price = pd.Series(np.exp(log_price), index=idx)
        semivol = downside_semivolatility(price, window=32)
        expected = math.sqrt(np.mean(np.minimum(returns, 0.0) ** 2)) * math.sqrt(365.0)
        self.assertAlmostEqual(float(semivol.iloc[-1]), expected, places=12)


class ExtraRuleTests(unittest.TestCase):
    def test_derisked_core_has_no_extra(self):
        out = extra_beta_rule(0.9, 1.0, 0.0, 0.1)
        self.assertEqual(out["extra_scale"], 0.0)
        self.assertAlmostEqual(out["total_scale"], 0.9)

    def test_good_volatility_is_not_penalized(self):
        out = extra_beta_rule(1.0, 1.0, 0.0, 0.0)
        self.assertAlmostEqual(out["downside_scaler"], 1.0)
        self.assertAlmostEqual(out["extra_scale"], 0.5)
        self.assertAlmostEqual(out["total_scale"], 1.5)

    def test_pbad_only_reduces_extra(self):
        out = extra_beta_rule(1.0, 1.0, 0.4, 0.1)
        self.assertAlmostEqual(out["extra_scale"], 0.3)
        self.assertAlmostEqual(out["total_scale"], 1.3)

    def test_high_downside_semivol_scales_extra(self):
        out = extra_beta_rule(1.0, 1.0, 0.0, 0.90)
        self.assertAlmostEqual(out["downside_scaler"], 0.5)
        self.assertAlmostEqual(out["extra_scale"], 0.25)
        self.assertAlmostEqual(out["total_scale"], 1.25)

    def test_negative_trend_has_no_extra(self):
        out = extra_beta_rule(1.0, -0.2, 0.0, 0.1)
        self.assertEqual(out["extra_scale"], 0.0)


if __name__ == "__main__":
    unittest.main()
