from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from research.brrk_exhaustion_state_0044 import run_once as runner

ROOT = Path(__file__).resolve().parents[2]


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
        self.assertEqual(
            runner.AXIS_FEATURES["S1_MOMENTUM_DECELERATION"],
            ("f1_trend_decay7", "f1_macd_hist_decay5"),
        )
        self.assertEqual(
            runner.AXIS_FEATURES["S2_TREND_DISAGREEMENT"],
            ("f7_slow_fast_disagreement", "f7_disagreement_persistence"),
        )
        self.assertEqual(
            runner.AXIS_FEATURES["S3_PRICE_STRUCTURE"],
            ("f2_prior_peak_shortfall", "f2_days_since_high60", "f2_ma20_slope10"),
        )
        self.assertEqual(
            runner.AXIS_FEATURES["S4_VOL_DOWNSIDE"],
            ("f4_rv10_vs_rv30", "f4_down_up_semivol", "f4_pnl_dd_duration_interaction"),
        )
        self.assertEqual(
            runner.AXIS_FEATURES["S5_VOLUME_CONFIRMATION"],
            ("f3_down_up_volume_ratio", "f3_price_obv_divergence20"),
        )

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
        interface = json.loads((ROOT / "research/brrk_exhaustion_state_0044/RUN_INTERFACE.json").read_text())
        self.assertEqual(interface["status"], "READY_NOT_RUN")
        self.assertFalse(interface["authority"]["trigger_defined"])
        self.assertFalse(interface["authority"]["portfolio_economics_executed"])
        self.assertFalse(interface["authority"]["production_authorized"])
        self.assertFalse(interface["authority"]["signature_authorized"])
        self.assertFalse(interface["authority"]["order_submission_authorized"])

    def test_no_result_or_marker_exists_before_execution(self) -> None:
        path = ROOT / "research/brrk_exhaustion_state_0044"
        self.assertFalse((path / "PRIMARY_RESULT.json").exists())
        self.assertFalse((path / "RUN_ONCE.marker").exists())


if __name__ == "__main__":
    unittest.main()
