from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from research.brrk_exhaustion_trigger_0045 import run_once as runner

ROOT = Path(__file__).resolve().parents[2]


class BRRKExhaustionTrigger0045RunOnceContractTests(unittest.TestCase):
    def test_frozen_thresholds_and_persistence(self) -> None:
        self.assertEqual(runner.LOOKBACK, 252); self.assertEqual(runner.MIN_HISTORY, 60)
        self.assertEqual((runner.DECEL_CORE, runner.DECEL_S2), (0.60, 0.60))
        self.assertEqual((runner.WATCH_CORE, runner.WATCH_S2), (0.65, 0.65))
        self.assertEqual((runner.RISK_CORE, runner.RISK_S2), (0.75, 0.80))
        self.assertEqual((runner.RECOVERY_CORE, runner.RECOVERY_S2, runner.RECOVERY_S3), (0.45, 0.45, 0.50))
        self.assertEqual((runner.HEALTHY_CORE, runner.HEALTHY_S2, runner.HEALTHY_S3), (0.55, 0.55, 0.55))
        self.assertEqual((runner.ENTRY_LOOKBACK, runner.ENTRY_REQUIRED), (3, 2))
        self.assertEqual(runner.RECOVERY_ENTRY_CONSECUTIVE, 5); self.assertEqual(runner.RECOVERY_MIN_HOLD, 5)
        self.assertEqual((runner.HEALTHY_REPAIR_LOOKBACK, runner.HEALTHY_REPAIR_REQUIRED), (5, 3))

    def test_causal_percentile_excludes_current(self) -> None:
        src = inspect.getsource(runner.causal_percentile)
        self.assertIn('values.iloc[max(0, i - LOOKBACK):i]', src)
        self.assertIn('len(prior) < MIN_HISTORY', src)
        self.assertIn('(prior <= cur).mean()', src)

    def test_state_machine_hierarchy_and_hysteresis(self) -> None:
        src = inspect.getsource(runner.run_state_machine)
        self.assertIn('"RISK" if rqual else "WATCH" if wqual else "DECELERATION"', src)
        self.assertIn('_all_true_consecutive(p["recovery_entry_raw"], pos, RECOVERY_ENTRY_CONSECUTIVE)', src)
        self.assertIn('recovery_age >= RECOVERY_MIN_HOLD and repair_qual', src)
        self.assertIn('elif wqual:', src)

    def test_windows_and_hard_gates(self) -> None:
        self.assertEqual(runner.WINDOWS, {"PRE14_7": (-14, -7), "PRE14_0": (-14, 0), "PRE7_POST3": (-7, 3), "PRE14_POST3": (-14, 3), "PRE21_0": (-21, 0)})
        src = inspect.getsource(runner.run)
        for literal in ('0.50', '0.34', '0.60', '0.50', '0.57', '0.57', '0.17', 'lead["count"] >= 4', '7 <= float(lead["median"]) <= 21', '0.25'):
            self.assertIn(literal, src)

    def test_parent_binding_and_no_gross_translation(self) -> None:
        self.assertEqual(runner.EXPECTED_0044_RESULT_STATUS, "PASS_TRIGGER_STAGE_ELIGIBLE")
        self.assertEqual(runner.EXPECTED_0044_ARTIFACT_DIGEST, "sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378")
        full = inspect.getsource(runner)
        for forbidden in ("create_order", "submit_order", "target_weights =", "gross_map", "portfolio_return", "position_size"):
            self.assertNotIn(forbidden, full)
        interface = json.loads((ROOT / "research/brrk_exhaustion_trigger_0045/RUN_INTERFACE.json").read_text())
        self.assertEqual(interface["status"], "READY_NOT_RUN")
        self.assertEqual(interface["candidate_count"], 1)
        self.assertFalse(interface["authority"]["gross_mapping_defined"])
        self.assertFalse(interface["authority"]["portfolio_economics_executed"])

    def test_no_result_exists_before_execution(self) -> None:
        path = ROOT / "research/brrk_exhaustion_trigger_0045"
        self.assertFalse((path / "PRIMARY_RESULT.json").exists())
        self.assertFalse((path / "RUN_ONCE.marker").exists())


if __name__ == "__main__": unittest.main()
