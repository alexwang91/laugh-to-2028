from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

from research.brrk_beta_handoff_0047 import engine as source_engine
from research.brrk_beta_deterioration_btc_takeover_diagnostic_0059 import engine as scientific_engine
from research.brrk_beta_deterioration_btc_takeover_diagnostic_0059 import run_once


def frozen_flat_frames() -> dict[str, pd.DataFrame]:
    index = pd.date_range(scientific_engine.SOURCE_START, scientific_engine.SOURCE_END, freq="D")
    return {
        asset: pd.DataFrame({"close": np.full(len(index), 100.0, dtype=np.float64)}, index=index)
        for asset in scientific_engine.ASSETS
    }


class ControlledRunContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.synthetic_measurement = scientific_engine.evaluate_frozen_contract(
            frozen_flat_frames(), scientific_engine.EXPECTED_PAYLOAD_SHA256
        )
        assert cls.synthetic_measurement["actual_variants_evaluated"] == 1
        assert cls.synthetic_measurement["classification"] == "FAIL_INSUFFICIENT_CAUSAL_SUPPORT"
        assert cls.synthetic_measurement["shared_origin_count"] == 0

    def _measurement(self) -> dict:
        return copy.deepcopy(self.synthetic_measurement)

    def _paths(self, root: Path) -> dict[str, Path]:
        market = root / "synthetic-placeholder-market.json"
        market.write_text("{}\n", encoding="utf-8")
        return {
            "market": market,
            "result": root / "PRIMARY_RESULT.json",
            "execution": root / "EXECUTION.json",
            "attempt": root / "RUN_ATTEMPT.marker",
            "marker": root / "RUN_ONCE.marker",
        }

    @staticmethod
    def _interface() -> dict:
        return {
            "frozen_market_evidence": {
                "payload_sha256": scientific_engine.EXPECTED_PAYLOAD_SHA256
            }
        }

    @classmethod
    def _static_context(cls) -> tuple[str, dict]:
        return ("frozen-head", cls._interface())

    def _result(self, measurement: dict | None = None) -> dict:
        measurement = self._measurement() if measurement is None else measurement
        return {
            "schema_id": run_once.SCHEMA_ID,
            "research_id": scientific_engine.RESEARCH_ID,
            "dataset_slice_id": run_once.DATASET_SLICE_ID,
            "payload_sha256": scientific_engine.EXPECTED_PAYLOAD_SHA256,
            "execution_head_sha": "frozen-head",
            "classification": measurement["classification"],
            "measurement": measurement,
            "authority": run_once._authority(),
        }

    def test_flat_full_calendar_measurement_validates_losslessly(self) -> None:
        value = self._result()
        run_once.validate_result(value)
        self.assertEqual(value["measurement"]["shared_origin_count"], 0)
        self.assertEqual(value["measurement"]["origin_panel"], [])
        self.assertIsNone(value["measurement"]["full_sample_rho_by_horizon"])
        self.assertEqual(value["classification"], "FAIL_INSUFFICIENT_CAUSAL_SUPPORT")

    def test_preflight_is_zero_result_and_reads_no_market_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", side_effect=AssertionError("preflight must not read market")
            ) as reader, mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("preflight must not load frames")
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", side_effect=AssertionError("preflight must not evaluate")
            ) as evaluate:
                value = run_once.preflight(expected_head_sha="frozen-head", **paths)
            reader.assert_not_called()
            loader.assert_not_called()
            evaluate.assert_not_called()
            self.assertEqual(value["candidate_count"], 1)
            self.assertEqual(value["actual_variants_evaluated"], 0)
            self.assertFalse(value["market_content_read"])
            self.assertFalse(paths["attempt"].exists())

    def test_start_attempt_is_create_only_and_consumes_no_market_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", side_effect=AssertionError("start must not read market")
            ) as reader:
                attempt = run_once.start_attempt(expected_head_sha="frozen-head", **paths)
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing runtime artifacts"):
                    run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            reader.assert_not_called()
            self.assertEqual(attempt["candidate_count"], 1)
            self.assertFalse(attempt["same_id_recomputation_allowed"])
            self.assertFalse(attempt["same_id_retuning_allowed"])
            self.assertFalse(attempt["same_id_rescue_allowed"])

    def test_evaluate_refuses_loader_and_engine_before_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ) as reader, mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value={}
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "RUN_ATTEMPT.marker"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            reader.assert_not_called()
            loader.assert_not_called()
            evaluate.assert_not_called()

    def test_staged_attempt_evaluate_finalize_calls_real_path_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)

            frames = {asset: object() for asset in scientific_engine.ASSETS}
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ) as reader, mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            reader.assert_called_once()
            loader.assert_called_once_with({})
            evaluate.assert_called_once_with(
                {asset: frames[asset] for asset in scientific_engine.ASSETS},
                scientific_engine.EXPECTED_PAYLOAD_SHA256,
            )
            self.assertEqual(result["classification"], "FAIL_INSUFFICIENT_CAUSAL_SUPPORT")
            self.assertTrue(paths["result"].exists())
            self.assertTrue(paths["execution"].exists())
            self.assertFalse(paths["marker"].exists())

            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", side_effect=AssertionError("finalize must not read market")
            ) as reader2, mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("finalize must not load frames")
            ) as loader2, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", side_effect=AssertionError("finalize must not reevaluate")
            ) as evaluate2:
                marker = run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
            reader2.assert_not_called()
            loader2.assert_not_called()
            evaluate2.assert_not_called()
            self.assertTrue(marker["finalized_without_market_read"])
            self.assertTrue(marker["finalized_without_remeasurement"])
            self.assertEqual(marker["actual_variants_evaluated"], 1)
            self.assertFalse(marker["same_id_rerun_allowed"])

    def test_second_evaluate_is_blocked_without_second_loader_or_engine_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            frames = {asset: object() for asset in scientific_engine.ASSETS}
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ) as reader, mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            self.assertEqual(reader.call_count, 1)
            self.assertEqual(loader.call_count, 1)
            self.assertEqual(evaluate.call_count, 1)

    def test_partial_primary_result_blocks_automatic_recompute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            paths["result"].write_text(json.dumps(self._result(), indent=2) + "\n", encoding="utf-8")
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ) as reader, mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value={}
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            reader.assert_not_called()
            loader.assert_not_called()
            evaluate.assert_not_called()

    def test_source_protocol_error_becomes_persisted_invalid_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ), mock.patch.object(
                source_engine, "frames_from_market_evidence",
                side_effect=source_engine.FrozenProtocolError("synthetic source failure"),
            ), mock.patch.object(
                scientific_engine, "evaluate_frozen_contract",
                side_effect=AssertionError("engine must not run after source failure"),
            ) as evaluate:
                result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            evaluate.assert_not_called()
            self.assertEqual(result["classification"], "INVALID_EXECUTION")
            self.assertEqual(result["measurement"]["actual_variants_evaluated"], 1)
            self.assertTrue(paths["result"].exists())
            self.assertTrue(paths["execution"].exists())

    def test_engine_protocol_error_becomes_persisted_invalid_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            frames = {asset: object() for asset in scientific_engine.ASSETS}
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ), mock.patch.object(
                scientific_engine, "evaluate_frozen_contract",
                side_effect=scientific_engine.DiagnosticProtocolError("synthetic engine failure"),
            ):
                result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            self.assertEqual(result["classification"], "INVALID_EXECUTION")
            self.assertEqual(result["measurement"]["actual_variants_evaluated"], 1)

    def test_finalize_rejects_tampered_valid_result_hash_without_remeasurement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", return_value={}
            ), mock.patch.object(
                source_engine, "frames_from_market_evidence",
                side_effect=source_engine.FrozenProtocolError("original source failure"),
            ):
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)

            value = json.loads(paths["result"].read_text(encoding="utf-8"))
            value["measurement"]["error"] = "tampered but structurally valid error text"
            paths["result"].write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

            with mock.patch.object(
                run_once, "_verify_static_context", return_value=self._static_context()
            ), mock.patch.object(
                run_once, "_read_market_wrapper_once", side_effect=AssertionError("finalize must not read market")
            ) as reader, mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("finalize must not load frames")
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", side_effect=AssertionError("finalize must not reevaluate")
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "Primary result hash mismatch"):
                    run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
            reader.assert_not_called()
            loader.assert_not_called()
            evaluate.assert_not_called()
            self.assertFalse(paths["marker"].exists())

    def test_marker_only_recovery_requires_complete_result_and_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            paths["result"].write_text(json.dumps(self._result(), indent=2) + "\n", encoding="utf-8")
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()):
                with self.assertRaisesRegex(run_once.ControlledRunError, "missing persisted artifacts"):
                    run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
            self.assertFalse(paths["marker"].exists())

    def test_schema_rejects_origin_panel_count_mismatch(self) -> None:
        value = self._result()
        value["measurement"]["shared_origin_count"] = 1
        with self.assertRaisesRegex(run_once.ControlledRunError, "origin_panel row count mismatch"):
            run_once.validate_result(value)

    def test_schema_rejects_gate_classification_drift(self) -> None:
        value = self._result()
        value["measurement"]["gates"]["G1_SUPPORT"] = True
        with self.assertRaises(run_once.ControlledRunError):
            run_once.validate_result(value)

    def test_schema_rejects_extra_strategy_metric(self) -> None:
        value = self._result()
        value["measurement"]["portfolio_nav"] = [1.0]
        with self.assertRaisesRegex(run_once.ControlledRunError, "extra"):
            run_once.validate_result(value)

    def test_static_runner_contains_no_network_or_refetch_api(self) -> None:
        text = Path(run_once.__file__).read_text(encoding="utf-8")
        forbidden = (
            "requests.get",
            "fetch_daily_frame(",
            "api.binance",
            "data-api.binance",
            "source_engine.fetch",
        )
        for token in forbidden:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
