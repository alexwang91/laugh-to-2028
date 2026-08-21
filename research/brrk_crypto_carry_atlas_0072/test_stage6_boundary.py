from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class TestCarryAtlasStage6Boundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.boundary = json.loads((ROOT / "CONTROLLED_EXECUTION_BOUNDARY.json").read_text(encoding="utf-8"))
        cls.schema = json.loads((ROOT / "RESULT_SCHEMA.json").read_text(encoding="utf-8"))

    def test_boundary_has_exact_stage_and_zero_authority(self):
        b = self.boundary
        self.assertEqual(b["research_id"], "BRRK-CRYPTO-CARRY-ATLAS-0072")
        self.assertEqual(b["stage"], "CONTROLLED_EXECUTION_BOUNDARY_NOT_RUN")
        self.assertFalse(b["boundary_authorizes_controlled_execution_now"])
        self.assertFalse(b["boundary_authorizes_raw_read_now"])
        self.assertFalse(b["boundary_authorizes_network_fetch"])
        self.assertEqual(b["controlled_scientific_history_reads_at_boundary"], 0)
        self.assertEqual(b["stage8_attempt_consumed_at_boundary"], 0)
        self.assertFalse(b["production_authorized"])
        self.assertFalse(b["signature_authorized"])
        self.assertFalse(b["order_submission_authorized"])

    def test_exact_six_scientific_objects_and_one_read_each(self):
        objects = self.boundary["scientific_raw_objects"]
        self.assertEqual(len(objects), 6)
        self.assertEqual(len({x["canonical_request_id"] for x in objects}), 6)
        self.assertTrue(all(x["read_budget"] == 1 for x in objects))
        self.assertEqual(self.boundary["controlled_read_budget"]["scientific_archive_object_reads_total"], 6)
        self.assertEqual(self.boundary["controlled_read_budget"]["CAPTURE_0002_RAW_ARTIFACT_DOWNLOAD"], 1)

    def test_support_only_objects_are_forbidden_for_science(self):
        forbidden = self.boundary["forbidden_scientific_raw_objects"]
        self.assertEqual(len(forbidden), 9)
        self.assertEqual(sum("PREMIUM_INDEX" in x for x in forbidden), 3)
        self.assertTrue(all("MARK_PRICE" in x or "INDEX_PRICE" in x or "PREMIUM_INDEX" in x for x in forbidden))
        self.assertFalse(self.boundary["frozen_science"]["premiumIndexKlines_as_funding_allowed"])

    def test_marker_must_precede_download_and_content_read(self):
        a = self.boundary["attempt_contract"]
        self.assertEqual(a["attempt_budget"], 1)
        self.assertTrue(a["durable_RUN_ATTEMPT_marker_must_precede_raw_artifact_download"])
        self.assertTrue(a["durable_RUN_ATTEMPT_marker_must_precede_any_controlled_content_read"])
        self.assertTrue(a["marker_must_be_remote_and_durable_before_read"])
        self.assertFalse(a["same_id_rerun_after_marker"])
        self.assertFalse(a["same_id_retune_after_marker"])
        self.assertFalse(a["same_id_rescue_after_marker"])
        self.assertFalse(a["same_id_recompute_after_marker"])

    def test_stage7_preflight_is_identity_only(self):
        p = self.boundary["zero_result_preflight"]
        self.assertEqual(p["stage"], 7)
        self.assertTrue(p["must_run_only_after_this_boundary_is_merged"])
        self.assertTrue(p["identity_and_metadata_only"])
        self.assertFalse(p["raw_artifact_download_allowed"])
        self.assertFalse(p["raw_archive_value_read_allowed"])
        self.assertEqual(p["requires_controlled_scientific_history_reads"], 0)
        self.assertEqual(p["requires_attempt_consumed"], 0)
        self.assertEqual(p["requires_source_network_fetches"], 0)

    def test_result_chain_is_create_only_and_ordered(self):
        r = self.boundary["result_persistence"]
        self.assertEqual(r["result_branch"], "research/0072-result-v1")
        self.assertEqual(r["create_only_artifacts_in_order"], [
            "RUN_ATTEMPT.marker", "PRIMARY_RESULT.json", "EVIDENCE.json", "EXECUTION.json", "RUN_ONCE.marker"
        ])
        self.assertFalse(r["overwrite_allowed"])
        self.assertTrue(r["hash_chain_required"])
        self.assertEqual(r["finalization_controlled_rereads"], 0)

    def test_result_schema_matches_preregistered_candidate_count(self):
        s = self.schema
        self.assertEqual(s["candidate_accounting"]["hypothesis_count_exact"], 6)
        self.assertEqual(len(s["candidate_accounting"]["hypothesis_ids_exact"]), 6)
        self.assertEqual(len(s["terminal_gate_ids"]), 7)
        self.assertEqual(s["source_read_counts"]["network_fetches_exact"], 0)
        self.assertEqual(s["source_read_counts"]["refetches_exact"], 0)
        self.assertTrue(s["create_only"])
        self.assertFalse(s["overwrite_allowed"])


if __name__ == "__main__":
    unittest.main()
