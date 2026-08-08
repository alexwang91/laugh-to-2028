from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research.governance.enforce_future import FUTURE_PRESENCE_FIELDS, enforce_changed_paths


def _root(records: list[dict]) -> Path:
    root = Path(tempfile.mkdtemp())
    path = root / "config/research_registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "schema_version": 1,
        "registry_id": "RESEARCH-REGISTRY-V1",
        "research_governance_version": 1,
        "legacy_boundary_commit": "896cbd123b7a0c38943815dd802f0f9dcd12e1c2",
        "records": records,
        "research_governance_debt": [],
    }), encoding="utf-8")
    return root


def _future(rid: str, prefixes: list[str] | None = None) -> dict:
    values = {
        "research_id": rid,
        "research_family_id": "TEST_FAMILY",
        "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1",
        "objective_type": "MECHANISM_TEST",
        "research_domain": "ROBUSTNESS_AUDIT",
        "created_at": "2026-08-08T10:00:00Z",
        "created_before_result": True,
        "question": "Does the frozen mechanism contain information?",
        "hypothesis": "Frozen hypothesis.",
        "hypothesis_origin": "EXTERNAL_HYPOTHESIS",
        "economic_mechanism": "Frozen mechanism.",
        "primary_target": "future_target",
        "primary_metric": "metric",
        "secondary_metrics": [],
        "feature_families": ["TEST_INFORMATION"],
        "horizon": "1d",
        "universe": ["BTC"],
        "development_dataset_refs": [],
        "validation_dataset_refs": [],
        "sealed_dataset_refs": [],
        "declared_variant_budget": 1,
        "actual_variants_evaluated": 0,
        "stopping_rule": "Run frozen variant once.",
        "success_criteria": ["predeclared pass"],
        "failure_criteria": ["otherwise fail"],
        "allowed_followup": ["next stage if pass"],
        "forbidden_followup": ["same-line rescue after fail"],
        "researcher_decisions": [],
        "research_process_complexity": {
            "declared_parameter_candidates": ["default"],
            "actual_parameter_candidates_evaluated": [],
            "universes_evaluated": [["BTC"]],
            "horizons_evaluated": ["1d"],
            "rebalance_variants": [],
            "feature_representations": ["TEST_INFORMATION"],
            "special_cases_introduced": [],
            "validation_exposure_event_refs": [],
        },
        "lineage_edges": [],
        "result_status": "PREREGISTERED_NOT_RUN",
        "failure_reason": None,
        "promotion_state": "NONE",
        "evidence_refs": [],
        "production_relevance": "research only",
        "production_authorized": False,
        "provenance_status": "FACT",
        "governed_path_prefixes": prefixes if prefixes is not None else [f"research/{rid.lower()}/"],
    }
    self_missing = set(FUTURE_PRESENCE_FIELDS) - set(values)
    if self_missing:
        raise AssertionError(f"fixture missing future fields: {sorted(self_missing)}")
    return values


class FutureEnforcementTests(unittest.TestCase):
    def test_unregistered_new_research_path_blocks(self):
        findings = enforce_changed_paths(_root([]), ["research/new_alpha/model.py"])
        self.assertIn("UNREGISTERED_FORMAL_RESEARCH_PATH", {item.code for item in findings})

    def test_registered_path_passes(self):
        record = _future("R-1", ["research/new_alpha/"])
        self.assertEqual(enforce_changed_paths(_root([record]), ["research/new_alpha/model.py"]), [])

    def test_result_path_requires_registration(self):
        findings = enforce_changed_paths(_root([]), ["research/results/new_alpha/summary.json"])
        self.assertIn("UNREGISTERED_FORMAL_RESEARCH_PATH", {item.code for item in findings})

    def test_failure_reason_key_is_required_but_null_is_allowed(self):
        record = _future("R-1", ["research/new_alpha/"])
        self.assertEqual(enforce_changed_paths(_root([record]), ["research/new_alpha/prereg.json"]), [])
        del record["failure_reason"]
        findings = enforce_changed_paths(_root([record]), ["research/new_alpha/prereg.json"])
        self.assertTrue(any(item.code == "MISSING_FUTURE_FIELD" and "failure_reason" in item.message for item in findings))

    def test_missing_governed_prefix_blocks_future_record(self):
        record = _future("R-1", [])
        findings = enforce_changed_paths(_root([record]), [])
        self.assertIn("MISSING_GOVERNED_PATH_PREFIX", {item.code for item in findings})

    def test_ambiguous_path_ownership_blocks(self):
        first = _future("R-1", ["research/new_alpha/"])
        second = _future("R-2", ["research/new_alpha/"])
        findings = enforce_changed_paths(_root([first, second]), ["research/new_alpha/model.py"])
        self.assertIn("AMBIGUOUS_RESEARCH_PATH_OWNERSHIP", {item.code for item in findings})

    def test_overbroad_prefix_blocks(self):
        record = _future("R-1", ["research/"])
        findings = enforce_changed_paths(_root([record]), [])
        self.assertIn("INVALID_GOVERNED_PATH_PREFIX", {item.code for item in findings})

    def test_governance_and_common_plumbing_are_not_formal_research_paths(self):
        findings = enforce_changed_paths(_root([]), [
            "research/governance/enforce_future.py",
            "research/common/io.py",
        ])
        self.assertEqual(findings, [])

    def test_unchanged_legacy_registry_is_grandfathered(self):
        legacy = {
            "research_id": "LEGACY-1",
            "research_family_id": "UNKNOWN",
            "research_governance_version": 1,
            "governance_mode": "RETROSPECTIVE_LEGACY",
            "objective_type": "FAILURE_ANALYSIS",
            "production_authorized": False,
        }
        self.assertEqual(enforce_changed_paths(_root([legacy]), []), [])


if __name__ == "__main__":
    unittest.main()
