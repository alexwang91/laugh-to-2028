import unittest

import numpy as np
import pandas as pd

from run_tsmom_alpha_0029 import (
    EPS,
    build_targets,
    event_pnl_date,
    funding_accounting,
    price_returns_and_costs,
)


class Tsmom0029Tests(unittest.TestCase):
    def test_targets_are_gross_one_and_follow_own_trend_direction(self):
        idx = pd.date_range("2023-01-01", periods=300, freq="D")
        close = pd.DataFrame(
            {
                "UPUSDT": np.exp(np.linspace(0, 1.2, len(idx))),
                "DOWNUSDT": np.exp(np.linspace(1.2, 0, len(idx))),
            },
            index=idx,
        )
        eligibility = pd.DataFrame(True, index=idx, columns=close.columns)
        target, trend, vol = build_targets(close, eligibility)
        row = target.iloc[-1]
        self.assertAlmostEqual(float(row.abs().sum()), 1.0, places=10)
        self.assertGreater(float(trend.iloc[-1]["UPUSDT"]), 0.0)
        self.assertLess(float(trend.iloc[-1]["DOWNUSDT"]), 0.0)
        self.assertGreater(float(row["UPUSDT"]), 0.0)
        self.assertLess(float(row["DOWNUSDT"]), 0.0)

    def test_target_is_held_one_day_later(self):
        idx = pd.date_range("2024-01-01", periods=4, freq="D")
        close = pd.DataFrame({"X": [100.0, 110.0, 121.0, 133.1]}, index=idx)
        target = pd.DataFrame({"X": [0.0, 1.0, 1.0, 1.0]}, index=idx)
        _, _, _, held, by_cost = price_returns_and_costs(close, target)
        self.assertEqual(float(held.loc[idx[1], "X"]), 0.0)
        self.assertEqual(float(held.loc[idx[2], "X"]), 1.0)
        self.assertGreater(float(by_cost[5.0].loc[idx[2]]), 0.0)

    def test_midnight_funding_belongs_to_previous_held_day(self):
        self.assertEqual(
            event_pnl_date(pd.Timestamp("2024-03-02 00:00:00", tz="UTC")),
            pd.Timestamp("2024-03-01"),
        )
        self.assertEqual(
            event_pnl_date(pd.Timestamp("2024-03-02 08:00:00", tz="UTC")),
            pd.Timestamp("2024-03-02"),
        )

    def test_positive_funding_costs_long_and_benefits_short(self):
        idx = pd.DatetimeIndex([pd.Timestamp("2024-03-01")])
        held = pd.DataFrame({"LONG": [0.5], "SHORT": [-0.5]}, index=idx)
        funding = {
            "LONG": pd.DataFrame({
                "timestamp": [pd.Timestamp("2024-03-01 08:00:00", tz="UTC")],
                "rate": [0.001],
            }),
            "SHORT": pd.DataFrame({
                "timestamp": [pd.Timestamp("2024-03-01 08:00:00", tz="UTC")],
                "rate": [0.001],
            }),
        }
        factor, summary, diag = funding_accounting(held, funding, idx)
        long_row = summary.set_index("symbol").loc["LONG"]
        short_row = summary.set_index("symbol").loc["SHORT"]
        self.assertLess(float(long_row["net_additive_contribution"]), 0.0)
        self.assertGreater(float(short_row["net_additive_contribution"]), 0.0)
        self.assertAlmostEqual(float(factor.iloc[0]), 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
