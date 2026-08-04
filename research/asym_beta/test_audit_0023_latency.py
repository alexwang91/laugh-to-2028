import unittest

import pandas as pd

from run_audit_0023_latency import first_crossing, interval_summary


class LatencyAuditTests(unittest.TestCase):
    def test_first_crossing_reports_days(self):
        idx = pd.date_range("2026-01-01", periods=4, freq="D")
        frame = pd.DataFrame({
            "monthly_held_extra": [0.4] * 4,
            "implied_to_held_ratio": [1.0, 0.9, 0.7, 0.4],
            "days_after_refit": [0, 1, 2, 3],
        }, index=idx)
        out = first_crossing(frame, 0.75)
        self.assertEqual(out["date"], "2026-01-03")
        self.assertEqual(out["days_after_refit"], 2)

    def test_inactive_interval_has_zero_gap(self):
        idx = pd.date_range("2026-01-01", periods=2, freq="D")
        frame = pd.DataFrame({
            "refit_date": [idx[0], idx[0]],
            "monthly_held_extra": [0.0, 0.0],
            "monthly_core_scale": [0.8, 0.8],
            "daily_btc_trend": [-0.2, -0.3],
            "daily_p_bad": [0.8, 0.9],
            "daily_downside_semivol30": [0.3, 0.4],
        }, index=idx)
        out = interval_summary(frame)
        self.assertFalse(out["active"])
        self.assertEqual(out["excess_exposure_days"], 0.0)


if __name__ == "__main__":
    unittest.main()
