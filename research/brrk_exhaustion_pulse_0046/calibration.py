from __future__ import annotations

"""Label-blind calibration for BRRK-EXHAUSTION-PULSE-0046.

This module may consume only the frozen S1-S4 predictor path and timestamps. It
contains no event-taxonomy, event-date, macro-episode, barrier, or outcome-window
loader. Evaluation is a separate module imported only after lock validation.
"""

import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

import numpy as np

from . import detector
from .state_input import PRIMARY_AXES, StateInput, load_predictor_path

RESEARCH_ID = "BRRK-EXHAUSTION-PULSE-0046"
PREREG_MERGE_COMMIT = "48a140a1d58cba859d537e7dee0ad399c541527a"
NULL_SEED = 460046
BLOCK_LENGTH = 7
NULL_PATHS = 5000
BURN_IN = 256
PATH_LENGTH = 1460
TOTAL_SIM_STEPS = BURN_IN + PATH_LENGTH
ARL0_TARGET = 365.0
BISECTION_ITERATIONS = 60
NO_CROSSING_CENSOR = PATH_LENGTH + 1
CALIBRATION_BATCH_SIZE = 100  # computational batching only; RNG stream is order-stable


class CalibrationInvalid(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json_sha(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _array_sha(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(np.asarray(array, dtype="<f8"))
    h = hashlib.sha256()
    h.update(json.dumps({"shape": list(arr.shape), "dtype": "<f8"}, sort_keys=True).encode("utf-8"))
    h.update(b"\n")
    h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def current_code_sha() -> str:
    env_sha = os.environ.get("GITHUB_SHA", "").strip()
    if len(env_sha) == 40:
        return env_sha
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root(), text=True
        ).strip()
    except Exception as exc:  # pragma: no cover - only unusual non-git execution
        raise CalibrationInvalid(f"cannot resolve code SHA: {exc}") from exc


def _validate_preregistration() -> dict[str, object]:
    root = repo_root()
    prereg = json.loads((root / "research/brrk_exhaustion_pulse_0046/PREREGISTRATION.json").read_text(encoding="utf-8"))
    registry = json.loads((root / "config/research_registry.json").read_text(encoding="utf-8"))
    matches = [r for r in registry.get("records", []) if r.get("research_id") == RESEARCH_ID]
    if len(matches) != 1 or matches[0] != prereg:
        raise CalibrationInvalid("0046 formal preregistration/central registry binding mismatch")
    if prereg.get("result_status") != "PREREGISTERED_NOT_RUN":
        raise CalibrationInvalid("0046 is not in PREREGISTERED_NOT_RUN state")
    if prereg.get("actual_variants_evaluated") != 0 or prereg.get("declared_variant_budget") != 1:
        raise CalibrationInvalid("0046 variant-budget state mismatch")
    return prereg


def fit_var1(values: np.ndarray) -> dict[str, np.ndarray | float]:
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != 4 or len(x) < 3 or not np.isfinite(x).all():
        raise CalibrationInvalid("VAR(1) input must be finite T x 4 predictor path")
    previous = x[:-1]
    current = x[1:]
    design = np.column_stack([np.ones(len(previous), dtype=np.float64), previous])
    beta, _, rank, _ = np.linalg.lstsq(design, current, rcond=None)
    if rank != 5:
        raise CalibrationInvalid(f"VAR(1) OLS design rank {rank}, expected 5")
    intercept = beta[0].astype(np.float64)
    transition = beta[1:].T.astype(np.float64)
    fitted = intercept[None, :] + previous @ transition.T
    residuals = current - fitted
    centered = residuals - residuals.mean(axis=0, keepdims=True)
    spectral_radius = float(np.max(np.abs(np.linalg.eigvals(transition))))
    return {
        "intercept": intercept,
        "transition": transition,
        "residuals_centered": centered,
        "spectral_radius": spectral_radius,
    }


def _bootstrap_residuals(
    residuals: np.ndarray, rng: np.random.Generator, batch: int
) -> np.ndarray:
    n_resid = len(residuals)
    blocks = int(math.ceil(TOTAL_SIM_STEPS / BLOCK_LENGTH))
    starts = rng.integers(0, n_resid, size=(batch, blocks), endpoint=False)
    offsets = np.arange(BLOCK_LENGTH, dtype=np.int64)
    idx = (starts[:, :, None] + offsets[None, None, :]) % n_resid
    idx = idx.reshape(batch, -1)[:, :TOTAL_SIM_STEPS]
    return residuals[idx]


def _simulate_batch(
    intercept: np.ndarray,
    transition: np.ndarray,
    unconditional_mean: np.ndarray,
    innovations: np.ndarray,
) -> np.ndarray:
    batch = innovations.shape[0]
    generated = np.empty((batch, TOTAL_SIM_STEPS, 4), dtype=np.float64)
    previous = np.broadcast_to(unconditional_mean, (batch, 4)).copy()
    for step in range(TOTAL_SIM_STEPS):
        current = intercept[None, :] + previous @ transition.T + innovations[:, step, :]
        generated[:, step, :] = current
        previous = current
    return generated[:, BURN_IN:, :]


def generate_null_scores(var: dict[str, np.ndarray | float]) -> np.ndarray:
    transition = np.asarray(var["transition"], dtype=np.float64)
    intercept = np.asarray(var["intercept"], dtype=np.float64)
    residuals = np.asarray(var["residuals_centered"], dtype=np.float64)
    unconditional = np.linalg.solve(np.eye(4, dtype=np.float64) - transition, intercept)
    rng = np.random.default_rng(NULL_SEED)
    scores = np.empty((NULL_PATHS, PATH_LENGTH), dtype=np.float64)
    for start in range(0, NULL_PATHS, CALIBRATION_BATCH_SIZE):
        stop = min(NULL_PATHS, start + CALIBRATION_BATCH_SIZE)
        batch = stop - start
        innovations = _bootstrap_residuals(residuals, rng, batch)
        paths = _simulate_batch(intercept, transition, unconditional, innovations)
        scores[start:stop] = detector.compute_detector(paths, details=False)
    return scores


def stopping_times(scores: np.ndarray, threshold: float) -> np.ndarray:
    s = np.asarray(scores, dtype=np.float64)
    crossed = np.isfinite(s) & (s >= float(threshold))
    any_cross = crossed.any(axis=1)
    first = np.argmax(crossed, axis=1) + 1  # 1-based from synthetic path session 1; warm-up remains on clock.
    return np.where(any_cross, first, NO_CROSSING_CENSOR).astype(np.int64)


def arl0_trunc(scores: np.ndarray, threshold: float) -> float:
    return float(stopping_times(scores, threshold).mean())


def select_threshold(scores: np.ndarray) -> tuple[float, float, float]:
    finite = scores[np.isfinite(scores)]
    if not len(finite):
        raise CalibrationInvalid("synthetic detector produced no finite scores")
    max_score = float(np.max(finite))
    low = 0.0
    high = max_score + 1.0
    if arl0_trunc(scores, high) < ARL0_TARGET:
        raise CalibrationInvalid("upper threshold bound does not satisfy frozen ARL0 target")
    for _ in range(BISECTION_ITERATIONS):
        mid = (low + high) / 2.0
        if arl0_trunc(scores, mid) >= ARL0_TARGET:
            high = mid
        else:
            low = mid
    threshold = float(high)
    return threshold, arl0_trunc(scores, threshold), max_score


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def calibration_lock_payload(state: StateInput) -> dict[str, object]:
    _validate_preregistration()
    code_sha = current_code_sha()
    values = state.axes[list(PRIMARY_AXES)].to_numpy(dtype=np.float64)
    var = fit_var1(values)
    spectral_radius = float(var["spectral_radius"])
    base: dict[str, object] = {
        "schema_version": 1,
        "research_id": RESEARCH_ID,
        "frozen_prereg_merge_commit": PREREG_MERGE_COMMIT,
        "code_sha": code_sha,
        "predictor_start": str(state.axes.index.min().date()),
        "predictor_end": str(state.axes.index.max().date()),
        "predictor_sessions": int(len(state.axes)),
        "predictor_digest": state.predictor_digest,
        "primary_axes": list(PRIMARY_AXES),
        "var1": {
            "intercept": np.asarray(var["intercept"]).tolist(),
            "transition": np.asarray(var["transition"]).tolist(),
            "spectral_radius": spectral_radius,
            "residual_data_digest": _array_sha(np.asarray(var["residuals_centered"])),
        },
        "null_bootstrap": {
            "block_length": BLOCK_LENGTH,
            "seed": NULL_SEED,
            "paths": NULL_PATHS,
            "burn_in_sessions": BURN_IN,
            "post_burn_path_sessions": PATH_LENGTH,
            "initialization": "FITTED_UNCONDITIONAL_MEAN",
            "residual_vectors_preserved_intact": True,
        },
        "false_alarm_budget": {
            "arl0_trunc_target": ARL0_TARGET,
            "no_crossing_censor": NO_CROSSING_CENSOR,
            "bisection_iterations": BISECTION_ITERATIONS,
            "stopping_time_clock": "ONE_BASED_FROM_SYNTHETIC_PATH_SESSION_1_INITIAL_DETECTOR_WARMUP_NONCROSSING_BUT_COUNTS",
        },
        "label_data_accessed": False,
        "event_taxonomy_loaded": False,
        "portfolio_economics_executed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    if spectral_radius >= 1.0:
        base["calibration_status"] = "FAIL_NULL_MODEL_NONSTATIONARY"
        base["result_status"] = "FAIL_NULL_MODEL_NONSTATIONARY"
        base["threshold"] = None
        base["synthetic_score_digest"] = None
    else:
        scores = generate_null_scores(var)
        threshold, arl, max_score = select_threshold(scores)
        base["calibration_status"] = "CALIBRATION_LOCKED"
        base["result_status"] = "CALIBRATION_PASS_LABEL_EVALUATION_ALLOWED"
        base["threshold"] = {
            "ieee754_float": threshold,
            "hex": float(threshold).hex(),
            "full_precision_decimal": format(threshold, ".17g"),
            "arl0_trunc": arl,
            "max_simulated_G": max_score,
        }
        base["synthetic_score_digest"] = _array_sha(scores)
    base["lock_payload_sha256_without_self_hash"] = _json_sha(base)
    return base


def calibrate_to_lock(path: Path) -> dict[str, object]:
    if path.exists():
        raise CalibrationInvalid(f"CALIBRATION_LOCK is create-only: {path}")
    state = load_predictor_path()
    payload = calibration_lock_payload(state)
    _atomic_write_json(path, payload)
    return payload


def validate_lock(path: Path, *, require_success: bool = True) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected_hash = payload.pop("lock_payload_sha256_without_self_hash", None)
    observed_hash = _json_sha(payload)
    payload["lock_payload_sha256_without_self_hash"] = expected_hash
    if expected_hash != observed_hash:
        raise CalibrationInvalid("CALIBRATION_LOCK payload hash mismatch")
    if payload.get("research_id") != RESEARCH_ID or payload.get("frozen_prereg_merge_commit") != PREREG_MERGE_COMMIT:
        raise CalibrationInvalid("CALIBRATION_LOCK research/prereg identity mismatch")
    if payload.get("code_sha") != current_code_sha():
        raise CalibrationInvalid("CALIBRATION_LOCK code SHA differs from current checkout")
    if payload.get("label_data_accessed") is not False or payload.get("event_taxonomy_loaded") is not False:
        raise CalibrationInvalid("CALIBRATION_LOCK does not prove label-blind calibration")
    if require_success and payload.get("calibration_status") != "CALIBRATION_LOCKED":
        raise CalibrationInvalid(f"calibration did not unlock evaluation: {payload.get('calibration_status')}")
    if require_success:
        threshold = payload.get("threshold")
        if not isinstance(threshold, dict) or float(threshold.get("arl0_trunc", -np.inf)) < ARL0_TARGET:
            raise CalibrationInvalid("CALIBRATION_LOCK ARL0 target not satisfied")
    return payload
