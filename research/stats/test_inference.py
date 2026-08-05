import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from inference import (
    comparison_report,
    deflated_sharpe_ratio,
    expected_max_sharpe_under_trials,
    min_track_record_length,
    paired_bootstrap,
    probabilistic_sharpe_ratio,
    sample_moments,
    sharpe_confidence_report,
)

RESULTS = Path(__file__).resolve().parents[1] / "results"


def load_return(col: str) -> pd.Series:
    eq = pd.read_csv(RESULTS / "pit_disp_0015" / "daily_equity.csv", parse_dates=["date"]).set_index("date")
    e = eq[col].astype(float)
    r = e.pct_change()
    r.iloc[0] = e.iloc[0] / 10_000.0 - 1.0
    return r


class SampleMomentsTests(unittest.TestCase):
    def test_normal_series_has_near_zero_skew_kurtosis(self):
        rng = np.random.default_rng(0)
        r = pd.Series(rng.normal(0.0005, 0.02, 5000))
        m = sample_moments(r)
        self.assertAlmostEqual(m["skew"], 0.0, delta=0.15)
        self.assertAlmostEqual(m["kurtosis"], 3.0, delta=0.3)

    def test_too_few_observations_raises(self):
        with self.assertRaises(ValueError):
            sample_moments(pd.Series([0.01, 0.02]))


class PSRRegressionTests(unittest.TestCase):
    """Pins the exact PSR/MinTRL values reported in docs/CODE_REVIEW_2026-08-04.md
    section 3.2, independently re-derived from the committed BRRK-0011 series."""

    def test_brrk0011_psr_matches_the_published_review_numbers(self):
        r = load_return("BRRK0011_BASELINE").dropna()
        m = sample_moments(r)
        self.assertEqual(m["n"], 1332)
        self.assertAlmostEqual(m["sharpe_annualized"], 1.353, places=2)
        self.assertAlmostEqual(m["skew"], 0.567, delta=0.01)
        self.assertAlmostEqual(m["kurtosis"], 7.07, delta=0.05)

        psr_zero = probabilistic_sharpe_ratio(m["sharpe_daily"], 0.0, m["n"], m["skew"], m["kurtosis"])
        self.assertAlmostEqual(psr_zero * 100, 99.57, delta=0.1)

        target_daily = 1.0 / math.sqrt(365.0)
        mintrl_days = min_track_record_length(m["sharpe_daily"], target_daily, m["skew"], m["kurtosis"])
        self.assertAlmostEqual(mintrl_days / 365.25, 20.97, delta=0.1)

    def test_v1_psr_matches_the_published_review_numbers(self):
        r = load_return("V1_BASELINE").dropna()
        m = sample_moments(r)
        self.assertAlmostEqual(m["sharpe_annualized"], 1.295, places=2)
        target_daily = 1.0 / math.sqrt(365.0)
        mintrl_days = min_track_record_length(m["sharpe_daily"], target_daily, m["skew"], m["kurtosis"])
        self.assertAlmostEqual(mintrl_days / 365.25, 30.10, delta=0.1)

    def test_sharpe_confidence_report_shape(self):
        r = load_return("BRRK0011_BASELINE")
        report = sharpe_confidence_report(r, target_sharpe_annualized=1.0)
        self.assertEqual(report["observations"], 1332)
        self.assertGreater(report["psr_above_zero"], 0.99)
        self.assertLess(report["psr_above_target"], report["psr_above_zero"])
        self.assertGreater(report["min_track_record_years"], 15.0)


class DeflatedSharpeTests(unittest.TestCase):
    def test_expected_max_sharpe_increases_with_trial_count(self):
        var = 1.237e-05  # from the six pit_disp_0015 variants, daily units
        vals = [expected_max_sharpe_under_trials(k, var) for k in (1, 6, 20, 100)]
        self.assertEqual(vals[0], 0.0)
        self.assertTrue(all(b >= a for a, b in zip(vals, vals[1:])))

    def test_deflated_sharpe_ratio_report_shape(self):
        r = load_return("BRRK0011_BASELINE")
        out = deflated_sharpe_ratio(r, n_trials=20, sharpe_variance_across_trials_daily=1.237e-05)
        self.assertIn("deflated_sharpe_ratio", out)
        self.assertGreater(out["deflated_sharpe_ratio"], 0.98)


class PairedBootstrapTests(unittest.TestCase):
    """Pins the paired-bootstrap results already published for BRRK-0011 vs V1
    (docs/CODE_REVIEW_2026-08-04.md section 3.3): daily correlation 0.9948,
    Sharpe difference +0.058 with 95% CI crossing zero."""

    def test_brrk_vs_v1_reproduces_published_bootstrap(self):
        v1 = load_return("V1_BASELINE")
        brrk = load_return("BRRK0011_BASELINE")
        report = comparison_report(v1, brrk, "V1", "BRRK-0011", n_resamples=4000, seed=7)
        self.assertAlmostEqual(report["daily_correlation"], 0.9948, places=3)
        self.assertAlmostEqual(
            report["sharpe"]["mean_difference_b_minus_a"], 0.058, delta=0.03
        )
        # The published finding is that this CI crosses zero -- pin that fact,
        # not the exact bound (bounds move slightly with the resample seed).
        self.assertFalse(report["sharpe"]["significant_at_confidence"])
        self.assertLess(report["sharpe"]["ci_low"], 0.0)
        self.assertGreater(report["sharpe"]["ci_high"], 0.0)

    def test_identical_series_gives_zero_difference_and_no_significance(self):
        idx = pd.date_range("2024-01-01", periods=500, freq="D")
        rng = np.random.default_rng(1)
        r = pd.Series(rng.normal(0.001, 0.02, len(idx)), index=idx)
        result = paired_bootstrap(r, r, "sharpe", n_resamples=500, seed=3)
        self.assertAlmostEqual(result.mean_difference, 0.0, places=6)
        self.assertFalse(result.excludes_zero)

    def test_clearly_different_series_is_detected_as_significant(self):
        idx = pd.date_range("2024-01-01", periods=1000, freq="D")
        rng = np.random.default_rng(2)
        a = pd.Series(rng.normal(0.0000, 0.02, len(idx)), index=idx)
        b = pd.Series(rng.normal(0.0030, 0.02, len(idx)), index=idx)
        result = paired_bootstrap(a, b, "sharpe", n_resamples=2000, seed=5)
        self.assertTrue(result.excludes_zero)
        self.assertGreater(result.probability_b_better, 0.95)

    def test_unknown_statistic_rejected(self):
        idx = pd.date_range("2024-01-01", periods=100, freq="D")
        r = pd.Series(0.001, index=idx)
        with self.assertRaises(ValueError):
            paired_bootstrap(r, r, statistic="sortino")

    def test_too_few_observations_rejected(self):
        idx = pd.date_range("2024-01-01", periods=10, freq="D")
        r = pd.Series(0.001, index=idx)
        with self.assertRaises(ValueError):
            paired_bootstrap(r, r, "sharpe")


if __name__ == "__main__":
    unittest.main()
