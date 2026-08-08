from __future__ import annotations

import argparse
import json
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
from .raw_vintage import DATASET_ID, SOURCE_ID, HttpCapture, verify_snapshot, write_snapshot
from .source_defillama import fetch_raw_snapshot

GATE_PATH = Path(__file__).with_name("CAPTURE_GATE.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_ID = "STABLECOIN-LIQUIDITY-0001-FIRST-CAPTURE-GATE-V1"
RESEARCH_ID = "STABLECOIN-LIQUIDITY-0001"
HISTORICAL_CLASSIFICATION = "RECONSTRUCTED_HISTORY_RESEARCHER_EXPOSED_HISTORY"
RESEARCH_RESULT_STATUS = "NO_RESEARCH_RESULT_CAPTURE_METADATA_ONLY"


class CaptureGateError(RuntimeError):
    pass


@dataclass(frozen=True)
class CaptureMetadata:
    schema_version: int
    gate_id: str
    research_id: str
    dataset_id: str
    source_id: str
    retrieved_at: str
    raw_sha256: str
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
        "PARSE_ONLY_THE_PERSISTED_VERIFIED_BYTES",
        "SELECT_FROZEN_HISTORICAL_COVERAGE",
        "EMIT_METADATA_ONLY",
    ]
    if contract.get("required_sequence") != expected_sequence:
        raise CaptureGateError("capture sequence drifted")
    allowed = contract.get("allowed_metadata_output_fields")
    if not isinstance(allowed, list) or set(allowed) != set(CaptureMetadata.__dataclass_fields__):
        raise CaptureGateError("metadata output contract drifted")


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


def execute_first_history_capture(
    storage_root: Path,
    fetcher: Callable[[], HttpCapture] = fetch_raw_snapshot,
) -> CaptureMetadata:
    """Execute the first capture gate without computing features or results.

    The order is intentionally strict: fetch once, persist exact bytes and
    manifest, verify the persisted snapshot, then parse those persisted bytes.
    The returned object contains provenance/coverage metadata only.
    """
    validate_frozen_contract()
    validate_capture_gate_contract()
    root = _validated_storage_root(Path(storage_root))
    _assert_no_prior_capture_artifact(root)

    capture = fetcher()
    paths = write_snapshot(root, capture)
    manifest = verify_snapshot(paths)

    # Downstream parsing must use the persisted, verified bytes rather than the
    # in-memory HTTP response so that provenance and interpretation cannot split.
    persisted_raw = paths.raw_path.read_bytes()
    points = parse_source_payload(persisted_raw)
    historical = select_frozen_historical_coverage(points)
    if not points:
        raise CaptureGateError("source returned no schema-valid rows")
    if not historical:
        raise CaptureGateError("source returned no rows inside frozen historical coverage")

    raw_relative = str(manifest["raw_relative_path"])
    manifest_relative = paths.manifest_path.relative_to(root).as_posix()
    return CaptureMetadata(
        schema_version=1,
        gate_id=GATE_ID,
        research_id=RESEARCH_ID,
        dataset_id=DATASET_ID,
        source_id=SOURCE_ID,
        retrieved_at=str(manifest["retrieved_at"]),
        raw_sha256=str(manifest["raw_sha256"]),
        raw_size_bytes=int(manifest["raw_size_bytes"]),
        raw_row_count=len(points),
        historical_row_count=len(historical),
        historical_start=_iso_z(historical[0].metric_timestamp),
        historical_end=_iso_z(historical[-1].metric_timestamp),
        historical_cutoff=_iso_z(HISTORICAL_CUTOFF_UTC),
        historical_classification=HISTORICAL_CLASSIFICATION,
        parser_version=PARSER_VERSION,
        raw_relative_path=raw_relative,
        manifest_relative_path=manifest_relative,
        research_result_status=RESEARCH_RESULT_STATUS,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="First Stablecoin historical capture gate")
    parser.add_argument("--storage-root", type=Path, required=True)
    parser.add_argument(
        "--execute-live-capture",
        action="store_true",
        help="Explicitly authorize the one-shot network fetch from the frozen source.",
    )
    parser.add_argument(
        "--durable-storage-attested",
        action="store_true",
        help="Attest that storage-root is a durable external create-only/versioned location.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.execute_live_capture:
        raise CaptureGateError("live capture blocked: explicit --execute-live-capture is required")
    if not args.durable_storage_attested:
        raise CaptureGateError("live capture blocked: --durable-storage-attested is required")
    metadata = execute_first_history_capture(args.storage_root)
    print(json.dumps(metadata.as_dict(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
