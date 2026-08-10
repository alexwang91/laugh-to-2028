from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RID = "BRRK-EXHAUSTION-TRIGGER-0045"
SLICE = "BRRK-EXHAUSTION-0045-EXPOSED-HIST-V1"
EXPOSURE = "BRRK-EXHAUSTION-TRIGGER-0045-DEVELOPMENT-DATA-REGISTRATION-20260810T124300Z"


class BRRKExhaustionTrigger0045PreregTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = ROOT / "research/brrk_exhaustion_trigger_0045"
        cls.prereg = json.loads((cls.path / "PREREGISTRATION.json").read_text())
        cls.result = json.loads((cls.path / "PRIMARY_RESULT.json").read_text())
        cls.execution = json.loads((cls.path / "EXECUTION.json").read_text())
        cls.interface = json.loads((cls.path / "RUN_INTERFACE.json").read_text())
        cls.dataset_decl = json.loads((cls.path / "DATASET_DECLARATION.json").read_text())
        cls.research_registry = json.loads((ROOT / "config/research_registry.json").read_text())
        cls.dataset_registry = json.loads((ROOT / "config/dataset_exposure_registry.json").read_text())
        matches = [r for r in cls.research_registry["records"] if r.get("research_id") == RID]
        if len(matches) != 1:
            raise AssertionError("0045 registry ownership is not unique")
        cls.record = matches[0]

    def test_immutable_preregistration_remains_pre_result_contract(self) -> None:
        self.assertEqual(self.prereg["research_id"], RID)
        self.assertEqual(self.prereg["governance_mode"], "PROGRAM_GOVERNED_V1")
        self.assertEqual(self.prereg["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(self.prereg["declared_variant_budget"], 1)
        self.assertEqual(self.prereg["actual_variants_evaluated"], 0)
        self.assertEqual(self.prereg["evidence_refs"], [])
        self.assertIsNone(self.prereg["failure_reason"])
        self.assertFalse(self.prereg["production_authorized"])

    def test_frozen_state_thresholds_and_hysteresis(self) -> None:
        d = "\n".join(self.prereg["researcher_decisions"])
        self.assertIn("pct_CORE4 >= 0.60 OR pct_S2 >= 0.60", d)
        self.assertIn("pct_CORE4 >= 0.65 AND pct_S2 >= 0.65", d)
        self.assertIn("pct_CORE4 >= 0.75 AND pct_S2 >= 0.80", d)
        self.assertIn("at least 2 of the most recent 3", d)
        self.assertIn("pct_CORE4 <= 0.45, pct_S2 <= 0.45 and pct_S3 <= 0.50 for 5 consecutive", d)
        self.assertIn("RECOVERY has a minimum 5-session hold", d)
        self.assertIn("pct_CORE4 <= 0.55, pct_S2 <= 0.55 and pct_S3 <= 0.55 on at least 3 of the most recent 5", d)

    def test_causal_percentile_and_frozen_windows(self) -> None:
        d = "\n".join(self.prereg["researcher_decisions"])
        self.assertIn("immediately preceding 252 available daily values, excluding date t, requiring at least 60 prior observations", d)
        for window in ("PRE14_7", "PRE14_0", "PRE7_POST3", "PRE14_POST3", "PRE21_0"):
            self.assertIn(window, d)
        self.assertIn("2026-08-02", self.prereg["horizon"])

    def test_volume_negative_evidence_is_respected(self) -> None:
        d = "\n".join(self.prereg["researcher_decisions"])
        self.assertIn("S5 is therefore excluded from 0045", d)
        self.assertIn("S5 volume reintroduction", "\n".join(self.prereg["forbidden_followup"]))
        self.assertEqual(self.prereg["feature_families"], [
            "CORE4_EQUAL_FIXED_FROM_0044",
            "S2_TREND_DISAGREEMENT_FIXED_FROM_0044",
            "S3_PRICE_STRUCTURE_FIXED_FROM_0044_RECOVERY_ONLY",
        ])

    def test_hard_gate_text_is_frozen(self) -> None:
        gates = "\n".join(self.prereg["success_criteria"])
        for expected in (
            "PRE14_7 is at least 0.50",
            "PRE14_0 is at most 0.34",
            "TRUE episode WATCH-or-RISK hit rate during PRE14_7 is at least 0.60",
            "CONTINUATION episode WATCH-or-RISK false-trigger rate during PRE14_0 is at most 0.50",
            "Severe -20% TRUE_EXHAUSTION event WATCH-or-RISK hit rate during PRE14_7 is at least 0.57",
            "RISK confirmation rate during PRE7_POST3 is at least 0.57",
            "RISK false-trigger rate during PRE14_POST3 is at most 0.17",
            "median onset lead is between 7 and 21",
            "premature-clear rate before that downside barrier is at most 0.25",
        ):
            self.assertIn(expected, gates)

    def test_registry_preserves_frozen_contract_and_advances_only_lifecycle(self) -> None:
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
        self.assertEqual(self.record["governed_path_prefixes"], ["research/brrk_exhaustion_trigger_0045/"])
        self.assertEqual(self.record["result_status"], "FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY")
        self.assertEqual(self.record["actual_variants_evaluated"], 1)
        self.assertIsNotNone(self.record["failure_reason"])
        self.assertEqual(self.record["promotion_state"], "NONE")
        self.assertIn("research/brrk_exhaustion_trigger_0045/PRIMARY_RESULT.json", self.record["evidence_refs"])
        self.assertIn("research/brrk_exhaustion_trigger_0045/RUN_ONCE.marker", self.record["evidence_refs"])
        self.assertIn("evidence_scorecard", self.record)
        self.assertEqual(
            self.record["research_process_complexity"]["actual_parameter_candidates_evaluated"],
            ["TRIGGER_STATE_MACHINE_V1_FIXED_CORE4_S2_S3_HYSTERESIS"],
        )
        slices = [s for s in self.dataset_registry["dataset_slices"] if s.get("dataset_slice_id") == SLICE]
        events = [e for e in self.dataset_registry["exposure_events"] if e.get("exposure_id") == EXPOSURE]
        self.assertEqual(slices, [self.dataset_decl["dataset_slice"]])
        self.assertEqual(events, [self.dataset_decl["exposure_event"]])

    def test_closed_fail_result_and_zero_authority(self) -> None:
        self.assertEqual(self.result["result_status"], "FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY")
        self.assertEqual(self.execution["execution_status"], "VALID_RESULT_RELEASED_AND_CLOSED")
        self.assertEqual(self.interface["status"], "CLOSED_RESULT_USED")
        self.assertTrue((self.path / "PRIMARY_RESULT.json").exists())
        self.assertTrue((self.path / "EXECUTION.json").exists())
        self.assertTrue((self.path / "RUN_ONCE.marker").exists())
        self.assertTrue((self.path / "RESULT.md").exists())
        self.assertFalse(self.result["authority"]["dynamic_gross_stage_eligible"])
        self.assertFalse(self.result["authority"]["gross_mapping_defined"])
        self.assertFalse(self.result["authority"]["portfolio_economics_executed"])
        self.assertFalse(self.result["authority"]["production_authorized"])
        self.assertFalse(self.interface["same_id_rerun_allowed"])
        self.assertFalse(self.interface["same_id_retuning_allowed"])
        text = (self.path / "README.md").read_text().lower()
        self.assertIn("no portfolio weights or gross-risk values", text)
        self.assertIn("threshold or percentile grid search", text)


if __name__ == "__main__":
    unittest.main()
