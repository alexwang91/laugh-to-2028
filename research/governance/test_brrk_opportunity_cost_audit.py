from __future__ import annotations

import json
import math
import unittest

from research.governance.brrk_opportunity_cost_audit import run_audit


class BRRKOpportunityCostAuditTests(unittest.TestCase):
    def test_audit_is_deterministic_and_zero_authority(self) -> None:
        a = run_audit()
        b = run_audit()
        self.assertEqual(a, b)
        self.assertEqual(a["audit_id"], "BRRK-OPPORTUNITY-COST-AUDIT-0042")
        self.assertEqual(a["status"], "DIAGNOSTIC_ONLY_NO_PROMOTION_AUTHORITY")
        self.assertFalse(a["authority"]["canonical_strategy_changed"])
        self.assertFalse(a["authority"]["phase6_observation_changed"])
        self.assertFalse(a["authority"]["production_authorized"])
        self.assertFalse(a["authority"]["promotion_authority"])

    def test_sources_and_window_match_frozen_history(self) -> None:
        report = run_audit()
        self.assertEqual(
            report["source_paths"],
            [
                "research/results/pit_disp_0015/daily_weights.csv",
                "research/results/pit_disp_0015/daily_equity.csv",
            ],
        )
        self.assertEqual(report["window"]["start"], "2022-12-10")
        self.assertGreater(report["window"]["rows"], 1000)

    def test_no_missing_state_is_reverse_engineered(self) -> None:
        report = run_audit()
        unavailable = report["unavailable_attribution"]
        self.assertTrue(unavailable["signal_speed_causal_attribution"].startswith("UNAVAILABLE_"))
        self.assertTrue(unavailable["historical_p3_3_5pct_band_return_attribution"].startswith("UNAVAILABLE_"))
        self.assertEqual(
            unavailable["winner_cap_return_counterfactual"],
            "NOT_RUN_THIS_AUDIT_STRUCTURAL_FREQUENCY_ONLY",
        )

    def test_numeric_outputs_are_finite_when_present(self) -> None:
        report = run_audit()
        for section in ("defensive_scaling", "portfolio_structure", "target_inertia"):
            stack = [report[section]]
            while stack:
                item = stack.pop()
                if isinstance(item, dict):
                    stack.extend(item.values())
                elif isinstance(item, (int, float)) and not isinstance(item, bool):
                    self.assertTrue(math.isfinite(float(item)))

    def test_emit_machine_readable_audit_for_ci_review(self) -> None:
        report = run_audit()
        print("BRRK_ATTR_AUDIT_JSON=" + json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    unittest.main()
