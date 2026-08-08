from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .data_contract import (
    HISTORICAL_CUTOFF_UTC,
    PARSER_VERSION,
    parse_source_payload,
    select_frozen_historical_coverage,
    validate_frozen_contract,
)
from .raw_vintage import (
    DATASET_ID,
    SOURCE_ID,
    HttpCapture,
    SnapshotPaths,
    sha256_bytes,
    verify_snapshot,
    write_snapshot,
)
from .source_defillama import fetch_raw_snapshot

GATE_PATH = Path(__file__).with_name("CAPTURE_GATE.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_ID = "STABLECOIN-LIQUIDITY-0001-FIRST-CAPTURE-GATE-V1"
RESEARCH_ID = "STABLECOIN-LIQUIDITY-0001"
HISTORICAL_CLASSIFICATION = "RECONSTRUCTED_HISTORY_RESEARCHER_EXPOSED_HISTORY"
RESEARCH_RESULT_STATUS = "NO_RESEARCH_RESULT_CAPTURE_METADATA_ONLY"
PENDING_STATE = "PERSISTED_VERIFIED_AWAITING_DURABLE_RECEIPT"
DURABILITY_WRITE_SEMANTICS = "CREATE_ONLY_VERSIONED_COPY"


class CaptureGateError(RuntimeError):
    pass


@dataclass(frozen=True)
class CaptureStagingMetadata:
    schema_version: int
    gate_id: str
    research_id: str
    dataset_id: str
    source_id: str
    retrieved_at: str
    raw_sha256: str
    manifest_sha256: str
    raw_size_bytes: int
    raw_relative_path: str
    manifest_relative_path: str
    state: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CaptureMetadata:
    schema_version: int
    gate_id: str
    research_id: str
    dataset_id: str
    source_id: str
    retrieved_at: str
    raw_sha256: str
    manifest_sha256: str
    raw_size_bytes: int
    raw_row_count: int
    historical_row_count: int
    historical_start: str
    historical_end: str
    historical_cutoff: str
    historical_classification: str
    parser_version: str
    raw_relative_path: str
    manifest_relative_path: str
    durable_backend: str
    durable_raw_ref: str
    durable_manifest_ref: str
    durability_archived_at: str
    research_result_status: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _iso_z(value) -> str:
    return value.isoformat().replace("+00:00", "Z")


def load_capture_gate(path: Path = GATE_PATH) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_capture_gate_contract(contract: dict[str, object] | None = None) -> None:
    contract = contract or load_capture_gate()
    if contract.get("gate_id") != GATE_ID:
        raise CaptureGateError("unexpected capture gate id")
    if contract.get("research_id") != RESEARCH_ID:
        raise CaptureGateError("unexpected capture gate research id")
    if contract.get("status") != "FROZEN_NOT_EXECUTED":
        raise CaptureGateError("capture gate status drifted")
    if contract.get("production_authorized") is not False:
        raise CaptureGateError("capture gate cannot confer production authority")
    expected_sequence = [
        "FETCH_ONCE_FROM_FROZEN_SOURCE",
        "PERSIST_EXACT_RAW_BYTES_CREATE_ONLY",
        "PERSIST_MANIFEST_CREATE_ONLY",
        "VERIFY_RAW_HASH_AND_MANIFEST_IDENTITY",
        "ARCHIVE_RAW_AND_MANIFEST_TO_DURABLE_EXTERNAL_STORE",
        "CREATE_DURABILITY_RECEIPT_CREATE_ONLY",
        "VERIFY_DURABILITY_RECEIPT_IDENTITY",
        "PARSE_ONLY_THE_PERSISTED_VERIFIED_BYTES",
        "SELECT_FROZEN_HISTORICAL_COVERAGE",
        "EMIT_METADATA_ONLY",
    ]
    if contract.get("required_sequence") != expected_sequence:
        raise CaptureGateError("capture sequence drifted")
    allowed = contract.get("allowed_metadata_output_fields")
    if not isinstance(allowed, list) or set(allowed) != set(CaptureMetadata.__dataclass_fields__):
        raise CaptureGateError("metadata output contract drifted")
    staging = contract.get("allowed_staging_output_fields")
    if not isinstance(staging, list) or set(staging) != set(CaptureStagingMetadata.__dataclass_fields__):
        raise CaptureGateError("staging output contract drifted")


def _validated_storage_root(storage_root: Path) -> Path:
    storage_root = Path(storage_root)
    if not storage_root.is_absolute():
        raise CaptureGateError("storage root must be an absolute path")
    resolved = storage_root.resolve(strict=False)
    repo = REPO_ROOT.resolve(strict=False)
    if resolved == repo or repo in resolved.parents:
        raise CaptureGateError("storage root must be outside the repository")
    return resolved


def _capture_prefix(root: Path) -> Path:
    return root / "defillama_stablecoin_all_charts"


def _assert_no_prior_capture_artifact(root: Path) -> None:
    prefix = _capture_prefix(root)
    if prefix.exists() and any(path.is_file() for path in prefix.rglob("*")):
        raise CaptureGateError(
            "existing first-capture artifact detected; do not fetch again until manual reconciliation"
        )


def _snapshot_paths_from_staging(root: Path, staging: CaptureStagingMetadata) -> SnapshotPaths:
    raw_path = root / staging.raw_relative_path
    manifest_path = root / staging.manifest_relative_path
    return SnapshotPaths(raw_path=raw_path, manifest_path=manifest_path)


def capture_and_persist_first_history(
    storage_root: Path,
    fetcher: Callable[[], HttpCapture] = fetch_raw_snapshot,
) -> CaptureStagingMetadata:
    """Fetch exactly once, persist+verify, and stop before parsing."""
    validate_frozen_contract()
    validate_capture_gate_contract()
    root = _validated_storage_root(Path(storage_root))
    _assert_no_prior_capture_artifact(root)

    capture = fetcher()
    paths = write_snapshot(root, capture)
    manifest = verify_snapshot(paths)
    manifest_sha256 = sha256_bytes(paths.manifest_path.read_bytes())
    raw_relative = str(manifest["raw_relative_path"])
    manifest_relative = paths.manifest_path.relative_to(root).as_posix()
    return CaptureStagingMetadata(
        schema_version=1,
        gate_id=GATE_ID,
        research_id=RESEARCH_ID,
        dataset_id=DATASET_ID,
        source_id=SOURCE_ID,
        retrieved_at=str(manifest["retrieved_at"]),
        raw_sha256=str(manifest["raw_sha256"]),
        manifest_sha256=manifest_sha256,
        raw_size_bytes=int(manifest["raw_size_bytes"]),
        raw_relative_path=raw_relative,
        manifest_relative_path=manifest_relative,
        state=PENDING_STATE,
    )


def write_durability_receipt(
    receipt_path: Path,
    staging: CaptureStagingMetadata,
    *,
    durable_backend: str,
    durable_raw_ref: str,
    durable_manifest_ref: str,
    archived_at: str,
) -> Path:
    if staging.state != PENDING_STATE:
        raise CaptureGateError("staging state is not awaiting durable receipt")
    values = {
        "durable_backend": durable_backend,
        "durable_raw_ref": durable_raw_ref,
        "durable_manifest_ref": durable_manifest_ref,
        "archived_at": archived_at,
    }
    if any(not isinstance(v, str) or not v.strip() for v in values.values()):
        raise CaptureGateError("durability receipt fields must be non-empty strings")
    receipt = {
        "schema_version": 1,
        "gate_id": staging.gate_id,
        "research_id": staging.research_id,
        "dataset_id": staging.dataset_id,
        "source_id": staging.source_id,
        "raw_sha256": staging.raw_sha256,
        "manifest_sha256": staging.manifest_sha256,
        "raw_relative_path": staging.raw_relative_path,
        "manifest_relative_path": staging.manifest_relative_path,
        "durable_backend": durable_backend,
        "durable_raw_ref": durable_raw_ref,
        "durable_manifest_ref": durable_manifest_ref,
        "archived_at": archived_at,
        "write_semantics": DURABILITY_WRITE_SEMANTICS,
    }
    path = Path(receipt_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        raise
    return path


def finalize_after_durable_copy(
    storage_root: Path,
    staging: CaptureStagingMetadata,
    durability_receipt_path: Path,
) -> CaptureMetadata:
    """Verify durable-copy receipt, then and only then parse persisted raw bytes."""
    validate_frozen_contract()
    validate_capture_gate_contract()
    root = _validated_storage_root(Path(storage_root))
    paths = _snapshot_paths_from_staging(root, staging)
    manifest = verify_snapshot(paths)
    if sha256_bytes(paths.manifest_path.read_bytes()) != staging.manifest_sha256:
        raise CaptureGateError("staging manifest SHA256 mismatch")

    receipt = json.loads(Path(durability_receipt_path).read_text(encoding="utf-8"))
    expected = {
        "schema_version": 1,
        "gate_id": staging.gate_id,
        "research_id": staging.research_id,
        "dataset_id": staging.dataset_id,
        "source_id": staging.source_id,
        "raw_sha256": staging.raw_sha256,
        "manifest_sha256": staging.manifest_sha256,
        "raw_relative_path": staging.raw_relative_path,
        "manifest_relative_path": staging.manifest_relative_path,
        "write_semantics": DURABILITY_WRITE_SEMANTICS,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise CaptureGateError(f"durability receipt {key} mismatch")
    for key in ("durable_backend", "durable_raw_ref", "durable_manifest_ref", "archived_at"):
        value = receipt.get(key)
        if not isinstance(value, str) or not value.strip():
            raise CaptureGateError(f"durability receipt missing {key}")

    persisted_raw = paths.raw_path.read_bytes()
    points = parse_source_payload(persisted_raw)
    historical = select_frozen_historical_coverage(points)
    if not points:
        raise CaptureGateError("source returned no schema-valid rows")
    if not historical:
        raise CaptureGateError("source returned no rows inside frozen historical coverage")

    return CaptureMetadata(
        schema_version=1,
        gate_id=GATE_ID,
        research_id=RESEARCH_ID,
        dataset_id=DATASET_ID,
        source_id=SOURCE_ID,
        retrieved_at=str(manifest["retrieved_at"]),
        raw_sha256=str(manifest["raw_sha256"]),
        manifest_sha256=staging.manifest_sha256,
        raw_size_bytes=int(manifest["raw_size_bytes"]),
        raw_row_count=len(points),
        historical_row_count=len(historical),
        historical_start=_iso_z(historical[0].metric_timestamp),
        historical_end=_iso_z(historical[-1].metric_timestamp),
        historical_cutoff=_iso_z(HISTORICAL_CUTOFF_UTC),
        historical_classification=HISTORICAL_CLASSIFICATION,
        parser_version=PARSER_VERSION,
        raw_relative_path=staging.raw_relative_path,
        manifest_relative_path=staging.manifest_relative_path,
        durable_backend=str(receipt["durable_backend"]),
        durable_raw_ref=str(receipt["durable_raw_ref"]),
        durable_manifest_ref=str(receipt["durable_manifest_ref"]),
        durability_archived_at=str(receipt["archived_at"]),
        research_result_status=RESEARCH_RESULT_STATUS,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Two-stage Stablecoin first historical capture gate")
    parser.add_argument("--storage-root", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture-only", action="store_true")
    mode.add_argument("--finalize-after-durable-copy", action="store_true")
    parser.add_argument(
        "--execute-live-capture",
        action="store_true",
        help="Explicitly authorize the one-shot network fetch from the frozen source.",
    )
    parser.add_argument("--staging-json", type=Path)
    parser.add_argument("--durability-receipt", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.capture_only:
        if not args.execute_live_capture:
            raise CaptureGateError("live capture blocked: explicit --execute-live-capture is required")
        staging = capture_and_persist_first_history(args.storage_root)
        print(json.dumps(staging.as_dict(), sort_keys=True, separators=(",", ":")))
        return 0

    if args.staging_json is None or args.durability_receipt is None:
        raise CaptureGateError("finalize requires --staging-json and --durability-receipt")
    staging_payload = json.loads(args.staging_json.read_text(encoding="utf-8"))
    staging = CaptureStagingMetadata(**staging_payload)
    metadata = finalize_after_durable_copy(args.storage_root, staging, args.durability_receipt)
    print(json.dumps(metadata.as_dict(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
