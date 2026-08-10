from __future__ import annotations

"""Fail-closed validation for the Phase-6 observation accounting index.

The ledger is intentionally non-authoritative. Durable GitHub Actions evidence
and its separately uploaded hash-bound receipt remain the evidence authority.
This module only prevents the repository-side accounting index from silently
creating credit, accepting manual/replay entries, drifting frozen Phase-6
thresholds, weakening receipt identity, or conferring production/security
authority.
"""

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .validate import repo_root_from_module

LEDGER_RELATIVE_PATH = Path("research/governance/phase6_observation_ledger.json")
GATE_RELATIVE_PATH = Path("research/governance/phase6_live_observation_gate.json")
PHASE6_CONTRACT_RELATIVE_PATH = Path("config/phase6_shadow_contract.json")
SHA256_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_RECEIPT_IDENTITY = {
    "github_run_id",
    "github_run_attempt",
    "workflow_sha",
    "decision_timestamp",
    "observed_at",
    "shadow_record_digest",
    "input_provenance_digest",
    "evidence_object_digest",
}


class Phase6ObservationLedgerError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase6ObservationLedgerError(f"{path} must contain a JSON object")
    return value


def _utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str):
        raise Phase6ObservationLedgerError(f"{field} must be an ISO-8601 UTC string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Phase6ObservationLedgerError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise Phase6ObservationLedgerError(f"{field} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise Phase6ObservationLedgerError(f"{field} must be a SHA-256 digest")
    return value.removeprefix("sha256:")


def _finite_number(value: object, *, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise Phase6ObservationLedgerError(f"{field} must be numeric") from exc
    if not math.isfinite(result):
        raise Phase6ObservationLedgerError(f"{field} must be finite")
    return result


def _nonnegative_int(value: object, *, field: str) -> int:
    if isinstance(value, bool):
        raise Phase6ObservationLedgerError(f"{field} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise Phase6ObservationLedgerError(f"{field} must be an integer") from exc
    if result < 0 or result != _finite_number(value, field=field):
        raise Phase6ObservationLedgerError(f"{field} must be a nonnegative integer")
    return result


def validate_ledger_mapping(
    ledger: Mapping[str, Any],
    *,
    gate: Mapping[str, Any],
    phase6_contract: Mapping[str, Any],
) -> dict[str, Any]:
    if ledger.get("schema_version") != 1:
        raise Phase6ObservationLedgerError("unsupported ledger schema")
    if ledger.get("ledger_id") != "PHASE6-LIVE-OBSERVATION-ACCOUNTING-V1":
        raise Phase6ObservationLedgerError("unexpected ledger id")
    if ledger.get("status") != "ACCOUNTING_INDEX_NON_EVIDENCE":
        raise Phase6ObservationLedgerError("ledger must remain explicitly non-evidence")
    if ledger.get("ledger_authority") != "ACCOUNTING_INDEX_ONLY":
        raise Phase6ObservationLedgerError("ledger cannot become an evidence authority")
    if ledger.get("recording_creates_credit") is not False:
        raise Phase6ObservationLedgerError("repository recording cannot create Phase-6 credit")

    for field in (
        "historical_backfill_authorized",
        "historical_replay_credit_authorized",
        "manual_dispatch_scheduled_decision_credit_authorized",
        "production_authorized",
        "signature_authorized",
        "order_submission_authorized",
    ):
        if ledger.get(field) is not False:
            raise Phase6ObservationLedgerError(f"ledger must keep {field}=false")

    arm_commit = ledger.get("arm_commit")
    if not isinstance(arm_commit, str) or SHA40_RE.fullmatch(arm_commit) is None:
        raise Phase6ObservationLedgerError("ledger requires the frozen 40-hex ARM commit")
    if arm_commit != gate.get("armed_commit"):
        raise Phase6ObservationLedgerError("ledger/gate ARM commit mismatch")

    first_eligible = _utc(ledger.get("first_eligible_decision"), field="first_eligible_decision")
    gate_future = gate.get("future_only_credit_rule", {})
    if gate_future.get("historical_backfill_authorized") is not False:
        raise Phase6ObservationLedgerError("gate historical-backfill rule drift")
    if gate_future.get("historical_replay_credit_authorized") is not False:
        raise Phase6ObservationLedgerError("gate replay-credit rule drift")
    if gate_future.get("manual_dispatch_counts_as_scheduled_decision") is not False:
        raise Phase6ObservationLedgerError("gate manual-dispatch credit rule drift")

    frozen = ledger.get("frozen_acceptance", {})
    live = phase6_contract.get("acceptance", {}).get("live_shadow_observation", {})
    gate_evidence = gate.get("evidence_requirements", {})
    threshold_fields = (
        "minimum_elapsed_calendar_days",
        "minimum_scheduled_decisions",
        "minimum_emergency_drills",
        "critical_reconciliation_errors",
        "unexplained_target_drift",
        "schedule_failures",
    )
    for field in threshold_fields:
        if frozen.get(field) != live.get(field) or frozen.get(field) != gate_evidence.get(field):
            raise Phase6ObservationLedgerError(f"frozen acceptance drift: {field}")

    gate_receipt_identity = gate_evidence.get("required_receipt_identity")
    if not isinstance(gate_receipt_identity, list) or set(gate_receipt_identity) != REQUIRED_RECEIPT_IDENTITY:
        raise Phase6ObservationLedgerError("frozen required receipt identity drift")

    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise Phase6ObservationLedgerError("entries must be a list")

    seen_decisions: set[str] = set()
    seen_runs: set[tuple[str, str]] = set()
    schedule_failures = 0
    reconciliation_errors = 0
    target_drifts = 0

    for index, row in enumerate(entries):
        if not isinstance(row, dict):
            raise Phase6ObservationLedgerError(f"entry {index} must be an object")
        prefix = f"entries[{index}]"
        decision_text = row.get("decision_timestamp")
        decision = _utc(decision_text, field=f"{prefix}.decision_timestamp")
        observed_text = row.get("observed_at")
        observed = _utc(observed_text, field=f"{prefix}.observed_at")
        if observed < decision:
            raise Phase6ObservationLedgerError(f"{prefix}.observed_at cannot predate decision")
        if decision < first_eligible:
            raise Phase6ObservationLedgerError(f"{prefix} predates first eligible decision")
        if decision_text in seen_decisions:
            raise Phase6ObservationLedgerError(f"duplicate credited decision timestamp: {decision_text}")
        seen_decisions.add(str(decision_text))

        if row.get("event_name") != "schedule":
            raise Phase6ObservationLedgerError(f"{prefix} scheduled credit must originate from schedule")
        if row.get("scheduled_decision_credit_candidate") is not True:
            raise Phase6ObservationLedgerError(f"{prefix} must bind a collector credit candidate")
        if row.get("credit_status") != "CREDITED_EXISTING_DURABLE_EVIDENCE":
            raise Phase6ObservationLedgerError(f"{prefix} has unexpected credit status")
        if row.get("recorded_after_event") is not True or row.get("source_evidence_already_persisted") is not True:
            raise Phase6ObservationLedgerError(f"{prefix} may index only already-persisted evidence")

        run_id = row.get("github_run_id")
        attempt = row.get("github_run_attempt")
        if not isinstance(run_id, str) or not run_id.isdigit():
            raise Phase6ObservationLedgerError(f"{prefix}.github_run_id must be numeric text")
        if not isinstance(attempt, str) or not attempt.isdigit():
            raise Phase6ObservationLedgerError(f"{prefix}.github_run_attempt must be numeric text")
        run_key = (run_id, attempt)
        if run_key in seen_runs:
            raise Phase6ObservationLedgerError(f"duplicate run/attempt in ledger: {run_key}")
        seen_runs.add(run_key)

        workflow_sha = row.get("workflow_sha")
        if not isinstance(workflow_sha, str) or SHA40_RE.fullmatch(workflow_sha) is None:
            raise Phase6ObservationLedgerError(f"{prefix}.workflow_sha must be 40-hex")

        evidence = row.get("evidence_artifact")
        receipt = row.get("receipt_artifact")
        binding = row.get("receipt_binding")
        checks = row.get("observation_checks")
        if not all(isinstance(value, dict) for value in (evidence, receipt, binding, checks)):
            raise Phase6ObservationLedgerError(f"{prefix} requires evidence, receipt, binding and checks")

        evidence_id = evidence.get("id")
        receipt_id = receipt.get("id")
        if not isinstance(evidence_id, str) or not evidence_id.isdigit():
            raise Phase6ObservationLedgerError(f"{prefix}.evidence_artifact.id must be numeric text")
        if not isinstance(receipt_id, str) or not receipt_id.isdigit() or receipt_id == evidence_id:
            raise Phase6ObservationLedgerError(f"{prefix} requires a distinct receipt artifact")
        evidence_digest = _sha256(evidence.get("digest"), field=f"{prefix}.evidence_artifact.digest")
        _sha256(receipt.get("digest"), field=f"{prefix}.receipt_artifact.digest")
        _utc(evidence.get("created_at"), field=f"{prefix}.evidence_artifact.created_at")
        _utc(receipt.get("created_at"), field=f"{prefix}.receipt_artifact.created_at")
        if _utc(evidence.get("expires_at"), field=f"{prefix}.evidence_artifact.expires_at") <= decision:
            raise Phase6ObservationLedgerError(f"{prefix} evidence expiry must be after decision")
        if _utc(receipt.get("expires_at"), field=f"{prefix}.receipt_artifact.expires_at") <= decision:
            raise Phase6ObservationLedgerError(f"{prefix} receipt expiry must be after decision")

        expected_binding_identity = {
            "github_run_id": run_id,
            "github_run_attempt": attempt,
            "workflow_sha": workflow_sha,
            "decision_timestamp": decision_text,
            "observed_at": observed_text,
        }
        for field, expected in expected_binding_identity.items():
            if binding.get(field) != expected:
                raise Phase6ObservationLedgerError(f"{prefix} receipt identity mismatch: {field}")
        if binding.get("scheduled_decision_credit_candidate") is not True:
            raise Phase6ObservationLedgerError(f"{prefix} receipt did not bind scheduled credit candidate")

        if str(binding.get("evidence_artifact_id")) != evidence_id:
            raise Phase6ObservationLedgerError(f"{prefix} receipt does not bind evidence artifact id")
        if _sha256(binding.get("evidence_artifact_digest"), field=f"{prefix}.receipt_binding.evidence_artifact_digest") != evidence_digest:
            raise Phase6ObservationLedgerError(f"{prefix} receipt/evidence digest mismatch")
        for digest_field in ("evidence_object_digest", "input_provenance_digest", "shadow_record_digest"):
            _sha256(binding.get(digest_field), field=f"{prefix}.receipt_binding.{digest_field}")
        missing_receipt_identity = REQUIRED_RECEIPT_IDENTITY - set(binding)
        if missing_receipt_identity:
            raise Phase6ObservationLedgerError(
                f"{prefix} missing frozen receipt identity: {sorted(missing_receipt_identity)}"
            )

        if checks.get("shadow_status") != "SHADOW_COMPUTED_NO_AUTHORITY":
            raise Phase6ObservationLedgerError(f"{prefix} shadow computation was not complete")
        if checks.get("shadow_alerts") != []:
            raise Phase6ObservationLedgerError(f"{prefix} carries shadow alerts and cannot be clean credit")
        if checks.get("target_reference_parity_passed") is not True:
            raise Phase6ObservationLedgerError(f"{prefix} target reference parity did not pass")
        if _finite_number(checks.get("target_reference_gross_abs_difference"), field=f"{prefix}.target_reference_gross_abs_difference") != 0.0:
            raise Phase6ObservationLedgerError(f"{prefix} gross reference drift is nonzero")
        if _finite_number(checks.get("target_reference_max_weight_abs_difference"), field=f"{prefix}.target_reference_max_weight_abs_difference") != 0.0:
            raise Phase6ObservationLedgerError(f"{prefix} weight reference drift is nonzero")
        if _finite_number(checks.get("offline_reference_l1_drift"), field=f"{prefix}.offline_reference_l1_drift") != 0.0:
            raise Phase6ObservationLedgerError(f"{prefix} offline reference drift is nonzero")

        for field in (
            "authorization_headers_used_for_market_or_account_reads",
            "secret_material_present",
            "production_authorized",
            "signature_authorized",
            "order_submission_authorized",
        ):
            if checks.get(field) is not False:
                raise Phase6ObservationLedgerError(f"{prefix} must keep {field}=false")

        rec = _nonnegative_int(checks.get("critical_reconciliation_errors_observed"), field=f"{prefix}.critical_reconciliation_errors_observed")
        drift = _nonnegative_int(checks.get("unexplained_target_drift_observed"), field=f"{prefix}.unexplained_target_drift_observed")
        sched = _nonnegative_int(checks.get("schedule_failure_observed"), field=f"{prefix}.schedule_failure_observed")
        reconciliation_errors += rec
        target_drifts += drift
        schedule_failures += sched

    progress = ledger.get("progress", {})
    if not isinstance(progress, dict):
        raise Phase6ObservationLedgerError("progress must be an object")
    genuine_scheduled = _nonnegative_int(progress.get("genuine_scheduled_decisions"), field="progress.genuine_scheduled_decisions")
    distinct_decisions = _nonnegative_int(progress.get("distinct_credited_decision_dates"), field="progress.distinct_credited_decision_dates")
    emergency_drills = _nonnegative_int(progress.get("emergency_drills"), field="progress.emergency_drills")
    progress_rec = _nonnegative_int(progress.get("critical_reconciliation_errors_observed"), field="progress.critical_reconciliation_errors_observed")
    progress_drift = _nonnegative_int(progress.get("unexplained_target_drift_observed"), field="progress.unexplained_target_drift_observed")
    progress_sched = _nonnegative_int(progress.get("schedule_failures_observed"), field="progress.schedule_failures_observed")

    if genuine_scheduled != len(entries):
        raise Phase6ObservationLedgerError("progress scheduled-decision count does not match entries")
    if distinct_decisions != len(seen_decisions):
        raise Phase6ObservationLedgerError("progress distinct-decision count does not match entries")
    if progress_rec != reconciliation_errors:
        raise Phase6ObservationLedgerError("progress reconciliation count does not match entries")
    if progress_drift != target_drifts:
        raise Phase6ObservationLedgerError("progress target-drift count does not match entries")
    if progress_sched != schedule_failures:
        raise Phase6ObservationLedgerError("progress schedule-failure count does not match entries")

    expected_decision_met = len(entries) >= int(frozen["minimum_scheduled_decisions"])
    expected_drill_met = emergency_drills >= int(frozen["minimum_emergency_drills"])
    if progress.get("scheduled_decision_requirement_met") is not expected_decision_met:
        raise Phase6ObservationLedgerError("scheduled-decision requirement flag drift")
    if progress.get("emergency_drill_requirement_met") is not expected_drill_met:
        raise Phase6ObservationLedgerError("emergency-drill requirement flag drift")
    if progress.get("phase6_live_acceptance_status") != "MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT":
        raise Phase6ObservationLedgerError("ledger cannot declare Phase-6 live acceptance passed")

    return {
        "ledger_id": ledger["ledger_id"],
        "status": ledger["status"],
        "genuine_scheduled_decisions": len(entries),
        "emergency_drills": emergency_drills,
        "critical_reconciliation_errors_observed": reconciliation_errors,
        "unexplained_target_drift_observed": target_drifts,
        "schedule_failures_observed": schedule_failures,
        "phase6_live_acceptance_status": progress.get("phase6_live_acceptance_status"),
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def ledger_snapshot(root: Path | None = None) -> dict[str, Any]:
    repo_root = Path(root or repo_root_from_module())
    return validate_ledger_mapping(
        _load_json(repo_root / LEDGER_RELATIVE_PATH),
        gate=_load_json(repo_root / GATE_RELATIVE_PATH),
        phase6_contract=_load_json(repo_root / PHASE6_CONTRACT_RELATIVE_PATH),
    )


def main() -> int:
    print(json.dumps(ledger_snapshot(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
