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
from research.brrk_btc_risk_signal_atlas_0062 import engine as scientific_engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INTERFACE_PATH = HERE / "RUN_INTERFACE.json"
SCHEMA_PATH = HERE / "RESULT_SCHEMA.json"
RID = "BRRK-BTC-RISK-SIGNAL-ATLAS-0062"


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
    return json.loads(path.read_text(encoding="utf-8"))


def create_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        f.write(json.dumps(json_safe(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        raise ControlledRunError(f"git {' '.join(args)} failed: {exc.output}") from exc


def exact_keys(value: Mapping[str, Any], keys, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != set(keys):
        raise ControlledRunError(f"{label} keys mismatch")


def finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ControlledRunError(f"{label} must be finite numeric")
    return float(value)


def interface() -> dict:
    value = load_json(INTERFACE_PATH)
    if value.get("research_id") != RID or value.get("declared_candidate_cells") != 185 or value.get("historical_execution_attempt_budget") != 1:
        raise ControlledRunError("RUN_INTERFACE identity mismatch")
    return value


def schema() -> dict:
    value = load_json(SCHEMA_PATH)
    if value.get("research_id") != RID:
        raise ControlledRunError("RESULT_SCHEMA identity mismatch")
    return value


def verify_head(expected: str) -> str:
    if not expected:
        raise ControlledRunError("--expected-head-sha required")
    actual = git("rev-parse", "HEAD")
    if actual != expected:
        raise ControlledRunError(f"HEAD mismatch expected={expected} actual={actual}")
    return actual


def verify_static(expected_head: str, market: Path) -> tuple[str, dict, dict]:
    head = verify_head(expected_head)
    i, s = interface(), schema()
    for path, expected in i["immutable_upstream_git_blobs"].items():
        actual = git("rev-parse", f"HEAD:{path}")
        if actual != expected:
            raise ControlledRunError(f"immutable blob mismatch {path}: {actual} != {expected}")
    frozen = i["frozen_market_evidence"]
    if market.resolve() != (ROOT / frozen["path"]).resolve():
        raise ControlledRunError("market path mismatch")
    return head, i, s


def runtime_paths(args) -> tuple[Path, Path, Path, Path, Path]:
    return tuple(Path(getattr(args, n)).resolve() for n in ("attempt", "result", "evidence", "execution", "marker"))


def verify_runtime_names(paths) -> None:
    expected = ("RUN_ATTEMPT.marker", "PRIMARY_RESULT.json", "EVIDENCE.json", "EXECUTION.json", "RUN_ONCE.marker")
    if tuple(p.name for p in paths) != expected:
        raise ControlledRunError("runtime filenames differ from frozen interface")


def validate_measurement(primary: Mapping[str, Any], evidence: Mapping[str, Any], s: Mapping[str, Any]) -> None:
    for key in s["required_primary_keys"]:
        if key not in primary:
            raise ControlledRunError(f"missing primary key {key}")
    for key in s["required_evidence_keys"]:
        if key not in evidence:
            raise ControlledRunError(f"missing evidence key {key}")
    counts = s["fixed_counts"]
    if primary.get("schema_version") != 1 or primary.get("research_id") != RID:
        raise ControlledRunError("primary identity mismatch")
    if primary.get("candidate_cell_count") != counts["candidate_cell_count"] or primary.get("family_count") != counts["family_count"] or primary.get("family_track_hypothesis_count") != counts["family_track_hypothesis_count"]:
        raise ControlledRunError("frozen dimension mismatch")
    if primary.get("classification") not in s["classification_enum"]:
        raise ControlledRunError("classification outside frozen enum")
    if primary.get("data_unavailable") != s["required_data_unavailable"]:
        raise ControlledRunError("DATA_UNAVAILABLE contract mismatch")
    gates = primary.get("gates", {})
    if gates.get("G0_CONTRACT_AND_DATA_IDENTITY", {}).get("pass") is not True:
        raise ControlledRunError("G0 must pass for persisted scientific result")
    n = primary.get("common_origin_count")
    if not isinstance(n, int) or n < 0:
        raise ControlledRunError("common origin count invalid")
    if len(evidence["common_origins"]) != n or len(evidence["block_ids"]) != n:
        raise ControlledRunError("lossless common-origin evidence mismatch")
    if n:
        if primary.get("common_origin_start") != evidence["common_origins"][0] or primary.get("common_origin_end") != evidence["common_origins"][-1]:
            raise ControlledRunError("common-origin endpoints mismatch")
    sizes = primary.get("chronological_block_sizes", [])
    g1_expected = n >= counts["minimum_common_origins"] and len(sizes) == 4 and min(sizes) >= counts["minimum_per_block"]
    if gates.get("G1_COMMON_SUPPORT", {}).get("pass") is not g1_expected:
        raise ControlledRunError("G1 derivation mismatch")
    if not g1_expected:
        if primary.get("classification") != "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT":
            raise ControlledRunError("G1-fail classification mismatch")
        if "bootstrap" in evidence:
            raise ControlledRunError("bootstrap must not exist after G1 short-circuit")
        return

    tracks = primary.get("family_tracks")
    if not isinstance(tracks, Mapping) or len(tracks) != counts["family_track_hypothesis_count"]:
        raise ControlledRunError("family-track count mismatch")
    if "bootstrap" not in evidence or "block_family_target_associations" not in evidence:
        raise ControlledRunError("G1-pass evidence incomplete")
    boot = evidence["bootstrap"]
    if boot.get("replicates") != counts["bootstrap_replicates"] or boot.get("seed") != counts["bootstrap_seed"] or boot.get("block_length") != counts["bootstrap_block_length"]:
        raise ControlledRunError("bootstrap identity mismatch")
    lcbs = boot.get("simultaneous_lcbs", {})
    passing = []
    for key, row in tracks.items():
        for required in s["required_track_keys_after_g1_pass"]:
            if required not in row:
                raise ControlledRunError(f"track {key} missing {required}")
        rhos = row["full_sample_rhos"]
        if not isinstance(rhos, Mapping) or len(rhos) != 4:
            raise ControlledRunError(f"track {key} rho map invalid")
        vals = [finite(v, f"{key}.rho") for v in rhos.values()]
        g2 = all(v > 0.0 for v in vals)
        if row["G2_full_sample_sign"] is not g2:
            raise ControlledRunError(f"track {key} G2 mismatch")
        if not isinstance(row["positive_blocks"], int) or row["positive_blocks"] < 0 or row["positive_blocks"] > 4:
            raise ControlledRunError(f"track {key} positive block count invalid")
        g3 = row["positive_blocks"] >= 3
        if row["G3_temporal_recurrence"] is not g3:
            raise ControlledRunError(f"track {key} G3 mismatch")
        frac = finite(row["favorable_cell_fraction"], f"{key}.favorable_fraction")
        reps = row["representation_favorable_fractions"]
        class_ok = sum(finite(v, f"{key}.repfrac") >= 0.40 for v in reps.values()) >= 2 if len(reps) >= 2 else True
        g4 = frac >= 0.50 and class_ok
        if row["G4_parameter_plateau"] is not g4:
            raise ControlledRunError(f"track {key} G4 mismatch")
        lcb = finite(row["simultaneous_lcb"], f"{key}.lcb")
        if key not in lcbs or abs(lcb - finite(lcbs[key], f"bootstrap.{key}")) > 1e-12:
            raise ControlledRunError(f"track {key} LCB evidence mismatch")
        g5 = lcb > 0.0
        if row["G5_simultaneous_lcb"] is not g5:
            raise ControlledRunError(f"track {key} G5 mismatch")
        all_pass = g2 and g3 and g4 and g5
        if row["passes_all_information_gates"] is not all_pass:
            raise ControlledRunError(f"track {key} all-gates mismatch")
        if all_pass:
            passing.append(key)
    expected_class = "PASS_SIGNAL_ATLAS_FAMILY_INFORMATION" if passing else "FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION"
    if primary["classification"] != expected_class:
        raise ControlledRunError("final classification derivation mismatch")
    if sorted(primary.get("passing_family_tracks", [])) != sorted(passing):
        raise ControlledRunError("passing-family-track list mismatch")


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
        "research_id": RID,
        "scientific_head_sha": head,
        "started_at": utc_now(),
        "dataset_slice_ref": i["frozen_market_evidence"]["dataset_slice_id"],
        "payload_sha256": i["frozen_market_evidence"]["payload_sha256"],
        "market_wrapper_git_blob_sha": i["frozen_market_evidence"]["git_blob_sha"],
        "scientific_engine_git_blob_sha": i["scientific_engine"]["git_blob_sha"],
        "run_interface_git_blob_sha": git("rev-parse", f"HEAD:{INTERFACE_PATH.relative_to(ROOT)}"),
        "result_schema_git_blob_sha": git("rev-parse", f"HEAD:{SCHEMA_PATH.relative_to(ROOT)}"),
        "declared_candidate_cells": 185,
        "historical_execution_attempt_budget": 1,
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
    attempt = load_json(path)
    if attempt.get("research_id") != RID or attempt.get("scientific_head_sha") != head or attempt.get("payload_sha256") != i["frozen_market_evidence"]["payload_sha256"]:
        raise ControlledRunError("attempt identity mismatch")
    if any(attempt.get(k) is not False for k in ("same_id_rerun_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed")):
        raise ControlledRunError("attempt authority mismatch")
    return attempt


def evaluate_after_attempt(args) -> None:
    attempt_p, result_p, evidence_p, exec_p, marker_p = runtime_paths(args)
    verify_runtime_names((attempt_p, result_p, evidence_p, exec_p, marker_p))
    head, i, s = verify_static(args.expected_head_sha, Path(args.market))
    attempt = verify_attempt(attempt_p, head, i)
    if any(p.exists() for p in (result_p, evidence_p, exec_p, marker_p)):
        raise ControlledRunError("existing partial/final runtime blocks automatic recomputation")
    market = load_json(Path(args.market))
    if market.get("payload_sha256") != i["frozen_market_evidence"]["payload_sha256"]:
        raise ControlledRunError("market wrapper payload mismatch")
    frames = source_engine.frames_from_market_evidence(market)
    if set(frames) != {"BTC", "ETH", "SOL"}:
        raise ControlledRunError("source loader asset set mismatch")
    measurement = scientific_engine.evaluate_atlas(frames)
    primary = json_safe(measurement["primary_result"])
    evidence = json_safe(measurement["evidence"])
    validate_measurement(primary, evidence, s)
    execution = {
        "research_id": RID,
        "scientific_head_sha": head,
        "attempt_started_at": attempt["started_at"],
        "measurement_completed_at": utc_now(),
        "dataset_slice_ref": i["frozen_market_evidence"]["dataset_slice_id"],
        "payload_sha256": i["frozen_market_evidence"]["payload_sha256"],
        "market_wrapper_git_blob_sha": i["frozen_market_evidence"]["git_blob_sha"],
        "source_loader_git_blob_sha": i["source_loader"]["git_blob_sha"],
        "scientific_engine_git_blob_sha": i["scientific_engine"]["git_blob_sha"],
        "run_interface_git_blob_sha": git("rev-parse", f"HEAD:{INTERFACE_PATH.relative_to(ROOT)}"),
        "result_schema_git_blob_sha": git("rev-parse", f"HEAD:{SCHEMA_PATH.relative_to(ROOT)}"),
        "attempt_sha256": sha_json(attempt),
        "primary_result_sha256": sha_json(primary),
        "evidence_sha256": sha_json(evidence),
        "market_content_reads": 1,
        "source_loader_calls": 1,
        "scientific_engine_calls": 1,
        "historical_execution_attempts": 1,
        "actual_variants_evaluated": 185,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False
    }
    exact_keys(execution, s["execution_required_keys"], "execution")
    create_json(result_p, primary)
    create_json(evidence_p, evidence)
    create_json(exec_p, execution)
    print(json.dumps({"classification": primary["classification"], "common_origin_count": primary["common_origin_count"], "passing_family_tracks": primary.get("passing_family_tracks", []), "primary_result_sha256": execution["primary_result_sha256"]}, sort_keys=True))


def finalize(args) -> None:
    attempt_p, result_p, evidence_p, exec_p, marker_p = runtime_paths(args)
    verify_runtime_names((attempt_p, result_p, evidence_p, exec_p, marker_p))
    head, i, s = verify_static(args.expected_head_sha, Path(args.market))
    attempt = verify_attempt(attempt_p, head, i)
    if not result_p.exists() or not evidence_p.exists() or not exec_p.exists():
        raise ControlledRunError("marker-only finalization requires result/evidence/execution")
    primary, evidence, execution = load_json(result_p), load_json(evidence_p), load_json(exec_p)
    validate_measurement(primary, evidence, s)
    if execution.get("attempt_sha256") != sha_json(attempt) or execution.get("primary_result_sha256") != sha_json(primary) or execution.get("evidence_sha256") != sha_json(evidence):
        raise ControlledRunError("runtime hash chain mismatch")
    if execution.get("scientific_head_sha") != head or execution.get("market_content_reads") != 1 or execution.get("source_loader_calls") != 1 or execution.get("scientific_engine_calls") != 1 or execution.get("historical_execution_attempts") != 1 or execution.get("actual_variants_evaluated") != 185:
        raise ControlledRunError("execution count invariant mismatch")
    marker = {
        "research_id": RID,
        "scientific_head_sha": head,
        "attempt_sha256": sha_json(attempt),
        "primary_result_sha256": sha_json(primary),
        "evidence_sha256": sha_json(evidence),
        "execution_sha256": sha_json(execution),
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
        if old.get("primary_result_sha256") != marker["primary_result_sha256"] or old.get("evidence_sha256") != marker["evidence_sha256"] or old.get("execution_sha256") != marker["execution_sha256"]:
            raise ControlledRunError("existing final marker hash mismatch")
        print("RUN_ONCE_ALREADY_FINALIZED=true")
        return
    create_json(marker_p, marker)
    print("RUN_ONCE_FINALIZED_WITHOUT_MARKET_READ=true")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for command in ("preflight", "start-attempt", "evaluate", "finalize"):
        x = sub.add_parser(command)
        x.add_argument("--expected-head-sha", required=True)
        x.add_argument("--market", required=True)
        x.add_argument("--attempt", default=str(HERE / "RUN_ATTEMPT.marker"))
        x.add_argument("--result", default=str(HERE / "PRIMARY_RESULT.json"))
        x.add_argument("--evidence", default=str(HERE / "EVIDENCE.json"))
        x.add_argument("--execution", default=str(HERE / "EXECUTION.json"))
        x.add_argument("--marker", default=str(HERE / "RUN_ONCE.marker"))
    return p


def main() -> None:
    args = parser().parse_args()
    {"preflight": preflight, "start-attempt": start_attempt, "evaluate": evaluate_after_attempt, "finalize": finalize}[args.cmd](args)


if __name__ == "__main__":
    main()
