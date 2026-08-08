from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .validate import SEVERITY_ORDER, load_json, repo_root_from_module, validate_repo


def _failed(value: Any) -> bool:
    text = str(value or "").upper()
    return any(token in text for token in ("FAIL", "REJECT", "NO_PROMOTION", "STOPPED"))


def _shadow(value: Any) -> bool:
    return "SHADOW" in str(value or "").upper()


def _promoted(value: Any) -> bool:
    text = str(value or "").upper()
    return "PROMOT" in text and "NO_PROMOTION" not in text


def audit_snapshot(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or repo_root_from_module())
    governance = load_json(root / "config/research_governance_v1.json")
    research = load_json(root / "config/research_registry.json")
    dataset = load_json(root / "config/dataset_exposure_registry.json")
    edge = load_json(root / "config/edge_registry.json")
    decision = load_json(root / "config/decision_registry.json")
    records = [item for item in research.get("records", []) if isinstance(item, dict)]
    slices = [item for item in dataset.get("dataset_slices", []) if isinstance(item, dict)]
    events = [item for item in dataset.get("exposure_events", []) if isinstance(item, dict)]
    findings = validate_repo(root)

    family_counts: Counter[str] = Counter()
    variants = 0
    parameters = 0
    preregistered = 0
    post_hoc = 0
    result_informed: set[str] = set()
    failed_ids = {item.get("research_id") for item in records if _failed(item.get("result_status"))}
    failed_ancestors = 0
    signatures: defaultdict[tuple[str, ...], set[str]] = defaultdict(set)

    for item in records:
        family = str(item.get("research_family_id") or "UNKNOWN")
        family_counts[family] += 1
        if isinstance(item.get("actual_variants_evaluated"), int):
            variants += item["actual_variants_evaluated"]
        dof = item.get("research_process_complexity", {})
        actual_params = dof.get("actual_parameter_candidates_evaluated", []) if isinstance(dof, dict) else []
        if isinstance(actual_params, list):
            parameters += len(actual_params)
        if item.get("created_before_result") is True:
            preregistered += 1
        elif item.get("created_before_result") is False:
            post_hoc += 1
        for link in item.get("lineage_edges", []) if isinstance(item.get("lineage_edges", []), list) else []:
            if not isinstance(link, dict):
                continue
            if link.get("relation") == "RESULT_INFORMED":
                result_informed.add(str(item.get("research_id")))
            if link.get("ref_research_id") in failed_ids:
                failed_ancestors += 1
        features = item.get("feature_families", [])
        if isinstance(features, list) and features:
            signatures[tuple(sorted(set(map(str, features))))].add(family)

    duplications = [
        {"feature_family_signature": list(signature), "research_families": sorted(families)}
        for signature, families in sorted(signatures.items()) if len(families) > 1
    ]
    severity = Counter(item.severity for item in findings)
    overall = "FAIL" if severity["ERROR"] or severity["BLOCKING"] else "WARNING" if severity["WARNING"] else "PASS"
    codes = Counter(item.code for item in findings)
    return {
        "title": "Research Governance Audit",
        "governance_version": governance.get("research_governance_version"),
        "legacy_boundary": governance.get("legacy_boundary_commit"),
        "total_research_records": len(records),
        "program_governed_records": sum(item.get("governance_mode") == "PROGRAM_GOVERNED_V1" for item in records),
        "legacy_retrospective_records": sum(item.get("governance_mode") == "RETROSPECTIVE_LEGACY" for item in records),
        "preregistered": preregistered,
        "post_hoc": post_hoc,
        "failed": sum(_failed(item.get("result_status")) for item in records),
        "stopped": sum("STOP" in str(item.get("result_status") or "").upper() for item in records),
        "shadow_only": sum(_shadow(item.get("result_status")) or _shadow(item.get("promotion_state")) for item in records),
        "promoted": sum(_promoted(item.get("promotion_state")) for item in records),
        "research_families": len(family_counts),
        "family_trial_counts": dict(sorted(family_counts.items())),
        "variants_evaluated_known_total": variants,
        "parameter_candidates_known_total": parameters,
        "validation_exposure_events": len(events),
        "consumed_sealed_datasets": sum(item.get("data_budget") == "SEALED" and item.get("consumed") is True for item in slices),
        "researcher_exposed_historical_slices": sum(item.get("researcher_exposed_history") is True or item.get("contamination_state") == "RESEARCHER_EXPOSED_HISTORY" for item in slices),
        "missing_primary_metrics": sum(not item.get("primary_metric") for item in records),
        "missing_stopping_rules": sum(not item.get("stopping_rule") for item in records),
        "missing_lineage": sum(not item.get("lineage_edges") for item in records),
        "invalid_lineage": codes["INVALID_LINEAGE_REF"] + codes["INVALID_LINEAGE_RELATION"] + codes["INVALID_LINEAGE_EDGE"],
        "circular_lineage": codes["CIRCULAR_LINEAGE"],
        "unregistered_variants": codes["UNREGISTERED_VARIANTS"],
        "potential_family_duplication": duplications,
        "result_informed_descendant_count": len(result_informed),
        "failed_ancestor_count": failed_ancestors,
        "research_governance_debt": sum(isinstance(item, dict) and item.get("status") != "RESOLVED" for item in research.get("research_governance_debt", [])),
        "edge_registry_entries": len(edge.get("entries", [])),
        "production_components_without_research_provenance": codes["PRODUCTION_COMPONENT_WITHOUT_RESEARCH_PROVENANCE"],
        "current_production_authorization": {"production_authorized_components": decision.get("production_authorized_components", [])},
        "finding_counts": {key: severity[key] for key in ("INFO", "WARNING", "ERROR", "BLOCKING")},
        "findings": [item.as_dict() for item in sorted(findings, key=lambda x: (SEVERITY_ORDER.get(x.severity, 99), x.code, x.subject, x.message))],
        "overall": overall,
    }


def render_text(snapshot: dict[str, Any]) -> str:
    rows = [
        "Research Governance Audit",
        f"Governance version: {snapshot['governance_version']}",
        f"Legacy boundary: {snapshot['legacy_boundary']}", "",
        f"Total research records: {snapshot['total_research_records']}",
        f"Program-governed records: {snapshot['program_governed_records']}",
        f"Legacy retrospective records: {snapshot['legacy_retrospective_records']}",
        f"Preregistered: {snapshot['preregistered']}", f"Post-hoc: {snapshot['post_hoc']}",
        f"Failed: {snapshot['failed']}", f"Stopped: {snapshot['stopped']}",
        f"Shadow-only: {snapshot['shadow_only']}", f"Promoted: {snapshot['promoted']}", "",
        f"Research families: {snapshot['research_families']}", "Family trial counts:",
    ]
    rows.extend([f"  {family}: {count}" for family, count in snapshot["family_trial_counts"].items()] or ["  <none>: 0"])
    rows.extend([
        f"Variants evaluated (known total): {snapshot['variants_evaluated_known_total']}",
        f"Parameter candidates (known total): {snapshot['parameter_candidates_known_total']}",
        f"Result-informed descendants: {snapshot['result_informed_descendant_count']}",
        f"Failed ancestors: {snapshot['failed_ancestor_count']}", "",
        f"Validation exposure events: {snapshot['validation_exposure_events']}",
        f"Consumed sealed datasets: {snapshot['consumed_sealed_datasets']}",
        f"Researcher-exposed historical slices: {snapshot['researcher_exposed_historical_slices']}", "",
        f"Missing primary metrics: {snapshot['missing_primary_metrics']}",
        f"Missing stopping rules: {snapshot['missing_stopping_rules']}",
        f"Missing lineage: {snapshot['missing_lineage']}", f"Invalid lineage: {snapshot['invalid_lineage']}",
        f"Circular lineage: {snapshot['circular_lineage']}", f"Unregistered variants: {snapshot['unregistered_variants']}",
        f"Potential family duplication: {len(snapshot['potential_family_duplication'])}",
        f"Research governance debt: {snapshot['research_governance_debt']}",
        f"Edge Registry entries: {snapshot['edge_registry_entries']}",
        f"Production components without research provenance: {snapshot['production_components_without_research_provenance']}",
        f"Current production authorization: {json.dumps(snapshot['current_production_authorization'], sort_keys=True)}", "", "Findings:",
    ])
    rows.extend([
        f"  [{item['severity']}] {item['code']} {item['subject']}: {item['message']}".rstrip()
        for item in snapshot["findings"]
    ] or ["  <none>"])
    rows.extend(["", f"Overall: {snapshot['overall']}"])
    return "\n".join(rows) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit deterministic Program-Level Epistemic Governance v1 audit")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    snapshot = audit_snapshot(args.root)
    print(json.dumps(snapshot, indent=2, sort_keys=True) if args.as_json else render_text(snapshot), end="\n" if args.as_json else "")
    return 1 if snapshot["overall"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
