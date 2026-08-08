from __future__ import annotations

"""Validation for the frozen Phase-6 live evidence storage/provenance contract."""

import json
from pathlib import Path
from typing import Any, Mapping

from .validate import repo_root_from_module


CONTRACT_RELATIVE_PATH = Path("research/governance/phase6_live_evidence_contract.json")
CONTRACT_ID = "PHASE6-LIVE-EVIDENCE-BACKEND-V1"
BACKEND_ID = "GITHUB_ACTIONS_ARTIFACT_V4"
RETENTION_DAYS = 90


class Phase6LiveEvidenceError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase6LiveEvidenceError(f"{path} must contain a JSON object")
    return value


def validate_evidence_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if int(contract.get("schema_version", -1)) != 1:
        raise Phase6LiveEvidenceError("unsupported Phase-6 live-evidence schema")
    if contract.get("contract_id") != CONTRACT_ID:
        raise Phase6LiveEvidenceError("unexpected Phase-6 live-evidence contract id")
    if contract.get("status") != "FROZEN_BACKEND_NOT_COLLECTING":
        raise Phase6LiveEvidenceError("evidence backend must remain frozen-not-collecting in this change")
    if contract.get("production_authorized") is not False:
        raise Phase6LiveEvidenceError("evidence storage cannot confer production authority")

    backend = contract.get("backend", {})
    if backend.get("provider") != BACKEND_ID:
        raise Phase6LiveEvidenceError("unexpected evidence backend")
    if backend.get("retention_days") != RETENTION_DAYS:
        raise Phase6LiveEvidenceError("Phase-6 evidence retention must remain exactly 90 days")
    if backend.get("overwrite") is not False:
        raise Phase6LiveEvidenceError("evidence artifacts must be create-only / overwrite=false")
    if backend.get("if_no_files_found") != "error":
        raise Phase6LiveEvidenceError("empty evidence upload must fail closed")
    required_outputs = {"artifact-id", "artifact-url", "artifact-digest"}
    if set(backend.get("required_upload_outputs", [])) != required_outputs:
        raise Phase6LiveEvidenceError("immutable artifact output identity drift detected")

    bundle = contract.get("evidence_bundle", {})
    required_categories = {
        "RAW_CANONICAL_DAILY_MARKET_INPUTS",
        "RAW_READ_ONLY_ACCOUNT_INPUTS",
        "RAW_READ_ONLY_ROUTE_INPUTS",
        "INPUT_PROVENANCE_MANIFEST",
        "SHADOW_RECORD",
    }
    if set(bundle.get("required_categories", [])) != required_categories:
        raise Phase6LiveEvidenceError("evidence bundle category set drift detected")
    for field in (
        "upload_before_credit",
        "raw_bytes_preserved_before_parse",
        "input_manifest_sha256_required",
        "shadow_record_sha256_required",
        "secret_material_forbidden",
        "authorization_headers_forbidden",
    ):
        if bundle.get(field) is not True:
            raise Phase6LiveEvidenceError(f"evidence bundle must keep {field}=true")

    receipt = contract.get("receipt", {})
    if receipt.get("backend_id") != BACKEND_ID:
        raise Phase6LiveEvidenceError("receipt backend id drift detected")
    if receipt.get("retention_days") != RETENTION_DAYS:
        raise Phase6LiveEvidenceError("receipt retention must remain exactly 90 days")
    if receipt.get("overwrite") is not False:
        raise Phase6LiveEvidenceError("receipt artifact must be create-only")
    for field in ("create_after_evidence_artifact", "upload_as_separate_artifact_before_credit"):
        if receipt.get(field) is not True:
            raise Phase6LiveEvidenceError(f"receipt must keep {field}=true")
    required_receipt_fields = {
        "github_run_id",
        "github_run_attempt",
        "workflow_sha",
        "decision_timestamp",
        "observed_at",
        "shadow_record_digest",
        "input_provenance_digest",
        "evidence_object_digest",
        "evidence_artifact_id",
        "evidence_artifact_url",
        "backend_id",
        "retention_days",
    }
    if set(receipt.get("required_fields", [])) != required_receipt_fields:
        raise Phase6LiveEvidenceError("receipt identity field set drift detected")

    credit = contract.get("credit_rules", {})
    required_false = (
        "ephemeral_runner_files_create_credit",
        "step_summary_creates_credit",
        "logs_create_credit",
        "evidence_artifact_without_receipt_creates_credit",
        "expired_artifact_before_acceptance_review_creates_credit",
        "artifact_upload_failure_creates_credit",
        "receipt_upload_failure_creates_credit",
    )
    for field in required_false:
        if credit.get(field) is not False:
            raise Phase6LiveEvidenceError(f"credit rule must keep {field}=false")
    for field in (
        "credit_only_after_evidence_and_receipt_uploads_succeed",
        "acceptance_review_must_complete_before_required_artifact_expiry",
    ):
        if credit.get(field) is not True:
            raise Phase6LiveEvidenceError(f"credit rule must keep {field}=true")

    precedent = contract.get("provenance_precedent", {})
    if precedent.get("research_id") != "STABLECOIN-LIQUIDITY-0001":
        raise Phase6LiveEvidenceError("unexpected provenance precedent")
    if int(precedent.get("workflow_run_id", -1)) != 31264048473:
        raise Phase6LiveEvidenceError("Stablecoin provenance precedent run drift detected")
    if precedent.get("precedent_only_not_shared_evidence") is not True:
        raise Phase6LiveEvidenceError("precedent must not be treated as Phase-6 evidence")

    non_actions = set(contract.get("explicit_non_actions", []))
    required_non_actions = {
        "NO_ACCOUNT_IDENTITY_SELECTION",
        "NO_POSITION_OR_EQUITY_VALUATION_CHANGE",
        "NO_SCHEDULE_ARM",
        "NO_ELAPSED_EVIDENCE_CREDIT",
        "NO_SIGNING",
        "NO_ORDER_SUBMISSION",
        "NO_PRODUCTION_AUTHORIZATION",
    }
    if non_actions != required_non_actions:
        raise Phase6LiveEvidenceError("explicit non-action boundary drift detected")

    return {
        "contract_id": CONTRACT_ID,
        "status": contract["status"],
        "backend": BACKEND_ID,
        "retention_days": RETENTION_DAYS,
        "overwrite": False,
        "credit_active": False,
        "production_authorized": False,
    }


def evidence_snapshot(root: Path | None = None) -> dict[str, Any]:
    repo_root = Path(root or repo_root_from_module())
    return validate_evidence_contract(_load_json(repo_root / CONTRACT_RELATIVE_PATH))


def main() -> int:
    print(json.dumps(evidence_snapshot(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
