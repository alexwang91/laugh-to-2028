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

    def test_runner_has_no_network_or_portfolio_surface(self):
        text = (HERE / "run_once.py").read_text(encoding="utf-8")
        for forbidden in ("requests.get", "urlopen(", "fetch_daily_frame", "portfolio", "CAGR", "Sharpe", "MDD", "order_submission_authorized=True"):
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

    def test_current_controlled_branch_contains_no_runtime_result_artifacts(self):
        forbidden = {
            "PRIMARY_RESULT.json",
            "RESULT_SUMMARY.json",
            "EXECUTION.json",
            "RUN_ATTEMPT.marker",
            "RUN_ONCE.marker",
            "RESULT.md",
            "portfolio.py",
            "portfolio_result.json",
        }
        present = {p.name for p in HERE.iterdir() if p.is_file()}
        self.assertTrue(forbidden.isdisjoint(present))
        self.assertTrue({"run_once.py", "RUN_INTERFACE.json", "RESULT_SCHEMA.json"}.issubset(present))

    def test_schema_validator_rejects_unfrozen_classification(self):
        schema = json.loads((HERE / "RESULT_SCHEMA.json").read_text(encoding="utf-8"))
        result = {
            key: None for key in schema["required_top_level_keys"]
        }
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
