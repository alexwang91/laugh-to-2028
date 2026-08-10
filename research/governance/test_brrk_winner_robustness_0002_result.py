from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/brrk_winner_robustness_0002/PRIMARY_RESULT.json"
EXECUTION = ROOT / "research/brrk_winner_robustness_0002/EXECUTION.json"
INTERFACE = ROOT / "research/brrk_winner_robustness_0002/RUN_INTERFACE.json"
MARKER = ROOT / "research/brrk_winner_robustness_0002/RUN_ONCE.marker"


class BRRKWinnerRobustness0002ResultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
        self.interface = json.loads(INTERFACE.read_text(encoding="utf-8"))

    def test_exact_artifact_bytes_are_bound(self) -> None:
        committed = hashlib.sha256(RESULT.read_bytes()).hexdigest()
        self.assertEqual(committed, "cf149308df5aea1a0cc1315432a7effd0e163cda21e6df0b8f39cf0b6ce6fdf0")
        self.assertEqual(committed, self.execution["primary_result_committed_sha256"])
        self.assertEqual(committed, self.execution["primary_result_runner_serialization_sha256"])
        self.assertEqual(
            self.execution["artifact_digest"],
            "sha256:8eb08d0080fae185953ae50a15b05bc9994d6c06da33761bd2125dc89037313c",
        )

    def test_exactly_one_execution_is_closed(self) -> None:
        self.assertTrue(MARKER.exists())
        marker = json.loads(MARKER.read_text(encoding="utf-8"))
        self.assertEqual(self.execution["candidate_execution_count"], 1)
        self.assertEqual(self.execution["actual_variants_evaluated"], 1)
        self.assertEqual(self.result["actual_variants_evaluated"], 1)
        self.assertFalse(self.execution["second_candidate_run_permitted"])
        self.assertFalse(marker["second_marker_permitted"])
        self.assertTrue(marker["same_id_retuning_forbidden"])
        self.assertFalse(self.result["retuning_performed"])
        self.assertFalse(self.execution["retuning_performed"])

    def test_reproduction_passed_before_robustness_release(self) -> None:
        self.assertTrue(self.result["baseline_reproduced_before_robustness_release"])
        self.assertTrue(self.result["robustness_metrics_released_after_reproduction"])
        self.assertTrue(self.result["reproduction"]["passed"])
        self.assertEqual(self.result["reproduction"]["absolute_tolerance"], 5e-10)
        self.assertEqual(
            self.result["reproduction"]["canonical_target_frame_sha256"],
            "bbb538ccfc0001e9458c5f7a4bed60eeed13a7c6d92a7f775a29af2affada5b8",
        )
        self.assertEqual(
            self.result["reproduction"]["candidate_target_frame_sha256"],
            "6e0ae02475677d6b0453100c99a38b1f3e7129686f34d12e8b030ec0809311b5",
        )

    def test_temporal_panel_retains_positive_and_negative_evidence(self) -> None:
        blocks = {row["block_id"]: row for row in self.result["temporal_panel"]["blocks"]}
        self.assertEqual(set(blocks), {"T1", "T2", "T3"})
        self.assertTrue(blocks["T1"]["gates"]["candidate_cagr_not_below_canonical"]["pass"])
        self.assertFalse(blocks["T2"]["gates"]["candidate_cagr_not_below_canonical"]["pass"])
        self.assertTrue(blocks["T3"]["gates"]["candidate_cagr_not_below_canonical"]["pass"])
        self.assertLess(blocks["T2"]["delta"]["cagr"], 0.0)
        aggregate = self.result["temporal_panel"]["aggregate_gates"]
        self.assertEqual(aggregate["candidate_cagr_not_below_canonical_block_count"]["value"], 2)
        self.assertTrue(aggregate["candidate_cagr_not_below_canonical_block_count"]["pass"])
        self.assertTrue(aggregate["max_drawdown_deterioration_safe_in_every_block"]["pass"])

    def test_both_cost_stresses_pass_without_band_change(self) -> None:
        rows = {float(row["cost_bps"]): row for row in self.result["cost_stress_panel"]["rows"]}
        self.assertEqual(set(rows), {10.0, 20.0})
        self.assertEqual(self.result["evaluation"]["p3_3_l1_band"], 0.05)
        for cost in (10.0, 20.0):
            row = rows[cost]
            self.assertGreater(row["candidate"]["cagr"], row["baseline"]["cagr"])
            self.assertGreaterEqual(row["candidate"]["calmar"], row["baseline"]["calmar"])
            self.assertTrue(row["gates"]["candidate_cagr_strictly_above_canonical"]["pass"])
            self.assertTrue(row["gates"]["calmar_not_below_canonical"]["pass"])
            self.assertTrue(row["gates"]["max_drawdown_deterioration_pp_max_4"]["pass"])

    def test_inherited_tail_turnover_and_safety_gates_pass(self) -> None:
        inherited = self.result["inherited_gates"]
        self.assertGreaterEqual(self.result["right_tail"]["capture_ratio"], 0.98)
        self.assertLessEqual(inherited["turnover_ratio_max_1_25"]["value"], 1.25)
        self.assertTrue(inherited["canonical_best20_log_growth_capture_min_0_98"]["pass"])
        self.assertTrue(inherited["turnover_ratio_max_1_25"]["pass"])
        self.assertTrue(inherited["long_only"]["pass"])
        self.assertTrue(inherited["gross_max_1"]["pass"])

    def test_result_is_future_validation_eligibility_only(self) -> None:
        self.assertTrue(self.result["all_hard_gates_pass"])
        self.assertEqual(self.result["result_status"], "PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE")
        self.assertEqual(self.result["promotion_authority"], "FUTURE_ONLY_VALIDATION_STAGE_ELIGIBILITY_ONLY")
        self.assertEqual(self.execution["result_status"], "PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE")
        self.assertFalse(self.result["canonical_brrk_changed"])
        self.assertFalse(self.result["phase6_observation_changed"])
        for obj in (self.result, self.execution):
            self.assertFalse(obj["production_authorized"])
            self.assertFalse(obj["signature_authorized"])
            self.assertFalse(obj["order_submission_authorized"])


if __name__ == "__main__":
    unittest.main()
