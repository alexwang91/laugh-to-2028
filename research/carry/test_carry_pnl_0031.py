import unittest

import pandas as pd

from run_carry_pnl_0031 import (
    ASSETS,
    WEIGHT,
    build_price_returns,
    complete_common_index,
    daily_key,
    event_pnl_date,
    turnover_from_drift,
)


class CarryPnl0031Tests(unittest.TestCase):
    def _panels(self, spot_values, perp_values, idx):
        spot = {symbol: pd.DataFrame({"close": spot_values}, index=idx) for symbol in ASSETS}
        perp = {symbol: pd.DataFrame({"close": perp_values}, index=idx) for symbol in ASSETS}
        return spot, perp

    def test_equal_spot_and_perp_returns_cancel_price_beta(self):
        idx = pd.date_range("2024-01-01", periods=4, freq="D")
        spot, perp = self._panels([100.0, 110.0, 99.0, 108.9], [100.0, 110.0, 99.0, 108.9], idx)
        _, _, price_component, contribution = build_price_returns(spot, perp, idx)
        self.assertAlmostEqual(float(price_component.loc[idx[1]]), 0.0, places=12)
        self.assertAlmostEqual(float(price_component.loc[idx[2]]), 0.0, places=12)
        self.assertAlmostEqual(float(contribution.loc[idx[3]].sum()), 0.0, places=12)

    def test_midnight_funding_is_assigned_to_previous_pnl_day(self):
        self.assertEqual(
            event_pnl_date(pd.Timestamp("2024-03-02 00:00:00", tz="UTC")),
            pd.Timestamp("2024-03-01"),
        )
        self.assertEqual(
            event_pnl_date(pd.Timestamp("2024-03-02 08:00:00", tz="UTC")),
            pd.Timestamp("2024-03-02"),
        )

    def test_daily_key_switches_monthly_to_daily_same_market(self):
        spot = daily_key("data/spot/monthly/klines/", "BTCUSDT", pd.Timestamp("2024-02-03"))
        perp = daily_key("data/futures/um/monthly/klines/", "BTCUSDT", pd.Timestamp("2024-02-03"))
        self.assertEqual(spot, "data/spot/daily/klines/BTCUSDT/1d/BTCUSDT-1d-2024-02-03.zip")
        self.assertEqual(perp, "data/futures/um/daily/klines/BTCUSDT/1d/BTCUSDT-1d-2024-02-03.zip")

    def test_turnover_charges_initial_entry_and_zero_drift_when_legs_flat(self):
        idx = pd.date_range("2024-01-01", periods=3, freq="D")
        zeros = pd.DataFrame(0.0, index=idx, columns=ASSETS)
        pre_factor = pd.Series(1.0, index=idx)
        first_held = idx[1]
        turnover = turnover_from_drift(zeros, zeros, pre_factor, first_held)
        self.assertAlmostEqual(float(turnover.loc[first_held]), 1.0, places=12)
        self.assertAlmostEqual(float(turnover.loc[idx[2]]), 0.0, places=12)

    def test_turnover_detects_notional_drift_even_if_portfolio_price_component_is_neutral(self):
        idx = pd.date_range("2024-01-01", periods=2, freq="D")
        spot_ret = pd.DataFrame(0.10, index=idx, columns=ASSETS)
        perp_ret = pd.DataFrame(0.10, index=idx, columns=ASSETS)
        pre_factor = pd.Series(1.0, index=idx)
        turnover = turnover_from_drift(spot_ret, perp_ret, pre_factor, idx[0])
        # Ten legs, each |0.1 * 1.0 - 0.1 * 1.1| = 0.01; plus gross=1 initial entry.
        self.assertAlmostEqual(float(turnover.loc[idx[0]]), 1.10, places=12)
        self.assertAlmostEqual(float(turnover.loc[idx[1]]), 0.10, places=12)

    def test_common_index_hard_fails_on_required_internal_gap(self):
        idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
        spot, perp = self._panels([100.0, 101.0, 102.0], [100.0, 101.0, 102.0], idx)
        spot[ASSETS[0]] = spot[ASSETS[0]].drop(pd.Timestamp("2024-01-02"))
        with self.assertRaises(RuntimeError):
            complete_common_index(spot, perp)


if __name__ == "__main__":
    unittest.main()
