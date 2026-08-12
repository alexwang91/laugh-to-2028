from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from research.brrk_beta_handoff_0047 import engine as source_engine
from research.brrk_simple_eth_sol_beta_router_0056 import engine as scientific_engine
from research.brrk_simple_eth_sol_beta_router_interface_replication_0057 import adapter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
SCHEMA_ID = "BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-INTERFACE-REPLICATION-0057-PRIMARY-RESULT-V1"


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
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        raise ControlledRunError(f"Git command failed: git {' '.join(args)}\n{exc.output}") from exc


def _interface() -> dict[str, Any]:
    value = _load_json(INTERFACE_PATH)
    if value.get("research_id") != adapter.RESEARCH_ID:
        raise ControlledRunError("RUN_INTERFACE research_id mismatch")
    return value


def _schema() -> dict[str, Any]:
    value = _load_json(SCHEMA_PATH)
    if value.get("schema_id") != SCHEMA_ID or value.get("research_id") != adapter.RESEARCH_ID:
        raise ControlledRunError("Unexpected 0057 result schema identity")
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


def _verify_market_wrapper(market: Path, interface: Mapping[str, Any]) -> str:
    frozen = interface["frozen_market_evidence"]
    configured = (ROOT / frozen["path"]).resolve()
    if market.resolve() != configured:
        raise ControlledRunError(f"Market path mismatch: expected {configured}, got {market.resolve()}")
    _verify_market_git_blob(interface)
    evidence = _load_json(market)
    actual_payload_sha = evidence.get("payload_sha256")
    if actual_payload_sha != frozen["payload_sha256"] or actual_payload_sha != adapter.EXPECTED_PAYLOAD_SHA256:
        raise ControlledRunError("Frozen market payload SHA256 mismatch")
    return str(actual_payload_sha)


def _verify_runtime_names(result: Path, execution: Path, attempt: Path, marker: Path) -> None:
    actual = (result.name, execution.name, attempt.name, marker.name)
    expected = ("PRIMARY_RESULT.json", "EXECUTION.json", "RUN_ATTEMPT.marker", "RUN_ONCE.marker")
    if actual != expected:
        raise ControlledRunError(f"Runtime artifact filenames differ from frozen interface: {actual}")


def _verify_static_context(expected_head_sha: str) -> tuple[str, dict[str, Any]]:
    interface = _interface()
    _ = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    _verify_market_git_blob(interface)
    return head, interface


def _verify_controlled_context(market: Path, expected_head_sha: str) -> tuple[str, str]:
    head, interface = _verify_static_context(expected_head_sha)
    return head, _verify_market_wrapper(market, interface)


def _measurement_authority() -> dict[str, Any]:
    return {
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized": False,
        "production_authorized_components": [],
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _authority() -> dict[str, Any]:
    return {
        "development_not_independent_oos": True,
        "researcher_exposed_history": True,
        "portfolio_economics_executed": True,
        "probability_or_predictive_metrics_executed": False,
        "btc_values_consumed_by_candidate_or_benchmarks": False,
        "oracle_or_hindsight_winner_metrics_executed": False,
        "actual_variants_evaluated": 1,
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized": False,
        "production_authorized_components": [],
        "signature_authorized": False,
        "order_submission_authorized": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }


def _scan_forbidden_metric_keys(value: Any, forbidden: list[str], path: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) == "authority":
                continue
            lowered = str(key).lower()
            hits = [token for token in forbidden if token.lower() in lowered]
            if hits:
                raise ControlledRunError(f"Forbidden non-preregistered metric key at {path}.{key}: {hits}")
            _scan_forbidden_metric_keys(child, forbidden, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            _scan_forbidden_metric_keys(child, forbidden, f"{path}[{i}]")


def _require_exact_keys(value: Mapping[str, Any], expected: list[str], label: str) -> None:
    actual = set(value.keys())
    wanted = set(expected)
    if actual != wanted:
        raise ControlledRunError(f"{label} key mismatch: missing={sorted(wanted-actual)} extra={sorted(actual-wanted)}")


def _finite_number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float, np.integer, np.floating)):
        raise ControlledRunError(f"{label} must be numeric")
    out = float(value)
    if not math.isfinite(out):
        raise ControlledRunError(f"{label} must be finite")
    return out


def validate_result(result: Mapping[str, Any], schema: Mapping[str, Any] | None = None) -> None:
    schema = _schema() if schema is None else schema
    _require_exact_keys(result, list(schema["required_top_level_keys"]), "PRIMARY_RESULT")
    if result["schema_id"] != schema["schema_id"] or result["research_id"] != adapter.RESEARCH_ID:
        raise ControlledRunError("PRIMARY_RESULT identity mismatch")
    if result["dataset_slice_id"] != schema["dataset_slice_id"] or result["payload_sha256"] != schema["payload_sha256"]:
        raise ControlledRunError("PRIMARY_RESULT dataset identity mismatch")
    if result["classification"] not in schema["classification_enum"]:
        raise ControlledRunError("PRIMARY_RESULT classification is not frozen")
    for key, expected in schema["authority_invariants"].items():
        if result["authority"].get(key) != expected:
            raise ControlledRunError(f"PRIMARY_RESULT authority invariant mismatch: {key}")

    measurement = result["measurement"]
    if not isinstance(measurement, Mapping):
        raise ControlledRunError("PRIMARY_RESULT measurement must be an object")

    if result["classification"] == "INVALID_EXECUTION":
        _require_exact_keys(measurement, list(schema["invalid_measurement_required_keys"]), "invalid measurement")
        if measurement.get("research_id") != adapter.RESEARCH_ID or measurement.get("classification") != "INVALID_EXECUTION":
            raise ControlledRunError("Invalid measurement identity mismatch")
        if measurement.get("actual_variants_evaluated") != 1:
            raise ControlledRunError("Invalid execution must still bind the single attempted variant")
    else:
        _require_exact_keys(measurement, list(schema["successful_measurement_required_keys"]), "successful measurement")
        if measurement.get("research_id") != adapter.RESEARCH_ID or measurement.get("classification") != result["classification"]:
            raise ControlledRunError("Measurement identity/classification mismatch")
        counts = schema["frozen_counts"]
        if measurement.get("rm60_origin_count") != counts["rm60_origin_count"] or measurement.get("target_count") != counts["target_count"]:
            raise ControlledRunError("Frozen 2122-origin count mismatch")
        targets = measurement.get("targets")
        if not isinstance(targets, (list, tuple)) or len(targets) != counts["target_count"] or any(x not in scientific_engine.ASSETS for x in targets):
            raise ControlledRunError("Frozen router target path is invalid")
        if measurement.get("actual_variants_evaluated") != 1:
            raise ControlledRunError("0057 must evaluate exactly one variant")

        gates = measurement.get("gates")
        if not isinstance(gates, Mapping):
            raise ControlledRunError("0057 gates must be an object")
        _require_exact_keys(gates, list(schema["required_gate_keys"]), "gates")
        if any(not isinstance(gates[key], bool) for key in schema["required_gate_keys"]):
            raise ControlledRunError("All 0057 gates must be booleans")
        if gates["G0_INTEGRITY"] is not True:
            raise ControlledRunError("Successful measurement shape requires G0 integrity pass")
        frozen_classification = scientific_engine.classification_from_gates(
            gates["G0_INTEGRITY"],
            gates["G1_PRIMARY_ECONOMIC_DOMINANCE_5BPS"],
            gates["G2_COST_SURVIVAL"],
            gates["G3_TEMPORAL_ROBUSTNESS"],
            gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"],
        )
        if frozen_classification != result["classification"]:
            raise ControlledRunError("Classification does not match frozen G0-G4 precedence")

        metrics = measurement.get("metrics_by_cost_bps")
        if not isinstance(metrics, Mapping):
            raise ControlledRunError("metrics_by_cost_bps must be an object")
        _require_exact_keys(metrics, list(schema["required_cost_keys"]), "cost panel")
        for cost_key in schema["required_cost_keys"]:
            arms = metrics[cost_key]
            _require_exact_keys(arms, list(schema["required_arm_keys"]), f"cost {cost_key} arms")
            for arm_name in schema["required_arm_keys"]:
                arm = arms[arm_name]
                _require_exact_keys(arm, list(schema["required_arm_metric_keys"]), f"{cost_key}/{arm_name}")
                wealth = _finite_number(arm["terminal_wealth"], f"{cost_key}/{arm_name}/terminal_wealth")
                cagr = _finite_number(arm["cagr"], f"{cost_key}/{arm_name}/cagr")
                mdd = _finite_number(arm["maximum_drawdown"], f"{cost_key}/{arm_name}/maximum_drawdown")
                turnover = _finite_number(arm["total_executed_l1_turnover"], f"{cost_key}/{arm_name}/turnover")
                if wealth <= 0.0 or cagr <= -1.0 or not (-1.0 <= mdd <= scientific_engine.STRICT_TOL) or turnover < 0.0:
                    raise ControlledRunError(f"Invalid economic metric domain for {cost_key}/{arm_name}")

        advantages = measurement.get("log_terminal_advantage_by_cost_bps")
        _require_exact_keys(advantages, list(schema["required_cost_keys"]), "log advantage panel")
        for cost_key in schema["required_cost_keys"]:
            _require_exact_keys(advantages[cost_key], list(schema["required_benchmark_keys"]), f"advantage {cost_key}")
            for benchmark in schema["required_benchmark_keys"]:
                _finite_number(advantages[cost_key][benchmark], f"advantage {cost_key}/{benchmark}")

        if measurement.get("best_static_5bps") not in schema["required_benchmark_keys"]:
            raise ControlledRunError("best_static_5bps is not one of the frozen static benchmarks")
        block_stats = measurement.get("temporal_block_relative_log_growth_vs_best_static_5bps")
        if not isinstance(block_stats, (list, tuple)) or len(block_stats) != counts["temporal_block_count"]:
            raise ControlledRunError("Frozen temporal block count mismatch")
        block_values = [_finite_number(x, "temporal block statistic") for x in block_stats]
        positive_count = sum(x > scientific_engine.STRICT_TOL for x in block_values)
        if measurement.get("temporal_positive_block_count") != positive_count:
            raise ControlledRunError("Temporal positive-block count mismatch")

        bootstrap = measurement.get("bootstrap_5bps")
        expected_bootstrap_keys = [
            "means", "q95", "lcbs", "benchmarks", "replicates", "block_length",
            "blocks_per_replicate_before_truncation", "seed"
        ]
        _require_exact_keys(bootstrap, expected_bootstrap_keys, "bootstrap_5bps")
        if tuple(bootstrap["benchmarks"]) != tuple(schema["required_benchmark_keys"]):
            raise ControlledRunError("Bootstrap benchmark order mismatch")
        if bootstrap["replicates"] != counts["bootstrap_replicates"] or bootstrap["block_length"] != counts["bootstrap_block_length"]:
            raise ControlledRunError("Bootstrap replicate/block contract mismatch")
        if bootstrap["blocks_per_replicate_before_truncation"] != counts["bootstrap_blocks_per_replicate_before_truncation"] or bootstrap["seed"] != counts["bootstrap_seed"]:
            raise ControlledRunError("Bootstrap block-count/seed contract mismatch")
        if len(bootstrap["means"]) != 3 or len(bootstrap["lcbs"]) != 3:
            raise ControlledRunError("Bootstrap mean/LCB vector length mismatch")
        for x in list(bootstrap["means"]) + [bootstrap["q95"]] + list(bootstrap["lcbs"]):
            _finite_number(x, "bootstrap statistic")

        diagnostics = measurement.get("diagnostics")
        _require_exact_keys(diagnostics, list(schema["required_diagnostic_keys"]), "diagnostics")
        _require_exact_keys(diagnostics["maximum_drawdown_5bps"], list(schema["required_arm_keys"]), "diagnostic MDD arms")
        _require_exact_keys(diagnostics["calendar_year_returns_5bps"], list(schema["required_arm_keys"]), "calendar-year arms")

        delegated = measurement["delegated_scientific_engine"]
        source_adapter = measurement["source_interface_adapter"]
        inv = schema["delegation_invariants"]
        if delegated != {
            "research_id": inv["delegated_research_id"],
            "git_blob_sha": inv["delegated_engine_git_blob_sha"],
            "portfolio_outputs_modified_by_0057_adapter": inv["portfolio_outputs_modified_by_0057_adapter"],
        }:
            raise ControlledRunError("Delegated scientific-engine provenance mismatch")
        if source_adapter != {
            "source_timezone_representation": inv["source_timezone_representation"],
            "operation": inv["adapter_operation"],
            "calendar_order_rowcount_close_values_changed": inv["calendar_order_rowcount_close_values_changed"],
        }:
            raise ControlledRunError("Source interface-adapter provenance mismatch")

    for key, expected in schema["measurement_authority_invariants"].items():
        if measurement["authority"].get(key) != expected:
            raise ControlledRunError(f"Measurement authority invariant mismatch: {key}")
    _scan_forbidden_metric_keys(measurement, list(schema["forbidden_metric_tokens"]))


def _build_result(market: Path, head: str, payload_sha: str) -> dict[str, Any]:
    schema = _schema()
    try:
        evidence = _load_json(market)
        source_frames = source_engine.frames_from_market_evidence(evidence)
        frames = {"ETH": source_frames["ETH"], "SOL": source_frames["SOL"]}
        measurement = adapter.evaluate_frozen_contract(frames, payload_sha)
        classification = str(measurement["classification"])
    except (adapter.InterfaceAdapterError, source_engine.FrozenProtocolError, scientific_engine.RouterProtocolError) as exc:
        classification = "INVALID_EXECUTION"
        measurement = {
            "research_id": adapter.RESEARCH_ID,
            "classification": classification,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "actual_variants_evaluated": 1,
            "authority": _measurement_authority(),
        }

    value = {
        "schema_id": schema["schema_id"],
        "research_id": adapter.RESEARCH_ID,
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


def preflight(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(market, expected_head_sha)
    forbidden = _runtime_paths_exist(result, execution, marker)
    if forbidden:
        raise ControlledRunError(f"Preflight found existing output artifacts: {forbidden}")
    return {
        "research_id": adapter.RESEARCH_ID,
        "status": "PREFLIGHT_ZERO_RESULT_PASS",
        "git_head_sha": head,
        "payload_sha256": payload_sha,
        "attempt_marker_exists": attempt.exists(),
        "result_exists": result.exists(),
        "execution_exists": execution.exists(),
        "final_marker_exists": marker.exists(),
        "actual_variants_evaluated": 0,
        "production_authorized": False,
    }


def start_attempt(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(market, expected_head_sha)
    existing = _runtime_paths_exist(attempt, result, execution, marker)
    if existing:
        raise ControlledRunError(f"Cannot start attempt with existing runtime artifacts: {existing}")
    value = {
        "research_id": adapter.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "started_at_utc": _utc_now(),
        "candidate_count": 1,
        "same_id_recomputation_allowed": False,
        "production_authorized": False,
    }
    _write_create_only(attempt, value)
    return value


def _verify_attempt(attempt: Path, *, head: str, payload_sha: str) -> dict[str, Any]:
    value = _load_json(attempt)
    if value.get("research_id") != adapter.RESEARCH_ID:
        raise ControlledRunError("RUN_ATTEMPT.marker research_id mismatch")
    if value.get("dataset_slice_id") != DATASET_SLICE_ID or value.get("payload_sha256") != payload_sha:
        raise ControlledRunError("RUN_ATTEMPT.marker dataset identity mismatch")
    if value.get("git_head_sha") != head:
        raise ControlledRunError("RUN_ATTEMPT.marker HEAD mismatch")
    if value.get("candidate_count") != 1 or value.get("same_id_recomputation_allowed") is not False:
        raise ControlledRunError("RUN_ATTEMPT.marker authority mismatch")
    return value


def evaluate_after_attempt(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, payload_sha = _verify_controlled_context(market, expected_head_sha)
    if not attempt.exists():
        raise ControlledRunError("RUN_ATTEMPT.marker must exist before portfolio evaluation")
    existing = _runtime_paths_exist(result, execution, marker)
    if existing:
        raise ControlledRunError(f"Cannot evaluate with existing output artifact: {existing}")
    attempt_value = _verify_attempt(attempt, head=head, payload_sha=payload_sha)

    value = _build_result(market, head, payload_sha)
    _write_create_only(result, value)

    execution_value = {
        "research_id": adapter.RESEARCH_ID,
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


def finalize_marker_only(*, market: Path, result: Path, execution: Path, attempt: Path, marker: Path, expected_head_sha: str) -> dict[str, Any]:
    _verify_runtime_names(result, execution, attempt, marker)
    head, interface = _verify_static_context(expected_head_sha)
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
    if execution_value.get("research_id") != adapter.RESEARCH_ID or execution_value.get("git_head_sha") != head:
        raise ControlledRunError("EXECUTION identity mismatch")
    if execution_value.get("payload_sha256") != payload_sha or execution_value.get("classification") != result_value.get("classification"):
        raise ControlledRunError("EXECUTION result identity mismatch")

    attempt_hash = _sha256_json_file(attempt)
    result_hash = _sha256_json_file(result)
    if execution_value.get("attempt_marker_sha256") != attempt_hash:
        raise ControlledRunError("Attempt marker hash mismatch")
    if execution_value.get("primary_result_sha256") != result_hash:
        raise ControlledRunError("Primary result hash mismatch")

    value = {
        "research_id": adapter.RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "payload_sha256": payload_sha,
        "git_head_sha": head,
        "finalized_at_utc": _utc_now(),
        "classification": result_value["classification"],
        "attempt_marker_sha256": attempt_hash,
        "primary_result_sha256": result_hash,
        "execution_sha256": _sha256_json_file(execution),
        "finalized_without_remeasurement": True,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
    }
    if attempt_value.get("same_id_recomputation_allowed") is not False:
        raise ControlledRunError("Attempt marker no longer forbids recomputation")
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
    parser = argparse.ArgumentParser(description="0057 controlled exactly-once execution state machine")
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
