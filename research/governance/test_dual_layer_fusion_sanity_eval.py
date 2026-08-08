from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from research.governance.dual_layer_fusion_sanity_eval import compare_paths, stablecoin_external_states


class DualLayerFusionEvaluatorTests(unittest.TestCase):
    def test_stablecoin_state_dates_are_lagged(self) -> None:
        idx = pd.date_range("2020-01-01", periods=80, freq="D")
        supply = pd.Series(np.exp(np.linspace(0.0, 0.2, len(idx))), index=idx)
        out = stablecoin_external_states(supply)
        self.assertTrue(out.iloc[:42]["external_state"].isna().all())
        self.assertTrue(out.iloc[42:]["external_state"].notna().all())

    def test_compare_is_identity_when_internal_gross_below_restrictive_cap(self) -> None:
        idx = pd.date_range("2020-01-01", periods=500, freq="D")
        returns = pd.DataFrame(0.0005, index=idx, columns=["BTC", "ETH", "SOL", "BNB"])
        targets = pd.DataFrame(
            {"BTC": 0.20, "ETH": 0.15, "SOL": 0.10, "BNB": 0.05}, index=idx
        )
        # Nonlinear positive series creates finite state inputs; every cap remains >= internal gross 0.50.
        supply = pd.Series(np.exp(np.linspace(0.0, 0.5, len(idx)) ** 2), index=idx)
        result = compare_paths(returns, targets, supply)
        self.assertAlmostEqual(result["baseline"]["cagr"], result["fused"]["cagr"], places=12)
        self.assertAlmostEqual(result["delta"]["average_gross"], 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
