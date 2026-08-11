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

from research.brrk_leadership_rotation_0048 import engine


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"


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
    if hasattr(value, "isoformat"):
        return value.isoformat()
    try:
        if bool(value != value):
            return None
    except Exception:
        pass
    return value


def _canonical_bytes(value: Any) -> bytes:
    safe = _json_safe(value)
    return json.dumps(safe, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_create_only(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = _json_safe(value)
    data = json.dumps(safe, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
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
    if value.get("research_id") != engine.RESEARCH_ID:
        raise RuntimeError("RUN_INTERFACE research_id mismatch")
    return value


def _schema() -> dict[str, Any]:
    value = _load_json(SCHEMA_PATH)
    if value.get("schema_id") != "BRRK-LEADERSHIP-ROTATION-0048-PRIMARY-RESULT-V1":
        raise RuntimeError("Unexpected 0048 result schema id")
    return value


def _verify_expected_head(expected_head_sha: str) -> str:
    if not expected_head_sha:
        raise RuntimeError("--expected-head-sha is mandatory for controlled execution")
    head = _git_head()
    if head != expected_head_sha:
        raise RuntimeError(f"Git HEAD mismatch: expected {expected_head_sha}, got {head}")
    return head


def _verify_upstream_blobs(interface: Mapping[str, Any]) -> None:
    expected = interface["immutable_upstream_git_blobs"]
    for path, blob_sha in expected.items():
        actual = _git_blob(str(path))
        if actual != blob_sha:
            raise RuntimeError(f"Immutable upstream blob mismatch for {path}: expected {blob_sha}, got {actual}")


def _verify_market_wrapper(market: Path, interface: Mapping[str, Any]) -> dict[str, Any]:
    configured = (ROOT / interface["frozen_market_evidence"]["path"]).resolve()
    if market.resolve() != configured:
        raise RuntimeError(f"Market path mismatch: expected {configured}, got {market.resolve()}")
    evidence = _load_json(market)
    expected_payload_sha = interface["frozen_market_evidence"]["payload_sha256"]
    actual_payload_sha = evidence.get("payload_sha256")
    if actual_payload_sha != expected_payload_sha:
        raise RuntimeError(f"Frozen market payload SHA256 mismatch: expected {expected_payload_sha}, got {actual_payload_sha}")
    return evidence


def _verify_pre_result_absence(output: Path, summary: Path, execution: Path, attempt: Path, marker: Path) -> None:
    existing = [str(p) for p in (output, summary, execution, attempt, marker) if p.exists()]
    if existing:
        raise RuntimeError(f"Controlled evaluate is create-only; existing runtime artifact(s): {existing}")


def _static_preflight(
    *,
    market: Path,
    output: Path,
    summary: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> dict[str, Any]:
    interface = _interface()
    _ = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    evidence = _verify_market_wrapper(market, interface)
    _verify_pre_result_absence(output, summary, execution, attempt, marker)
    return {
        "research_id": engine.RESEARCH_ID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT",
        "git_head_sha": head,
        "market_payload_sha256": evidence["payload_sha256"],
        "actual_variants_evaluated": 0,
        "historical_model_evaluation_started": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _row_records(eval_rows: Any, schema: Mapping[str, Any]) -> list[dict[str, Any]]:
    fields = list(schema["formal_evaluation_row_fields"])
    records: list[dict[str, Any]] = []
    for dt, row in eval_rows.iterrows():
        record: dict[str, Any] = {"date": dt.strftime("%Y-%m-%d")}
        for field in fields:
            if field == "date":
                continue
            value = row[field]
            if field == "refit_date":
                record[field] = value.strftime("%Y-%m-%d")
            else:
                record[field] = _json_safe(value)
        records.append(record)
    return records


def _score_summary(eval_rows: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if eval_rows.empty:
        proper = {
            "candidate_nll": None,
            "baseline_nll": {"B0": None, "B1": None, "B2": None, "B3": None},
            "candidate_brier": None,
            "baseline_brier": {"B0": None, "B1": None, "B2": None, "B3": None},
        }
        discrimination = {"auc": None, "balanced_accuracy": None, "direction_metrics": {}}
        return proper, discrimination

    y = eval_rows["Y"].to_numpy(dtype=int)
    p = eval_rows["p_candidate"].to_numpy(dtype=float)
    proper = {
        "candidate_nll": float(eval_rows["loss_candidate"].mean()),
        "baseline_nll": {b: float(eval_rows[f"loss_{b}"].mean()) for b in ("B0", "B1", "B2", "B3")},
        "candidate_brier": engine.brier_score(y, p),
        "baseline_brier": {b: engine.brier_score(y, eval_rows[f"p_{b}"].to_numpy(dtype=float)) for b in ("B0", "B1", "B2", "B3")},
    }
    discrimination = {
        "auc": engine.auc_score(y, p),
        "balanced_accuracy": engine.balanced_accuracy(y, p),
        "direction_metrics": engine.direction_precision_recall(y, p),
    }
    return proper, discrimination


def _confidence_diagnostics(eval_rows: Any) -> dict[str, Any]:
    unavailable = {
        "status": "NOT_AVAILABLE_FROM_FROZEN_ENGINE_NON_GATING_NO_REPLACEMENT_AUTHORITY",
        "selection_authority": False,
        "rescue_authority": False,
    }
    if eval_rows.empty:
        return {
            "spearman_point": None,
            "natural_cubic_spline": None,
            "segmented_breakpoint": None,
            "high_support": None,
            "nonselection_calibration_diagnostics": {
                "beta_calibration": unavailable,
                "isotonic_regression": unavailable,
            },
        }

    c = eval_rows["confidence"].to_numpy(dtype=float)
    z = eval_rows["Z"].to_numpy(dtype=float)
    rho = engine.spearmanr(c, z).statistic
    spline: dict[str, Any] | None = None
    if len(eval_rows) >= 6:
        coef = engine.fit_natural_spline(c, z)
        grid = np.linspace(0.0, 1.0, 101)
        spline = {
            "internal_knots": list(engine.SPLINE_INTERNAL_KNOTS),
            "coefficients": coef.tolist(),
            "grid": grid.tolist(),
            "G": engine.evaluate_natural_spline(coef, grid, derivative=0).tolist(),
            "G_prime": engine.evaluate_natural_spline(coef, grid, derivative=1).tolist(),
            "G_second": engine.evaluate_natural_spline(coef, grid, derivative=2).tolist(),
            "second_derivative_selection_authority": False,
        }
    bp = engine.fit_segmented_breakpoint(c, z, engine.sequential_full_block_ids(len(eval_rows))) if len(eval_rows) >= 3 else None
    bp_record = None
    high = None
    if bp is not None:
        bp_record = {
            "kappa": bp.kappa,
            "alpha": bp.alpha,
            "beta": bp.beta,
            "delta": bp.delta,
            "sse": bp.sse,
        }
        high = engine.high_support(eval_rows, bp.kappa)
    return {
        "spearman_point": float(rho) if np.isfinite(rho) else None,
        "natural_cubic_spline": spline,
        "segmented_breakpoint": bp_record,
        "high_support": high,
        "nonselection_calibration_diagnostics": {
            "beta_calibration": unavailable,
            "isotonic_regression": unavailable,
        },
    }


def _validate_result(result: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    missing = [key for key in schema["required_top_level_keys"] if key not in result]
    if missing:
        raise RuntimeError(f"PRIMARY_RESULT missing schema keys: {missing}")
    if result["schema_id"] != schema["schema_id"]:
        raise RuntimeError("PRIMARY_RESULT schema_id mismatch")
    if result["research_id"] != engine.RESEARCH_ID:
        raise RuntimeError("PRIMARY_RESULT research_id mismatch")
    if result["classification"] not in schema["classification_enum"]:
        raise RuntimeError(f"PRIMARY_RESULT classification is not frozen: {result['classification']}")
    fields = list(schema["formal_evaluation_row_fields"])
    for index, row in enumerate(result["formal_evaluation_rows"]):
        if set(row) != set(fields):
            raise RuntimeError(f"PRIMARY_RESULT row {index} fields differ from frozen schema")
    if result["formal_evaluation_rows_sha256"] != _sha256(result["formal_evaluation_rows"]):
        raise RuntimeError("PRIMARY_RESULT formal row digest mismatch")
    for key, expected in schema["authority_invariants"].items():
        if result["authority"].get(key) != expected:
            raise RuntimeError(f"PRIMARY_RESULT authority invariant mismatch for {key}")


def _build_result(head: str, market: Path, schema: Mapping[str, Any]) -> dict[str, Any]:
    frames = engine.load_frozen_market_evidence(market)
    panel = engine.build_feature_target_panel(frames)

    try:
        predictions = engine.walk_forward_predictions(panel)
    except engine.CalibrationUnidentifiable as exc:
        rows: list[dict[str, Any]] = []
        result = {
            "schema_id": schema["schema_id"],
            "research_id": engine.RESEARCH_ID,
            "dataset_slice_id": engine.DATASET_SLICE_ID,
            "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
            "execution_head_sha": head,
            "classification": "MEASUREMENT_INCONCLUSIVE_CALIBRATION_UNIDENTIFIABLE",
            "classification_detail": {"gates": {"G0": True, "G1": False}, "reason": str(exc)},
            "evaluation_window": {"first_formal_date": None, "last_formal_date": None},
            "counts": {
                "formal_predictions": 0,
                "formal_evaluation_rows": 0,
                "eligible_feature_valid_origins": int((panel["ELIGIBLE"] & panel["FEATURE_VALID"]).sum()),
                "target_ties": int(panel["TARGET_TIE"].sum()),
            },
            "proper_scores": _score_summary(panel.iloc[0:0])[0],
            "discrimination": _score_summary(panel.iloc[0:0])[1],
            "bootstrap": None,
            "confidence_diagnostics": _confidence_diagnostics(panel.iloc[0:0]),
            "formal_evaluation_rows": rows,
            "formal_evaluation_rows_sha256": _sha256(rows),
            "authority": {
                "development_not_independent_oos": True,
                "portfolio_economics_executed": False,
                "canonical_strategy_changed": False,
                "phase6_changed": False,
                "production_authorized": False,
                "signature_authorized": False,
                "order_submission_authorized": False,
                "same_id_rerun_allowed": False,
                "same_id_retuning_allowed": False,
                "same_id_rescue_allowed": False,
            },
        }
        _validate_result(result, schema)
        return result

    eval_rows = engine.build_evaluation_table(panel, predictions)
    support = engine.support_statistics(eval_rows) if not eval_rows.empty else {
        "full_blocks": 0,
        "eth_leader_full_blocks": 0,
        "sol_leader_full_blocks": 0,
        "pass": False,
    }

    if support["pass"]:
        bootstrap_stats = engine.bootstrap_statistics(eval_rows)
        classification_detail = engine.classify_frozen_result(eval_rows, bootstrap_stats)
        classification = classification_detail["classification"]
        bootstrap_record: dict[str, Any] | None = {
            "replicates": engine.BOOTSTRAP_REPLICATES,
            "block_length": engine.BOOTSTRAP_BLOCK_LENGTH,
            "seed": engine.BOOTSTRAP_SEED,
            "statistics": bootstrap_stats,
        }
    else:
        bootstrap_record = None
        classification = "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT"
        classification_detail = {"classification": classification, "gates": {"G0": True, "G1": False}, "support": support}

    proper, discrimination = _score_summary(eval_rows)
    rows = _row_records(eval_rows, schema)
    result = {
        "schema_id": schema["schema_id"],
        "research_id": engine.RESEARCH_ID,
        "dataset_slice_id": engine.DATASET_SLICE_ID,
        "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
        "execution_head_sha": head,
        "classification": classification,
        "classification_detail": classification_detail,
        "evaluation_window": {
            "first_formal_date": eval_rows.index.min().strftime("%Y-%m-%d") if not eval_rows.empty else None,
            "last_formal_date": eval_rows.index.max().strftime("%Y-%m-%d") if not eval_rows.empty else None,
        },
        "counts": {
            "formal_predictions": int(len(predictions)),
            "formal_evaluation_rows": int(len(eval_rows)),
            "eligible_feature_valid_origins": int((panel["ELIGIBLE"] & panel["FEATURE_VALID"]).sum()),
            "target_ties": int(panel["TARGET_TIE"].sum()),
        },
        "proper_scores": proper,
        "discrimination": discrimination,
        "bootstrap": bootstrap_record,
        "confidence_diagnostics": _confidence_diagnostics(eval_rows),
        "formal_evaluation_rows": rows,
        "formal_evaluation_rows_sha256": _sha256(rows),
        "authority": {
            "development_not_independent_oos": True,
            "portfolio_economics_executed": False,
            "canonical_strategy_changed": False,
            "phase6_changed": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
            "same_id_rerun_allowed": False,
            "same_id_retuning_allowed": False,
            "same_id_rescue_allowed": False,
        },
    }
    _validate_result(result, schema)
    return result


def _build_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    detail = result["classification_detail"]
    return {
        "research_id": result["research_id"],
        "dataset_slice_id": result["dataset_slice_id"],
        "classification": result["classification"],
        "gates": detail.get("gates", {}),
        "inference_fragile": detail.get("inference_fragile"),
        "evaluation_window": result["evaluation_window"],
        "counts": result["counts"],
        "candidate_nll": result["proper_scores"]["candidate_nll"],
        "baseline_nll": result["proper_scores"]["baseline_nll"],
        "candidate_brier": result["proper_scores"]["candidate_brier"],
        "baseline_brier": result["proper_scores"]["baseline_brier"],
        "auc": result["discrimination"]["auc"],
        "balanced_accuracy": result["discrimination"]["balanced_accuracy"],
        "market_payload_sha256": result["market_payload_sha256"],
        "execution_head_sha": result["execution_head_sha"],
        "authority": result["authority"],
    }


def preflight(
    market: Path,
    output: Path,
    summary: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> None:
    record = _static_preflight(
        market=market,
        output=output,
        summary=summary,
        execution=execution,
        attempt=attempt,
        marker=marker,
        expected_head_sha=expected_head_sha,
    )
    print("BRRK_0048_PREFLIGHT=" + json.dumps(record, sort_keys=True))


def evaluate(
    market: Path,
    output: Path,
    summary: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> None:
    preflight_record = _static_preflight(
        market=market,
        output=output,
        summary=summary,
        execution=execution,
        attempt=attempt,
        marker=marker,
        expected_head_sha=expected_head_sha,
    )
    interface = _interface()
    schema = _schema()
    head = preflight_record["git_head_sha"]

    attempt_record = {
        "research_id": engine.RESEARCH_ID,
        "status": "HISTORICAL_COMPUTATION_ATTEMPT_STARTED_NO_RERUN",
        "started_at_utc": _utc_now(),
        "git_head_sha": head,
        "dataset_slice_id": engine.DATASET_SLICE_ID,
        "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
        "actual_variants_evaluated_before_attempt": 0,
        "same_id_recomputation_allowed_after_this_marker": False,
    }
    _write_create_only(attempt, attempt_record)
    attempt_sha = _sha256(attempt_record)

    result = _build_result(head, market, schema)
    result_sha = _sha256(result)
    summary_record = _build_summary(result)
    summary_sha = _sha256(summary_record)

    execution_record = {
        "research_id": engine.RESEARCH_ID,
        "dataset_slice_id": engine.DATASET_SLICE_ID,
        "git_head_sha": head,
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "run_interface_status": interface["status"],
        "market_evidence_path": str(market),
        "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
        "attempt_marker_path": str(attempt),
        "attempt_marker_sha256": attempt_sha,
        "primary_result_path": str(output),
        "primary_result_sha256": result_sha,
        "result_summary_path": str(summary),
        "result_summary_sha256": summary_sha,
        "result_schema_id": schema["schema_id"],
        "actual_variants_evaluated": 1,
        "result_status": result["classification"],
        "bootstrap_replicates": engine.BOOTSTRAP_REPLICATES,
        "bootstrap_block_length": engine.BOOTSTRAP_BLOCK_LENGTH,
        "bootstrap_seed": engine.BOOTSTRAP_SEED,
        "portfolio_economics_executed": False,
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    execution_sha = _sha256(execution_record)

    _write_create_only(output, result)
    _write_create_only(summary, summary_record)
    _write_create_only(execution, execution_record)

    marker_record = {
        "research_id": engine.RESEARCH_ID,
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "completed_at_utc": _utc_now(),
        "git_head_sha": head,
        "market_payload_sha256": engine.EXPECTED_0047_MARKET_PAYLOAD_SHA256,
        "attempt_marker_sha256": attempt_sha,
        "primary_result_sha256": result_sha,
        "result_summary_sha256": summary_sha,
        "execution_sha256": execution_sha,
        "result_status": result["classification"],
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _write_create_only(marker, marker_record)
    print(
        "BRRK_0048_RESULT="
        + json.dumps(
            {
                "result_status": result["classification"],
                "primary_result_sha256": result_sha,
                "result_summary_sha256": summary_sha,
                "execution_sha256": execution_sha,
                "attempt_marker_sha256": attempt_sha,
                "git_head_sha": head,
            },
            sort_keys=True,
        )
    )


def recover_marker(
    output: Path,
    summary: Path,
    execution: Path,
    attempt: Path,
    marker: Path,
    expected_head_sha: str,
) -> None:
    interface = _interface()
    schema = _schema()
    head = _verify_expected_head(expected_head_sha)
    _verify_upstream_blobs(interface)
    if marker.exists():
        raise RuntimeError(f"Final RUN_ONCE marker already exists: {marker}")
    required = (output, summary, execution, attempt)
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise RuntimeError(f"Marker recovery requires a complete existing result bundle; missing: {missing}")

    result = _load_json(output)
    summary_record = _load_json(summary)
    execution_record = _load_json(execution)
    attempt_record = _load_json(attempt)
    _validate_result(result, schema)

    if result["execution_head_sha"] != head or execution_record.get("git_head_sha") != head or attempt_record.get("git_head_sha") != head:
        raise RuntimeError("Recovery bundle git-head mismatch")
    if result["market_payload_sha256"] != interface["frozen_market_evidence"]["payload_sha256"]:
        raise RuntimeError("Recovery result market payload mismatch")

    result_sha = _sha256(result)
    summary_sha = _sha256(summary_record)
    attempt_sha = _sha256(attempt_record)
    if execution_record.get("primary_result_sha256") != result_sha:
        raise RuntimeError("Recovery primary-result hash mismatch")
    if execution_record.get("result_summary_sha256") != summary_sha:
        raise RuntimeError("Recovery summary hash mismatch")
    if execution_record.get("attempt_marker_sha256") != attempt_sha:
        raise RuntimeError("Recovery attempt-marker hash mismatch")
    execution_sha = _sha256(execution_record)

    marker_record = {
        "research_id": engine.RESEARCH_ID,
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "completed_at_utc": _utc_now(),
        "recovered_without_model_recomputation": True,
        "git_head_sha": head,
        "market_payload_sha256": result["market_payload_sha256"],
        "attempt_marker_sha256": attempt_sha,
        "primary_result_sha256": result_sha,
        "result_summary_sha256": summary_sha,
        "execution_sha256": execution_sha,
        "result_status": result["classification"],
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _write_create_only(marker, marker_record)
    print("BRRK_0048_MARKER_RECOVERY=" + json.dumps({"status": "RECOVERED_WITHOUT_RECOMPUTATION", "execution_sha256": execution_sha}, sort_keys=True))


def _add_common_paths(parser: argparse.ArgumentParser, *, include_market: bool) -> None:
    if include_market:
        parser.add_argument("--market", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--execution", required=True, type=Path)
    parser.add_argument("--attempt", required=True, type=Path)
    parser.add_argument("--marker", required=True, type=Path)
    parser.add_argument("--expected-head-sha", required=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash-bound exactly-once runner for BRRK Leadership Rotation 0048")
    subparsers = parser.add_subparsers(dest="command", required=True)

    pre = subparsers.add_parser("preflight")
    _add_common_paths(pre, include_market=True)

    run = subparsers.add_parser("evaluate")
    _add_common_paths(run, include_market=True)

    recover = subparsers.add_parser("recover-marker")
    _add_common_paths(recover, include_market=False)

    args = parser.parse_args()
    if args.command == "preflight":
        preflight(args.market, args.output, args.summary, args.execution, args.attempt, args.marker, args.expected_head_sha)
    elif args.command == "evaluate":
        evaluate(args.market, args.output, args.summary, args.execution, args.attempt, args.marker, args.expected_head_sha)
    elif args.command == "recover-marker":
        recover_marker(args.output, args.summary, args.execution, args.attempt, args.marker, args.expected_head_sha)
    else:  # pragma: no cover
        raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
