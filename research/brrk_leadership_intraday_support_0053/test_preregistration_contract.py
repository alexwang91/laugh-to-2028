import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

class Test0053Preregistration(unittest.TestCase):
    def test_prereg_and_registry_exact_match(self):
        p = json.loads((HERE / "PREREGISTRATION.json").read_text())
        reg = json.loads((ROOT / "config/research_registry.json").read_text())
        rows = [r for r in reg["records"] if r.get("research_id") == p["research_id"]]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], p)
        self.assertEqual(p["declared_variant_budget"], 1)
        self.assertEqual(p["actual_variants_evaluated"], 0)
        self.assertEqual(p["result_status"], "PREREGISTERED_DATA_NOT_CAPTURED")

    def test_primary_track_and_diagnostics_are_frozen(self):
        p = json.loads((HERE / "PREREGISTRATION.json").read_text())
        text = " ".join(p["researcher_decisions"])
        self.assertIn("Track A is primary: 2190", text)
        self.assertIn("336-row dependence block, 12 complete blocks required", text)
        self.assertIn("Track B is raw-row multiplication diagnostic only", text)
        self.assertIn("Track C is hybrid diagnostic only", text)

    def test_retrieval_contract_is_pre_capture(self):
        c = json.loads((HERE / "DATA_RETRIEVAL_CONTRACT.json").read_text())
        self.assertEqual(c["status"], "FROZEN_BEFORE_FIRST_4H_CAPTURE")
        self.assertEqual(c["source"]["interval"], "4h")
        self.assertEqual(c["source"]["symbols"], ["BTCUSDT", "ETHUSDT", "SOLUSDT"])
        self.assertEqual(c["source"]["requested_end_inclusive"], "2026-08-02T20:00:00Z")

    def test_no_result_or_dataset_capture_artifact_exists(self):
        forbidden = ["MARKET_4H_EVIDENCE.json", "DATASET_DECLARATION.json", "PRIMARY_RESULT.json", "RESULT_SUMMARY.json", "EXECUTION.json", "RUN_ONCE.marker"]
        for name in forbidden:
            self.assertFalse((HERE / name).exists(), name)

if __name__ == "__main__":
    unittest.main()
