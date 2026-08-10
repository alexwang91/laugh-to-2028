from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config/research_registry.json"
DATASETS = ROOT / "config/dataset_exposure_registry.json"
DRAFT = ROOT / "research/governance/BRRK_WINNER_ROBUSTNESS_0002_PREREG_DRAFT.json"
FORMAL = ROOT / "research/brrk_winner_robustness_0002/PREREGISTRATION.json"
README = ROOT / "research/brrk_winner_robustness_0002/README.md"


class BRRKWinnerRobustness0002PreregistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.datasets = json.loads(DATASETS.read_text(encoding="utf-8"))
        self.draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        self.formal = json.loads(FORMAL.read_text(encoding="utf-8"))

    def _record(self) -> dict:
        matches = [
            r for r in self.registry["records"]
            if r.get("research_id") == "BRRK-WINNER-ROBUSTNESS-0002"
        ]
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
        self.assertEqual(record["promotion_state"], "NONE")
        self.assertFalse(record["production_authorized"])
        self.assertEqual(
            record["governed_path_prefixes"],
            ["research/brrk_winner_robustness_0002/"],
        )

    def test_exact_40_60_construction_is_fixed_without_split_search(self) -> None:
        formal = self.formal
        self.assertEqual(formal["candidate"]["single_alt_btc_share"], 0.40)
        self.assertEqual(formal["candidate"]["single_alt_winner_share"], 0.60)
        self.assertTrue(formal["candidate"]["allocation_is_frozen_from_brrk_winner_0001"])
        self.assertFalse(formal["candidate"]["alternative_splits_permitted"])
        self.assertFalse(formal["candidate"]["signals_changed"])
        self.assertFalse(formal["candidate"]["eligibility_changed"])
        self.assertFalse(formal["candidate"]["multi_alt_allocation_changed"])
        self.assertFalse(formal["candidate"]["defensive_scale_changed"])
        forbidden = "\n".join(self._record()["forbidden_followup"])
        for split in ("45/55", "35/65", "30/70"):
            self.assertIn(split, forbidden)

    def test_reproduction_gate_is_frozen(self) -> None:
        reproduction = self.formal["reproduction"]
        self.assertEqual(reproduction["source_result"], "research/brrk_winner_0001/PRIMARY_RESULT.json")
        self.assertEqual(reproduction["cost_bps"], 5.0)
        self.assertEqual(reproduction["absolute_tolerance"], 5e-10)
        self.assertTrue(reproduction["required_before_robustness_release"])

    def test_temporal_panel_is_exact_three_equal_contiguous_blocks(self) -> None:
        panel = self.formal["temporal_panel"]
        self.assertEqual(panel["cost_bps"], 5.0)
        self.assertEqual(panel["partition_rule"], "THREE_EQUAL_CONTIGUOUS_BLOCKS_BY_SESSION_ORDER")
        self.assertEqual(panel["session_count_total"], 1332)
        self.assertEqual(
            panel["blocks"],
            [
                {"id": "T1", "start": "2022-12-10", "end": "2024-02-26", "sessions": 444},
                {"id": "T2", "start": "2024-02-27", "end": "2025-05-15", "sessions": 444},
                {"id": "T3", "start": "2025-05-16", "end": "2026-08-02", "sessions": 444},
            ],
        )

    def test_cost_stress_panel_is_exactly_10_and_20_bps(self) -> None:
        panel = self.formal["cost_stress_panel"]
        self.assertEqual(panel["full_horizon_start"], "2022-12-10")
        self.assertEqual(panel["full_horizon_end"], "2026-08-02")
        self.assertEqual(panel["cost_bps"], [10.0, 20.0])
        self.assertEqual(panel["p3_3_l1_band"], 0.05)

    def test_hard_gates_are_frozen(self) -> None:
        gates = self.formal["hard_success_gates"]
        self.assertEqual(gates["temporal_blocks_candidate_cagr_not_below_canonical_min_count"], 2)
        self.assertEqual(gates["temporal_block_max_drawdown_deterioration_pp_max"], 4.0)
        self.assertTrue(gates["cost_stress_candidate_cagr_strictly_above_canonical_all"])
        self.assertEqual(gates["cost_stress_max_drawdown_deterioration_pp_max"], 4.0)
        self.assertTrue(gates["cost_stress_calmar_not_below_canonical_all"])
        self.assertEqual(gates["primary_canonical_top20_log_growth_capture_min"], 0.98)
        self.assertEqual(gates["total_turnover_ratio_max"], 1.25)
        self.assertTrue(gates["long_only"])
        self.assertEqual(gates["gross_never_above"], 1.0)

    def test_reused_dataset_is_consumed_researcher_exposed_development(self) -> None:
        matches = [
            s for s in self.datasets["dataset_slices"]
            if s.get("dataset_slice_id") == "BRRK-WINNER-0001-CANONICAL-HIST-V1"
        ]
        self.assertEqual(len(matches), 1)
        item = matches[0]
        self.assertEqual(item["data_budget"], "DEVELOPMENT")
        self.assertEqual(item["contamination_state"], "RESEARCHER_EXPOSED_HISTORY")
        self.assertTrue(item["researcher_exposed_history"])
        self.assertTrue(item["consumed"])
        self.assertEqual(self.formal["development_dataset_ref"], item["dataset_slice_id"])
        self.assertTrue(self.formal["development_evidence_is_researcher_exposed"])
        self.assertTrue(self.formal["development_dataset_already_consumed"])

    def test_no_economics_or_authority_in_preregistration(self) -> None:
        self.assertEqual(self.formal["status"], "PREREGISTERED_NOT_RUN")
        self.assertFalse(self.formal["economics_executed"])
        self.assertEqual(self.formal["actual_variants_evaluated"], 0)
        self.assertFalse(self.formal["production_authorized"])
        self.assertFalse(self.formal["phase6_observation_changed"])
        self.assertFalse(self.formal["canonical_brrk_changed"])
        self.assertTrue(self.formal["same_id_rescue_tuning_forbidden"])

    def test_readme_states_development_only_and_future_validation_gate(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("PREREGISTERED_NOT_RUN", text)
        self.assertIn("No new allocation split is searched", text)
        self.assertIn("already consumed and researcher-exposed DEVELOPMENT history", text)
        self.assertIn("future-only validation stage eligible", text)
        self.assertNotIn("Status: **PASS", text)


if __name__ == "__main__":
    unittest.main()
