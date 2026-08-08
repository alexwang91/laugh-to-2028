from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from research.governance.audit import audit_snapshot, render_text
from research.governance.validate import validate_repo

BOUNDARY = "896cbd123b7a0c38943815dd802f0f9dcd12e1c2"


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _root() -> Path:
    root = Path(tempfile.mkdtemp())
    _write(root / "config/research_governance_v1.json", {
        "research_governance_version": 1,
        "legacy_boundary_commit": BOUNDARY,
        "research_domains": ["DIRECTION_REGIME", "ROBUSTNESS_AUDIT"],
        "objective_types": ["ALPHA_DISCOVERY", "ROBUSTNESS_AUDIT"],
        "lineage_relation_types": [
            "RESULT_INFORMED", "PARAMETER_DESCENDANT", "MECHANISM_FORK", "NEW_TARGET_FORK",
            "NEW_DATA_FORK", "IMPLEMENTATION_FIX", "MEASUREMENT_FIX", "EXTERNAL_HYPOTHESIS",
            "INDEPENDENT_REPLICATION", "SUPERSEDES",
        ],
    })
    _write(root / "config/research_registry.json", {
        "schema_version": 1, "registry_id": "RESEARCH-REGISTRY-V1", "research_governance_version": 1,
        "legacy_boundary_commit": BOUNDARY, "records": [], "research_governance_debt": [],
    })
    _write(root / "config/dataset_exposure_registry.json", {
        "schema_version": 1, "registry_id": "DATASET-EXPOSURE-REGISTRY-V1", "research_governance_version": 1,
        "dataset_slices": [], "exposure_events": [],
    })
    _write(root / "config/edge_registry.json", {
        "schema_version": 1, "registry_id": "EDGE-REGISTRY-V1", "research_governance_version": 1, "entries": [],
    })
    _write(root / "config/decision_registry.json", {"schema_version": 1, "production_authorized_components": [], "decisions": []})
    for name in ("research_registry.schema.json", "dataset_exposure_registry.schema.json", "edge_registry.schema.json"):
        _write(root / "research/governance/schemas" / name, {"$id": name})
    return root


def _record(rid: str, family: str = "PRICE_TREND") -> dict:
    return {
        "research_id": rid, "research_family_id": family, "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1", "objective_type": "ALPHA_DISCOVERY",
        "research_domain": "DIRECTION_REGIME", "created_at": "2026-08-08T10:00:00Z",
        "created_before_result": True, "question": "Does X contain information about Y?",
        "hypothesis": "X predicts Y.", "hypothesis_origin": "EXTERNAL_HYPOTHESIS",
        "economic_mechanism": "Mechanism.", "primary_target": "future_return", "primary_metric": "rank_ic",
        "secondary_metrics": ["hit_rate"], "feature_families": ["PRICE_TREND"], "horizon": "20d",
        "universe": ["BTC", "ETH", "SOL", "BNB"], "development_dataset_refs": [],
        "validation_dataset_refs": [], "sealed_dataset_refs": [], "declared_variant_budget": 1,
        "actual_variants_evaluated": 0, "stopping_rule": "Run frozen variant once.",
        "success_criteria": ["rank_ic > threshold"], "failure_criteria": ["otherwise fail"],
        "allowed_followup": ["robustness if pass"], "forbidden_followup": ["same-line rescue after fail"],
        "researcher_decisions": [],
        "research_process_complexity": {
            "declared_parameter_candidates": ["default"], "actual_parameter_candidates_evaluated": [],
            "universes_evaluated": [["BTC", "ETH", "SOL", "BNB"]], "horizons_evaluated": ["20d"],
            "rebalance_variants": [], "feature_representations": ["PRICE_TREND"],
            "special_cases_introduced": [], "validation_exposure_event_refs": [],
        },
        "lineage_edges": [], "result_status": "PREREGISTERED_NOT_RUN", "promotion_state": "NONE",
        "evidence_refs": [], "decision_refs": [], "production_relevance": "research only",
        "production_authorized": False, "provenance_status": "FACT", "governed_path_prefixes": [],
    }


def _records(root: Path, records: list[dict], debt=None) -> None:
    path = root / "config/research_registry.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["records"] = records
    if debt is not None:
        value["research_governance_debt"] = debt
    _write(path, value)


class GovernanceTests(unittest.TestCase):
    def test_empty_registries_pass(self):
        root = _root()
        self.assertEqual(validate_repo(root), [])
        self.assertEqual(audit_snapshot(root)["overall"], "PASS")

    def test_duplicate_research_id_blocks(self):
        root = _root()
        item = _record("R-1")
        _records(root, [item, deepcopy(item)])
        self.assertIn("DUPLICATE_RESEARCH_ID", {x.code for x in validate_repo(root)})

    def test_missing_primary_metric_blocks_future(self):
        root = _root()
        item = _record("R-1")
        del item["primary_metric"]
        _records(root, [item])
        self.assertIn("MISSING_PROGRAM_FIELD", {x.code for x in validate_repo(root)})

    def test_variant_budget_is_fail_closed(self):
        root = _root()
        item = _record("R-1")
        item["actual_variants_evaluated"] = 2
        _records(root, [item])
        self.assertIn("UNREGISTERED_VARIANTS", {x.code for x in validate_repo(root)})

    def test_invalid_parent_blocks(self):
        root = _root()
        item = _record("R-1")
        item["lineage_edges"] = [{"relation": "RESULT_INFORMED", "ref_research_id": "MISSING", "provenance_status": "FACT"}]
        _records(root, [item])
        self.assertIn("INVALID_LINEAGE_REF", {x.code for x in validate_repo(root)})

    def test_circular_lineage_blocks(self):
        root = _root()
        a, b = _record("A"), _record("B")
        a["lineage_edges"] = [{"relation": "RESULT_INFORMED", "ref_research_id": "B", "provenance_status": "FACT"}]
        b["lineage_edges"] = [{"relation": "RESULT_INFORMED", "ref_research_id": "A", "provenance_status": "FACT"}]
        _records(root, [a, b])
        self.assertIn("CIRCULAR_LINEAGE", {x.code for x in validate_repo(root)})

    def test_result_informed_cannot_claim_independent_replication(self):
        root = _root()
        a, b, c = _record("A"), _record("B"), _record("C")
        c["lineage_edges"] = [
            {"relation": "RESULT_INFORMED", "ref_research_id": "A", "provenance_status": "FACT"},
            {"relation": "INDEPENDENT_REPLICATION", "ref_research_id": "B", "provenance_status": "FACT"},
        ]
        _records(root, [a, b, c])
        self.assertIn("FALSE_INDEPENDENCE", {x.code for x in validate_repo(root)})

    def test_released_sealed_slice_must_be_consumed(self):
        root = _root()
        item = _record("R-1")
        item["sealed_dataset_refs"] = ["S-1"]
        _records(root, [item])
        _write(root / "config/dataset_exposure_registry.json", {
            "schema_version": 1, "registry_id": "DATASET-EXPOSURE-REGISTRY-V1", "research_governance_version": 1,
            "dataset_slices": [{
                "dataset_slice_id": "S-1", "dataset_id": "D", "dataset_version": "v1", "source": "source",
                "assets": ["BTC"], "fields": ["close"], "resolution": "1d", "start": "2026-01-01",
                "end": "2026-02-01", "transformation": "none", "pit_publication_semantics": "public close",
                "data_budget": "SEALED", "contamination_state": "DATA_SEALED", "consumed": False,
                "researcher_exposed_history": False, "provenance_status": "FACT", "evidence_refs": [],
            }],
            "exposure_events": [{
                "exposure_id": "E-1", "research_id": "R-1", "dataset_slice_ref": "S-1",
                "timestamp": "2026-08-08T10:00:00Z", "release_type": "PASS_FAIL_ONLY",
                "result_informed_followup": False, "provenance_status": "FACT", "evidence_ref": None,
            }],
        })
        self.assertIn("CONSUMED_SEALED_CLAIMED_PRISTINE", {x.code for x in validate_repo(root)})

    def test_completed_future_research_requires_four_dimensional_scorecard(self):
        root = _root()
        item = _record("R-1")
        item["result_status"] = "PASS"
        item["evidence_refs"] = ["result.json"]
        _records(root, [item])
        self.assertIn("MISSING_EVIDENCE_SCORECARD", {x.code for x in validate_repo(root)})

    def test_edge_admission_requires_incremental_pass(self):
        root = _root()
        _write(root / "config/edge_registry.json", {
            "schema_version": 1, "registry_id": "EDGE-REGISTRY-V1", "research_governance_version": 1,
            "entries": [{"edge_id": "EDGE-1", "status": "ADMITTED", "incremental_evidence_status": "UNKNOWN",
                         "evidence_refs": ["x"], "production_authorized": False}],
        })
        self.assertIn("EDGE_ADMISSION_WITHOUT_INCREMENTAL_PASS", {x.code for x in validate_repo(root)})

    def test_legacy_unknown_is_warning_not_failure(self):
        root = _root()
        legacy = {
            "research_id": "LEGACY-1", "research_family_id": "UNKNOWN", "research_governance_version": 1,
            "governance_mode": "RETROSPECTIVE_LEGACY", "objective_type": "ROBUSTNESS_AUDIT",
            "production_authorized": False, "provenance_status": "UNKNOWN", "lineage_edges": [],
        }
        debt = [{"debt_id": "DEBT-1", "category": "historical_trials_unknown", "status": "OPEN",
                 "description": "Historical trial count unknown.", "affected_research_ids": ["LEGACY-1"], "evidence_refs": []}]
        _records(root, [legacy], debt)
        findings = validate_repo(root)
        self.assertFalse(any(x.severity in {"ERROR", "BLOCKING"} for x in findings))
        self.assertEqual(audit_snapshot(root)["overall"], "WARNING")

    def test_audit_is_deterministic(self):
        root = _root()
        first, second = audit_snapshot(root), audit_snapshot(root)
        self.assertEqual(first, second)
        self.assertEqual(render_text(first), render_text(second))


if __name__ == "__main__":
    unittest.main()
