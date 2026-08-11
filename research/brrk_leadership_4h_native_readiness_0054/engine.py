from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research.brrk_leadership_rotation_0048.engine import (
    FittedOffsetModel,
    TemperatureFit,
    fit_offset_ridge,
    fit_temperature,
    logit_probability,
    prevalence_from_labels,
    raw_probability,
    sigmoid,
)

RESEARCH_ID = "BRRK-LEADERSHIP-4H-NATIVE-READINESS-0054"
EXPECTED_PAYLOAD_SHA256 = "471b54991ae648b79433285f073ea7bc813663319b6e2389c1682dad1a319135"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
BAR_INTERVAL_MS = 14_400_000
FEATURE_COLUMNS = ("K1", "K2", "K3", "K4", "Persistence360", "Position720", "Participation")
TARGET_HORIZONS = (84, 168, 336)
MAX_TARGET_BARS = 336
REFIT_BARS = 168
MAX_FEATURE_BARS = 1440
BTC_HORIZONS = (120, 360, 720, 1440)
BTC_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
EPSILON = 1e-12
HAC_LAG = 335
NUMERICAL_FLOOR = 672
Z_975 = 1.959963984540054
TRAIN_P90_WIDTH_MAX = 0.10
TRAIN_MAX_WIDTH_MAX = 0.20
CAL_MAX_WIDTH_MAX = 0.10
CONSECUTIVE_REFITS_REQUIRED = 3
METHOD_TARGET_END = pd.Timestamp("2022-12-31T20:00:00Z")
RESERVED_SUFFIX_START = pd.Timestamp("2023-01-01T00:00:00Z")
RESERVED_BLOCK_LENGTH = 336
RESERVED_REQUIRED_BLOCKS = 12
NUMERIC_TOL = 1e-12


class ReadinessProtocolError(RuntimeError):
    pass


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


@dataclass(frozen=True)
class CalibrationPrecision:
    refit_timestamp: str
    matured_shadow_count: int
    status: str
    passed: bool
    gamma: float | None
    max_width: float | None
    probe_widths: tuple[float, ...]
    hac_variance: float | None
    curvature: float | None


def _iso(ts: pd.Timestamp) -> str:
    return pd.Timestamp(ts).tz_convert("UTC").isoformat().replace("+00:00", "Z")


def _finite_array(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if not np.isfinite(arr).all():
        raise ReadinessProtocolError(f"{name} contains non-finite values")
    return arr


def _validate_payload_bytes(raw: bytes) -> dict[str, Any]:
    sha = hashlib.sha256(raw).hexdigest()
    if sha != EXPECTED_PAYLOAD_SHA256:
        raise ReadinessProtocolError(f"0054 frozen payload SHA256 mismatch: {sha}")
    payload = json.loads(raw)
    if payload.get("interval") != "4h":
        raise ReadinessProtocolError("0054 payload interval must be 4h")
    symbols = payload.get("symbols")
    if not isinstance(symbols, dict) or tuple(symbols.keys()) != SYMBOLS:
        raise ReadinessProtocolError("0054 payload symbol ordering/identity mismatch")
    return payload


def load_frozen_payload(path: str | Path) -> dict[str, pd.DataFrame]:
    """Load the immutable 0053 4h payload. Controlled execution only.

    Implementation tests must not call this function on the real payload.
    """
    payload = _validate_payload_bytes(Path(path).read_bytes())
    frames: dict[str, pd.DataFrame] = {}
    for symbol in SYMBOLS:
        rows = payload["symbols"][symbol]
        if not isinstance(rows, list) or not rows:
            raise ReadinessProtocolError(f"Empty frozen rows for {symbol}")
        parsed: list[dict[str, Any]] = []
        previous: int | None = None
        for row in rows:
            if not isinstance(row, list) or len(row) < 12:
                raise ReadinessProtocolError(f"Malformed kline row for {symbol}")
            open_ms = int(row[0])
            if open_ms % BAR_INTERVAL_MS != 0:
                raise ReadinessProtocolError(f"Non-4h aligned timestamp for {symbol}")
            if previous is not None and open_ms - previous != BAR_INTERVAL_MS:
                raise ReadinessProtocolError(f"Internal 4h gap for {symbol}")
            previous = open_ms
            close = float(row[4])
            quote_volume = float(row[7])
            if not math.isfinite(close) or close <= 0.0:
                raise ReadinessProtocolError(f"Invalid close for {symbol}")
            if not math.isfinite(quote_volume) or quote_volume <= 0.0:
                raise ReadinessProtocolError(f"Invalid quote_volume for {symbol}")
            parsed.append(
                {
                    "open_time": pd.to_datetime(open_ms, unit="ms", utc=True),
                    "close": close,
                    "quote_volume": quote_volume,
                }
            )
        frame = pd.DataFrame(parsed).set_index("open_time")
        if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
            raise ReadinessProtocolError(f"Invalid index for {symbol}")
        frames[symbol] = frame

    common = frames[SYMBOLS[0]].index
    for symbol in SYMBOLS[1:]:
        common = common.intersection(frames[symbol].index)
    common = common.sort_values()
    if len(common) == 0:
        raise ReadinessProtocolError("Empty common 4h index")
    expected = pd.date_range(common[0], common[-1], freq="4h", tz="UTC")
    if not common.equals(expected):
        raise ReadinessProtocolError("Common BTC/ETH/SOL index must be contiguous 4h UTC")
    return {symbol: frames[symbol].loc[common].copy() for symbol in SYMBOLS}


def trend_score_4h(price: pd.Series) -> pd.Series:
    price = pd.Series(price, copy=False).astype(float)
    values = price.to_numpy(dtype=float)
    if price.empty or not np.isfinite(values).all() or (values <= 0.0).any():
        raise ReadinessProtocolError("BTC price series must be finite and positive")
    lr = np.log(price).diff()
    out = pd.Series(0.0, index=price.index, dtype=float)
    valid = pd.Series(True, index=price.index, dtype=bool)
    for horizon, weight in zip(BTC_HORIZONS, BTC_WEIGHTS):
        momentum = np.log(price / price.shift(horizon))
        scale = lr.rolling(horizon, min_periods=horizon).std(ddof=1) * math.sqrt(horizon)
        component = np.tanh(momentum / scale)
        out = out + weight * component
        valid &= component.notna()
    return out.where(valid)


def _rolling_position(z: pd.Series, window: int = 720) -> pd.Series:
    lo = z.rolling(window, min_periods=window).min()
    hi = z.rolling(window, min_periods=window).max()
    span = hi - lo
    raw = 2.0 * (z - lo) / span - 1.0
    return raw.where(span.ne(0.0), 0.0)


def _target_score_at(log_price: np.ndarray, origin: int, horizon: int) -> float:
    if origin < 0 or origin + horizon >= len(log_price):
        raise ReadinessProtocolError("Target path is out of range")
    future = log_price[origin + 1 : origin + horizon + 1] - log_price[origin]
    if len(future) != horizon or not np.isfinite(future).all():
        raise ReadinessProtocolError("Target path contains invalid values")
    return float((2.0 / (horizon * (horizon + 1.0))) * np.sum(future))


def build_methodology_panel(frames: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    if tuple(frames.keys()) != SYMBOLS:
        raise ReadinessProtocolError(f"Frames must contain exact symbol order {SYMBOLS}")
    index = frames[SYMBOLS[0]].index
    if not isinstance(index, pd.DatetimeIndex) or index.tz is None or index.has_duplicates or not index.is_monotonic_increasing:
        raise ReadinessProtocolError("Frames require a unique monotonic timezone-aware index")
    if not all(index.equals(frames[s].index) for s in SYMBOLS[1:]):
        raise ReadinessProtocolError("Frames must share identical common index")
    if len(index) < MAX_FEATURE_BARS + MAX_TARGET_BARS + 1:
        raise ReadinessProtocolError("Insufficient rows for frozen feature/target horizons")

    for symbol in SYMBOLS:
        for col in ("close", "quote_volume"):
            if col not in frames[symbol].columns:
                raise ReadinessProtocolError(f"Missing {symbol} {col}")
            values = np.asarray(frames[symbol][col], dtype=float)
            if not np.isfinite(values).all() or (values <= 0.0).any():
                raise ReadinessProtocolError(f"{symbol} {col} must be finite and positive")

    prices = pd.DataFrame({s: frames[s]["close"].astype(float) for s in SYMBOLS}, index=index)
    logp = np.log(prices)
    z = logp["SOLUSDT"] - logp["ETHUSDT"]
    d = z.diff()
    sigma1440 = d.rolling(1440, min_periods=1440).std(ddof=1)
    denom = sigma1440 + EPSILON

    panel = pd.DataFrame(index=index)
    panel["BTC_FAST_4H"] = trend_score_4h(prices["BTCUSDT"])
    panel["z"] = z
    panel["d"] = d
    panel["sigma1440"] = sigma1440

    bucket_specs = {
        "K1": (0, 120),
        "K2": (120, 240),
        "K3": (360, 360),
        "K4": (720, 720),
    }
    for name, (shift_bars, length) in bucket_specs.items():
        block_sum = d.shift(shift_bars).rolling(length, min_periods=length).sum()
        panel[name] = np.tanh(block_sum / (denom * math.sqrt(length)))

    panel["Persistence360"] = np.sign(d).rolling(360, min_periods=360).mean()
    panel["Position720"] = _rolling_position(z, 720)

    activity: dict[str, pd.Series] = {}
    for symbol in ("ETHUSDT", "SOLUSDT"):
        qv = frames[symbol]["quote_volume"].astype(float)
        med120 = qv.rolling(120, min_periods=120).median()
        med720 = qv.rolling(720, min_periods=720).median()
        activity[symbol] = np.log((med120 + EPSILON) / (med720 + EPSILON))
    panel["Participation"] = np.tanh(activity["SOLUSDT"] - activity["ETHUSDT"])

    feature_matrix = panel.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)
    panel["FEATURE_VALID"] = np.isfinite(feature_matrix).all(axis=1) & panel["BTC_FAST_4H"].notna()
    panel["ELIGIBLE"] = panel["FEATURE_VALID"] & panel["BTC_FAST_4H"].ge(0.0)

    positions = np.arange(len(index), dtype=int)
    panel["ORIGIN_POS"] = positions
    panel["FULL_FUTURE_AVAILABLE"] = positions + MAX_TARGET_BARS < len(index)
    target_allowed = np.zeros(len(index), dtype=bool)
    for pos in range(len(index)):
        j = pos + MAX_TARGET_BARS
        if j < len(index) and pd.Timestamp(index[j]) <= METHOD_TARGET_END:
            target_allowed[pos] = True
    panel["TARGET_ALLOWED"] = target_allowed
    panel["TARGET_FIREWALLED"] = ~panel["TARGET_ALLOWED"]
    panel["M"] = np.nan
    panel["Y"] = np.nan
    panel["TARGET_TIE"] = False

    log_eth = logp["ETHUSDT"].to_numpy(dtype=float)
    log_sol = logp["SOLUSDT"].to_numpy(dtype=float)
    allowed_positions = np.flatnonzero(target_allowed)
    for pos in allowed_positions:
        eth_scores = [_target_score_at(log_eth, int(pos), h) for h in TARGET_HORIZONS]
        sol_scores = [_target_score_at(log_sol, int(pos), h) for h in TARGET_HORIZONS]
        margin = float(np.mean(sol_scores) - np.mean(eth_scores))
        panel.iat[int(pos), panel.columns.get_loc("M")] = margin
        if margin > 0.0:
            panel.iat[int(pos), panel.columns.get_loc("Y")] = 1.0
        elif margin < 0.0:
            panel.iat[int(pos), panel.columns.get_loc("Y")] = 0.0
        else:
            panel.iat[int(pos), panel.columns.get_loc("TARGET_TIE")] = True
    panel["TARGET_DEFINED"] = panel["TARGET_ALLOWED"] & panel["Y"].notna()

    # Hard firewall invariant: no target value exists where a 336-bar path would
    # extend past the preregistered methodology cutoff.
    forbidden = ~panel["TARGET_ALLOWED"].to_numpy(dtype=bool)
    if panel.loc[forbidden, ["M", "Y"]].notna().to_numpy().any():
        raise ReadinessProtocolError("Post-firewall target leakage detected")
    return panel


def refit_positions(panel: pd.DataFrame) -> np.ndarray:
    valid = panel["FEATURE_VALID"].to_numpy(dtype=bool)
    first = np.flatnonzero(valid)
    if len(first) == 0:
        return np.asarray([], dtype=int)
    anchor = int(first[0])
    return np.arange(anchor, len(panel), REFIT_BARS, dtype=int)


def matured_training_positions(panel: pd.DataFrame, refit_pos: int) -> np.ndarray:
    pos = panel["ORIGIN_POS"].to_numpy(dtype=int)
    mask = (
        panel["ELIGIBLE"].to_numpy(dtype=bool)
        & panel["FEATURE_VALID"].to_numpy(dtype=bool)
        & panel["TARGET_DEFINED"].to_numpy(dtype=bool)
        & panel["TARGET_ALLOWED"].to_numpy(dtype=bool)
        & (pos + MAX_TARGET_BARS <= int(refit_pos))
    )
    return np.flatnonzero(mask)


def bartlett_hac_sum(scores: Any, lag: int = HAC_LAG) -> np.ndarray:
    g = _finite_array(scores, "HAC scores")
    if g.ndim == 1:
        g = g.reshape(-1, 1)
    if g.ndim != 2 or g.shape[0] < 1:
        raise ReadinessProtocolError("HAC scores require a non-empty 2d array")
    if lag < 0 or g.shape[0] <= lag:
        raise ReadinessProtocolError("HAC sample must exceed frozen lag")
    centered = g - np.mean(g, axis=0, keepdims=True)
    omega = centered.T @ centered
    for k in range(1, lag + 1):
        weight = 1.0 - k / float(lag + 1)
        cross = centered[k:].T @ centered[:-k]
        omega = omega + weight * (cross + cross.T)
    omega = 0.5 * (omega + omega.T)
    if not np.isfinite(omega).all():
        raise ReadinessProtocolError("HAC covariance is non-finite")
    return omega


def training_probe_library() -> np.ndarray:
    probes = [np.zeros(len(FEATURE_COLUMNS), dtype=float)]
    for j in range(len(FEATURE_COLUMNS)):
        for magnitude in (0.5, 1.0):
            for sign in (1.0, -1.0):
                q = np.zeros(len(FEATURE_COLUMNS), dtype=float)
                q[j] = sign * magnitude
                probes.append(q)
    out = np.asarray(probes, dtype=float)
    if out.shape != (29, 7):
        raise ReadinessProtocolError("Canonical training probe library shape mismatch")
    return out


def calibration_probe_library() -> np.ndarray:
    return np.asarray([-2.0, -1.0, -0.5, -0.2, 0.2, 0.5, 1.0, 2.0], dtype=float)


def _probability_widths_beta(beta: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    beta = _finite_array(beta, "beta")
    covariance = _finite_array(covariance, "beta covariance")
    if beta.shape != (7,) or covariance.shape != (7, 7):
        raise ReadinessProtocolError("Beta/covariance dimensions differ from frozen 7-feature model")
    widths: list[float] = []
    for q in training_probe_library():
        p = float(sigmoid(np.asarray([float(np.dot(beta, q))]))[0])
        grad = p * (1.0 - p) * q
        variance = float(grad @ covariance @ grad)
        if variance < -1e-12 or not math.isfinite(variance):
            raise ReadinessProtocolError("Invalid beta probe variance")
        variance = max(variance, 0.0)
        widths.append(2.0 * Z_975 * math.sqrt(variance))
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
    hessian = X.T @ (X * weights[:, None]) + np.eye(X.shape[1], dtype=float)
    hessian = 0.5 * (hessian + hessian.T)
    eig_h = np.linalg.eigvalsh(hessian)
    eig_o = np.linalg.eigvalsh(omega)
    if not np.isfinite(eig_h).all() or float(np.min(eig_h)) <= 0.0:
        raise ReadinessProtocolError("Training Hessian is not positive definite")
    if not np.isfinite(eig_o).all() or float(np.min(eig_o)) < -1e-8:
        raise ReadinessProtocolError("Training HAC covariance is not positive semidefinite")
    h_inv = np.linalg.inv(hessian)
    covariance = h_inv @ omega @ h_inv
    covariance = 0.5 * (covariance + covariance.T)
    widths = _probability_widths_beta(model.beta, covariance)
    p90 = float(np.quantile(widths, 0.90, method="linear"))
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
    priors = _finite_array(priors, "calibration priors").reshape(-1)
    etas = _finite_array(etas, "calibration etas").reshape(-1)
    y = _finite_array(y, "calibration labels").reshape(-1)
    if not (priors.shape == etas.shape == y.shape):
        raise ReadinessProtocolError("Calibration pair shapes mismatch")
    n = int(len(y))
    timestamp = _iso(pd.Timestamp(refit_timestamp))
    if n < NUMERICAL_FLOOR:
        return CalibrationPrecision(timestamp, n, "INSUFFICIENT_FOR_HAC", False, None, None, tuple(), None, None)
    fit: TemperatureFit = fit_temperature(priors, etas, y)
    if not fit.identified or fit.gamma is None:
        return CalibrationPrecision(timestamp, n, f"UNIDENTIFIED:{fit.reason}", False, None, None, tuple(), None, None)
    gamma = float(fit.gamma)
    offsets = logit_probability(priors)
    p = sigmoid(offsets + gamma * etas)
    scores = etas * (y - p)
    omega_matrix = bartlett_hac_sum(scores.reshape(-1, 1), HAC_LAG)
    omega = float(omega_matrix[0, 0])
    curvature = float(np.sum((etas ** 2) * p * (1.0 - p)))
    if not math.isfinite(omega) or omega < -1e-8:
        raise ReadinessProtocolError("Calibration HAC variance is invalid")
    if not math.isfinite(curvature) or curvature <= NUMERIC_TOL:
        raise ReadinessProtocolError("Calibration curvature is invalid")
    variance_gamma = max(omega, 0.0) / (curvature ** 2)
    widths: list[float] = []
    for eta_probe in calibration_probe_library():
        pc = float(sigmoid(np.asarray([gamma * eta_probe]))[0])
        grad = pc * (1.0 - pc) * eta_probe
        variance = float((grad ** 2) * variance_gamma)
        widths.append(2.0 * Z_975 * math.sqrt(max(variance, 0.0)))
    max_width = float(np.max(widths))
    passed = bool(max_width <= CAL_MAX_WIDTH_MAX)
    return CalibrationPrecision(
        timestamp,
        n,
        "PASS" if passed else "PRECISION_TOO_WIDE",
        passed,
        gamma,
        max_width,
        tuple(float(x) for x in widths),
        float(max(omega, 0.0)),
        curvature,
    )


def consecutive_ready(records: list[TrainingPrecision | CalibrationPrecision]) -> bool:
    if len(records) < CONSECUTIVE_REFITS_REQUIRED:
        return False
    return all(record.passed for record in records[-CONSECUTIVE_REFITS_REQUIRED:])


def _fit_training_model(panel: pd.DataFrame, refit_pos: int) -> tuple[FittedOffsetModel, int]:
    train_pos = matured_training_positions(panel, refit_pos)
    if len(train_pos) < NUMERICAL_FLOOR:
        raise ReadinessProtocolError("Training model requested below frozen numerical floor")
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
    training_ready_model: FittedOffsetModel | None = None
    for r in refits:
        record, model = training_precision_at_refit(panel, int(r))
        training_records.append(record)
        if consecutive_ready(training_records):
            training_ready_pos = int(r)
            training_ready_model = model if model is not None else _fit_training_model(panel, int(r))[0]
            break

    if training_ready_pos is None:
        return {
            "research_id": RESEARCH_ID,
            "classification": "FAIL_4H_NATIVE_TRAINING_PRECISION_NOT_ESTABLISHED",
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
            # Shadow labels are created only inside the methodology prefix.
            # Reserved/post-cutoff target values are never consulted.
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
            "classification": "FAIL_4H_NATIVE_CALIBRATION_PRECISION_NOT_ESTABLISHED",
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
        "PASS_4H_NATIVE_READINESS_METHOD_ELIGIBLE_FOR_NEW_PREDICTIVE_STUDY"
        if complete_blocks >= RESERVED_REQUIRED_BLOCKS
        else "FAIL_4H_NATIVE_METHOD_READY_BUT_RESERVED_SUPPORT_INSUFFICIENT"
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
        "canonical_strategy_changed": False,
        "phase6_changed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def measure_frozen_readiness(payload_path: str | Path) -> dict[str, Any]:
    frames = load_frozen_payload(payload_path)
    return measure_readiness_from_frames(frames)
