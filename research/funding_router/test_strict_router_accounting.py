from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from run_strict_router_accounting import (
    build_equity,
    daily_funding_factors,
    price_returns_from_equity,
    verified_spot_targets,
)


class StrictRouterAccountingTests(unittest.TestCase):
    def test_verified_spot_policy_only_accepts_approved_classes(self) -> None:
        targets = {
            "BTC": {"primary_spot_classification": "verified_official_ui_remap"},
            "ETH": {"primary_spot_classification": "candidate_wrapped_or_bridged"},
            "SOL": {"primary_spot_classification": "candidate_wrapped_or_bridged"},
            "BNB": {"primary_spot_classification": "no_direct_spot_candidate"},
            "XRP": {"primary_spot_classification": "no_direct_spot_candidate"},
        }
        summary = {
            "targets": targets,
            "decision": {"verified_spot_targets": ["BTC"]},
        }
        self.assertEqual(verified_spot_targets(summary), ["BTC"])

    def test_daily_funding_factor_compounds_blocks(self) -> None:
        frame = pd.DataFrame(
            [
                {"source": "HYPERLIQUID_COMMON", "date": "2026-01-01", "block": "a", "asset": "ETH", "contribution": -0.01},
                {"source": "HYPERLIQUID_COMMON", "date": "2026-01-01", "block": "a", "asset": "SOL", "contribution": 0.002},
                {"source": "HYPERLIQUID_COMMON", "date": "2026-01-01", "block": "b", "asset": "ETH", "contribution": -0.005},
                {"source": "HYPERLIQUID_COMMON", "date": "2026-01-01", "block": "b", "asset": "SOL", "contribution": 0.001},
            ]
        )
        dates = pd.Series(["2026-01-01"])
        got = daily_funding_factors(frame, dates, ["ETH", "SOL"])[0]
        expected = (1 - 0.01 + 0.002) * (1 - 0.005 + 0.001)
        self.assertAlmostEqual(got, expected, places=12)

    def test_price_equity_round_trip(self) -> None:
        price_equity = pd.Series([10_100.0, 10_302.0])
        returns = price_returns_from_equity(price_equity)
        nav = build_equity(returns, np.ones(2))
        np.testing.assert_allclose(nav, price_equity.to_numpy(), rtol=0, atol=1e-10)


if __name__ == "__main__":
    unittest.main()
