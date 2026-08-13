from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from research.brrk_beta_handoff_0047 import engine as source_engine
from research.brrk_beta_deterioration_btc_takeover_diagnostic_0059 import engine as scientific_engine


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
SCHEMA_ID = "BRRK-BETA-DETERIORATION-BTC-TAKEOVER-DIAGNOSTIC-0059-PRIMARY-RESULT-V1"


class ControlledRunError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, (float, np.floating)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return [_json_safe(x) for x in value.tolist()]
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except Exception:
            pass
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _json_safe(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256_json_file(path: Path) -> str:
    return hashlib.sha256(_canonical_bytes(_load_json(path))).hexdigest()


def _write_create_only(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ControlledRunError(f"Git command failed: git {' '.join(args)}\n{exc.output}") from exc


def _interface() -> dict[str, Any]:
    value = _load_json(INTERFACE_PATH)
    if value.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("RUN_INTERFACE research_id mismatch")
    if value.get("candidate_count") != 1:
        raise ControlledRunError("RUN_INTERFACE candidate_count mismatch")
    if value.get("actual_variants_evaluated") != 0:
        raise ControlledRunError("RUN_INTERFACE must remain zero-result")
    return value


def _schema() -> dict[str, Any]:
    value = _load_json(SCHEMA_PATH)
    if value.get("schema_id") != SCHEMA_ID or value.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("Unexpected 0059 result schema identity")
    return value


def _verify_expected_head(expected_head_sha: str) -> str:
    if not expected_head_sha:
        raise ControlledRunError("--expected-head-sha is mandatory")
    head = _git("rev-parse", "HEAD")
    if head != expected_head_sha:
        raise ControlledRunError(f"Git HEAD mismatch: expected {expected_head_sha}, got {head}")
    return head


def _verify_upstream_blobs(interface: Mapping[str, Any]) -> None:
    for path, expected in interface["immutable_upstream_git_blobs"].items():
        actual = _git("rev-parse", f"HEAD:{path}")
        if actual != expected:
            raise ControlledRunError(
                f"Immutable upstream blob mismatch for {path}: expected {expected}, got {actual}"
            )


def _verify_market_git_blob(interface: Mapping[str, Any]) -> None:
    frozen = interface["frozen_market_evidence"]
    actual = _git("rev-parse", f"HEAD:{frozen['path']}")
    if actual != frozen["git_blob_sha"]:
        raise ControlledRunError("Frozen market evidence git blob mismatch")


def _verify_market_path(market: Path, interface: Mapping[str, Any]) -> None:
    configured = (ROOT / interface["frozen_market_evidence"]["path"]).resolve()
    if market.resolve() != configured:
        raise ControlledRunError(f"Market path mismatch: expected {configured}, got {market.resolve()}")


def _verify_static_context(
    expected_head_sha: str,
    market: Path,
) -> tuple[str, dict[str, Any]]:
    interface = _interface()
    _ = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    _verify_market_git_blob(interface)
    _verify_market_path(market, interface)
    return head, interface


def _read_market_wrapper_once(market: Path, interface: Mapping[str, Any]) -> dict[str, Any]:
    # This is the only real market-content read path. It is unreachable before a durable
    # RUN_ATTEMPT.marker in evaluate_after_attempt and is never called by preflight/finalize.
    evidence = _load_json(market)
    if not isinstance(evidence, dict):
        raise source_engine.FrozenProtocolError("0059 market evidence wrapper must be an object")
    expected = str(interface["frozen_market_evidence"]["payload_sha256"])
    if evidence.get("payload_sha256") != expected:
        raise source_engine.FrozenProtocolError("0059 frozen market wrapper payload SHA256 mismatch")
    return evidence


def _verify_runtime_names(
    result: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
) -> None:
    actual = (result.name, execution.name, attempt.name, marker.name)
    expected = ("PRIMARY_RESULT.json", "EXECUTION.json", "RUN_ATTEMPT.marker", "RUN_ONCE.marker")
    if actual != expected:
        raise ControlledRunError(f"Runtime artifact filenames differ from frozen interface: {actual}")


def _measurement_authority() -> dict[str, Any]:
    return {
        "development_not_independent_oos": True,
        "researcher_exposed_history": True,
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized_components": [],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _authority() -> dict[str, Any]:
    return {
        "development_not_independent_oos": True,
        "researcher_exposed_history": True,
        "historical_execution_attempted": True,
        "declared_variants": 1,
        "actual_variants_evaluated": 1,
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized_components": [],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }


def _require_exact_keys(value: Mapping[str, Any], expected: Sequence[str], label: str) -> None:
    actual = set(value.keys())
    wanted = set(expected)
    if actual != wanted:
        raise ControlledRunError(
            f"{label} key mismatch: missing={sorted(wanted-actual)} extra={sorted(actual-wanted)}"
        )


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ControlledRunError(f"{label} must be numeric")
    out = float(value)
    if not math.isfinite(out):
        raise ControlledRunError(f"{label} must be finite")
    return out


def _nullable_finite(value: Any, label: str) -> float | None:
    if value is None:
        return None
    return _finite_number(value, label)


def _validate_authority(
    value: Mapping[str, Any],
    expected: Mapping[str, Any],
    label: str,
) -> None:
    _require_exact_keys(value, expected.keys(), label)
    for key, frozen in expected.items():
        if value.get(key) != frozen:
            raise ControlledRunError(f"{label} invariant mismatch: {key}")


def _validate_horizon_map(
    value: Any,
    schema: Mapping[str, Any],
    label: str,
    *,
    nullable_values: bool,
) -> dict[str, float | None]:
    if not isinstance(value, Mapping):
        raise ControlledRunError(f"{label} must be an object")
    _require_exact_keys(value, schema["horizon_keys"], label)
    out: dict[str, float | None] = {}
    for key in schema["horizon_keys"]:
        number = _nullable_finite(value[key], f"{label}.{key}")
        if number is None and not nullable_values:
            raise ControlledRunError(f"{label}.{key} may not be null")
        out[key] = number
    return out


def _validate_origin_panel(
    rows: Any,
    expected_count: int,
    schema: Mapping[str, Any],
) -> None:
    if not isinstance(rows, list):
        raise ControlledRunError("origin_panel must be a list")
    if len(rows) != expected_count:
        raise ControlledRunError("origin_panel row count mismatch")
    fields = schema["origin_panel_fields"]
    dates: list[str] = []
    blocks: list[int] = []
    numeric_fields = [x for x in fields if x not in {"origin_date", "chronological_block_id"}]
    for i, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise ControlledRunError(f"origin_panel row {i} must be an object")
        _require_exact_keys(row, fields, f"origin_panel row {i}")
        date = row["origin_date"]
        if not isinstance(date, str) or len(date) != 20 or not date.endswith("T00:00:00Z"):
            raise ControlledRunError(f"origin_panel row {i} origin_date format mismatch")
        block = row["chronological_block_id"]
        if isinstance(block, bool) or not isinstance(block, (int, np.integer)) or int(block) not in (1, 2, 3, 4):
            raise ControlledRunError(f"origin_panel row {i} chronological_block_id invalid")
        for key in numeric_fields:
            _finite_number(row[key], f"origin_panel row {i}.{key}")
        dates.append(date)
        blocks.append(int(block))
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ControlledRunError("origin_panel dates must be unique chronological order")
    if expected_count:
        q, r = divmod(expected_count, 4)
        expected_blocks: list[int] = []
        for i in range(4):
            expected_blocks.extend([i + 1] * (q + 1 if i < r else q))
        if blocks != expected_blocks:
            raise ControlledRunError("origin_panel chronological blocks do not match frozen q,r partition")


def _classification_from_persisted_gates(gates: Mapping[str, Any]) -> str:
    if gates["G1_SUPPORT"] is not True:
        return "FAIL_INSUFFICIENT_CAUSAL_SUPPORT"
    if gates["G2_MONOTONE_INFORMATION"] is not True:
        return "FAIL_NO_MONOTONE_CONTINUATION_INFORMATION"
    if gates["G3_TEMPORAL_RECURRENCE"] is not True:
        return "FAIL_TEMPORAL_INSTABILITY"
    if gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"] is not True:
        return "FAIL_DEPENDENCE_AWARE_ROBUSTNESS"
    return "PASS_MECHANISM_INFORMATION_STAGE_ELIGIBLE"


def _validate_successful_measurement(
    measurement: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> None:
    _require_exact_keys(measurement, schema["successful_measurement_required_keys"], "measurement")
    if measurement["research_id"] != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("measurement research_id mismatch")
    if measurement["classification"] not in schema["classification_enum"] or measurement["classification"] == "INVALID_EXECUTION":
        raise ControlledRunError("measurement classification is not a frozen non-invalid class")
    if measurement["actual_variants_evaluated"] != 1:
        raise ControlledRunError("measurement actual_variants_evaluated must equal one")

    gates = measurement["gates"]
    if not isinstance(gates, Mapping):
        raise ControlledRunError("measurement.gates must be an object")
    _require_exact_keys(gates, schema["required_gate_keys"], "measurement.gates")
    if gates["G0_INTEGRITY"] is not True:
        raise ControlledRunError("successful measurement must preserve G0_INTEGRITY=true")
    for key in schema["required_gate_keys"][1:]:
        if gates[key] not in (True, False, None):
            raise ControlledRunError(f"{key} must be bool or null")

    n = measurement["shared_origin_count"]
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or int(n) < 0:
        raise ControlledRunError("shared_origin_count must be a nonnegative integer")
    n = int(n)
    _validate_origin_panel(measurement["origin_panel"], n, schema)
    if n == 0:
        if measurement["shared_origin_start"] is not None or measurement["shared_origin_end"] is not None:
            raise ControlledRunError("zero support requires null origin endpoints")
    else:
        rows = measurement["origin_panel"]
        if measurement["shared_origin_start"] != rows[0]["origin_date"]:
            raise ControlledRunError("shared_origin_start mismatch")
        if measurement["shared_origin_end"] != rows[-1]["origin_date"]:
            raise ControlledRunError("shared_origin_end mismatch")

    expected_g1 = n >= int(schema["frozen_counts"]["minimum_shared_origins"])
    if gates["G1_SUPPORT"] is not expected_g1:
        raise ControlledRunError("G1 does not match persisted shared support")

    if not expected_g1:
        for key in (
            "full_sample_rho_by_horizon",
            "temporal_block_rho_by_horizon",
            "bootstrap_q95",
            "simultaneous_lcb_by_horizon",
            "component_target_spearman",
            "component_redundancy_matrix",
            "component_eigenvalues",
            "component_effective_rank",
        ):
            if measurement[key] is not None:
                raise ControlledRunError(f"{key} must be null when G1 fails")
        if gates["G2_MONOTONE_INFORMATION"] is not None or gates["G3_TEMPORAL_RECURRENCE"] is not None or gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"] is not None:
            raise ControlledRunError("G2-G4 must remain null when G1 fails")
    else:
        full = _validate_horizon_map(
            measurement["full_sample_rho_by_horizon"], schema, "full_sample_rho_by_horizon", nullable_values=True
        )
        finite_full = all(full[k] is not None for k in schema["horizon_keys"])
        expected_g2 = finite_full and all(float(full[k]) > 0.0 for k in schema["horizon_keys"])
        if gates["G2_MONOTONE_INFORMATION"] is not expected_g2:
            raise ControlledRunError("G2 does not match persisted full-sample rhos")

        temporal = measurement["temporal_block_rho_by_horizon"]
        if not isinstance(temporal, Mapping):
            raise ControlledRunError("temporal_block_rho_by_horizon must be an object")
        _require_exact_keys(temporal, schema["temporal_block_keys"], "temporal_block_rho_by_horizon")
        positive_blocks = 0
        for block in schema["temporal_block_keys"]:
            row = _validate_horizon_map(
                temporal[block], schema, f"temporal_block_rho_by_horizon.{block}", nullable_values=True
            )
            if all(row[k] is not None and float(row[k]) > 0.0 for k in schema["horizon_keys"]):
                positive_blocks += 1
        expected_g3 = positive_blocks >= 3
        if gates["G3_TEMPORAL_RECURRENCE"] is not expected_g3:
            raise ControlledRunError("G3 does not match persisted temporal-block rhos")

        component = measurement["component_target_spearman"]
        if not isinstance(component, Mapping):
            raise ControlledRunError("component_target_spearman must be an object")
        _require_exact_keys(component, schema["component_keys"], "component_target_spearman")
        for axis in schema["component_keys"]:
            _validate_horizon_map(
                component[axis], schema, f"component_target_spearman.{axis}", nullable_values=True
            )

        matrix = measurement["component_redundancy_matrix"]
        if not isinstance(matrix, list) or len(matrix) != 3 or any(not isinstance(row, list) or len(row) != 3 for row in matrix):
            raise ControlledRunError("component_redundancy_matrix must be 3x3")
        finite_matrix = True
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if _nullable_finite(value, f"component_redundancy_matrix[{i}][{j}]") is None:
                    finite_matrix = False
        eig = measurement["component_eigenvalues"]
        erank = measurement["component_effective_rank"]
        if finite_matrix:
            if not isinstance(eig, list) or len(eig) != 3:
                raise ControlledRunError("finite component matrix requires three eigenvalues")
            for i, value in enumerate(eig):
                _finite_number(value, f"component_eigenvalues[{i}]")
            rank_value = _finite_number(erank, "component_effective_rank")
            if rank_value < 0.0 or rank_value > 3.0 + 1e-12:
                raise ControlledRunError("component_effective_rank outside [0,3]")
        else:
            if eig is not None or erank is not None:
                raise ControlledRunError("nonfinite component matrix requires null eigenvalues/effective rank")

        if finite_full:
            q95 = _finite_number(measurement["bootstrap_q95"], "bootstrap_q95")
            _ = q95
            lcbs = _validate_horizon_map(
                measurement["simultaneous_lcb_by_horizon"],
                schema,
                "simultaneous_lcb_by_horizon",
                nullable_values=False,
            )
            expected_g4 = all(float(lcbs[k]) > 0.0 for k in schema["horizon_keys"])
            if gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"] is not expected_g4:
                raise ControlledRunError("G4 does not match persisted simultaneous LCBs")
        else:
            if measurement["bootstrap_q95"] is not None or measurement["simultaneous_lcb_by_horizon"] is not None:
                raise ControlledRunError("undefined full-sample rho requires null bootstrap outputs")
            if gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"] is not False:
                raise ControlledRunError("undefined full-sample rho requires G4=false")

    expected_class = _classification_from_persisted_gates(gates)
    if measurement["classification"] != expected_class:
        raise ControlledRunError("measurement classification does not match persisted gates")
    _validate_authority(
        measurement["authority"],
        schema["measurement_authority_invariants"],
        "measurement.authority",
    )


def validate_result(
    result: Mapping[str, Any],
    schema: Mapping[str, Any] | None = None,
) -> None:
    schema = _schema() if schema is None else schema
    if not isinstance(result, Mapping):
        raise ControlledRunError("PRIMARY_RESULT must be an object")
    _require_exact_keys(result, schema["required_top_level_keys"], "PRIMARY_RESULT")
    if result["schema_id"] != schema["schema_id"] or result["research_id"] != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("PRIMARY_RESULT identity mismatch")
    if result["dataset_slice_id"] != schema["dataset_slice_id"] or result["payload_sha256"] != schema["payload_sha256"]:
        raise ControlledRunError("PRIMARY_RESULT dataset identity mismatch")
    if not isinstance(result["execution_head_sha"], str) or not result["execution_head_sha"]:
        raise ControlledRunError("PRIMARY_RESULT execution_head_sha missing")
    if result["classification"] not in schema["classification_enum"]:
        raise ControlledRunError("PRIMARY_RESULT classification is not frozen")
    _validate_authority(result["authority"], schema["authority_invariants"], "PRIMARY_RESULT.authority")

    measurement = result["measurement"]
    if not isinstance(measurement, Mapping):
        raise ControlledRunError("PRIMARY_RESULT measurement must be an object")
    if result["classification"] == "INVALID_EXECUTION":
        _require_exact_keys(measurement, schema["invalid_measurement_required_keys"], "invalid measurement")
        if measurement["research_id"] != scientific_engine.RESEARCH_ID or measurement["classification"] != "INVALID_EXECUTION":
            raise ControlledRunError("invalid measurement identity mismatch")
        if measurement["actual_variants_evaluated"] != 1:
            raise ControlledRunError("invalid attempt must consume the single frozen historical variant")
        if not isinstance(measurement["error_type"], str) or not isinstance(measurement["error"], str):
            raise ControlledRunError("invalid measurement error fields must be strings")
        _validate_authority(
            measurement["authority"],
            schema["measurement_authority_invariants"],
            "invalid measurement.authority",
        )
    else:
        if measurement.get("classification") != result["classification"]:
            raise ControlledRunError("measurement/top-level classification mismatch")
        _validate_successful_measurement(measurement, schema)


def _build_result(
    market: Path,
    head: str,
    interface: Mapping[str, Any],
) -> dict[str, Any]:
    schema = _schema()
    payload_sha = str(interface["frozen_market_evidence"]["payload_sha256"])
    try:
        evidence = _read_market_wrapper_once(market, interface)
        source_frames = source_engine.frames_from_market_evidence(evidence)
        if set(source_frames) != set(scientific_engine.ASSETS):
            raise source_engine.FrozenProtocolError("0059 source loader did not return exact BTC/ETH/SOL set")
        frames = {asset: source_frames[asset] for asset in scientific_engine.ASSETS}
        measurement = scientific_engine.evaluate_frozen_contract(frames, payload_sha)
        classification = str(measurement["classification"])
    except (source_engine.FrozenProtocolError, scientific_engine.DiagnosticProtocolError) as exc:
        classification = "INVALID_EXECUTION"
        measurement = {
            "research_id": scientific_engine.RESEARCH_ID,
            "classification": classification,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "actual_variants_evaluated": 1,
            "authority": _measurement_authority(),
        }
    value = {
        "schema_id": schema["schema_id"],
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "execution_head_sha": head,
        "classification": classification,
        "measurement": _json_safe(measurement),
        "authority": _authority(),
    }
    validate_result(value, schema)
    return value


def _runtime_paths_exist(*paths: Path) -> list[str]:
    return [path.name for path in paths if path.exists()]


def preflight(
    *,
    market: Path,
    result: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, interface = _verify_static_context(expected_head_sha, market)
    forbidden = _runtime_paths_exist(result, execution, marker)
    if forbidden:
        raise ControlledRunError(f"Preflight found existing output artifacts: {forbidden}")
    return {
        "research_id": scientific_engine.RESEARCH_ID,
        "status": "PREFLIGHT_ZERO_RESULT_PASS",
        "git_head_sha": head,
        "payload_sha256": str(interface["frozen_market_evidence"]["payload_sha256"]),
        "attempt_marker_exists": attempt.exists(),
        "result_exists": result.exists(),
        "execution_exists": execution.exists(),
        "final_marker_exists": marker.exists(),
        "candidate_count": 1,
        "actual_variants_evaluated": 0,
        "market_content_read": False,
        "production_authorized": False,
    }


def start_attempt(
    *,
    market: Path,
    result: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, interface = _verify_static_context(expected_head_sha, market)
    existing = _runtime_paths_exist(attempt, result, execution, marker)
    if existing:
        raise ControlledRunError(f"Cannot start attempt with existing runtime artifacts: {existing}")
    value = {
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": str(interface["frozen_market_evidence"]["payload_sha256"]),
        "git_head_sha": head,
        "started_at_utc": _utc_now(),
        "candidate_count": 1,
        "target_horizons": list(scientific_engine.HORIZONS),
        "same_id_recomputation_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
    }
    _write_create_only(attempt, value)
    return value


def _verify_attempt(
    attempt: Path,
    *,
    head: str,
    payload_sha: str,
) -> dict[str, Any]:
    value = _load_json(attempt)
    if value.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("RUN_ATTEMPT.marker research_id mismatch")
    if value.get("dataset_slice_id") != DATASET_SLICE_ID or value.get("payload_sha256") != payload_sha:
        raise ControlledRunError("RUN_ATTEMPT.marker dataset identity mismatch")
    if value.get("git_head_sha") != head:
        raise ControlledRunError("RUN_ATTEMPT.marker HEAD mismatch")
    if value.get("candidate_count") != 1 or value.get("target_horizons") != list(scientific_engine.HORIZONS):
        raise ControlledRunError("RUN_ATTEMPT.marker frozen candidate/horizon mismatch")
    for key in ("same_id_recomputation_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed"):
        if value.get(key) is not False:
            raise ControlledRunError(f"RUN_ATTEMPT.marker authority mismatch: {key}")
    return value


def evaluate_after_attempt(
    *,
    market: Path,
    result: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, interface = _verify_static_context(expected_head_sha, market)
    payload_sha = str(interface["frozen_market_evidence"]["payload_sha256"])
    if not attempt.exists():
        raise ControlledRunError("RUN_ATTEMPT.marker must exist before historical evaluation")
    existing = _runtime_paths_exist(result, execution, marker)
    if existing:
        raise ControlledRunError(f"Cannot evaluate with existing output artifact: {existing}")
    attempt_value = _verify_attempt(attempt, head=head, payload_sha=payload_sha)

    value = _build_result(market, head, interface)
    _write_create_only(result, value)
    execution_value = {
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "started_at_utc": attempt_value["started_at_utc"],
        "completed_at_utc": _utc_now(),
        "classification": value["classification"],
        "actual_variants_evaluated": 1,
        "attempt_marker_sha256": _sha256_json_file(attempt),
        "primary_result_sha256": _sha256_json_file(result),
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
    }
    _write_create_only(execution, execution_value)
    return value


def finalize_marker_only(
    *,
    market: Path,
    result: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, interface = _verify_static_context(expected_head_sha, market)
    payload_sha = str(interface["frozen_market_evidence"]["payload_sha256"])
    if marker.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists")
    missing = [path.name for path in (attempt, result, execution) if not path.exists()]
    if missing:
        raise ControlledRunError(f"Cannot finalize marker; missing persisted artifacts: {missing}")

    attempt_value = _verify_attempt(attempt, head=head, payload_sha=payload_sha)
    result_value = _load_json(result)
    validate_result(result_value)
    if result_value.get("execution_head_sha") != head or result_value.get("payload_sha256") != payload_sha:
        raise ControlledRunError("PRIMARY_RESULT identity mismatch during finalize")

    execution_value = _load_json(execution)
    expected_execution_keys = {
        "research_id","dataset_slice_id","payload_sha256","git_head_sha","started_at_utc","completed_at_utc",
        "classification","actual_variants_evaluated","attempt_marker_sha256","primary_result_sha256",
        "same_id_rerun_allowed","same_id_retuning_allowed","same_id_rescue_allowed","production_authorized"
    }
    if set(execution_value) != expected_execution_keys:
        raise ControlledRunError("EXECUTION key mismatch")
    if execution_value.get("research_id") != scientific_engine.RESEARCH_ID or execution_value.get("git_head_sha") != head:
        raise ControlledRunError("EXECUTION identity mismatch")
    if execution_value.get("payload_sha256") != payload_sha or execution_value.get("classification") != result_value.get("classification"):
        raise ControlledRunError("EXECUTION result identity mismatch")
    if execution_value.get("actual_variants_evaluated") != 1:
        raise ControlledRunError("EXECUTION actual_variants_evaluated mismatch")
    for key in ("same_id_rerun_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed", "production_authorized"):
        if execution_value.get(key) is not False:
            raise ControlledRunError(f"EXECUTION authority mismatch: {key}")

    attempt_hash = _sha256_json_file(attempt)
    result_hash = _sha256_json_file(result)
    if execution_value.get("attempt_marker_sha256") != attempt_hash:
        raise ControlledRunError("Attempt marker hash mismatch")
    if execution_value.get("primary_result_sha256") != result_hash:
        raise ControlledRunError("Primary result hash mismatch")

    value = {
        "research_id": scientific_engine.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "finalized_at_utc": _utc_now(),
        "classification": result_value["classification"],
        "actual_variants_evaluated": 1,
        "attempt_marker_sha256": attempt_hash,
        "primary_result_sha256": result_hash,
        "execution_sha256": _sha256_json_file(execution),
        "finalized_without_market_read": True,
        "finalized_without_remeasurement": True,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
    }
    if any(attempt_value.get(k) is not False for k in ("same_id_recomputation_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed")):
        raise ControlledRunError("Attempt marker no longer forbids same-ID recomputation/retuning/rescue")
    _write_create_only(marker, value)
    return value


def _default_paths() -> dict[str, Path]:
    return {
        "market": ROOT / "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json",
        "result": HERE / "PRIMARY_RESULT.json",
        "execution": HERE / "EXECUTION.json",
        "attempt": HERE / "RUN_ATTEMPT.marker",
        "marker": HERE / "RUN_ONCE.marker",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="0059 controlled exactly-once Beta-deterioration/BTC-takeover diagnostic state machine"
    )
    parser.add_argument("command", choices=("preflight", "start-attempt", "evaluate", "finalize"))
    parser.add_argument("--expected-head-sha", required=True)
    defaults = _default_paths()
    for name, path in defaults.items():
        parser.add_argument(f"--{name}", type=Path, default=path)
    args = parser.parse_args()
    kwargs = {
        "market": args.market,
        "result": args.result,
        "execution": args.execution,
        "attempt": args.attempt,
        "marker": args.marker,
        "expected_head_sha": args.expected_head_sha,
    }
    if args.command == "preflight":
        value = preflight(**kwargs)
    elif args.command == "start-attempt":
        value = start_attempt(**kwargs)
    elif args.command == "evaluate":
        value = evaluate_after_attempt(**kwargs)
    else:
        value = finalize_marker_only(**kwargs)
    print(json.dumps(_json_safe(value), indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
