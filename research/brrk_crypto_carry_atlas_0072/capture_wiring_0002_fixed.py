from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime, timezone

import capture_wiring_0002 as base

SOURCE_CONTRACT_ID = "BRRK-CRYPTO-CARRY-ATLAS-0072-SOURCE-IDENTITY-V1"
SPOT_FAMILY = "spot/monthly/klines"
FUTURES_FAMILIES = {
    "futures/um/monthly/klines",
    "futures/um/monthly/markPriceKlines",
    "futures/um/monthly/indexPriceKlines",
    "futures/um/monthly/premiumIndexKlines",
}
_ORIGINAL_VALIDATE_CONTRACT_DATA = base._validate_contract_data


def _validate_contract_data_fixed(request: dict, plan: dict, source: dict, amendment: dict) -> None:
    """Validate the frozen source contract using its actual canonical field name."""
    if source.get("research_id") != base.RID or source.get("contract_id") != SOURCE_CONTRACT_ID:
        raise base.CaptureError("SOURCE_CONTRACT_DRIFT")
    compatible_source = dict(source)
    compatible_source["identity_contract_id"] = compatible_source["contract_id"]
    _ORIGINAL_VALIDATE_CONTRACT_DATA(request, plan, compatible_source, amendment)


def _timestamp_divisor(archive_family: str) -> int:
    if archive_family == SPOT_FAMILY:
        return 1_000_000
    if archive_family in FUTURES_FAMILIES:
        return 1_000
    raise base.CaptureError("TIMESTAMP_UNIT_FAMILY_DRIFT")


def _timestamp_bounds(rows: list[list[str]], archive_family: str) -> tuple[str | None, str | None]:
    values = []
    for row in rows:
        if not row:
            continue
        try:
            value = int(row[0])
        except (TypeError, ValueError):
            continue
        values.append(value)
    if not values:
        return None, None
    if len(values) != len(set(values)) or values != sorted(values):
        raise base.CaptureError("DUPLICATE_OR_NON_MONOTONE_TIMESTAMP")

    divisor = _timestamp_divisor(archive_family)
    if archive_family == SPOT_FAMILY:
        if any(value < 1_000_000_000_000_000 or value >= 10_000_000_000_000_000 for value in values):
            raise base.CaptureError("TIMESTAMP_UNIT_DRIFT")
    else:
        if any(value < 1_000_000_000_000 or value >= 10_000_000_000_000 for value in values):
            raise base.CaptureError("TIMESTAMP_UNIT_DRIFT")

    converted = [
        datetime.fromtimestamp(value / divisor, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        for value in values
    ]
    return converted[0], converted[-1]


def _parse_archive_metadata(raw: bytes, archive_family: str) -> tuple[int, str | None, str | None, dict, dict, str, str | None]:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
            if len(names) != 1:
                raise base.CaptureError("SCHEMA_DRIFT")
            text = archive.read(names[0]).decode("utf-8")
    except base.CaptureError:
        raise
    except Exception as exc:
        raise base.CaptureError("SCHEMA_DRIFT") from exc

    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return 0, None, None, {}, {}, "FAIL", "SCHEMA_DRIFT"
    data_rows = rows
    try:
        int(rows[0][0])
    except (IndexError, TypeError, ValueError):
        data_rows = rows[1:]
    if not data_rows or max((len(row) for row in data_rows), default=0) < 6:
        return 0, None, None, {}, {}, "FAIL", "SCHEMA_DRIFT"

    width = max(len(row) for row in data_rows)
    field_types = {f"col_{idx}": "str" for idx in range(width)}
    missingness = {
        f"col_{idx}": sum(idx >= len(row) or row[idx] == "" for row in data_rows)
        for idx in range(width)
    }
    lo, hi = _timestamp_bounds(data_rows, archive_family)
    if lo is None or hi is None:
        return len(data_rows), None, None, field_types, missingness, "FAIL", "POINT_IN_TIME_SEMANTICS_UNPROVABLE"
    return len(data_rows), lo, hi, field_types, missingness, "PASS", None


def finalize(storage, staging: dict, receipt_path, *, git: bool = True) -> dict:
    plan = base.validate_contract(git=git)
    root = base.capture_root(storage)
    saved = base.load(root / "STAGING_MANIFEST.json")
    if saved != staging:
        raise base.CaptureError("RAW_HASH_MISMATCH")
    unsigned = dict(staging)
    manifest_hash = unsigned.pop("manifest_sha256")
    if base.sha256_bytes(base.canon(unsigned)) != manifest_hash:
        raise base.CaptureError("RAW_HASH_MISMATCH")

    receipt = base.load(receipt_path)
    required = {
        "research_id": base.RID,
        "capture_request_id": base.CID,
        "plan_id": base.PLAN_ID,
        "manifest_sha256": staging["manifest_sha256"],
        "aggregate_raw_sha256": staging["aggregate_raw_sha256"],
        "archive_object_count": 15,
        "checksum_object_count": 15,
        "network_object_count_total": 30,
        "write_semantics": "CREATE_ONLY_VERSIONED_COPY_OVERWRITE_FALSE",
    }
    for key, expected in required.items():
        if receipt.get(key) != expected:
            raise base.CaptureError("RAW_HASH_MISMATCH")

    plan_by_id = {row["object_id"]: row for row in plan["objects"]}
    metadata = []
    for pair in staging["pairs"]:
        row = plan_by_id[pair["canonical_request_id"]]
        archive_path = root / pair["archive_raw_locator"]
        checksum_path = root / pair["checksum_raw_locator"]
        archive_raw = archive_path.read_bytes()
        checksum_raw = checksum_path.read_bytes()
        if base.sha256_bytes(archive_raw) != pair["archive_raw_sha256"] or base.sha256_bytes(checksum_raw) != pair["checksum_raw_sha256"]:
            raise base.CaptureError("RAW_HASH_MISMATCH")
        if base._checksum_token(checksum_raw) != pair["archive_raw_sha256"]:
            raise base.CaptureError("CHECKSUM_MISMATCH")

        row_count, lo, hi, field_types, missingness, status, failure = _parse_archive_metadata(
            archive_raw, row["archive_family"]
        )
        item = {
            "capture_request_id": base.CID,
            "source_contract_blob": base.EXPECTED_BLOBS["SOURCE_IDENTITY_CONTRACT.json"],
            "source_id": "BINANCE_OFFICIAL_PUBLIC_FUTURES_AND_ARCHIVE_V1",
            "canonical_request_id": pair["canonical_request_id"],
            "retrieved_at_utc": pair["archive_retrieved_at_utc"],
            "raw_sha256": pair["archive_raw_sha256"],
            "raw_size_bytes": pair["archive_raw_size_bytes"],
            "http_status": 200,
            "parser_version": base.PARSER,
            "row_count": row_count,
            "observed_min_timestamp": lo,
            "observed_max_timestamp": hi,
            "field_names_and_types": field_types,
            "missingness_counts": missingness,
            "asset": row["asset"],
            "venue": "BINANCE",
            "instrument_family": row["archive_family"],
            "support_status": status,
            "support_failure_code": failure,
            "raw_object_locator": receipt["durable_root_ref"] + "#" + pair["archive_raw_locator"],
            "manifest_locator": receipt["durable_root_ref"] + "#" + pair["archive_manifest_locator"],
        }
        if set(item) != base.METADATA_ALLOWLIST:
            raise base.CaptureError("METADATA_ALLOWLIST_DRIFT")
        metadata.append(item)

    support = {
        "schema_version": 1,
        "research_id": base.RID,
        "capture_request_id": base.CID,
        "plan_id": base.PLAN_ID,
        "parser_version": base.PARSER,
        "lifecycle_credit": "NONE_STAGE_3_REMAINS_2_OF_10",
        "controlled_scientific_history_reads_to_researcher": 0,
        "stage8_attempt_consumed": 0,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "archive_object_count": 15,
        "checksum_object_count": 15,
        "network_object_count_total": 30,
        "objects": metadata,
    }
    base.create_only(root / "SUPPORT_MANIFEST.json", base.canon(support))
    base.create_only(root / "CAPTURE_RECEIPT.json", receipt_path.read_bytes())
    return support


# Patch only the two audited implementation defects before delegating to the frozen base engine.
base._validate_contract_data = _validate_contract_data_fixed
base.finalize = finalize


def main(argv=None) -> int:
    return base.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
