from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research.brrk_leadership_rotation_0048 import engine, run_once


HERE = Path(__file__).resolve().parent


class RunInterfaceContractTest(unittest.TestCase):
    def test_interface_binds_exact_frozen_upstream(self):
        interface = json.loads((HERE / "RUN_INTERFACE.json").read_text(encoding="utf-8"))
        self.assertEqual(interface["research_id"], engine.RESEARCH_ID)
        self.assertEqual(interface["controlled_execution_base_main_sha"], "a60696d5fe23e5dd95c40f868ccca199f36a3c20")
        self.assertEqual(interface["frozen_market_evidence"]["payload_sha256"], engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256)
        self.assertEqual(interface["frozen_market_evidence"]["git_blob_sha"], "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe")
        self.assertEqual(interface["actual_variants_evaluated"], 0)
        self.assertEqual(interface["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertFalse(interface["execution_authority"]["historical_execution_authorized_before_this_interface_merges_green"])
        self.assertFalse(interface["exactly_once_policy"]["same_id_rerun_allowed"])
        self.assertIn("RUN_ATTEMPT.marker", interface["commands"]["evaluate"])
        self.assertIn("recover-marker", interface["commands"]["recover_marker_only"])

    def test_result_schema_freezes_classification_and_no_portfolio_authority(self):
        schema = json.loads((HERE / "RESULT_SCHEMA.json").read_text(encoding="utf-8"))
        expected = {
            "INVALID_EXECUTION",
            "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT",
            "MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE",
            "FAIL_NO_INCREMENTAL_DYNAMIC_LEADERSHIP",
            "FAIL_NO_ROBUST_DYNAMIC_LEADERSHIP",
            "PASS_LEADERSHIP_INFORMATION_NO_CONCENTRATION_HANDOFF",
            "PASS_ONE_SIDED_LEADERSHIP_NO_FULL_ROUTER",
            "PASS_LEADERSHIP_INFORMATION_CONCENTRATION_HANDOFF_ELIGIBLE",
        }
        self.assertEqual(set(schema["classification_enum"]), expected)
        authority = schema["authority_invariants"]
        self.assertTrue(authority["development_not_independent_oos"])
        self.assertFalse(authority["portfolio_economics_executed"])
        self.assertFalse(authority["canonical_strategy_changed"])
        self.assertFalse(authority["phase6_changed"])
        self.assertFalse(authority["production_authorized"])
        self.assertFalse(authority["same_id_rerun_allowed"])

    def test_runner_has_no_network_or_portfolio_execution_surface(self):
        text = (HERE / "run_once.py").read_text(encoding="utf-8")
        for forbidden in (
            "requests.get",
            "urlopen(",
            "fetch_daily_frame",
            "def portfolio",
            "portfolio_result.json",
            "CAGR",
            "Sharpe",
            "MDD",
            "submit_order",
            "place_order",
            "sign_transaction",
        ):
            self.assertNotIn(forbidden, text)

    def test_attempt_marker_is_written_before_historical_computation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            market = root / "market.json"
            output = root / "PRIMARY_RESULT.json"
            summary = root / "RESULT_SUMMARY.json"
            execution = root / "EXECUTION.json"
            attempt = root / "RUN_ATTEMPT.marker"
            marker = root / "RUN_ONCE.marker"
            market.write_text("{}", encoding="utf-8")
            preflight = {
                "research_id": engine.RESEARCH_ID,
                "status": "PREFLIGHT_PASS_ZERO_RESULT",
                "git_head_sha": "abc123",
                "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
                "actual_variants_evaluated": 0,
                "historical_model_evaluation_started": False,
                "production_authorized": False,
                "signature_authorized": False,
                "order_submission_authorized": False,
            }
            with mock.patch.object(run_once, "_static_preflight", return_value=preflight), mock.patch.object(
                run_once, "_interface", return_value={"status": "CONTROLLED_EXECUTION_INTERFACE_FROZEN_NOT_RUN"}
            ), mock.patch.object(run_once, "_schema", return_value={"schema_id": "BRRK-LEADERSHIP-ROTATION-0048-PRIMARY-RESULT-V1"}), mock.patch.object(
                run_once, "_build_result", side_effect=RuntimeError("synthetic crash after attempt start")
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic crash"):
                    run_once.evaluate(market, output, summary, execution, attempt, marker, "abc123")
            self.assertTrue(attempt.exists())
            self.assertFalse(output.exists())
            self.assertFalse(summary.exists())
            self.assertFalse(execution.exists())
            self.assertFalse(marker.exists())
            record = json.loads(attempt.read_text(encoding="utf-8"))
            self.assertEqual(record["status"], "HISTORICAL_COMPUTATION_ATTEMPT_STARTED_NO_RERUN")
            self.assertFalse(record["same_id_recomputation_allowed_after_this_marker"])

    def test_marker_recovery_validates_existing_bundle_without_model_recomputation(self):
        schema = json.loads((HERE / "RESULT_SCHEMA.json").read_text(encoding="utf-8"))
        interface = {
            "frozen_market_evidence": {"payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256},
            "immutable_upstream_git_blobs": {},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "PRIMARY_RESULT.json"
            summary = root / "RESULT_SUMMARY.json"
            execution = root / "EXECUTION.json"
            attempt = root / "RUN_ATTEMPT.marker"
            marker = root / "RUN_ONCE.marker"
            head = "abc123"
            result = {
                "schema_id": schema["schema_id"],
                "research_id": engine.RESEARCH_ID,
                "dataset_slice_id": engine.DATASET_SLICE_ID,
                "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
                "execution_head_sha": head,
                "classification": "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT",
                "classification_detail": {"gates": {"G0": True, "G1": False}},
                "evaluation_window": {"first_formal_date": None, "last_formal_date": None},
                "counts": {"formal_predictions": 0, "formal_evaluation_rows": 0, "eligible_feature_valid_origins": 0, "target_ties": 0},
                "proper_scores": {"candidate_nll": None, "baseline_nll": {"B0": None, "B1": None, "B2": None, "B3": None}, "candidate_brier": None, "baseline_brier": {"B0": None, "B1": None, "B2": None, "B3": None}},
                "discrimination": {"auc": None, "balanced_accuracy": None, "direction_metrics": {}},
                "bootstrap": None,
                "confidence_diagnostics": {"spearman_point": None, "natural_cubic_spline": None, "segmented_breakpoint": None, "high_support": None, "nonselection_calibration_diagnostics": {}},
                "formal_evaluation_rows": [],
                "formal_evaluation_rows_sha256": run_once._sha256([]),
                "authority": dict(schema["authority_invariants"]),
            }
            summary_record = {"research_id": engine.RESEARCH_ID, "classification": result["classification"]}
            attempt_record = {"research_id": engine.RESEARCH_ID, "git_head_sha": head, "status": "HISTORICAL_COMPUTATION_ATTEMPT_STARTED_NO_RERUN"}
            execution_record = {
                "research_id": engine.RESEARCH_ID,
                "git_head_sha": head,
                "primary_result_sha256": run_once._sha256(result),
                "result_summary_sha256": run_once._sha256(summary_record),
                "attempt_marker_sha256": run_once._sha256(attempt_record),
            }
            for path, value in ((output, result), (summary, summary_record), (execution, execution_record), (attempt, attempt_record)):
                path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

            with mock.patch.object(run_once, "_interface", return_value=interface), mock.patch.object(
                run_once, "_schema", return_value=schema
            ), mock.patch.object(run_once, "_verify_expected_head", return_value=head), mock.patch.object(
                run_once, "_verify_upstream_blobs"
            ), mock.patch.object(run_once, "_build_result", side_effect=AssertionError("model recomputation forbidden")) as build:
                run_once.recover_marker(output, summary, execution, attempt, marker, head)
            build.assert_not_called()
            self.assertTrue(marker.exists())
            recovered = json.loads(marker.read_text(encoding="utf-8"))
            self.assertTrue(recovered["recovered_without_model_recomputation"])
            self.assertEqual(recovered["result_status"], result["classification"])

    def test_immutable_runtime_bundle_is_complete_and_closed(self):
        required = {
            "PRIMARY_RESULT.json",
            "RESULT_SUMMARY.json",
            "EXECUTION.json",
            "RUN_ATTEMPT.marker",
            "RUN_ONCE.marker",
            "RESULT.md",
            "CLOSEOUT.json",
        }
        present = {p.name for p in HERE.iterdir() if p.is_file()}
        self.assertTrue(required.issubset(present), sorted(required - present))
        self.assertNotIn("portfolio.py", present)
        self.assertNotIn("portfolio_result.json", present)

        marker = json.loads((HERE / "RUN_ONCE.marker").read_text(encoding="utf-8"))
        summary = json.loads((HERE / "RESULT_SUMMARY.json").read_text(encoding="utf-8"))
        closeout = json.loads((HERE / "CLOSEOUT.json").read_text(encoding="utf-8"))
        self.assertEqual(marker["status"], "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN")
        self.assertEqual(marker["result_status"], "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT")
        self.assertEqual(summary["classification"], marker["result_status"])
        self.assertEqual(closeout["result_status"], marker["result_status"])
        self.assertFalse(marker["same_id_rerun_allowed"])
        self.assertFalse(marker["same_id_retuning_allowed"])
        self.assertFalse(marker["same_id_rescue_allowed"])

    def test_schema_validator_rejects_unfrozen_classification(self):
        schema = json.loads((HERE / "RESULT_SCHEMA.json").read_text(encoding="utf-8"))
        result = {key: None for key in schema["required_top_level_keys"]}
        result.update(
            {
                "schema_id": schema["schema_id"],
                "research_id": engine.RESEARCH_ID,
                "classification": "POST_HOC_RESCUE_PASS",
                "formal_evaluation_rows": [],
                "formal_evaluation_rows_sha256": run_once._sha256([]),
                "authority": dict(schema["authority_invariants"]),
            }
        )
        with self.assertRaisesRegex(RuntimeError, "classification is not frozen"):
            run_once._validate_result(result, schema)


if __name__ == "__main__":
    unittest.main()
