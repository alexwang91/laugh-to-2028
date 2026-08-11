from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from research.brrk_leadership_4h_structural_readiness_0055 import engine
from research.brrk_leadership_rotation_0048.engine import FrozenProtocolError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-INTRADAY-SUPPORT-0053-BINANCE-4H-HIST-V1"
SCHEMA_ID = "BRRK-LEADERSHIP-4H-STRUCTURAL-READINESS-0055-METHOD-RESULT-V1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if value == value and value not in (float("inf"), float("-inf")) else None
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except Exception:
            pass
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha256_json_file(path: Path) -> str:
    return hashlib.sha256(_canonical_bytes(_load_json(path))).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_create_only(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Git command failed: git {' '.join(args)}\n{exc.output}") from exc


def _interface() -> dict[str, Any]:
    value = _load_json(INTERFACE_PATH)
    if value.get("research_id") != engine.RESEARCH_ID:
        raise RuntimeError("RUN_INTERFACE research_id mismatch")
    return value


def _schema() -> dict[str, Any]:
    value = _load_json(SCHEMA_PATH)
    if value.get("schema_id") != SCHEMA_ID or value.get("research_id") != engine.RESEARCH_ID:
        raise RuntimeError("Unexpected 0055 result schema identity")
    return value


def _verify_expected_head(expected_head_sha: str) -> str:
    if not expected_head_sha:
        raise RuntimeError("--expected-head-sha is mandatory")
    head = _git("rev-parse", "HEAD")
    if head != expected_head_sha:
        raise RuntimeError(f"Git HEAD mismatch: expected {expected_head_sha}, got {head}")
    return head


def _verify_upstream_blobs(interface: Mapping[str, Any]) -> None:
    for path, expected in interface["immutable_upstream_git_blobs"].items():
        actual = _git("rev-parse", f"HEAD:{path}")
        if actual != expected:
            raise RuntimeError(f"Immutable upstream blob mismatch for {path}: expected {expected}, got {actual}")


def _verify_payload(payload: Path, interface: Mapping[str, Any]) -> str:
    frozen = interface["frozen_market_payload"]
    configured = (ROOT / frozen["path"]).resolve()
    if payload.resolve() != configured:
        raise RuntimeError(f"Payload path mismatch: expected {configured}, got {payload.resolve()}")
    actual_blob = _git("rev-parse", f"HEAD:{frozen['path']}")
    if actual_blob != frozen["git_blob_sha"]:
        raise RuntimeError("Frozen payload git blob mismatch")
    actual_sha = _sha256_file(payload)
    if actual_sha != frozen["payload_sha256"] or actual_sha != engine.EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("Frozen payload SHA256 mismatch")
    return actual_sha


def _verify_runtime_names(result: Path, execution: Path, attempt: Path, marker: Path) -> None:
    actual = (result.name, execution.name, attempt.name, marker.name)
    expected = ("METHOD_RESULT.json", "EXECUTION.json", "RUN_ATTEMPT.marker", "RUN_ONCE.marker")
    if actual != expected:
        raise RuntimeError(f"Runtime artifact filenames differ from frozen interface: {actual}")


def _verify_controlled_context(payload: Path, expected_head_sha: str) -> tuple[str, str]:
    interface = _interface()
    _ = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    return head, _verify_payload(payload, interface)


def _authority() -> dict[str, Any]:
    return {
        "development_not_independent_oos": True,
        "post_2022_target_values_read": False,
        "predictive_performance_metrics_executed": False,
        "portfolio_economics_executed": False,
        "0048_rerun_or_rescue_executed": False,
        "0053_rerun_or_rescue_executed": False,
        "0054_rerun_or_rescue_executed": False,
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _scan_forbidden_metric_keys(value: Any, forbidden: list[str], path: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            lowered = str(key).lower()
            hits = [token for token in forbidden if token.lower() in lowered]
            if hits:
                raise RuntimeError(f"Forbidden predictive/economic metric key at {path}.{key}: {hits}")
            _scan_forbidden_metric_keys(child, forbidden, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            _scan_forbidden_metric_keys(child, forbidden, f"{path}[{i}]")


def validate_result(result: Mapping[str, Any], schema: Mapping[str, Any] | None = None) -> None:
    schema = _schema() if schema is None else schema
    missing = [key for key in schema["required_top_level_keys"] if key not in result]
    if missing:
        raise RuntimeError(f"METHOD_RESULT missing fields: {missing}")
    if result["schema_id"] != schema["schema_id"] or result["research_id"] != engine.RESEARCH_ID:
        raise RuntimeError("METHOD_RESULT identity mismatch")
    if result["dataset_slice_id"] != schema["dataset_slice_id"] or result["payload_sha256"] != schema["payload_sha256"]:
        raise RuntimeError("METHOD_RESULT dataset identity mismatch")
    if result["classification"] not in schema["classification_enum"]:
        raise RuntimeError("METHOD_RESULT classification is not frozen")
    for key, expected in schema["authority_invariants"].items():
        if result["authority"].get(key) != expected:
            raise RuntimeError(f"METHOD_RESULT authority invariant mismatch: {key}")
    measurement = result["measurement"]
    if isinstance(measurement, Mapping) and "authority" in measurement:
        for key, expected in schema["authority_invariants"].items():
            if measurement["authority"].get(key) != expected:
                raise RuntimeError(f"Nested authority invariant mismatch: {key}")
    _scan_forbidden_metric_keys(result, list(schema["forbidden_metric_tokens"]))


def preflight(*, payload: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(payload, expected_head_sha)
    existing = [str(path) for path in (result, execution, attempt, marker) if path.exists()]
    if existing:
        raise RuntimeError(f"Controlled 0055 start is create-only; existing runtime artifacts: {existing}")
    return {
        "research_id": engine.RESEARCH_ID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT",
        "git_head_sha": head,
        "payload_sha256": payload_sha,
        "actual_variants_evaluated": 0,
        "methodology_measurement_started": False,
        "post_2022_target_values_read": False,
        "predictive_performance_metrics_executed": False,
        "portfolio_economics_executed": False,
        "production_authorized": False,
    }


def start_attempt(*, payload: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    pf = preflight(payload=payload, result=result, execution=execution, attempt=attempt, marker=marker, expected_head_sha=expected_head_sha)
    value = {
        "research_id": engine.RESEARCH_ID,
        "status": "METHODOLOGY_MEASUREMENT_ATTEMPT_STARTED_CLOSED_TO_RECOMPUTATION",
        "started_at_utc": _utc_now(),
        "git_head_sha": pf["git_head_sha"],
        "payload_sha256": pf["payload_sha256"],
        "same_id_recomputation_allowed": False,
    }
    _write_create_only(attempt, value)
    return value


def _build_result(head: str, payload_sha: str) -> dict[str, Any]:
    schema = _schema()
    try:
        measurement = engine.measure_frozen_readiness(ROOT / _interface()["frozen_market_payload"]["path"])
        classification = str(measurement["classification"])
    except (engine.ReadinessProtocolError, FrozenProtocolError) as exc:
        classification = "INVALID_EXECUTION_PROTOCOL_OR_NUMERICAL_INTEGRITY"
        measurement = {
            "research_id": engine.RESEARCH_ID,
            "classification": classification,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "authority": _authority(),
        }
    result = {
        "schema_id": schema["schema_id"],
        "research_id": engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "execution_head_sha": head,
        "classification": classification,
        "measurement": measurement,
        "authority": _authority(),
    }
    validate_result(result, schema)
    return result


def evaluate_after_attempt(*, payload: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(payload, expected_head_sha)
    if not attempt.exists():
        raise RuntimeError("RUN_ATTEMPT.marker must be durably persisted before evaluate")
    existing = [str(path) for path in (result, execution, marker) if path.exists()]
    if existing:
        raise RuntimeError(f"0055 evaluate is create-only; existing output artifact(s): {existing}")
    attempt_value = _load_json(attempt)
    if attempt_value.get("research_id") != engine.RESEARCH_ID or attempt_value.get("same_id_recomputation_allowed") is not False:
        raise RuntimeError("Attempt marker identity/closure mismatch")
    if attempt_value.get("git_head_sha") != head or attempt_value.get("payload_sha256") != payload_sha:
        raise RuntimeError("Attempt marker binding mismatch")

    method_result = _build_result(head, payload_sha)
    _write_create_only(result, method_result)
    completed = _utc_now()
    execution_value = {
        "research_id": engine.RESEARCH_ID,
        "status": "VALID_METHODOLOGY_MEASUREMENT_COMPLETE_PENDING_FINAL_MARKER",
        "started_at_utc": attempt_value["started_at_utc"],
        "completed_at_utc": completed,
        "git_head_sha": head,
        "payload_sha256": payload_sha,
        "attempt_marker_sha256": _sha256_json_file(attempt),
        "method_result_sha256": _sha256_json_file(result),
        "classification": method_result["classification"],
        "actual_variants_evaluated": 1,
        "post_2022_target_values_read": False,
        "predictive_performance_metrics_executed": False,
        "portfolio_economics_executed": False,
        "production_authorized": False,
    }
    _write_create_only(execution, execution_value)
    return method_result


def finalize_marker_only(*, payload: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(payload, expected_head_sha)
    if marker.exists():
        raise RuntimeError("RUN_ONCE.marker already exists")
    if not (attempt.exists() and result.exists() and execution.exists()):
        raise RuntimeError("Finalize requires attempt, result and execution artifacts")
    attempt_value = _load_json(attempt)
    method_result = _load_json(result)
    execution_value = _load_json(execution)
    validate_result(method_result)
    if execution_value.get("git_head_sha") != head or execution_value.get("payload_sha256") != payload_sha:
        raise RuntimeError("Execution binding mismatch during finalize")
    if execution_value.get("attempt_marker_sha256") != _sha256_json_file(attempt):
        raise RuntimeError("Attempt marker hash mismatch during finalize")
    if execution_value.get("method_result_sha256") != _sha256_json_file(result):
        raise RuntimeError("Method result hash mismatch during finalize")
    marker_value = {
        "research_id": engine.RESEARCH_ID,
        "status": "VALID_METHODOLOGY_MEASUREMENT_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "completed_at_utc": execution_value["completed_at_utc"],
        "git_head_sha": head,
        "payload_sha256": payload_sha,
        "attempt_marker_sha256": _sha256_json_file(attempt),
        "method_result_sha256": _sha256_json_file(result),
        "execution_sha256": _sha256_json_file(execution),
        "classification": method_result["classification"],
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "finalized_without_remeasurement": True,
    }
    _write_create_only(marker, marker_value)
    return marker_value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "start-attempt", "evaluate", "finalize"):
        q = sub.add_parser(name)
        q.add_argument("--payload", required=True)
        q.add_argument("--result", required=True)
        q.add_argument("--execution", required=True)
        q.add_argument("--attempt", required=True)
        q.add_argument("--marker", required=True)
        q.add_argument("--expected-head-sha", required=True)
    return parser


def main() -> None:
    args = _parser().parse_args()
    kwargs = {
        "payload": Path(args.payload), "result": Path(args.result), "execution": Path(args.execution),
        "attempt": Path(args.attempt), "marker": Path(args.marker), "expected_head_sha": args.expected_head_sha,
    }
    if args.command == "preflight":
        value = preflight(**kwargs)
    elif args.command == "start-attempt":
        value = start_attempt(**kwargs)
    elif args.command == "evaluate":
        value = evaluate_after_attempt(**kwargs)
    elif args.command == "finalize":
        value = finalize_marker_only(**kwargs)
    else:
        raise RuntimeError("Unknown command")
    print(json.dumps(_json_safe(value), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
