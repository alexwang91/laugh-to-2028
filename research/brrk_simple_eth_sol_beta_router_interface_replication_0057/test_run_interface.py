from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from research.brrk_beta_handoff_0047 import engine as source_engine
from research.brrk_simple_eth_sol_beta_router_0056 import engine as scientific_engine
from research.brrk_simple_eth_sol_beta_router_interface_replication_0057 import adapter, run_once


class ControlledRunContractTests(unittest.TestCase):
    def _paths(self, root: Path) -> dict[str, Path]:
        market = root / "synthetic-placeholder-market.json"
        market.write_text("{}\n")
        return {
            "market": market,
            "result": root / "PRIMARY_RESULT.json",
            "execution": root / "EXECUTION.json",
            "attempt": root / "RUN_ATTEMPT.marker",
            "marker": root / "RUN_ONCE.marker",
        }

    @staticmethod
    def _context() -> tuple[str, str]:
        return ("frozen-head", adapter.EXPECTED_PAYLOAD_SHA256)

    @staticmethod
    def _static_context() -> tuple[str, dict]:
        return (
            "frozen-head",
            {"frozen_market_evidence": {"payload_sha256": adapter.EXPECTED_PAYLOAD_SHA256}},
        )

    @staticmethod
    def _measurement(classification: str = "PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY") -> dict:
        if classification != "PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY":
            raise AssertionError("Synthetic success helper is intentionally PASS-only")
        arm_values = {
            "ROUTER": (2.00, 1.0),
            "B0_STATIC_ETH": (1.50, 1.0),
            "B1_STATIC_SOL": (1.40, 1.0),
            "B2_STATIC_50_50": (1.45, 1.0),
        }
        metrics = {}
        advantages = {}
        for cost in ("5", "10", "20"):
            metrics[cost] = {}
            for name, (wealth, turnover) in arm_values.items():
                metrics[cost][name] = {
                    "terminal_wealth": wealth,
                    "cagr": wealth ** (scientific_engine.ANNUALIZATION_DAYS / scientific_engine.HELD_PERIODS) - 1.0,
                    "maximum_drawdown": -0.20,
                    "total_executed_l1_turnover": turnover,
                }
            advantages[cost] = {
                "B0_STATIC_ETH": math.log(2.00 / 1.50),
                "B1_STATIC_SOL": math.log(2.00 / 1.40),
                "B2_STATIC_50_50": math.log(2.00 / 1.45),
            }
        return {
            "research_id": adapter.RESEARCH_ID,
            "classification": classification,
            "gates": {
                "G0_INTEGRITY": True,
                "G1_PRIMARY_ECONOMIC_DOMINANCE_5BPS": True,
                "G2_COST_SURVIVAL": True,
                "G3_TEMPORAL_ROBUSTNESS": True,
                "G4_DEPENDENCE_AWARE_ROBUSTNESS": True,
            },
            "rm60_origin_count": scientific_engine.HELD_PERIODS,
            "target_count": scientific_engine.HELD_PERIODS,
            "targets": tuple(["ETH"] * scientific_engine.HELD_PERIODS),
            "metrics_by_cost_bps": metrics,
            "log_terminal_advantage_by_cost_bps": advantages,
            "best_static_5bps": "B0_STATIC_ETH",
            "temporal_block_relative_log_growth_vs_best_static_5bps": (0.1, 0.1, 0.1, 0.1),
            "temporal_positive_block_count": 4,
            "bootstrap_5bps": {
                "means": (0.001, 0.0011, 0.0012),
                "q95": 0.0002,
                "lcbs": (0.0008, 0.0009, 0.0010),
                "benchmarks": scientific_engine.BENCHMARKS,
                "replicates": scientific_engine.BOOTSTRAP_REPLICATES,
                "block_length": scientific_engine.BOOTSTRAP_BLOCK_LENGTH,
                "blocks_per_replicate_before_truncation": scientific_engine.BOOTSTRAP_BLOCKS_PER_REPLICATE,
                "seed": scientific_engine.BOOTSTRAP_SEED,
            },
            "diagnostics": {
                "maximum_drawdown_5bps": {name: -0.20 for name in ("ROUTER", *scientific_engine.BENCHMARKS)},
                "router_total_executed_l1_turnover_5bps": 1.0,
                "router_switch_count": 0,
                "router_average_holding_duration_days": float(scientific_engine.HELD_PERIODS),
                "router_median_holding_duration_days": float(scientific_engine.HELD_PERIODS),
                "router_holding_spell_count": 1,
                "longest_underperformance_interval_days_vs_b_star_5bps": 0,
                "calendar_year_returns_5bps": {
                    name: {"2020": 0.01, "2021": 0.02}
                    for name in ("ROUTER", *scientific_engine.BENCHMARKS)
                },
            },
            "actual_variants_evaluated": 1,
            "authority": run_once._measurement_authority(),
            "delegated_scientific_engine": {
                "research_id": adapter.BOUND_0056_RESEARCH_ID,
                "git_blob_sha": adapter.BOUND_0056_ENGINE_BLOB_SHA,
                "portfolio_outputs_modified_by_0057_adapter": False,
            },
            "source_interface_adapter": {
                "source_timezone_representation": "UTC_NORMALIZED_TZ_NAIVE_DAILY_DATES",
                "operation": "COPY_THEN_INDEX_TZ_LOCALIZE_UTC_ONLY",
                "calendar_order_rowcount_close_values_changed": False,
            },
        }

    def test_evaluate_refuses_adapter_before_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                adapter, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "RUN_ATTEMPT.marker"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                evaluate.assert_not_called()

    def test_staged_attempt_evaluate_finalize_calls_adapter_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                attempt = run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            self.assertTrue(paths["attempt"].exists())
            self.assertFalse(attempt["same_id_recomputation_allowed"])

            frames = {"BTC": object(), "ETH": object(), "SOL": object()}
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ) as loader, mock.patch.object(
                adapter, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                loader.assert_called_once_with({})
                evaluate.assert_called_once_with(
                    {"ETH": frames["ETH"], "SOL": frames["SOL"]}, adapter.EXPECTED_PAYLOAD_SHA256
                )
            self.assertEqual(result["classification"], "PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY")
            self.assertTrue(paths["result"].exists())
            self.assertTrue(paths["execution"].exists())
            self.assertFalse(paths["marker"].exists())

            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("finalize must never load market")
            ) as loader, mock.patch.object(
                adapter, "evaluate_frozen_contract", side_effect=AssertionError("finalize must never reevaluate")
            ) as evaluate:
                marker = run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
                loader.assert_not_called()
                evaluate.assert_not_called()
            self.assertTrue(paths["marker"].exists())
            self.assertTrue(marker["finalized_without_remeasurement"])
            self.assertFalse(marker["same_id_rerun_allowed"])
            self.assertFalse(marker["same_id_retuning_allowed"])
            self.assertFalse(marker["same_id_rescue_allowed"])

    def test_second_start_or_evaluate_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing runtime artifacts"):
                    run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            frames = {"ETH": object(), "SOL": object(), "BTC": object()}
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ), mock.patch.object(adapter, "evaluate_frozen_contract", return_value=self._measurement()) as evaluate:
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(evaluate.call_count, 1)
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(evaluate.call_count, 1)

    def test_partial_result_blocks_automatic_recompute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            result = {
                "schema_id": run_once.SCHEMA_ID,
                "research_id": adapter.RESEARCH_ID,
                "dataset_slice_id": run_once.DATASET_SLICE_ID,
                "payload_sha256": adapter.EXPECTED_PAYLOAD_SHA256,
                "execution_head_sha": "frozen-head",
                "classification": self._measurement()["classification"],
                "measurement": self._measurement(),
                "authority": run_once._authority(),
            }
            paths["result"].write_text(json.dumps(result, indent=2) + "\n")
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                adapter, "evaluate_frozen_contract", return_value=self._measurement()
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "existing output artifact"):
                    run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                evaluate.assert_not_called()

    def test_finalize_rejects_tampered_result_without_remeasurement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                run_once.start_attempt(expected_head_sha="frozen-head", **paths)
            frames = {"ETH": object(), "SOL": object(), "BTC": object()}
            with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", return_value=frames
            ), mock.patch.object(adapter, "evaluate_frozen_contract", return_value=self._measurement()):
                run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
            value = json.loads(paths["result"].read_text())
            value["measurement"]["diagnostics"]["router_switch_count"] = 1
            paths["result"].write_text(json.dumps(value, indent=2) + "\n")
            with mock.patch.object(run_once, "_verify_static_context", return_value=self._static_context()), mock.patch.object(
                source_engine, "frames_from_market_evidence", side_effect=AssertionError("finalize must never reload")
            ) as loader, mock.patch.object(
                adapter, "evaluate_frozen_contract", side_effect=AssertionError("finalize must never reevaluate")
            ) as evaluate:
                with self.assertRaisesRegex(run_once.ControlledRunError, "Primary result hash mismatch"):
                    run_once.finalize_marker_only(expected_head_sha="frozen-head", **paths)
                loader.assert_not_called()
                evaluate.assert_not_called()
                self.assertFalse(paths["marker"].exists())

    def test_source_or_adapter_protocol_error_becomes_invalid_execution(self) -> None:
        for exc in (
            source_engine.FrozenProtocolError("synthetic source failure"),
            adapter.InterfaceAdapterError("synthetic adapter failure"),
            scientific_engine.RouterProtocolError("synthetic delegated failure"),
        ):
            with self.subTest(type=type(exc).__name__), tempfile.TemporaryDirectory() as tmp:
                paths = self._paths(Path(tmp))
                with mock.patch.object(run_once, "_verify_controlled_context", return_value=self._context()):
                    run_once.start_attempt(expected_head_sha="frozen-head", **paths)
                frames = {"ETH": object(), "SOL": object(), "BTC": object()}
                if isinstance(exc, source_engine.FrozenProtocolError):
                    loader_side_effect = exc
                    adapter_side_effect = None
                else:
                    loader_side_effect = None
                    adapter_side_effect = exc
                with mock.patch.object(
                    run_once, "_verify_controlled_context", return_value=self._context()
                ), mock.patch.object(
                    source_engine,
                    "frames_from_market_evidence",
                    return_value=frames if loader_side_effect is None else mock.DEFAULT,
                    side_effect=loader_side_effect,
                ), mock.patch.object(
                    adapter,
                    "evaluate_frozen_contract",
                    return_value=self._measurement() if adapter_side_effect is None else mock.DEFAULT,
                    side_effect=adapter_side_effect,
                ):
                    result = run_once.evaluate_after_attempt(expected_head_sha="frozen-head", **paths)
                self.assertEqual(result["classification"], "INVALID_EXECUTION")
                self.assertEqual(result["measurement"]["actual_variants_evaluated"], 1)
                self.assertTrue(paths["execution"].exists())

    def test_schema_rejects_predictive_metric_key(self) -> None:
        schema = run_once._schema()
        measurement = self._measurement()
        measurement["diagnostics"]["calendar_year_returns_5bps"]["ROUTER"]["candidate_nll"] = 0.5
        value = {
            "schema_id": schema["schema_id"],
            "research_id": adapter.RESEARCH_ID,
            "dataset_slice_id": schema["dataset_slice_id"],
            "payload_sha256": schema["payload_sha256"],
            "execution_head_sha": "x",
            "classification": measurement["classification"],
            "measurement": measurement,
            "authority": run_once._authority(),
        }
        with self.assertRaisesRegex(run_once.ControlledRunError, "Forbidden non-preregistered metric"):
            run_once.validate_result(value, schema)

    def test_schema_rejects_classification_gate_mismatch(self) -> None:
        schema = run_once._schema()
        measurement = self._measurement()
        measurement["classification"] = "FAIL_NO_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT"
        value = {
            "schema_id": schema["schema_id"],
            "research_id": adapter.RESEARCH_ID,
            "dataset_slice_id": schema["dataset_slice_id"],
            "payload_sha256": schema["payload_sha256"],
            "execution_head_sha": "x",
            "classification": measurement["classification"],
            "measurement": measurement,
            "authority": run_once._authority(),
        }
        with self.assertRaisesRegex(run_once.ControlledRunError, "Classification does not match frozen G0-G4 precedence"):
            run_once.validate_result(value, schema)

    def test_schema_rejects_adapter_provenance_mismatch(self) -> None:
        schema = run_once._schema()
        measurement = self._measurement()
        measurement["source_interface_adapter"]["operation"] = "TZ_CONVERT"
        value = {
            "schema_id": schema["schema_id"],
            "research_id": adapter.RESEARCH_ID,
            "dataset_slice_id": schema["dataset_slice_id"],
            "payload_sha256": schema["payload_sha256"],
            "execution_head_sha": "x",
            "classification": measurement["classification"],
            "measurement": measurement,
            "authority": run_once._authority(),
        }
        with self.assertRaisesRegex(run_once.ControlledRunError, "Source interface-adapter provenance mismatch"):
            run_once.validate_result(value, schema)

    def test_runtime_artifact_names_are_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            run_once._verify_runtime_names(paths["result"], paths["execution"], paths["attempt"], paths["marker"])
            with self.assertRaisesRegex(run_once.ControlledRunError, "filenames differ"):
                run_once._verify_runtime_names(Path(tmp) / "WRONG.json", paths["execution"], paths["attempt"], paths["marker"])


if __name__ == "__main__":
    unittest.main()
