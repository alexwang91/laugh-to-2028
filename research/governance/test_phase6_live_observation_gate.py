from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.governance.phase6_live_observation_gate import (
    Phase6ObservationGateError,
    first_eligible_decision_after,
    validate_gate_mapping,
)

ROOT = Path(__file__).resolve().parents[2]
MASTER = "0x1111111111111111111111111111111111111111"
ARM_MARKER = "cbd58adb05187651ca72d67900a0ccbbd3e83b1e"
SCHEDULE_BLOCK = "  schedule:\n    - cron: '0 0 * * *'\n"


class Phase6LiveObservationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = json.loads((ROOT / "research/governance/phase6_live_observation_gate.json").read_text(encoding="utf-8"))
        self.phase6 = json.loads((ROOT / "config/phase6_shadow_contract.json").read_text(encoding="utf-8"))
        self.evidence_contract = json.loads((ROOT / "research/governance/phase6_live_evidence_contract.json").read_text(encoding="utf-8"))
        self.valuation_contract = json.loads((ROOT / "research/governance/phase6_live_valuation_contract.json").read_text(encoding="utf-8"))
        self.account_identity_contract = json.loads((ROOT / "research/governance/phase6_live_account_identity_contract.json").read_text(encoding="utf-8"))
        self.instrument_registry = json.loads((ROOT / "config/instrument_registry.json").read_text(encoding="utf-8"))
        self.workflow = (ROOT / ".github/workflows/research-governance.yml").read_text(encoding="utf-8")

    def validate(
        self,
        gate=None,
        workflow=None,
        evidence_contract=None,
        valuation_contract=None,
        account_identity_contract=None,
        instrument_registry=None,
    ):
        return validate_gate_mapping(
            self.gate if gate is None else gate,
            phase6_contract=self.phase6,
            evidence_contract=self.evidence_contract if evidence_contract is None else evidence_contract,
            valuation_contract=self.valuation_contract if valuation_contract is None else valuation_contract,
            account_identity_contract=(
                self.account_identity_contract
                if account_identity_contract is None
                else account_identity_contract
            ),
            instrument_registry=self.instrument_registry if instrument_registry is None else instrument_registry,
            workflow_text=self.workflow if workflow is None else workflow,
        )

    def prearm_evidence_contract(self):
        contract = copy.deepcopy(self.evidence_contract)
        contract["status"] = "FROZEN_BACKEND_NOT_COLLECTING"
        contract["collection_active"] = False
        contract["elapsed_evidence_credit_active"] = False
        contract["armed_commit"] = None
        contract["explicit_non_actions"] = [
            "NO_ACCOUNT_IDENTITY_SELECTION",
            "NO_POSITION_OR_EQUITY_VALUATION_CHANGE",
            "NO_SCHEDULE_ARM",
            "NO_ELAPSED_EVIDENCE_CREDIT",
            "NO_SIGNING",
            "NO_ORDER_SUBMISSION",
            "NO_PRODUCTION_AUTHORIZATION",
        ]
        return contract

    def unarmed_gate(self):
        gate = copy.deepcopy(self.gate)
        gate["status"] = "PREACTIVATION_READY_AWAITING_SEPARATE_ARM"
        gate["collector_armed"] = False
        gate["schedule_configured"] = False
        gate["elapsed_evidence_credit_authorized"] = False
        gate["armed_commit"] = None
        return gate

    def unbound_identity_contract(self):
        contract = copy.deepcopy(self.account_identity_contract)
        contract.update(
            {
                "status": "AWAITING_EXPLICIT_PUBLIC_ADDRESS",
                "account_address": None,
                "identity_frozen": False,
                "address_source": None,
                "binding_evidence": None,
            }
        )
        return contract

    def bound_identity_contract(self):
        contract = self.unbound_identity_contract()
        contract.update(
            {
                "status": "FROZEN_VERIFIED_READ_ONLY_IDENTITY",
                "account_address": MASTER,
                "identity_frozen": True,
                "address_source": "EXPLICIT_PUBLIC_ADDRESS",
                "binding_evidence": {
                    "query_address": MASTER,
                    "verified_at": "2026-08-09T12:00:00Z",
                    "user_role_response": {"role": "user"},
                    "user_abstraction_response": "disabled",
                    "raw_response_sha256": {
                        "userRole": "a" * 64,
                        "userAbstraction": "b" * 64,
                    },
                },
            }
        )
        return contract

    def workflow_without_schedule(self) -> str:
        self.assertIn(SCHEDULE_BLOCK, self.workflow)
        return self.workflow.replace(SCHEDULE_BLOCK, "", 1)

    def test_repository_gate_is_armed_future_only_and_zero_authority(self) -> None:
        snapshot = self.validate()
        self.assertEqual(snapshot["status"], "ARMED_FUTURE_ONLY_OBSERVATION_ACTIVE")
        self.assertTrue(snapshot["collector_armed"])
        self.assertTrue(snapshot["dependencies_ready"])
        self.assertEqual(snapshot["account_identity_contract_status"], "FROZEN_VERIFIED_READ_ONLY_IDENTITY")
        self.assertTrue(snapshot["account_identity_frozen"])
        self.assertIsNotNone(snapshot["account_address"])
        self.assertEqual(snapshot["valuation_mode"], "disabled")
        self.assertTrue(snapshot["evidence_collection_active"])
        self.assertTrue(snapshot["schedule_configured"])
        self.assertTrue(snapshot["elapsed_evidence_credit_authorized"])
        self.assertEqual(snapshot["armed_commit"], ARM_MARKER)
        self.assertFalse(snapshot["production_authorized"])
        self.assertFalse(snapshot["signature_authorized"])
        self.assertFalse(snapshot["order_submission_authorized"])

    def test_first_eligible_decision_is_strictly_after_arm_commit_timestamp(self) -> None:
        self.assertEqual(first_eligible_decision_after("2026-08-09T13:41:32Z"), "2026-08-10T00:00:00Z")
        self.assertEqual(first_eligible_decision_after("2026-08-09T00:00:00Z"), "2026-08-10T00:00:00Z")

    def test_unarmed_ready_fixture_remains_valid_but_has_no_clock(self) -> None:
        snapshot = self.validate(
            gate=self.unarmed_gate(),
            evidence_contract=self.prearm_evidence_contract(),
            workflow=self.workflow_without_schedule(),
        )
        self.assertEqual(snapshot["status"], "PREACTIVATION_READY_AWAITING_SEPARATE_ARM")
        self.assertFalse(snapshot["collector_armed"])
        self.assertTrue(snapshot["dependencies_ready"])
        self.assertFalse(snapshot["evidence_collection_active"])
        self.assertFalse(snapshot["schedule_configured"])
        self.assertFalse(snapshot["elapsed_evidence_credit_authorized"])
        self.assertIsNone(snapshot["armed_commit"])

    def test_backfill_replay_rerun_and_manual_scheduled_credit_are_rejected(self) -> None:
        for field in (
            "historical_backfill_authorized",
            "historical_replay_credit_authorized",
            "ci_replay_credit_authorized",
            "workflow_rerun_creates_new_decision_credit",
            "duplicate_decision_timestamp_creates_new_credit",
            "manual_dispatch_counts_as_scheduled_decision",
        ):
            gate = copy.deepcopy(self.gate)
            gate["future_only_credit_rule"][field] = True
            with self.subTest(field=field):
                with self.assertRaises(Phase6ObservationGateError):
                    self.validate(gate=gate)

    def test_armed_gate_requires_exact_daily_midnight_schedule(self) -> None:
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(workflow=self.workflow_without_schedule())
        wrong = self.workflow.replace("cron: '0 0 * * *'", "cron: '17 0 * * *'", 1)
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(workflow=wrong)

    def test_gate_and_evidence_backend_must_reference_same_arm_marker(self) -> None:
        evidence = copy.deepcopy(self.evidence_contract)
        evidence["armed_commit"] = "a" * 40
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(evidence_contract=evidence)
        gate = copy.deepcopy(self.gate)
        gate["armed_commit"] = "deadbeef"
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate)

    def test_armed_gate_cannot_lose_any_prearm_dependency(self) -> None:
        for field in self.gate["required_before_arm"]:
            gate = copy.deepcopy(self.gate)
            gate["required_before_arm"][field] = False
            with self.subTest(field=field):
                with self.assertRaises(Phase6ObservationGateError):
                    self.validate(gate=gate)

    def test_identity_contract_rejects_agent_or_nonstandard_account(self) -> None:
        contract = self.bound_identity_contract()
        contract["binding_evidence"]["user_role_response"] = {"role": "agent", "data": {"user": MASTER}}
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(account_identity_contract=contract)

        contract = self.bound_identity_contract()
        contract["binding_evidence"]["user_abstraction_response"] = "portfolioMargin"
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(account_identity_contract=contract)

    def test_unbound_identity_still_blocks_arm(self) -> None:
        gate = copy.deepcopy(self.gate)
        gate["required_before_arm"]["observation_account_identity_frozen"] = False
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate, account_identity_contract=self.unbound_identity_contract())

    def test_evidence_backend_and_valuation_must_remain_valid(self) -> None:
        evidence = copy.deepcopy(self.evidence_contract)
        evidence["backend"]["overwrite"] = True
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(evidence_contract=evidence)

        valuation = copy.deepcopy(self.valuation_contract)
        valuation["supported_account_mode"]["required_value"] = "unifiedAccount"
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(valuation_contract=valuation)

    def test_frozen_phase6_acceptance_thresholds_cannot_drift(self) -> None:
        gate = copy.deepcopy(self.gate)
        gate["evidence_requirements"]["minimum_scheduled_decisions"] = 9
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate)
        phase6 = copy.deepcopy(self.phase6)
        phase6["acceptance"]["live_shadow_observation"]["minimum_elapsed_calendar_days"] = 13
        with self.assertRaises(Phase6ObservationGateError):
            validate_gate_mapping(
                gate=self.gate,
                phase6_contract=phase6,
                evidence_contract=self.evidence_contract,
                valuation_contract=self.valuation_contract,
                account_identity_contract=self.account_identity_contract,
                instrument_registry=self.instrument_registry,
                workflow_text=self.workflow,
            )


if __name__ == "__main__":
    unittest.main()
