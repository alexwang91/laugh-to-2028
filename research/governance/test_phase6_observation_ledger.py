from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.governance.phase6_observation_ledger import (
    Phase6ObservationLedgerError,
    validate_ledger_mapping,
)

ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Phase6ObservationLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = load("research/governance/phase6_observation_ledger.json")
        self.gate = load("research/governance/phase6_live_observation_gate.json")
        self.contract = load("config/phase6_shadow_contract.json")

    def validate(self, ledger: dict) -> dict:
        return validate_ledger_mapping(ledger, gate=self.gate, phase6_contract=self.contract)

    def test_current_ledger_is_clean_non_authoritative_index(self) -> None:
        snapshot = self.validate(self.ledger)
        self.assertEqual(snapshot["genuine_scheduled_decisions"], 1)
        self.assertEqual(snapshot["emergency_drills"], 0)
        self.assertEqual(snapshot["critical_reconciliation_errors_observed"], 0)
        self.assertEqual(snapshot["unexplained_target_drift_observed"], 0)
        self.assertEqual(snapshot["schedule_failures_observed"], 0)
        self.assertEqual(snapshot["phase6_live_acceptance_status"], "MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT")
        self.assertFalse(snapshot["production_authorized"])
        self.assertFalse(snapshot["signature_authorized"])
        self.assertFalse(snapshot["order_submission_authorized"])

    def test_repository_recording_cannot_create_credit(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["recording_creates_credit"] = True
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_manual_dispatch_cannot_be_indexed_as_scheduled_credit(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["event_name"] = "workflow_dispatch"
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_pre_arm_or_pre_eligible_decision_cannot_receive_credit(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["decision_timestamp"] = "2026-08-09T00:00:00Z"
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_duplicate_decision_cannot_create_second_credit(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["entries"].append(copy.deepcopy(bad["entries"][0]))
        bad["progress"]["genuine_scheduled_decisions"] = 2
        bad["progress"]["distinct_credited_decision_dates"] = 2
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_receipt_must_be_distinct_and_bind_evidence(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["receipt_artifact"]["id"] = bad["entries"][0]["evidence_artifact"]["id"]
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["receipt_binding"]["evidence_artifact_digest"] = "0" * 64
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_receipt_identity_cannot_be_substituted(self) -> None:
        fields_and_bad_values = {
            "github_run_id": "99999999999",
            "github_run_attempt": "2",
            "workflow_sha": "0" * 40,
            "decision_timestamp": "2026-08-11T00:00:00Z",
            "observed_at": "2026-08-10T01:15:21Z",
        }
        for field, value in fields_and_bad_values.items():
            bad = copy.deepcopy(self.ledger)
            bad["entries"][0]["receipt_binding"][field] = value
            with self.assertRaises(Phase6ObservationLedgerError, msg=field):
                self.validate(bad)

        bad = copy.deepcopy(self.ledger)
        del bad["entries"][0]["receipt_binding"]["shadow_record_digest"]
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["receipt_binding"]["scheduled_decision_credit_candidate"] = False
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_clean_credit_rejects_shadow_alert_or_target_drift(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["observation_checks"]["shadow_alerts"] = ["TARGET_REFERENCE_MISMATCH"]
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

        bad = copy.deepcopy(self.ledger)
        bad["entries"][0]["observation_checks"]["offline_reference_l1_drift"] = 1e-4
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)

    def test_ledger_cannot_confer_production_or_security_authority(self) -> None:
        for field in ("production_authorized", "signature_authorized", "order_submission_authorized"):
            bad = copy.deepcopy(self.ledger)
            bad[field] = True
            with self.assertRaises(Phase6ObservationLedgerError, msg=field):
                self.validate(bad)

    def test_progress_cannot_overstate_entry_count(self) -> None:
        bad = copy.deepcopy(self.ledger)
        bad["progress"]["genuine_scheduled_decisions"] = 10
        bad["progress"]["scheduled_decision_requirement_met"] = True
        with self.assertRaises(Phase6ObservationLedgerError):
            self.validate(bad)


if __name__ == "__main__":
    unittest.main()
