from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.governance.phase6_live_evidence import (
    Phase6LiveEvidenceError,
    validate_evidence_contract,
)


ROOT = Path(__file__).resolve().parents[2]


class Phase6LiveEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(
            (ROOT / "research/governance/phase6_live_evidence_contract.json").read_text(
                encoding="utf-8"
            )
        )

    def test_repository_contract_is_armed_future_only_and_zero_authority(self) -> None:
        snapshot = validate_evidence_contract(self.contract)
        self.assertEqual(snapshot["status"], "ARMED_COLLECTING_FUTURE_ONLY")
        self.assertEqual(snapshot["backend"], "GITHUB_ACTIONS_ARTIFACT_V4")
        self.assertEqual(snapshot["retention_days"], 90)
        self.assertFalse(snapshot["overwrite"])
        self.assertTrue(snapshot["collection_active"])
        self.assertTrue(snapshot["credit_active"])
        self.assertEqual(snapshot["armed_commit"], "cbd58adb05187651ca72d67900a0ccbbd3e83b1e")
        self.assertFalse(snapshot["production_authorized"])

    def test_prearm_fixture_remains_valid_and_inactive(self) -> None:
        contract = copy.deepcopy(self.contract)
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
        snapshot = validate_evidence_contract(contract)
        self.assertFalse(snapshot["collection_active"])
        self.assertFalse(snapshot["credit_active"])
        self.assertIsNone(snapshot["armed_commit"])

    def test_armed_backend_requires_real_marker_and_future_only_boundaries(self) -> None:
        broken = copy.deepcopy(self.contract)
        broken["armed_commit"] = "deadbeef"
        with self.assertRaises(Phase6LiveEvidenceError):
            validate_evidence_contract(broken)

        broken = copy.deepcopy(self.contract)
        broken["explicit_non_actions"].remove("NO_HISTORICAL_CREDIT")
        with self.assertRaises(Phase6LiveEvidenceError):
            validate_evidence_contract(broken)

    def test_overwrite_is_forbidden(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["backend"]["overwrite"] = True
        with self.assertRaises(Phase6LiveEvidenceError):
            validate_evidence_contract(contract)

    def test_ephemeral_or_log_only_evidence_cannot_create_credit(self) -> None:
        for field in (
            "ephemeral_runner_files_create_credit",
            "step_summary_creates_credit",
            "logs_create_credit",
            "evidence_artifact_without_receipt_creates_credit",
            "expired_artifact_before_acceptance_review_creates_credit",
            "artifact_upload_failure_creates_credit",
            "receipt_upload_failure_creates_credit",
        ):
            contract = copy.deepcopy(self.contract)
            contract["credit_rules"][field] = True
            with self.subTest(field=field):
                with self.assertRaises(Phase6LiveEvidenceError):
                    validate_evidence_contract(contract)

    def test_retention_cannot_be_shortened(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["backend"]["retention_days"] = 14
        with self.assertRaises(Phase6LiveEvidenceError):
            validate_evidence_contract(contract)

    def test_receipt_must_bind_immutable_artifact_identity_and_phase6_digests(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["receipt"]["required_fields"].remove("evidence_object_digest")
        with self.assertRaises(Phase6LiveEvidenceError):
            validate_evidence_contract(contract)

        contract = copy.deepcopy(self.contract)
        contract["backend"]["required_upload_outputs"].remove("artifact-digest")
        with self.assertRaises(Phase6LiveEvidenceError):
            validate_evidence_contract(contract)


if __name__ == "__main__":
    unittest.main()
