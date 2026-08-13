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
from research.brrk_btc_cash_absolute_risk_measurement_replication_0061 import engine as scientific_engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"


class ControlledRunError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_safe(v: Any) -> Any:
    if v is None or isinstance(v, (str, bool, int)):
        return v
    if isinstance(v, (float, np.floating)):
        x = float(v)
        return x if math.isfinite(x) else None
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.ndarray):
        return [json_safe(x) for x in v.tolist()]
    if isinstance(v, Mapping):
        return {str(k): json_safe(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [json_safe(x) for x in v]
    return v


def canonical_bytes(v: Any) -> bytes:
    return json.dumps(json_safe(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha_json(v: Any) -> str:
    return hashlib.sha256(canonical_bytes(v)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def create_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        f.write(json.dumps(json_safe(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as e:
        raise ControlledRunError(f"git {' '.join(args)} failed: {e.output}") from e


def exact_keys(x: Mapping[str, Any], keys, label: str) -> None:
    if not isinstance(x, Mapping) or set(x) != set(keys):
        missing = sorted(set(keys) - set(x)) if isinstance(x, Mapping) else list(keys)
        extra = sorted(set(x) - set(keys)) if isinstance(x, Mapping) else []
        raise ControlledRunError(f"{label} keys mismatch missing={missing} extra={extra}")


def finite(v: Any, label: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
        raise ControlledRunError(f"{label} must be finite numeric")
    return float(v)


def finite_or_null(v: Any, label: str) -> float | None:
    if v is None:
        return None
    return finite(v, label)


def all_null_target_map(x: Mapping[str, Any], targets, label: str) -> None:
    exact_keys(x, targets, label)
    if any(x[k] is not None for k in targets):
        raise ControlledRunError(f"{label} must be all null after preregistered short-circuit")


def interface() -> dict:
    x = load_json(INTERFACE_PATH)
    if x.get("research_id") != scientific_engine.RESEARCH_ID or x.get("candidate_count") != 1:
        raise ControlledRunError("RUN_INTERFACE identity mismatch")
    return x


def schema() -> dict:
    x = load_json(SCHEMA_PATH)
    if x.get("research_id") != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("RESULT_SCHEMA identity mismatch")
    return x


def verify_head(expected: str) -> str:
    if not expected:
        raise ControlledRunError("--expected-head-sha required")
    head = git("rev-parse", "HEAD")
    if head != expected:
        raise ControlledRunError(f"HEAD mismatch expected={expected} actual={head}")
    return head


def verify_static(expected_head: str, market: Path) -> tuple[str, dict, dict]:
    head = verify_head(expected_head)
    i, s = interface(), schema()
    for path, expected in i["immutable_upstream_git_blobs"].items():
        actual = git("rev-parse", f"HEAD:{path}")
        if actual != expected:
            raise ControlledRunError(f"immutable blob mismatch {path}: {actual} != {expected}")
    frozen = i["frozen_market_evidence"]
    if git("rev-parse", f"HEAD:{frozen['path']}") != frozen["git_blob_sha"]:
        raise ControlledRunError("market git blob mismatch")
    if market.resolve() != (ROOT / frozen["path"]).resolve():
        raise ControlledRunError("market path mismatch")
    return head, i, s


def runtime_paths(args) -> tuple[Path, Path, Path, Path]:
    return tuple(Path(getattr(args, n)).resolve() for n in ("attempt", "result", "execution", "marker"))


def verify_runtime_names(paths) -> None:
    if tuple(p.name for p in paths) != ("RUN_ATTEMPT.marker", "PRIMARY_RESULT.json", "EXECUTION.json", "RUN_ONCE.marker"):
        raise ControlledRunError("runtime filenames differ from frozen interface")


def _validate_origin_panel(r: Mapping[str, Any], s: Mapping[str, Any]) -> None:
    rows = r["origin_panel"]
    if not isinstance(rows, list) or len(rows) != r["shared_origin_count"]:
        raise ControlledRunError("lossless origin panel count mismatch")
    fields = s["origin_panel_fields"]
    dates = []
    for j, row in enumerate(rows):
        exact_keys(row, fields, f"origin[{j}]")
        if not isinstance(row["origin_date"], str):
            raise ControlledRunError("origin date must be string")
        dates.append(row["origin_date"])
        if row["chronological_block_id"] not in (1, 2, 3, 4):
            raise ControlledRunError("block id invalid")
        for k in fields:
            if k not in ("origin_date", "chronological_block_id"):
                finite(row[k], f"origin[{j}].{k}")
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ControlledRunError("origin dates not unique chronological")
    if rows:
        if r["shared_origin_start"] != rows[0]["origin_date"] or r["shared_origin_end"] != rows[-1]["origin_date"]:
            raise ControlledRunError("origin endpoint mismatch")


def _validate_diagnostics(r: Mapping[str, Any], targets) -> None:
    if set(r["axis_target_spearman"]) != {"A1", "A2", "A3"}:
        raise ControlledRunError("axis diagnostic keys mismatch")
    for axis, vals in r["axis_target_spearman"].items():
        exact_keys(vals, targets, f"axis.{axis}")
        for k in targets:
            finite_or_null(vals[k], f"axis.{axis}.{k}")
    if not isinstance(r["axis_redundancy_matrix"], list):
        raise ControlledRunError("axis redundancy matrix invalid")
    if not isinstance(r["axis_eigenvalues"], list):
        raise ControlledRunError("axis eigenvalues invalid")
    finite_or_null(r["axis_effective_rank"], "axis_effective_rank")
    if set(r["terminal_positive_rate_by_horizon"]) != {"20", "60", "120", "240"}:
        raise ControlledRunError("terminal positive-rate keys mismatch")
    for h, v in r["terminal_positive_rate_by_horizon"].items():
        x = finite(v, f"terminal_positive_rate.{h}")
        if x < 0 or x > 1:
            raise ControlledRunError("terminal positive rate outside [0,1]")


def validate_result(r: Mapping[str, Any], s: Mapping[str, Any]) -> None:
    exact_keys(r, s["required_primary_result_keys"], "result")
    if r["schema_version"] != 1 or r["research_id"] != scientific_engine.RESEARCH_ID:
        raise ControlledRunError("result identity mismatch")
    if r["upstream_research_id"] != scientific_engine.UPSTREAM_RESEARCH_ID:
        raise ControlledRunError("upstream research identity mismatch")
    if r["dataset_slice_ref"] != scientific_engine.DATASET_SLICE_REF or r["payload_sha256"] != scientific_engine.EXPECTED_PAYLOAD_SHA256:
        raise ControlledRunError("result dataset identity mismatch")
    if r["classification"] not in s["classification_enum"]:
        raise ControlledRunError("classification outside frozen enum")
    exact_keys(r["gates"], s["gate_keys"], "gates")
    if r["gates"]["G0"] is not True:
        raise ControlledRunError("G0 must be true in persisted scientific measurement")
    if r["actual_variants_evaluated"] != 1:
        raise ControlledRunError("actual_variants_evaluated must be 1")
    if r["portfolio_economics_executed"] or r["btc_cash_gross_map_executed"]:
        raise ControlledRunError("portfolio/gross-map economics forbidden")
    if r["production_authorized"] or r["signature_authorized"] or r["order_submission_authorized"]:
        raise ControlledRunError("authority must remain false")
    if not isinstance(r["shared_origin_count"], int) or r["shared_origin_count"] < 0:
        raise ControlledRunError("shared_origin_count invalid")
    _validate_origin_panel(r, s)
    targets = s["target_keys"]
    exact_keys(r["full_sample_rho_by_target"], targets, "full_sample_rho")
    exact_keys(r["fixed_score_observed_by_target"], targets, "fixed_score_observed")
    exact_keys(r["simultaneous_lcb_by_target"], targets, "lcb")
    if set(r["temporal_block_rho_by_target"]) != {"1", "2", "3", "4"}:
        raise ControlledRunError("temporal block keys mismatch")
    for b in ("1", "2", "3", "4"):
        exact_keys(r["temporal_block_rho_by_target"][b], targets, f"temporal.{b}")
    _validate_diagnostics(r, targets)

    n = r["shared_origin_count"]
    g1 = n >= int(s["frozen_counts"]["minimum_shared_origins"])
    if r["gates"]["G1"] is not g1:
        raise ControlledRunError("G1 derivation mismatch")
    if not g1:
        if r["gates"]["G2"] is not None or r["gates"]["G3"] is not None or r["gates"]["G4"] is not None:
            raise ControlledRunError("G1 short-circuit gate mismatch")
        if r["classification"] != scientific_engine.CLASS_SUPPORT:
            raise ControlledRunError("G1 classification mismatch")
        all_null_target_map(r["full_sample_rho_by_target"], targets, "full_sample_rho")
        for b in ("1", "2", "3", "4"):
            all_null_target_map(r["temporal_block_rho_by_target"][b], targets, f"temporal.{b}")
        if r["temporal_positive_block_count"] is not None:
            raise ControlledRunError("temporal count must be null after G1 fail")
        all_null_target_map(r["fixed_score_observed_by_target"], targets, "fixed_score_observed")
        all_null_target_map(r["simultaneous_lcb_by_target"], targets, "lcb")
        if r["spearman_equivalence_max_abs_error"] is not None or r["bootstrap_q95"] is not None or r["fixed_score_panel"] is not None:
            raise ControlledRunError("fixed-score outputs must be null after G1 fail")
        return

    full = r["full_sample_rho_by_target"]
    for k in targets:
        finite_or_null(full[k], f"rho.{k}")
    g2 = all(full[k] is not None and full[k] > 0 for k in targets)
    if r["gates"]["G2"] is not g2:
        raise ControlledRunError("G2 derivation mismatch")
    if not g2:
        if r["gates"]["G3"] is not None or r["gates"]["G4"] is not None or r["classification"] != scientific_engine.CLASS_INFO:
            raise ControlledRunError("G2 short-circuit mismatch")
        for b in ("1", "2", "3", "4"):
            all_null_target_map(r["temporal_block_rho_by_target"][b], targets, f"temporal.{b}")
        if r["temporal_positive_block_count"] is not None:
            raise ControlledRunError("temporal count must be null after G2 fail")
        all_null_target_map(r["fixed_score_observed_by_target"], targets, "fixed_score_observed")
        all_null_target_map(r["simultaneous_lcb_by_target"], targets, "lcb")
        if r["spearman_equivalence_max_abs_error"] is not None or r["bootstrap_q95"] is not None or r["fixed_score_panel"] is not None:
            raise ControlledRunError("fixed-score outputs must be null after G2 fail")
        return

    for b in ("1", "2", "3", "4"):
        for k in targets:
            finite_or_null(r["temporal_block_rho_by_target"][b][k], f"temporal.{b}.{k}")
    tp = r["temporal_positive_block_count"]
    if not isinstance(tp, int) or tp < 0 or tp > 4:
        raise ControlledRunError("temporal positive block count invalid")
    derived_tp = sum(all(r["temporal_block_rho_by_target"][b][k] is not None and r["temporal_block_rho_by_target"][b][k] > 0 for k in targets) for b in ("1", "2", "3", "4"))
    if tp != derived_tp:
        raise ControlledRunError("temporal positive block count derivation mismatch")
    g3 = tp >= 3
    if r["gates"]["G3"] is not g3:
        raise ControlledRunError("G3 derivation mismatch")
    if not g3:
        if r["gates"]["G4"] is not None or r["classification"] != scientific_engine.CLASS_TEMPORAL:
            raise ControlledRunError("G3 short-circuit mismatch")
        all_null_target_map(r["fixed_score_observed_by_target"], targets, "fixed_score_observed")
        all_null_target_map(r["simultaneous_lcb_by_target"], targets, "lcb")
        if r["spearman_equivalence_max_abs_error"] is not None or r["bootstrap_q95"] is not None or r["fixed_score_panel"] is not None:
            raise ControlledRunError("fixed-score outputs must be null after G3 fail")
        return

    for k in targets:
        finite(r["fixed_score_observed_by_target"][k], f"fixed.{k}")
        finite(r["simultaneous_lcb_by_target"][k], f"lcb.{k}")
        if abs(r["fixed_score_observed_by_target"][k] - full[k]) > float(s["frozen_counts"]["spearman_equivalence_abs_tolerance"]):
            raise ControlledRunError("fixed-score/Spearman identity mismatch")
    eq = finite(r["spearman_equivalence_max_abs_error"], "spearman_equivalence_max_abs_error")
    if eq > float(s["frozen_counts"]["spearman_equivalence_abs_tolerance"]):
        raise ControlledRunError("Spearman-equivalence tolerance exceeded")
    finite(r["bootstrap_q95"], "bootstrap_q95")
    fs = r["fixed_score_panel"]
    if not isinstance(fs, list) or len(fs) != n:
        raise ControlledRunError("fixed-score panel required when G4 reached")
    fields = s["fixed_score_panel_fields"]
    for j, row in enumerate(fs):
        exact_keys(row, fields, f"fixed_score[{j}]")
        if row["origin_date"] != r["origin_panel"][j]["origin_date"]:
            raise ControlledRunError("fixed-score origin alignment mismatch")
        for k in fields:
            if k != "origin_date":
                finite(row[k], f"fixed_score[{j}].{k}")
    g4 = all(r["simultaneous_lcb_by_target"][k] > 0 for k in targets)
    if r["gates"]["G4"] is not g4:
        raise ControlledRunError("G4 derivation mismatch")
    expected_class = scientific_engine.CLASS_PASS if g4 else scientific_engine.CLASS_DEP
    if r["classification"] != expected_class:
        raise ControlledRunError("G4 classification mismatch")


def preflight(args) -> None:
    paths = runtime_paths(args)
    verify_runtime_names(paths)
    head, _, _ = verify_static(args.expected_head_sha, Path(args.market))
    print(json.dumps({"status": "PREFLIGHT_PASS_ZERO_RESULT", "scientific_head_sha": head, "market_content_read": False, "runtime_exists": {p.name: p.exists() for p in paths}}, sort_keys=True))


def start_attempt(args) -> None:
    paths = runtime_paths(args)
    verify_runtime_names(paths)
    head, i, _ = verify_static(args.expected_head_sha, Path(args.market))
    if any(p.exists() for p in paths):
        raise ControlledRunError("start-attempt requires all runtime artifacts absent")
    attempt = {
        "research_id": scientific_engine.RESEARCH_ID,
        "scientific_head_sha": head,
        "started_at": utc_now(),
        "dataset_slice_ref": i["frozen_market_evidence"]["dataset_slice_id"],
        "payload_sha256": i["frozen_market_evidence"]["payload_sha256"],
        "market_wrapper_git_blob_sha": i["frozen_market_evidence"]["git_blob_sha"],
        "scientific_engine_git_blob_sha": i["scientific_engine"]["git_blob_sha"],
        "run_interface_git_blob_sha": git("rev-parse", f"HEAD:{INTERFACE_PATH.relative_to(ROOT)}"),
        "result_schema_git_blob_sha": git("rev-parse", f"HEAD:{SCHEMA_PATH.relative_to(ROOT)}"),
        "declared_variants": 1,
        "market_content_read": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False
    }
    create_json(paths[0], attempt)
    print("RUN_ATTEMPT_CREATED=true")


def verify_attempt(path: Path, head: str, i: Mapping[str, Any]) -> dict:
    if not path.exists():
        raise ControlledRunError("attempt marker absent")
    a = load_json(path)
    if a.get("research_id") != scientific_engine.RESEARCH_ID or a.get("scientific_head_sha") != head:
        raise ControlledRunError("attempt identity mismatch")
    if a.get("payload_sha256") != i["frozen_market_evidence"]["payload_sha256"]:
        raise ControlledRunError("attempt payload mismatch")
    if any(a.get(k) is not False for k in ("same_id_rerun_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed")):
        raise ControlledRunError("attempt authority mismatch")
    return a


def evaluate_after_attempt(args) -> None:
    attempt_p, result_p, exec_p, marker_p = runtime_paths(args)
    verify_runtime_names((attempt_p, result_p, exec_p, marker_p))
    head, i, s = verify_static(args.expected_head_sha, Path(args.market))
    a = verify_attempt(attempt_p, head, i)
    if result_p.exists() or exec_p.exists() or marker_p.exists():
        raise ControlledRunError("existing partial/final runtime blocks automatic recomputation")
    evidence = load_json(Path(args.market))
    if evidence.get("payload_sha256") != i["frozen_market_evidence"]["payload_sha256"]:
        raise ControlledRunError("market wrapper payload SHA mismatch")
    frames = source_engine.frames_from_market_evidence(evidence)
    if set(frames) != {"BTC", "ETH", "SOL"}:
        raise ControlledRunError("source loader asset set mismatch")
    measurement = scientific_engine.evaluate(frames["BTC"], i["frozen_market_evidence"]["payload_sha256"], require_frozen_calendar=True, bootstrap_reps=10000)
    measurement = json_safe(measurement)
    validate_result(measurement, s)
    result_sha = sha_json(measurement)
    execution = {
        "research_id": scientific_engine.RESEARCH_ID,
        "scientific_head_sha": head,
        "attempt_started_at": a["started_at"],
        "measurement_completed_at": utc_now(),
        "dataset_slice_ref": i["frozen_market_evidence"]["dataset_slice_id"],
        "payload_sha256": i["frozen_market_evidence"]["payload_sha256"],
        "market_wrapper_git_blob_sha": i["frozen_market_evidence"]["git_blob_sha"],
        "source_loader_git_blob_sha": i["source_loader"]["git_blob_sha"],
        "scientific_engine_git_blob_sha": i["scientific_engine"]["git_blob_sha"],
        "run_interface_git_blob_sha": git("rev-parse", f"HEAD:{INTERFACE_PATH.relative_to(ROOT)}"),
        "result_schema_git_blob_sha": git("rev-parse", f"HEAD:{SCHEMA_PATH.relative_to(ROOT)}"),
        "attempt_sha256": sha_json(a),
        "primary_result_sha256": result_sha,
        "market_content_reads": 1,
        "source_loader_calls": 1,
        "scientific_engine_calls": 1,
        "actual_variants_evaluated": 1,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False
    }
    exact_keys(execution, s["execution_required_keys"], "execution")
    create_json(result_p, measurement)
    create_json(exec_p, execution)
    print(json.dumps({"classification": measurement["classification"], "shared_origin_count": measurement["shared_origin_count"], "primary_result_sha256": result_sha}, sort_keys=True))


def finalize(args) -> None:
    attempt_p, result_p, exec_p, marker_p = runtime_paths(args)
    verify_runtime_names((attempt_p, result_p, exec_p, marker_p))
    head, i, s = verify_static(args.expected_head_sha, Path(args.market))
    a = verify_attempt(attempt_p, head, i)
    if not result_p.exists() or not exec_p.exists():
        raise ControlledRunError("marker-only finalization requires result and execution")
    r, e = load_json(result_p), load_json(exec_p)
    validate_result(r, s)
    if e.get("primary_result_sha256") != sha_json(r) or e.get("attempt_sha256") != sha_json(a):
        raise ControlledRunError("runtime hash chain mismatch")
    if e.get("scientific_head_sha") != head or e.get("scientific_engine_calls") != 1 or e.get("market_content_reads") != 1 or e.get("source_loader_calls") != 1:
        raise ControlledRunError("execution invariant mismatch")
    marker = {
        "research_id": scientific_engine.RESEARCH_ID,
        "scientific_head_sha": head,
        "attempt_sha256": sha_json(a),
        "primary_result_sha256": sha_json(r),
        "execution_sha256": sha_json(e),
        "finalized_at": utc_now(),
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "market_content_read_during_finalize": False,
        "scientific_remeasurement_during_finalize": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False
    }
    exact_keys(marker, s["final_marker_required_keys"], "final_marker")
    if marker_p.exists():
        old = load_json(marker_p)
        if old.get("primary_result_sha256") != marker["primary_result_sha256"] or old.get("execution_sha256") != marker["execution_sha256"]:
            raise ControlledRunError("existing final marker hash mismatch")
        print("RUN_ONCE_ALREADY_FINALIZED=true")
        return
    create_json(marker_p, marker)
    print("RUN_ONCE_FINALIZED_WITHOUT_MARKET_READ=true")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for cmd in ("preflight", "start-attempt", "evaluate", "finalize"):
        x = sub.add_parser(cmd)
        x.add_argument("--expected-head-sha", required=True)
        x.add_argument("--market", required=True)
        x.add_argument("--attempt", default=str(HERE / "RUN_ATTEMPT.marker"))
        x.add_argument("--result", default=str(HERE / "PRIMARY_RESULT.json"))
        x.add_argument("--execution", default=str(HERE / "EXECUTION.json"))
        x.add_argument("--marker", default=str(HERE / "RUN_ONCE.marker"))
    return p


def main() -> None:
    args = parser().parse_args()
    {"preflight": preflight, "start-attempt": start_attempt, "evaluate": evaluate_after_attempt, "finalize": finalize}[args.cmd](args)


if __name__ == "__main__":
    main()
