from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RID = "BRRK-CRYPTO-CARRY-ATLAS-0072"
CID = "BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0002"
PLAN_ID = "BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0002-SUPPORT-PLAN-V1"
PARSER = "0072_CAPTURE_0002_ARCHIVE_METADATA_V1"
ALLOWED_HOST = "data.binance.vision"
EXPECTED_BLOBS = {
    "SOURCE_IDENTITY_CONTRACT.json": "8b933f357a4f4b1299558386e7ad6e91742df939",
    "SOURCE_IDENTITY_AMENDMENT_0001.json": "dde70ee217d10896ff06abfd03ffe804c242cd64",
    "CAPTURE_REQUEST_0002.json": "a7322f7e3da1494afc4a2dd2e6468ab5499b73ff",
    "CAPTURE_PLAN_0002.json": "d18c1d84051c4bb0274cca6fa953954333283fbd",
}
ALLOWED_FAMILIES = {
    "spot/monthly/klines",
    "futures/um/monthly/klines",
    "futures/um/monthly/markPriceKlines",
    "futures/um/monthly/indexPriceKlines",
    "futures/um/monthly/premiumIndexKlines",
}
METADATA_ALLOWLIST = {
    "capture_request_id",
    "source_contract_blob",
    "source_id",
    "canonical_request_id",
    "retrieved_at_utc",
    "raw_sha256",
    "raw_size_bytes",
    "http_status",
    "parser_version",
    "row_count",
    "observed_min_timestamp",
    "observed_max_timestamp",
    "field_names_and_types",
    "missingness_counts",
    "asset",
    "venue",
    "instrument_family",
    "support_status",
    "support_failure_code",
    "raw_object_locator",
    "manifest_locator",
}


class CaptureError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "redirect forbidden", headers, fp)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canon(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def create_only(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(fd, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def git_blob(name: str) -> str:
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:research/brrk_crypto_carry_atlas_0072/{name}"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _validate_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise CaptureError("UNAPPROVED_HOST")
    if parsed.username or parsed.password or parsed.fragment:
        raise CaptureError("INVALID_URL_IDENTITY")


def _validate_contract_data(request: dict, plan: dict, source: dict, amendment: dict) -> None:
    if request.get("research_id") != RID or request.get("capture_request_id") != CID:
        raise CaptureError("REQUEST_IDENTITY_DRIFT")
    if request.get("status") != "PROSPECTIVE_NOT_EXECUTED":
        raise CaptureError("REQUEST_STATUS_DRIFT")
    if request.get("capture_0001_status") != "SEALED_FAILED_NO_RETRY":
        raise CaptureError("CAPTURE_0001_SEAL_DRIFT")
    if request.get("allowed_delivery_host") != ALLOWED_HOST:
        raise CaptureError("REQUEST_HOST_DRIFT")
    if set(request.get("forbidden_delivery_hosts", [])) != {"fapi.binance.com", "api.bybit.com"}:
        raise CaptureError("FORBIDDEN_HOST_SET_DRIFT")
    if request.get("network_retry_policy") != "ZERO_AUTOMATIC_RETRIES":
        raise CaptureError("RETRY_POLICY_DRIFT")
    if request.get("redirect_policy") != "NO_REDIRECT_FOLLOWING":
        raise CaptureError("REDIRECT_POLICY_DRIFT")
    if request.get("stage8_attempt_consumed") != 0 or request.get("controlled_scientific_history_reads_to_researcher") != 0:
        raise CaptureError("ATTEMPT_OR_READ_BUDGET_DRIFT")

    if plan.get("research_id") != RID or plan.get("capture_request_id") != CID or plan.get("plan_id") != PLAN_ID:
        raise CaptureError("PLAN_IDENTITY_DRIFT")
    if plan.get("status") != "PROSPECTIVE_NOT_EXECUTED":
        raise CaptureError("PLAN_STATUS_DRIFT")
    if plan.get("host") != ALLOWED_HOST:
        raise CaptureError("PLAN_HOST_DRIFT")
    if plan.get("automatic_retry") is not False or plan.get("redirect_following") is not False:
        raise CaptureError("PLAN_NETWORK_POLICY_DRIFT")
    rows = plan.get("objects")
    if not isinstance(rows, list) or len(rows) != 15:
        raise CaptureError("OBJECT_COUNT_DRIFT")
    if plan.get("archive_object_count") != 15 or plan.get("checksum_object_count") != 15 or plan.get("network_object_count_total") != 30:
        raise CaptureError("NETWORK_OBJECT_COUNT_DRIFT")
    if request.get("requested_archive_object_count") != 15 or request.get("requested_checksum_object_count") != 15 or request.get("requested_network_object_count_total") != 30:
        raise CaptureError("REQUEST_OBJECT_COUNT_DRIFT")
    if set(request.get("allowed_archive_families", [])) != ALLOWED_FAMILIES:
        raise CaptureError("REQUEST_FAMILY_DRIFT")

    object_ids = set()
    urls = set()
    asset_family = set()
    for row in rows:
        oid = row.get("object_id")
        asset = row.get("asset")
        family = row.get("archive_family")
        role = row.get("capture_role")
        if not isinstance(oid, str) or not oid or oid in object_ids:
            raise CaptureError("OBJECT_ID_DRIFT")
        if asset not in {"BTC", "ETH", "SOL"} or family not in ALLOWED_FAMILIES:
            raise CaptureError("ASSET_OR_FAMILY_DRIFT")
        if (asset, family) in asset_family:
            raise CaptureError("DUPLICATE_ASSET_FAMILY")
        if family.endswith("premiumIndexKlines") and role != "PREMIUM_INDEX_RAW_SUPPORT_ONLY":
            raise CaptureError("PREMIUM_INDEX_SEMANTICS_DRIFT")
        archive_url = row.get("archive_url")
        checksum_url = row.get("checksum_url")
        if not isinstance(archive_url, str) or not isinstance(checksum_url, str):
            raise CaptureError("OBJECT_URL_DRIFT")
        _validate_url(archive_url)
        _validate_url(checksum_url)
        if checksum_url != archive_url + ".CHECKSUM":
            raise CaptureError("CHECKSUM_PAIR_DRIFT")
        if archive_url in urls or checksum_url in urls or archive_url == checksum_url:
            raise CaptureError("DUPLICATE_NETWORK_OBJECT")
        object_ids.add(oid)
        asset_family.add((asset, family))
        urls.add(archive_url)
        urls.add(checksum_url)
    if len(asset_family) != 15 or len(urls) != 30:
        raise CaptureError("FROZEN_OBJECT_MATRIX_DRIFT")

    if source.get("research_id") != RID or source.get("identity_contract_id") != "BRRK-CRYPTO-CARRY-ATLAS-0072-SOURCE-IDENTITY-V1":
        raise CaptureError("SOURCE_CONTRACT_DRIFT")
    if amendment.get("research_id") != RID or amendment.get("amendment_id") != "BRRK-CRYPTO-CARRY-ATLAS-0072-SOURCE-IDENTITY-AMENDMENT-0001":
        raise CaptureError("SOURCE_AMENDMENT_DRIFT")
    decision = amendment.get("prospective_capture_identity_decision", {})
    if decision.get("new_source_admission") is not False or decision.get("feature_family_replacement") is not False:
        raise CaptureError("SOURCE_AMENDMENT_PERMISSION_DRIFT")
    rules = amendment.get("future_capture_rules", {})
    if rules.get("capture_0001_retry_forbidden") is not True or rules.get("future_capture_may_not_use_fapi_or_bybit_under_current_execution_environment") is not True:
        raise CaptureError("SOURCE_AMENDMENT_GUARD_DRIFT")


def validate_contract(*, git: bool = True) -> dict:
    request = load(HERE / "CAPTURE_REQUEST_0002.json")
    plan = load(HERE / "CAPTURE_PLAN_0002.json")
    source = load(HERE / "SOURCE_IDENTITY_CONTRACT.json")
    amendment = load(HERE / "SOURCE_IDENTITY_AMENDMENT_0001.json")
    implementation = load(HERE / "CAPTURE_IMPLEMENTATION_CONTRACT_0002.json")
    boundary = load(HERE / "CAPTURE_EXECUTION_BOUNDARY_0002.json")
    _validate_contract_data(request, plan, source, amendment)
    if implementation.get("contract_id") != "BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-IMPLEMENTATION-0002-V1":
        raise CaptureError("IMPLEMENTATION_IDENTITY_DRIFT")
    if implementation.get("capture_request_id") != CID or implementation.get("status") != "PROSPECTIVE_NOT_EXECUTED":
        raise CaptureError("IMPLEMENTATION_STATUS_DRIFT")
    if implementation.get("expected_network_object_count_total") != 30 or implementation.get("allowed_host") != ALLOWED_HOST:
        raise CaptureError("IMPLEMENTATION_OBJECT_BOUNDARY_DRIFT")
    if boundary.get("boundary_id") != "BRRK-CRYPTO-CARRY-ATLAS-0072-CAPTURE-0002-EXECUTION-BOUNDARY-V1":
        raise CaptureError("BOUNDARY_IDENTITY_DRIFT")
    if boundary.get("network_execution_authorized_by_this_boundary") is not False or boundary.get("execution_trigger_in_this_boundary") is not False:
        raise CaptureError("BOUNDARY_EXECUTION_AUTHORITY_DRIFT")
    if boundary.get("preflight", {}).get("repository_wide_nonexpired_capture_0002_artifact_count_required") != 0:
        raise CaptureError("BOUNDARY_PREFLIGHT_DRIFT")
    if git:
        for name, expected in EXPECTED_BLOBS.items():
            if git_blob(name) != expected:
                raise CaptureError(f"BLOB_IDENTITY_DRIFT_{name}")
    return plan


def storage_root(path: Path) -> Path:
    if not path.is_absolute():
        raise CaptureError("STORAGE_ROOT_MUST_BE_ABSOLUTE")
    resolved = path.resolve(strict=False)
    repo = ROOT.resolve(strict=False)
    if resolved == repo or repo in resolved.parents:
        raise CaptureError("STORAGE_ROOT_INSIDE_REPOSITORY")
    return resolved


def capture_root(path: Path) -> Path:
    return storage_root(path) / "research" / "brrk_crypto_carry_atlas_0072" / "captures" / CID


def fetch_once(url: str, timeout: int = 30) -> dict:
    _validate_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "BRRK-0072-capture-0002/1", "Accept": "*/*"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout) as response:
            status = int(response.getcode())
            if status != 200:
                raise CaptureError("HTTP_NON_200")
            body = response.read()
            selected_headers = {
                key: response.headers.get(key, "")
                for key in ("Content-Type", "Content-Length", "Last-Modified", "ETag")
            }
    except urllib.error.HTTPError as exc:
        if 300 <= int(exc.code) < 400:
            raise CaptureError("REDIRECT_FORBIDDEN") from exc
        raise CaptureError("HTTP_NON_200") from exc
    except CaptureError:
        raise
    except Exception as exc:
        raise CaptureError("NETWORK_FAILURE") from exc
    return {
        "body": body,
        "status": status,
        "selected_headers": selected_headers,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)


def _checksum_token(payload: bytes) -> str:
    try:
        token = payload.decode("ascii").strip().split()[0].lower()
    except Exception as exc:
        raise CaptureError("CHECKSUM_SCHEMA_DRIFT") from exc
    if len(token) != 64 or any(ch not in "0123456789abcdef" for ch in token):
        raise CaptureError("CHECKSUM_SCHEMA_DRIFT")
    return token


def _failure_receipt(root: Path, code: str, persisted_network_objects: int) -> None:
    receipt = {
        "schema_version": 1,
        "research_id": RID,
        "capture_request_id": CID,
        "plan_id": PLAN_ID,
        "state": "FAILED_CLOSED_RECONCILIATION_REQUIRED",
        "failure_code": code,
        "persisted_network_object_count": persisted_network_objects,
        "automatic_retry": False,
        "second_fetch_allowed": False,
        "scientific_payload_exposed_to_researcher": False,
        "controlled_scientific_history_reads_to_researcher": 0,
        "stage8_attempt_consumed": 0,
    }
    try:
        create_only(root / "CAPTURE_FAILURE.json", canon(receipt))
    except FileExistsError:
        pass


def capture(
    storage: Path,
    fetcher: Callable[[str], dict] = fetch_once,
    *,
    git: bool = True,
) -> dict:
    plan = validate_contract(git=git)
    root = capture_root(storage)
    if root.exists() and any(path.is_file() for path in root.rglob("*")):
        raise CaptureError("CAPTURE_ALREADY_EXISTS")

    pairs = []
    persisted = 0
    try:
        for row in plan["objects"]:
            oid = row["object_id"]
            safe = _safe_name(oid)
            archive = fetcher(row["archive_url"])
            archive_body = archive["body"]
            archive_path = root / "raw" / f"{safe}.zip"
            create_only(archive_path, archive_body)
            persisted += 1
            archive_hash = sha256_bytes(archive_body)
            archive_manifest = {
                "schema_version": 1,
                "capture_request_id": CID,
                "canonical_request_id": oid,
                "network_object_kind": "ARCHIVE_ZIP",
                "url_identity": row["archive_url"],
                "retrieved_at_utc": archive["retrieved_at_utc"],
                "raw_sha256": archive_hash,
                "raw_size_bytes": len(archive_body),
                "http_status": archive["status"],
                "selected_headers": archive.get("selected_headers", {}),
                "raw_object_locator": f"raw/{safe}.zip",
            }
            create_only(root / "manifests" / f"{safe}.archive.json", canon(archive_manifest))

            checksum = fetcher(row["checksum_url"])
            checksum_body = checksum["body"]
            checksum_path = root / "raw" / f"{safe}.CHECKSUM"
            create_only(checksum_path, checksum_body)
            persisted += 1
            checksum_hash = sha256_bytes(checksum_body)
            checksum_manifest = {
                "schema_version": 1,
                "capture_request_id": CID,
                "canonical_request_id": oid,
                "network_object_kind": "CHECKSUM",
                "url_identity": row["checksum_url"],
                "retrieved_at_utc": checksum["retrieved_at_utc"],
                "raw_sha256": checksum_hash,
                "raw_size_bytes": len(checksum_body),
                "http_status": checksum["status"],
                "selected_headers": checksum.get("selected_headers", {}),
                "raw_object_locator": f"raw/{safe}.CHECKSUM",
            }
            create_only(root / "manifests" / f"{safe}.checksum.json", canon(checksum_manifest))

            expected = _checksum_token(checksum_body)
            if expected != archive_hash:
                raise CaptureError("CHECKSUM_MISMATCH")
            pairs.append(
                {
                    "canonical_request_id": oid,
                    "asset": row["asset"],
                    "archive_family": row["archive_family"],
                    "capture_role": row["capture_role"],
                    "archive_raw_sha256": archive_hash,
                    "checksum_raw_sha256": checksum_hash,
                    "archive_raw_size_bytes": len(archive_body),
                    "checksum_raw_size_bytes": len(checksum_body),
                    "archive_retrieved_at_utc": archive["retrieved_at_utc"],
                    "checksum_retrieved_at_utc": checksum["retrieved_at_utc"],
                    "archive_raw_locator": f"raw/{safe}.zip",
                    "checksum_raw_locator": f"raw/{safe}.CHECKSUM",
                    "archive_manifest_locator": f"manifests/{safe}.archive.json",
                    "checksum_manifest_locator": f"manifests/{safe}.checksum.json",
                    "checksum_verified": True,
                }
            )
    except CaptureError as exc:
        _failure_receipt(root, str(exc), persisted)
        raise
    except Exception as exc:
        _failure_receipt(root, "INTERNAL_FAIL_CLOSED", persisted)
        raise CaptureError("INTERNAL_FAIL_CLOSED") from exc

    aggregate = hashlib.sha256()
    for pair in pairs:
        aggregate.update(pair["canonical_request_id"].encode("utf-8"))
        aggregate.update(bytes.fromhex(pair["archive_raw_sha256"]))
        aggregate.update(bytes.fromhex(pair["checksum_raw_sha256"]))
    staging = {
        "schema_version": 1,
        "research_id": RID,
        "capture_request_id": CID,
        "plan_id": PLAN_ID,
        "parser_version": PARSER,
        "source_contract_blob": EXPECTED_BLOBS["SOURCE_IDENTITY_CONTRACT.json"],
        "state": "PERSISTED_CHECKSUM_VERIFIED_AWAITING_DURABLE_RECEIPT",
        "archive_object_count": 15,
        "checksum_object_count": 15,
        "network_object_count_total": 30,
        "pair_count": len(pairs),
        "aggregate_raw_sha256": aggregate.hexdigest(),
        "pairs": pairs,
        "controlled_scientific_history_reads_to_researcher": 0,
        "stage8_attempt_consumed": 0,
    }
    staging["manifest_sha256"] = sha256_bytes(canon(staging))
    create_only(root / "STAGING_MANIFEST.json", canon(staging))
    return staging


def write_durability_receipt(
    path: Path,
    staging: dict,
    *,
    durable_backend: str,
    durable_root_ref: str,
    artifact_id: str,
    artifact_url: str,
    artifact_digest: str,
    archived_at_utc: str,
) -> dict:
    values = (durable_backend, durable_root_ref, artifact_id, artifact_url, artifact_digest, archived_at_utc)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise CaptureError("INVALID_DURABILITY_IDENTITY")
    receipt = {
        "schema_version": 1,
        "research_id": RID,
        "capture_request_id": CID,
        "plan_id": PLAN_ID,
        "manifest_sha256": staging["manifest_sha256"],
        "aggregate_raw_sha256": staging["aggregate_raw_sha256"],
        "archive_object_count": staging["archive_object_count"],
        "checksum_object_count": staging["checksum_object_count"],
        "network_object_count_total": staging["network_object_count_total"],
        "durable_backend": durable_backend,
        "durable_root_ref": durable_root_ref,
        "artifact_id": artifact_id,
        "artifact_url": artifact_url,
        "artifact_digest": artifact_digest,
        "archived_at_utc": archived_at_utc,
        "write_semantics": "CREATE_ONLY_VERSIONED_COPY_OVERWRITE_FALSE",
    }
    create_only(path, canon(receipt))
    return receipt


def _timestamp_bounds(rows: list[list[str]]) -> tuple[str | None, str | None]:
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
        raise CaptureError("DUPLICATE_OR_NON_MONOTONE_TIMESTAMP")
    converted = [datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z") for value in values]
    return converted[0], converted[-1]


def _parse_archive_metadata(raw: bytes) -> tuple[int, str | None, str | None, dict, dict, str, str | None]:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            names = [name for name in archive.namelist() if not name.endswith("/")]
            if len(names) != 1:
                raise CaptureError("SCHEMA_DRIFT")
            text = archive.read(names[0]).decode("utf-8")
    except CaptureError:
        raise
    except Exception as exc:
        raise CaptureError("SCHEMA_DRIFT") from exc
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
    lo, hi = _timestamp_bounds(data_rows)
    if lo is None or hi is None:
        return len(data_rows), None, None, field_types, missingness, "FAIL", "POINT_IN_TIME_SEMANTICS_UNPROVABLE"
    return len(data_rows), lo, hi, field_types, missingness, "PASS", None


def finalize(storage: Path, staging: dict, receipt_path: Path, *, git: bool = True) -> dict:
    plan = validate_contract(git=git)
    root = capture_root(storage)
    saved = load(root / "STAGING_MANIFEST.json")
    if saved != staging:
        raise CaptureError("RAW_HASH_MISMATCH")
    unsigned = dict(staging)
    manifest_hash = unsigned.pop("manifest_sha256")
    if sha256_bytes(canon(unsigned)) != manifest_hash:
        raise CaptureError("RAW_HASH_MISMATCH")
    receipt = load(receipt_path)
    required = {
        "research_id": RID,
        "capture_request_id": CID,
        "plan_id": PLAN_ID,
        "manifest_sha256": staging["manifest_sha256"],
        "aggregate_raw_sha256": staging["aggregate_raw_sha256"],
        "archive_object_count": 15,
        "checksum_object_count": 15,
        "network_object_count_total": 30,
        "write_semantics": "CREATE_ONLY_VERSIONED_COPY_OVERWRITE_FALSE",
    }
    for key, expected in required.items():
        if receipt.get(key) != expected:
            raise CaptureError("RAW_HASH_MISMATCH")

    plan_by_id = {row["object_id"]: row for row in plan["objects"]}
    metadata = []
    for pair in staging["pairs"]:
        row = plan_by_id[pair["canonical_request_id"]]
        archive_path = root / pair["archive_raw_locator"]
        checksum_path = root / pair["checksum_raw_locator"]
        archive_raw = archive_path.read_bytes()
        checksum_raw = checksum_path.read_bytes()
        if sha256_bytes(archive_raw) != pair["archive_raw_sha256"] or sha256_bytes(checksum_raw) != pair["checksum_raw_sha256"]:
            raise CaptureError("RAW_HASH_MISMATCH")
        if _checksum_token(checksum_raw) != pair["archive_raw_sha256"]:
            raise CaptureError("CHECKSUM_MISMATCH")
        row_count, lo, hi, field_types, missingness, status, failure = _parse_archive_metadata(archive_raw)
        item = {
            "capture_request_id": CID,
            "source_contract_blob": EXPECTED_BLOBS["SOURCE_IDENTITY_CONTRACT.json"],
            "source_id": "BINANCE_OFFICIAL_PUBLIC_FUTURES_AND_ARCHIVE_V1",
            "canonical_request_id": pair["canonical_request_id"],
            "retrieved_at_utc": pair["archive_retrieved_at_utc"],
            "raw_sha256": pair["archive_raw_sha256"],
            "raw_size_bytes": pair["archive_raw_size_bytes"],
            "http_status": 200,
            "parser_version": PARSER,
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
        if set(item) != METADATA_ALLOWLIST:
            raise CaptureError("METADATA_ALLOWLIST_DRIFT")
        metadata.append(item)
    support = {
        "schema_version": 1,
        "research_id": RID,
        "capture_request_id": CID,
        "plan_id": PLAN_ID,
        "parser_version": PARSER,
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
    create_only(root / "SUPPORT_MANIFEST.json", canon(support))
    create_only(root / "CAPTURE_RECEIPT.json", receipt_path.read_bytes())
    return support


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-contract", action="store_true")
    parser.add_argument("--storage-root", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--capture-only", action="store_true")
    mode.add_argument("--finalize", action="store_true")
    parser.add_argument("--execute-live-capture", action="store_true")
    parser.add_argument("--durable-storage-attested", action="store_true")
    parser.add_argument("--zero-existing-artifact-preflight-pass", action="store_true")
    parser.add_argument("--staging-json", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(argv)

    if args.validate_contract:
        validate_contract()
        print("CAPTURE_0002_CONTRACT_VALID_NO_NETWORK")
        return 0
    if args.storage_root is None:
        raise CaptureError("STORAGE_ROOT_REQUIRED")
    if args.capture_only:
        if not args.execute_live_capture or not args.durable_storage_attested or not args.zero_existing_artifact_preflight_pass:
            raise CaptureError("EXPLICIT_MERGED_BOUNDARY_AND_ZERO_EXISTING_ARTIFACT_PREFLIGHT_REQUIRED")
        staging = capture(args.storage_root)
        print(
            json.dumps(
                {
                    "research_id": RID,
                    "capture_request_id": CID,
                    "state": staging["state"],
                    "archive_object_count": staging["archive_object_count"],
                    "checksum_object_count": staging["checksum_object_count"],
                    "network_object_count_total": staging["network_object_count_total"],
                    "manifest_sha256": staging["manifest_sha256"],
                    "aggregate_raw_sha256": staging["aggregate_raw_sha256"],
                    "controlled_scientific_history_reads_to_researcher": 0,
                    "stage8_attempt_consumed": 0,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    if args.finalize:
        if args.staging_json is None or args.receipt is None:
            raise CaptureError("FINALIZE_REQUIRES_STAGING_AND_RECEIPT")
        support = finalize(args.storage_root, load(args.staging_json), args.receipt)
        print(
            json.dumps(
                {
                    "research_id": RID,
                    "capture_request_id": CID,
                    "archive_object_count": support["archive_object_count"],
                    "support_manifest_sha256": sha256_bytes(canon(support)),
                    "controlled_scientific_history_reads_to_researcher": 0,
                    "stage8_attempt_consumed": 0,
                    "lifecycle_credit": support["lifecycle_credit"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    raise CaptureError("VALIDATE_OR_EXECUTION_MODE_REQUIRED")


if __name__ == "__main__":
    raise SystemExit(main())
