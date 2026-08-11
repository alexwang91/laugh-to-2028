from __future__ import annotations

import json
import unittest
from pathlib import Path

from research.brrk_leadership_rotation_0048 import run_once


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RID = "BRRK-LEADERSHIP-ROTATION-0048"
RESULT = "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT"
HEAD = "12f70c927df39b9e2ba799c8d4c597a7ae9b1726"


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class CloseoutContractTest(unittest.TestCase):
    def test_unique_result_identity_is_exact(self):
        result = load("PRIMARY_RESULT.json")
        summary = load("RESULT_SUMMARY.json")
        execution = load("EXECUTION.json")
        marker = load("RUN_ONCE.marker")
        closeout = load("CLOSEOUT.json")

        self.assertEqual(result["research_id"], RID)
        self.assertEqual(result["classification"], RESULT)
        self.assertEqual(summary["classification"], RESULT)
        self.assertEqual(execution["result_status"], RESULT)
        self.assertEqual(marker["result_status"], RESULT)
        self.assertEqual(closeout["result_status"], RESULT)
        self.assertEqual(closeout["closeout_status"], RESULT + " / CLOSED")
        self.assertEqual(result["execution_head_sha"], HEAD)
        self.assertEqual(execution["git_head_sha"], HEAD)
        self.assertEqual(marker["git_head_sha"], HEAD)

    def test_marker_hashes_bind_exact_existing_bundle(self):
        result = load("PRIMARY_RESULT.json")
        summary = load("RESULT_SUMMARY.json")
        execution = load("EXECUTION.json")
        attempt = load("RUN_ATTEMPT.marker")
        marker = load("RUN_ONCE.marker")

        self.assertEqual(marker["attempt_marker_sha256"], run_once._sha256(attempt))
        self.assertEqual(marker["primary_result_sha256"], run_once._sha256(result))
        self.assertEqual(marker["result_summary_sha256"], run_once._sha256(summary))
        self.assertEqual(marker["execution_sha256"], run_once._sha256(execution))
        self.assertEqual(execution["attempt_marker_sha256"], marker["attempt_marker_sha256"])
        self.assertEqual(execution["primary_result_sha256"], marker["primary_result_sha256"])
        self.assertEqual(execution["result_summary_sha256"], marker["result_summary_sha256"])

    def test_g1_support_stop_is_exact_and_bootstrap_did_not_run(self):
        result = load("PRIMARY_RESULT.json")
        closeout = load("CLOSEOUT.json")
        detail = result["classification_detail"]
        self.assertEqual(detail["gates"], {"G0": True, "G1": False})
        self.assertEqual(detail["support"]["full_blocks"], 4)
        self.assertEqual(detail["support"]["eth_leader_full_blocks"], 4)
        self.assertEqual(detail["support"]["sol_leader_full_blocks"], 4)
        self.assertFalse(detail["support"]["pass"])
        self.assertEqual(result["counts"]["formal_evaluation_rows"], 245)
        self.assertEqual(result["evaluation_window"], {"first_formal_date": "2025-01-14", "last_formal_date": "2026-05-10"})
        self.assertIsNone(result["bootstrap"])
        gate = closeout["support_gate_result"]
        self.assertEqual(gate["required_complete_56_observation_blocks"], 12)
        self.assertEqual(gate["observed_complete_56_observation_blocks"], 4)
        self.assertEqual(gate["minimum_formal_rows_implied_by_block_requirement"], 672)
        self.assertEqual(gate["formal_row_shortfall_vs_block_minimum"], 427)
        self.assertFalse(gate["bootstrap_executed"])

    def test_descriptive_metrics_are_preserved_but_non_authorizing(self):
        result = load("PRIMARY_RESULT.json")
        closeout = load("CLOSEOUT.json")
        self.assertAlmostEqual(result["proper_scores"]["candidate_nll"], 0.7185986814752551)
        self.assertAlmostEqual(result["proper_scores"]["baseline_nll"]["B0"], 0.6931471805599453)
        self.assertAlmostEqual(result["discrimination"]["auc"], 0.378946493851778)
        self.assertAlmostEqual(result["confidence_diagnostics"]["spearman_point"], -0.41118068940326613)
        authority = closeout["authority"]
        self.assertFalse(authority["leadership_information_established"])
        self.assertFalse(authority["concentration_research_0049_eligible_from_0048"])
        self.assertFalse(authority["portfolio_economics_executed"])
        self.assertFalse(authority["canonical_strategy_changed"])
        self.assertFalse(authority["phase6_changed"])
        self.assertFalse(authority["production_authorized"])
        self.assertFalse(authority["signature_authorized"])
        self.assertFalse(authority["order_submission_authorized"])

    def test_exactly_once_closure_is_permanent(self):
        attempt = load("RUN_ATTEMPT.marker")
        marker = load("RUN_ONCE.marker")
        closeout = load("CLOSEOUT.json")
        self.assertEqual(attempt["status"], "HISTORICAL_COMPUTATION_ATTEMPT_STARTED_NO_RERUN")
        self.assertFalse(attempt["same_id_recomputation_allowed_after_this_marker"])
        self.assertEqual(marker["status"], "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN")
        for key in ("same_id_rerun_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed"):
            self.assertFalse(marker[key])
            self.assertFalse(closeout["closure"][key])
        self.assertEqual(closeout["unique_scientific_execution"]["github_actions_run_id"], 31505757608)
        self.assertEqual(closeout["unique_scientific_execution"]["github_actions_job_id"], 93826791780)
        self.assertEqual(closeout["unique_scientific_execution"]["run_attempt"], 1)
        self.assertEqual(closeout["unique_scientific_execution"]["actual_variants_evaluated"], 1)

    def test_temporary_execution_workflow_is_not_in_closeout_tree(self):
        workflow_dir = ROOT / ".github" / "workflows"
        existing = {p.name for p in workflow_dir.glob("*.yml")}
        self.assertNotIn("_tmp_0048_exactly_once_execution.yml", existing)
        self.assertFalse((HERE / "portfolio.py").exists())
        self.assertFalse((HERE / "portfolio_result.json").exists())


if __name__ == "__main__":
    unittest.main()
