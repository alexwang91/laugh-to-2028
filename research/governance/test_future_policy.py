from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from research.governance.future_policy import authorize_future_research_path


def _future_record(
    rid: str = "R-1",
    prefix: str = "research/new_alpha/",
    *,
    production_authorized: bool = False,
) -> dict:
    return {
        "research_id": rid,
        "research_family_id": "EXTERNAL_TEST_INFORMATION",
        "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1",
        "objective_type": "MECHANISM_TEST",
        "research_domain": "ROBUSTNESS_AUDIT",
        "created_at": "2026-08-08T12:00:00Z",
        "created_before_result": True,
        "question": "Does frozen external information add signal?",
        "hypothesis": "The frozen external information family contains incremental information.",
        "hypothesis_origin": "EXTERNAL_HYPOTHESIS",
        "economic_mechanism": "A predeclared external state may contain information absent from the frozen baseline.",
        "primary_target": "future_target",
        "primary_metric": "predeclared_loss_differential",
        "secondary_metrics": [],
        "feature_families": ["EXTERNAL_TEST_INFORMATION"],
        "horizon": "20d",
        "universe": ["BTC"],
        "development_dataset_refs": [],
        "validation_dataset_refs": [],
        "sealed_dataset_refs": [],
        "declared_variant_budget": 1,
        "actual_variants_evaluated": 0,
        "stopping_rule": "Run the one frozen variant once and stop.",
        "success_criteria": ["Primary metric passes the frozen criterion."],
        "failure_criteria": ["Otherwise fail or remain inconclusive."],
        "allowed_followup": ["Proceed only to the next preregistered research stage after pass."],
        "forbidden_followup": ["No same-line parameter rescue after failure."],
        "researcher_decisions": [],
        "research_process_complexity": {
            "declared_parameter_candidates": ["default"],
            "actual_parameter_candidates_evaluated": [],
            "universes_evaluated": [["BTC"]],
            "horizons_evaluated": ["20d"],
            "rebalance_variants": [],
            "feature_representations": ["EXTERNAL_TEST_INFORMATION"],
            "special_cases_introduced": [],
            "validation_exposure_event_refs": [],
        },
        "lineage_edges": [],
        "result_status": "PREREGISTERED_NOT_RUN",
        "failure_reason": None,
        "promotion_state": "NONE",
        "evidence_refs": [],
        "production_relevance": "Research-only; no automatic production authority.",
        "production_authorized": production_authorized,
        "provenance_status": "FACT",
        "governed_path_prefixes": [prefix],
    }


class GitRepoFixture:
    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self._git("init")
        self._git("config", "user.email", "governance-test@example.com")
        self._git("config", "user.name", "Governance Test")
        (self.root / "config").mkdir(parents=True)
        self.write_registry([])
        self.commit_all("legacy boundary")
        self.boundary = self._git("rev-parse", "HEAD")

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()

    def write_registry(self, records: list[dict]) -> None:
        path = self.root / "config/research_registry.json"
        path.write_text(
            json.dumps({
                "schema_version": 1,
                "registry_id": "RESEARCH-REGISTRY-V1",
                "research_governance_version": 1,
                "legacy_boundary_commit": "TEST_BOUNDARY",
                "records": records,
                "research_governance_debt": [],
            }, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def write(self, path: str, content: str = "x\n") -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def commit_all(self, message: str) -> str:
        self._git("add", "-A")
        self._git("commit", "-m", message)
        return self._git("rev-parse", "HEAD")


class FutureResearchProvenanceTests(unittest.TestCase):
    def test_registered_same_commit_new_path_passes(self):
        repo = GitRepoFixture()
        repo.write_registry([_future_record()])
        repo.write("research/new_alpha/model.py")
        intro = repo.commit_all("preregister and introduce future research")

        result = authorize_future_research_path(
            repo.root,
            repo.boundary,
            "research/new_alpha/model.py",
        )

        self.assertTrue(result.allowed, result.findings)
        self.assertEqual(result.research_id, "R-1")
        self.assertEqual(result.introduction_commit, intro)

    def test_post_hoc_registration_cannot_launder_prior_result_path(self):
        repo = GitRepoFixture()
        repo.write("research/new_alpha/model.py")
        repo.commit_all("introduce unregistered research")
        repo.write_registry([_future_record()])
        repo.commit_all("register after the path already existed")

        result = authorize_future_research_path(
            repo.root,
            repo.boundary,
            "research/new_alpha/model.py",
        )

        self.assertFalse(result.allowed)
        self.assertIn(
            "REGISTRATION_NOT_PRESENT_AT_PATH_INTRODUCTION",
            {item.code for item in result.findings},
        )

    def test_future_owner_cannot_take_over_legacy_research_tree(self):
        repo = GitRepoFixture()
        repo.write("research/legacy_family/frozen.txt")
        repo.commit_all("add legacy research tree")
        boundary = repo._git("rev-parse", "HEAD")

        repo.write_registry([_future_record(prefix="research/legacy_family/")])
        repo.write("research/legacy_family/new_model.py")
        repo.commit_all("attempt future ownership of legacy tree")

        result = authorize_future_research_path(
            repo.root,
            boundary,
            "research/legacy_family/new_model.py",
        )

        self.assertFalse(result.allowed)
        self.assertIn(
            "GOVERNED_PREFIX_EXISTED_AT_LEGACY_BOUNDARY",
            {item.code for item in result.findings},
        )

    def test_legacy_material_cannot_be_renamed_into_future_prefix(self):
        repo = GitRepoFixture()
        repo.write("research/legacy_source/model.py", "legacy\n")
        repo.commit_all("add legacy source")
        boundary = repo._git("rev-parse", "HEAD")

        repo.write_registry([_future_record()])
        (repo.root / "research/new_alpha").mkdir(parents=True)
        repo._git(
            "mv",
            "research/legacy_source/model.py",
            "research/new_alpha/model.py",
        )
        repo.commit_all("attempt rename laundering")

        result = authorize_future_research_path(
            repo.root,
            boundary,
            "research/new_alpha/model.py",
        )

        self.assertFalse(result.allowed)
        self.assertIn(
            "FUTURE_PATH_INTRODUCED_BY_RENAME_OR_COPY",
            {item.code for item in result.findings},
        )

    def test_research_record_cannot_authorize_production(self):
        repo = GitRepoFixture()
        repo.write_registry([_future_record(production_authorized=True)])
        repo.write("research/new_alpha/model.py")
        repo.commit_all("attempt illegal research production authority")

        result = authorize_future_research_path(
            repo.root,
            repo.boundary,
            "research/new_alpha/model.py",
        )

        self.assertFalse(result.allowed)
        self.assertIn(
            "ILLEGAL_RESEARCH_PRODUCTION_AUTHORIZATION",
            {item.code for item in result.findings},
        )


if __name__ == "__main__":
    unittest.main()
