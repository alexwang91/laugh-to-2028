from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research.brrk_leadership_4h_native_readiness_0054 import engine as upstream
from research.brrk_leadership_rotation_0048.engine import (
    FittedOffsetModel,
    fit_offset_ridge,
    prevalence_from_labels,
    raw_probability,
    sigmoid,
)

RESEARCH_ID = "BRRK-LEADERSHIP-4H-STRUCTURAL-READINESS-0055"
EXPECTED_PAYLOAD_SHA256 = upstream.EXPECTED_PAYLOAD_SHA256
SYMBOLS = upstream.SYMBOLS
RAW_FEATURE_COLUMNS = upstream.FEATURE_COLUMNS
FEATURE_COLUMNS = ("TrendLevel", "TrendAge", "StateSupport")
TARGET_HORIZONS = upstream.TARGET_HORIZONS
MAX_TARGET_BARS = upstream.MAX_TARGET_BARS
REFIT_BARS = upstream.REFIT_BARS
HAC_LAG = upstream.HAC_LAG
NUMERICAL_FLOOR = upstream.NUMERICAL_FLOOR
Z_975 = upstream.Z_975
TRAIN_P90_WIDTH_MAX = upstream.TRAIN_P90_WIDTH_MAX
TRAIN_MAX_WIDTH_MAX = upstream.TRAIN_MAX_WIDTH_MAX
CAL_MAX_WIDTH_MAX = upstream.CAL_MAX_WIDTH_MAX
CONSECUTIVE_REFITS_REQUIRED = upstream.CONSECUTIVE_REFITS_REQUIRED
METHOD_TARGET_END = upstream.METHOD_TARGET_END
RESERVED_SUFFIX_START = upstream.RESERVED_SUFFIX_START
RESERVED_BLOCK_LENGTH = upstream.RESERVED_BLOCK_LENGTH
RESERVED_REQUIRED_BLOCKS = upstream.RESERVED_REQUIRED_BLOCKS
NUMERIC_TOL = upstream.NUMERIC_TOL

TREND_LEVEL_WEIGHTS = np.asarray([0.25, 0.25, 0.25, 0.25], dtype=float)
TREND_AGE_WEIGHTS = np.asarray([0.375, 0.125, -0.125, -0.375], dtype=float)
STATE_SUPPORT_WEIGHTS = np.asarray([1.0 / 3.0] * 3, dtype=float)

ReadinessProtocolError = upstream.ReadinessProtocolError
CalibrationPrecision = upstream.CalibrationPrecision


@dataclass(frozen=True)
class TrainingPrecision:
    refit_timestamp: str
    matured_eligible_count: int
    status: str
    passed: bool
    p90_width: float | None
    max_width: float | None
    probe_widths: tuple[float, ...]
    hac_min_eigenvalue: float | None
    hessian_min_eigenvalue: float | None


def _iso(ts: pd.Timestamp) -> str:
    return pd.Timestamp(ts).tz_convert("UTC").isoformat().replace("+00:00", "Z")


def _finite_array(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if not np.isfinite(arr).all():
        raise ReadinessProtocolError(f"{name} contains non-finite values")
    return arr


def structural_transform(raw_features: Any) -> np.ndarray:
    """Apply the sole preregistered 7D -> 3D structural compression."""
    raw = _finite_array(raw_features, "raw 0054 features")
    one_dim = raw.ndim == 1
    if one_dim:
        raw = raw.reshape(1, -1)
    if raw.ndim != 2 or raw.shape[1] != 7:
        raise ReadinessProtocolError("Structural transform requires exactly seven inherited features")
    trend = raw[:, :4]
    support = raw[:, 4:]
    out = np.column_stack(
        [
            trend @ TREND_LEVEL_WEIGHTS,
            trend @ TREND_AGE_WEIGHTS,
            support @ STATE_SUPPORT_WEIGHTS,
        ]
    )
    if not np.isfinite(out).all():
        raise ReadinessProtocolError("Structural transform produced non-finite values")
    if np.max(np.abs(out)) > 1.0 + 1e-12:
        raise ReadinessProtocolError("Structural transform violated frozen [-1,1] boundedness")
    return out[0] if one_dim else out


def build_methodology_panel(frames: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Reuse 0054 raw features/targets/firewall exactly, then append fixed 3D state."""
    panel = upstream.build_methodology_panel(frames).copy()
    raw = panel.loc[:, list(RAW_FEATURE_COLUMNS)].to_numpy(dtype=float)
    structural = np.full((len(panel), 3), np.nan, dtype=float)
    raw_valid = np.isfinite(raw).all(axis=1)
    if np.any(raw_valid):
        structural[raw_valid] = structural_transform(raw[raw_valid])
    for j, name in enumerate(FEATURE_COLUMNS):
        panel[name] = structural[:, j]

    expected_valid = panel["FEATURE_VALID"].to_numpy(dtype=bool)
    actual_valid = np.isfinite(structural).all(axis=1) & panel["BTC_FAST_4H"].notna().to_numpy(dtype=bool)
    if not np.array_equal(expected_valid, actual_valid):
        raise ReadinessProtocolError("3D transform changed inherited feature-valid support")

    forbidden = ~panel["TARGET_ALLOWED"].to_numpy(dtype=bool)
    if panel.loc[forbidden, ["M", "Y"]].notna().to_numpy().any():
        raise ReadinessProtocolError("Post-firewall target leakage detected after structural transform")
    return panel


def load_frozen_payload(path: str | Path) -> dict[str, pd.DataFrame]:
    return upstream.load_frozen_payload(path)


def refit_positions(panel: pd.DataFrame) -> np.ndarray:
    return upstream.refit_positions(panel)


def matured_training_positions(panel: pd.DataFrame, refit_pos: int) -> np.ndarray:
    return upstream.matured_training_positions(panel, refit_pos)


def bartlett_hac_sum(scores: Any, lag: int = HAC_LAG) -> np.ndarray:
    return upstream.bartlett_hac_sum(scores, lag)


def calibration_probe_library() -> np.ndarray:
    return upstream.calibration_probe_library()


def training_probe_library() -> np.ndarray:
    probes = [np.zeros(3, dtype=float)]
    for j in range(3):
        for magnitude in (0.5, 1.0):
            for sign in (1.0, -1.0):
                q = np.zeros(3, dtype=float)
                q[j] = sign * magnitude
                probes.append(q)
    out = np.asarray(probes, dtype=float)
    if out.shape != (13, 3):
        raise ReadinessProtocolError("Canonical 0055 training probe library shape mismatch")
    return out


def type7_quantile(values: Any, probability: float) -> float:
    x = np.sort(_finite_array(values, "quantile values").reshape(-1))
    if len(x) == 0 or not 0.0 <= probability <= 1.0:
        raise ReadinessProtocolError("Invalid Type-7 quantile input")
    h = (len(x) - 1) * float(probability)
    lo = int(math.floor(h))
    hi = int(math.ceil(h))
    frac = h - lo
    return float((1.0 - frac) * x[lo] + frac * x[hi])


def _probability_widths_beta(beta: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    beta = _finite_array(beta, "beta")
    covariance = _finite_array(covariance, "beta covariance")
    if beta.shape != (3,) or covariance.shape != (3, 3):
        raise ReadinessProtocolError("Beta/covariance dimensions differ from frozen 3D model")
    widths: list[float] = []
    for q in training_probe_library():
        p = float(sigmoid(np.asarray([float(np.dot(beta, q))]))[0])
        grad = p * (1.0 - p) * q
        variance = float(grad @ covariance @ grad)
        if variance < -1e-12 or not math.isfinite(variance):
            raise ReadinessProtocolError("Invalid 3D beta probe variance")
        widths.append(2.0 * Z_975 * math.sqrt(max(variance, 0.0)))
    return np.asarray(widths, dtype=float)


def training_precision_at_refit(panel: pd.DataFrame, refit_pos: int) -> tuple[TrainingPrecision, FittedOffsetModel | None]:
    timestamp = _iso(panel.index[int(refit_pos)])
    train_pos = matured_training_positions(panel, int(refit_pos))
    n = int(len(train_pos))
    if n < NUMERICAL_FLOOR:
        return TrainingPrecision(timestamp, n, "INSUFFICIENT_FOR_HAC", False, None, None, tuple(), None, None), None

    X = panel.iloc[train_pos].loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)
    y = panel.iloc[train_pos]["Y"].to_numpy(dtype=float)
    pi = prevalence_from_labels(y)
    model = fit_offset_ridge(X, y, pi)
    p, _ = raw_probability(model, X)
    scores = X * (y - p)[:, None]
    omega = bartlett_hac_sum(scores, HAC_LAG)
    weights = p * (1.0 - p)
    hessian = X.T @ (X * weights[:, None]) + np.eye(3, dtype=float)
    hessian = 0.5 * (hessian + hessian.T)
    eig_h = np.linalg.eigvalsh(hessian)
    eig_o = np.linalg.eigvalsh(omega)
    if not np.isfinite(eig_h).all() or float(np.min(eig_h)) <= 0.0:
        raise ReadinessProtocolError("3D training Hessian is not positive definite")
    if not np.isfinite(eig_o).all() or float(np.min(eig_o)) < -1e-8:
        raise ReadinessProtocolError("3D training HAC covariance is not positive semidefinite")
    h_inv = np.linalg.inv(hessian)
    covariance = h_inv @ omega @ h_inv
    covariance = 0.5 * (covariance + covariance.T)
    widths = _probability_widths_beta(model.beta, covariance)
    p90 = type7_quantile(widths, 0.90)
    max_width = float(np.max(widths))
    passed = bool(p90 <= TRAIN_P90_WIDTH_MAX and max_width <= TRAIN_MAX_WIDTH_MAX)
    return (
        TrainingPrecision(
            timestamp,
            n,
            "PASS" if passed else "PRECISION_TOO_WIDE",
            passed,
            p90,
            max_width,
            tuple(float(x) for x in widths),
            float(np.min(eig_o)),
            float(np.min(eig_h)),
        ),
        model,
    )


def calibration_precision_from_pairs(
    refit_timestamp: pd.Timestamp,
    priors: np.ndarray,
    etas: np.ndarray,
    y: np.ndarray,
) -> CalibrationPrecision:
    return upstream.calibration_precision_from_pairs(refit_timestamp, priors, etas, y)


def consecutive_ready(records: list[TrainingPrecision | CalibrationPrecision]) -> bool:
    if len(records) < CONSECUTIVE_REFITS_REQUIRED:
        return False
    return all(record.passed for record in records[-CONSECUTIVE_REFITS_REQUIRED:])


def _fit_training_model(panel: pd.DataFrame, refit_pos: int) -> tuple[FittedOffsetModel, int]:
    train_pos = matured_training_positions(panel, refit_pos)
    if len(train_pos) < NUMERICAL_FLOOR:
        raise ReadinessProtocolError("3D training model requested below frozen numerical floor")
    X = panel.iloc[train_pos].loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)
    y = panel.iloc[train_pos]["Y"].to_numpy(dtype=float)
    pi = prevalence_from_labels(y)
    return fit_offset_ridge(X, y, pi), int(len(train_pos))


def measure_readiness_from_frames(frames: Mapping[str, pd.DataFrame]) -> dict[str, Any]:
    panel = build_methodology_panel(frames)
    refits = refit_positions(panel)
    if len(refits) == 0:
        raise ReadinessProtocolError("No frozen refit grid is available")

    training_records: list[TrainingPrecision] = []
    training_ready_pos: int | None = None
    for r in refits:
        record, _ = training_precision_at_refit(panel, int(r))
        training_records.append(record)
        if consecutive_ready(training_records):
            training_ready_pos = int(r)
            break

    if training_ready_pos is None:
        return {
            "research_id": RESEARCH_ID,
            "classification": "FAIL_4H_STRUCTURAL_3D_TRAINING_PRECISION_NOT_ESTABLISHED",
            "training_readiness": None,
            "calibration_readiness": None,
            "reserved_support": None,
            "training_records": [record.__dict__ for record in training_records],
            "calibration_records": [],
            "authority": _authority_record(),
        }

    shadow: list[dict[str, Any]] = []
    calibration_records: list[CalibrationPrecision] = []
    calibration_ready_pos: int | None = None
    refits_after = [int(r) for r in refits if int(r) >= training_ready_pos]

    for idx, r in enumerate(refits_after):
        model, training_n = _fit_training_model(panel, r)
        matured_shadow = [row for row in shadow if int(row["origin_pos"]) + MAX_TARGET_BARS <= r]
        if matured_shadow:
            cal = calibration_precision_from_pairs(
                pd.Timestamp(panel.index[r]),
                np.asarray([row["pi"] for row in matured_shadow], dtype=float),
                np.asarray([row["eta"] for row in matured_shadow], dtype=float),
                np.asarray([row["y"] for row in matured_shadow], dtype=float),
            )
        else:
            cal = CalibrationPrecision(_iso(panel.index[r]), 0, "INSUFFICIENT_FOR_HAC", False, None, None, tuple(), None, None)
        calibration_records.append(cal)
        if consecutive_ready(calibration_records):
            calibration_ready_pos = r
            break

        next_r = refits_after[idx + 1] if idx + 1 < len(refits_after) else len(panel)
        for pos in range(r, next_r):
            row = panel.iloc[pos]
            if not bool(row["ELIGIBLE"]) or not bool(row["FEATURE_VALID"]):
                continue
            if not bool(row["TARGET_DEFINED"]) or not bool(row["TARGET_ALLOWED"]):
                continue
            x = row.loc[list(FEATURE_COLUMNS)].to_numpy(dtype=float).reshape(1, -1)
            _, eta = raw_probability(model, x)
            shadow.append(
                {
                    "origin_pos": int(pos),
                    "pi": float(model.prevalence),
                    "eta": float(eta[0]),
                    "y": float(row["Y"]),
                    "training_n": training_n,
                }
            )

    training_ready_record = training_records[-1]
    training_readiness = {
        "timestamp": _iso(panel.index[training_ready_pos]),
        "matured_eligible_count": int(training_ready_record.matured_eligible_count),
        "p90_width": training_ready_record.p90_width,
        "max_width": training_ready_record.max_width,
        "three_consecutive_passes": True,
    }

    if calibration_ready_pos is None:
        return {
            "research_id": RESEARCH_ID,
            "classification": "FAIL_4H_STRUCTURAL_3D_CALIBRATION_PRECISION_NOT_ESTABLISHED",
            "training_readiness": training_readiness,
            "calibration_readiness": None,
            "reserved_support": None,
            "training_records": [record.__dict__ for record in training_records],
            "calibration_records": [record.__dict__ for record in calibration_records],
            "authority": _authority_record(),
        }

    cal_ready = calibration_records[-1]
    calibration_readiness = {
        "timestamp": _iso(panel.index[calibration_ready_pos]),
        "matured_shadow_count": int(cal_ready.matured_shadow_count),
        "gamma": cal_ready.gamma,
        "max_width": cal_ready.max_width,
        "three_consecutive_passes": True,
    }

    index = panel.index
    reserved_positions = np.flatnonzero(index >= RESERVED_SUFFIX_START)
    reserved_start_pos = int(reserved_positions[0]) if len(reserved_positions) else len(panel)
    activation = max(reserved_start_pos, calibration_ready_pos)
    positions = panel["ORIGIN_POS"].to_numpy(dtype=int)
    support_mask = (
        panel["ELIGIBLE"].to_numpy(dtype=bool)
        & panel["FEATURE_VALID"].to_numpy(dtype=bool)
        & panel["FULL_FUTURE_AVAILABLE"].to_numpy(dtype=bool)
        & (positions >= activation)
    )
    formal_positions = np.flatnonzero(support_mask)
    formal_rows = int(len(formal_positions))
    complete_blocks = formal_rows // RESERVED_BLOCK_LENGTH
    trailing = formal_rows % RESERVED_BLOCK_LENGTH
    reserved_support = {
        "activation_timestamp": _iso(panel.index[activation]) if activation < len(panel) else None,
        "first_formal_timestamp": _iso(panel.index[int(formal_positions[0])]) if formal_rows else None,
        "last_formal_timestamp": _iso(panel.index[int(formal_positions[-1])]) if formal_rows else None,
        "formal_rows": formal_rows,
        "complete_336_row_blocks": int(complete_blocks),
        "trailing_partial_rows": int(trailing),
        "required_blocks": RESERVED_REQUIRED_BLOCKS,
        "post_2022_target_values_read": False,
    }
    classification = (
        "PASS_4H_STRUCTURAL_3D_READINESS_ELIGIBLE_FOR_NEW_PREDICTIVE_STUDY"
        if complete_blocks >= RESERVED_REQUIRED_BLOCKS
        else "FAIL_4H_STRUCTURAL_3D_METHOD_READY_BUT_RESERVED_SUPPORT_INSUFFICIENT"
    )
    return {
        "research_id": RESEARCH_ID,
        "classification": classification,
        "training_readiness": training_readiness,
        "calibration_readiness": calibration_readiness,
        "reserved_support": reserved_support,
        "training_records": [record.__dict__ for record in training_records],
        "calibration_records": [record.__dict__ for record in calibration_records],
        "authority": _authority_record(),
    }


def _authority_record() -> dict[str, Any]:
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


def measure_frozen_readiness(payload_path: str | Path) -> dict[str, Any]:
    frames = load_frozen_payload(payload_path)
    return measure_readiness_from_frames(frames)
