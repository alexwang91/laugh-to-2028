import unittest

import pandas as pd

from risk_free import (
    annual_carry_vs_cash,
    compare_to_cash,
    excess_return_metrics,
    investment_basis_rate,
    load_fred_daily_risk_free,
    load_fred_daily_risk_free_investment_basis,
)


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

    def test_compare_to_cash_contract_is_frozen(self):
        """CARRY-RF-0036R1 evidence on disk depends on these exact keys."""
        idx = pd.date_range("2025-01-01", periods=90, freq="D")
        strategy = pd.Series(0.0001, index=idx)
        cash = pd.Series(0.00012, index=idx)
        self.assertEqual(
            sorted(compare_to_cash(strategy, cash)),
            [
                "arithmetic_excess_sharpe_daily_mean_diagnostic",
                "cash_benchmark",
                "excess_ann_vol",
                "excess_cagr_over_rf",
                "excess_sharpe_over_rf",
                "strategy",
            ],
        )

    def test_excess_metrics_name_both_committed_denominators(self):
        idx = pd.date_range("2025-01-01", periods=365, freq="D")
        rng = [0.0004 if i % 2 == 0 else -0.0002 for i in range(len(idx))]
        strategy = pd.Series(rng, index=idx)
        cash = pd.Series(0.00012, index=idx)

        out = excess_return_metrics(strategy, cash)
        frozen = compare_to_cash(strategy, cash)
        # The R1 field must remain reproducible from the new function.
        self.assertAlmostEqual(
            out["excess_sharpe_excess_vol_denominator"],
            frozen["excess_sharpe_over_rf"],
            places=12,
        )
        self.assertAlmostEqual(
            out["excess_sharpe_strategy_vol_denominator"],
            out["excess_cagr_over_rf"] / out["strategy_ann_vol"],
            places=12,
        )
        self.assertTrue(out["geometric_sharpe_interpretable"])
        self.assertEqual(
            out["preferred_ratio_field"], "excess_sharpe_excess_vol_denominator"
        )

    def test_near_identical_series_flag_geometric_ratio_as_uninterpretable(self):
        """The CARRY-STACK-0033 shape: benchmark ~= strategy, so excess vol ~ 0."""
        idx = pd.date_range("2025-01-01", periods=365, freq="D")
        base = pd.Series(
            [0.02 if i % 2 == 0 else -0.019 for i in range(len(idx))], index=idx
        )
        strategy = base
        # Small but *varying* wedge, as in 0033 where the sleeve's contribution
        # moves day to day. A constant wedge would give exactly zero excess vol.
        benchmark = base + pd.Series(
            [0.00006 if i % 3 else 0.00004 for i in range(len(idx))], index=idx
        )
        out = excess_return_metrics(strategy, benchmark)
        self.assertLess(out["excess_to_strategy_vol_ratio"], 0.01)
        self.assertFalse(out["geometric_sharpe_interpretable"])
        self.assertEqual(out["preferred_ratio_field"], "excess_information_ratio")
        # The geometric ratio blows up; the information ratio stays a real number.
        self.assertGreater(abs(out["excess_sharpe_excess_vol_denominator"]), 10.0)
        self.assertLess(out["excess_information_ratio"], 0.0)

    def test_investment_basis_exceeds_discount_basis(self):
        self.assertAlmostEqual(investment_basis_rate(0.05), 365 * 0.05 / (360 - 91 * 0.05))
        self.assertGreater(investment_basis_rate(0.05), 0.05)
        self.assertAlmostEqual(investment_basis_rate(0.0), 0.0)

    def test_investment_basis_loader_accrues_more_than_discount_loader(self):
        csv = "DATE,DTB3\n2026-01-02,5.00\n2026-01-03,5.00\n"
        discount = load_fred_daily_risk_free(
            "2026-01-02", "2026-01-03", session=FakeSession(csv)
        )
        investment = load_fred_daily_risk_free_investment_basis(
            "2026-01-02", "2026-01-03", session=FakeSession(csv)
        )
        self.assertGreater(
            investment.daily["rf_daily_return"].iloc[0],
            discount.daily["rf_daily_return"].iloc[0],
        )
        self.assertEqual(investment.metadata["quotation_basis"], "investment (bond-equivalent)")
        self.assertEqual(investment.raw_csv, discount.raw_csv)


if __name__ == "__main__":
    unittest.main()
