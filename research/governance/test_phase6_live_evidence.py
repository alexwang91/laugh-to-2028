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

    def test_repository_contract_is_frozen_but_not_collecting(self) -> None:
        snapshot = validate_evidence_contract(self.contract)
        self.assertEqual(snapshot["backend"], "GITHUB_ACTIONS_ARTIFACT_V4")
        self.assertEqual(snapshot["retention_days"], 90)
        self.assertFalse(snapshot["overwrite"])
        self.assertFalse(snapshot["credit_active"])
        self.assertFalse(snapshot["production_authorized"])

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

    def test_backend_contract_does_not_select_account_or_arm_collector(self) -> None:
        expected = {
            "NO_ACCOUNT_IDENTITY_SELECTION",
            "NO_POSITION_OR_EQUITY_VALUATION_CHANGE",
            "NO_SCHEDULE_ARM",
            "NO_ELAPSED_EVIDENCE_CREDIT",
            "NO_SIGNING",
            "NO_ORDER_SUBMISSION",
            "NO_PRODUCTION_AUTHORIZATION",
        }
        self.assertEqual(set(self.contract["explicit_non_actions"]), expected)


if __name__ == "__main__":
    unittest.main()
