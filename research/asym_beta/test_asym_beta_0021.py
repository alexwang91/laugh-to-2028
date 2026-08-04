import unittest
import numpy as np

from run_asym_beta_0021 import extra_beta_rule, safe_total_scale


class ExtraBetaRuleTests(unittest.TestCase):
    def test_derisked_core_has_no_extra_authority(self):
        out = extra_beta_rule(0.8, 1.0, 0.0, 1.5)
        self.assertEqual(out["extra_scale"], 0.0)
        self.assertAlmostEqual(out["total_scale"], 0.8)

    def test_full_core_trend_and_pbad(self):
        out = extra_beta_rule(1.0, 1.0, 0.2, 1.5)
        self.assertAlmostEqual(out["trend_candidate_extra"], 0.5)
        self.assertAlmostEqual(out["pbad_adjusted_extra"], 0.4)
        self.assertAlmostEqual(out["extra_scale"], 0.4)
        self.assertAlmostEqual(out["total_scale"], 1.4)

    def test_risk_capacity_caps_extra(self):
        out = extra_beta_rule(1.0, 1.0, 0.0, 1.23)
        self.assertAlmostEqual(out["extra_scale"], 0.23, places=10)
        self.assertAlmostEqual(out["total_scale"], 1.23, places=10)

    def test_negative_trend_has_no_extra(self):
        out = extra_beta_rule(1.0, -0.5, 0.0, 1.5)
        self.assertEqual(out["extra_scale"], 0.0)

    def test_full_bad_probability_has_no_extra(self):
        out = extra_beta_rule(1.0, 1.0, 1.0, 1.5)
        self.assertEqual(out["extra_scale"], 0.0)

    def test_zero_paths_allow_full_cap(self):
        paths = np.zeros((100, 20), dtype=float)
        out = safe_total_scale(paths, 0.20, 1.50)
        self.assertAlmostEqual(out["safe_total_scale"], 1.50)


if __name__ == "__main__":
    unittest.main()
