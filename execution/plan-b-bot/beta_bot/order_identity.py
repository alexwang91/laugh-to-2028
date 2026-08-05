from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


CLOID_PERSON = b"brrk-order-v1"
TARGET_QTY_DECIMALS = 5
VALID_SIDES = {"buy", "sell"}
VALID_INTENTS = {"increase", "reduce"}


def canonical_target_revision(target_qty: float, decimals: int = TARGET_QTY_DECIMALS) -> str:
    """Return the economic target revision at executable position precision.

    The identity is target-centric rather than delta-centric. A process restart after a
    fill changes current_qty, but the same desired target must retain the same identity.
    Rounding deliberately matches the current executor's order-size rounding semantics.
    """
    if decimals < 0:
        raise ValueError("decimals must be non-negative")
    rounded = round(float(target_qty), decimals)
    if rounded == 0:
        rounded = 0.0
    return f"target_qty:{rounded:.{decimals}f}"


@dataclass(frozen=True)
class OrderIdentity:
    schema_version: int
    release_id: str
    decision_timestamp_ms: int
    asset: str
    side: str
    intent: str
    target_revision: str
    cloid: str

    def to_dict(self) -> dict:
        return asdict(self)


def build_order_identity(
    *,
    release_id: str,
    decision_timestamp_ms: int,
    asset: str,
    side: str,
    intent: str,
    target_revision: str,
) -> OrderIdentity:
    release = release_id.strip()
    normalized_asset = asset.strip().upper()
    normalized_side = side.strip().lower()
    normalized_intent = intent.strip().lower()
    revision = target_revision.strip()

    if not release:
        raise ValueError("release_id is required for deterministic order identity")
    if decision_timestamp_ms <= 0:
        raise ValueError("decision_timestamp_ms must be positive")
    if not normalized_asset:
        raise ValueError("asset is required")
    if normalized_side not in VALID_SIDES:
        raise ValueError(f"Unsupported side: {side}")
    if normalized_intent not in VALID_INTENTS:
        raise ValueError(f"Unsupported intent: {intent}")
    if not revision:
        raise ValueError("target_revision is required")

    canonical = {
        "schema_version": 1,
        "release_id": release,
        "decision_timestamp_ms": int(decision_timestamp_ms),
        "asset": normalized_asset,
        "side": normalized_side,
        "intent": normalized_intent,
        "target_revision": revision,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.blake2b(encoded, digest_size=16, person=CLOID_PERSON).hexdigest()

    return OrderIdentity(
        **canonical,
        cloid=f"0x{digest}",
    )
