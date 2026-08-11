from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "research" / "brrk_beta_handoff_0047"
RID = "BRRK-BETA-HANDOFF-EVENT-STUDY-0047"


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def raw_sha(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


class TestBrrkBetaHandoff0047Closeout(unittest.TestCase):
    def test_result_and_closeout_classification_are_exact(self):
        result = load("PRIMARY_RESULT.json")
        summary = load("RESULT_SUMMARY.json")
        closeout = load("CLOSEOUT.json")
        self.assertEqual(result["research_id"], RID)
        self.assertEqual(result["classification"]["result_status"], "FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE")
        self.assertEqual(summary["result_status"], "FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE")
        self.assertEqual(closeout["result_status"], "FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE")
        self.assertEqual(closeout["closeout_status"], "FAIL_NO_RECURRENT_DURABLE_HANDOFF_STRUCTURE / CLOSED")

    def test_primary_gate_values_match_unique_result(self):
        result = load("PRIMARY_RESULT.json")
        closeout = load("CLOSEOUT.json")
        c = result["classification"]
        self.assertEqual(c["total_BTC_positive_episodes"], 27)
        self.assertEqual(c["target_eligible_BTC_positive_episodes"], 27)
        self.assertEqual(c["primary_handoff_episodes"], 12)
        self.assertEqual(c["episode_level_durable_handoff_prevalence"], 12 / 27)
        self.assertEqual(c["ETH_primary_handoff_episodes"], 3)
        self.assertEqual(c["SOL_primary_handoff_episodes"], 9)
        self.assertTrue(c["gates"]["target_eligible_episode_count_ge_5"])
        self.assertTrue(c["gates"]["handoff_episode_count_ge_3"])
        self.assertFalse(c["gates"]["episode_level_prevalence_ge_0_50"])
        self.assertTrue(c["gates"]["ETH_cause_episode_count_ge_1"])
        self.assertTrue(c["gates"]["SOL_cause_episode_count_ge_1"])
        self.assertEqual(closeout["primary_stage_result"]["only_failed_hard_gate"], "episode_level_prevalence_ge_0_50")

    def test_official_recovery_artifact_binding_is_frozen(self):
        closeout = load("CLOSEOUT.json")
        artifact = closeout["official_recovery_artifact"]
        self.assertEqual(artifact["artifact_id"], 9084248250)
        self.assertEqual(artifact["source_run_id"], 31445193701)
        self.assertEqual(artifact["digest"], "sha256:b1992fa56b78a1a5807a156c8a483c0f035290669ff0e04095481d11000cde66")
        self.assertEqual(artifact["size_bytes"], 487959)
        self.assertFalse(artifact["expired"])

    def test_hash_semantics_preserve_original_and_recovered_identities(self):
        closeout = load("CLOSEOUT.json")
        hashes = closeout["result_hash_semantics"]
        self.assertEqual(hashes["primary_result_pre_serialization_object_sha256"], "961ac99bd5a2d3d6556262b17411333bfbeead921616dccf120190ee1dd67c2a")
        self.assertEqual(hashes["primary_result_recovered_raw_json_file_sha256"], raw_sha("PRIMARY_RESULT.json"))
        self.assertEqual(raw_sha("PRIMARY_RESULT.json"), "6c354b054bde2dfce12dbb1efe3809d59d371df02beddc613befe9373a17807d")
        reparsed = load("PRIMARY_RESULT.json")
        canonical = json.dumps(reparsed, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), "35f0ee3934d45e19b5b652fa13b0cfa1f328aac51843ac9432e8cc94d20dd6b8")
        self.assertNotEqual(hashes["primary_result_pre_serialization_object_sha256"], hashes["primary_result_reparsed_canonical_sha256"])

    def test_recovery_is_not_a_second_research_execution(self):
        recovery = load("EVIDENCE_RECOVERY.json")
        closeout = load("CLOSEOUT.json")
        marker = load("RUN_ONCE.marker")
        self.assertEqual(recovery["recovery_type"], "EVIDENCE_RECOVERY_NOT_NEW_RESEARCH_EXECUTION")
        self.assertFalse(recovery["new_research_execution"])
        self.assertEqual(recovery["actual_variants_evaluated_before_recovery"], 1)
        self.assertEqual(recovery["actual_variants_evaluated_after_recovery"], 1)
        self.assertTrue(recovery["recovery_hash_match"])
        self.assertEqual(closeout["unique_scientific_execution"]["github_actions_run_id"], 31444910921)
        self.assertEqual(closeout["unique_scientific_execution"]["github_actions_job_id"], 93636897419)
        self.assertFalse(marker["same_id_rerun_allowed"])
        self.assertFalse(marker["same_id_retuning_allowed"])
        self.assertFalse(marker["same_id_rescue_allowed"])

    def test_method_and_authority_boundaries_remain_closed(self):
        result = load("PRIMARY_RESULT.json")
        closeout = load("CLOSEOUT.json")
        for key, value in result["method_compliance"].items():
            self.assertTrue(value, key)
        authority = closeout["authority"]
        self.assertFalse(authority["duration_aware_handoff_model_stage_eligible"])
        self.assertFalse(authority["duration_aware_handoff_model_fitted"])
        self.assertFalse(authority["portfolio_allocation_tested"])
        self.assertFalse(authority["portfolio_economics_executed"])
        self.assertFalse(authority["canonical_strategy_changed"])
        self.assertFalse(authority["phase6_observation_changed"])
        self.assertFalse(authority["production_authorized"])
        self.assertFalse(authority["signature_authorized"])
        self.assertFalse(authority["order_submission_authorized"])

    def test_no_write_enabled_0047_execution_workflow_remains(self):
        workflow_dir = ROOT / ".github" / "workflows"
        forbidden = {
            "tmp-0047-market-evidence-only.yml",
            "tmp-0047-evaluate-once.yml",
            "tmp-0047-evidence-recovery.yml",
            "tmp-0047-closeout-finalize.yml",
        }
        existing = {p.name for p in workflow_dir.glob("*.yml")}
        self.assertTrue(forbidden.isdisjoint(existing))


if __name__ == "__main__":
    unittest.main()
