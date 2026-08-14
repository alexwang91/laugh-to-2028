from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.optimize import nnls
from scipy.stats import mannwhitneyu
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler

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
BASE_ARCHITECTURES = (
    "P01_FAMILY_RIDGE_LOGIT",
    "P02_RAW_ELASTIC_NET_LOGIT",
    "P03_VALIDATION_SCREENED_SIGNAL_LOGIT",
    "P04_PCR_LOGIT",
    "P05_THEORY_QUADRATIC_LOGIT",
    "P06_SHALLOW_GBDT_CLASSIFIER",
    "P07_DISCRETE_TIME_HAZARD_LOGIT",
)
ARCHITECTURES = BASE_ARCHITECTURES + ("P08_STACKED_PROBABILITY_ENSEMBLE",)


def frozen_configurations() -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {
        "P01_FAMILY_RIDGE_LOGIT": [{"C": c} for c in (0.01, 0.1, 1.0, 10.0)],
        "P02_RAW_ELASTIC_NET_LOGIT": [{"C": c, "l1_ratio": l} for c in (0.01, 0.1, 1.0) for l in (0.1, 0.5, 0.9)],
        "P03_VALIDATION_SCREENED_SIGNAL_LOGIT": [{"C": c} for c in (0.1, 1.0, 10.0)],
        "P04_PCR_LOGIT": [{"n_components": n, "C": c} for n in (5, 10, 20, 40) for c in (0.1, 1.0, 10.0)],
        "P05_THEORY_QUADRATIC_LOGIT": [{"C": c} for c in (0.001, 0.01, 0.1, 1.0)],
        "P06_SHALLOW_GBDT_CLASSIFIER": [
            {"max_depth": d, "n_estimators": n, "learning_rate": lr}
            for d in (1, 2) for n in (50, 100) for lr in (0.03, 0.1)
        ],
        "P07_DISCRETE_TIME_HAZARD_LOGIT": [{"C": c} for c in (0.01, 0.1, 1.0, 10.0)],
    }
    expected = {"P01_FAMILY_RIDGE_LOGIT": 4, "P02_RAW_ELASTIC_NET_LOGIT": 9, "P03_VALIDATION_SCREENED_SIGNAL_LOGIT": 3, "P04_PCR_LOGIT": 12, "P05_THEORY_QUADRATIC_LOGIT": 4, "P06_SHALLOW_GBDT_CLASSIFIER": 8, "P07_DISCRETE_TIME_HAZARD_LOGIT": 4}
    if {k: len(v) for k, v in out.items()} != expected:
        raise RuntimeError("0066 frozen configuration drift")
    return out


def canonical_params(params: Mapping[str, Any]) -> str:
    return json.dumps(dict(params), sort_keys=True, separators=(",", ":"))


def count_balanced_blocks(n: int, k: int = 4) -> list[np.ndarray]:
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    out: list[np.ndarray] = []
    pos = 0
    for size in sizes:
        out.append(np.arange(pos, pos + size, dtype=int))
        pos += size
    return out


def binary_metrics(y: Sequence[float], score: Sequence[float], probability: Sequence[float] | None = None, *, include_blocks: bool = False) -> dict[str, Any]:
    yy = np.asarray(y, dtype=float)
    ss = np.asarray(score, dtype=float)
    mask = np.isfinite(yy) & np.isfinite(ss)
    if probability is not None:
        pp = np.asarray(probability, dtype=float)
        mask &= np.isfinite(pp)
    else:
        pp = None
    yy, ss = yy[mask], ss[mask]
    if pp is not None:
        pp = np.clip(pp[mask], 0.0, 1.0)
    if len(yy) == 0 or len(np.unique(yy)) < 2:
        return {"status": "NOT_WELL_DEFINED", "n": int(len(yy)), "positives": int(np.sum(yy == 1.0))}
    prevalence = float(np.mean(yy))
    auc = float(roc_auc_score(yy, ss))
    ap = float(average_precision_score(yy, ss))
    out: dict[str, Any] = {
        "status": "OK",
        "n": int(len(yy)),
        "positives": int(np.sum(yy == 1.0)),
        "prevalence": prevalence,
        "ROC_AUC": auc,
        "PR_AUC": ap,
        "PR_AUC_LIFT": float(ap - prevalence),
        "Brier": float(brier_score_loss(yy, pp)) if pp is not None else None,
    }
    if include_blocks:
        blocks = []
        for ix in count_balanced_blocks(len(yy), 4):
            if len(ix) == 0 or len(np.unique(yy[ix])) < 2:
                blocks.append({"status": "NOT_WELL_DEFINED", "n": int(len(ix)), "prevalence": float(np.mean(yy[ix])) if len(ix) else None})
            else:
                prev = float(np.mean(yy[ix]))
                ba = float(roc_auc_score(yy[ix], ss[ix]))
                bp = float(average_precision_score(yy[ix], ss[ix]))
                blocks.append({"status": "OK", "n": int(len(ix)), "prevalence": prev, "ROC_AUC": ba, "PR_AUC": bp, "PR_AUC_LIFT": float(bp - prev)})
        out["chronological_blocks"] = blocks
    return out


def validation_rank_key(metrics: Mapping[str, Any], params: Mapping[str, Any] | None = None) -> tuple:
    if metrics.get("status") != "OK":
        return (float("inf"), float("inf"), float("inf"), canonical_params(params or {}))
    return (
        -float(metrics["PR_AUC_LIFT"]),
        -float(metrics["ROC_AUC"]),
        float(metrics["Brier"]) if metrics.get("Brier") is not None else float("inf"),
        canonical_params(params or {}),
    )


def _median_impute(train: pd.DataFrame, other: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    med = train.median(axis=0, skipna=True).to_numpy(dtype=float)
    if not np.isfinite(med).all():
        raise ValueError("all-missing required feature column")
    a = train.to_numpy(dtype=float)
    b = other.to_numpy(dtype=float)
    return np.where(np.isfinite(a), a, med), np.where(np.isfinite(b), b, med), med


def _impute(frame: pd.DataFrame, med: np.ndarray) -> np.ndarray:
    x = frame.to_numpy(dtype=float)
    return np.where(np.isfinite(x), x, med)


def quadratic_frame(families: pd.DataFrame) -> pd.DataFrame:
    f = families.loc[:, FAMILY_ORDER]
    cols: dict[str, pd.Series] = {c: f[c] for c in FAMILY_ORDER}
    for c in FAMILY_ORDER:
        cols[f"SQ::{c}"] = f[c] * f[c]
    for a, b in INTERACTIONS:
        cols[f"X::{a}::{b}"] = f[a] * f[b]
    out = pd.DataFrame(cols, index=f.index)
    if out.shape[1] != 44:
        raise RuntimeError("0066 quadratic width drift")
    return out


@dataclass
class FittedClassifier:
    architecture: str
    payload: dict[str, Any]

    def predict_proba(self, cells: pd.DataFrame, families: pd.DataFrame, signals: pd.DataFrame) -> np.ndarray:
        a, p = self.architecture, self.payload
        if a == "P01_FAMILY_RIDGE_LOGIT":
            frame = families.loc[:, FAMILY_ORDER]
        elif a == "P02_RAW_ELASTIC_NET_LOGIT":
            frame = cells.loc[:, p["columns"]]
        elif a == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT":
            frame = signals.loc[:, p["columns"]]
        elif a == "P04_PCR_LOGIT":
            frame = cells.loc[:, p["columns"]]
        elif a == "P05_THEORY_QUADRATIC_LOGIT":
            frame = quadratic_frame(families)
        elif a == "P06_SHALLOW_GBDT_CLASSIFIER":
            frame = families.loc[:, FAMILY_ORDER]
        else:
            raise KeyError(a)
        x = _impute(frame, p["median"])
        if p.get("scaler") is not None:
            x = p["scaler"].transform(x)
        if p.get("pca") is not None:
            x = p["pca"].transform(x)
        return np.asarray(p["model"].predict_proba(x)[:, 1], dtype=float)


def fit_classifier(
    architecture: str,
    params: Mapping[str, Any],
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    y: pd.Series,
    *,
    selected_signals: Sequence[str] | None = None,
) -> FittedClassifier:
    yy = pd.to_numeric(y, errors="coerce")
    if len(yy) < 10 or yy.nunique(dropna=True) < 2:
        raise ValueError("classifier training labels lack both classes")
    if architecture == "P01_FAMILY_RIDGE_LOGIT":
        frame = families.loc[:, FAMILY_ORDER]
        model = LogisticRegression(C=float(params["C"]), penalty="l2", solver="lbfgs", class_weight="balanced", max_iter=5000)
        use_scale, pca = True, None
    elif architecture == "P02_RAW_ELASTIC_NET_LOGIT":
        frame = cells.copy()
        model = LogisticRegression(C=float(params["C"]), penalty="elasticnet", solver="saga", l1_ratio=float(params["l1_ratio"]), class_weight="balanced", max_iter=10000, tol=1e-6, random_state=660066)
        use_scale, pca = True, None
    elif architecture == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT":
        cols = list(selected_signals or [])
        if not cols:
            raise ValueError("P03 has no validation-screened signals")
        frame = signals.loc[:, cols]
        model = LogisticRegression(C=float(params["C"]), penalty="l2", solver="lbfgs", class_weight="balanced", max_iter=5000)
        use_scale, pca = True, None
    elif architecture == "P04_PCR_LOGIT":
        frame = cells.copy()
        model = LogisticRegression(C=float(params["C"]), penalty="l2", solver="lbfgs", class_weight="balanced", max_iter=5000)
        use_scale = True
        pca = PCA(n_components=int(params["n_components"]), svd_solver="full")
    elif architecture == "P05_THEORY_QUADRATIC_LOGIT":
        frame = quadratic_frame(families)
        model = LogisticRegression(C=float(params["C"]), penalty="l2", solver="lbfgs", class_weight="balanced", max_iter=5000)
        use_scale, pca = True, None
    elif architecture == "P06_SHALLOW_GBDT_CLASSIFIER":
        frame = families.loc[:, FAMILY_ORDER]
        model = GradientBoostingClassifier(max_depth=int(params["max_depth"]), n_estimators=int(params["n_estimators"]), learning_rate=float(params["learning_rate"]), min_samples_leaf=20, subsample=0.8, random_state=660066)
        use_scale, pca = False, None
    else:
        raise KeyError(architecture)

    x, _, med = _median_impute(frame, frame)
    scaler = StandardScaler().fit(x) if use_scale else None
    xs = scaler.transform(x) if scaler is not None else x
    if pca is not None:
        max_components = min(xs.shape[0], xs.shape[1])
        if int(params["n_components"]) > max_components:
            raise ValueError("PCA components exceed training rank bound")
        pca.fit(xs)
        xs = pca.transform(xs)
    model.fit(xs, yy.to_numpy(dtype=int))
    cols = list(frame.columns)
    return FittedClassifier(architecture, {"model": model, "median": med, "scaler": scaler, "pca": pca, "columns": cols})


@dataclass
class FittedHazard:
    model: LogisticRegression
    median: np.ndarray
    scaler: StandardScaler

    def predict(self, families: pd.DataFrame, horizon: int) -> np.ndarray:
        base = families.loc[:, FAMILY_ORDER]
        x = _impute(base, self.median)
        x = self.scaler.transform(x)
        hcols = np.column_stack([np.full(len(base), 1.0 if horizon == h else 0.0) for h in (1, 3, 5, 10, 20)])
        return np.asarray(self.model.predict_proba(np.column_stack([x, hcols]))[:, 1], dtype=float)


def fit_hazard(families: pd.DataFrame, labels_by_horizon: Mapping[int, pd.Series], params: Mapping[str, Any]) -> FittedHazard:
    base = families.loc[:, FAMILY_ORDER]
    med = base.median(axis=0, skipna=True).to_numpy(dtype=float)
    if not np.isfinite(med).all():
        raise ValueError("hazard all-missing family")
    xbase = _impute(base, med)
    scaler = StandardScaler().fit(xbase)
    xbase = scaler.transform(xbase)
    rows, ys = [], []
    for h in (1, 3, 5, 10, 20):
        y = pd.to_numeric(labels_by_horizon[h], errors="coerce").reindex(base.index)
        mask = y.notna().to_numpy()
        if not mask.any():
            continue
        hcols = np.column_stack([np.full(int(mask.sum()), 1.0 if h == hh else 0.0) for hh in (1, 3, 5, 10, 20)])
        rows.append(np.column_stack([xbase[mask], hcols]))
        ys.append(y.to_numpy(dtype=float)[mask])
    if not rows:
        raise ValueError("hazard no risk-set rows")
    X = np.vstack(rows)
    Y = np.concatenate(ys).astype(int)
    if len(np.unique(Y)) < 2:
        raise ValueError("hazard labels lack both classes")
    model = LogisticRegression(C=float(params["C"]), penalty="l2", solver="lbfgs", class_weight="balanced", max_iter=5000)
    model.fit(X, Y)
    return FittedHazard(model, med, scaler)


def stack_weights(validation_predictions: Mapping[str, np.ndarray], y: np.ndarray) -> dict[str, float]:
    names = [a for a in BASE_ARCHITECTURES if a in validation_predictions]
    if not names:
        raise ValueError("no base predictions for stack")
    mat = np.column_stack([np.asarray(validation_predictions[a], dtype=float) for a in names])
    yy = np.asarray(y, dtype=float)
    mask = np.isfinite(yy) & np.isfinite(mat).all(axis=1)
    if mask.sum() < 10 or len(np.unique(yy[mask])) < 2:
        return {a: 1.0 / len(names) for a in names}
    w, _ = nnls(mat[mask], yy[mask])
    if not np.isfinite(w).all() or float(w.sum()) <= 0:
        w = np.ones(len(names), dtype=float)
    w = w / w.sum()
    return {a: float(w[i]) for i, a in enumerate(names)}


def holm_adjust(pvalues: Mapping[str, float], alpha: float = 0.05) -> dict[str, dict[str, float | bool]]:
    finite = [(k, float(v)) for k, v in pvalues.items() if np.isfinite(v)]
    finite.sort(key=lambda kv: (kv[1], kv[0]))
    m = len(finite)
    adjusted: dict[str, float] = {}
    running = 0.0
    for i, (k, p) in enumerate(finite):
        raw_adj = min(1.0, (m - i) * p)
        running = max(running, raw_adj)
        adjusted[k] = running
    return {k: {"raw_p": p, "holm_adjusted_p": adjusted[k], "reject_fwer_0_05": bool(adjusted[k] <= alpha)} for k, p in finite}


def one_sided_auc_pvalue(y: Sequence[float], oriented_score: Sequence[float]) -> float:
    yy = np.asarray(y, dtype=float)
    ss = np.asarray(oriented_score, dtype=float)
    mask = np.isfinite(yy) & np.isfinite(ss)
    yy, ss = yy[mask], ss[mask]
    pos, neg = ss[yy == 1.0], ss[yy == 0.0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    return float(mannwhitneyu(pos, neg, alternative="greater", method="auto").pvalue)


def empirical_percentile(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    ref = np.sort(np.asarray(reference, dtype=float)[np.isfinite(reference)])
    v = np.asarray(values, dtype=float)
    if len(ref) == 0:
        raise ValueError("empty percentile calibration reference")
    return np.searchsorted(ref, v, side="right").astype(float) / float(len(ref))
