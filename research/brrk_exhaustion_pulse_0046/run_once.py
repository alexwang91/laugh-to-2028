from __future__ import annotations

"""Staged exactly-once interface for BRRK-EXHAUSTION-PULSE-0046.

prepare-predictors -> calibrate -> evaluate. The evaluation module is not
imported until a successful CALIBRATION_LOCK has been hash/code/ARL validated.
"""

import argparse
import importlib
import json
import os
from pathlib import Path

from . import calibration
from . import window_compat

RESEARCH_ID = "BRRK-EXHAUSTION-PULSE-0046"


class RunInvalid(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _atomic_result(path: Path, payload: dict[str, object]) -> None:
    if path.exists():
        raise RunInvalid(f"result output is create-only: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def prepare_predictors(path: Path) -> dict[str, object]:
    # Raw causal feature construction exists only in this pre-calibration step.
    module = importlib.import_module("research.brrk_exhaustion_pulse_0046.state_input")
    return module.materialize_predictor_artifact(path)


def calibrate(predictor_path: Path, lock_path: Path) -> dict[str, object]:
    return calibration.calibrate_to_lock(predictor_path, lock_path)


def evaluate(predictor_path: Path, lock_path: Path, output_path: Path) -> dict[str, object]:
    marker = repo_root() / "research/brrk_exhaustion_pulse_0046/RUN_ONCE.marker"
    if marker.exists():
        raise RunInvalid("0046 RUN_ONCE.marker already exists; same-ID rerun is forbidden")

    # CRITICAL FIREWALL: validate lock before evaluation module import.
    lock = calibration.validate_lock(lock_path, require_success=True)
    evaluation = importlib.import_module("research.brrk_exhaustion_pulse_0046.evaluation")

    # Post-lock infrastructure repair only: bind evaluation to the exact immutable
    # 0045 session-window semantics already frozen by the 0046 preregistration.
    # This does not filter events or change any denominator, detector, calibration,
    # threshold, gate, seed, pulse rule, episode rule, or taxonomy.
    evaluation._window_positions = window_compat.window_positions
    evaluation._earliest_pulse = window_compat.earliest_pulse

    result = evaluation.run_locked(predictor_path, lock)
    _atomic_result(output_path, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    p_prepare = sub.add_parser("prepare-predictors")
    p_prepare.add_argument("--predictor", type=Path, required=True)

    p_cal = sub.add_parser("calibrate")
    p_cal.add_argument("--predictor", type=Path, required=True)
    p_cal.add_argument("--lock", type=Path, required=True)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--predictor", type=Path, required=True)
    p_eval.add_argument("--lock", type=Path, required=True)
    p_eval.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.mode == "prepare-predictors":
        payload = prepare_predictors(args.predictor)
        print("BRRK_0046_PREDICTOR_ARTIFACT=" + json.dumps({
            "research_id": payload["research_id"],
            "start": payload["start"],
            "end": payload["end"],
            "sessions": payload["sessions"],
            "predictor_digest": payload["predictor_digest"],
        }, sort_keys=True, separators=(",", ":")))
    elif args.mode == "calibrate":
        payload = calibrate(args.predictor, args.lock)
        print("BRRK_0046_CALIBRATION=" + json.dumps({
            "research_id": payload["research_id"],
            "calibration_status": payload["calibration_status"],
            "result_status": payload["result_status"],
            "spectral_radius": payload["var1"]["spectral_radius"],
            "threshold": payload["threshold"],
            "lock_payload_sha256": payload["lock_payload_sha256_without_self_hash"],
        }, sort_keys=True, separators=(",", ":")))
    elif args.mode == "evaluate":
        result = evaluate(args.predictor, args.lock, args.output)
        print("BRRK_0046_RESULT=" + json.dumps({
            "research_id": result["research_id"],
            "result_status": result["result_status"],
            "point_metrics": result["point_metrics"],
            "alarm_path": {k: v for k, v in result["alarm_path"].items() if k != "pulse_dates"},
            "gates": result["gates"],
            "authority": result["authority"],
        }, sort_keys=True, separators=(",", ":")))
    else:  # pragma: no cover
        raise RunInvalid(f"unknown mode {args.mode}")


if __name__ == "__main__":
    main()
