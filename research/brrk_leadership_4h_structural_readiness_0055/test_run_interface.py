from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research.brrk_leadership_4h_structural_readiness_0055 import engine, run_once


class ControlledRunContractTests(unittest.TestCase):
    def _paths(self, root: Path) -> dict[str, Path]:
        return {
            "payload": root / "synthetic-placeholder-payload.json",
            "result": root / "METHOD_RESULT.json",
            "execution": root / "EXECUTION.json",
            "attempt": root / "RUN_ATTEMPT.marker",
            "marker": root / "RUN_ONCE.marker",
        }

    @staticmethod
    def _measurement(classification: str = "FAIL_4H_STRUCTURAL_3D_TRAINING_PRECISION_NOT_ESTABLISHED") -> dict:
        return {
            "research_id": engine.RESEARCH_ID,
            "classification": classification,
            "training_readiness": None,
            "calibration_readiness": None,
            "reserved_support": None,
            "training_records": [],
            "calibration_records": [],
            "authority": run_once._authority(),
        }

    @staticmethod
    def _context() -> tuple[str, str]:
        return ("frozen-head", engine.EXPECTED_PAYLOAD_SHA256)

    def test_evaluate_refuses_engine_before_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                engine, "measure_frozen_readiness", return_value=self._measurement()
            ) as measure:
                with self.assertRaisesRegex(RuntimeError, "RUN_ATTEMPT.marker"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                measure.assert_not_called()

    def test_staged_attempt_evaluate_finalize_calls_engine_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                attempt = run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            self.assertTrue(paths["attempt"].exists())
            self.assertFalse(attempt["same_id_recomputation_allowed"])

            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                engine, "measure_frozen_readiness", return_value=self._measurement()
            ) as measure:
                result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                measure.assert_called_once()
            self.assertEqual(result["classification"], "FAIL_4H_STRUCTURAL_3D_TRAINING_PRECISION_NOT_ESTABLISHED")
            self.assertTrue(paths["result"].exists())
            self.assertTrue(paths["execution"].exists())
            self.assertFalse(paths["marker"].exists())

            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                engine, "measure_frozen_readiness", side_effect=AssertionError("finalize must never remeasure")
            ) as measure:
                marker = run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
                measure.assert_not_called()
            self.assertTrue(paths["marker"].exists())
            self.assertTrue(marker["finalized_without_remeasurement"])
            self.assertFalse(marker["same_id_rerun_allowed"])
            self.assertFalse(marker["same_id_retuning_allowed"])
            self.assertFalse(marker["same_id_rescue_allowed"])

    def test_second_start_or_evaluate_is_create_only_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
                with self.assertRaisesRegex(RuntimeError, "existing runtime artifacts"):
                    run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                engine, "measure_frozen_readiness", return_value=self._measurement()
            ) as measure:
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(measure.call_count, 1)
                with self.assertRaisesRegex(RuntimeError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(measure.call_count, 1)

    def test_finalize_rejects_tampered_result_without_remeasurement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                engine, "measure_frozen_readiness", return_value=self._measurement()
            ):
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            value = json.loads(paths["result"].read_text())
            value["measurement"]["training_records"] = [{"tampered": True}]
            paths["result"].write_text(json.dumps(value, indent=2) + "\n")
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                engine, "measure_frozen_readiness", side_effect=AssertionError("finalize must never remeasure")
            ) as measure:
                with self.assertRaisesRegex(RuntimeError, "Method result hash mismatch"):
                    run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
                measure.assert_not_called()
                self.assertFalse(paths["marker"].exists())

    def test_schema_rejects_predictive_metric_key(self) -> None:
        schema = run_once._schema()
        value = {
            "schema_id": schema["schema_id"],
            "research_id": engine.RESEARCH_ID,
            "dataset_slice_id": schema["dataset_slice_id"],
            "payload_sha256": schema["payload_sha256"],
            "execution_head_sha": "x",
            "classification": "FAIL_4H_STRUCTURAL_3D_TRAINING_PRECISION_NOT_ESTABLISHED",
            "measurement": {**self._measurement(), "candidate_nll": 0.5},
            "authority": run_once._authority(),
        }
        with self.assertRaisesRegex(RuntimeError, "Forbidden predictive/economic metric"):
            run_once.validate_result(value, schema)

    def test_runtime_artifact_names_are_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            run_once._verify_runtime_names(paths["result"], paths["execution"], paths["attempt"], paths["marker"])
            with self.assertRaisesRegex(RuntimeError, "filenames differ"):
                run_once._verify_runtime_names(Path(tmp) / "WRONG.json", paths["execution"], paths["attempt"], paths["marker"])


if __name__ == "__main__":
    unittest.main()
