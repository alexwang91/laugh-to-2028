"""History-agnostic create-only persistence primitives for BRRK 0084 Stage4.

The functions in this module perform no file or network I/O. Stage5 can qualify
serialization and accounting behavior entirely with synthetic fixtures. Stage8
may only call an external create-only writer after its durable attempt marker
exists and after the single scientific-engine invocation has completed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping

RESEARCH_ID = "BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084"
DECLARED_TRIALS = 64
ATTEMPT_BUDGET = 1
SCIENTIFIC_ENGINE_BUDGET = 1
SOURCE_NETWORK_FETCH_BUDGET = 0


@dataclass(frozen=True)
class ExecutionCounters:
    attempt_markers_created: int
    controlled_objects_authorized: int
    controlled_object_reads: Mapping[str, int]
    scientific_engine_calls: int
    scientific_source_network_fetches: int
    declared_trials: int

    def validate_pre_attempt(self) -> None:
        if self.attempt_markers_created != 0:
            raise ValueError("pre-attempt state must have zero attempt markers")
        if any(int(v) != 0 for v in self.controlled_object_reads.values()):
            raise ValueError("pre-attempt state must have zero controlled reads")
        if self.scientific_engine_calls != 0:
            raise ValueError("pre-attempt state must have zero scientific-engine calls")
        if self.scientific_source_network_fetches != 0:
            raise ValueError("scientific source-network fetch budget is zero")
        if self.declared_trials != DECLARED_TRIALS:
            raise ValueError("declared trial accounting drift")

    def validate_terminal(self) -> None:
        if self.attempt_markers_created != ATTEMPT_BUDGET:
            raise ValueError("terminal execution requires exactly one attempt marker")
        if self.controlled_objects_authorized < 0:
            raise ValueError("negative authorized-object count")
        if len(self.controlled_object_reads) != self.controlled_objects_authorized:
            raise ValueError("read-ledger object cardinality drift")
        if any(int(v) not in (0, 1) for v in self.controlled_object_reads.values()):
            raise ValueError("each authorized object may be read at most once")
        if self.scientific_engine_calls != SCIENTIFIC_ENGINE_BUDGET:
            raise ValueError("terminal execution requires exactly one scientific-engine call")
        if self.scientific_source_network_fetches != SOURCE_NETWORK_FETCH_BUDGET:
            raise ValueError("scientific source-network fetch budget is zero")
        if self.declared_trials != DECLARED_TRIALS:
            raise ValueError("declared trial accounting drift")


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize deterministic UTF-8 JSON suitable for create-only result files."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def build_result_bundle(
    *,
    classification: str,
    counters: ExecutionCounters,
    trial_results: Iterable[Mapping[str, Any]],
    gate_summary: Mapping[str, Any],
    provenance: Mapping[str, Any],
) -> tuple[bytes, str]:
    """Build a canonical create-only result payload and its SHA-256 digest.

    This function deliberately does not write the payload. The caller must use
    a create-only writer and must refuse to overwrite any existing result path.
    """
    allowed = {
        "PASS",
        "FAIL_NO_QUALIFIED_FACTOR",
        "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
        "INVALID_EXECUTION",
    }
    if classification not in allowed:
        raise ValueError("unknown terminal classification")
    counters.validate_terminal()
    trials = list(trial_results)
    if len(trials) != DECLARED_TRIALS:
        raise ValueError("result bundle must contain exactly 64 declared trials")
    payload = {
        "research_id": RESEARCH_ID,
        "classification": classification,
        "execution_counters": asdict(counters),
        "gate_summary": dict(gate_summary),
        "provenance": dict(provenance),
        "trial_results": trials,
    }
    encoded = canonical_json_bytes(payload)
    return encoded, sha256_hex(encoded)


def validate_create_only_targets(existing_paths: Iterable[str], new_paths: Iterable[str]) -> tuple[str, ...]:
    existing = set(existing_paths)
    targets = tuple(new_paths)
    if not targets:
        raise ValueError("at least one create-only target is required")
    if len(set(targets)) != len(targets):
        raise ValueError("duplicate create-only target")
    collisions = sorted(existing.intersection(targets))
    if collisions:
        raise FileExistsError(f"create-only target already exists: {collisions}")
    return targets
