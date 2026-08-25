from __future__ import annotations

from datetime import date, timedelta
import json
import math
import unittest
from types import SimpleNamespace

from research.brrk_multi_horizon_trend_vol_target_0085.engine import (
    CLASSIFICATIONS,
    TrendVolTargetEngine,
    run_from_sources,
)


def synthetic_prices(days: int = 1100, trend: float = 0.0012, wobble: float = 0.012) -> dict[str, bytes]:
    start = date(2020, 1, 1)
    out: dict[str, bytes] = {}
    specs = [
        ("btc_daily.json", 100.0, 7),
        ("eth_daily.json", 50.0, 9),
        ("sol_daily.json", 20.0, 11),
    ]
    for filename, base, cycle_step in specs:
        price = base
        rows = []
        for i in range(days):
            if i:
                cycle = ((i * cycle_step) % 23 - 11) / 11.0
                price *= math.exp(trend + wobble * cycle)
            rows.append({"date": (start + timedelta(days=i)).isoformat(), "close": price})
        out[filename] = json.dumps(rows, separators=(",", ":")).encode()
    return out


def add_cash(sources: dict[str, bytes], days: int, daily_return: float = 0.0002) -> None:
    start = date(2020, 1, 1)
    rows = [
        {"date": (start + timedelta(days=i)).isoformat(), "return": daily_return}
        for i in range(days)
    ]
    sources["cash_daily.json"] = json.dumps(rows, separators=(",", ":")).encode()


class Trend0085BuildStandingQualification(unittest.TestCase):
    def test_deterministic_full_interface_and_allowed_classification(self) -> None:
        sources = synthetic_prices()
        first = run_from_sources(sources)
        second = run_from_sources(sources)
        self.assertEqual(first, second)
        self.assertTrue(first["execution_valid"])
        self.assertIn(first["classification"], CLASSIFICATIONS)
        self.assertGreaterEqual(first["support_sessions"], 730)
        self.assertEqual(set(first["cost_panels_bps"]), {"10", "20", "30"})
        self.assertEqual(len(first["primary_diagnostics"]["chronological_block_cagr"]), 4)

    def test_gross_no_short_and_cost_monotonicity(self) -> None:
        result = run_from_sources(synthetic_prices())
        self.assertTrue(result["gates"]["gross_cap_and_no_short"])
        wealth = [result["cost_panels_bps"][str(bps)]["terminal_wealth_multiple"] for bps in (10, 20, 30)]
        self.assertGreaterEqual(wealth[0], wealth[1])
        self.assertGreaterEqual(wealth[1], wealth[2])
        exposures = result["primary_diagnostics"]["asset_average_exposure"]
        self.assertTrue(all(value >= 0 for value in exposures.values()))
        self.assertLessEqual(sum(exposures.values()), 1.0 + 1e-12)

    def test_insufficient_support_is_inconclusive(self) -> None:
        result = run_from_sources(synthetic_prices(days=700))
        self.assertTrue(result["execution_valid"])
        self.assertEqual(result["classification"], "INCONCLUSIVE_INSUFFICIENT_SUPPORT")

    def test_cash_is_frozen_risk_free_and_missing_bound_cash_fails_closed(self) -> None:
        zero_cash = run_from_sources(synthetic_prices())
        with_cash_sources = synthetic_prices()
        add_cash(with_cash_sources, 1100)
        with_cash = run_from_sources(with_cash_sources)
        self.assertEqual(with_cash["cash_rule"], "ARM_BOUND_CASH_DAILY")
        self.assertNotEqual(
            zero_cash["cost_panels_bps"]["10"]["sharpe"],
            with_cash["cost_panels_bps"]["10"]["sharpe"],
        )
        short_cash_sources = synthetic_prices()
        add_cash(short_cash_sources, 500)
        with self.assertRaisesRegex(Exception, "MISSING_BOUND_CASH_RETURN"):
            run_from_sources(short_cash_sources)

    def test_unknown_source_duplicate_date_and_invalid_price_fail_closed(self) -> None:
        sources = synthetic_prices(days=300)
        sources["unexpected.json"] = b"[]"
        with self.assertRaisesRegex(Exception, "UNKNOWN_SOURCE"):
            run_from_sources(sources)

        sources = synthetic_prices(days=300)
        rows = json.loads(sources["btc_daily.json"])
        rows[10]["date"] = rows[9]["date"]
        sources["btc_daily.json"] = json.dumps(rows).encode()
        with self.assertRaisesRegex(Exception, "NON_INCREASING_DATE"):
            run_from_sources(sources)

        sources = synthetic_prices(days=300)
        rows = json.loads(sources["eth_daily.json"])
        rows[100]["close"] = 0
        sources["eth_daily.json"] = json.dumps(rows).encode()
        with self.assertRaisesRegex(Exception, "INVALID_PRICE"):
            run_from_sources(sources)

    def test_runner_interface_returns_invalid_envelope_without_retry(self) -> None:
        sources = synthetic_prices(days=300)
        sources["bad.json"] = b"[]"
        result = TrendVolTargetEngine().execute(SimpleNamespace(sources=sources))
        self.assertEqual(result["classification"], "INVALID_EXECUTION")
        self.assertFalse(result["execution_valid"])


if __name__ == "__main__":
    unittest.main()
