import unittest
import pandas as pd

from run_audit_0026_semantic_risk import first_crossing


class SemanticRiskAuditTests(unittest.TestCase):
    def test_first_crossing(self):
        idx = pd.date_range("2026-01-01", periods=4, freq="D")
        frame = pd.DataFrame({
            "p_riskoff": [0.1,0.2,0.55,0.8],
            "days_after_refit": [0,1,2,3],
        }, index=idx)
        out = first_crossing(frame, 0.5)
        self.assertEqual(out["date"], "2026-01-03")
        self.assertEqual(out["days_after_refit"], 2)

    def test_no_crossing(self):
        idx = pd.date_range("2026-01-01", periods=2, freq="D")
        frame = pd.DataFrame({"p_riskoff":[0.1,0.2],"days_after_refit":[0,1]}, index=idx)
        self.assertIsNone(first_crossing(frame,0.5)["date"])


if __name__ == "__main__":
    unittest.main()
