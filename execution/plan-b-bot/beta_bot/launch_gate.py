from __future__ import annotations

"""Phase 7 limited-live readiness gate.

Pure authorization policy only.  It never imports an executor, signer or exchange
client and never submits orders.  Current repository state intentionally lacks
Phase-6 elapsed evidence and owner approval, therefore current launch remains
blocked even if this module is implementation-ready.
"""

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


P7_GATE_VERSION = "P7-LIMITED-LIVE-GATE-V1"
PRODUCTION_GROSS_CAP = 1.0


class ProgramState(str, Enum):
    MONITOR_ONLY = "MONITOR_ONLY"
    FLAT = "FLAT"
    LONG = "LONG"
    SHORT_READY = "SHORT_READY"
    SHORT = "SHORT"
    ACTIVE = "ACTIVE"


@dataclass(frozen=True)
class LaunchEvidence:
    phase6_implementation_replay_passed: bool
    phase6_live_elapsed_evidence_passed: bool
    production_release_frozen: bool
    trading_agent_credential_only: bool
    master_wallet_private_key_absent: bool
    withdrawal_transfer_automation_absent: bool
    hard_exposure_cap: float
    kill_switch_tested: bool
    startup_reconciliation_passed: bool
    monitoring_active: bool


@dataclass(frozen=True)
class GateDecision:
    gate_version: str
    allowed: bool
    current_state: str
    requested_state: str
    blockers: tuple[str, ...]
    approval_ref: str | None
    production_authorized: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def launch_blockers(e: LaunchEvidence) -> tuple[str, ...]:
    checks = [
        (e.phase6_implementation_replay_passed, "PHASE6_IMPLEMENTATION_REPLAY_NOT_PASSED"),
        (e.phase6_live_elapsed_evidence_passed, "PHASE6_LIVE_ELAPSED_EVIDENCE_NOT_PASSED"),
        (e.production_release_frozen, "PRODUCTION_RELEASE_NOT_FROZEN"),
        (e.trading_agent_credential_only, "TRADING_AGENT_CREDENTIAL_NOT_PROVEN"),
        (e.master_wallet_private_key_absent, "MASTER_WALLET_PRIVATE_KEY_NOT_PROVEN_ABSENT"),
        (e.withdrawal_transfer_automation_absent, "WITHDRAWAL_TRANSFER_AUTOMATION_NOT_PROVEN_ABSENT"),
        (abs(float(e.hard_exposure_cap) - PRODUCTION_GROSS_CAP) <= 1e-12, "HARD_EXPOSURE_CAP_NOT_CANONICAL_1_0"),
        (e.kill_switch_tested, "KILL_SWITCH_NOT_TESTED"),
        (e.startup_reconciliation_passed, "STARTUP_RECONCILIATION_NOT_PASSED"),
        (e.monitoring_active, "MONITORING_NOT_ACTIVE"),
    ]
    return tuple(reason for ok, reason in checks if not ok)


def evaluate_transition(
    *,
    evidence: LaunchEvidence,
    current_state: ProgramState,
    requested_state: ProgramState,
    owner_approval_ref: str | None = None,
    first_bear_short_approval_ref: str | None = None,
) -> GateDecision:
    blockers = list(launch_blockers(evidence))
    approval_ref = (owner_approval_ref or "").strip() or None

    if current_state == ProgramState.MONITOR_ONLY and requested_state == ProgramState.ACTIVE:
        if not approval_ref:
            blockers.append("EXPLICIT_OWNER_APPROVAL_REQUIRED_MONITOR_ONLY_TO_ACTIVE")
    elif current_state == ProgramState.FLAT and requested_state == ProgramState.LONG:
        if not approval_ref:
            blockers.append("EXPLICIT_OWNER_APPROVAL_REQUIRED_FLAT_TO_LONG")
    elif current_state == ProgramState.FLAT and requested_state in {ProgramState.SHORT_READY, ProgramState.SHORT}:
        if not approval_ref:
            blockers.append("EXPLICIT_OWNER_APPROVAL_REQUIRED_FLAT_TO_SHORT")
        if requested_state == ProgramState.SHORT and not (first_bear_short_approval_ref or "").strip():
            blockers.append("EXPLICIT_FIRST_BEAR_SHORT_APPROVAL_REQUIRED")
    else:
        blockers.append("TRANSITION_NOT_A_P7_LAUNCH_BOUNDARY")

    normalized = tuple(dict.fromkeys(blockers))
    allowed = not normalized
    return GateDecision(
        gate_version=P7_GATE_VERSION,
        allowed=allowed,
        current_state=current_state.value,
        requested_state=requested_state.value,
        blockers=normalized,
        approval_ref=approval_ref,
        production_authorized=allowed,
    )
