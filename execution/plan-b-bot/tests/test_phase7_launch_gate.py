from __future__ import annotations

import ast
from pathlib import Path

from beta_bot.launch_gate import (
    LaunchEvidence,
    ProgramState,
    evaluate_transition,
    launch_blockers,
)


def evidence(**overrides) -> LaunchEvidence:
    values = dict(
        phase6_implementation_replay_passed=True,
        phase6_live_elapsed_evidence_passed=False,
        production_release_frozen=True,
        trading_agent_credential_only=True,
        master_wallet_private_key_absent=True,
        withdrawal_transfer_automation_absent=True,
        hard_exposure_cap=1.0,
        kill_switch_tested=True,
        startup_reconciliation_passed=True,
        monitoring_active=True,
    )
    values.update(overrides)
    return LaunchEvidence(**values)


def test_current_project_state_remains_blocked_by_elapsed_evidence_and_owner_gate() -> None:
    decision = evaluate_transition(
        evidence=evidence(),
        current_state=ProgramState.MONITOR_ONLY,
        requested_state=ProgramState.ACTIVE,
    )
    assert decision.allowed is False
    assert decision.production_authorized is False
    assert "PHASE6_LIVE_ELAPSED_EVIDENCE_NOT_PASSED" in decision.blockers
    assert "EXPLICIT_OWNER_APPROVAL_REQUIRED_MONITOR_ONLY_TO_ACTIVE" in decision.blockers


def test_all_launch_checklist_items_are_fail_closed() -> None:
    fields = {
        "production_release_frozen": "PRODUCTION_RELEASE_NOT_FROZEN",
        "trading_agent_credential_only": "TRADING_AGENT_CREDENTIAL_NOT_PROVEN",
        "master_wallet_private_key_absent": "MASTER_WALLET_PRIVATE_KEY_NOT_PROVEN_ABSENT",
        "withdrawal_transfer_automation_absent": "WITHDRAWAL_TRANSFER_AUTOMATION_NOT_PROVEN_ABSENT",
        "kill_switch_tested": "KILL_SWITCH_NOT_TESTED",
        "startup_reconciliation_passed": "STARTUP_RECONCILIATION_NOT_PASSED",
        "monitoring_active": "MONITORING_NOT_ACTIVE",
    }
    for field, blocker in fields.items():
        assert blocker in launch_blockers(evidence(phase6_live_elapsed_evidence_passed=True, **{field: False}))
    assert "HARD_EXPOSURE_CAP_NOT_CANONICAL_1_0" in launch_blockers(
        evidence(phase6_live_elapsed_evidence_passed=True, hard_exposure_cap=1.2)
    )


def test_human_boundaries_require_distinct_explicit_approval() -> None:
    ready = evidence(phase6_live_elapsed_evidence_passed=True)
    assert evaluate_transition(
        evidence=ready,
        current_state=ProgramState.MONITOR_ONLY,
        requested_state=ProgramState.ACTIVE,
        owner_approval_ref="OWNER-APPROVAL-ACTIVE-TEST",
    ).allowed
    assert evaluate_transition(
        evidence=ready,
        current_state=ProgramState.FLAT,
        requested_state=ProgramState.LONG,
        owner_approval_ref="OWNER-APPROVAL-LONG-TEST",
    ).allowed
    short_ready = evaluate_transition(
        evidence=ready,
        current_state=ProgramState.FLAT,
        requested_state=ProgramState.SHORT,
        owner_approval_ref="OWNER-APPROVAL-SHORT-TEST",
    )
    assert not short_ready.allowed
    assert "EXPLICIT_FIRST_BEAR_SHORT_APPROVAL_REQUIRED" in short_ready.blockers
    assert evaluate_transition(
        evidence=ready,
        current_state=ProgramState.FLAT,
        requested_state=ProgramState.SHORT,
        owner_approval_ref="OWNER-APPROVAL-SHORT-TEST",
        first_bear_short_approval_ref="OWNER-FIRST-BEAR-SHORT-TEST",
    ).allowed


def test_gate_has_no_executor_signer_or_secret_import_path() -> None:
    path = Path(__file__).resolve().parents[1] / "beta_bot" / "launch_gate.py"
    tree = ast.parse(path.read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = ("executor", "hyperliquid", "eth_account", "web3", "config")
    assert not any(any(fragment in name for fragment in forbidden) for name in imports)
