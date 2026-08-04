import unittest
import numpy as np
import pandas as pd

from run_audit_0025_april_trend import components, first_zero_cross


class TrendDecompTests(unittest.TestCase):
    def test_weighted_components_sum(self):
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        price = pd.Series(np.exp(np.linspace(0, 2, len(idx)) + 0.02*np.sin(np.arange(len(idx))/7)), index=idx)
        frame = components(price).dropna()
        weighted = frame[["weighted_20","weighted_60","weighted_120","weighted_240"]].sum(axis=1)
        self.assertLess(float((weighted-frame["aggregate_from_components"]).abs().max()), 1e-12)

    def test_first_negative_cross(self):
        idx = pd.date_range("2026-01-01", periods=4, freq="D")
        frame = pd.DataFrame({"comp_20":[0.2,0.1,-0.1,-0.2]}, index=idx)
        self.assertEqual(first_zero_cross(frame, "comp_20"), "2026-01-03")


if __name__ == "__main__":
    unittest.main()
