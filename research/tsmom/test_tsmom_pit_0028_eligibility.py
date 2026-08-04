import unittest

import numpy as np
import pandas as pd

from run_tsmom_pit_0028_eligibility import build_eligibility, month_in_range


class PitEligibilityTests(unittest.TestCase):
    def test_month_range(self):
        self.assertTrue(month_in_range("2020-09"))
        self.assertTrue(month_in_range("2026-07"))
        self.assertFalse(month_in_range("2020-08"))
        self.assertFalse(month_in_range("2026-08"))

    def test_requires_contiguous_240_and_volume(self):
        idx = pd.date_range("2020-09-01", periods=300, freq="D")
        close = pd.DataFrame({"A": 1.0, "B": 1.0}, index=idx)
        qvol = pd.DataFrame({"A": 30_000_000.0, "B": 30_000_000.0}, index=idx)
        close.loc[idx[100], "B"] = np.nan
        eligible = build_eligibility(close, qvol)
        self.assertTrue(bool(eligible.loc[idx[-1], "A"]))
        self.assertFalse(bool(eligible.loc[idx[239], "B"]))

    def test_volume_floor_is_completed_day_gate(self):
        idx = pd.date_range("2020-09-01", periods=300, freq="D")
        close = pd.DataFrame({"A": 1.0}, index=idx)
        qvol = pd.DataFrame({"A": 30_000_000.0}, index=idx)
        qvol.loc[idx[-1], "A"] = 24_999_999.0
        eligible = build_eligibility(close, qvol)
        self.assertFalse(bool(eligible.loc[idx[-1], "A"]))


if __name__ == "__main__":
    unittest.main()
