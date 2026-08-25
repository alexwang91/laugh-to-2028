from __future__ import annotations

"""Read-only auditor for Phase-6 future-only observation evidence.

This tool never creates observation credit. It inventories existing GitHub Actions
runs/artifacts and verifies the already-frozen evidence/receipt bindings so a
later repository accounting change can index only evidence that already exists.
"""

import argparse
import io
import json
import os
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com"
FIRST_ELIGIBLE_DECISION = "2026-08-10T00:00:00Z"
WORKFLOW_FILE = "research-governance.yml"


class AuditError(RuntimeError):
    pass


def _iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _norm_digest(value: object) -> str:
    text = str(value or "")
    return text.split(":", 1)[1] if text.startswith("sha256:") else text


def _request_json(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "phase6-observation-closeout-audit-v1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise AuditError(f"GitHub response must be object: {url}")
    return payload


def _request_bytes(url: str, token: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "phase6-observation-closeout-audit-v1",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _read_json_from_zip(raw_zip: bytes, basename: str) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as archive:
        matches = [name for name in archive.namelist() if Path(name).name == basename]
        if len(matches) != 1:
            raise AuditError(f"expected exactly one {basename}, found {len(matches)}")
        value = json.loads(archive.read(matches[0]).decode("utf-8"))
    if not isinstance(value, dict):
        raise AuditError(f"{basename} must contain a JSON object")
    return value


def _list_runs(repo: str, token: str) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    page = 1
    first = _parse_iso(FIRST_ELIGIBLE_DECISION)
    while True:
        query = urllib.parse.urlencode({"per_page": 100, "page": page})
        payload = _request_json(
            f"{API_ROOT}/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/runs?{query}", token
        )
        rows = payload.get("workflow_runs", [])
        if not isinstance(rows, list):
            raise AuditError("workflow_runs must be a list")
        if not rows:
            break
        stop = False
        for row in rows:
            if not isinstance(row, dict):
                continue
            created = _parse_iso(str(row["created_at"]))
            if created < first - timedelta(days=1):
                stop = True
                continue
            if row.get("event") in {"schedule", "workflow_dispatch"}:
                runs.append(row)
        if stop or len(rows) < 100:
            break
        page += 1
        if page > 10:
            raise AuditError("unexpected workflow-run pagination >10 pages")
    return runs


def _artifacts(repo: str, run_id: int, token: str) -> list[dict[str, Any]]:
    payload = _request_json(
        f"{API_ROOT}/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100", token
    )
    rows = payload.get("artifacts", [])
    if not isinstance(rows, list):
        raise AuditError("artifacts must be a list")
    return [row for row in rows if isinstance(row, dict)]


def _download_artifact_json(artifact: dict[str, Any], basename: str, token: str) -> dict[str, Any]:
    url = str(artifact.get("archive_download_url") or "")
    if not url:
        raise AuditError(f"artifact {artifact.get('id')} missing archive_download_url")
    return _read_json_from_zip(_request_bytes(url, token), basename)


def _verify_pair(
    *, repo: str, run: dict[str, Any], evidence: dict[str, Any], receipt: dict[str, Any], token: str
) -> dict[str, Any]:
    errors: list[str] = []
    run_id = int(run["id"])
    run_attempt = int(run.get("run_attempt") or 0)
    event_name = str(run.get("event"))
    conclusion = run.get("conclusion")

    if run_attempt != 1:
        errors.append("RUN_ATTEMPT_NOT_ONE_RERUN_INELIGIBLE")
    if conclusion != "success":
        errors.append(f"RUN_NOT_SUCCESS:{conclusion}")
    if evidence.get("expired") is True:
        errors.append("EVIDENCE_ARTIFACT_EXPIRED")
    if receipt.get("expired") is True:
        errors.append("RECEIPT_ARTIFACT_EXPIRED")

    try:
        metadata = _download_artifact_json(evidence, "evidence_metadata.json", token)
        provenance = _download_artifact_json(evidence, "input_provenance_manifest.json", token)
        receipt_json = _download_artifact_json(receipt, "receipt.json", token)
    except Exception as exc:  # audit must fail closed but preserve run inventory
        return {
            "run_id": run_id,
            "run_attempt": run_attempt,
            "event_name": event_name,
            "conclusion": conclusion,
            "evidence_artifact_id": evidence.get("id"),
            "receipt_artifact_id": receipt.get("id"),
            "creditable_schedule": False,
            "creditable_emergency_drill": False,
            "errors": errors + [f"ARTIFACT_PARSE_ERROR:{type(exc).__name__}:{exc}"],
        }

    expected_identity = {
        "github_run_id": str(run_id),
        "github_run_attempt": str(run_attempt),
        "workflow_sha": str(run.get("head_sha")),
    }
    for key, expected in expected_identity.items():
        if str(metadata.get(key)) != expected:
            errors.append(f"METADATA_{key.upper()}_MISMATCH")
        if str(receipt_json.get(key)) != expected:
            errors.append(f"RECEIPT_{key.upper()}_MISMATCH")

    for key in (
        "decision_timestamp",
        "observed_at",
        "shadow_record_digest",
        "input_provenance_digest",
        "evidence_object_digest",
    ):
        if metadata.get(key) != receipt_json.get(key):
            errors.append(f"RECEIPT_BINDING_MISMATCH:{key}")

    if str(receipt_json.get("evidence_artifact_id")) != str(evidence.get("id")):
        errors.append("RECEIPT_EVIDENCE_ARTIFACT_ID_MISMATCH")
    if _norm_digest(receipt_json.get("evidence_artifact_digest")) != _norm_digest(evidence.get("digest")):
        errors.append("RECEIPT_EVIDENCE_ARTIFACT_DIGEST_MISMATCH")
    if metadata.get("event_name") != event_name:
        errors.append("METADATA_EVENT_NAME_MISMATCH")

    if any(metadata.get(key) is True for key in (
        "production_authorized", "signature_authorized", "order_submission_authorized"
    )):
        errors.append("AUTHORITY_LEAK_IN_METADATA")
    if receipt_json.get("production_authorized") is True:
        errors.append("AUTHORITY_LEAK_IN_RECEIPT")
    if provenance.get("secret_material_present") is not False:
        errors.append("SECRET_MATERIAL_FLAG_NOT_FALSE")
    if provenance.get("authorization_headers_used_for_market_or_account_reads") is not False:
        errors.append("AUTH_HEADER_USED")

    parity = provenance.get("target_reference_parity")
    if not isinstance(parity, dict) or parity.get("passed") is not True:
        errors.append("TARGET_REFERENCE_PARITY_NOT_PASS")
    if metadata.get("shadow_status") != "SHADOW_COMPUTED_NO_AUTHORITY":
        errors.append("SHADOW_STATUS_NOT_ZERO_AUTHORITY")
    if metadata.get("shadow_alerts") != []:
        errors.append("SHADOW_ALERTS_NONEMPTY")

    schedule_candidate = metadata.get("scheduled_decision_credit_candidate") is True
    drill_candidate = metadata.get("emergency_drill_candidate") is True
    if bool(receipt_json.get("scheduled_decision_credit_candidate")) != schedule_candidate:
        errors.append("RECEIPT_SCHEDULE_CANDIDATE_MISMATCH")
    if bool(receipt_json.get("emergency_drill_candidate")) != drill_candidate:
        errors.append("RECEIPT_DRILL_CANDIDATE_MISMATCH")

    creditable_schedule = event_name == "schedule" and schedule_candidate and not errors
    creditable_drill = event_name == "workflow_dispatch" and drill_candidate and not errors
    return {
        "run_id": run_id,
        "run_attempt": run_attempt,
        "event_name": event_name,
        "conclusion": conclusion,
        "head_sha": run.get("head_sha"),
        "decision_timestamp": metadata.get("decision_timestamp"),
        "observed_at": metadata.get("observed_at"),
        "scheduled_decision_credit_candidate": schedule_candidate,
        "emergency_drill_candidate": drill_candidate,
        "creditable_schedule": creditable_schedule,
        "creditable_emergency_drill": creditable_drill,
        "evidence_artifact": {
            "id": str(evidence.get("id")),
            "name": evidence.get("name"),
            "digest": evidence.get("digest"),
            "created_at": evidence.get("created_at"),
            "expires_at": evidence.get("expires_at"),
            "expired": evidence.get("expired"),
        },
        "receipt_artifact": {
            "id": str(receipt.get("id")),
            "name": receipt.get("name"),
            "digest": receipt.get("digest"),
            "created_at": receipt.get("created_at"),
            "expires_at": receipt.get("expires_at"),
            "expired": receipt.get("expired"),
        },
        "receipt_binding": {
            key: receipt_json.get(key)
            for key in (
                "github_run_id", "github_run_attempt", "workflow_sha", "decision_timestamp",
                "observed_at", "scheduled_decision_credit_candidate", "emergency_drill_candidate",
                "evidence_artifact_id", "evidence_artifact_digest", "evidence_object_digest",
                "input_provenance_digest", "shadow_record_digest",
            )
        },
        "observation_checks": {
            "shadow_status": metadata.get("shadow_status"),
            "shadow_alerts": metadata.get("shadow_alerts"),
            "target_reference_parity_passed": parity.get("passed") if isinstance(parity, dict) else None,
            "target_reference_gross_abs_difference": parity.get("gross_abs_difference") if isinstance(parity, dict) else None,
            "target_reference_max_weight_abs_difference": parity.get("max_weight_abs_difference") if isinstance(parity, dict) else None,
            "authorization_headers_used_for_market_or_account_reads": provenance.get("authorization_headers_used_for_market_or_account_reads"),
            "secret_material_present": provenance.get("secret_material_present"),
            "production_authorized": metadata.get("production_authorized"),
            "signature_authorized": metadata.get("signature_authorized"),
            "order_submission_authorized": metadata.get("order_submission_authorized"),
        },
        "errors": errors,
    }


def audit(repo: str, token: str, as_of: datetime) -> dict[str, Any]:
    runs = _list_runs(repo, token)
    records: list[dict[str, Any]] = []
    run_inventory: list[dict[str, Any]] = []

    for run in sorted(runs, key=lambda row: (str(row.get("created_at")), int(row.get("id", 0)))):
        run_id = int(run["id"])
        artifacts = _artifacts(repo, run_id, token)
        evidence = [a for a in artifacts if str(a.get("name", "")).startswith("phase6-evidence-")]
        receipts = [a for a in artifacts if str(a.get("name", "")).startswith("phase6-receipt-")]
        run_inventory.append({
            "run_id": run_id,
            "run_attempt": run.get("run_attempt"),
            "event_name": run.get("event"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "head_sha": run.get("head_sha"),
            "evidence_artifact_count": len(evidence),
            "receipt_artifact_count": len(receipts),
        })
        if len(evidence) != 1 or len(receipts) != 1:
            records.append({
                "run_id": run_id,
                "run_attempt": run.get("run_attempt"),
                "event_name": run.get("event"),
                "conclusion": run.get("conclusion"),
                "creditable_schedule": False,
                "creditable_emergency_drill": False,
                "errors": [f"ARTIFACT_PAIR_COUNT:{len(evidence)}:{len(receipts)}"],
            })
            continue
        records.append(_verify_pair(repo=repo, run=run, evidence=evidence[0], receipt=receipts[0], token=token))

    schedule = [row for row in records if row.get("creditable_schedule") is True]
    drills = [row for row in records if row.get("creditable_emergency_drill") is True]
    decision_timestamps = [str(row["decision_timestamp"]) for row in schedule]
    duplicate_decisions = sorted({value for value in decision_timestamps if decision_timestamps.count(value) > 1})
    unique_schedule = {str(row["decision_timestamp"]): row for row in schedule}

    first_date = _parse_iso(FIRST_ELIGIBLE_DECISION).date()
    as_of_date = as_of.astimezone(timezone.utc).date()
    expected_dates: list[str] = []
    cursor = first_date
    while cursor <= as_of_date:
        expected_dates.append(cursor.isoformat())
        cursor += timedelta(days=1)
    credited_dates = sorted({str(row["decision_timestamp"])[:10] for row in schedule})
    missing_expected_dates = [value for value in expected_dates if value not in credited_dates]

    schedule_run_failures = [
        row for row in records
        if row.get("event_name") == "schedule" and row.get("creditable_schedule") is not True
    ]
    elapsed_days = (as_of_date - first_date).days
    requirements = {
        "elapsed_days": elapsed_days,
        "minimum_elapsed_calendar_days": 14,
        "elapsed_requirement_met": elapsed_days >= 14,
        "genuine_scheduled_decisions": len(unique_schedule),
        "minimum_scheduled_decisions": 10,
        "scheduled_decision_requirement_met": len(unique_schedule) >= 10 and not duplicate_decisions,
        "emergency_drills": len(drills),
        "minimum_emergency_drills": 1,
        "emergency_drill_requirement_met": len(drills) >= 1,
        "schedule_run_failures": len(schedule_run_failures),
        "missing_expected_schedule_dates": missing_expected_dates,
        "duplicate_decision_timestamps": duplicate_decisions,
    }
    requirements["phase6_acceptance_preliminary"] = bool(
        requirements["elapsed_requirement_met"]
        and requirements["scheduled_decision_requirement_met"]
        and requirements["emergency_drill_requirement_met"]
        and requirements["schedule_run_failures"] == 0
        and not requirements["missing_expected_schedule_dates"]
    )

    return {
        "schema_version": 1,
        "audit_id": "PHASE6-LIVE-OBSERVATION-CLOSEOUT-AUDIT-V1",
        "status": "READ_ONLY_EXISTING_EVIDENCE_AUDIT",
        "repository": repo,
        "workflow": WORKFLOW_FILE,
        "first_eligible_decision": FIRST_ELIGIBLE_DECISION,
        "audited_at": _iso_z(as_of),
        "recording_creates_credit": False,
        "historical_backfill_authorized": False,
        "historical_replay_credit_authorized": False,
        "manual_dispatch_scheduled_decision_credit_authorized": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "requirements": requirements,
        "creditable_schedule_records": schedule,
        "creditable_emergency_drill_records": drills,
        "all_candidate_records": records,
        "run_inventory": run_inventory,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.repo or not args.token:
        raise SystemExit("--repo and --token/GITHUB_TOKEN are required")
    result = audit(args.repo, args.token, datetime.now(timezone.utc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
