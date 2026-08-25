from __future__ import annotations

"""Read-only audit of already-persisted Phase-6 live-shadow evidence.

The audit never creates observation credit. It verifies the durable evidence +
separate receipt pair produced by the Phase-6 observation job. A failure in an
unrelated job of the same workflow does not erase a successfully persisted
Phase-6 observation; conversely a workflow rerun cannot manufacture a new
scheduled decision. Only attempt-1 Phase-6 observation evidence is eligible.
"""

import argparse
import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com"
FIRST_ELIGIBLE_DECISION = "2026-08-10T00:00:00Z"
WORKFLOW_FILE = "research-governance.yml"
PHASE6_JOB_NAME = "phase6-live-observation"


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
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "phase6-observation-closeout-audit-v1",
        },
    )
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        if exc.code not in (301, 302, 303, 307, 308):
            raise
        location = exc.headers.get("Location")
        if not location:
            raise AuditError("artifact download redirect missing Location") from exc
    redirected = urllib.request.Request(
        location, headers={"User-Agent": "phase6-observation-closeout-audit-v1"}
    )
    with urllib.request.urlopen(redirected, timeout=60) as response:
        return response.read()


def _json_from_artifact(artifact: dict[str, Any], basename: str, token: str) -> dict[str, Any]:
    url = str(artifact.get("archive_download_url") or "")
    if not url:
        raise AuditError(f"artifact {artifact.get('id')} has no download URL")
    raw = _request_bytes(url, token)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        matches = [name for name in archive.namelist() if Path(name).name == basename]
        if len(matches) != 1:
            raise AuditError(f"artifact {artifact.get('id')} expected one {basename}, found {len(matches)}")
        value = json.loads(archive.read(matches[0]).decode("utf-8"))
    if not isinstance(value, dict):
        raise AuditError(f"{basename} must be a JSON object")
    return value


def _list_runs(repo: str, token: str) -> list[dict[str, Any]]:
    first = _parse_iso(FIRST_ELIGIBLE_DECISION)
    rows_out: list[dict[str, Any]] = []
    for event_name in ("schedule", "workflow_dispatch"):
        page = 1
        while True:
            query = urllib.parse.urlencode({"event": event_name, "per_page": 100, "page": page})
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
                rows_out.append(row)
            if stop or len(rows) < 100:
                break
            page += 1
            if page > 10:
                raise AuditError(f"unexpected {event_name} pagination >10 pages")
    return rows_out


def _artifacts(repo: str, run_id: int, token: str) -> list[dict[str, Any]]:
    payload = _request_json(
        f"{API_ROOT}/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100", token
    )
    rows = payload.get("artifacts", [])
    if not isinstance(rows, list):
        raise AuditError("artifacts must be a list")
    return [row for row in rows if isinstance(row, dict)]


def _phase6_attempt_job(repo: str, run_id: int, attempt: int, token: str) -> dict[str, Any] | None:
    payload = _request_json(
        f"{API_ROOT}/repos/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100", token
    )
    rows = payload.get("jobs", [])
    if not isinstance(rows, list):
        raise AuditError("jobs must be a list")
    matches = [row for row in rows if isinstance(row, dict) and row.get("name") == PHASE6_JOB_NAME]
    if len(matches) != 1:
        return None
    return matches[0]


def _verify_pair(
    *,
    repo: str,
    run: dict[str, Any],
    evidence: dict[str, Any],
    receipt: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    errors: list[str] = []
    run_id = int(run["id"])
    event_name = str(run.get("event"))

    try:
        metadata = _json_from_artifact(evidence, "evidence_metadata.json", token)
        provenance = _json_from_artifact(evidence, "input_provenance_manifest.json", token)
        shadow = _json_from_artifact(evidence, "shadow_record.json", token)
        receipt_json = _json_from_artifact(receipt, "receipt.json", token)
    except Exception as exc:
        return {
            "run_id": run_id,
            "event_name": event_name,
            "creditable_schedule": False,
            "creditable_emergency_drill": False,
            "errors": [f"ARTIFACT_PARSE_ERROR:{type(exc).__name__}:{exc}"],
        }

    artifact_attempt_text = str(metadata.get("github_run_attempt") or "")
    try:
        artifact_attempt = int(artifact_attempt_text)
    except ValueError:
        artifact_attempt = -1
        errors.append("INVALID_ARTIFACT_RUN_ATTEMPT")
    if artifact_attempt != 1:
        errors.append("RERUN_EVIDENCE_INELIGIBLE_FOR_NEW_DECISION_CREDIT")

    try:
        job = _phase6_attempt_job(repo, run_id, artifact_attempt, token) if artifact_attempt > 0 else None
    except Exception as exc:
        job = None
        errors.append(f"PHASE6_JOB_LOOKUP_ERROR:{type(exc).__name__}:{exc}")
    if job is None:
        errors.append("PHASE6_OBSERVATION_JOB_NOT_UNIQUE")
    elif job.get("conclusion") != "success":
        errors.append(f"PHASE6_OBSERVATION_JOB_NOT_SUCCESS:{job.get('conclusion')}")

    if evidence.get("expired") is True:
        errors.append("EVIDENCE_ARTIFACT_EXPIRED")
    if receipt.get("expired") is True:
        errors.append("RECEIPT_ARTIFACT_EXPIRED")

    expected_identity = {
        "github_run_id": str(run_id),
        "github_run_attempt": "1",
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

    parity = provenance.get("target_reference_parity")
    if not isinstance(parity, dict) or parity.get("passed") is not True:
        errors.append("TARGET_REFERENCE_PARITY_NOT_PASS")
    if metadata.get("shadow_status") != "SHADOW_COMPUTED_NO_AUTHORITY":
        errors.append("SHADOW_STATUS_NOT_ZERO_AUTHORITY")
    alerts = shadow.get("alerts")
    if alerts != []:
        errors.append("SHADOW_ALERTS_NONEMPTY")
    offline_drift = shadow.get("offline_reference_l1_drift")
    try:
        offline_drift_value = float(offline_drift)
    except (TypeError, ValueError):
        offline_drift_value = float("nan")
        errors.append("OFFLINE_REFERENCE_DRIFT_INVALID")
    if offline_drift_value != 0.0:
        errors.append("OFFLINE_REFERENCE_DRIFT_NONZERO")

    if provenance.get("secret_material_present") is not False:
        errors.append("SECRET_MATERIAL_FLAG_NOT_FALSE")
    if provenance.get("authorization_headers_used_for_market_or_account_reads") is not False:
        errors.append("AUTH_HEADER_USED")
    for field in ("production_authorized", "signature_authorized", "order_submission_authorized"):
        if metadata.get(field) is not False:
            errors.append(f"AUTHORITY_LEAK:{field}")

    schedule_candidate = metadata.get("scheduled_decision_credit_candidate") is True
    drill_candidate = metadata.get("emergency_drill_candidate") is True
    if bool(receipt_json.get("scheduled_decision_credit_candidate")) != schedule_candidate:
        errors.append("RECEIPT_SCHEDULE_CANDIDATE_MISMATCH")
    if bool(receipt_json.get("emergency_drill_candidate")) != drill_candidate:
        errors.append("RECEIPT_DRILL_CANDIDATE_MISMATCH")
    if event_name == "workflow_dispatch" and drill_candidate and shadow.get("emergency_hypothetical_action") != "FLATTEN":
        errors.append("EMERGENCY_DRILL_DID_NOT_COMPUTE_FLATTEN")

    creditable_schedule = event_name == "schedule" and schedule_candidate and not errors
    creditable_drill = event_name == "workflow_dispatch" and drill_candidate and not errors
    return {
        "run_id": run_id,
        "github_run_attempt": "1",
        "latest_run_attempt_seen": run.get("run_attempt"),
        "overall_workflow_conclusion": run.get("conclusion"),
        "phase6_observation_job_conclusion": job.get("conclusion") if isinstance(job, dict) else None,
        "event_name": event_name,
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
            "shadow_alerts": alerts,
            "target_reference_parity_passed": parity.get("passed") if isinstance(parity, dict) else None,
            "target_reference_gross_abs_difference": parity.get("gross_abs_difference") if isinstance(parity, dict) else None,
            "target_reference_max_weight_abs_difference": parity.get("max_weight_abs_difference") if isinstance(parity, dict) else None,
            "offline_reference_l1_drift": offline_drift_value,
            "critical_reconciliation_errors_observed": 0 if metadata.get("shadow_status") == "SHADOW_COMPUTED_NO_AUTHORITY" else 1,
            "unexplained_target_drift_observed": 0 if offline_drift_value == 0.0 and alerts == [] else 1,
            "schedule_failure_observed": 0 if "DAILY_SCHEDULE_DRIFT" not in (alerts or []) else 1,
            "authorization_headers_used_for_market_or_account_reads": provenance.get("authorization_headers_used_for_market_or_account_reads"),
            "secret_material_present": provenance.get("secret_material_present"),
            "production_authorized": metadata.get("production_authorized"),
            "signature_authorized": metadata.get("signature_authorized"),
            "order_submission_authorized": metadata.get("order_submission_authorized"),
        },
        "errors": errors,
    }


def _select_attempt1_pair(run_id: int, artifacts: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    suffix = f"-{run_id}-1"
    evidence = [
        row for row in artifacts
        if str(row.get("name", "")).startswith("phase6-evidence-") and str(row.get("name", "")).endswith(suffix)
    ]
    receipt = [
        row for row in artifacts
        if str(row.get("name", "")).startswith("phase6-receipt-") and str(row.get("name", "")).endswith(suffix)
    ]
    return (evidence[0] if len(evidence) == 1 else None, receipt[0] if len(receipt) == 1 else None)


def audit(repo: str, token: str, as_of: datetime) -> dict[str, Any]:
    runs = _list_runs(repo, token)
    records: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []

    for run in sorted(runs, key=lambda row: (str(row.get("created_at")), int(row.get("id", 0)))):
        run_id = int(run["id"])
        artifacts = _artifacts(repo, run_id, token)
        evidence, receipt = _select_attempt1_pair(run_id, artifacts)
        inventory.append({
            "run_id": run_id,
            "latest_run_attempt_seen": run.get("run_attempt"),
            "event_name": run.get("event"),
            "overall_workflow_conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "head_sha": run.get("head_sha"),
            "attempt1_evidence_found": evidence is not None,
            "attempt1_receipt_found": receipt is not None,
        })
        if evidence is None or receipt is None:
            records.append({
                "run_id": run_id,
                "event_name": run.get("event"),
                "creditable_schedule": False,
                "creditable_emergency_drill": False,
                "errors": ["ATTEMPT1_EVIDENCE_RECEIPT_PAIR_MISSING_OR_AMBIGUOUS"],
            })
            continue
        records.append(_verify_pair(repo=repo, run=run, evidence=evidence, receipt=receipt, token=token))

    schedules = [row for row in records if row.get("creditable_schedule") is True]
    drills = [row for row in records if row.get("creditable_emergency_drill") is True]
    decision_values = [str(row["decision_timestamp"]) for row in schedules]
    duplicates = sorted({value for value in decision_values if decision_values.count(value) > 1})
    unique_schedules = {str(row["decision_timestamp"]): row for row in schedules}

    first_date = _parse_iso(FIRST_ELIGIBLE_DECISION).date()
    as_of_date = as_of.astimezone(timezone.utc).date()
    expected_dates: list[str] = []
    cursor = first_date
    while cursor <= as_of_date:
        expected_dates.append(cursor.isoformat())
        cursor += timedelta(days=1)
    credited_dates = sorted({str(row["decision_timestamp"])[:10] for row in schedules})
    missing_dates = [value for value in expected_dates if value not in credited_dates]
    schedule_failures = [
        row for row in records
        if row.get("event_name") == "schedule" and row.get("creditable_schedule") is not True
    ]
    rec_errors = sum(int(row.get("observation_checks", {}).get("critical_reconciliation_errors_observed", 0)) for row in schedules)
    drift_errors = sum(int(row.get("observation_checks", {}).get("unexplained_target_drift_observed", 0)) for row in schedules)
    observed_schedule_failures = sum(int(row.get("observation_checks", {}).get("schedule_failure_observed", 0)) for row in schedules)
    total_schedule_failures = len(schedule_failures) + observed_schedule_failures
    elapsed_days = (as_of_date - first_date).days

    requirements = {
        "elapsed_days": elapsed_days,
        "minimum_elapsed_calendar_days": 14,
        "elapsed_requirement_met": elapsed_days >= 14,
        "genuine_scheduled_decisions": len(unique_schedules),
        "minimum_scheduled_decisions": 10,
        "scheduled_decision_requirement_met": len(unique_schedules) >= 10 and not duplicates,
        "emergency_drills": len(drills),
        "minimum_emergency_drills": 1,
        "emergency_drill_requirement_met": len(drills) >= 1,
        "critical_reconciliation_errors_observed": rec_errors,
        "unexplained_target_drift_observed": drift_errors,
        "schedule_failures_observed": total_schedule_failures,
        "missing_expected_schedule_dates": missing_dates,
        "duplicate_decision_timestamps": duplicates,
    }
    requirements["phase6_acceptance_preliminary"] = bool(
        requirements["elapsed_requirement_met"]
        and requirements["scheduled_decision_requirement_met"]
        and requirements["emergency_drill_requirement_met"]
        and rec_errors == 0
        and drift_errors == 0
        and total_schedule_failures == 0
        and not missing_dates
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
        "creditable_schedule_records": schedules,
        "creditable_emergency_drill_records": drills,
        "all_candidate_records": records,
        "run_inventory": inventory,
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
