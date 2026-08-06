import math
import unittest

import numpy as np
import pandas as pd

from metrics import (
    ASYM_BETA_0024_BRRK0011_CAGR,
    ASYM_BETA_0024_BRRK0011_FINAL_10K,
    PIT_DISP_0015_BRRK0011_CAGR,
    PIT_DISP_0015_BRRK0011_FINAL_10K,
    cagr_from_returns,
    elapsed_years,
    max_drawdown,
    metrics,
    sharpe_ratio,
)


class ElapsedYearsTests(unittest.TestCase):
    def test_matches_calendar_span_not_observation_count(self):
        # 1332 daily observations spanning 1331 calendar days (no gaps) --
        # exactly the BRRK-0011 series shape that produced the F7 gap.
        idx = pd.date_range("2022-12-10", periods=1332, freq="D")
        self.assertEqual(len(idx), 1332)
        self.assertEqual((idx[-1] - idx[0]).days, 1331)
        self.assertAlmostEqual(elapsed_years(idx), 1331 / 365.25, places=10)
        self.assertNotAlmostEqual(elapsed_years(idx), 1332 / 365.25, places=6)

    def test_single_observation_does_not_divide_by_zero(self):
        idx = pd.DatetimeIndex(["2026-01-01"])
        self.assertGreater(elapsed_years(idx), 0.0)

    def test_gap_in_series_is_reflected_in_calendar_span(self):
        """The reason to prefer calendar span: observation-count silently
        understates elapsed time when a series has a gap (e.g. a delisted
        asset's missing rows), inflating CAGR. Deleting 20 interior rows
        doesn't move the first/last timestamps, so calendar span stays at
        the true ~100-day window while observation count drops to 80 --
        an observation-count convention would understate elapsed time by
        20%, silently inflating any CAGR computed on this series."""
        with_gap = pd.date_range("2024-01-01", periods=100, freq="D").delete(
            slice(40, 60)
        )
        self.assertEqual(len(with_gap), 80)
        calendar_based = elapsed_years(with_gap)
        observation_count_based = len(with_gap) / 365.25
        self.assertAlmostEqual(calendar_based, 99 / 365.25, places=10)
        self.assertGreater(calendar_based, observation_count_based)


class MetricsReproductionTests(unittest.TestCase):
    def test_reproduces_pit_disp_0015_convention_via_observation_count(self):
        """Confirms the F7 diagnosis: replicate the OLD (observation-count)
        formula directly and check it lands on the published pit_disp_0015
        number, not this module's calendar-span number."""
        final_multiple = PIT_DISP_0015_BRRK0011_FINAL_10K / 10_000.0
        n = 1332
        old_convention_years = n / 365.25
        reconstructed = final_multiple ** (1.0 / old_convention_years) - 1.0
        self.assertAlmostEqual(reconstructed, PIT_DISP_0015_BRRK0011_CAGR, places=6)

    def test_reproduces_asym_beta_0024_convention_via_calendar_span(self):
        final_multiple = ASYM_BETA_0024_BRRK0011_FINAL_10K / 10_000.0
        span_days = 1331
        calendar_years = span_days / 365.25
        reconstructed = final_multiple ** (1.0 / calendar_years) - 1.0
        self.assertAlmostEqual(reconstructed, ASYM_BETA_0024_BRRK0011_CAGR, places=6)

    def test_this_module_agrees_with_asym_beta_0024_not_pit_disp_0015(self):
        """This module's cagr_from_returns should match the calendar-span
        published number (asym_beta_0024) to high precision, and visibly
        differ from the observation-count published number (pit_disp_0015)
        by the known ~0.0007 gap -- proving which convention was adopted."""
        idx = pd.date_range("2022-12-10", periods=1332, freq="D")
        final_multiple = ASYM_BETA_0024_BRRK0011_FINAL_10K / 10_000.0
        daily_growth = final_multiple ** (1.0 / (len(idx) - 1))
        nav = daily_growth ** np.arange(len(idx))
        ret = pd.Series(nav, index=idx).pct_change()
        ret.iloc[0] = nav[0] - 1.0

        got = cagr_from_returns(ret)
        self.assertAlmostEqual(got, ASYM_BETA_0024_BRRK0011_CAGR, places=4)
        self.assertGreater(abs(got - PIT_DISP_0015_BRRK0011_CAGR), 1e-5)


class EquityToReturnsConventionTests(unittest.TestCase):
    """Pins the caller trap that produced a third BRRK-0011 CAGR on 2026-08-06.

    `elapsed_years` measures the span of the index it is given. Converting an
    equity curve with `pct_change().dropna()` drops the first row, losing both
    a day of PNL and a day of calendar span. These tests fix the size and the
    direction of that error so nobody has to rediscover it.
    """

    def _equity_curve(self):
        """Same shape as research/results/pit_disp_0015/daily_equity.csv.

        1332 rows, 1331-day span, ending on the published final_10k. The first
        row is deliberately ~flat (9999.10 in the real file): BRRK-0011's first
        walk-forward decision day carries essentially no position, so day one's
        return is ~0 while the rest of the window compounds hard. That
        asymmetry is *why* dropping the first row inflates CAGR -- a curve with
        uniform daily growth would hide the effect, because losing an
        average-sized day and losing a day of span roughly cancel.
        """
        idx = pd.date_range("2022-12-10", periods=1332, freq="D")
        first_close = 9999.10
        final_multiple = ASYM_BETA_0024_BRRK0011_FINAL_10K / first_close
        daily_growth = final_multiple ** (1.0 / (len(idx) - 1))
        nav = first_close * daily_growth ** np.arange(len(idx))
        return pd.Series(nav, index=idx)

    def test_seeding_first_return_off_base_capital_matches_published_cagr(self):
        equity = self._equity_curve()
        ret = equity.pct_change()
        ret.iloc[0] = equity.iloc[0] / 10_000.0 - 1.0
        self.assertAlmostEqual(cagr_from_returns(ret), ASYM_BETA_0024_BRRK0011_CAGR, places=6)

    def test_dropna_loses_a_day_and_inflates_cagr(self):
        equity = self._equity_curve()
        dropped = cagr_from_returns(equity.pct_change().dropna())
        self.assertGreater(dropped, ASYM_BETA_0024_BRRK0011_CAGR)
        # The observed inflation was ~0.06 pp; hold it in a tight band so a
        # future change to elapsed_years can't quietly widen or hide it.
        inflation_pp = (dropped - ASYM_BETA_0024_BRRK0011_CAGR) * 100.0
        self.assertGreater(inflation_pp, 0.03)
        self.assertLess(inflation_pp, 0.12)

    def test_dropna_shortens_the_span_by_exactly_one_day(self):
        equity = self._equity_curve()
        seeded = equity.pct_change()
        seeded.iloc[0] = equity.iloc[0] / 10_000.0 - 1.0
        dropped = equity.pct_change().dropna()
        self.assertEqual(len(seeded) - len(dropped), 1)
        span_seeded = round(elapsed_years(seeded.index) * 365.25)
        span_dropped = round(elapsed_years(dropped.index) * 365.25)
        self.assertEqual(span_seeded, 1331)
        self.assertEqual(span_dropped, 1330)


class MetricsDictTests(unittest.TestCase):
    def test_full_dict_shape_and_bounds(self):
        idx = pd.date_range("2024-01-01", periods=400, freq="D")
        rng = np.random.default_rng(0)
        ret = pd.Series(rng.normal(0.001, 0.02, len(idx)), index=idx)
        turnover = pd.Series(0.05, index=idx)
        gross = pd.Series(1.0, index=idx)
        m = metrics(ret, turnover, gross)
        for key in ("start", "end", "observations", "elapsed_years", "end_multiple",
                    "final_10k", "cagr", "max_drawdown", "ann_vol", "sharpe", "calmar",
                    "turnover", "avg_gross_exposure"):
            self.assertIn(key, m)
        self.assertLessEqual(m["max_drawdown"], 0.0)
        self.assertEqual(m["observations"], len(idx))

    def test_empty_series_returns_empty_dict(self):
        self.assertEqual(metrics(pd.Series(dtype=float)), {})

    def test_max_drawdown_is_nonpositive(self):
        nav = pd.Series([1.0, 1.2, 0.9, 1.1])
        self.assertLessEqual(max_drawdown(nav), 0.0)
        self.assertAlmostEqual(max_drawdown(nav), 0.9 / 1.2 - 1.0, places=10)

    def test_sharpe_nan_on_zero_vol(self):
        ret = pd.Series([0.001] * 10)
        self.assertTrue(math.isnan(sharpe_ratio(ret)))


if __name__ == "__main__":
    unittest.main()
