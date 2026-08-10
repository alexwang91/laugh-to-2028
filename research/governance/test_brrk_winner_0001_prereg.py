from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config/research_registry.json"
DATASETS = ROOT / "config/dataset_exposure_registry.json"
DRAFT = ROOT / "research/governance/BRRK_WINNER_0001_PREREG_DRAFT.json"
FORMAL = ROOT / "research/brrk_winner_0001/PREREGISTRATION.json"
RESULT = ROOT / "research/brrk_winner_0001/PRIMARY_RESULT.json"
EXECUTION = ROOT / "research/brrk_winner_0001/EXECUTION.json"
RUN_INTERFACE = ROOT / "research/brrk_winner_0001/RUN_INTERFACE.json"


class BRRKWinner0001ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.datasets = json.loads(DATASETS.read_text(encoding="utf-8"))
        self.draft = json.loads(DRAFT.read_text(encoding="utf-8"))

    def _record(self) -> dict:
        matches = [r for r in self.registry["records"] if r.get("research_id") == "BRRK-WINNER-0001"]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_original_preregistration_remains_frozen(self) -> None:
        formal = json.loads(FORMAL.read_text(encoding="utf-8"))
        self.assertEqual(formal["research_id"], "BRRK-WINNER-0001")
        self.assertEqual(formal["status"], "PREREGISTERED_NOT_RUN")
        self.assertEqual(formal["candidate"]["single_alt_btc_share"], 0.40)
        self.assertEqual(formal["candidate"]["single_alt_winner_share"], 0.60)
        self.assertEqual(formal["actual_variants_evaluated"], 0)
        self.assertFalse(formal["economics_executed"])
        self.assertFalse(formal["production_authorized"])
        self.assertEqual(self.draft["declared_variant_budget"], 1)
        self.assertEqual(self.draft["actual_variants_evaluated"], 0)

    def test_registry_closes_exactly_one_variant(self) -> None:
        record = self._record()
        self.assertEqual(record["governance_mode"], "PROGRAM_GOVERNED_V1")
        self.assertTrue(record["created_before_result"])
        self.assertEqual(record["declared_variant_budget"], 1)
        self.assertEqual(record["actual_variants_evaluated"], 1)
        self.assertEqual(record["result_status"], "PASS_ROBUSTNESS_STAGE_ELIGIBLE")
        self.assertEqual(record["promotion_state"], "ROBUSTNESS_STAGE_ELIGIBLE_ONLY")
        self.assertFalse(record["production_authorized"])
        self.assertEqual(record["research_process_complexity"]["actual_parameter_candidates_evaluated"], ["SINGLE_ALT_BTC_SHARE=0.40;SINGLE_ALT_WINNER_SHARE=0.60"])

    def test_candidate_and_hard_gates_remain_frozen(self) -> None:
        record = self._record()
        decisions = "\n".join(record["researcher_decisions"])
        forbidden = "\n".join(record["forbidden_followup"])
        criteria = "\n".join(record["success_criteria"])
        self.assertIn("0.50/0.50 -> 0.40/0.60", decisions)
        self.assertIn("45/55", forbidden)
        self.assertIn("35/65", forbidden)
        self.assertIn("30/70", forbidden)
        self.assertIn("+3.00 percentage points", criteria)
        self.assertIn("4.00 percentage points worse", criteria)
        self.assertIn("98%", criteria)
        self.assertIn("1.25 times", criteria)

    def test_development_dataset_is_consumed_and_exposed(self) -> None:
        item = next(s for s in self.datasets["dataset_slices"] if s.get("dataset_slice_id") == "BRRK-WINNER-0001-CANONICAL-HIST-V1")
        self.assertEqual(item["data_budget"], "DEVELOPMENT")
        self.assertEqual(item["contamination_state"], "RESEARCHER_EXPOSED_HISTORY")
        self.assertTrue(item["researcher_exposed_history"])
        self.assertTrue(item["consumed"])
        events = [e for e in self.datasets["exposure_events"] if e.get("research_id") == "BRRK-WINNER-0001"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["exposure_id"], "BRRK-WINNER-0001-DEVELOPMENT-RUN-20260810T071111Z")

    def test_one_shot_result_matches_frozen_contract(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
        interface = json.loads(RUN_INTERFACE.read_text(encoding="utf-8"))
        self.assertTrue(result["baseline_reproduced"])
        self.assertEqual(result["actual_variants_evaluated"], 1)
        self.assertTrue(result["all_hard_gates_pass"])
        self.assertEqual(result["result_status"], "PASS_ROBUSTNESS_STAGE_ELIGIBLE")
        self.assertEqual(result["candidate_definition"]["single_alt_btc_share"], 0.40)
        self.assertEqual(result["candidate_definition"]["single_alt_winner_share"], 0.60)
        self.assertTrue(all(g["pass"] for g in result["hard_gates"].values()))
        self.assertEqual(execution["candidate_execution_count"], 1)
        self.assertFalse(execution["second_candidate_run_permitted"])
        self.assertEqual(interface["candidate"]["variant_count"], 1)
        self.assertTrue(interface["same_id_retuning_forbidden"])

    def test_no_authority_change(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
        for obj in (result, execution):
            self.assertFalse(obj["production_authorized"])
            self.assertFalse(obj["signature_authorized"])
            self.assertFalse(obj["order_submission_authorized"])


if __name__ == "__main__":
    unittest.main()
