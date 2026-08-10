from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RID = "BRRK-EXHAUSTION-STATE-0044"
SLICE = "BRRK-EXHAUSTION-0044-EXPOSED-HIST-V1"
EXPOSURE = "BRRK-EXHAUSTION-STATE-0044-DEVELOPMENT-DATA-REGISTRATION-20260810T115400Z"


class BRRKExhaustionState0044PreregTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prereg = json.loads((ROOT / "research/brrk_exhaustion_state_0044/PREREGISTRATION.json").read_text())
        cls.dataset_decl = json.loads((ROOT / "research/brrk_exhaustion_state_0044/DATASET_DECLARATION.json").read_text())
        cls.research_registry = json.loads((ROOT / "config/research_registry.json").read_text())
        cls.dataset_registry = json.loads((ROOT / "config/dataset_exposure_registry.json").read_text())

    def test_identity_and_pre_result_state(self) -> None:
        self.assertEqual(self.prereg["research_id"], RID)
        self.assertEqual(self.prereg["governance_mode"], "PROGRAM_GOVERNED_V1")
        self.assertEqual(self.prereg["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(self.prereg["promotion_state"], "NONE")
        self.assertEqual(self.prereg["actual_variants_evaluated"], 0)
        self.assertEqual(self.prereg["evidence_refs"], [])
        self.assertIsNone(self.prereg["failure_reason"])
        self.assertFalse(self.prereg["production_authorized"])

    def test_frozen_core4_and_secondary_core5(self) -> None:
        decisions = "\n".join(self.prereg["researcher_decisions"])
        self.assertIn("S1 is the equal-weight mean of causal-z f1_trend_decay7 and f1_macd_hist_decay5", decisions)
        self.assertIn("S2 is the equal-weight mean of causal-z f7_slow_fast_disagreement and f7_disagreement_persistence", decisions)
        self.assertIn("S3 is the equal-weight mean of causal-z f2_prior_peak_shortfall, f2_days_since_high60, and f2_ma20_slope10", decisions)
        self.assertIn("S4 is the equal-weight mean of causal-z f4_rv10_vs_rv30, f4_down_up_semivol, and f4_pnl_dd_duration_interaction", decisions)
        self.assertIn("CORE4 is the equal-weight mean of S1 through S4", decisions)
        self.assertIn("CORE5", decisions)
        self.assertIn("CORE5 is diagnostic-only and cannot control pass/fail", decisions)
        self.assertEqual(self.prereg["declared_variant_budget"], 2)

    def test_frozen_data_event_and_episode_boundaries(self) -> None:
        self.assertIn("2026-08-02", self.prereg["horizon"])
        decisions = "\n".join(self.prereg["researcher_decisions"])
        self.assertIn("+2%", decisions)
        self.assertIn("Cross-episode pairwise AUC", decisions)
        self.assertIn("Leave-one-episode-out", decisions)
        self.assertEqual(self.dataset_decl["dataset_slice"]["dataset_slice_id"], SLICE)
        self.assertEqual(self.dataset_decl["dataset_slice"]["end"], "2026-08-02T00:00:00Z")
        self.assertEqual(self.dataset_decl["dataset_slice"]["data_budget"], "DEVELOPMENT")
        self.assertEqual(self.dataset_decl["dataset_slice"]["contamination_state"], "RESEARCHER_EXPOSED_HISTORY")
        self.assertEqual(self.dataset_decl["exposure_event"]["exposure_id"], EXPOSURE)
        self.assertTrue(self.dataset_decl["exposure_event"]["result_informed_followup"])

    def test_formal_registry_owns_exact_path(self) -> None:
        matches = [r for r in self.research_registry["records"] if r.get("research_id") == RID]
        self.assertEqual(matches, [self.prereg])
        self.assertEqual(matches[0]["governed_path_prefixes"], ["research/brrk_exhaustion_state_0044/"])
        slices = [s for s in self.dataset_registry["dataset_slices"] if s.get("dataset_slice_id") == SLICE]
        events = [e for e in self.dataset_registry["exposure_events"] if e.get("exposure_id") == EXPOSURE]
        self.assertEqual(slices, [self.dataset_decl["dataset_slice"]])
        self.assertEqual(events, [self.dataset_decl["exposure_event"]])

    def test_prereg_contract_remains_frozen_before_result(self) -> None:
        path = ROOT / "research/brrk_exhaustion_state_0044"
        self.assertTrue((path / "PREREGISTRATION.json").exists())
        self.assertTrue((path / "DATASET_DECLARATION.json").exists())
        self.assertTrue((path / "README.md").exists())
        self.assertFalse((path / "PRIMARY_RESULT.json").exists())
        self.assertFalse((path / "RUN_ONCE.marker").exists())
        text = (path / "README.md").read_text()
        self.assertIn("no fitted coefficients", text.lower())
        self.assertIn("no portfolio", text.lower())
        self.assertIn("trigger threshold search", text.lower())


if __name__ == "__main__":
    unittest.main()
