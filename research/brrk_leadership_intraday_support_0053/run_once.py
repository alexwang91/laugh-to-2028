from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from research.brrk_leadership_intraday_support_0053 import support_funnel as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053-BINANCE-4H-HIST-V1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_create_only(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Git command failed: git {' '.join(args)}\n{exc.output}") from exc


def _git_head() -> str:
    return _git("rev-parse", "HEAD")


def _git_blob(path: str) -> str:
    return _git("rev-parse", f"HEAD:{path}")


def _interface() -> dict[str, Any]:
    value = _load_json(INTERFACE_PATH)
    if value.get("research_id") != sf.RESEARCH_ID:
        raise RuntimeError("RUN_INTERFACE research_id mismatch")
    return value


def _schema() -> dict[str, Any]:
    value = _load_json(SCHEMA_PATH)
    if value.get("schema_id") != "BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053-RESULT-V1":
        raise RuntimeError("Unexpected 0053 result schema")
    return value


def _verify_expected_head(expected_head_sha: str) -> str:
    if not expected_head_sha:
        raise RuntimeError("--expected-head-sha is mandatory")
    head = _git_head()
    if head != expected_head_sha:
        raise RuntimeError(f"Git HEAD mismatch: expected {expected_head_sha}, got {head}")
    return head


def _verify_upstream_blobs(interface: Mapping[str, Any]) -> None:
    for path, expected in interface["immutable_upstream_git_blobs"].items():
        actual = _git_blob(str(path))
        if actual != expected:
            raise RuntimeError(f"Immutable upstream blob mismatch for {path}: expected {expected}, got {actual}")


def _verify_payload(payload: Path, interface: Mapping[str, Any]) -> str:
    configured = (ROOT / interface["frozen_payload"]["path"]).resolve()
    if payload.resolve() != configured:
        raise RuntimeError(f"Payload path mismatch: expected {configured}, got {payload.resolve()}")
    actual = _sha256_file(payload)
    expected = str(interface["frozen_payload"]["sha256"])
    if actual != expected or actual != sf.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError(f"Frozen 4h payload SHA256 mismatch: expected {expected}, got {actual}")
    return actual


def _verify_absence(result: Path, execution: Path, attempt: Path, marker: Path) -> None:
    existing = [str(p) for p in (result, execution, attempt, marker) if p.exists()]
    if existing:
        raise RuntimeError(f"Controlled measurement is create-only; existing runtime artifacts: {existing}")


def preflight(*, payload: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    interface = _interface()
    _ = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    payload_sha = _verify_payload(payload, interface)
    _verify_absence(result, execution, attempt, marker)
    return {
        "research_id": sf.RESEARCH_ID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT",
        "git_head_sha": head,
        "payload_sha256": payload_sha,
        "actual_variants_evaluated": 0,
        "support_measurement_started": False,
        "winner_labels_executed": False,
        "predictive_model_executed": False,
        "portfolio_economics_executed": False,
        "production_authorized": False,
    }


def _result_from_measurement(head: str, measurement: sf.FunnelMeasurement, schema: Mapping[str, Any]) -> dict[str, Any]:
    m = measurement.to_dict()
    track_a = m["tracks"]["A"]
    classification = sf.classify_track_a(measurement)
    from pandas import Timestamp
    old_first = Timestamp("2025-01-14T00:00:00Z")
    old_last = Timestamp("2026-05-10T00:00:00Z")
    new_first = Timestamp(track_a["first_formal_origin_timestamp"]) if track_a["first_formal_origin_timestamp"] else None
    new_last = Timestamp(track_a["last_formal_origin_timestamp"]) if track_a["last_formal_origin_timestamp"] else None
    old_span_days = float((old_last - old_first).total_seconds() / 86400.0)
    new_span_days = track_a["formal_calendar_span_days"]
    comparison = {
        "0048_formal_rows": 245,
        "0053_track_a_formal_rows": int(track_a["formal_rows"]),
        "formal_row_ratio_0053A_to_0048": (float(track_a["formal_rows"]) / 245.0),
        "0048_complete_blocks": 4,
        "0053_track_a_complete_blocks": int(track_a["complete_blocks"]),
        "complete_block_difference": int(track_a["complete_blocks"]) - 4,
        "0048_first_formal_date": "2025-01-14T00:00:00Z",
        "0053_track_a_first_formal_timestamp": track_a["first_formal_origin_timestamp"],
        "first_formal_shift_days": float((new_first - old_first).total_seconds() / 86400.0) if new_first is not None else None,
        "0048_formal_calendar_span_days": old_span_days,
        "0053_track_a_formal_calendar_span_days": new_span_days,
        "formal_calendar_span_difference_days": float(new_span_days - old_span_days) if new_span_days is not None else None,
        "0053_track_a_last_formal_timestamp": track_a["last_formal_origin_timestamp"],
        "0048_last_formal_date": "2026-05-10T00:00:00Z",
        "last_formal_shift_days": float((new_last - old_last).total_seconds() / 86400.0) if new_last is not None else None
    }
    authority = dict(schema["authority_invariants"])
    result = {
        "schema_id": schema["schema_id"],
        "research_id": sf.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": sf.EXPECTED_PAYLOAD_SHA256,
        "execution_head_sha": head,
        "classification": classification,
        "measurement": m,
        "comparison_vs_0048": comparison,
        "authority": authority,
    }
    validate_result(result, schema)
    return result


def validate_result(result: Mapping[str, Any], schema: Mapping[str, Any] | None = None) -> None:
    schema = _schema() if schema is None else schema
    missing = [k for k in schema["required_top_level_keys"] if k not in result]
    if missing:
        raise RuntimeError(f"SUPPORT_RESULT missing fields: {missing}")
    if result["schema_id"] != schema["schema_id"] or result["research_id"] != sf.RESEARCH_ID:
        raise RuntimeError("SUPPORT_RESULT identity mismatch")
    if result["classification"] not in schema["classification_enum"]:
        raise RuntimeError("SUPPORT_RESULT classification not frozen")
    tracks = result["measurement"]["tracks"]
    if set(tracks) != {"A", "B", "C"}:
        raise RuntimeError("SUPPORT_RESULT must contain Tracks A/B/C exactly")
    required_track = set(schema["required_track_keys"])
    for name, record in tracks.items():
        if set(record) != required_track:
            raise RuntimeError(f"Track {name} fields differ from frozen schema")
    expected = "PASS_4H_CALENDAR_EQUIVALENT_SUPPORT_FEASIBLE" if int(tracks["A"]["complete_blocks"]) >= 12 else "FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT"
    if result["classification"] != expected:
        raise RuntimeError("Primary classification does not match frozen Track-A rule")
    for key, expected_value in schema["authority_invariants"].items():
        if result["authority"].get(key) != expected_value:
            raise RuntimeError(f"Authority invariant mismatch: {key}")


def evaluate(*, payload: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    pf = preflight(payload=payload, result=result, execution=execution, attempt=attempt, marker=marker, expected_head_sha=expected_head_sha)
    head = pf["git_head_sha"]
    started = _utc_now()
    attempt_value = {
        "research_id": sf.RESEARCH_ID,
        "status": "SUPPORT_MEASUREMENT_ATTEMPT_STARTED_CLOSED_TO_RECOMPUTATION",
        "started_at_utc": started,
        "git_head_sha": head,
        "payload_sha256": sf.EXPECTED_PAYLOAD_SHA256,
        "same_id_recomputation_allowed": False,
    }
    # This create-only marker must precede the first real-payload support calculation.
    _write_create_only(attempt, attempt_value)

    try:
        measurement = sf.measure_support_funnel(payload)
        support_result = _result_from_measurement(head, measurement, _schema())
    except sf.SupportProtocolError as exc:
        raise RuntimeError(f"Frozen support measurement failed after attempt marker: {exc}") from exc

    _write_create_only(result, support_result)
    completed = _utc_now()
    execution_value = {
        "research_id": sf.RESEARCH_ID,
        "status": "VALID_SUPPORT_MEASUREMENT_COMPLETE_PENDING_FINAL_MARKER",
        "started_at_utc": started,
        "completed_at_utc": completed,
        "git_head_sha": head,
        "payload_sha256": sf.EXPECTED_PAYLOAD_SHA256,
        "attempt_marker_sha256": _sha256_file(attempt),
        "support_result_sha256": _sha256_file(result),
        "classification": support_result["classification"],
        "actual_variants_evaluated": 1,
        "winner_labels_executed": False,
        "predictive_model_executed": False,
        "portfolio_economics_executed": False,
        "production_authorized": False,
    }
    _write_create_only(execution, execution_value)
    marker_value = {
        "research_id": sf.RESEARCH_ID,
        "status": "VALID_SUPPORT_MEASUREMENT_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "completed_at_utc": completed,
        "git_head_sha": head,
        "payload_sha256": sf.EXPECTED_PAYLOAD_SHA256,
        "attempt_marker_sha256": _sha256_file(attempt),
        "support_result_sha256": _sha256_file(result),
        "execution_sha256": _sha256_file(execution),
        "classification": support_result["classification"],
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _write_create_only(marker, marker_value)
    return support_result


def recover_marker(*, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    interface = _interface()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    if marker.exists():
        raise RuntimeError("RUN_ONCE.marker already exists")
    if not (attempt.exists() and result.exists() and execution.exists()):
        raise RuntimeError("Marker-only recovery requires attempt, result and execution")
    support_result = _load_json(result)
    validate_result(support_result)
    ex = _load_json(execution)
    if ex.get("git_head_sha") != head:
        raise RuntimeError("Execution HEAD mismatch during recovery")
    if ex.get("attempt_marker_sha256") != _sha256_file(attempt):
        raise RuntimeError("Attempt hash mismatch during recovery")
    if ex.get("support_result_sha256") != _sha256_file(result):
        raise RuntimeError("Support-result hash mismatch during recovery")
    marker_value = {
        "research_id": sf.RESEARCH_ID,
        "status": "VALID_SUPPORT_MEASUREMENT_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "completed_at_utc": ex["completed_at_utc"],
        "git_head_sha": head,
        "payload_sha256": sf.EXPECTED_PAYLOAD_SHA256,
        "attempt_marker_sha256": _sha256_file(attempt),
        "support_result_sha256": _sha256_file(result),
        "execution_sha256": _sha256_file(execution),
        "classification": support_result["classification"],
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "recovered_without_remeasurement": True,
    }
    _write_create_only(marker, marker_value)
    return marker_value


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("preflight", "evaluate"):
        q = sub.add_parser(name)
        q.add_argument("--payload", required=True)
        q.add_argument("--result", required=True)
        q.add_argument("--execution", required=True)
        q.add_argument("--attempt", required=True)
        q.add_argument("--marker", required=True)
        q.add_argument("--expected-head-sha", required=True)
    q = sub.add_parser("recover-marker")
    q.add_argument("--result", required=True)
    q.add_argument("--execution", required=True)
    q.add_argument("--attempt", required=True)
    q.add_argument("--marker", required=True)
    q.add_argument("--expected-head-sha", required=True)
    return p


def main() -> None:
    args = _parser().parse_args()
    common = {
        "result": Path(args.result),
        "execution": Path(args.execution),
        "attempt": Path(args.attempt),
        "marker": Path(args.marker),
        "expected_head_sha": args.expected_head_sha,
    }
    if args.command == "preflight":
        out = preflight(payload=Path(args.payload), **common)
    elif args.command == "evaluate":
        out = evaluate(payload=Path(args.payload), **common)
    else:
        out = recover_marker(**common)
    print(json.dumps(out, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
