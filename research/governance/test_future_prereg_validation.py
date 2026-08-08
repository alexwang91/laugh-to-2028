from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research.governance.validate import has_failures, repo_root_from_module, validate_repo


def _future_prereg() -> dict:
    return {
        "research_id": "FUTURE-PREREG-TEST-0001",
        "research_family_id": "EXTERNAL_INFORMATION_TEST",
        "research_domain": "DIRECTION_REGIME",
        "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1",
        "objective_type": "MECHANISM_TEST",
        "created_at": "2026-08-08T12:38:18Z",
        "created_before_result": True,
        "question": "Does the frozen external information family add predictive information beyond the frozen baseline?",
        "hypothesis": "The frozen external information family contains incremental information beyond the frozen baseline.",
        "hypothesis_origin": "EXTERNAL_HYPOTHESIS",
        "economic_mechanism": "A predeclared external state may contain information not present in the frozen baseline state vector.",
        "primary_target": "future_20d_frozen_baseline_outcome",
        "primary_metric": "walk_forward_oos_loss_differential",
        "secondary_metrics": [],
        "feature_families": ["EXTERNAL_INFORMATION_STATE_V1"],
        "horizon": "20d",
        "universe": ["BTC", "ETH", "SOL", "BNB"],
        "development_dataset_refs": [],
        "validation_dataset_refs": [],
        "sealed_dataset_refs": [],
        "declared_variant_budget": 1,
        "actual_variants_evaluated": 0,
        "parameter_candidate_count": 1,
        "stopping_rule": "Run one frozen variant once; failure or inconclusive evidence stops this research ID.",
        "success_criteria": ["The frozen primary metric satisfies its preregistered positive-information criterion."],
        "failure_criteria": ["The frozen primary metric fails its preregistered positive-information criterion."],
        "allowed_followup": ["A pass may create a separately preregistered robustness-stage research ID."],
        "forbidden_followup": ["No same-ID parameter, target, horizon, universe or feature rescue after observing results."],
        "researcher_decisions": [],
        "research_process_complexity": {
            "declared_parameter_candidates": ["FROZEN_SINGLE_VARIANT"],
            "actual_parameter_candidates_evaluated": [],
            "universes_evaluated": [],
            "horizons_evaluated": [],
            "rebalance_variants": [],
            "feature_representations": ["EXTERNAL_INFORMATION_STATE_V1"],
            "special_cases_introduced": [],
            "validation_exposure_event_refs": [],
            "related_family_trials": 1,
        },
        "lineage_edges": [],
        "result_status": "PREREGISTERED_NOT_RUN",
        "failure_reason": None,
        "promotion_state": "NONE",
        "evidence_refs": [],
        "production_relevance": "Research-only; pass cannot authorize production.",
        "production_authorized": False,
        "provenance_status": "FACT",
        "governed_path_prefixes": ["research/future_prereg_test_0001/"],
        "notes": [],
    }


def _fixture_root(record: dict) -> Path:
    source = repo_root_from_module()
    root = Path(tempfile.mkdtemp())
    (root / "config").mkdir(parents=True)
    (root / "research/governance/schemas").mkdir(parents=True)

    for name in (
        "research_governance_v1.json",
        "research_registry.json",
        "dataset_exposure_registry.json",
        "edge_registry.json",
        "decision_registry.json",
    ):
        shutil.copy2(source / "config" / name, root / "config" / name)
    for name in (
        "dataset_exposure_registry.schema.json",
        "edge_registry.schema.json",
        "research_registry.schema.json",
    ):
        shutil.copy2(
            source / "research/governance/schemas" / name,
            root / "research/governance/schemas" / name,
        )

    registry_path = root / "config/research_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["records"].append(record)
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return root


class FuturePreregistrationValidationTests(unittest.TestCase):
    def test_empty_pre_result_accounting_arrays_are_valid(self):
        findings = validate_repo(_fixture_root(_future_prereg()))
        future = [item for item in findings if item.subject == "FUTURE-PREREG-TEST-0001"]
        self.assertFalse(has_failures(future), future)
        self.assertNotIn("MISSING_PROGRAM_FIELD", {item.code for item in future})
        self.assertNotIn("BLANK_PROGRAM_FIELD", {item.code for item in future})

    def test_preregistered_not_run_rejects_result_evidence(self):
        record = _future_prereg()
        record["evidence_refs"] = ["research/results/future/summary.json"]
        findings = validate_repo(_fixture_root(record))
        codes = {item.code for item in findings if item.subject == record["research_id"]}
        self.assertIn("PREREG_WITH_RESULT_EVIDENCE", codes)

    def test_preregistered_not_run_rejects_evaluated_variants(self):
        record = _future_prereg()
        record["actual_variants_evaluated"] = 1
        findings = validate_repo(_fixture_root(record))
        codes = {item.code for item in findings if item.subject == record["research_id"]}
        self.assertIn("PREREG_WITH_EVALUATED_VARIANTS", codes)

    def test_preregistered_not_run_requires_no_promotion(self):
        record = _future_prereg()
        record["promotion_state"] = "CANDIDATE"
        findings = validate_repo(_fixture_root(record))
        codes = {item.code for item in findings if item.subject == record["research_id"]}
        self.assertIn("PREREG_WITH_PROMOTION", codes)


if __name__ == "__main__":
    unittest.main()
