from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from research.brrk_exhaustion_state_0044 import run_once as runner

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "research/brrk_exhaustion_state_0044"


class BRRKExhaustionState0044RunOnceContractTests(unittest.TestCase):
    def test_frozen_identity_taxonomy_and_axes(self) -> None:
        self.assertEqual(runner.RESEARCH_ID, "BRRK-EXHAUSTION-STATE-0044")
        self.assertEqual(str(runner.FROZEN_EVAL_END.date()), "2026-08-02")
        self.assertEqual(runner.DOWNSIDE_PANELS, (0.10, 0.15, 0.20))
        self.assertEqual(runner.PRIMARY_DOWNSIDE, 0.15)
        self.assertEqual(runner.SEVERE_DOWNSIDE, 0.20)
        self.assertEqual(
            runner.PRIMARY_AXES,
            (
                "S1_MOMENTUM_DECELERATION",
                "S2_TREND_DISAGREEMENT",
                "S3_PRICE_STRUCTURE",
                "S4_VOL_DOWNSIDE",
            ),
        )
        self.assertEqual(runner.AXIS_FEATURES["S1_MOMENTUM_DECELERATION"], ("f1_trend_decay7", "f1_macd_hist_decay5"))
        self.assertEqual(runner.AXIS_FEATURES["S2_TREND_DISAGREEMENT"], ("f7_slow_fast_disagreement", "f7_disagreement_persistence"))
        self.assertEqual(runner.AXIS_FEATURES["S3_PRICE_STRUCTURE"], ("f2_prior_peak_shortfall", "f2_days_since_high60", "f2_ma20_slope10"))
        self.assertEqual(runner.AXIS_FEATURES["S4_VOL_DOWNSIDE"], ("f4_rv10_vs_rv30", "f4_down_up_semivol", "f4_pnl_dd_duration_interaction"))
        self.assertEqual(runner.AXIS_FEATURES["S5_VOLUME_CONFIRMATION"], ("f3_down_up_volume_ratio", "f3_price_obv_divergence20"))

    def test_frozen_source_reproduction_guard(self) -> None:
        self.assertEqual(runner.EXPECTED_0043_CANDIDATE_COUNT, 16)
        self.assertEqual(
            runner.EXPECTED_0043_PANEL_COUNTS,
            {
                0.10: {"TRUE_EXHAUSTION": 12, "CONTINUATION_FALSE_TOP": 4, "AMBIGUOUS": 0},
                0.15: {"TRUE_EXHAUSTION": 9, "CONTINUATION_FALSE_TOP": 6, "AMBIGUOUS": 1},
                0.20: {"TRUE_EXHAUSTION": 7, "CONTINUATION_FALSE_TOP": 6, "AMBIGUOUS": 3},
            },
        )

    def test_equal_weight_construction_and_no_fit(self) -> None:
        source = inspect.getsource(runner.build_state_axes)
        self.assertIn('state["CORE4"] = state[list(PRIMARY_AXES)].mean', source)
        self.assertIn('state["CORE5"] = state[list(SECONDARY_AXES)].mean', source)
        full = inspect.getsource(runner)
        for forbidden in ("LogisticRegression", "RandomForest", "XGB", "fit(", "GridSearch", "argmax"):
            self.assertNotIn(forbidden, full)

    def test_macro_episode_rule_is_plus_two_percent_anchor_recovery(self) -> None:
        source = inspect.getsource(runner.assign_macro_episodes)
        self.assertIn("anchor_nav * 1.02", source)
        self.assertIn("peak > recovery", source)

    def test_cross_episode_excludes_same_episode_and_equal_weights_episode_pairs(self) -> None:
        source = inspect.getsource(runner.cross_episode_auc)
        self.assertIn("if true_ep == cont_ep", source)
        self.assertIn('np.mean([r["concordance"] for r in pair_rows])', source)

    def test_hard_gates_match_preregistration(self) -> None:
        source = inspect.getsource(runner.run)
        self.assertIn("len(usable_eps) >= 4", source)
        self.assertIn("len(true_eps) >= 2", source)
        self.assertIn("len(cont_eps) >= 2", source)
        self.assertIn("_gate(primary_cross[\"auc\"], 0.70)", source)
        self.assertIn("_gate(primary_event[\"auc\"], 0.68)", source)
        self.assertIn("_gate(severe_cross[\"auc\"], 0.75)", source)
        self.assertIn("_gate(loeo[\"min_auc\"], 0.55)", source)
        self.assertIn("_gate(loeo[\"median_auc\"], 0.68)", source)

    def test_no_trigger_portfolio_or_authority_translation(self) -> None:
        full = inspect.getsource(runner)
        for forbidden in ("create_order", "submit_order", "target_weights =", "gross_map", "portfolio_return", "position_size"):
            self.assertNotIn(forbidden, full)
        interface = json.loads((PATH / "RUN_INTERFACE.json").read_text())
        result = json.loads((PATH / "PRIMARY_RESULT.json").read_text())
        self.assertEqual(interface["status"], "CLOSED_RESULT_USED")
        self.assertEqual(interface["frozen_parent_merge_commit"], "223d00202242d2d7e8eeffc489367e8078408604")
        self.assertEqual(interface["valid_result_run"]["workflow_run_id"], 31388103016)
        self.assertEqual(interface["valid_result_run"]["artifact_id"], 9062525981)
        self.assertEqual(interface["valid_result_run"]["result_status"], "PASS_TRIGGER_STAGE_ELIGIBLE")
        self.assertFalse(interface["same_id_rerun_allowed"])
        self.assertFalse(interface["same_id_retuning_allowed"])
        self.assertTrue(interface["authority"]["trigger_stage_eligible"])
        self.assertFalse(interface["authority"]["trigger_defined"])
        self.assertFalse(interface["authority"]["portfolio_economics_executed"])
        self.assertFalse(interface["authority"]["production_authorized"])
        self.assertFalse(interface["authority"]["signature_authorized"])
        self.assertFalse(interface["authority"]["order_submission_authorized"])
        self.assertEqual(result["result_status"], "PASS_TRIGGER_STAGE_ELIGIBLE")
        self.assertFalse(result["authority"]["trigger_defined"])
        self.assertFalse(result["authority"]["portfolio_economics_executed"])

    def test_permanent_result_and_marker_bind_unique_valid_run(self) -> None:
        self.assertTrue((PATH / "PRIMARY_RESULT.json").exists())
        self.assertTrue((PATH / "EXECUTION.json").exists())
        self.assertTrue((PATH / "RUN_ONCE.marker").exists())
        self.assertTrue((PATH / "RESULT.md").exists())
        marker = (PATH / "RUN_ONCE.marker").read_text()
        self.assertIn("STATUS=USED_CLOSED", marker)
        self.assertIn("VALID_RESULT_WORKFLOW_RUN_ID=31388103016", marker)
        self.assertIn("RESULT_STATUS=PASS_TRIGGER_STAGE_ELIGIBLE", marker)
        self.assertIn("SAME_ID_RERUN_ALLOWED=false", marker)
        self.assertIn("PRE_RESULT_WORKFLOW_RUN_31387906469=FAILED_BEFORE_DIAGNOSTIC_NO_RESULT", marker)


if __name__ == "__main__":
    unittest.main()
