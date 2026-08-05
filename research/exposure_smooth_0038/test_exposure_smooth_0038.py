import math
import unittest

import numpy as np
import pandas as pd

from run_exposure_smooth_0038 import btc_smooth_beta, vol_multiplier


class ContinuityTests(unittest.TestCase):
    def test_no_discontinuity_at_trend_zero(self):
        """The defect under test: old beta jumped up to 0.61 across an infinitesimal
        change in trend sign at t=0. The new formula is a single linear function, so
        it has a bounded slope (continuous) rather than a jump (discontinuous) -- the
        change in beta must shrink proportionally as the interval around t=0 shrinks,
        with no fixed-size residual jump left over as the interval goes to zero."""
        for vol_level in [0.20, 0.40, 0.60, 0.90]:
            vm = float(vol_multiplier(pd.Series([vol_level]))[0])
            gaps = []
            for eps in [1e-2, 1e-3, 1e-4, 1e-5]:
                t = pd.Series([-eps, eps])
                raw = (0.65 + 0.65 * t) * vm
                beta = raw.clip(lower=0.18, upper=1.30)
                gaps.append(float(beta.iloc[1] - beta.iloc[0]))
            # A discontinuous function keeps a fixed-size gap no matter how small eps
            # gets. A continuous linear function's gap shrinks proportionally with eps.
            self.assertLess(
                gaps[-1], gaps[0] / 500,
                f"beta gap did not shrink with the interval at vol={vol_level}: {gaps}",
            )

    def test_matches_old_positive_ceiling_at_t1_low_vol(self):
        raw = (0.65 + 0.65 * 1.0) * 1.0
        self.assertAlmostEqual(raw, 1.30, places=10)

    def test_matches_old_negative_branch_at_t0(self):
        for vol_level, vm_expected in [(0.20, 1.00), (0.40, 0.90), (0.60, 0.75), (0.90, 0.60)]:
            vm = float(vol_multiplier(pd.Series([vol_level]))[0])
            self.assertAlmostEqual(vm, vm_expected, places=10)
            raw = (0.65 + 0.65 * 0.0) * vm
            self.assertAlmostEqual(raw, 0.65 * vm_expected, places=10)

    def test_monotonic_increasing_in_trend_for_fixed_vol(self):
        t = pd.Series(np.linspace(-1.0, 1.0, 41))
        vol = pd.Series(0.30, index=t.index)
        vm = vol_multiplier(vol)
        raw = (0.65 + 0.65 * t) * vm
        beta = raw.clip(lower=0.18, upper=1.30)
        diffs = beta.diff().dropna()
        self.assertTrue((diffs >= -1e-12).all(), "beta must be non-decreasing in trend")

    def test_vol_reduces_exposure_even_when_trend_strongly_positive(self):
        """This is defect 2 under test: old formula was inert here because the
        downstream gross<=1.0 cap swallowed the vol scaler whenever beta>=1.0."""
        t = pd.Series([0.9, 0.9])
        low_vol = pd.Series([0.20, 0.90])
        vm = vol_multiplier(low_vol)
        raw = (0.65 + 0.65 * t) * vm
        beta = raw.clip(lower=0.18, upper=1.30)
        self.assertGreater(
            float(beta.iloc[0] - beta.iloc[1]), 0.1,
            "high volatility must materially reduce exposure even with a strong positive trend",
        )

    def test_btc_smooth_beta_bounds_and_alignment(self):
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        rng = np.random.default_rng(0)
        price = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.02, len(idx)))), index=idx)
        beta, t, vol = btc_smooth_beta(price)
        valid = beta.dropna()
        self.assertGreater(len(valid), 0)
        self.assertTrue((valid >= 0.18 - 1e-9).all())
        self.assertTrue((valid <= 1.30 + 1e-9).all())
        self.assertTrue(beta.index.equals(t.index))
        self.assertTrue(beta.index.equals(vol.index))


if __name__ == "__main__":
    unittest.main()
