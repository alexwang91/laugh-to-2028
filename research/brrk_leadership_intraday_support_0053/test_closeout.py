from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Test0053Closeout(unittest.TestCase):
    def setUp(self):
        self.result = json.loads((HERE / "SUPPORT_RESULT.json").read_text())
        self.execution = json.loads((HERE / "EXECUTION.json").read_text())
        self.attempt = json.loads((HERE / "RUN_ATTEMPT.marker").read_text())
        self.marker = json.loads((HERE / "RUN_ONCE.marker").read_text())
        self.closeout = json.loads((HERE / "CLOSEOUT.json").read_text())

    def test_exact_result_identity(self):
        self.assertEqual(self.result["classification"], "FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT")
        self.assertEqual(self.result["payload_sha256"], "471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135")
        self.assertEqual(self.result["execution_head_sha"], "4de5b8b97075d5614b2dad121b6eb0d93b4def24")
        self.assertEqual(self.marker["status"], "VALID_SUPPORT_MEASUREMENT_COMPLETE_CLOSED_TO_SAME_ID_RERUN")
        self.assertFalse(self.marker["same_id_rerun_allowed"])
        self.assertFalse(self.marker["same_id_retuning_allowed"])
        self.assertFalse(self.marker["same_id_rescue_allowed"])

    def test_hash_bindings(self):
        def sha(path: Path) -> str:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(sha(HERE / "RUN_ATTEMPT.marker"), "037fa7ca0aef037a7233b3811e91e9cdab37d7fbcb27a2b2f454fe7451859f54")
        self.assertEqual(sha(HERE / "SUPPORT_RESULT.json"), "8228dfb88dc609289c53072a28dcb127b30d866b22d88704eb15c726eca841e5")
        self.assertEqual(sha(HERE / "EXECUTION.json"), "ee73c7f57130ecc0e1365040da90d9596c03a1563a7f85d2a8a2e2c2fe5731db")
        self.assertEqual(self.execution["attempt_marker_sha256"], sha(HERE / "RUN_ATTEMPT.marker"))
        self.assertEqual(self.execution["support_result_sha256"], sha(HERE / "SUPPORT_RESULT.json"))
        self.assertEqual(self.marker["execution_sha256"], sha(HERE / "EXECUTION.json"))

    def test_track_a_binding_failure(self):
        a = self.result["measurement"]["tracks"]["A"]
        self.assertEqual(a["formal_rows"], 1468)
        self.assertEqual(a["complete_blocks"], 4)
        self.assertEqual(a["block_length"], 336)
        self.assertEqual(a["training_support_required"], 2190)
        self.assertEqual(a["shadow_support_required"], 2190)
        self.assertLess(a["complete_blocks"], 12)

    def test_diagnostics_preserved_but_non_authorizing(self):
        b = self.result["measurement"]["tracks"]["B"]
        c = self.result["measurement"]["tracks"]["C"]
        self.assertEqual(b["complete_blocks"], 98)
        self.assertEqual(c["complete_blocks"], 16)
        self.assertEqual(b["authority"], "DIAGNOSTIC_RAW_ROW_MULTIPLICATION_ONLY")
        self.assertEqual(c["authority"], "DIAGNOSTIC_HYBRID_EARLIER_BURNIN_ONLY")
        self.assertEqual(self.result["classification"], "FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT")

    def test_row_frequency_result(self):
        cmp = self.result["comparison_vs_0048"]
        self.assertEqual(cmp["0048_formal_rows"], 245)
        self.assertEqual(cmp["0053_track_a_formal_rows"], 1468)
        self.assertAlmostEqual(cmp["formal_row_ratio_0053A_to_0048"], 5.9918367346938775)
        self.assertEqual(cmp["0048_complete_blocks"], 4)
        self.assertEqual(cmp["0053_track_a_complete_blocks"], 4)
        self.assertEqual(cmp["complete_block_difference"], 0)

    def test_no_predictive_or_portfolio_authority(self):
        authority = self.result["authority"]
        for key in [
            "winner_labels_executed",
            "predictive_model_executed",
            "calibration_model_executed",
            "predictive_metrics_executed",
            "portfolio_economics_executed",
            "0048_rerun_or_rescue_executed",
            "canonical_strategy_changed",
            "phase6_changed",
            "production_authorized",
            "signature_authorized",
            "order_submission_authorized",
            "same_id_rerun_allowed",
            "same_id_retuning_allowed",
            "same_id_rescue_allowed",
        ]:
            self.assertFalse(authority[key], key)

    def test_closeout_matches_result(self):
        self.assertEqual(self.closeout["result_status"], self.result["classification"])
        self.assertEqual(self.closeout["track_A_primary_calendar_equivalent"]["complete_blocks"], 4)
        self.assertEqual(self.closeout["track_C_hybrid_diagnostic"]["complete_blocks"], 16)
        self.assertFalse(self.closeout["next_research_implication"]["0048_rescue_allowed"])
        self.assertFalse(self.closeout["next_research_implication"]["0049_concentration_unlocked"])


if __name__ == "__main__":
    unittest.main()
