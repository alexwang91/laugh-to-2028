from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research/brrk_winner_robustness_0002/PREREGISTRATION.json"
INTERFACE = ROOT / "research/brrk_winner_robustness_0002/RUN_INTERFACE.json"
RUNNER = ROOT / "research/brrk_winner_robustness_0002/run_once.py"
SOURCE_RESULT = ROOT / "research/brrk_winner_0001/PRIMARY_RESULT.json"


class BRRKWinnerRobustness0002RunInterfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prereg = json.loads(PREREG.read_text(encoding="utf-8"))
        self.interface = json.loads(INTERFACE.read_text(encoding="utf-8"))
        self.source = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
        self.runner_text = RUNNER.read_text(encoding="utf-8")

    def test_interface_is_bound_to_merged_preregistration(self) -> None:
        self.assertEqual(self.interface["research_id"], "BRRK-WINNER-ROBUSTNESS-0002")
        self.assertEqual(self.interface["run_interface_id"], "BRRK-WINNER-ROBUSTNESS-0002-RUN-ONCE-V1")
        self.assertEqual(self.interface["status"], "FROZEN_PRE_RESULT_RUN_INTERFACE")
        self.assertEqual(self.prereg["status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(self.interface["variant_count"], 1)
        self.assertFalse(self.interface["second_run_permitted"])
        self.assertTrue(self.interface["same_id_retuning_forbidden"])

    def test_candidate_is_exact_40_60_and_reuses_closed_constructor(self) -> None:
        candidate = self.interface["candidate"]
        self.assertEqual(candidate["single_alt_btc_share"], 0.40)
        self.assertEqual(candidate["single_alt_winner_share"], 0.60)
        self.assertFalse(candidate["alternative_splits_permitted"])
        self.assertIn("primary._candidate_targets", self.runner_text)
        self.assertIn("from research.brrk_winner_0001 import run_once as primary", self.runner_text)
        self.assertNotIn("BTC_SHARE = 0.45", self.runner_text)
        self.assertNotIn("BTC_SHARE = 0.35", self.runner_text)
        self.assertNotIn("BTC_SHARE = 0.30", self.runner_text)

    def test_reproduction_gate_precedes_robustness_release(self) -> None:
        gate = self.interface["reproduction_gate"]
        self.assertEqual(gate["cost_bps"], 5.0)
        self.assertEqual(gate["p3_3_l1_band"], 0.05)
        self.assertEqual(gate["absolute_tolerance"], 5e-10)
        self.assertTrue(gate["compare_full_metric_payloads"])
        self.assertTrue(gate["compare_target_frame_hashes"])
        self.assertFalse(gate["release_robustness_metrics_before_pass"])
        self.assertEqual(self.interface["failure_semantics"]["reproduction_failure"], "ABORT_WITHOUT_ROBUSTNESS_RESULT_FILE")
        self.assertIn("_reproduce_primary", self.runner_text)

    def test_temporal_panel_is_exact_and_does_not_reset_positions(self) -> None:
        panel = self.interface["temporal_panel"]
        self.assertEqual(
            panel["simulation_semantics"],
            "SIMULATE_FULL_CONTINUOUS_5BPS_PATH_ONCE_THEN_SLICE_REALIZED_SESSION_RETURNS_WITHOUT_POSITION_RESET",
        )
        self.assertFalse(panel["boundary_rebalance_or_position_reset"])
        self.assertEqual(panel["cost_bps"], 5.0)
        self.assertEqual(panel["p3_3_l1_band"], 0.05)
        self.assertEqual(
            panel["blocks"],
            [
                {"id": "T1", "start": "2022-12-10", "end": "2024-02-26", "sessions": 444},
                {"id": "T2", "start": "2024-02-27", "end": "2025-05-15", "sessions": 444},
                {"id": "T3", "start": "2025-05-16", "end": "2026-08-02", "sessions": 444},
            ],
        )

    def test_cost_stress_panel_changes_only_cost_input(self) -> None:
        panel = self.interface["cost_stress_panel"]
        self.assertEqual(panel["cost_bps"], [10.0, 20.0])
        self.assertEqual(panel["p3_3_l1_band"], 0.05)
        self.assertEqual(panel["fill_fraction"], 1.0)
        self.assertEqual(panel["transaction_cost_multiplier"], 1.0)
        self.assertIsNone(panel["funding_blocks"])
        self.assertEqual(panel["sessions"], 1332)
        self.assertIn("band=fusion.BAND", self.runner_text)

    def test_all_preregistered_hard_gates_remain_fixed(self) -> None:
        gates = self.interface["hard_gates"]
        self.assertEqual(gates["temporal_candidate_cagr_not_below_canonical_min_blocks"], 2)
        self.assertEqual(gates["temporal_max_drawdown_deterioration_pp_max_each_block"], 4.0)
        self.assertTrue(gates["cost_stress_candidate_cagr_strictly_above_canonical_all"])
        self.assertEqual(gates["cost_stress_max_drawdown_deterioration_pp_max_each"], 4.0)
        self.assertTrue(gates["cost_stress_calmar_not_below_canonical_all"])
        self.assertEqual(gates["primary_right_tail_capture_min"], 0.98)
        self.assertEqual(gates["primary_turnover_ratio_max"], 1.25)
        self.assertTrue(gates["long_only"])
        self.assertEqual(gates["target_gross_max"], 1.0)

    def test_source_primary_result_is_closed_pass(self) -> None:
        self.assertEqual(self.source["research_id"], "BRRK-WINNER-0001")
        self.assertEqual(self.source["result_status"], "PASS_ROBUSTNESS_STAGE_ELIGIBLE")
        self.assertEqual(self.source["actual_variants_evaluated"], 1)
        self.assertTrue(self.source["all_hard_gates_pass"])

    def test_zero_authority_is_immutable(self) -> None:
        self.assertFalse(self.interface["production_authorized"])
        self.assertFalse(self.interface["signature_authorized"])
        self.assertFalse(self.interface["order_submission_authorized"])
        self.assertFalse(self.prereg["production_authorized"])
        self.assertFalse(self.prereg["canonical_brrk_changed"])
        self.assertFalse(self.prereg["phase6_observation_changed"])


if __name__ == "__main__":
    unittest.main()
