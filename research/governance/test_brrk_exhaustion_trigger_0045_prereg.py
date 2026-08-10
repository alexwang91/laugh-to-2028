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
        cls.dataset_decl = json.loads((cls.path / "DATASET_DECLARATION.json").read_text())
        cls.research_registry = json.loads((ROOT / "config/research_registry.json").read_text())
        cls.dataset_registry = json.loads((ROOT / "config/dataset_exposure_registry.json").read_text())

    def test_identity_and_pre_result_state(self) -> None:
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
        self.assertIn("PRE14_7", d)
        self.assertIn("PRE14_0", d)
        self.assertIn("PRE7_POST3", d)
        self.assertIn("PRE14_POST3", d)
        self.assertIn("PRE21_0", d)
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

    def test_formal_registry_and_dataset_ownership(self) -> None:
        records = [r for r in self.research_registry["records"] if r.get("research_id") == RID]
        self.assertEqual(records, [self.prereg])
        self.assertEqual(records[0]["governed_path_prefixes"], ["research/brrk_exhaustion_trigger_0045/"])
        slices = [s for s in self.dataset_registry["dataset_slices"] if s.get("dataset_slice_id") == SLICE]
        events = [e for e in self.dataset_registry["exposure_events"] if e.get("exposure_id") == EXPOSURE]
        self.assertEqual(slices, [self.dataset_decl["dataset_slice"]])
        self.assertEqual(events, [self.dataset_decl["exposure_event"]])

    def test_no_result_or_gross_translation_before_execution(self) -> None:
        names = {p.name for p in self.path.iterdir() if p.is_file()}
        self.assertEqual(names, {"PREREGISTRATION.json", "DATASET_DECLARATION.json", "README.md"})
        text = (self.path / "README.md").read_text().lower()
        self.assertIn("no portfolio weights or gross-risk values", text)
        self.assertIn("threshold or percentile grid search", text)


if __name__ == "__main__":
    unittest.main()
