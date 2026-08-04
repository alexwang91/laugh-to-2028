import unittest

import numpy as np
import pandas as pd

from run_tsmom_0029_first_mechanism import actual_held_weights, normalized_target_weights, trend_score


class TsmomMechanismTests(unittest.TestCase):
    def test_monotonic_series_trend_sign(self):
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        up = pd.Series(np.exp(np.arange(400) * 0.005 + 0.001*np.sin(np.arange(400))), index=idx)
        down = pd.Series(np.exp(-np.arange(400) * 0.005 + 0.001*np.sin(np.arange(400))), index=idx)
        close = pd.DataFrame({"UP": up, "DOWN": down})
        score = trend_score(close)
        self.assertGreater(float(score.iloc[-1]["UP"]), 0.0)
        self.assertLess(float(score.iloc[-1]["DOWN"]), 0.0)

    def test_target_normalizes_to_unit_gross(self):
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        close = pd.DataFrame({
            "A": np.exp(np.arange(400) * 0.004 + 0.01*np.sin(np.arange(400)/5)),
            "B": np.exp(-np.arange(400) * 0.003 + 0.01*np.cos(np.arange(400)/7)),
        }, index=idx)
        eligible = pd.DataFrame(True, index=idx, columns=close.columns)
        target, _, _ = normalized_target_weights(close, eligible)
        gross = float(target.iloc[-1].abs().sum())
        self.assertAlmostEqual(gross, 1.0, places=12)

    def test_ineligible_contract_gets_zero_target(self):
        idx = pd.date_range("2020-01-01", periods=400, freq="D")
        close = pd.DataFrame({"A": np.exp(np.arange(400) * 0.003), "B": np.exp(np.arange(400) * 0.002)}, index=idx)
        eligible = pd.DataFrame(True, index=idx, columns=close.columns)
        eligible.loc[idx[-1], "B"] = False
        target, _, _ = normalized_target_weights(close, eligible)
        self.assertAlmostEqual(float(target.loc[idx[-1], "B"]), 0.0, places=12)

    def test_missing_execution_return_zeroes_actual_held(self):
        idx = pd.date_range("2020-01-01", periods=5, freq="D")
        target = pd.DataFrame({"A": [0.0, 1.0, 1.0, 1.0, 1.0]}, index=idx)
        close = pd.DataFrame({"A": [100.0, 101.0, 102.0, np.nan, np.nan]}, index=idx)
        actual, _ = actual_held_weights(target, close)
        self.assertEqual(float(actual.loc[idx[3], "A"]), 0.0)


if __name__ == "__main__":
    unittest.main()
