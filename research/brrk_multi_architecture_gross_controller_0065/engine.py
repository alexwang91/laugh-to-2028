from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from scipy.optimize import nnls
from scipy.special import logsumexp
from scipy.stats import norm, rankdata, skew, kurtosis
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.preprocessing import SplineTransformer, StandardScaler

from research.brrk_btc_risk_signal_atlas_0062.engine import build_signal_atlas

RID = "BRRK-MULTI-ARCHITECTURE-GROSS-CONTROLLER-0065"
FAMILY_ORDER = (
    "F01_TREND_LEVEL_DIRECTION",
    "F02_TREND_SPREAD_DISAGREEMENT",
    "F03_TREND_ACCELERATION_DECELERATION",
    "F04_TREND_CROSS_TRANSITION",
    "F05_VOL_ADJUSTED_TREND_GUARDS",
    "F06_MOMENTUM_LEVEL",
    "F07_OVERBOUGHT_STRETCH",
    "F08_BEARISH_DIVERGENCE_EXHAUSTION",
    "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE",
    "F10_VOLATILITY_REGIME",
    "F11_DOWNSIDE_ASYMMETRY_TAIL",
    "F12_VOLUME_FLOW_CONFIRMATION",
    "F13_CROSS_CRYPTO_BREADTH",
    "F14_RELATIVE_CRYPTO_LEADERSHIP",
    "F21_SEQUENTIAL_CHANGE_DETECTION",
    "F23_MULTI_TIMESCALE_DISAGREEMENT",
    "F24_FIXED_LOW_ORDER_INTERACTIONS",
)
ARCHITECTURES = (
    "A01_FAMILY_ELASTIC_NET",
    "A02_RAW_ELASTIC_NET",
    "A03_PCR_RIDGE",
    "A04_THEORY_QUADRATIC_HESSIAN_RIDGE",
    "A05_GAM_SPLINE_RIDGE",
    "A06_SHALLOW_GBDT",
    "A07_HMM_REGIME_MIXTURE_RIDGE",
    "A08_STACKED_ENSEMBLE",
)
BASE_ARCHITECTURES = ARCHITECTURES[:7]
INTERACTIONS = (
    ("F01_TREND_LEVEL_DIRECTION", "F10_VOLATILITY_REGIME"),
    ("F03_TREND_ACCELERATION_DECELERATION", "F10_VOLATILITY_REGIME"),
    ("F05_VOL_ADJUSTED_TREND_GUARDS", "F11_DOWNSIDE_ASYMMETRY_TAIL"),
    ("F06_MOMENTUM_LEVEL", "F13_CROSS_CRYPTO_BREADTH"),
    ("F07_OVERBOUGHT_STRETCH", "F08_BEARISH_DIVERGENCE_EXHAUSTION"),
    ("F09_BREAKDOWN_FAILED_BREAK_STRUCTURE", "F12_VOLUME_FLOW_CONFIRMATION"),
    ("F14_RELATIVE_CRYPTO_LEADERSHIP", "F13_CROSS_CRYPTO_BREADTH"),
    ("F21_SEQUENTIAL_CHANGE_DETECTION", "F23_MULTI_TIMESCALE_DISAGREEMENT"),
    ("F01_TREND_LEVEL_DIRECTION", "F14_RELATIVE_CRYPTO_LEADERSHIP"),
    ("F11_DOWNSIDE_ASYMMETRY_TAIL", "F12_VOLUME_FLOW_CONFIRMATION"),
)
META_BLOCKS = {
    "TREND_STRUCTURE": (
        "F01_TREND_LEVEL_DIRECTION", "F02_TREND_SPREAD_DISAGREEMENT",
        "F03_TREND_ACCELERATION_DECELERATION", "F04_TREND_CROSS_TRANSITION",
        "F05_VOL_ADJUSTED_TREND_GUARDS", "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE",
        "F21_SEQUENTIAL_CHANGE_DETECTION", "F23_MULTI_TIMESCALE_DISAGREEMENT",
    ),
    "MOMENTUM_EXHAUSTION": (
        "F06_MOMENTUM_LEVEL", "F07_OVERBOUGHT_STRETCH", "F08_BEARISH_DIVERGENCE_EXHAUSTION",
    ),
    "VOL_TAIL": ("F10_VOLATILITY_REGIME", "F11_DOWNSIDE_ASYMMETRY_TAIL"),
    "BREADTH_FLOW_RELATIVE": (
        "F12_VOLUME_FLOW_CONFIRMATION", "F13_CROSS_CRYPTO_BREADTH",
        "F14_RELATIVE_CRYPTO_LEADERSHIP", "F24_FIXED_LOW_ORDER_INTERACTIONS",
    ),
}
TRAIN_END = pd.Timestamp("2021-12-31")
VALID_START = pd.Timestamp("2022-01-01")
VALID_END = pd.Timestamp("2022-11-19")
EVAL_START = pd.Timestamp("2022-12-10")
EVAL_END = pd.Timestamp("2026-08-02")
TARGET_H = 20
REFIT_CADENCE = 20
OUTER_COST = 0.001
CASH_REALIZATION = 0.5
CASH_ANNUAL_FEE = 0.01
BOOT_BLOCK = 60
BOOT_REPS = 4000
BOOT_SEED = 650065
EXPECTED_0064 = {
    "terminal_wealth": 62813.41563922909,
    "cagr": 0.6557689400699214,
    "max_drawdown": -0.3366471268083583,
}


def _naive_index(index: pd.Index) -> pd.DatetimeIndex:
    out = pd.DatetimeIndex(pd.to_datetime(index))
    if out.tz is not None:
        out = out.tz_convert("UTC").tz_localize(None)
    return out


def _with_naive_index(frame: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    out = frame.copy()
    out.index = _naive_index(out.index)
    return out.sort_index()


def frozen_configurations() -> dict[str, list[dict[str, Any]]]:
    configs: dict[str, list[dict[str, Any]]] = {}
    configs["A01_FAMILY_ELASTIC_NET"] = [
        {"alpha": a, "l1_ratio": l} for a in (0.0001, 0.001, 0.01, 0.1) for l in (0.1, 0.5, 0.9)
    ]
    configs["A02_RAW_ELASTIC_NET"] = [
        {"alpha": a, "l1_ratio": l} for a in (0.0001, 0.001, 0.01, 0.1) for l in (0.1, 0.5, 0.9)
    ]
    configs["A03_PCR_RIDGE"] = [
        {"n_components": n, "ridge_alpha": a} for n in (5, 10, 20, 40) for a in (0.1, 1.0, 10.0)
    ]
    configs["A04_THEORY_QUADRATIC_HESSIAN_RIDGE"] = [{"ridge_alpha": a} for a in (1.0, 10.0, 100.0, 1000.0)]
    configs["A05_GAM_SPLINE_RIDGE"] = [
        {"n_knots": k, "ridge_alpha": a} for k in (3, 5, 7) for a in (1.0, 10.0, 100.0)
    ]
    configs["A06_SHALLOW_GBDT"] = [
        {"max_depth": d, "n_estimators": n, "learning_rate": lr}
        for d in (1, 2) for n in (50, 100) for lr in (0.03, 0.1)
    ]
    configs["A07_HMM_REGIME_MIXTURE_RIDGE"] = [
        {"n_components": n, "ridge_alpha": a} for n in (2, 3) for a in (1.0, 10.0, 100.0)
    ]
    if sum(map(len, configs.values())) != 63 or set(configs) != set(BASE_ARCHITECTURES):
        raise RuntimeError("frozen configuration count drift")
    return configs


def _serialize_params(params: Mapping[str, Any]) -> str:
    return "|".join(f"{k}={params[k]}" for k in sorted(params))


def _target_and_endpoints(btc_close: pd.Series) -> tuple[pd.Series, pd.Series]:
    close = _with_naive_index(pd.to_numeric(btc_close, errors="coerce"))
    y = np.log(close.shift(-TARGET_H) / close)
    idx = close.index
    endpoints = pd.Series(pd.NaT, index=idx, dtype="datetime64[ns]")
    if len(idx) > TARGET_H:
        endpoints.iloc[:-TARGET_H] = idx[TARGET_H:].to_numpy()
    return y.rename("Y20"), endpoints.rename("target_endpoint")


def _median_impute(train: pd.DataFrame, other: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    med = train.median(axis=0, skipna=True).to_numpy(dtype=float)
    if not np.isfinite(med).all():
        raise ValueError("all-missing or non-finite feature column")
    a = train.to_numpy(dtype=float)
    b = other.to_numpy(dtype=float)
    a = np.where(np.isfinite(a), a, med)
    b = np.where(np.isfinite(b), b, med)
    return a, b, med


def _impute_with_median(frame: pd.DataFrame, med: np.ndarray) -> np.ndarray:
    arr = frame.to_numpy(dtype=float)
    if arr.shape[1] != len(med):
        raise ValueError("feature width drift")
    return np.where(np.isfinite(arr), arr, med)


def _quadratic_expand(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    f = frame.loc[:, FAMILY_ORDER].copy()
    cols: dict[str, pd.Series] = {name: f[name] for name in FAMILY_ORDER}
    for name in FAMILY_ORDER:
        cols[f"SQ::{name}"] = f[name] * f[name]
    for a, b in INTERACTIONS:
        cols[f"X::{a}::{b}"] = f[a] * f[b]
    out = pd.DataFrame(cols, index=f.index)
    if out.shape[1] != 44:
        raise RuntimeError("quadratic expansion drift")
    return out, list(out.columns)


def _meta_factors(families: pd.DataFrame) -> pd.DataFrame:
    out = {name: families.loc[:, cols].mean(axis=1, skipna=True) for name, cols in META_BLOCKS.items()}
    return pd.DataFrame(out, index=families.index)


def _hmm_filtered_probabilities(model: GaussianHMM, x: np.ndarray) -> np.ndarray:
    log_b = model._compute_log_likelihood(x)  # deterministic hmmlearn primitive; no smoothing of future prediction rows
    log_start = np.log(np.maximum(model.startprob_, 1e-300))
    log_trans = np.log(np.maximum(model.transmat_, 1e-300))
    out = np.empty_like(log_b, dtype=float)
    la = log_start + log_b[0]
    la -= logsumexp(la)
    out[0] = np.exp(la)
    for i in range(1, len(x)):
        la = log_b[i] + logsumexp(la[:, None] + log_trans, axis=0)
        la -= logsumexp(la)
        out[i] = np.exp(la)
    return out


@dataclass
class FittedModel:
    architecture: str
    params: dict[str, Any]
    train_index: pd.DatetimeIndex
    train_predictions: np.ndarray
    payload: dict[str, Any]
    diagnostics: dict[str, Any]

    def predict(self, cells: pd.DataFrame, families: pd.DataFrame) -> np.ndarray:
        a = self.architecture
        p = self.payload
        if a in {"A01_FAMILY_ELASTIC_NET", "A06_SHALLOW_GBDT"}:
            x = _impute_with_median(families.loc[:, FAMILY_ORDER], p["median"])
            xs = p["scaler"].transform(x) if p.get("scaler") is not None else x
            return np.asarray(p["model"].predict(xs), dtype=float)
        if a == "A02_RAW_ELASTIC_NET":
            x = _impute_with_median(cells.loc[:, p["columns"]], p["median"])
            return np.asarray(p["model"].predict(p["scaler"].transform(x)), dtype=float)
        if a == "A03_PCR_RIDGE":
            x = _impute_with_median(cells.loc[:, p["columns"]], p["median"])
            z = p["pca"].transform(p["scaler"].transform(x))
            return np.asarray(p["model"].predict(z), dtype=float)
        if a == "A04_THEORY_QUADRATIC_HESSIAN_RIDGE":
            q, _ = _quadratic_expand(families)
            x = _impute_with_median(q.loc[:, p["columns"]], p["median"])
            return np.asarray(p["model"].predict(p["scaler"].transform(x)), dtype=float)
        if a == "A05_GAM_SPLINE_RIDGE":
            x = _impute_with_median(families.loc[:, FAMILY_ORDER], p["median"])
            z = p["spline"].transform(x)
            return np.asarray(p["model"].predict(p["scaler"].transform(z)), dtype=float)
        if a == "A07_HMM_REGIME_MIXTURE_RIDGE":
            fam = families.loc[:, FAMILY_ORDER]
            xf = _impute_with_median(fam, p["family_median"])
            xs = p["family_scaler"].transform(xf)
            meta = _meta_factors(fam)
            xm = _impute_with_median(meta, p["meta_median"])
            full = np.vstack([p["meta_train_scaled"], p["meta_scaler"].transform(xm)])
            probs = _hmm_filtered_probabilities(p["hmm"], full)[-len(xm):]
            state_pred = np.column_stack([m.predict(xs) for m in p["state_models"]])
            return np.sum(probs * state_pred, axis=1)
        raise ValueError(f"unsupported architecture {a}")


def fit_model(architecture: str, params: Mapping[str, Any], cells: pd.DataFrame, families: pd.DataFrame, y: pd.Series) -> FittedModel:
    if architecture not in BASE_ARCHITECTURES:
        raise ValueError("architecture is not a frozen base architecture")
    common = y.index
    cells = cells.loc[common]
    families = families.loc[common, FAMILY_ORDER]
    yy = y.to_numpy(dtype=float)
    if len(yy) < 40 or not np.isfinite(yy).all():
        raise ValueError("insufficient/non-finite training target")
    params = dict(params)
    diagnostics: dict[str, Any] = {}

    if architecture == "A01_FAMILY_ELASTIC_NET":
        x, _, med = _median_impute(families, families.iloc[:1])
        sc = StandardScaler().fit(x)
        xs = sc.transform(x)
        model = ElasticNet(alpha=params["alpha"], l1_ratio=params["l1_ratio"], fit_intercept=True,
                           max_iter=20000, tol=1e-7, selection="cyclic").fit(xs, yy)
        pred = model.predict(xs)
        payload = {"median": med, "scaler": sc, "model": model}
    elif architecture == "A02_RAW_ELASTIC_NET":
        cols = list(cells.columns)
        x, _, med = _median_impute(cells, cells.iloc[:1])
        sc = StandardScaler().fit(x)
        xs = sc.transform(x)
        model = ElasticNet(alpha=params["alpha"], l1_ratio=params["l1_ratio"], fit_intercept=True,
                           max_iter=20000, tol=1e-7, selection="cyclic").fit(xs, yy)
        pred = model.predict(xs)
        payload = {"columns": cols, "median": med, "scaler": sc, "model": model}
    elif architecture == "A03_PCR_RIDGE":
        cols = list(cells.columns)
        x, _, med = _median_impute(cells, cells.iloc[:1])
        sc = StandardScaler().fit(x)
        xs = sc.transform(x)
        ncomp = min(int(params["n_components"]), xs.shape[0], xs.shape[1])
        if ncomp != int(params["n_components"]):
            raise ValueError("frozen PCA component count infeasible")
        pca = PCA(n_components=ncomp, svd_solver="full").fit(xs)
        z = pca.transform(xs)
        model = Ridge(alpha=float(params["ridge_alpha"])).fit(z, yy)
        pred = model.predict(z)
        diagnostics["explained_variance_ratio_sum"] = float(np.sum(pca.explained_variance_ratio_))
        payload = {"columns": cols, "median": med, "scaler": sc, "pca": pca, "model": model}
    elif architecture == "A04_THEORY_QUADRATIC_HESSIAN_RIDGE":
        q, cols = _quadratic_expand(families)
        x, _, med = _median_impute(q, q.iloc[:1])
        sc = StandardScaler().fit(x)
        xs = sc.transform(x)
        model = Ridge(alpha=float(params["ridge_alpha"])).fit(xs, yy)
        pred = model.predict(xs)
        coef = np.asarray(model.coef_, dtype=float)
        h = np.zeros((17, 17), dtype=float)
        for i in range(17):
            h[i, i] = 2.0 * coef[17 + i]
        for j, (a, b) in enumerate(INTERACTIONS):
            ia, ib = FAMILY_ORDER.index(a), FAMILY_ORDER.index(b)
            v = coef[34 + j]
            h[ia, ib] = v
            h[ib, ia] = v
        diagnostics = {
            "basis": "STANDARDIZED_EXPANDED_FEATURE_BASIS",
            "linear_coefficients": {FAMILY_ORDER[i]: float(coef[i]) for i in range(17)},
            "square_coefficients": {FAMILY_ORDER[i]: float(coef[17+i]) for i in range(17)},
            "interaction_coefficients": {f"{a}*{b}": float(coef[34+j]) for j, (a, b) in enumerate(INTERACTIONS)},
            "symmetric_quadratic_hessian": h.tolist(),
        }
        payload = {"columns": cols, "median": med, "scaler": sc, "model": model}
    elif architecture == "A05_GAM_SPLINE_RIDGE":
        x, _, med = _median_impute(families, families.iloc[:1])
        spline = SplineTransformer(n_knots=int(params["n_knots"]), degree=3, include_bias=False).fit(x)
        z = spline.transform(x)
        sc = StandardScaler().fit(z)
        zs = sc.transform(z)
        model = Ridge(alpha=float(params["ridge_alpha"])).fit(zs, yy)
        pred = model.predict(zs)
        payload = {"median": med, "spline": spline, "scaler": sc, "model": model}
    elif architecture == "A06_SHALLOW_GBDT":
        x, _, med = _median_impute(families, families.iloc[:1])
        model = GradientBoostingRegressor(
            max_depth=int(params["max_depth"]), n_estimators=int(params["n_estimators"]),
            learning_rate=float(params["learning_rate"]), min_samples_leaf=20,
            subsample=0.8, loss="squared_error", random_state=650065,
        ).fit(x, yy)
        pred = model.predict(x)
        payload = {"median": med, "scaler": None, "model": model}
    else:
        fam_x, _, fam_med = _median_impute(families, families.iloc[:1])
        fam_scaler = StandardScaler().fit(fam_x)
        fam_s = fam_scaler.transform(fam_x)
        meta = _meta_factors(families)
        meta_x, _, meta_med = _median_impute(meta, meta.iloc[:1])
        meta_scaler = StandardScaler().fit(meta_x)
        meta_s = meta_scaler.transform(meta_x)
        hmm = GaussianHMM(
            n_components=int(params["n_components"]), covariance_type="diag", n_iter=200,
            tol=0.0001, random_state=650065,
        ).fit(meta_s)
        probs = hmm.predict_proba(meta_s)
        state_models = []
        state_pred = []
        for s in range(int(params["n_components"])):
            w = np.asarray(probs[:, s], dtype=float)
            if float(np.sum(w)) <= 1e-8:
                raise ValueError("degenerate HMM state weight")
            model = Ridge(alpha=float(params["ridge_alpha"])).fit(fam_s, yy, sample_weight=w)
            state_models.append(model)
            state_pred.append(model.predict(fam_s))
        pred = np.sum(probs * np.column_stack(state_pred), axis=1)
        diagnostics = {"hmm_converged": bool(hmm.monitor_.converged), "state_weight_sums": [float(x) for x in probs.sum(axis=0)]}
        payload = {
            "family_median": fam_med, "family_scaler": fam_scaler,
            "meta_median": meta_med, "meta_scaler": meta_scaler, "meta_train_scaled": meta_s,
            "hmm": hmm, "state_models": state_models,
        }
    pred = np.asarray(pred, dtype=float)
    if pred.shape != yy.shape or not np.isfinite(pred).all():
        raise ValueError("non-finite fitted prediction")
    return FittedModel(architecture, params, pd.DatetimeIndex(common), pred, payload, diagnostics)


def _eligible_train_index(origin_index: pd.DatetimeIndex, endpoints: pd.Series, refit_date: pd.Timestamp) -> pd.DatetimeIndex:
    mask = (origin_index <= refit_date) & (endpoints.reindex(origin_index).to_numpy() < np.datetime64(refit_date))
    return origin_index[mask]


def walk_forward_predictions(
    architecture: str,
    params: Mapping[str, Any],
    cells: pd.DataFrame,
    families: pd.DataFrame,
    y: pd.Series,
    endpoints: pd.Series,
    prediction_origins: pd.DatetimeIndex,
    *,
    refit_cadence: int = REFIT_CADENCE,
) -> tuple[pd.Series, dict[str, Any]]:
    prediction_origins = pd.DatetimeIndex(prediction_origins)
    out = pd.Series(np.nan, index=prediction_origins, dtype=float)
    fit_count = 0
    last_diag: dict[str, Any] = {}
    for start in range(0, len(prediction_origins), refit_cadence):
        block = prediction_origins[start:start + refit_cadence]
        refit = pd.Timestamp(block[0])
        train_idx = _eligible_train_index(cells.index, endpoints, refit)
        train_idx = train_idx[y.reindex(train_idx).notna().to_numpy()]
        model = fit_model(architecture, params, cells.loc[train_idx], families.loc[train_idx], y.loc[train_idx])
        pred = model.predict(cells.loc[block], families.loc[block])
        if len(pred) != len(block) or not np.isfinite(pred).all():
            raise ValueError("walk-forward prediction failure")
        out.loc[block] = pred
        fit_count += 1
        last_diag = model.diagnostics
    if not np.isfinite(out.to_numpy()).all():
        raise ValueError("incomplete walk-forward predictions")
    return out, {"fit_count": fit_count, "last_refit_diagnostics": last_diag}


def select_hyperparameters(
    cells: pd.DataFrame, families: pd.DataFrame, y: pd.Series, endpoints: pd.Series,
) -> tuple[dict[str, dict[str, Any]], dict[str, float], dict[str, pd.Series], dict[str, Any]]:
    valid_origins = cells.index[(cells.index >= VALID_START) & (cells.index <= VALID_END)]
    configs = frozen_configurations()
    selected: dict[str, dict[str, Any]] = {}
    selected_mse: dict[str, float] = {}
    selected_predictions: dict[str, pd.Series] = {}
    audit: dict[str, Any] = {}
    for arch in BASE_ARCHITECTURES:
        candidates = []
        failures = []
        for params in configs[arch]:
            try:
                pred, diag = walk_forward_predictions(arch, params, cells, families, y, endpoints, valid_origins)
                yy = y.reindex(valid_origins).to_numpy(dtype=float)
                if not np.isfinite(yy).all():
                    raise ValueError("validation target incomplete")
                mse = float(np.mean((pred.to_numpy(dtype=float) - yy) ** 2))
                candidates.append((mse, _serialize_params(params), dict(params), pred, diag))
            except Exception as exc:  # frozen failure is recorded, never repaired adaptively
                failures.append({"params": dict(params), "error_type": type(exc).__name__, "message": str(exc)})
        if not candidates:
            selected[arch] = {}
            selected_mse[arch] = float("nan")
            audit[arch] = {"status": "MODEL_FIT_FAILURE", "failures": failures}
            continue
        candidates.sort(key=lambda x: (x[0], x[1]))
        mse, _, params, pred, diag = candidates[0]
        selected[arch] = params
        selected_mse[arch] = mse
        selected_predictions[arch] = pred
        audit[arch] = {
            "status": "SELECTED", "selected_params": params, "selected_validation_mse": mse,
            "valid_config_count": len(candidates), "failed_config_count": len(failures),
            "failures": failures, "selected_prediction_diagnostics": diag,
        }
    return selected, selected_mse, selected_predictions, audit


def stack_weights(validation_predictions: Mapping[str, pd.Series], y_validation: pd.Series) -> dict[str, float]:
    if set(validation_predictions) != set(BASE_ARCHITECTURES):
        raise ValueError("stack requires all seven frozen base architectures")
    idx = y_validation.index
    matrix = np.column_stack([validation_predictions[a].reindex(idx).to_numpy(dtype=float) for a in BASE_ARCHITECTURES])
    yy = y_validation.to_numpy(dtype=float)
    if not np.isfinite(matrix).all() or not np.isfinite(yy).all():
        raise ValueError("stack validation matrix incomplete")
    w, _ = nnls(matrix, yy)
    if not np.isfinite(w).all() or float(w.sum()) <= 0.0:
        w = np.full(len(BASE_ARCHITECTURES), 1.0 / len(BASE_ARCHITECTURES))
    else:
        w = w / w.sum()
    return {a: float(v) for a, v in zip(BASE_ARCHITECTURES, w)}


def _prediction_to_g(current: np.ndarray, fitted: np.ndarray) -> np.ndarray:
    fitted = np.asarray(fitted, dtype=float)
    current = np.asarray(current, dtype=float)
    med = float(np.median(fitted))
    mad = float(np.median(np.abs(fitted - med)))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale <= 0:
        z = np.zeros_like(current)
    else:
        z = (current - med) / scale
    return np.clip(1.0 + 0.25 * z, 0.0, 1.0)


def evaluation_g_paths(
    cells: pd.DataFrame,
    families: pd.DataFrame,
    y: pd.Series,
    endpoints: pd.Series,
    eval_dates: pd.DatetimeIndex,
    selected_params: Mapping[str, Mapping[str, Any]],
    weights: Mapping[str, float],
) -> tuple[dict[str, pd.Series], dict[str, Any]]:
    eval_dates = pd.DatetimeIndex(eval_dates)
    position = {d: i for i, d in enumerate(cells.index)}
    origins = []
    for d in eval_dates:
        i = position.get(d)
        if i is None or i == 0:
            raise ValueError(f"evaluation date missing from feature calendar: {d}")
        origins.append(cells.index[i - 1])
    origins = pd.DatetimeIndex(origins)
    if len(set(origins)) != len(origins):
        raise ValueError("duplicate evaluation forecast origins")
    prediction_paths = {a: pd.Series(np.nan, index=origins, dtype=float) for a in BASE_ARCHITECTURES}
    g_paths = {a: pd.Series(np.nan, index=eval_dates, dtype=float) for a in ARCHITECTURES}
    diagnostics: dict[str, Any] = {a: {"refit_count": 0, "last_refit_diagnostics": {}} for a in BASE_ARCHITECTURES}
    stack_pred = pd.Series(np.nan, index=origins, dtype=float)

    for start in range(0, len(origins), REFIT_CADENCE):
        oblock = origins[start:start + REFIT_CADENCE]
        dblock = eval_dates[start:start + REFIT_CADENCE]
        refit = pd.Timestamp(oblock[0])
        train_idx = _eligible_train_index(cells.index, endpoints, refit)
        train_idx = train_idx[y.reindex(train_idx).notna().to_numpy()]
        fitted_models: dict[str, FittedModel] = {}
        for arch in BASE_ARCHITECTURES:
            params = selected_params.get(arch, {})
            if not params:
                raise ValueError(f"selected base architecture unavailable: {arch}")
            model = fit_model(arch, params, cells.loc[train_idx], families.loc[train_idx], y.loc[train_idx])
            fitted_models[arch] = model
            pred = model.predict(cells.loc[oblock], families.loc[oblock])
            prediction_paths[arch].loc[oblock] = pred
            g_paths[arch].loc[dblock] = _prediction_to_g(pred, model.train_predictions)
            diagnostics[arch]["refit_count"] += 1
            diagnostics[arch]["last_refit_diagnostics"] = model.diagnostics
        wpred = np.zeros(len(oblock), dtype=float)
        wtrain = np.zeros(len(train_idx), dtype=float)
        for arch in BASE_ARCHITECTURES:
            w = float(weights[arch])
            wpred += w * prediction_paths[arch].loc[oblock].to_numpy(dtype=float)
            wtrain += w * fitted_models[arch].train_predictions
        stack_pred.loc[oblock] = wpred
        g_paths["A08_STACKED_ENSEMBLE"].loc[dblock] = _prediction_to_g(wpred, wtrain)
    for arch, s in g_paths.items():
        if not np.isfinite(s.to_numpy()).all() or ((s < 0) | (s > 1)).any():
            raise ValueError(f"invalid gross path {arch}")
    diagnostics["A08_STACKED_ENSEMBLE"] = {"stack_weights": dict(weights), "refit_count": int(math.ceil(len(origins)/REFIT_CADENCE))}
    return g_paths, diagnostics


def cash_net_daily_from_risk_free(rf_daily: pd.Series) -> pd.Series:
    rf = _with_naive_index(pd.to_numeric(rf_daily, errors="coerce"))
    return CASH_REALIZATION * rf - CASH_ANNUAL_FEE / 365.25


def portfolio_returns_from_g(
    g: pd.Series, baseline_returns: pd.Series, baseline_gross: pd.Series, cash_net_daily: pd.Series,
) -> tuple[pd.Series, dict[str, float]]:
    g = _with_naive_index(pd.to_numeric(g, errors="coerce"))
    r = _with_naive_index(pd.to_numeric(baseline_returns, errors="coerce")).reindex(g.index)
    gross = _with_naive_index(pd.to_numeric(baseline_gross, errors="coerce")).reindex(g.index)
    cash = _with_naive_index(pd.to_numeric(cash_net_daily, errors="coerce")).reindex(g.index)
    arrs = [g.to_numpy(dtype=float), r.to_numpy(dtype=float), gross.to_numpy(dtype=float), cash.to_numpy(dtype=float)]
    if not all(np.isfinite(x).all() for x in arrs):
        raise ValueError("portfolio input contains non-finite values")
    gv, rv, bv, cv = arrs
    cash_fraction = 1.0 - gv * bv
    if np.min(cash_fraction) < -1e-12 or np.min(gv) < -1e-12 or np.max(gv) > 1 + 1e-12:
        raise ValueError("negative cash, leverage, or invalid g")
    prev = np.concatenate([[1.0], gv[:-1]])
    outer_turn = np.abs(gv - prev) * bv
    costs = OUTER_COST * outer_turn
    ret = gv * rv + cash_fraction * cv - costs
    s = pd.Series(ret, index=g.index, name="candidate_return")
    return s, {
        "average_outer_multiplier": float(np.mean(gv)),
        "average_total_gross": float(np.mean(gv * bv)),
        "average_cash_fraction": float(np.mean(cash_fraction)),
        "outer_turnover": float(np.sum(outer_turn)),
        "outer_transaction_cost_return_units": float(np.sum(costs)),
    }


def nav_from_returns(returns: pd.Series, initial: float = 10000.0) -> pd.Series:
    r = pd.to_numeric(returns, errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(r).all() or np.any(r <= -1.0):
        raise ValueError("invalid return path")
    return pd.Series(initial * np.cumprod(1.0 + r), index=returns.index, dtype=float)


def calendar_span_cagr(nav: pd.Series) -> float:
    if len(nav) < 2:
        return float("nan")
    days = (pd.Timestamp(nav.index[-1]) - pd.Timestamp(nav.index[0])).days
    if days <= 0 or float(nav.iloc[0]) <= 0 or float(nav.iloc[-1]) <= 0:
        return float("nan")
    years = days / 365.25
    return float((float(nav.iloc[-1]) / 10000.0) ** (1.0 / years) - 1.0)


def max_drawdown(nav: pd.Series) -> float:
    arr = nav.to_numpy(dtype=float)
    peak = np.maximum.accumulate(arr)
    return float(np.min(arr / peak - 1.0))


def count_balanced_blocks(n: int, k: int) -> list[np.ndarray]:
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    out, pos = [], 0
    for size in sizes:
        out.append(np.arange(pos, pos + size, dtype=int))
        pos += size
    return out


def simultaneous_mbb_lcbs(relative_log_increments: Mapping[str, np.ndarray], *, block_length: int = BOOT_BLOCK, reps: int = BOOT_REPS, seed: int = BOOT_SEED) -> tuple[float, dict[str, float]]:
    names = list(relative_log_increments)
    if not names:
        raise ValueError("no valid methods for bootstrap")
    mat = np.column_stack([np.asarray(relative_log_increments[n], dtype=float) for n in names])
    if not np.isfinite(mat).all() or len(mat) < block_length:
        raise ValueError("invalid bootstrap matrix")
    n = len(mat)
    obs = mat.mean(axis=0)
    k = int(math.ceil(n / block_length))
    rng = np.random.default_rng(seed)
    maxdiff = np.empty(reps, dtype=float)
    max_start = n - block_length
    for b in range(reps):
        starts = rng.integers(0, max_start + 1, size=k)
        idx = np.concatenate([np.arange(s, s + block_length) for s in starts])[:n]
        boot = mat[idx].mean(axis=0)
        maxdiff[b] = float(np.max(obs - boot))
    q95 = float(np.quantile(maxdiff, 0.95, method="linear"))
    return q95, {name: float(obs[i] - q95) for i, name in enumerate(names)}


def _annualized_sharpe(ret: np.ndarray) -> float:
    x = np.asarray(ret, dtype=float)
    sd = float(np.std(x, ddof=1))
    return float(math.sqrt(365.0) * np.mean(x) / sd) if len(x) > 1 and sd > 0 and np.isfinite(sd) else float("nan")


def pbo_cscv(method_returns: Mapping[str, np.ndarray], slices: int = 8) -> dict[str, Any]:
    names = list(method_returns)
    mat = np.column_stack([np.asarray(method_returns[n], dtype=float) for n in names])
    if not np.isfinite(mat).all() or len(names) < 2:
        return {"status": "NOT_WELL_DEFINED"}
    blocks = count_balanced_blocks(len(mat), slices)
    records = []
    overfit = 0
    for combo in itertools.combinations(range(slices), slices // 2):
        ins = np.concatenate([blocks[i] for i in combo])
        outs = np.concatenate([blocks[i] for i in range(slices) if i not in combo])
        sr_in = np.array([_annualized_sharpe(mat[ins, j]) for j in range(len(names))])
        sr_out = np.array([_annualized_sharpe(mat[outs, j]) for j in range(len(names))])
        if not np.isfinite(sr_in).all() or not np.isfinite(sr_out).all():
            continue
        winner = int(np.argmax(sr_in))
        ranks = rankdata(sr_out, method="average")  # rank 1=worst, rank m=best
        bad = bool(ranks[winner] <= (len(names) + 1.0) / 2.0)
        overfit += int(bad)
        records.append({"in_slices": list(combo), "winner": names[winner], "winner_oos_rank": float(ranks[winner]), "overfit": bad})
    return {
        "status": "OK" if records else "NOT_WELL_DEFINED",
        "split_count": len(records),
        "pbo": float(overfit / len(records)) if records else None,
        "records": records,
    }


def deflated_sharpe_diagnostic(ret: np.ndarray, trial_count: int = 71) -> dict[str, Any]:
    x = np.asarray(ret, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 30 or trial_count < 2:
        return {"status": "NOT_WELL_DEFINED"}
    sd = float(np.std(x, ddof=1))
    if sd <= 0:
        return {"status": "NOT_WELL_DEFINED"}
    sr = float(np.mean(x) / sd)  # daily Sharpe, matching finite-sample formula
    sk = float(skew(x, bias=False))
    ku = float(kurtosis(x, fisher=False, bias=False))
    var_null = 1.0 / max(len(x) - 1, 1)
    gamma = 0.5772156649015329
    sr_star = math.sqrt(var_null) * ((1.0 - gamma) * norm.ppf(1.0 - 1.0 / trial_count) + gamma * norm.ppf(1.0 - 1.0 / (trial_count * math.e)))
    denom_sq = (1.0 - sk * sr + ((ku - 1.0) / 4.0) * sr * sr) / max(len(x) - 1, 1)
    if not np.isfinite(denom_sq) or denom_sq <= 0:
        return {"status": "NOT_WELL_DEFINED"}
    z = (sr - sr_star) / math.sqrt(denom_sq)
    return {
        "status": "OK", "trial_count": trial_count, "daily_sharpe": sr,
        "annualized_sharpe": sr * math.sqrt(365.0), "skew": sk, "kurtosis": ku,
        "expected_max_null_daily_sharpe": float(sr_star), "deflated_sharpe_z": float(z),
        "deflated_sharpe_probability": float(norm.cdf(z)),
        "formula_note": "Bailey-Lopez-de-Prado-style finite-sample PSR adjustment with expected maximum null Sharpe under 71 declared trials; diagnostic only.",
    }


def evaluate_tournament(
    frames: Mapping[str, pd.DataFrame],
    baseline_returns: pd.Series,
    baseline_gross: pd.Series,
    rf_daily: pd.Series,
    *,
    enforce_historical_anchors: bool = False,
) -> dict[str, Any]:
    """Single top-level scientific engine call. It performs no file or network I/O."""
    cells, families, _ = build_signal_atlas(frames)
    cells = _with_naive_index(cells)
    families = _with_naive_index(families).loc[:, FAMILY_ORDER]
    if cells.shape[1] != 185 or families.shape[1] != 17:
        raise RuntimeError("0065 feature dimension drift")
    btc = _with_naive_index(frames["BTC"])
    y, endpoints = _target_and_endpoints(btc["close"])
    common = cells.index.intersection(families.index).intersection(y.index)
    cells, families, y, endpoints = cells.loc[common], families.loc[common], y.loc[common], endpoints.loc[common]

    selected, validation_mse, validation_predictions, validation_audit = select_hyperparameters(cells, families, y, endpoints)
    if any(not selected.get(a) for a in BASE_ARCHITECTURES):
        return {
            "primary_result": {
                "schema_version": 1, "research_id": RID, "classification": "MEASUREMENT_INCONCLUSIVE_MODEL_FIT_FAILURE",
                "actual_validation_configs_evaluated": 63, "final_architecture_count": 8,
                "validation_audit": validation_audit,
            },
            "evidence": {"selected_hyperparameters": selected, "validation_mse": validation_mse},
        }
    validation_idx = cells.index[(cells.index >= VALID_START) & (cells.index <= VALID_END)]
    weights = stack_weights(validation_predictions, y.loc[validation_idx])

    base_r = _with_naive_index(pd.to_numeric(baseline_returns, errors="coerce"))
    base_g = _with_naive_index(pd.to_numeric(baseline_gross, errors="coerce"))
    rf = _with_naive_index(pd.to_numeric(rf_daily, errors="coerce"))
    eval_idx = base_r.index[(base_r.index >= EVAL_START) & (base_r.index <= EVAL_END)]
    if len(eval_idx) == 0 or not eval_idx.equals(base_g.reindex(eval_idx).index):
        raise ValueError("evaluation support unavailable")
    cash_net = cash_net_daily_from_risk_free(rf).reindex(eval_idx)
    if not np.isfinite(cash_net.to_numpy(dtype=float)).all():
        raise ValueError("cash rate support incomplete")

    benchmark_g = pd.Series(1.0, index=eval_idx)
    benchmark_r, benchmark_extra = portfolio_returns_from_g(benchmark_g, base_r.reindex(eval_idx), base_g.reindex(eval_idx), cash_net)
    benchmark_nav = nav_from_returns(benchmark_r)
    benchmark = {
        "terminal_wealth": float(benchmark_nav.iloc[-1]),
        "cagr": calendar_span_cagr(benchmark_nav),
        "max_drawdown": max_drawdown(benchmark_nav),
        **benchmark_extra,
    }
    if enforce_historical_anchors:
        for key, target in EXPECTED_0064.items():
            if not math.isclose(float(benchmark[key]), float(target), rel_tol=0.0, abs_tol=1e-12):
                raise ValueError(f"0064 benchmark reconstruction drift {key}: {benchmark[key]} != {target}")

    g_paths, eval_diag = evaluation_g_paths(cells, families, y, endpoints, eval_idx, selected, weights)
    method_results: dict[str, Any] = {}
    rel_series: dict[str, np.ndarray] = {}
    method_returns: dict[str, np.ndarray] = {}
    blocks = count_balanced_blocks(len(eval_idx), 4)
    benchmark_arr = benchmark_r.to_numpy(dtype=float)
    for arch in ARCHITECTURES:
        ret, extra = portfolio_returns_from_g(g_paths[arch], base_r.reindex(eval_idx), base_g.reindex(eval_idx), cash_net)
        nav = nav_from_returns(ret)
        rel = np.log1p(ret.to_numpy(dtype=float)) - np.log1p(benchmark_arr)
        block_rel = [float(np.sum(rel[ix])) for ix in blocks]
        method_results[arch] = {
            "status": "EVALUATED",
            "selected_hyperparameters": selected.get(arch) if arch != "A08_STACKED_ENSEMBLE" else {"stack_weights": weights},
            "validation_MSE": validation_mse.get(arch) if arch != "A08_STACKED_ENSEMBLE" else float(np.mean((np.column_stack([validation_predictions[a].reindex(validation_idx).to_numpy(dtype=float) for a in BASE_ARCHITECTURES]) @ np.array([weights[a] for a in BASE_ARCHITECTURES]) - y.loc[validation_idx].to_numpy(dtype=float)) ** 2)),
            "terminal_wealth": float(nav.iloc[-1]), "calendar_CAGR": calendar_span_cagr(nav), "max_drawdown": max_drawdown(nav),
            **extra,
            "four_block_relative_log_growth": block_rel,
            "positive_block_count": int(sum(v > 0 for v in block_rel)),
            "relative_terminal_log_growth": float(np.sum(rel)),
            "evaluation_diagnostics": eval_diag.get(arch, {}),
            "deflated_sharpe": deflated_sharpe_diagnostic(ret.to_numpy(dtype=float), 71),
        }
        rel_series[arch] = rel
        method_returns[arch] = ret.to_numpy(dtype=float)

    q95, lcbs = simultaneous_mbb_lcbs(rel_series)
    for arch in ARCHITECTURES:
        m = method_results[arch]
        m["simultaneous_LCB"] = lcbs[arch]
        m["G2"] = bool(m["terminal_wealth"] > benchmark["terminal_wealth"] and m["calendar_CAGR"] > benchmark["cagr"])
        m["G3"] = bool(m["max_drawdown"] >= benchmark["max_drawdown"] - 1e-12)
        m["G4"] = bool(m["positive_block_count"] >= 3)
        m["G5"] = bool(m["simultaneous_LCB"] > 0.0)
        m["G6"] = bool(m["average_cash_fraction"] >= -1e-12 and m["average_outer_multiplier"] <= 1.0 + 1e-12)
        m["passes_all_scientific_gates"] = bool(m["G2"] and m["G3"] and m["G4"] and m["G5"] and m["G6"])

    winners = [a for a in ARCHITECTURES if method_results[a]["passes_all_scientific_gates"]]
    descriptive_best = max(ARCHITECTURES, key=lambda a: method_results[a]["calendar_CAGR"])
    classification = "PASS_MULTI_ARCHITECTURE_GROSS_CONTROLLER" if winners else "FAIL_NO_ROBUST_MULTI_ARCHITECTURE_IMPROVEMENT"
    primary = {
        "schema_version": 1, "research_id": RID, "classification": classification,
        "actual_validation_configs_evaluated": 63, "final_architecture_count": 8, "actual_variants_evaluated": 71,
        "benchmark_0064": benchmark, "methods": method_results,
        "descriptive_best_CAGR_method": descriptive_best,
        "scientific_winners": winners,
        "simultaneous_bootstrap": {"block_length": BOOT_BLOCK, "replicates": BOOT_REPS, "seed": BOOT_SEED, "q95": q95},
        "PBO_CSCV": pbo_cscv(method_returns, 8),
        "stack_weights": weights,
        "production_authorized": False, "signature_authorized": False, "order_submission_authorized": False,
    }
    evidence = {
        "selected_hyperparameters": selected, "validation_mse": validation_mse, "validation_audit": validation_audit,
        "stack_weights": weights,
        "evaluation_dates": [str(x.date()) for x in eval_idx],
        "gross_paths": {a: [float(v) for v in g_paths[a].to_numpy(dtype=float)] for a in ARCHITECTURES},
        "relative_log_increment_series": {a: [float(v) for v in rel_series[a]] for a in ARCHITECTURES},
        "method_return_series": {a: [float(v) for v in method_returns[a]] for a in ARCHITECTURES},
    }
    return {"primary_result": primary, "evidence": evidence}
