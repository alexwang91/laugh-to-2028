from __future__ import annotations

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
    start = __import__("datetime").date(2020, 1, 1)
    out: dict[str, bytes] = {}
    for ai, (asset, filename, base) in enumerate([
        ("BTC", "btc_daily.json", 100.0),
        ("ETH", "eth_daily.json", 50.0),
        ("SOL", "sol_daily.json", 20.0),
    ]):
        p = base
        rows = []
        for i in range(days):
            d = (start + __import__("datetime").timedelta(days=i)).isoformat()
            if i:
                cycle = ((i * (7 + ai * 2)) % 23 - 11) / 11.0
                shock = wobble * cycle
                p *= math.exp(trend + shock)
            rows.append({"date": d, "close": p})
        out[filename] = json.dumps(rows, separators=(",", ":")).encode()
    return out


class Trend0085Qualification(unittest.TestCase):
    def test_deterministic_full_interface_and_allowed_classification(self) -> None:
        sources = synthetic_prices()
        first = run_from_sources(sources)
        second = run_from_sources(sources)
        self.assertEqual(first, second)
        self.assertTrue(first["execution_valid"])
        self.assertIn(first["classification"], CLASSIFICATIONS)
        self.assertGreaterEqual(first["support_sessions"], 730)
        self.assertEqual(set(first["cost_panels_bps"]), {"10", "20", "30"})
        self.assertIn("equal_weight_btc_eth_sol", first["benchmarks"])
        self.assertIn("btc_buy_and_hold", first["benchmarks"])
        self.assertIn("chronological_block_cagr", first["primary_diagnostics"])
        self.assertEqual(len(first["primary_diagnostics"]["chronological_block_cagr"]), 4)

    def test_gross_cap_no_short_and_cost_monotonicity(self) -> None:
        result = run_from_sources(synthetic_prices())
        self.assertTrue(result["gates"]["gross_cap_and_no_short"])
        w10 = result["cost_panels_bps"]["10"]["terminal_wealth_multiple"]
        w20 = result["cost_panels_bps"]["20"]["terminal_wealth_multiple"]
        w30 = result["cost_panels_bps"]["30"]["terminal_wealth_multiple"]
        self.assertGreaterEqual(w10, w20)
        self.assertGreaterEqual(w20, w30)
        exposures = result["primary_diagnostics"]["asset_average_exposure"]
        self.assertTrue(all(v >= 0 for v in exposures.values()))
        self.assertLessEqual(sum(exposures.values()), 1.0 + 1e-12)

    def test_insufficient_support_is_inconclusive_not_fail(self) -> None:
        result = run_from_sources(synthetic_prices(days=700))
        self.assertTrue(result["execution_valid"])
        self.assertEqual(result["classification"], "INCONCLUSIVE_INSUFFICIENT_SUPPORT")

    def test_unknown_source_fails_closed(self) -> None:
        sources = synthetic_prices()
        sources["unexpected.json"] = b"[]"
        with self.assertRaisesRegex(Exception, "UNKNOWN_SOURCE"):
            run_from_sources(sources)

    def test_duplicate_or_nonincreasing_dates_fail_closed(self) -> None:
        sources = synthetic_prices(days=300)
        rows = json.loads(sources["btc_daily.json"])
        rows[10]["date"] = rows[9]["date"]
        sources["btc_daily.json"] = json.dumps(rows).encode()
        with self.assertRaisesRegex(Exception, "NON_INCREASING_DATE"):
            run_from_sources(sources)

    def test_nonfinite_or_nonpositive_price_fails_closed(self) -> None:
        sources = synthetic_prices(days=300)
        rows = json.loads(sources["eth_daily.json"])
        rows[100]["close"] = 0
        sources["eth_daily.json"] = json.dumps(rows).encode()
        with self.assertRaisesRegex(Exception, "INVALID_PRICE"):
            run_from_sources(sources)

    def test_runner_engine_interface_returns_invalid_envelope(self) -> None:
        sources = synthetic_prices(days=300)
        sources["bad.json"] = b"[]"
        result = TrendVolTargetEngine().execute(SimpleNamespace(sources=sources))
        self.assertEqual(result["classification"], "INVALID_EXECUTION")
        self.assertFalse(result["execution_valid"])

    def test_zero_cash_rule_is_explicit_when_cash_source_absent(self) -> None:
        result = run_from_sources(synthetic_prices(days=1000))
        self.assertEqual(result["cash_rule"], "ZERO_CASH_RETURN")
        self.assertFalse(result["canonical_brrk_present"])


if __name__ == "__main__":
    unittest.main()
