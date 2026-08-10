from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config/research_registry.json"
DATASETS = ROOT / "config/dataset_exposure_registry.json"
DRAFT = ROOT / "research/governance/BRRK_WINNER_0001_PREREG_DRAFT.json"
FORMAL = ROOT / "research/brrk_winner_0001/PREREGISTRATION.json"


class BRRKWinner0001PreregistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.datasets = json.loads(DATASETS.read_text(encoding="utf-8"))
        self.draft = json.loads(DRAFT.read_text(encoding="utf-8"))

    def _record(self) -> dict:
        matches = [r for r in self.registry["records"] if r.get("research_id") == "BRRK-WINNER-0001"]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_registry_record_is_frozen_before_results(self) -> None:
        record = self._record()
        self.assertEqual(record, self.draft)
        self.assertEqual(record["governance_mode"], "PROGRAM_GOVERNED_V1")
        self.assertTrue(record["created_before_result"])
        self.assertEqual(record["result_status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(record["declared_variant_budget"], 1)
        self.assertEqual(record["actual_variants_evaluated"], 0)
        self.assertEqual(record["parameter_candidate_count"], 1)
        self.assertFalse(record["production_authorized"])
        self.assertEqual(record["governed_path_prefixes"], ["research/brrk_winner_0001/"])

    def test_candidate_is_exactly_one_40_60_single_alt_change(self) -> None:
        record = self._record()
        decisions = "\n".join(record["researcher_decisions"])
        forbidden = "\n".join(record["forbidden_followup"])
        self.assertIn("0.50/0.50 -> 0.40/0.60", decisions)
        self.assertIn("20/60/120/240", forbidden)
        self.assertIn("45/55", forbidden)
        self.assertIn("35/65", forbidden)
        self.assertIn("30/70", forbidden)
        self.assertEqual(record["universe"], ["BTC", "ETH", "SOL", "BNB"])

    def test_hard_gates_are_frozen(self) -> None:
        criteria = "\n".join(self._record()["success_criteria"])
        self.assertIn("+3.00 percentage points", criteria)
        self.assertIn("4.00 percentage points worse", criteria)
        self.assertIn("Calmar ratio", criteria)
        self.assertIn("98%", criteria)
        self.assertIn("1.25 times", criteria)
        self.assertIn("gross never exceeds 1.0", criteria)

    def test_dataset_is_researcher_exposed_development_only(self) -> None:
        matches = [
            s for s in self.datasets["dataset_slices"]
            if s.get("dataset_slice_id") == "BRRK-WINNER-0001-CANONICAL-HIST-V1"
        ]
        self.assertEqual(len(matches), 1)
        item = matches[0]
        self.assertEqual(item["data_budget"], "DEVELOPMENT")
        self.assertEqual(item["contamination_state"], "RESEARCHER_EXPOSED_HISTORY")
        self.assertTrue(item["researcher_exposed_history"])
        self.assertFalse(item["consumed"])

    def test_formal_preregistration_matches_registry_when_present(self) -> None:
        if not FORMAL.exists():
            self.skipTest("formal governed path is introduced after registry registration commit")
        formal = json.loads(FORMAL.read_text(encoding="utf-8"))
        self.assertEqual(formal["research_id"], "BRRK-WINNER-0001")
        self.assertEqual(formal["status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(formal["candidate"]["single_alt_btc_share"], 0.40)
        self.assertEqual(formal["candidate"]["single_alt_winner_share"], 0.60)
        self.assertEqual(formal["actual_variants_evaluated"], 0)
        self.assertFalse(formal["production_authorized"])
        self.assertFalse(formal["economics_executed"])


if __name__ == "__main__":
    unittest.main()
