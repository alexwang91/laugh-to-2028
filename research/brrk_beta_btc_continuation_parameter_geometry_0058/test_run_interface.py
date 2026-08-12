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
from research.brrk_beta_btc_continuation_parameter_geometry_0058 import engine as scientific_engine
from research.brrk_beta_btc_continuation_parameter_geometry_0058 import run_once


def frozen_flat_frames() -> dict[str, pd.DataFrame]:
    index = pd.date_range(scientific_engine.SOURCE_START, scientific_engine.TERMINAL_CLOSE, freq="D")
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
        assert cls.synthetic_measurement["actual_variants_evaluated"] == 108
        assert cls.synthetic_measurement["classification"] == "FAIL_STABLE_PLATEAU_NOT_COST_ROBUST"

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
    def _context() -> tuple[str, str]:
        return ("frozen-head", scientific_engine.EXPECTED_PAYLOAD_SHA256)

    @staticmethod
    def _static_context() -> tuple[str, dict]:
        return (
            "frozen-head",
            {"frozen_market_evidence": {"payload_sha256": scientific_engine.EXPECTED_PAYLOAD_SHA256}},
        )

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

    def test_full_synthetic_measurement_validates_losslessly(self) -> None:
        value = self._result()
        run_once.validate_result(value)
        measurement = value["measurement"]
        self.assertEqual(len(measurement["surface_table_every_cell_every_cost"]), 324)
        self.assertEqual(len(measurement["geometry_every_interior_cell_every_cost"]), 210)
        self.assertEqual(len(measurement["selected_representative_daily_path"]), 1942)
        self.assertEqual(len(measurement["benchmark_daily_paths"]), 5826)

    def test_preflight_is_zero_result_and_does_not_call_loader_or_engine(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("preflight must not load frames")
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", side_effect=AssertionError("preflight must not evaluate")
            ) as evaluate:
                value = run_once.preflight(expected_head_sha="frozen-head", **paths)
            loader.assert_not_called()
            evaluate.assert_not_called()
            self.assertEqual(value["actual_variants_evaluated"], 0)
            self.assertEqual(value["candidate_count"], 108)
            self.assertFalse(paths["attempt"].exists())

    def test_evaluate_refuses_engine_before_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value={asset: object() for asset in scientific_engine.ASSETS}
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "RUN_ATTEMPT.marker"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            loader.assert_not_called()
            evaluate.assert_not_called()

    def test_staged_attempt_evaluate_finalize_calls_engine_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                attempt = run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            self.assertEqual(attempt["candidate_count"], 108)
            self.assertFalse(attempt["same_id_recomputation_allowed"])
            frames = {asset: object() for asset in scientific_engine.ASSETS}
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            loader.assert_called_once_with({})
            evaluate.assert_called_once_with(
                {asset: frames[asset] for asset in scientific_engine.ASSETS},
                scientific_engine.EXPECTED_PAYLOAD_SHA256,
            )
            self.assertEqual(result["classification"], "FAIL_STABLE_PLATEAU_NOT_COST_ROBUST")
            self.assertTrue(paths["result"].exists())
            self.assertTrue(paths["execution"].exists())
            self.assertFalse(paths["marker"].exists())

            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("finalize must never load market")
            ) as loader2, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", side_effect=AssertionError("finalize must never reevaluate")
            ) as evaluate2:
                marker = run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
            loader2.assert_not_called()
            evaluate2.assert_not_called()
            self.assertTrue(paths["marker"].exists())
            self.assertTrue(marker["finalized_without_remeasurement"])
            self.assertEqual(marker["actual_variants_evaluated"], 108)
            self.assertFalse(marker["same_id_rerun_allowed"])
            self.assertFalse(marker["same_id_retuning_allowed"])
            self.assertFalse(marker["same_id_rescue_allowed"])

    def test_second_start_and_second_evaluate_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing runtime artifacts"):
                    run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            frames = {asset: object() for asset in scientific_engine.ASSETS}
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ), mock.patch.object(scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()) as evaluate:
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(evaluate.call_count, 1)
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(evaluate.call_count, 1)

    def test_partial_primary_result_blocks_automatic_recompute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            paths["result"].write_text(json.dumps(self._result(), indent=2) + "\n", encoding="utf-8")
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value={asset: object() for asset in scientific_engine.ASSETS}
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            loader.assert_not_called()
            evaluate.assert_not_called()

    def test_protocol_errors_become_invalid_execution_without_retry(self) -> None:
        cases = (
            (source_engine.FrozenProtocolError("synthetic source failure"), True),
            (scientific_engine.ParameterGeometryProtocolError("synthetic engine failure"), False),
        )
        for exc, source_fails in cases:
            with self.subTest(type=type(exc).__name__), tempfile.TemporaryDirectory() as tmp:
                paths = self._paths(Path(tmp))
                with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                    run_once.start_attempt(expected_head_sha="frozen-head", **paths)
                frames = {asset: object() for asset in scientific_engine.ASSETS}
                with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                    source_engine,
                    "frames_from_market_evidence",
                    return_value=mock.DEFAULT if source_fails else frames,
                    side_effect=exc if source_fails else None,
                ), mock.patch.object(
                    scientific_engine,
                    "evaluate_frozen_contract",
                    return_value=mock.DEFAULT if not source_fails else self._measurement(),
                    side_effect=exc if not source_fails else None,
                ):
                    result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(result["classification"], "INVALID_EXECUTION")
                self.assertEqual(result["measurement"]["actual_variants_evaluated"], 108)
                self.assertTrue(paths["result"].exists())
                self.assertTrue(paths["execution"].exists())
                self.assertFalse(paths["marker"].exists())

    def test_finalize_rejects_tampered_result_without_remeasurement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            frames = {asset: object() for asset in scientific_engine.ASSETS}
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ), mock.patch.object(scientific_engine, "evaluate_frozen_contract", return_value=self._measurement()):
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            value = json.loads(paths["result"].read_text(encoding="utf-8"))
            value["measurement"]["diagnostics"]["calendar_year_returns_2021_partial_through_2026_partial"]["2021"] += 0.000001
            paths["result"].write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("finalize must never reload")
            ) as loader, mock.patch.object(
                scientific_engine, "evaluate_frozen_contract", side_effect=AssertionError("finalize must never reevaluate")
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "Primary result hash mismatch"):
                    run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
            loader.assert_not_called()
            evaluate.assert_not_called()
            self.assertFalse(paths["marker"].exists())

    def test_schema_rejects_missing_surface_cell(self) -> None:
        value = self._result()
        value["measurement"]["surface_table_every_cell_every_cost"].pop()
        with self.assertRaisesRegex(run_once.ControlledRunError, "surface row count"):
            run_once.validate_result(value)

    def test_schema_rejects_geometry_not_derived_from_surface(self) -> None:
        value = self._result()
        value["measurement"]["geometry_every_interior_cell_every_cost"][0]["D_L"] += 0.01
        with self.assertRaisesRegex(run_once.ControlledRunError, "D_L mismatch"):
            run_once.validate_result(value)

    def test_schema_rejects_truncated_selected_path(self) -> None:
        value = self._result()
        value["measurement"]["selected_representative_daily_path"].pop()
        with self.assertRaisesRegex(run_once.ControlledRunError, "daily path row count"):
            run_once.validate_result(value)

    def test_schema_rejects_forbidden_predictive_metric(self) -> None:
        value = self._result()
        value["measurement"]["diagnostics"]["candidate_auc"] = 0.5
        with self.assertRaises(run_once.ControlledRunError):
            run_once.validate_result(value)

    def test_static_runner_contains_no_network_or_refetch_api(self) -> None:
        text = Path(run_once.__file__).read_text(encoding="utf-8")
        forbidden = ("requests.get", "fetch_daily_frame(", "api.binance", "data-api.binance")
        for token in forbidden:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
