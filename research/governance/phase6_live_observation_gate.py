from __future__ import annotations

"""Fail-closed preactivation gate for genuine future Phase-6 elapsed evidence.

This module is governance infrastructure only. It does not fetch market/account
state, calculate BRRK targets, sign orders, submit orders, or create elapsed-time
credit. Its job is to prevent a scheduled live-shadow collector from being armed
until the missing operational semantics are frozen prospectively.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from .validate import repo_root_from_module


GATE_RELATIVE_PATH = Path("research/governance/phase6_live_observation_gate.json")
WORKFLOW_RELATIVE_PATH = Path(".github/workflows/research-governance.yml")
PHASE6_CONTRACT_RELATIVE_PATH = Path("config/phase6_shadow_contract.json")


class Phase6ObservationGateError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise Phase6ObservationGateError(f"{path} must contain a JSON object")
    return raw


def first_eligible_decision_after(armed_commit_timestamp: str) -> str:
    """Return the first 00:00 UTC decision strictly after the arm commit time."""
    try:
        parsed = datetime.fromisoformat(armed_commit_timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Phase6ObservationGateError("armed commit timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise Phase6ObservationGateError("armed commit timestamp must be timezone-aware UTC")
    parsed = parsed.astimezone(timezone.utc)
    midnight = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
    first = midnight + timedelta(days=1)
    return first.strftime("%Y-%m-%dT00:00:00Z")


def validate_gate_mapping(
    gate: Mapping[str, Any],
    *,
    phase6_contract: Mapping[str, Any],
    workflow_text: str,
) -> dict[str, Any]:
    if int(gate.get("schema_version", -1)) != 1:
        raise Phase6ObservationGateError("unsupported Phase-6 observation gate schema")
    if gate.get("gate_id") != "PHASE6-LIVE-OBSERVATION-PREACTIVATION-V1":
        raise Phase6ObservationGateError("unexpected Phase-6 observation gate id")
    if gate.get("canonical_phase6_contract") != str(PHASE6_CONTRACT_RELATIVE_PATH):
        raise Phase6ObservationGateError("gate must point to canonical Phase-6 contract")
    if gate.get("canonical_decision_time_utc") != "00:00:00":
        raise Phase6ObservationGateError("Phase-6 canonical decision time must remain 00:00:00 UTC")

    for field in ("production_authorized", "signature_authorized", "order_submission_authorized"):
        if gate.get(field) is not False:
            raise Phase6ObservationGateError(f"{field} must remain false")
        if phase6_contract.get(field) is not False:
            raise Phase6ObservationGateError(f"canonical Phase-6 {field} drift detected")

    live = phase6_contract.get("acceptance", {}).get("live_shadow_observation", {})
    evidence = gate.get("evidence_requirements", {})
    frozen_pairs = (
        ("minimum_elapsed_calendar_days", 14),
        ("minimum_scheduled_decisions", 10),
        ("minimum_emergency_drills", 1),
        ("critical_reconciliation_errors", 0),
        ("unexplained_target_drift", 0),
        ("schedule_failures", 0),
    )
    for field, expected in frozen_pairs:
        if live.get(field) != expected or evidence.get(field) != expected:
            raise Phase6ObservationGateError(f"Phase-6 evidence threshold drift: {field}")

    future = gate.get("future_only_credit_rule", {})
    required_false = (
        "historical_backfill_authorized",
        "historical_replay_credit_authorized",
        "ci_replay_credit_authorized",
        "workflow_rerun_creates_new_decision_credit",
        "duplicate_decision_timestamp_creates_new_credit",
        "manual_dispatch_counts_as_scheduled_decision",
    )
    for field in required_false:
        if future.get(field) is not False:
            raise Phase6ObservationGateError(f"future-only rule must keep {field}=false")
    if future.get("manual_emergency_drill_may_count_as_emergency_drill_only") is not True:
        raise Phase6ObservationGateError("manual emergency drill role drift detected")
    if future.get("first_eligible_decision") != (
        "FIRST_00_00_UTC_DECISION_STRICTLY_AFTER_ARM_COMMIT_TIMESTAMP"
    ):
        raise Phase6ObservationGateError("first eligible decision rule drift detected")

    required_before_arm = gate.get("required_before_arm", {})
    required_keys = {
        "observation_account_identity_frozen",
        "current_position_and_equity_valuation_contract_frozen",
        "durable_create_only_evidence_backend_frozen",
        "schedule_and_duplicate_credit_rule_frozen",
    }
    if set(required_before_arm) != required_keys:
        raise Phase6ObservationGateError("required-before-arm dependency set drift detected")

    armed = gate.get("collector_armed") is True
    schedule_configured = gate.get("schedule_configured") is True
    credit_authorized = gate.get("elapsed_evidence_credit_authorized") is True
    dependencies_ready = all(required_before_arm.get(key) is True for key in required_keys)

    if armed:
        if not dependencies_ready:
            raise Phase6ObservationGateError("collector cannot arm before every dependency is frozen")
        if not schedule_configured or not credit_authorized:
            raise Phase6ObservationGateError("armed collector requires schedule and elapsed-credit authorization")
        if not gate.get("armed_commit"):
            raise Phase6ObservationGateError("armed collector requires an explicit arm commit")
    else:
        if schedule_configured or credit_authorized:
            raise Phase6ObservationGateError("unarmed collector cannot configure schedule or elapsed credit")
        if gate.get("armed_commit") is not None:
            raise Phase6ObservationGateError("unarmed collector must not carry an arm commit")
        if "schedule:" in workflow_text:
            raise Phase6ObservationGateError(
                "research-governance workflow must not schedule Phase-6 elapsed collection while gate is unarmed"
            )

    if phase6_contract.get("status") != "PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY":
        raise Phase6ObservationGateError("canonical Phase-6 implementation/replay status drift detected")
    if live.get("status") != "MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT":
        raise Phase6ObservationGateError("Phase-6 live elapsed status must remain inconclusive before evidence")

    return {
        "gate_id": gate["gate_id"],
        "status": gate.get("status"),
        "collector_armed": armed,
        "dependencies_ready": dependencies_ready,
        "schedule_configured": schedule_configured,
        "elapsed_evidence_credit_authorized": credit_authorized,
        "phase6_live_status": live.get("status"),
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def gate_snapshot(root: Path | None = None) -> dict[str, Any]:
    repo_root = Path(root or repo_root_from_module())
    gate = _load_json(repo_root / GATE_RELATIVE_PATH)
    phase6 = _load_json(repo_root / PHASE6_CONTRACT_RELATIVE_PATH)
    workflow = (repo_root / WORKFLOW_RELATIVE_PATH).read_text(encoding="utf-8")
    return validate_gate_mapping(gate, phase6_contract=phase6, workflow_text=workflow)


def main() -> int:
    print(json.dumps(gate_snapshot(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
