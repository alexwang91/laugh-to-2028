from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .validate import repo_root_from_module

CONTRACT_RELATIVE_PATH = Path("research/governance/phase6_live_account_identity_contract.json")
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ACCEPTED_ROLES = ("user", "subAccount")
REJECTED_ROLES = ("agent", "vault", "missing")


class Phase6AccountIdentityError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase6AccountIdentityError(f"{path} must contain a JSON object")
    return value


def _validate_address(value: object, *, field: str) -> str:
    if not isinstance(value, str) or ADDRESS_RE.fullmatch(value) is None:
        raise Phase6AccountIdentityError(f"{field} must be a 42-character 0x hexadecimal address")
    return value


def _validate_utc_timestamp(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise Phase6AccountIdentityError(f"{field} must be an ISO-8601 UTC string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Phase6AccountIdentityError(f"{field} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise Phase6AccountIdentityError(f"{field} must be UTC")
    return value


def verify_identity_observation(
    *,
    account_address: str,
    user_role_response: Mapping[str, Any],
    user_abstraction_response: object,
) -> dict[str, Any]:
    """Validate read-only Hyperliquid identity observations without signing or mutation."""
    address = _validate_address(account_address, field="account_address")
    if not isinstance(user_role_response, Mapping):
        raise Phase6AccountIdentityError("userRole response must be an object")
    role = user_role_response.get("role")
    if role not in ACCEPTED_ROLES:
        if role in REJECTED_ROLES:
            raise Phase6AccountIdentityError(f"observation identity role is forbidden: {role}")
        raise Phase6AccountIdentityError(f"unexpected observation identity role: {role}")
    if user_abstraction_response != "disabled":
        raise Phase6AccountIdentityError(
            "observation account must use explicit Standard/disabled userAbstraction"
        )

    master_address: str | None = None
    if role == "subAccount":
        data = user_role_response.get("data")
        if not isinstance(data, Mapping):
            raise Phase6AccountIdentityError("subAccount userRole must include data")
        master_address = _validate_address(data.get("master"), field="userRole.data.master")
        if master_address.lower() == address.lower():
            raise Phase6AccountIdentityError("subAccount master must differ from the subaccount address")

    return {
        "account_address": address,
        "account_address_lower": address.lower(),
        "role": role,
        "master_address": master_address,
        "user_abstraction": "disabled",
        "identity_compatible": True,
    }


def validate_identity_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    if contract.get("schema_version") != 1:
        raise Phase6AccountIdentityError("unsupported account identity contract schema")
    if contract.get("contract_id") != "PHASE6-LIVE-ACCOUNT-IDENTITY-V1":
        raise Phase6AccountIdentityError("unexpected account identity contract id")
    if contract.get("venue") != "hyperliquid":
        raise Phase6AccountIdentityError("account identity venue must remain hyperliquid")
    if contract.get("info_endpoint") != "https://api.hyperliquid.xyz/info":
        raise Phase6AccountIdentityError("account identity source endpoint drift")
    if contract.get("address_format") != "0x_PLUS_40_HEX_CHARS":
        raise Phase6AccountIdentityError("account address format drift")

    for field in (
        "production_authorized",
        "signature_authorized",
        "order_submission_authorized",
        "elapsed_evidence_credit_authorized",
    ):
        if contract.get(field) is not False:
            raise Phase6AccountIdentityError(f"{field} must remain false")

    required = contract.get("required_queries")
    if not isinstance(required, Mapping):
        raise Phase6AccountIdentityError("required_queries must be an object")
    role_rule = required.get("user_role")
    abstraction_rule = required.get("user_abstraction")
    if not isinstance(role_rule, Mapping) or not isinstance(abstraction_rule, Mapping):
        raise Phase6AccountIdentityError("both userRole and userAbstraction rules are required")
    if role_rule.get("request_type") != "userRole":
        raise Phase6AccountIdentityError("userRole request type drift")
    if tuple(role_rule.get("accepted_roles", [])) != ACCEPTED_ROLES:
        raise Phase6AccountIdentityError("accepted userRole set drift")
    if tuple(role_rule.get("rejected_roles", [])) != REJECTED_ROLES:
        raise Phase6AccountIdentityError("rejected userRole set drift")
    if abstraction_rule.get("request_type") != "userAbstraction":
        raise Phase6AccountIdentityError("userAbstraction request type drift")
    if abstraction_rule.get("required_value") != "disabled":
        raise Phase6AccountIdentityError("identity contract must require Standard/disabled abstraction")

    subaccount = contract.get("subaccount_policy")
    if not isinstance(subaccount, Mapping):
        raise Phase6AccountIdentityError("subaccount policy is required")
    if subaccount.get("subaccount_address_may_be_observed_directly") is not True:
        raise Phase6AccountIdentityError("subaccount direct observation rule drift")
    if subaccount.get("returned_master_address_required_for_subaccount") is not True:
        raise Phase6AccountIdentityError("subaccount master-evidence rule drift")
    if subaccount.get("silent_substitution_to_master_for_observation") is not False:
        raise Phase6AccountIdentityError("silent master substitution must remain forbidden")

    account_address = contract.get("account_address")
    identity_frozen = contract.get("identity_frozen") is True
    binding = contract.get("binding_evidence")
    address_source = contract.get("address_source")

    if account_address is None:
        if contract.get("status") != "AWAITING_EXPLICIT_PUBLIC_ADDRESS":
            raise Phase6AccountIdentityError("unbound identity must remain awaiting explicit public address")
        if identity_frozen:
            raise Phase6AccountIdentityError("identity cannot be frozen without an account address")
        if address_source is not None or binding is not None:
            raise Phase6AccountIdentityError("unbound identity cannot carry source or binding evidence")
        return {
            "contract_id": contract["contract_id"],
            "status": contract["status"],
            "account_address": None,
            "identity_frozen": False,
            "binding_ready": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
            "elapsed_evidence_credit_authorized": False,
        }

    address = _validate_address(account_address, field="account_address")
    if contract.get("status") != "FROZEN_VERIFIED_READ_ONLY_IDENTITY":
        raise Phase6AccountIdentityError("bound identity status must be FROZEN_VERIFIED_READ_ONLY_IDENTITY")
    if not identity_frozen:
        raise Phase6AccountIdentityError("bound verified identity must set identity_frozen=true")
    if not isinstance(address_source, str) or not address_source.strip():
        raise Phase6AccountIdentityError("bound identity requires non-secret address provenance")
    if not isinstance(binding, Mapping):
        raise Phase6AccountIdentityError("bound identity requires binding evidence")
    if str(binding.get("query_address", "")).lower() != address.lower():
        raise Phase6AccountIdentityError("binding evidence query address must match account_address")

    observation = verify_identity_observation(
        account_address=address,
        user_role_response=binding.get("user_role_response", {}),
        user_abstraction_response=binding.get("user_abstraction_response"),
    )
    _validate_utc_timestamp(binding.get("verified_at"), field="binding_evidence.verified_at")
    digests = binding.get("raw_response_sha256")
    if not isinstance(digests, Mapping) or set(digests) != {"userRole", "userAbstraction"}:
        raise Phase6AccountIdentityError("binding evidence requires exact userRole/userAbstraction raw digests")
    for name, digest in digests.items():
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise Phase6AccountIdentityError(f"invalid SHA256 digest for {name}")

    return {
        "contract_id": contract["contract_id"],
        "status": contract["status"],
        "account_address": address,
        "account_role": observation["role"],
        "master_address": observation["master_address"],
        "identity_frozen": True,
        "binding_ready": True,
        "user_abstraction": "disabled",
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "elapsed_evidence_credit_authorized": False,
    }


def contract_snapshot(root: Path | None = None) -> dict[str, Any]:
    repo_root = Path(root or repo_root_from_module())
    return validate_identity_contract(_load_json(repo_root / CONTRACT_RELATIVE_PATH))


def main() -> int:
    print(json.dumps(contract_snapshot(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
