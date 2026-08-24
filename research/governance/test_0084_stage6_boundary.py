from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RID_DIR = ROOT / "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084"
SOURCE_DIR = ROOT / "research/brrk_crypto_cross_sectional_factor_atlas_0075"


def _blob(path: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class Test0084Stage6ControlledBoundary(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads((RID_DIR / "CONTROLLED_BOUNDARY_CONTRACT.json").read_text())

    def test_replacement_frozen_execution_identities(self) -> None:
        expected = {
            "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084/PREREGISTRATION.md": self.contract["frozen_preregistration_blob"],
            "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084/IMPLEMENTATION_CONTRACT.json": self.contract["frozen_implementation_contract_blob"],
            "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084/engine.py": self.contract["frozen_engine_blob"],
            "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084/execution_interface.py": self.contract["frozen_execution_interface_blob"],
            "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084/integration.py": self.contract["frozen_integration_blob"],
            "research/brrk_crypto_cross_sectional_factor_atlas_replacement_0084/NONHISTORICAL_QUALIFICATION.md": self.contract["stage5_qualification_blob"],
        }
        for path, blob in expected.items():
            self.assertEqual(_blob(path), blob, path)

    def test_zero_result_identity_staging_evidence(self) -> None:
        reuse = self.contract["identity_staging_reuse"]
        manifest = SOURCE_DIR / "AUTHORIZED_OBJECT_MANIFEST.json"
        universe = SOURCE_DIR / "STAGE6_SYMBOL_UNIVERSE.json"
        staging = SOURCE_DIR / "STAGE6_STAGING_EVIDENCE.json"

        self.assertTrue(reuse["allowed"])
        self.assertFalse(reuse["scientific_result_inherited"])
        self.assertFalse(reuse["lifecycle_credit_inherited"])
        self.assertEqual(_blob("research/brrk_crypto_cross_sectional_factor_atlas_0075/AUTHORIZED_OBJECT_MANIFEST.json"), reuse["source_manifest_git_blob"])
        self.assertEqual(_blob("research/brrk_crypto_cross_sectional_factor_atlas_0075/STAGE6_SYMBOL_UNIVERSE.json"), reuse["source_symbol_universe_git_blob"])
        self.assertEqual(_blob("research/brrk_crypto_cross_sectional_factor_atlas_0075/STAGE6_STAGING_EVIDENCE.json"), reuse["source_staging_evidence_git_blob"])
        self.assertEqual(_sha256(manifest), reuse["source_manifest_sha256"])
        self.assertEqual(_sha256(universe), reuse["source_symbol_universe_sha256"])

        evidence = json.loads(staging.read_text())
        self.assertEqual(evidence["artifact_id"], str(reuse["artifact_id"]))
        self.assertEqual(evidence["artifact_name"], reuse["artifact_name"])
        self.assertEqual(evidence["artifact_retention_days"], reuse["artifact_retention_days"])
        self.assertEqual(evidence["authorized_payload_objects"], 53541)
        self.assertEqual(evidence["hash_verified_objects"], 53541)
        self.assertEqual(evidence["offline_zip_readability_passed_objects"], 53541)
        self.assertEqual(evidence["candidate_symbol_count"], 652)
        self.assertEqual(evidence["controlled_scientific_history_reads"], 0)
        self.assertEqual(evidence["scientific_engine_calls"], 0)
        self.assertEqual(evidence["stage8_scientific_source_network_fetches"], 0)
        self.assertFalse(evidence["scientific_values_exposed"])

    def test_stage6_and_stage8_budgets(self) -> None:
        budgets = self.contract["budgets"]
        self.assertEqual(budgets["controlled_attempt_total"], 1)
        self.assertEqual(budgets["controlled_attempt_consumed"], 0)
        self.assertEqual(budgets["controlled_scientific_history_reads_stage6"], 0)
        self.assertEqual(budgets["scientific_engine_calls_stage6"], 0)
        self.assertEqual(budgets["scientific_engine_calls_stage8_exact"], 1)
        self.assertEqual(budgets["scientific_source_network_fetches_stage8_exact"], 0)
        self.assertEqual(budgets["authorized_object_max_controlled_reads_stage8"], 1)
        self.assertTrue(self.contract["marker_before_read"])
        self.assertTrue(self.contract["create_only_result_persistence"])
        self.assertTrue(self.contract["stage6_scientific_payload_values_forbidden"])
        self.assertTrue(self.contract["stage7_scientific_payload_values_forbidden"])

    def test_result_artifacts_absent_before_stage8_execution(self) -> None:
        forbidden = (
            "PRIMARY_RESULT.json",
            "EVIDENCE.json",
            "EXECUTION.json",
            "RUN_ONCE.marker",
        )
        for name in forbidden:
            self.assertFalse((RID_DIR / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
