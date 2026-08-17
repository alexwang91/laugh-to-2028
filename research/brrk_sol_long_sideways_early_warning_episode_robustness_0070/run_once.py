from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research.brrk_beta_handoff_0047.engine import frames_from_market_evidence
from research.brrk_btc_sol_path_event_early_warning_0066 import engine as ref
from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import engine as opt
from research.brrk_sol_long_sideways_early_warning_episode_robustness_0070 import engine as robustness

RID = "BRRK-SOL-LONG-SIDEWAYS-EARLY-WARNING-EPISODE-ROBUSTNESS-0070"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

SOURCE_PRIMARY = ROOT / "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PRIMARY_RESULT.json"
SOURCE_EVIDENCE = ROOT / "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/EVIDENCE.json"
MARKET = ROOT / "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json"

ATTEMPT = HERE / "RUN_ATTEMPT.marker"
RESULT = HERE / "PRIMARY_RESULT.json"
EVIDENCE = HERE / "EVIDENCE.json"
EXECUTION = HERE / "EXECUTION.json"
FINAL = HERE / "RUN_ONCE.marker"

RUN_INTERFACE_BLOB = "38c898f4b6b6af36551c8016684e94956b1bb5da"
BOUNDARY_DECLARATION_BLOB = "48eb7307cda164b017fb8dc820a844755b28c81e"
QUALIFICATION_RESULT_BLOB = "8ad8cc764407f954da7c82e06ad5fa0cb3b97ca1"
MARKET_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"

PINNED_BLOBS = {
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/RUN_INTERFACE.json": RUN_INTERFACE_BLOB,
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/CONTROLLED_EXECUTION_BOUNDARY.json": BOUNDARY_DECLARATION_BLOB,
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/QUALIFICATION_RESULT.json": QUALIFICATION_RESULT_BLOB,
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/PREREGISTRATION.json": "b2618ea6e0c2bc2b321e280e8ae2611e106e909f",
    "research/brrk_sol_long_sideways_early_warning_episode_robustness_0070/engine.py": "d0c02600c7f5abd3edb91caadfd38a547cf5bd22",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PRIMARY_RESULT.json": "df00901c77d8d334d61c7c65a14b8d127e9ca8b6",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/EVIDENCE.json": "6266e6a11205e21592766546342ca5bca1dd97f0",
    "research/brrk_btc_sol_path_event_early_warning_runtime_qualified_0067/engine.py": "482868d45ccdeaa5fbad8033f122a8fcfde79ca6",
    "research/brrk_btc_sol_path_event_early_warning_0066/engine.py": "79320c83d0ce89c2c952fd0a4f7a9b7452a8e0ae",
    "research/brrk_btc_sol_path_event_early_warning_0066/event_engine.py": "651ebb824b9dc1390ed0170a4eab07a3870786aa",
    "research/brrk_btc_sol_path_event_early_warning_0066/models.py": "6b255b887f2cd8f1741086a7bf27e6254288e836",
    "research/brrk_btc_risk_signal_atlas_0062/engine.py": "cac8e946998c836d10842b9388e1e3ef345a8c0b",
    "research/brrk_beta_handoff_0047/engine.py": "059b55961e279dab41ba29b5b017de0922e4f33c",
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json": "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe",
}

REQUIRED = (robustness.PRIMARY,) + robustness.CLUSTER


class ControlledRunError(RuntimeError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True).strip()


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _verify_pinned_blobs() -> None:
    bad = []
    for path, expected in PINNED_BLOBS.items():
        actual = _git_blob(path)
        if actual != expected:
            bad.append({"path": path, "expected": expected, "actual": actual})
    if bad:
        raise ControlledRunError(f"pinned blob identity mismatch: {bad}")


def _runtime_existing() -> list[str]:
    return [p.name for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION, FINAL) if p.exists()]


def preflight(boundary_sha: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("preflight must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    existing = _runtime_existing()
    if existing:
        raise ControlledRunError(f"preflight requires zero-result state; found {existing}")
    return {
        "research_id": RID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT_GIT_IDENTITY_ONLY",
        "boundary_sha": boundary_sha,
        "qualification_result_blob": QUALIFICATION_RESULT_BLOB,
        "historical_or_0069_content_reads": 0,
        "market_payload_reads": 0,
        "market_loader_calls": 0,
        "frozen_prediction_reconstruction_calls": 0,
        "network_fetches": 0,
        "controlled_attempt_consumed": 0,
        "runtime_artifacts_present": [],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def start_attempt(boundary_sha: str, workflow_run_id: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("attempt must start on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if _runtime_existing():
        raise ControlledRunError("attempt/result artifact already exists; same-ID start forbidden")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "workflow_run_id": str(workflow_run_id),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "qualification_result_blob": QUALIFICATION_RESULT_BLOB,
        "warning_horizon_sessions": 10,
        "loeo_fold_count": 7,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _create_only(ATTEMPT, _json_bytes(marker))
    return marker


def _read_once(path: Path, counts: dict[str, int], key: str) -> bytes:
    if counts[key] != 0:
        raise ControlledRunError(f"controlled input {key} attempted more than once")
    data = path.read_bytes()
    counts[key] += 1
    return data


def _parse_market(data: bytes, counts: dict[str, int]) -> dict[str, pd.DataFrame]:
    obj = json.loads(data.decode("utf-8"))
    if obj.get("payload_sha256") != MARKET_PAYLOAD_SHA256:
        raise ControlledRunError("market evidence payload SHA256 mismatch")
    if counts["market_loader_calls"] != 0:
        raise ControlledRunError("market loader attempted more than once")
    frames = frames_from_market_evidence(obj)
    counts["market_loader_calls"] += 1
    return frames


def _parse_atrack(key: str) -> tuple[str, str, str, int]:
    parts = key.split("|")
    if len(parts) != 4 or not parts[3].startswith("L"):
        raise ControlledRunError(f"invalid selected-hyperparameter key {key}")
    return parts[0], parts[1], parts[2], int(parts[3][1:])


def _parse_track(key: str) -> tuple[str, str, int]:
    parts = key.split("|")
    if len(parts) != 3 or not parts[2].startswith("L"):
        raise ControlledRunError(f"invalid screened-signal key {key}")
    return parts[0], parts[1], int(parts[2][1:])


def _locked_selection(evidence: Mapping[str, Any]) -> tuple[dict, dict]:
    raw_params = evidence.get("validation_selected_hyperparameters")
    raw_screened = evidence.get("validation_screened_signals")
    if not isinstance(raw_params, Mapping) or not isinstance(raw_screened, Mapping):
        raise ControlledRunError("0069 evidence missing frozen validation selection")

    all_params: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for key, value in raw_params.items():
        parsed = _parse_atrack(str(key))
        if isinstance(value, Mapping):
            all_params[parsed] = dict(value)

    p08_key = ("P08_STACKED_PROBABILITY_ENSEMBLE", "SOL", "T4_LONG_SIDEWAYS", 10)
    p02_key = ("P02_RAW_ELASTIC_NET_LOGIT", "SOL", "T4_LONG_SIDEWAYS", 10)
    p03_key = ("P03_VALIDATION_SCREENED_SIGNAL_LOGIT", "SOL", "T4_LONG_SIDEWAYS", 10)
    for key in (p02_key, p03_key, p08_key):
        if key not in all_params:
            raise ControlledRunError(f"frozen required selection missing {key}")

    weights = all_params[p08_key].get("stack_weights")
    if not isinstance(weights, Mapping) or not weights:
        raise ControlledRunError("frozen P08 stack weights missing")

    selected: dict[tuple[str, str, str, int], dict[str, Any]] = {
        p02_key: all_params[p02_key],
        p03_key: all_params[p03_key],
        p08_key: all_params[p08_key],
    }
    for arch in weights:
        key = (str(arch), "SOL", "T4_LONG_SIDEWAYS", 10)
        if key not in all_params:
            raise ControlledRunError(f"P08 frozen component selection missing {key}")
        selected[key] = all_params[key]

    screened: dict[tuple[str, str, int], list[str]] = {}
    for key, value in raw_screened.items():
        parsed = _parse_track(str(key))
        if parsed == ("SOL", "T4_LONG_SIDEWAYS", 10):
            screened[parsed] = list(value)
    if ("SOL", "T4_LONG_SIDEWAYS", 10) not in screened:
        raise ControlledRunError("frozen P03 screened signals missing")
    return selected, screened


def _source_reference(primary: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    tracks = primary.get("predictor_tracks")
    if not isinstance(tracks, Mapping):
        raise ControlledRunError("0069 PRIMARY_RESULT predictor_tracks missing")
    out: dict[str, dict[str, float]] = {}
    for track in REQUIRED:
        row = tracks.get(track)
        if not isinstance(row, Mapping) or row.get("status") != "EVALUATED":
            raise ControlledRunError(f"0069 frozen source track unavailable {track}")
        if int(row.get("preferred_warning_horizon", -1)) != 10:
            raise ControlledRunError(f"0069 frozen source horizon drift {track}")
        fm = row.get("final_metrics")
        if not isinstance(fm, Mapping) or fm.get("status") != "OK":
            raise ControlledRunError(f"0069 frozen source final metrics unavailable {track}")
        needed = robustness.FROZEN[track]
        vals = {k: float(fm[k]) for k in needed}
        for k, expected in needed.items():
            if abs(vals[k] - float(expected)) > robustness.TOL:
                raise ControlledRunError(f"0069 source metric identity mismatch {track} {k}")
        out[track] = vals
    return out


def _supported_final_onsets(bundle: Any, common: pd.DatetimeIndex) -> list[pd.Timestamp]:
    q = ref.ee.qualifying_events(bundle, "SOL", "T4_LONG_SIDEWAYS")
    if q.empty:
        return []
    aidx = bundle.asset_indices["SOL"]
    risk = bundle.risk_masks[("SOL", ref.ee.target_event_type("T4_LONG_SIDEWAYS"))]
    pset = set(pd.DatetimeIndex(common))
    out: list[pd.Timestamp] = []
    for row in q.itertuples():
        date = pd.Timestamp(row.Index)
        if not (ref.FINAL_START <= date <= ref.FINAL_END):
            continue
        pos = int(row.position)
        has_precursor = any(
            pos - k >= 0 and aidx[pos - k] in pset and bool(risk.iloc[pos - k])
            for k in range(1, 11)
        )
        if has_precursor:
            out.append(date)
    return out


def _reconstruct(
    frames: Mapping[str, pd.DataFrame],
    source_evidence: Mapping[str, Any],
    counts: dict[str, int],
) -> dict[str, Any]:
    if counts["frozen_prediction_reconstruction_calls"] != 0:
        raise ControlledRunError("frozen prediction reconstruction attempted more than once")
    counts["frozen_prediction_reconstruction_calls"] += 1

    frames = ref._naive_frames(frames)
    cells, families, _, signals = ref._common_feature_objects(frames)
    bundle = ref.ee.build_event_atlas(frames)
    labels, support = ref._labels_and_support(bundle, cells.index)
    selected, screened_partial = _locked_selection(source_evidence)

    screened = {("SOL", "T4_LONG_SIDEWAYS", 10): screened_partial[("SOL", "T4_LONG_SIDEWAYS", 10)]}
    predictions, replay_audit = opt._evaluate_selected_parallel(
        cells,
        families,
        signals,
        labels,
        {a: bundle.asset_indices[a] for a in ref.ee.ASSETS},
        screened,
        selected,
        {},
    )

    fidx = ref._period_index(cells.index, ref.FINAL_START, ref.FINAL_END)
    label = labels[("SOL", "T4_LONG_SIDEWAYS", 10)].reindex(fidx).to_numpy(dtype=float)
    arrays: dict[str, np.ndarray] = {}
    for track in REQUIRED:
        arch = track.split("|", 1)[0]
        key = (arch, "SOL", "T4_LONG_SIDEWAYS", 10)
        if key not in predictions:
            raise ControlledRunError(f"frozen reconstructed prediction unavailable {track}")
        arrays[track] = predictions[key].reindex(fidx).to_numpy(dtype=float)

    mask = np.isfinite(label)
    for track in REQUIRED:
        mask &= np.isfinite(arrays[track])
    if int(mask.sum()) == 0 or len(np.unique(label[mask])) != 2:
        raise ControlledRunError("common frozen prediction support undefined")

    times = pd.DatetimeIndex(fidx[mask])
    y = label[mask].astype(int)
    locked_predictions = {track: arrays[track][mask] for track in REQUIRED}

    reproduced: dict[str, dict[str, float]] = {}
    for track in REQUIRED:
        m = robustness.metrics(y, locked_predictions[track], robustness.FROZEN[track]["PR_AUC_LIFT"])
        reproduced[track] = {k: float(m[k]) for k in robustness.FROZEN[track]}

    onsets = _supported_final_onsets(bundle, cells.index)
    if len(onsets) != 7:
        raise ControlledRunError(f"frozen final unique onset support drift expected=7 observed={len(onsets)}")
    sup = support[("SOL", "T4_LONG_SIDEWAYS", 10)]
    if int(sup.get("final_unique_onsets", -1)) != 7:
        raise ControlledRunError("0066 support reconstruction final onset count drift")

    return {
        "times": times,
        "y": y,
        "predictions": locked_predictions,
        "onsets": onsets,
        "session_axis": bundle.asset_indices["SOL"],
        "reproduced": reproduced,
        "replay_audit": replay_audit,
        "support": dict(sup),
    }


def _validate_reproduction(
    reproduced: Mapping[str, Mapping[str, float]],
    source: Mapping[str, Mapping[str, float]],
) -> None:
    for track in REQUIRED:
        for key, expected in source[track].items():
            observed = float(reproduced[track][key])
            if abs(observed - float(expected)) > robustness.TOL:
                raise ControlledRunError(
                    f"full-window reproduction mismatch {track} {key}: observed={observed} expected={expected}"
                )


def _invalid_primary(exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "research_id": RID,
        "classification": robustness.INVALID,
        "execution_valid": False,
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def evaluate(boundary_sha: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("evaluate must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if not ATTEMPT.exists():
        raise ControlledRunError("durable RUN_ATTEMPT.marker required before controlled source read")
    if any(p.exists() for p in (RESULT, EVIDENCE, EXECUTION, FINAL)):
        raise ControlledRunError("result/final artifact already exists; same-ID evaluation forbidden")
    marker = json.loads(ATTEMPT.read_text(encoding="utf-8"))
    if (
        marker.get("research_id") != RID
        or marker.get("boundary_merge_sha") != boundary_sha
        or marker.get("attempt_number") != 1
    ):
        raise ControlledRunError("RUN_ATTEMPT identity mismatch")

    counts = {
        "0069_primary_result": 0,
        "0069_evidence": 0,
        "market_evidence": 0,
        "market_loader_calls": 0,
        "frozen_prediction_reconstruction_calls": 0,
        "validation_tuning_calls": 0,
        "model_reselection_calls": 0,
        "loeo_retrain_calls": 0,
        "network_fetches": 0,
    }
    primary: dict[str, Any]
    evidence: dict[str, Any]
    failure: Exception | None = None
    try:
        primary_b = _read_once(SOURCE_PRIMARY, counts, "0069_primary_result")
        evidence_b = _read_once(SOURCE_EVIDENCE, counts, "0069_evidence")
        market_b = _read_once(MARKET, counts, "market_evidence")
        source_primary = json.loads(primary_b.decode("utf-8"))
        source_evidence = json.loads(evidence_b.decode("utf-8"))
        source_reference = _source_reference(source_primary)
        frames = _parse_market(market_b, counts)
        rec = _reconstruct(frames, source_evidence, counts)
        _validate_reproduction(rec["reproduced"], source_reference)

        result = robustness.evaluate_locked_predictions(
            times=rec["times"],
            y=rec["y"],
            predictions=rec["predictions"],
            onsets=rec["onsets"],
            reproduced=rec["reproduced"],
            session_axis=rec["session_axis"],
        )
        result["source_read_counts"] = {
            "0069_PRIMARY_RESULT": counts["0069_primary_result"],
            "0069_EVIDENCE": counts["0069_evidence"],
            "MARKET_EVIDENCE": counts["market_evidence"],
        }
        result["network_fetches"] = counts["network_fetches"]
        result["controlled_attempt_consumed"] = 1
        result["frozen_prediction_reconstruction_calls"] = counts["frozen_prediction_reconstruction_calls"]
        result["validation_tuning_calls"] = 0
        result["model_reselection_calls"] = 0
        result["loeo_retrain_calls"] = 0
        primary = {"schema_version": 1, **result}
        evidence = {
            "schema_version": 1,
            "research_id": RID,
            "source_reference": source_reference,
            "full_window_reproduction": rec["reproduced"],
            "support": rec["support"],
            "unique_onsets": [x.isoformat() for x in rec["onsets"]],
            "replay_audit": rec["replay_audit"],
            "P02_folds": result.get("P02_folds", []),
            "corroborative_cluster": result.get("corroborative_cluster", {}),
            "P02_median_retention": result.get("P02_median_retention"),
            "P02_retention_gte_0_50_count": result.get("P02_retention_gte_0_50_count"),
            "corroborative_cluster_pass": result.get("corroborative_cluster_pass"),
        }
    except Exception as exc:
        failure = exc
        primary = _invalid_primary(exc)
        evidence = {
            "schema_version": 1,
            "research_id": RID,
            "invalid_execution": {"error_type": type(exc).__name__, "error_message": str(exc)},
        }

    execution = {
        "schema_version": 1,
        "research_id": RID,
        "boundary_merge_sha": boundary_sha,
        "attempt_sha256": _sha256_file(ATTEMPT),
        "controlled_source_read_counters": {
            "0069_PRIMARY_RESULT": counts["0069_primary_result"],
            "0069_EVIDENCE": counts["0069_evidence"],
            "MARKET_EVIDENCE": counts["market_evidence"],
        },
        "market_loader_calls": counts["market_loader_calls"],
        "frozen_prediction_reconstruction_calls": counts["frozen_prediction_reconstruction_calls"],
        "validation_tuning_calls": 0,
        "model_reselection_calls": 0,
        "loeo_retrain_calls": 0,
        "network_fetches": 0,
        "classification": primary["classification"],
        "execution_valid": bool(primary.get("execution_valid", False)),
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }

    _create_only(RESULT, _json_bytes(primary))
    _create_only(EVIDENCE, _json_bytes(evidence))
    execution["primary_result_sha256"] = _sha256_file(RESULT)
    execution["evidence_sha256"] = _sha256_file(EVIDENCE)
    _create_only(EXECUTION, _json_bytes(execution))

    if failure is not None:
        return {
            "classification": robustness.INVALID,
            "error_type": type(failure).__name__,
            "error_message": str(failure),
            "execution": execution,
        }
    return {"classification": primary["classification"], "execution": execution}


def finalize(boundary_sha: str) -> dict[str, Any]:
    if _git_head() != boundary_sha:
        raise ControlledRunError("finalize must run on exact merged boundary HEAD")
    _verify_pinned_blobs()
    if FINAL.exists():
        raise ControlledRunError("RUN_ONCE.marker already exists; finalize cannot repeat")
    missing = [p.name for p in (ATTEMPT, RESULT, EVIDENCE, EXECUTION) if not p.exists()]
    if missing:
        raise ControlledRunError(f"cannot finalize incomplete durable bundle: {missing}")
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if (
        execution.get("attempt_sha256") != _sha256_file(ATTEMPT)
        or execution.get("primary_result_sha256") != _sha256_file(RESULT)
        or execution.get("evidence_sha256") != _sha256_file(EVIDENCE)
    ):
        raise ControlledRunError("durable result hash chain mismatch")
    marker = {
        "schema_version": 1,
        "research_id": RID,
        "attempt_number": 1,
        "boundary_merge_sha": boundary_sha,
        "classification": json.loads(RESULT.read_text(encoding="utf-8"))["classification"],
        "attempt_sha256": _sha256_file(ATTEMPT),
        "primary_result_sha256": _sha256_file(RESULT),
        "evidence_sha256": _sha256_file(EVIDENCE),
        "execution_sha256": _sha256_file(EXECUTION),
        "finalize_controlled_source_reads": 0,
        "finalize_market_loader_calls": 0,
        "finalize_frozen_prediction_reconstruction_calls": 0,
        "same_id_rerun_allowed": False,
        "same_id_retune_allowed": False,
        "same_id_rescue_allowed": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _create_only(FINAL, _json_bytes(marker))
    return marker


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "evaluate", "finalize"):
        p = sub.add_parser(name)
        p.add_argument("--boundary-sha", required=True)
    p = sub.add_parser("start")
    p.add_argument("--boundary-sha", required=True)
    p.add_argument("--workflow-run-id", required=True)
    args = parser.parse_args(argv)

    if args.command == "preflight":
        out = preflight(args.boundary_sha)
    elif args.command == "start":
        out = start_attempt(args.boundary_sha, args.workflow_run_id)
    elif args.command == "evaluate":
        out = evaluate(args.boundary_sha)
    else:
        out = finalize(args.boundary_sha)
    print(json.dumps(out, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
