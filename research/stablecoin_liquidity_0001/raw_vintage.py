from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

RESEARCH_ID = "STABLECOIN-LIQUIDITY-0001"
DATASET_ID = "DEFILLAMA-STABLECOIN-ALL-CHARTS"
SOURCE_ID = "DEFILLAMA-STABLECOIN-ALL-CHARTS-V1"
SOURCE_URL = "https://stablecoins.llama.fi/stablecoincharts/all"
SOURCE_SDK_COMMIT = "f0d43119c746dda0c1ad8460c37ac9e00e8e5161"
PARSER_VERSION = "STABLECOIN-DATA-PARSER-V1"
_CAPTURED_HEADERS = ("content-type", "date", "etag", "last-modified")


@dataclass(frozen=True)
class HttpCapture:
    raw_bytes: bytes
    retrieval_started_at: datetime
    retrieved_at: datetime
    http_status: int
    response_headers: Mapping[str, str]
    source_url: str = SOURCE_URL
    request_method: str = "GET"


@dataclass(frozen=True)
class SnapshotPaths:
    raw_path: Path
    manifest_path: Path


def _require_aware_utc(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso_z(value: datetime) -> str:
    value = _require_aware_utc(value, "timestamp")
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _safe_stamp(value: datetime) -> str:
    value = _require_aware_utc(value, "timestamp")
    return value.strftime("%Y%m%dT%H%M%S%fZ")


def sha256_bytes(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def _selected_headers(headers: Mapping[str, str]) -> dict[str, str]:
    lowered = {str(key).lower(): str(value) for key, value in headers.items()}
    return {key: lowered[key] for key in _CAPTURED_HEADERS if key in lowered}


def build_manifest(capture: HttpCapture, raw_relative_path: str) -> dict[str, object]:
    started = _require_aware_utc(capture.retrieval_started_at, "retrieval_started_at")
    retrieved = _require_aware_utc(capture.retrieved_at, "retrieved_at")
    if retrieved < started:
        raise ValueError("retrieved_at cannot precede retrieval_started_at")
    if capture.http_status != 200:
        raise ValueError(f"refuse to persist non-200 capture: {capture.http_status}")
    if capture.source_url != SOURCE_URL:
        raise ValueError(f"unexpected source URL: {capture.source_url}")
    if capture.request_method != "GET":
        raise ValueError(f"unexpected request method: {capture.request_method}")

    return {
        "schema_version": 1,
        "research_id": RESEARCH_ID,
        "dataset_id": DATASET_ID,
        "source_id": SOURCE_ID,
        "source_url": capture.source_url,
        "request_method": capture.request_method,
        "retrieval_started_at": _iso_z(started),
        "retrieved_at": _iso_z(retrieved),
        "http_status": capture.http_status,
        "response_headers": _selected_headers(capture.response_headers),
        "raw_sha256": sha256_bytes(capture.raw_bytes),
        "raw_size_bytes": len(capture.raw_bytes),
        "raw_relative_path": raw_relative_path,
        "source_sdk_commit": SOURCE_SDK_COMMIT,
        "parser_version": PARSER_VERSION,
    }


def _write_exclusive(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    try:
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        # Fail closed. An incomplete/orphan create-only artifact is evidence of a
        # failed capture and must be reconciled manually; never overwrite it.
        raise


def write_snapshot(root: Path, capture: HttpCapture) -> SnapshotPaths:
    root = Path(root)
    retrieved = _require_aware_utc(capture.retrieved_at, "retrieved_at")
    raw_hash = sha256_bytes(capture.raw_bytes)
    directory = (
        root
        / "defillama_stablecoin_all_charts"
        / f"{retrieved.year:04d}"
        / f"{retrieved.month:02d}"
        / f"{retrieved.day:02d}"
    )
    raw_name = f"{_safe_stamp(retrieved)}__{raw_hash}.json"
    raw_path = directory / raw_name
    manifest_path = directory / f"{raw_name}.manifest.json"
    raw_relative_path = raw_path.relative_to(root).as_posix()
    manifest = build_manifest(capture, raw_relative_path)
    manifest_bytes = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

    _write_exclusive(raw_path, capture.raw_bytes)
    _write_exclusive(manifest_path, manifest_bytes)
    return SnapshotPaths(raw_path=raw_path, manifest_path=manifest_path)


def verify_snapshot(paths: SnapshotPaths) -> dict[str, object]:
    raw_bytes = paths.raw_path.read_bytes()
    manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
    if manifest.get("raw_sha256") != sha256_bytes(raw_bytes):
        raise ValueError("raw SHA256 mismatch")
    if manifest.get("raw_size_bytes") != len(raw_bytes):
        raise ValueError("raw byte-length mismatch")
    raw_relative = str(manifest.get("raw_relative_path") or "")
    if not raw_relative.endswith(paths.raw_path.name):
        raise ValueError("manifest raw path does not match snapshot")
    if manifest.get("research_id") != RESEARCH_ID:
        raise ValueError("manifest research_id mismatch")
    if manifest.get("dataset_id") != DATASET_ID:
        raise ValueError("manifest dataset_id mismatch")
    if manifest.get("source_sdk_commit") != SOURCE_SDK_COMMIT:
        raise ValueError("manifest source SDK commit mismatch")
    if manifest.get("parser_version") != PARSER_VERSION:
        raise ValueError("manifest parser version mismatch")
    return manifest
