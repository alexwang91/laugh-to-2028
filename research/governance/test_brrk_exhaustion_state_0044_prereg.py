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
        cls.path = ROOT / "research/brrk_exhaustion_state_0044"
        cls.prereg = json.loads((cls.path / "PREREGISTRATION.json").read_text())
        cls.result = json.loads((cls.path / "PRIMARY_RESULT.json").read_text())
        cls.execution = json.loads((cls.path / "EXECUTION.json").read_text())
        cls.interface = json.loads((cls.path / "RUN_INTERFACE.json").read_text())
        cls.dataset_decl = json.loads((cls.path / "DATASET_DECLARATION.json").read_text())
        cls.research_registry = json.loads((ROOT / "config/research_registry.json").read_text())
        cls.dataset_registry = json.loads((ROOT / "config/dataset_exposure_registry.json").read_text())
        matches = [r for r in cls.research_registry["records"] if r.get("research_id") == RID]
        if len(matches) != 1:
            raise AssertionError("0044 registry ownership is not unique")
        cls.record = matches[0]

    def test_immutable_preregistration_remains_pre_result_contract(self) -> None:
        self.assertEqual(self.prereg["research_id"], RID)
        self.assertEqual(self.prereg["governance_mode"], "PROGRAM_GOVERNED_V1")
        self.assertEqual(self.prereg["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(self.prereg["promotion_state"], "NONE")
        self.assertEqual(self.prereg["actual_variants_evaluated"], 0)
        self.assertEqual(self.prereg["evidence_refs"], [])
        self.assertIsNone(self.prereg["failure_reason"])
        self.assertFalse(self.prereg["production_authorized"])

    def test_frozen_core4_and_secondary_core5_contract_is_unchanged(self) -> None:
        decisions = "\n".join(self.prereg["researcher_decisions"])
        self.assertIn("S1 is the equal-weight mean of causal-z f1_trend_decay7 and f1_macd_hist_decay5", decisions)
        self.assertIn("S2 is the equal-weight mean of causal-z f7_slow_fast_disagreement and f7_disagreement_persistence", decisions)
        self.assertIn("S3 is the equal-weight mean of causal-z f2_prior_peak_shortfall, f2_days_since_high60, and f2_ma20_slope10", decisions)
        self.assertIn("S4 is the equal-weight mean of causal-z f4_rv10_vs_rv30, f4_down_up_semivol, and f4_pnl_dd_duration_interaction", decisions)
        self.assertIn("CORE4 is the equal-weight mean of S1 through S4", decisions)
        self.assertIn("CORE5 is diagnostic-only and cannot control pass/fail", decisions)
        self.assertEqual(self.prereg["declared_variant_budget"], 2)

    def test_frozen_data_event_and_episode_boundaries_are_unchanged(self) -> None:
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

    def test_registry_preserves_frozen_contract_and_advances_only_lifecycle_fields(self) -> None:
        frozen_keys = (
            "research_id", "research_family_id", "research_domain", "research_governance_version",
            "governance_mode", "objective_type", "created_at", "created_before_result", "question",
            "hypothesis", "hypothesis_origin", "economic_mechanism", "primary_target", "primary_metric",
            "secondary_metrics", "feature_families", "horizon", "universe", "development_dataset_refs",
            "validation_dataset_refs", "sealed_dataset_refs", "declared_variant_budget", "parameter_candidate_count",
            "stopping_rule", "success_criteria", "failure_criteria", "allowed_followup", "forbidden_followup",
            "researcher_decisions", "lineage_edges", "production_relevance", "production_authorized",
            "provenance_status", "governed_path_prefixes"
        )
        for key in frozen_keys:
            self.assertEqual(self.record[key], self.prereg[key], key)
        self.assertEqual(self.record["governed_path_prefixes"], ["research/brrk_exhaustion_state_0044/"])
        self.assertEqual(self.record["result_status"], "PASS_TRIGGER_STAGE_ELIGIBLE")
        self.assertEqual(self.record["actual_variants_evaluated"], 2)
        self.assertIsNone(self.record["failure_reason"])
        self.assertEqual(self.record["promotion_state"], "NONE")
        self.assertIn("research/brrk_exhaustion_state_0044/PRIMARY_RESULT.json", self.record["evidence_refs"])
        self.assertIn("research/brrk_exhaustion_state_0044/RUN_ONCE.marker", self.record["evidence_refs"])
        self.assertIn("evidence_scorecard", self.record)
        self.assertEqual(
            self.record["research_process_complexity"]["actual_parameter_candidates_evaluated"],
            [
                "CORE4_EQUAL=S1_S2_S3_S4_FIXED_EQUAL_WEIGHT",
                "CORE5_VOLUME_DIAGNOSTIC=S1_S2_S3_S4_S5_FIXED_EQUAL_WEIGHT_SECONDARY_ONLY",
            ],
        )
        slices = [s for s in self.dataset_registry["dataset_slices"] if s.get("dataset_slice_id") == SLICE]
        events = [e for e in self.dataset_registry["exposure_events"] if e.get("exposure_id") == EXPOSURE]
        self.assertEqual(slices, [self.dataset_decl["dataset_slice"]])
        self.assertEqual(events, [self.dataset_decl["exposure_event"]])

    def test_closed_result_evidence_and_authority(self) -> None:
        self.assertEqual(self.result["result_status"], "PASS_TRIGGER_STAGE_ELIGIBLE")
        self.assertEqual(self.execution["execution_status"], "VALID_RESULT_RELEASED_AND_CLOSED")
        self.assertEqual(self.interface["status"], "CLOSED_RESULT_USED")
        self.assertTrue((self.path / "PRIMARY_RESULT.json").exists())
        self.assertTrue((self.path / "EXECUTION.json").exists())
        self.assertTrue((self.path / "RUN_ONCE.marker").exists())
        self.assertTrue((self.path / "RESULT.md").exists())
        self.assertTrue(self.result["authority"]["trigger_stage_eligible"])
        self.assertFalse(self.result["authority"]["trigger_defined"])
        self.assertFalse(self.result["authority"]["portfolio_economics_executed"])
        self.assertFalse(self.result["authority"]["production_authorized"])
        self.assertFalse(self.interface["same_id_rerun_allowed"])
        self.assertFalse(self.interface["same_id_retuning_allowed"])
        text = (self.path / "README.md").read_text()
        self.assertIn("no fitted coefficients", text.lower())
        self.assertIn("no portfolio", text.lower())
        self.assertIn("trigger threshold search", text.lower())


if __name__ == "__main__":
    unittest.main()
