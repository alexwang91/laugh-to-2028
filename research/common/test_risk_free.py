import unittest

import pandas as pd

from risk_free import annual_carry_vs_cash, compare_to_cash, load_fred_daily_risk_free


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, text: str):
        self.text = text
        self.urls = []

    def get(self, url, timeout):
        self.urls.append((url, timeout))
        return FakeResponse(self.text)


class RiskFreeTests(unittest.TestCase):
    def test_calendar_forward_fill_and_daily_conversion(self):
        csv = "DATE,DTB3\n2026-01-02,3.65\n2026-01-05,3.66\n"
        loaded = load_fred_daily_risk_free(
            "2026-01-02", "2026-01-05", session=FakeSession(csv)
        )
        self.assertEqual(len(loaded.daily), 4)
        self.assertAlmostEqual(loaded.daily.loc[pd.Timestamp("2026-01-03"), "fred_rate_percent"], 3.65)
        self.assertAlmostEqual(
            loaded.daily.loc[pd.Timestamp("2026-01-03"), "rf_daily_return"],
            0.0365 / 365.0,
        )
        self.assertEqual(
            loaded.daily.loc[pd.Timestamp("2026-01-04"), "source_observation_date"],
            "2026-01-02",
        )

    def test_first_day_without_observation_fails(self):
        csv = "DATE,DTB3\n2026-01-05,3.66\n"
        with self.assertRaises(RuntimeError):
            load_fred_daily_risk_free(
                "2026-01-03", "2026-01-05", session=FakeSession(csv)
            )

    def test_geometric_excess_metrics_and_annual_table(self):
        idx = pd.date_range("2025-01-01", periods=365, freq="D")
        strategy = pd.Series(
            [0.00009 if i % 2 == 0 else 0.00011 for i in range(len(idx))],
            index=idx,
        )
        cash = pd.Series(
            [0.000115 if i % 3 == 0 else 0.000125 for i in range(len(idx))],
            index=idx,
        )
        out = compare_to_cash(strategy, cash)
        self.assertLess(out["excess_cagr_over_rf"], 0)
        self.assertIsNotNone(out["excess_sharpe_over_rf"])
        self.assertLess(out["excess_sharpe_over_rf"], 0)
        rows = annual_carry_vs_cash(strategy, cash)
        self.assertEqual(len(rows), 1)
        self.assertLess(rows[0]["excess_percentage_points"], 0)


if __name__ == "__main__":
    unittest.main()
