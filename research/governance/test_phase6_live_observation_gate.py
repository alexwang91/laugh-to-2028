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


class Phase6LiveObservationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = json.loads((ROOT / "research/governance/phase6_live_observation_gate.json").read_text(encoding="utf-8"))
        self.phase6 = json.loads((ROOT / "config/phase6_shadow_contract.json").read_text(encoding="utf-8"))
        self.evidence_contract = json.loads((ROOT / "research/governance/phase6_live_evidence_contract.json").read_text(encoding="utf-8"))
        self.valuation_contract = json.loads((ROOT / "research/governance/phase6_live_valuation_contract.json").read_text(encoding="utf-8"))
        self.instrument_registry = json.loads((ROOT / "config/instrument_registry.json").read_text(encoding="utf-8"))
        self.workflow = (ROOT / ".github/workflows/research-governance.yml").read_text(encoding="utf-8")

    def validate(self, gate=None, workflow=None, evidence_contract=None, valuation_contract=None, instrument_registry=None):
        return validate_gate_mapping(
            gate or self.gate,
            phase6_contract=self.phase6,
            evidence_contract=evidence_contract or self.evidence_contract,
            valuation_contract=valuation_contract or self.valuation_contract,
            instrument_registry=instrument_registry or self.instrument_registry,
            workflow_text=self.workflow if workflow is None else workflow,
        )

    def test_repository_gate_is_fail_closed_and_does_not_start_elapsed_clock(self) -> None:
        snapshot = self.validate()
        self.assertEqual(snapshot["status"], "PREACTIVATION_BLOCKED_FAIL_CLOSED")
        self.assertFalse(snapshot["collector_armed"])
        self.assertFalse(snapshot["dependencies_ready"])
        self.assertFalse(snapshot["account_identity_frozen"])
        self.assertTrue(snapshot["valuation_contract_frozen"])
        self.assertEqual(snapshot["valuation_mode"], "disabled")
        self.assertTrue(snapshot["durable_evidence_backend_frozen"])
        self.assertEqual(snapshot["durable_evidence_backend"], "GITHUB_ACTIONS_ARTIFACT_V4")
        self.assertFalse(snapshot["schedule_configured"])
        self.assertFalse(snapshot["elapsed_evidence_credit_authorized"])
        self.assertFalse(snapshot["production_authorized"])
        self.assertFalse(snapshot["signature_authorized"])
        self.assertFalse(snapshot["order_submission_authorized"])

    def test_first_eligible_decision_is_strictly_after_arm_commit(self) -> None:
        self.assertEqual(first_eligible_decision_after("2026-08-08T16:30:00Z"), "2026-08-09T00:00:00Z")
        self.assertEqual(first_eligible_decision_after("2026-08-08T00:00:00Z"), "2026-08-09T00:00:00Z")

    def test_backfill_or_replay_credit_is_rejected(self) -> None:
        for field in (
            "historical_backfill_authorized", "historical_replay_credit_authorized",
            "ci_replay_credit_authorized", "workflow_rerun_creates_new_decision_credit",
            "duplicate_decision_timestamp_creates_new_credit", "manual_dispatch_counts_as_scheduled_decision",
        ):
            gate = copy.deepcopy(self.gate)
            gate["future_only_credit_rule"][field] = True
            with self.subTest(field=field):
                with self.assertRaises(Phase6ObservationGateError):
                    self.validate(gate=gate)

    def test_unarmed_gate_rejects_schedule_or_credit(self) -> None:
        gate = copy.deepcopy(self.gate)
        gate["schedule_configured"] = True
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate)
        gate = copy.deepcopy(self.gate)
        gate["elapsed_evidence_credit_authorized"] = True
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate)
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(workflow=self.workflow + "\nschedule:\n  - cron: '17 0 * * *'\n")

    def test_collector_cannot_arm_with_account_identity_still_unfrozen(self) -> None:
        gate = copy.deepcopy(self.gate)
        gate["collector_armed"] = True
        gate["schedule_configured"] = True
        gate["elapsed_evidence_credit_authorized"] = True
        gate["armed_commit"] = "deadbeef"
        with self.assertRaises(Phase6ObservationGateError, msg="missing account identity must block"):
            self.validate(gate=gate)

    def test_evidence_backend_flag_requires_valid_frozen_contract(self) -> None:
        evidence = copy.deepcopy(self.evidence_contract)
        evidence["backend"]["overwrite"] = True
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(evidence_contract=evidence)
        gate = copy.deepcopy(self.gate)
        gate["required_before_arm"]["durable_create_only_evidence_backend_frozen"] = False
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate)

    def test_valuation_flag_requires_valid_standard_mode_contract(self) -> None:
        valuation = copy.deepcopy(self.valuation_contract)
        valuation["supported_account_mode"]["required_value"] = "unifiedAccount"
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(valuation_contract=valuation)
        gate = copy.deepcopy(self.gate)
        gate["required_before_arm"]["current_position_and_equity_valuation_contract_frozen"] = False
        with self.assertRaises(Phase6ObservationGateError):
            self.validate(gate=gate)

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
                instrument_registry=self.instrument_registry,
                workflow_text=self.workflow,
            )


if __name__ == "__main__":
    unittest.main()
