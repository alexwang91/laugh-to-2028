from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SEVERITY_ORDER = {"INFO": 0, "WARNING": 1, "ERROR": 2, "BLOCKING": 3}
UNKNOWN = {"UNKNOWN", "NOT_HISTORICALLY_RECORDED"}
PROGRAM_REQUIRED = [
    "research_id", "research_family_id", "research_governance_version", "governance_mode",
    "objective_type", "research_domain", "created_at", "created_before_result", "question",
    "hypothesis", "hypothesis_origin", "economic_mechanism", "primary_target", "primary_metric",
    "secondary_metrics", "feature_families", "horizon", "universe", "development_dataset_refs",
    "validation_dataset_refs", "sealed_dataset_refs", "declared_variant_budget",
    "actual_variants_evaluated", "stopping_rule", "success_criteria", "failure_criteria",
    "allowed_followup", "forbidden_followup", "researcher_decisions", "research_process_complexity",
    "lineage_edges", "result_status", "promotion_state", "evidence_refs", "production_relevance",
    "production_authorized", "provenance_status",
]
DOF_REQUIRED = [
    "declared_parameter_candidates", "actual_parameter_candidates_evaluated", "universes_evaluated",
    "horizons_evaluated", "rebalance_variants", "feature_representations",
    "special_cases_introduced", "validation_exposure_event_refs",
]


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    subject: str = ""

    def as_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "code": self.code, "subject": self.subject, "message": self.message}


def repo_root_from_module() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _add(out: list[Finding], severity: str, code: str, message: str, subject: str = "") -> None:
    out.append(Finding(severity, code, message, subject))


def _blank(record: dict[str, Any], key: str) -> bool:
    return key not in record or record[key] is None or record[key] == "" or record[key] == []


def _count(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _cycle_nodes(graph: dict[str, set[str]]) -> set[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    cycle: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            cycle.update(stack[stack.index(node):] if node in stack else [node])
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for parent in sorted(graph.get(node, set())):
            visit(parent, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node, [])
    return cycle


def validate_repo(root: Path | None = None) -> list[Finding]:
    root = Path(root or repo_root_from_module())
    out: list[Finding] = []
    paths = {
        "governance": root / "config/research_governance_v1.json",
        "research": root / "config/research_registry.json",
        "dataset": root / "config/dataset_exposure_registry.json",
        "edge": root / "config/edge_registry.json",
    }
    data: dict[str, Any] = {}
    for name, path in paths.items():
        if not path.exists():
            _add(out, "BLOCKING", "MISSING_REGISTRY", str(path.relative_to(root)), name)
            continue
        try:
            data[name] = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            _add(out, "BLOCKING", "INVALID_JSON", str(exc), name)
    if len(data) != len(paths):
        return sorted(out, key=_finding_key)

    governance, research, dataset, edge = (data[k] for k in ("governance", "research", "dataset", "edge"))
    version = governance.get("research_governance_version")
    boundary = governance.get("legacy_boundary_commit")
    if version != 1:
        _add(out, "BLOCKING", "GOVERNANCE_VERSION", "research_governance_version must equal 1", "governance")
    if any(reg.get("research_governance_version") != version for reg in (research, dataset, edge)):
        _add(out, "BLOCKING", "REGISTRY_VERSION_MISMATCH", "registry governance versions differ", "registries")
    if research.get("legacy_boundary_commit") != boundary:
        _add(out, "BLOCKING", "LEGACY_BOUNDARY_MISMATCH", "Research Registry boundary differs", "research")

    for filename in ("dataset_exposure_registry.schema.json", "edge_registry.schema.json", "research_registry.schema.json"):
        path = root / "research/governance/schemas" / filename
        try:
            schema = load_json(path)
            if schema.get("$id") != filename:
                _add(out, "ERROR", "SCHEMA_ID_MISMATCH", "unexpected $id", filename)
        except (OSError, json.JSONDecodeError) as exc:
            _add(out, "BLOCKING", "INVALID_SCHEMA_JSON", str(exc), filename)

    domains = set(governance.get("research_domains", []))
    objectives = set(governance.get("objective_types", []))
    relations = set(governance.get("lineage_relation_types", []))
    records = research.get("records", [])
    if not isinstance(records, list):
        _add(out, "BLOCKING", "RECORDS_NOT_LIST", "records must be a list", "research")
        records = []
    ids = [r.get("research_id") for r in records if isinstance(r, dict) and isinstance(r.get("research_id"), str)]
    for rid in sorted({x for x in ids if ids.count(x) > 1}):
        _add(out, "BLOCKING", "DUPLICATE_RESEARCH_ID", f"duplicate {rid}", rid)
    id_set = set(ids)
    graph = {rid: set() for rid in id_set}
    dataset_refs: list[tuple[str, str, str]] = []

    for record in records:
        if not isinstance(record, dict):
            _add(out, "BLOCKING", "INVALID_RESEARCH_RECORD", "record must be an object", "research")
            continue
        rid = str(record.get("research_id", "<missing>"))
        mode = record.get("governance_mode")
        if record.get("research_governance_version") != 1:
            _add(out, "BLOCKING", "RECORD_VERSION", "record must use governance version 1", rid)
        if record.get("production_authorized") is not False:
            _add(out, "BLOCKING", "ILLEGAL_RESEARCH_PRODUCTION_AUTHORIZATION", "research cannot confer production authority", rid)
        if mode not in {"RETROSPECTIVE_LEGACY", "PROGRAM_GOVERNED_V1"}:
            _add(out, "BLOCKING", "INVALID_GOVERNANCE_MODE", repr(mode), rid)
        if mode == "PROGRAM_GOVERNED_V1":
            for field in PROGRAM_REQUIRED:
                if _blank(record, field):
                    _add(out, "BLOCKING", "MISSING_PROGRAM_FIELD", field, rid)
            if record.get("created_before_result") is not True:
                _add(out, "BLOCKING", "NOT_CREATED_BEFORE_RESULT", "future formal research must be frozen before results", rid)
            if record.get("objective_type") not in objectives:
                _add(out, "BLOCKING", "INVALID_OBJECTIVE_TYPE", repr(record.get("objective_type")), rid)
            if record.get("research_domain") not in domains:
                _add(out, "BLOCKING", "INVALID_RESEARCH_DOMAIN", repr(record.get("research_domain")), rid)
            for field in ("research_family_id", "question", "hypothesis", "economic_mechanism", "primary_target", "primary_metric", "stopping_rule"):
                if record.get(field) in UNKNOWN:
                    _add(out, "BLOCKING", "UNKNOWN_NOT_ALLOWED_FUTURE", field, rid)
            dof = record.get("research_process_complexity")
            if not isinstance(dof, dict):
                _add(out, "BLOCKING", "MISSING_RESEARCH_PROCESS_COMPLEXITY", "structured DoF record required", rid)
            else:
                for field in DOF_REQUIRED:
                    if field not in dof:
                        _add(out, "BLOCKING", "MISSING_DOF_FIELD", field, rid)
            declared, actual = record.get("declared_variant_budget"), record.get("actual_variants_evaluated")
            if not _count(declared):
                _add(out, "BLOCKING", "INVALID_VARIANT_BUDGET", repr(declared), rid)
            if not _count(actual):
                _add(out, "BLOCKING", "INVALID_ACTUAL_VARIANTS", repr(actual), rid)
            if _count(declared) and _count(actual) and actual > declared:
                _add(out, "BLOCKING", "UNREGISTERED_VARIANTS", f"{actual}>{declared}", rid)
            status = str(record.get("result_status") or "").upper()
            released = bool(record.get("evidence_refs")) or any(token in status for token in ("PASS", "FAIL", "REJECT", "NO_PROMOTION", "SHADOW"))
            if released:
                scorecard = record.get("evidence_scorecard")
                needed = {"temporal_novelty", "statistical_sufficiency", "governance_integrity", "operational_realism"}
                if not isinstance(scorecard, dict) or not needed.issubset(scorecard):
                    _add(out, "BLOCKING", "MISSING_EVIDENCE_SCORECARD", "four evidence dimensions required after result release", rid)
        elif mode == "RETROSPECTIVE_LEGACY" and record.get("provenance_status") == "UNKNOWN":
            _add(out, "WARNING", "LEGACY_PROVENANCE_UNKNOWN", "unrecoverable legacy provenance", rid)

        lineage = record.get("lineage_edges", [])
        if not isinstance(lineage, list):
            _add(out, "BLOCKING", "LINEAGE_NOT_LIST", "lineage_edges must be a list", rid)
            lineage = []
        relation_set: set[str] = set()
        for link in lineage:
            if not isinstance(link, dict):
                _add(out, "BLOCKING", "INVALID_LINEAGE_EDGE", "edge must be an object", rid)
                continue
            relation, parent = link.get("relation"), link.get("ref_research_id")
            relation_set.add(str(relation))
            if relation not in relations:
                _add(out, "BLOCKING", "INVALID_LINEAGE_RELATION", repr(relation), rid)
            if parent not in id_set:
                _add(out, "BLOCKING", "INVALID_LINEAGE_REF", repr(parent), rid)
            elif rid in graph:
                graph[rid].add(parent)
        if {"RESULT_INFORMED", "INDEPENDENT_REPLICATION"}.issubset(relation_set):
            _add(out, "BLOCKING", "FALSE_INDEPENDENCE", "result-informed research cannot claim independent replication", rid)
        for field in ("development_dataset_refs", "validation_dataset_refs", "sealed_dataset_refs"):
            for ref in record.get(field, []) if isinstance(record.get(field, []), list) else []:
                dataset_refs.append((rid, field, ref))

    cycle = _cycle_nodes(graph)
    if cycle:
        _add(out, "BLOCKING", "CIRCULAR_LINEAGE", ",".join(sorted(cycle)), ",".join(sorted(cycle)))

    slices = dataset.get("dataset_slices", []) if isinstance(dataset.get("dataset_slices", []), list) else []
    events = dataset.get("exposure_events", []) if isinstance(dataset.get("exposure_events", []), list) else []
    slice_ids = [s.get("dataset_slice_id") for s in slices if isinstance(s, dict) and isinstance(s.get("dataset_slice_id"), str)]
    if len(slice_ids) != len(set(slice_ids)):
        _add(out, "BLOCKING", "DUPLICATE_DATASET_SLICE_ID", "duplicate dataset slice", "dataset")
    slice_map = {s["dataset_slice_id"]: s for s in slices if isinstance(s, dict) and isinstance(s.get("dataset_slice_id"), str)}
    for rid, field, ref in dataset_refs:
        if ref not in slice_map:
            _add(out, "BLOCKING", "INVALID_DATASET_REF", f"{field}:{ref}", rid)

    exposure_ids: set[str] = set()
    record_map = {r.get("research_id"): r for r in records if isinstance(r, dict)}
    for event in events:
        if not isinstance(event, dict):
            _add(out, "BLOCKING", "INVALID_EXPOSURE_EVENT", "event must be an object", "dataset")
            continue
        eid, rid, sid = event.get("exposure_id"), event.get("research_id"), event.get("dataset_slice_ref")
        if eid in exposure_ids:
            _add(out, "BLOCKING", "DUPLICATE_EXPOSURE_ID", str(eid), str(eid))
        exposure_ids.add(eid)
        if rid not in id_set:
            _add(out, "BLOCKING", "EXPOSURE_UNKNOWN_RESEARCH", repr(rid), str(eid))
        if sid not in slice_map:
            _add(out, "BLOCKING", "EXPOSURE_UNKNOWN_DATASET", repr(sid), str(eid))
        else:
            item = slice_map[sid]
            if item.get("data_budget") == "SEALED" and (item.get("consumed") is not True or item.get("contamination_state") == "DATA_SEALED"):
                _add(out, "BLOCKING", "CONSUMED_SEALED_CLAIMED_PRISTINE", "released sealed slice must be consumed/exposed", str(sid))
        if event.get("release_type") == "UNKNOWN" and record_map.get(rid, {}).get("governance_mode") != "RETROSPECTIVE_LEGACY":
            _add(out, "BLOCKING", "UNKNOWN_RELEASE_TYPE_FUTURE", "UNKNOWN release type is legacy-only", str(eid))
    for sid, item in slice_map.items():
        if item.get("data_budget") == "SEALED" and item.get("consumed") is True and item.get("contamination_state") == "DATA_SEALED":
            _add(out, "BLOCKING", "CONSUMED_SEALED_CLAIMED_PRISTINE", "consumed sealed slice cannot remain pristine", sid)
        if item.get("contamination_state") == "TEMPORALLY_UNSEEN" and item.get("data_budget") != "TEMPORALLY_UNSEEN":
            _add(out, "ERROR", "TEMPORAL_NOVELTY_BUDGET_MISMATCH", "temporally unseen state requires matching budget", sid)

    entries = edge.get("entries", []) if isinstance(edge.get("entries", []), list) else []
    edge_ids: set[str] = set()
    for item in entries:
        if not isinstance(item, dict):
            _add(out, "BLOCKING", "INVALID_EDGE_RECORD", "edge must be an object", "edge")
            continue
        eid = str(item.get("edge_id", "<missing>"))
        if eid in edge_ids:
            _add(out, "BLOCKING", "DUPLICATE_EDGE_ID", eid, eid)
        edge_ids.add(eid)
        if item.get("production_authorized") is not False:
            _add(out, "BLOCKING", "ILLEGAL_EDGE_PRODUCTION_AUTHORIZATION", "edge registry cannot authorize production", eid)
        if item.get("status") == "ADMITTED" and item.get("incremental_evidence_status") != "PASS":
            _add(out, "BLOCKING", "EDGE_ADMISSION_WITHOUT_INCREMENTAL_PASS", "ADMITTED requires incremental PASS", eid)
        if item.get("status") == "ADMITTED" and not item.get("evidence_refs"):
            _add(out, "BLOCKING", "EDGE_ADMISSION_WITHOUT_EVIDENCE", "ADMITTED requires evidence refs", eid)

    for debt in research.get("research_governance_debt", []) if isinstance(research.get("research_governance_debt", []), list) else []:
        if isinstance(debt, dict) and debt.get("status") != "RESOLVED":
            _add(out, "WARNING", "RESEARCH_GOVERNANCE_DEBT", str(debt.get("description", "open debt")), str(debt.get("debt_id", "")))

    decision_path = root / "config/decision_registry.json"
    if decision_path.exists():
        decision = load_json(decision_path)
        provenance = {ref for record in records if isinstance(record, dict) for ref in record.get("decision_refs", []) if isinstance(record.get("decision_refs", []), list)}
        for component in decision.get("production_authorized_components", []) if isinstance(decision.get("production_authorized_components", []), list) else []:
            if component not in provenance:
                _add(out, "BLOCKING", "PRODUCTION_COMPONENT_WITHOUT_RESEARCH_PROVENANCE", repr(component), str(component))
    return sorted(out, key=_finding_key)


def _finding_key(item: Finding) -> tuple[int, str, str, str]:
    return (SEVERITY_ORDER.get(item.severity, 99), item.code, item.subject, item.message)


def has_failures(findings: Iterable[Finding]) -> bool:
    return any(item.severity in {"ERROR", "BLOCKING"} for item in findings)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Program-Level Epistemic Governance v1 registries")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    findings = validate_repo(args.root)
    if args.as_json:
        print(json.dumps([item.as_dict() for item in findings], indent=2, sort_keys=True))
    else:
        for item in findings:
            print(f"[{item.severity}] {item.code} {item.subject}: {item.message}".rstrip())
        print("Research governance validation: " + ("FAIL" if has_failures(findings) else "WARNING" if findings else "PASS"))
    return 1 if has_failures(findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
