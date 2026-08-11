from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize
from scipy.stats import rankdata, spearmanr

from research.brrk_beta_handoff_0047.engine import (
    FAST_WEIGHTS,
    frames_from_market_evidence,
    trend_score,
)

RESEARCH_ID = "BRRK-LEADERSHIP-ROTATION-0048"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
EXPECTED_0047_MARKET_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
FROZEN_START = pd.Timestamp("2020-08-11")
FROZEN_END = pd.Timestamp("2026-08-02")
ASSETS = ("BTC", "ETH", "SOL")
TARGET_HORIZONS = (14, 28, 56)
MAX_TARGET_HORIZON_DAYS = 56
FEATURE_COLUMNS = ("K1", "K2", "K3", "K4", "Persistence60", "Position120", "Participation")
RIDGE_LAMBDA = 1.0
INITIAL_TRAIN_SUPPORT = 365
INITIAL_CALIBRATION_SUPPORT = 365
REFIT_CALENDAR_DAYS = 28
EPSILON = 1e-12
PROBABILITY_CLIP = 1e-12
BOOTSTRAP_BLOCK_LENGTH = 56
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 4_292_549_012
SPLINE_BOUNDARY_KNOTS = (0.0, 1.0)
SPLINE_INTERNAL_KNOTS = (0.25, 0.50, 0.75)
BREAKPOINT_RANGE = (0.20, 0.80)
BREAKPOINT_MIN_SIDE_SHARE = 0.10
BREAKPOINT_MIN_FULL_BLOCKS_PER_SIDE = 4
BREAKPOINT_MIN_VALID_BOOTSTRAP_SHARE = 0.90
BREAKPOINT_MAX_CI_WIDTH = 0.20
BREAKPOINT_MIN_POSITIVE_DELTA_SHARE = 0.95
MIN_FULL_EVAL_BLOCKS = 12
MIN_DIRECTION_FULL_BLOCKS = 3
TEMPORAL_REQUIRED_WINS = 3
MIN_EPISODE_DURATION = 14
HIGH_MIN_COVERAGE = 0.10
HIGH_MIN_FULL_BLOCKS = 6
HIGH_MIN_EPISODES_PER_DIRECTION = 2
NUMERIC_TOL = 1e-10
OPT_TOL = 1e-12


class FrozenProtocolError(RuntimeError):
    pass


class CalibrationUnidentifiable(FrozenProtocolError):
    pass


@dataclass(frozen=True)
class FittedOffsetModel:
    beta: np.ndarray
    prevalence: float


@dataclass(frozen=True)
class TemperatureFit:
    gamma: float | None
    identified: bool
    reason: str


@dataclass(frozen=True)
class BreakpointFit:
    kappa: float
    alpha: float
    beta: float
    delta: float
    sse: float


def _as_float_array(values: Any) -> np.ndarray:
    out = np.asarray(values, dtype=float)
    if not np.isfinite(out).all():
        raise FrozenProtocolError("Non-finite numerical input")
    return out


def sigmoid(x: Any) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.empty_like(x, dtype=float)
    positive = x >= 0
    out[positive] = 1.0 / (1.0 + np.exp(-x[positive]))
    ex = np.exp(x[~positive])
    out[~positive] = ex / (1.0 + ex)
    return out


def logit_probability(p: Any) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    if ((p <= 0.0) | (p >= 1.0) | ~np.isfinite(p)).any():
        raise FrozenProtocolError("Probability offset must be finite and strictly inside (0,1)")
    return np.log(p) - np.log1p(-p)


def clip_for_score(p: Any) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), PROBABILITY_CLIP, 1.0 - PROBABILITY_CLIP)


def nll_losses(y: Any, p: Any) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    p = clip_for_score(p)
    if y.shape != p.shape:
        raise FrozenProtocolError("NLL y/p shape mismatch")
    return -(y * np.log(p) + (1.0 - y) * np.log1p(-p))


def brier_score(y: Any, p: Any) -> float:
    y = _as_float_array(y)
    p = _as_float_array(p)
    if y.shape != p.shape:
        raise FrozenProtocolError("Brier y/p shape mismatch")
    return float(np.mean((p - y) ** 2))


def auc_score(y: Any, score: Any) -> float:
    y = np.asarray(y, dtype=int)
    score = _as_float_array(score)
    if y.shape != score.shape:
        raise FrozenProtocolError("AUC y/score shape mismatch")
    n1 = int(np.sum(y == 1))
    n0 = int(np.sum(y == 0))
    if n1 == 0 or n0 == 0:
        return float("nan")
    ranks = rankdata(score, method="average")
    rank_sum_pos = float(ranks[y == 1].sum())
    return float((rank_sum_pos - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def balanced_accuracy(y: Any, p: Any) -> float:
    y = np.asarray(y, dtype=int)
    pred = (np.asarray(p, dtype=float) > 0.5).astype(int)
    recalls: list[float] = []
    for cls in (0, 1):
        mask = y == cls
        if not mask.any():
            return float("nan")
        recalls.append(float(np.mean(pred[mask] == cls)))
    return float(np.mean(recalls))


def direction_precision_recall(y: Any, p: Any) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    pred = (np.asarray(p, dtype=float) > 0.5).astype(int)
    out: dict[str, float] = {}
    for cls, name in ((0, "ETH"), (1, "SOL")):
        true_mask = y == cls
        pred_mask = pred == cls
        out[f"{name}_recall"] = float(np.mean(pred[true_mask] == cls)) if true_mask.any() else float("nan")
        out[f"{name}_precision"] = float(np.mean(y[pred_mask] == cls)) if pred_mask.any() else float("nan")
    return out


def load_frozen_market_evidence(path: str | Path) -> dict[str, pd.DataFrame]:
    evidence = json.loads(Path(path).read_text(encoding="utf-8"))
    if evidence.get("payload_sha256") != EXPECTED_0047_MARKET_PAYLOAD_SHA256:
        raise FrozenProtocolError("0047 market payload SHA256 does not match frozen 0048 identity")
    frames = frames_from_market_evidence(evidence)
    common = frames["BTC"].index
    if common.min() != FROZEN_START or common.max() != FROZEN_END:
        raise FrozenProtocolError(
            f"Frozen 0048 common history mismatch: {common.min()}..{common.max()} expected {FROZEN_START}..{FROZEN_END}"
        )
    expected = pd.date_range(FROZEN_START, FROZEN_END, freq="D")
    if not common.equals(expected):
        raise FrozenProtocolError("Frozen 0048 history must be contiguous daily UTC observations")
    return frames


def _path_integrated(log_price: pd.Series, horizon: int, *, forward: bool) -> pd.Series:
    if horizon <= 0:
        raise FrozenProtocolError("Path horizon must be positive")
    total = pd.Series(0.0, index=log_price.index, dtype=float)
    valid = pd.Series(True, index=log_price.index)
    for u in range(1, horizon + 1):
        term = log_price.shift(-u) - log_price if forward else log_price - log_price.shift(u)
        total = total + term.fillna(0.0)
        valid &= term.notna()
    scale = 2.0 / (horizon * (horizon + 1.0))
    return (scale * total).where(valid)


def _rolling_position(z: pd.Series) -> pd.Series:
    lo = z.rolling(120, min_periods=120).min()
    hi = z.rolling(120, min_periods=120).max()
    span = hi - lo
    raw = 2.0 * (z - lo) / span - 1.0
    return raw.where(span.ne(0.0), 0.0)


def _causal_episode_columns(index: pd.DatetimeIndex, eligible: pd.Series, rrel60: pd.Series) -> pd.DataFrame:
    episode_id = pd.Series(pd.NA, index=index, dtype="Int64")
    episode_state = pd.Series(pd.NA, index=index, dtype="string")
    current_state: int | None = None
    current_id = 0
    for dt in index:
        if not bool(eligible.loc[dt]) or pd.isna(rrel60.loc[dt]):
            current_state = None
            continue
        raw = int(np.sign(float(rrel60.loc[dt])))
        if raw == 0:
            if current_state is None:
                continue
            state = current_state
        else:
            state = raw
        if current_state is None or state != current_state:
            current_id += 1
            current_state = state
        episode_id.loc[dt] = current_id
        episode_state.loc[dt] = "SOL" if current_state > 0 else "ETH"
    duration = pd.Series(pd.NA, index=index, dtype="Int64")
    valid_ids = episode_id.dropna().unique().tolist()
    for eid in valid_ids:
        mask = episode_id.eq(eid)
        duration.loc[mask] = int(mask.sum())
    return pd.DataFrame(
        {"EPISODE_ID": episode_id, "EPISODE_STATE": episode_state, "EPISODE_DURATION": duration},
        index=index,
    )


def build_feature_target_panel(frames: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    if set(frames) != set(ASSETS):
        raise FrozenProtocolError(f"Frames must contain exactly {ASSETS}")
    indexes = [frames[a].index for a in ASSETS]
    if not all(indexes[0].equals(idx) for idx in indexes[1:]):
        raise FrozenProtocolError("BTC/ETH/SOL frames must share an identical daily index")
    index = indexes[0]
    if not isinstance(index, pd.DatetimeIndex) or index.has_duplicates or not index.is_monotonic_increasing:
        raise FrozenProtocolError("Invalid common daily index")
    for asset in ASSETS:
        for col in ("close", "quote_volume"):
            if col not in frames[asset].columns:
                raise FrozenProtocolError(f"Missing {asset} {col}")
            values = np.asarray(frames[asset][col], dtype=float)
            if not np.isfinite(values).all() or (values <= 0.0).any():
                raise FrozenProtocolError(f"{asset} {col} must be finite and strictly positive")

    prices = pd.DataFrame({asset: frames[asset]["close"].astype(float) for asset in ASSETS}, index=index)
    logp = np.log(prices)
    z = logp["SOL"] - logp["ETH"]
    d = z.diff()
    sigma240 = d.rolling(240, min_periods=240).std(ddof=1)
    denom = sigma240 + EPSILON

    panel = pd.DataFrame(index=index)
    panel["BTC_FAST"] = trend_score(prices["BTC"], FAST_WEIGHTS)
    panel["ELIGIBLE"] = panel["BTC_FAST"].notna() & panel["BTC_FAST"].ge(0.0)
    panel["z"] = z
    panel["d"] = d
    panel["sigma240"] = sigma240

    bucket_specs = {
        "K1": (0, 20),
        "K2": (20, 40),
        "K3": (60, 60),
        "K4": (120, 120),
    }
    for name, (shift_days, length) in bucket_specs.items():
        block_sum = d.shift(shift_days).rolling(length, min_periods=length).sum()
        panel[name] = np.tanh(block_sum / (denom * math.sqrt(length)))

    panel["Persistence60"] = np.sign(d).rolling(60, min_periods=60).mean()
    panel["Position120"] = _rolling_position(z)

    activities: dict[str, pd.Series] = {}
    for asset in ("ETH", "SOL"):
        qv = frames[asset]["quote_volume"].astype(float)
        med20 = qv.rolling(20, min_periods=20).median()
        med120 = qv.rolling(120, min_periods=120).median()
        activities[asset] = np.log((med20 + EPSILON) / (med120 + EPSILON))
    panel["Participation"] = np.tanh(activities["SOL"] - activities["ETH"])

    past_scores: dict[str, list[pd.Series]] = {"ETH": [], "SOL": []}
    future_scores: dict[str, list[pd.Series]] = {"ETH": [], "SOL": []}
    for asset in ("ETH", "SOL"):
        for horizon in TARGET_HORIZONS:
            past = _path_integrated(logp[asset], horizon, forward=False)
            future = _path_integrated(logp[asset], horizon, forward=True)
            panel[f"PAST_A_{asset}_{horizon}"] = past
            panel[f"FUTURE_A_{asset}_{horizon}"] = future
            past_scores[asset].append(past)
            future_scores[asset].append(future)
        panel[f"PAST_L_{asset}"] = pd.concat(past_scores[asset], axis=1).mean(axis=1, skipna=False)
        panel[f"FUTURE_L_{asset}"] = pd.concat(future_scores[asset], axis=1).mean(axis=1, skipna=False)

    panel["H_LAGGED_LEADER"] = np.sign(panel["PAST_L_SOL"] - panel["PAST_L_ETH"])
    panel["RM60"] = np.tanh((z - z.shift(60)) / (denom * math.sqrt(60.0)))
    panel["M"] = panel["FUTURE_L_SOL"] - panel["FUTURE_L_ETH"]
    panel["TARGET_TIE"] = panel["M"].eq(0.0) & panel["M"].notna()
    panel["Y"] = np.where(panel["M"].gt(0.0), 1.0, np.where(panel["M"].lt(0.0), 0.0, np.nan))
    panel["TARGET_DEFINED"] = panel["Y"].notna()
    panel["FEATURE_VALID"] = np.isfinite(panel.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float)).all(axis=1)

    rrel60 = z - z.shift(60)
    panel["RREL60"] = rrel60
    episodes = _causal_episode_columns(index, panel["ELIGIBLE"], rrel60)
    panel = panel.join(episodes)
    return panel


def prevalence_from_labels(y: Any) -> float:
    y = np.asarray(y, dtype=float)
    if y.size == 0 or not np.isfinite(y).all():
        raise FrozenProtocolError("Prevalence requires non-empty finite labels")
    n_sol = float(np.sum(y == 1.0))
    n_eth = float(np.sum(y == 0.0))
    if n_sol + n_eth != float(y.size):
        raise FrozenProtocolError("Prevalence labels must be binary")
    return float((n_sol + 1.0) / (n_sol + n_eth + 2.0))


def fit_offset_ridge(X: Any, y: Any, prevalence: float) -> FittedOffsetModel:
    X = _as_float_array(X)
    y = _as_float_array(y)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    if X.ndim != 2 or y.ndim != 1 or X.shape[0] != y.shape[0] or X.shape[0] == 0:
        raise FrozenProtocolError("Invalid offset-ridge training shapes")
    if not np.isin(y, [0.0, 1.0]).all():
        raise FrozenProtocolError("Offset-ridge labels must be binary")
    offset = float(logit_probability(np.asarray([prevalence]))[0])

    def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
        logits = offset + X @ beta
        loss = float(np.sum(np.logaddexp(0.0, logits) - y * logits) + 0.5 * RIDGE_LAMBDA * np.dot(beta, beta))
        prob = sigmoid(logits)
        grad = X.T @ (prob - y) + RIDGE_LAMBDA * beta
        return loss, grad

    result = minimize(
        lambda b: objective(b)[0],
        np.zeros(X.shape[1], dtype=float),
        jac=lambda b: objective(b)[1],
        method="L-BFGS-B",
        options={"ftol": OPT_TOL, "gtol": OPT_TOL, "maxiter": 5000},
    )
    if not result.success or not np.isfinite(result.x).all():
        raise FrozenProtocolError(f"Offset-ridge optimization failed: {result.message}")
    grad_norm = float(np.max(np.abs(objective(result.x)[1])))
    if grad_norm > 1e-7:
        raise FrozenProtocolError(f"Offset-ridge gradient did not converge: {grad_norm}")
    return FittedOffsetModel(beta=np.asarray(result.x, dtype=float), prevalence=float(prevalence))


def raw_probability(model: FittedOffsetModel, X: Any) -> tuple[np.ndarray, np.ndarray]:
    X = _as_float_array(X)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    eta = X @ model.beta
    offset = float(logit_probability(np.asarray([model.prevalence]))[0])
    return sigmoid(offset + eta), np.asarray(eta, dtype=float)


def fit_temperature(priors: Any, etas: Any, y: Any) -> TemperatureFit:
    priors = _as_float_array(priors)
    etas = _as_float_array(etas)
    y = _as_float_array(y)
    if priors.ndim != 1 or etas.ndim != 1 or y.ndim != 1 or not (priors.shape == etas.shape == y.shape):
        raise FrozenProtocolError("Temperature calibration shape mismatch")
    if priors.size == 0 or not np.isin(y, [0.0, 1.0]).all():
        raise FrozenProtocolError("Temperature calibration requires binary labels")
    offsets = logit_probability(priors)
    if float(np.max(np.abs(etas))) <= NUMERIC_TOL:
        return TemperatureFit(None, False, "DYNAMIC_LOGIT_HAS_ZERO_INFORMATION_VARIATION")

    def derivative(gamma: float) -> float:
        p = sigmoid(offsets + gamma * etas)
        return float(np.sum(etas * (p - y)))

    def curvature(gamma: float) -> float:
        p = sigmoid(offsets + gamma * etas)
        return float(np.sum((etas**2) * p * (1.0 - p)))

    d0 = derivative(0.0)
    if d0 >= 0.0:
        if curvature(0.0) <= NUMERIC_TOL:
            return TemperatureFit(None, False, "BOUNDARY_OPTIMUM_WITH_ZERO_CURVATURE")
        return TemperatureFit(0.0, True, "FINITE_BOUNDARY_OPTIMUM")

    asymptotic_derivative = float(
        np.sum(np.where(etas > 0.0, etas * (1.0 - y), np.where(etas < 0.0, etas * (0.0 - y), 0.0)))
    )
    if asymptotic_derivative <= NUMERIC_TOL:
        return TemperatureFit(None, False, "NO_FINITE_STABLE_MINIMIZER")

    upper = 1.0
    while derivative(upper) <= 0.0:
        upper *= 2.0
        if not np.isfinite(upper) or upper > 1e12:
            return TemperatureFit(None, False, "FAILED_TO_BRACKET_FINITE_MINIMIZER")
    gamma = float(brentq(derivative, 0.0, upper, xtol=OPT_TOL, rtol=1e-14, maxiter=1000))
    if not np.isfinite(gamma) or curvature(gamma) <= NUMERIC_TOL:
        return TemperatureFit(None, False, "FINITE_MINIMIZER_NOT_STABLE")
    return TemperatureFit(gamma, True, "FINITE_INTERIOR_OPTIMUM")


def calibrated_probability(prior: Any, eta: Any, gamma: float) -> np.ndarray:
    prior = _as_float_array(prior)
    eta = _as_float_array(eta)
    if prior.shape != eta.shape:
        raise FrozenProtocolError("Calibrated probability prior/eta shape mismatch")
    if not np.isfinite(gamma) or gamma < 0.0:
        raise FrozenProtocolError("Calibration gamma must be finite and non-negative")
    return sigmoid(logit_probability(prior) + gamma * eta)


def matured_training_mask(panel: pd.DataFrame, prediction_date: pd.Timestamp) -> pd.Series:
    cutoff = pd.Timestamp(prediction_date) - pd.Timedelta(days=MAX_TARGET_HORIZON_DAYS)
    return (
        panel["ELIGIBLE"].astype(bool)
        & panel["FEATURE_VALID"].astype(bool)
        & panel["TARGET_DEFINED"].astype(bool)
        & panel.index.to_series().le(cutoff)
    )


def _fit_models_at_refit(panel: pd.DataFrame, refit_date: pd.Timestamp) -> dict[str, Any]:
    mask = matured_training_mask(panel, refit_date)
    train = panel.loc[mask]
    if len(train) < INITIAL_TRAIN_SUPPORT:
        raise FrozenProtocolError("Refit attempted before 365 matured eligible training origins")
    y = train["Y"].to_numpy(dtype=float)
    pi = prevalence_from_labels(y)
    candidate = fit_offset_ridge(train.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=float), y, pi)
    b2 = fit_offset_ridge(train[["H_LAGGED_LEADER"]].to_numpy(dtype=float), y, pi)
    b3 = fit_offset_ridge(train[["RM60"]].to_numpy(dtype=float), y, pi)
    return {"pi": pi, "candidate": candidate, "B2": b2, "B3": b3, "training_size": int(len(train))}


def _first_shadow_anchor(panel: pd.DataFrame) -> pd.Timestamp:
    candidate_dates = panel.index[panel["ELIGIBLE"].astype(bool) & panel["FEATURE_VALID"].astype(bool)]
    for dt in candidate_dates:
        if int(matured_training_mask(panel, dt).sum()) >= INITIAL_TRAIN_SUPPORT:
            return pd.Timestamp(dt)
    raise FrozenProtocolError("No date reaches the frozen 365-origin shadow-training support")


def walk_forward_predictions(panel: pd.DataFrame) -> pd.DataFrame:
    required = {"ELIGIBLE", "FEATURE_VALID", "TARGET_DEFINED", "Y", "M", "H_LAGGED_LEADER", "RM60", *FEATURE_COLUMNS}
    missing = sorted(required - set(panel.columns))
    if missing:
        raise FrozenProtocolError(f"Panel missing walk-forward columns: {missing}")
    if not isinstance(panel.index, pd.DatetimeIndex) or panel.index.has_duplicates or not panel.index.is_monotonic_increasing:
        raise FrozenProtocolError("Walk-forward panel must use a unique monotonic DatetimeIndex")

    anchor = _first_shadow_anchor(panel)
    models: dict[str, Any] | None = None
    gammas: dict[str, float] | None = None
    current_refit: pd.Timestamp | None = None
    shadow: list[dict[str, Any]] = []
    formal: list[dict[str, Any]] = []

    for dt in panel.index[panel.index >= anchor]:
        dt = pd.Timestamp(dt)
        if (dt - anchor).days % REFIT_CALENDAR_DAYS == 0:
            models = _fit_models_at_refit(panel, dt)
            current_refit = dt
            matured_shadow = [
                row
                for row in shadow
                if row["target_defined"] and row["origin"] + pd.Timedelta(days=MAX_TARGET_HORIZON_DAYS) <= dt
            ]
            if len(matured_shadow) >= INITIAL_CALIBRATION_SUPPORT:
                y_cal = np.asarray([row["y"] for row in matured_shadow], dtype=float)
                new_gammas: dict[str, float] = {}
                for key in ("candidate", "B2", "B3"):
                    fit = fit_temperature(
                        np.asarray([row["pi"] for row in matured_shadow], dtype=float),
                        np.asarray([row[f"eta_{key}"] for row in matured_shadow], dtype=float),
                        y_cal,
                    )
                    if not fit.identified or fit.gamma is None:
                        raise CalibrationUnidentifiable(f"{key} calibration unidentified at {dt.date()}: {fit.reason}")
                    new_gammas[key] = float(fit.gamma)
                gammas = new_gammas
            else:
                gammas = None

        if models is None or current_refit is None:
            continue
        row = panel.loc[dt]
        if not bool(row["ELIGIBLE"]) or not bool(row["FEATURE_VALID"]):
            continue

        Xc = row.loc[list(FEATURE_COLUMNS)].to_numpy(dtype=float).reshape(1, -1)
        X2 = np.asarray([[float(row["H_LAGGED_LEADER"])]] , dtype=float)
        X3 = np.asarray([[float(row["RM60"])]] , dtype=float)
        _, eta_c = raw_probability(models["candidate"], Xc)
        _, eta_2 = raw_probability(models["B2"], X2)
        _, eta_3 = raw_probability(models["B3"], X3)
        y_value = float(row["Y"]) if bool(row["TARGET_DEFINED"]) else float("nan")
        shadow_row = {
            "origin": dt,
            "pi": float(models["pi"]),
            "eta_candidate": float(eta_c[0]),
            "eta_B2": float(eta_2[0]),
            "eta_B3": float(eta_3[0]),
            "target_defined": bool(row["TARGET_DEFINED"]),
            "y": y_value,
        }
        shadow.append(shadow_row)

        if gammas is None:
            continue
        prior = np.asarray([models["pi"]], dtype=float)
        p_candidate = float(calibrated_probability(prior, eta_c, gammas["candidate"])[0])
        p_b2 = float(calibrated_probability(prior, eta_2, gammas["B2"])[0])
        p_b3 = float(calibrated_probability(prior, eta_3, gammas["B3"])[0])
        formal.append(
            {
                "date": dt,
                "refit_date": current_refit,
                "training_size": int(models["training_size"]),
                "calibration_pool_size": int(
                    sum(
                        r["target_defined"]
                        and r["origin"] + pd.Timedelta(days=MAX_TARGET_HORIZON_DAYS) <= current_refit
                        for r in shadow[:-1]
                    )
                ),
                "pi": float(models["pi"]),
                "gamma_candidate": float(gammas["candidate"]),
                "gamma_B2": float(gammas["B2"]),
                "gamma_B3": float(gammas["B3"]),
                "p_candidate": p_candidate,
                "p_B0": 0.5,
                "p_B1": float(models["pi"]),
                "p_B2": p_b2,
                "p_B3": p_b3,
            }
        )

    if not formal:
        return pd.DataFrame(
            columns=[
                "refit_date", "training_size", "calibration_pool_size", "pi", "gamma_candidate", "gamma_B2", "gamma_B3",
                "p_candidate", "p_B0", "p_B1", "p_B2", "p_B3",
            ]
        ).rename_axis("date")
    return pd.DataFrame(formal).set_index("date").sort_index()


def build_evaluation_table(panel: pd.DataFrame, predictions: pd.DataFrame) -> pd.DataFrame:
    if predictions.empty:
        return predictions.copy()
    eval_rows = predictions.join(
        panel[["Y", "M", "TARGET_DEFINED", "EPISODE_ID", "EPISODE_STATE", "EPISODE_DURATION"]],
        how="left",
    )
    eval_rows = eval_rows.loc[eval_rows["TARGET_DEFINED"].fillna(False) & eval_rows["Y"].notna()].copy()
    eval_rows["Y"] = eval_rows["Y"].astype(int)
    eval_rows["confidence"] = 2.0 * np.abs(eval_rows["p_candidate"] - 0.5)
    direction = np.where(eval_rows["p_candidate"].to_numpy(dtype=float) > 0.5, 1.0, -1.0)
    eval_rows["Z"] = direction * eval_rows["M"].to_numpy(dtype=float)
    for key in ("candidate", "B0", "B1", "B2", "B3"):
        eval_rows[f"loss_{key}"] = nll_losses(eval_rows["Y"].to_numpy(dtype=float), eval_rows[f"p_{key}"].to_numpy(dtype=float))
    return eval_rows


def sequential_full_block_ids(n: int, block_length: int = BOOTSTRAP_BLOCK_LENGTH) -> np.ndarray:
    if n < 0 or block_length <= 0:
        raise FrozenProtocolError("Invalid block-id dimensions")
    ids = np.full(n, -1, dtype=int)
    full = n // block_length
    if full:
        ids[: full * block_length] = np.arange(full * block_length, dtype=int) // block_length
    return ids


def moving_block_indices(n: int, rng: np.random.Generator, block_length: int = BOOTSTRAP_BLOCK_LENGTH) -> np.ndarray:
    if n < block_length:
        raise FrozenProtocolError("Moving-block bootstrap requires at least one full block")
    starts = np.arange(0, n - block_length + 1, dtype=int)
    pieces: list[np.ndarray] = []
    total = 0
    while total < n:
        start = int(rng.choice(starts))
        piece = np.arange(start, start + block_length, dtype=int)
        pieces.append(piece)
        total += block_length
    return np.concatenate(pieces)[:n]


def _natural_spline_basis(x: Any, derivative: int = 0) -> np.ndarray:
    x = _as_float_array(x).reshape(-1)
    knots = np.asarray((*SPLINE_BOUNDARY_KNOTS[:1], *SPLINE_INTERNAL_KNOTS, *SPLINE_BOUNDARY_KNOTS[1:]), dtype=float)
    last2 = float(knots[-2])
    last = float(knots[-1])

    def positive_power(v: np.ndarray, knot: float, power: int) -> np.ndarray:
        return np.maximum(v - knot, 0.0) ** power

    columns: list[np.ndarray] = []
    if derivative == 0:
        columns.extend([np.ones_like(x), x])
        power, mult = 3, 1.0
    elif derivative == 1:
        columns.extend([np.zeros_like(x), np.ones_like(x)])
        power, mult = 2, 3.0
    elif derivative == 2:
        columns.extend([np.zeros_like(x), np.zeros_like(x)])
        power, mult = 1, 6.0
    else:
        raise FrozenProtocolError("Spline derivative order must be 0, 1 or 2")

    denom = last - last2
    for knot in knots[:-2]:
        term = (
            positive_power(x, float(knot), power)
            - positive_power(x, last2, power) * ((last - float(knot)) / denom)
            + positive_power(x, last, power) * ((last2 - float(knot)) / denom)
        )
        columns.append(mult * term)
    return np.column_stack(columns)


def fit_natural_spline(confidence: Any, z: Any) -> np.ndarray:
    c = _as_float_array(confidence).reshape(-1)
    z = _as_float_array(z).reshape(-1)
    if c.shape != z.shape or c.size < 6 or ((c < 0.0) | (c > 1.0)).any():
        raise FrozenProtocolError("Invalid spline sample")
    basis = _natural_spline_basis(c, derivative=0)
    coef, *_ = np.linalg.lstsq(basis, z, rcond=None)
    return np.asarray(coef, dtype=float)


def evaluate_natural_spline(coef: Any, confidence: Any, derivative: int = 0) -> np.ndarray:
    coef = _as_float_array(coef).reshape(-1)
    basis = _natural_spline_basis(confidence, derivative=derivative)
    if basis.shape[1] != coef.size:
        raise FrozenProtocolError("Spline coefficient dimension mismatch")
    return basis @ coef


def _segmented_sse_direct(c: np.ndarray, z: np.ndarray, kappa: float) -> tuple[float, np.ndarray]:
    design = np.column_stack([np.ones_like(c), c, np.maximum(c - kappa, 0.0)])
    coef, *_ = np.linalg.lstsq(design, z, rcond=None)
    residual = z - design @ coef
    return float(np.dot(residual, residual)), np.asarray(coef, dtype=float)


def _breakpoint_admissible(c: np.ndarray, kappa: float, block_ids: np.ndarray) -> bool:
    n = c.size
    min_obs = int(math.ceil(BREAKPOINT_MIN_SIDE_SHARE * n))
    low = c < kappa
    high = ~low
    if int(low.sum()) < min_obs or int(high.sum()) < min_obs:
        return False
    full_ids = np.unique(block_ids[block_ids >= 0])
    low_blocks = sum(bool(np.any(low & (block_ids == bid))) for bid in full_ids)
    high_blocks = sum(bool(np.any(high & (block_ids == bid))) for bid in full_ids)
    return low_blocks >= BREAKPOINT_MIN_FULL_BLOCKS_PER_SIDE and high_blocks >= BREAKPOINT_MIN_FULL_BLOCKS_PER_SIDE


def fit_segmented_breakpoint(confidence: Any, z: Any, block_ids: Any | None = None) -> BreakpointFit | None:
    c = _as_float_array(confidence).reshape(-1)
    z = _as_float_array(z).reshape(-1)
    if c.shape != z.shape or c.size < 3:
        raise FrozenProtocolError("Invalid segmented-regression sample")
    if block_ids is None:
        block_ids = sequential_full_block_ids(c.size)
    block_ids = np.asarray(block_ids, dtype=int).reshape(-1)
    if block_ids.shape != c.shape:
        raise FrozenProtocolError("Breakpoint block-id shape mismatch")

    lo_bound, hi_bound = BREAKPOINT_RANGE
    unique = np.unique(c[(c > lo_bound) & (c < hi_bound)])
    boundaries = np.unique(np.concatenate(([lo_bound], unique, [hi_bound]))).astype(float)
    candidates: list[float] = []

    # Within each interval the active hinge set is fixed. After residualizing the
    # hinge against [1,c], SSE has at most one interior stationary point; checking
    # that point plus interval boundaries gives the deterministic global minimum.
    for left, right in zip(boundaries[:-1], boundaries[1:]):
        if right < left:
            continue
        mid = (left + right) / 2.0
        active = c > mid
        A = np.column_stack([np.ones_like(c), c])
        G = A.T @ A
        try:
            Ginv = np.linalg.inv(G)
        except np.linalg.LinAlgError:
            continue
        yproj = A.T @ z
        u = c * active.astype(float)
        v = active.astype(float)
        A_u = A.T @ u
        A_v = A.T @ v
        a = float(np.dot(u, z) - A_u @ Ginv @ yproj)
        b = float(np.dot(v, z) - A_v @ Ginv @ yproj)
        aa = float(np.dot(u, u) - A_u @ Ginv @ A_u)
        bb = float(np.dot(u, v) - A_u @ Ginv @ A_v)
        cc = float(np.dot(v, v) - A_v @ Ginv @ A_v)
        denom = b * bb - a * cc
        local = [float(left), float(right)]
        if abs(denom) > NUMERIC_TOL:
            stationary = float((b * aa - a * bb) / denom)
            if left <= stationary <= right:
                local.append(stationary)
        candidates.extend(local)

    best: BreakpointFit | None = None
    for kappa in sorted(set(round(float(x), 14) for x in candidates if lo_bound <= x <= hi_bound)):
        if not _breakpoint_admissible(c, kappa, block_ids):
            continue
        sse, coef = _segmented_sse_direct(c, z, kappa)
        candidate = BreakpointFit(kappa=float(kappa), alpha=float(coef[0]), beta=float(coef[1]), delta=float(coef[2]), sse=sse)
        if best is None:
            best = candidate
        else:
            tolerance = OPT_TOL * max(1.0, abs(best.sse), abs(candidate.sse))
            if candidate.sse < best.sse - tolerance or (abs(candidate.sse - best.sse) <= tolerance and candidate.kappa < best.kappa):
                best = candidate
    return best


def _percentile_interval(values: Sequence[float]) -> tuple[float, float]:
    arr = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan")
    return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))


def bootstrap_statistics(eval_rows: pd.DataFrame, *, replicates: int = BOOTSTRAP_REPLICATES, seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    if replicates <= 0:
        raise FrozenProtocolError("Bootstrap replicates must be positive")
    required = {
        "Y", "confidence", "Z", "p_candidate",
        "loss_candidate", "loss_B0", "loss_B1", "loss_B2", "loss_B3",
    }
    missing = sorted(required - set(eval_rows.columns))
    if missing:
        raise FrozenProtocolError(f"Evaluation table missing bootstrap columns: {missing}")
    n = len(eval_rows)
    if n < BOOTSTRAP_BLOCK_LENGTH:
        raise FrozenProtocolError("Evaluation table is shorter than one frozen bootstrap block")

    y = eval_rows["Y"].to_numpy(dtype=int)
    c = eval_rows["confidence"].to_numpy(dtype=float)
    z = eval_rows["Z"].to_numpy(dtype=float)
    p = eval_rows["p_candidate"].to_numpy(dtype=float)
    baseline_names = ("B0", "B1", "B2", "B3")
    diffs = np.column_stack(
        [eval_rows["loss_candidate"].to_numpy(dtype=float) - eval_rows[f"loss_{b}"].to_numpy(dtype=float) for b in baseline_names]
    )
    mean_diffs = np.mean(diffs, axis=0)
    rng = np.random.default_rng(seed)
    tstars: list[float] = []
    auc_values: list[float] = []
    rho_values: list[float] = []
    kappas: list[float] = []
    deltas: list[float] = []
    high_means: list[float] = []
    valid_breakpoints = 0

    for _ in range(replicates):
        idx = moving_block_indices(n, rng)
        dstar = np.mean(diffs[idx], axis=0)
        tstars.append(float(np.max(dstar - mean_diffs)))
        auc_values.append(auc_score(y[idx], p[idx]))
        rho = spearmanr(c[idx], z[idx]).statistic
        rho_values.append(float(rho) if np.isfinite(rho) else float("nan"))
        _ = fit_natural_spline(c[idx], z[idx])
        replicate_blocks = sequential_full_block_ids(n)
        bp = fit_segmented_breakpoint(c[idx], z[idx], replicate_blocks)
        if bp is not None:
            valid_breakpoints += 1
            kappas.append(bp.kappa)
            deltas.append(bp.delta)
            high = c[idx] >= bp.kappa
            high_means.append(float(np.mean(z[idx][high])) if high.any() else float("nan"))

    q95 = float(np.percentile(np.asarray(tstars, dtype=float), 95.0))
    simultaneous_ucl = {b: float(mean_diffs[i] + q95) for i, b in enumerate(baseline_names)}
    kappa_ci = _percentile_interval(kappas)
    auc_ci = _percentile_interval(auc_values)
    rho_ci = _percentile_interval(rho_values)
    high_ci = _percentile_interval(high_means)
    valid_share = valid_breakpoints / float(replicates)
    delta_positive_share = float(np.mean(np.asarray(deltas) > 0.0)) if deltas else 0.0
    return {
        "mean_nll_differentials": {b: float(mean_diffs[i]) for i, b in enumerate(baseline_names)},
        "simultaneous_q95": q95,
        "simultaneous_ucl": simultaneous_ucl,
        "auc_ci95": auc_ci,
        "spearman_ci95": rho_ci,
        "valid_breakpoint_share": float(valid_share),
        "kappa_ci95": kappa_ci,
        "kappa_ci_width": float(kappa_ci[1] - kappa_ci[0]) if np.isfinite(kappa_ci).all() else float("nan"),
        "delta_positive_share": delta_positive_share,
        "high_mean_z_ci95": high_ci,
    }


def temporal_block_wins(eval_rows: pd.DataFrame) -> tuple[int, list[dict[str, float]]]:
    if len(eval_rows) < 4:
        return 0, []
    blocks = np.array_split(np.arange(len(eval_rows), dtype=int), 4)
    details: list[dict[str, float]] = []
    wins = 0
    for idx in blocks:
        candidate = float(np.mean(eval_rows["loss_candidate"].to_numpy(dtype=float)[idx]))
        baselines = {
            b: float(np.mean(eval_rows[f"loss_{b}"].to_numpy(dtype=float)[idx]))
            for b in ("B0", "B1", "B2", "B3")
        }
        best = min(baselines.values())
        if candidate < best:
            wins += 1
        details.append({"candidate": candidate, "best_baseline": best, **baselines})
    return wins, details


def episode_robustness(eval_rows: pd.DataFrame) -> dict[str, Any]:
    eligible = eval_rows.loc[
        eval_rows["EPISODE_ID"].notna()
        & eval_rows["EPISODE_DURATION"].fillna(0).astype(float).ge(MIN_EPISODE_DURATION)
    ]
    values: list[float] = []
    for _, group in eligible.groupby("EPISODE_ID", sort=True):
        candidate = float(group["loss_candidate"].mean())
        best = min(float(group[f"loss_{b}"].mean()) for b in ("B0", "B1", "B2", "B3"))
        values.append(candidate - best)
    if not values:
        return {"episode_count": 0, "median_delta_nll": float("nan"), "negative_share": float("nan"), "pass": False}
    arr = np.asarray(values, dtype=float)
    return {
        "episode_count": int(arr.size),
        "median_delta_nll": float(np.median(arr)),
        "negative_share": float(np.mean(arr < 0.0)),
        "pass": bool(np.median(arr) < 0.0 and np.mean(arr < 0.0) > 0.5),
    }


def support_statistics(eval_rows: pd.DataFrame) -> dict[str, Any]:
    block_ids = sequential_full_block_ids(len(eval_rows))
    full_ids = np.unique(block_ids[block_ids >= 0])
    y = eval_rows["Y"].to_numpy(dtype=int)
    eth_blocks = sum(bool(np.any((block_ids == bid) & (y == 0))) for bid in full_ids)
    sol_blocks = sum(bool(np.any((block_ids == bid) & (y == 1))) for bid in full_ids)
    return {
        "full_blocks": int(len(full_ids)),
        "eth_leader_full_blocks": int(eth_blocks),
        "sol_leader_full_blocks": int(sol_blocks),
        "pass": bool(len(full_ids) >= MIN_FULL_EVAL_BLOCKS and eth_blocks >= MIN_DIRECTION_FULL_BLOCKS and sol_blocks >= MIN_DIRECTION_FULL_BLOCKS),
    }


def high_support(eval_rows: pd.DataFrame, kappa: float) -> dict[str, Any]:
    c = eval_rows["confidence"].to_numpy(dtype=float)
    high = c >= kappa
    block_ids = sequential_full_block_ids(len(eval_rows))
    full_ids = np.unique(block_ids[(block_ids >= 0) & high])
    coverage = float(np.mean(high)) if len(high) else 0.0
    predicted_sol = eval_rows["p_candidate"].to_numpy(dtype=float) > 0.5
    sol_episode_ids = set(
        eval_rows.loc[high & predicted_sol & eval_rows["EPISODE_STATE"].eq("SOL"), "EPISODE_ID"].dropna().astype(int).tolist()
    )
    eth_episode_ids = set(
        eval_rows.loc[high & ~predicted_sol & eval_rows["EPISODE_STATE"].eq("ETH"), "EPISODE_ID"].dropna().astype(int).tolist()
    )
    return {
        "coverage": coverage,
        "full_blocks": int(len(full_ids)),
        "sol_high_episodes": int(len(sol_episode_ids)),
        "eth_high_episodes": int(len(eth_episode_ids)),
        "g10_pass": bool(coverage >= HIGH_MIN_COVERAGE and len(full_ids) >= HIGH_MIN_FULL_BLOCKS),
        "g11_pass": bool(len(sol_episode_ids) >= HIGH_MIN_EPISODES_PER_DIRECTION and len(eth_episode_ids) >= HIGH_MIN_EPISODES_PER_DIRECTION),
    }


def subsampling_fragility(eval_rows: pd.DataFrame, primary_g2_pass: bool) -> dict[str, Any]:
    n = len(eval_rows)
    if n == 0:
        return {"block_length": 0, "subsamples": 0, "nonnegative_share": float("nan"), "inference_fragile": False}
    b = max(56, int(math.ceil(n ** (2.0 / 3.0))))
    if b > n:
        return {"block_length": b, "subsamples": 0, "nonnegative_share": float("nan"), "inference_fragile": False}
    diffs = np.column_stack(
        [eval_rows["loss_candidate"].to_numpy(dtype=float) - eval_rows[f"loss_{name}"].to_numpy(dtype=float) for name in ("B0", "B1", "B2", "B3")]
    )
    dmax_values = [float(np.max(np.mean(diffs[start : start + b], axis=0))) for start in range(0, n - b + 1)]
    share = float(np.mean(np.asarray(dmax_values) >= 0.0)) if dmax_values else float("nan")
    return {
        "block_length": int(b),
        "subsamples": int(len(dmax_values)),
        "nonnegative_share": share,
        "inference_fragile": bool(primary_g2_pass and np.isfinite(share) and share >= 0.5),
    }


def classify_frozen_result(eval_rows: pd.DataFrame, bootstrap: Mapping[str, Any]) -> dict[str, Any]:
    if eval_rows.empty:
        return {"classification": "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT", "gates": {"G0": True, "G1": False}}

    support = support_statistics(eval_rows)
    if not support["pass"]:
        return {"classification": "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT", "gates": {"G0": True, "G1": False}, "support": support}

    y = eval_rows["Y"].to_numpy(dtype=int)
    p = eval_rows["p_candidate"].to_numpy(dtype=float)
    g2 = max(float(x) for x in bootstrap["simultaneous_ucl"].values()) < 0.0
    auc_lower = float(bootstrap["auc_ci95"][0])
    g3 = bool(np.isfinite(auc_lower) and auc_lower > 0.5 and balanced_accuracy(y, p) > 0.5)
    candidate_brier = brier_score(y, p)
    baseline_briers = {b: brier_score(y, eval_rows[f"p_{b}"].to_numpy(dtype=float)) for b in ("B0", "B1", "B2", "B3")}
    g4 = candidate_brier < min(baseline_briers.values())
    temporal_wins, temporal_details = temporal_block_wins(eval_rows)
    g5 = temporal_wins >= TEMPORAL_REQUIRED_WINS
    episodes = episode_robustness(eval_rows)
    g6 = bool(episodes["pass"])
    gates: dict[str, bool] = {"G0": True, "G1": True, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6}

    if not (g2 and g3 and g4):
        classification = "FAIL_NO_INCREMENTAL_DYNAMIC_LEADERSHIP"
    elif not (g5 and g6):
        classification = "FAIL_NO_ROBUST_DYNAMIC_LEADERSHIP"
    else:
        rho_lower = float(bootstrap["spearman_ci95"][0])
        g7 = bool(np.isfinite(rho_lower) and rho_lower > 0.0)
        valid_share = float(bootstrap["valid_breakpoint_share"])
        kappa_ci = bootstrap["kappa_ci95"]
        kappa_width = float(bootstrap["kappa_ci_width"])
        delta_share = float(bootstrap["delta_positive_share"])
        g9 = bool(
            valid_share >= BREAKPOINT_MIN_VALID_BOOTSTRAP_SHARE
            and np.isfinite(kappa_width)
            and kappa_width <= BREAKPOINT_MAX_CI_WIDTH
            and delta_share >= BREAKPOINT_MIN_POSITIVE_DELTA_SHARE
        )
        g8 = bool(g9 and np.isfinite(float(bootstrap["high_mean_z_ci95"][0])) and float(bootstrap["high_mean_z_ci95"][0]) > 0.0)
        gates.update({"G7": g7, "G8": g8, "G9": g9})
        original_bp = fit_segmented_breakpoint(
            eval_rows["confidence"].to_numpy(dtype=float),
            eval_rows["Z"].to_numpy(dtype=float),
            sequential_full_block_ids(len(eval_rows)),
        )
        if g9 and original_bp is not None:
            hs = high_support(eval_rows, original_bp.kappa)
            g10 = bool(hs["g10_pass"])
            g11 = bool(hs["g11_pass"])
        else:
            hs = {"coverage": 0.0, "full_blocks": 0, "sol_high_episodes": 0, "eth_high_episodes": 0, "g10_pass": False, "g11_pass": False}
            g10 = False
            g11 = False
        gates.update({"G10": g10, "G11": g11})
        if not (g7 and g8 and g9 and g10):
            classification = "PASS_LEADERSHIP_INFORMATION_NO_CONCENTRATION_HANDOFF"
        elif not g11:
            classification = "PASS_ONE_SIDED_LEADERSHIP_NO_FULL_ROUTER"
        else:
            classification = "PASS_LEADERSHIP_INFORMATION_CONCENTRATION_HANDOFF_ELIGIBLE"

    fragility = subsampling_fragility(eval_rows, g2)
    return {
        "classification": classification,
        "gates": gates,
        "support": support,
        "candidate_brier": candidate_brier,
        "baseline_briers": baseline_briers,
        "balanced_accuracy": balanced_accuracy(y, p),
        "direction_metrics": direction_precision_recall(y, p),
        "temporal_wins": temporal_wins,
        "temporal_details": temporal_details,
        "episode_robustness": episodes,
        "subsampling": fragility,
        "inference_fragile": bool(fragility["inference_fragile"]),
    }


def assert_no_result_artifacts(directory: str | Path) -> None:
    directory = Path(directory)
    forbidden = {
        "run_once.py",
        "RUN_INTERFACE.json",
        "PRIMARY_RESULT.json",
        "RESULT_SUMMARY.json",
        "EXECUTION.json",
        "RUN_ONCE.marker",
        "RESULT.md",
        "portfolio.py",
        "portfolio_result.json",
    }
    present = {p.name for p in directory.iterdir() if p.is_file()}
    overlap = sorted(forbidden & present)
    if overlap:
        raise FrozenProtocolError(f"Implementation-only boundary violated by result/run artifacts: {overlap}")
