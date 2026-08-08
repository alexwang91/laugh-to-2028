from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.governance.phase6_live_account_identity import (
    Phase6AccountIdentityError,
    validate_identity_contract,
    verify_identity_observation,
)

ROOT = Path(__file__).resolve().parents[2]
MASTER = "0x1111111111111111111111111111111111111111"
SUBACCOUNT = "0x2222222222222222222222222222222222222222"
AGENT = "0x3333333333333333333333333333333333333333"


class Phase6LiveAccountIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(
            (ROOT / "research/governance/phase6_live_account_identity_contract.json").read_text(
                encoding="utf-8"
            )
        )

    def test_repository_contract_freezes_rules_not_identity(self) -> None:
        snapshot = validate_identity_contract(self.contract)
        self.assertEqual(snapshot["status"], "AWAITING_EXPLICIT_PUBLIC_ADDRESS")
        self.assertIsNone(snapshot["account_address"])
        self.assertFalse(snapshot["identity_frozen"])
        self.assertFalse(snapshot["binding_ready"])
        self.assertFalse(snapshot["production_authorized"])
        self.assertFalse(snapshot["signature_authorized"])
        self.assertFalse(snapshot["order_submission_authorized"])
        self.assertFalse(snapshot["elapsed_evidence_credit_authorized"])

    def test_master_user_role_with_disabled_abstraction_is_compatible(self) -> None:
        observed = verify_identity_observation(
            account_address=MASTER,
            user_role_response={"role": "user"},
            user_abstraction_response="disabled",
        )
        self.assertEqual(observed["role"], "user")
        self.assertIsNone(observed["master_address"])
        self.assertTrue(observed["identity_compatible"])

    def test_subaccount_is_observed_directly_and_requires_master_evidence(self) -> None:
        observed = verify_identity_observation(
            account_address=SUBACCOUNT,
            user_role_response={"role": "subAccount", "data": {"master": MASTER}},
            user_abstraction_response="disabled",
        )
        self.assertEqual(observed["account_address"], SUBACCOUNT)
        self.assertEqual(observed["master_address"], MASTER)

        with self.assertRaises(Phase6AccountIdentityError):
            verify_identity_observation(
                account_address=SUBACCOUNT,
                user_role_response={"role": "subAccount", "data": {}},
                user_abstraction_response="disabled",
            )

    def test_agent_vault_missing_and_unknown_roles_fail_closed(self) -> None:
        for role in ("agent", "vault", "missing", "somethingElse"):
            with self.subTest(role=role):
                with self.assertRaises(Phase6AccountIdentityError):
                    verify_identity_observation(
                        account_address=AGENT,
                        user_role_response={"role": role},
                        user_abstraction_response="disabled",
                    )

    def test_unsupported_account_abstraction_fails_closed(self) -> None:
        for mode in ("unifiedAccount", "portfolioMargin", "default", None):
            with self.subTest(mode=mode):
                with self.assertRaises(Phase6AccountIdentityError):
                    verify_identity_observation(
                        account_address=MASTER,
                        user_role_response={"role": "user"},
                        user_abstraction_response=mode,
                    )

    def test_address_must_be_exact_42_character_hex(self) -> None:
        for value in ("", "0x1234", "1111111111111111111111111111111111111111", "0x" + "z" * 40):
            with self.subTest(value=value):
                with self.assertRaises(Phase6AccountIdentityError):
                    verify_identity_observation(
                        account_address=value,
                        user_role_response={"role": "user"},
                        user_abstraction_response="disabled",
                    )

    def test_contract_cannot_claim_frozen_identity_without_address(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["identity_frozen"] = True
        with self.assertRaises(Phase6AccountIdentityError):
            validate_identity_contract(contract)

    def test_contract_cannot_claim_binding_evidence_while_unbound(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["address_source"] = "made-up"
        with self.assertRaises(Phase6AccountIdentityError):
            validate_identity_contract(contract)

    def test_future_bound_master_fixture_requires_role_mode_and_raw_digests(self) -> None:
        contract = copy.deepcopy(self.contract)
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
        snapshot = validate_identity_contract(contract)
        self.assertTrue(snapshot["identity_frozen"])
        self.assertTrue(snapshot["binding_ready"])
        self.assertEqual(snapshot["account_address"], MASTER)
        self.assertEqual(snapshot["account_role"], "user")

        broken = copy.deepcopy(contract)
        broken["binding_evidence"]["user_role_response"] = {"role": "agent", "data": {"user": MASTER}}
        with self.assertRaises(Phase6AccountIdentityError):
            validate_identity_contract(broken)

        broken = copy.deepcopy(contract)
        broken["binding_evidence"]["raw_response_sha256"]["userRole"] = "not-a-digest"
        with self.assertRaises(Phase6AccountIdentityError):
            validate_identity_contract(broken)

    def test_contract_cannot_confer_authority(self) -> None:
        for field in (
            "production_authorized",
            "signature_authorized",
            "order_submission_authorized",
            "elapsed_evidence_credit_authorized",
        ):
            contract = copy.deepcopy(self.contract)
            contract[field] = True
            with self.subTest(field=field):
                with self.assertRaises(Phase6AccountIdentityError):
                    validate_identity_contract(contract)


if __name__ == "__main__":
    unittest.main()
