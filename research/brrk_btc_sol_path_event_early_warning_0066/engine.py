from __future__ import annotations

import itertools
import math
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.special import expit, logit
from scipy.stats import rankdata
from sklearn.metrics import average_precision_score, roc_auc_score

from research.brrk_btc_risk_signal_atlas_0062.engine import build_signal_atlas
from research.brrk_btc_sol_path_event_early_warning_0066 import event_engine as ee
from research.brrk_btc_sol_path_event_early_warning_0066 import models as mdl

RID = "BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-0066"
TARGETS = ("T1_ANY_DOWN", "T2_MAJOR_DOWN", "T3_ANY_SIDEWAYS", "T4_LONG_SIDEWAYS")
VALID_START = pd.Timestamp("2023-01-01")
VALID_END = pd.Timestamp("2023-12-31")
FINAL_START = pd.Timestamp("2024-01-01")
FINAL_END = pd.Timestamp("2025-11-15")
ECON_START = pd.Timestamp("2024-01-01")
ECON_END = pd.Timestamp("2026-08-02")
REFIT_CADENCE = 20
MAX_EVENT_H = 240
OUTER_COST = 0.001
CASH_REALIZATION = 0.5
CASH_ANNUAL_FEE = 0.01
BOOT_BLOCK = 60
BOOT_REPS = 4000
BOOT_SEED = 660066
CONTROLLERS = (
    "C01_BTC_ANY_DOWN_5D",
    "C02_SOL_ANY_DOWN_5D",
    "C03_MAX_BTC_SOL_ANY_DOWN_5D",
    "C04_BTC_MAJOR_DOWN_10D",
    "C05_MAX_BTC_SOL_MAJOR_DOWN_10D",
    "C06_MULTILEAD_DOWN_BLEND_3_5_10",
    "C07_DOWN_PLUS_SIDEWAYS",
    "C08_STACKED_EVENT_RISK",
)


def _idx(index: pd.Index) -> pd.DatetimeIndex:
    return ee.naive_index(index)


def _series(obj: pd.Series) -> pd.Series:
    return ee.with_naive_index(pd.to_numeric(obj, errors="coerce"))


def _track(asset: str, target: str, horizon: int) -> str:
    return f"{asset}|{target}|L{horizon}"


def _atrack(architecture: str, asset: str, target: str, horizon: int) -> str:
    return f"{architecture}|{asset}|{target}|L{horizon}"


def _naive_frames(frames: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {k: ee.with_naive_index(v) for k, v in frames.items()}


def _common_feature_objects(frames: Mapping[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], pd.DataFrame]:
    cells, families, meta = build_signal_atlas(frames)
    cells = ee.with_naive_index(cells)
    families = ee.with_naive_index(families).loc[:, mdl.FAMILY_ORDER]
    if cells.shape[1] != 185 or families.shape[1] != 17:
        raise RuntimeError("0066 frozen feature dimension drift")
    common = cells.index.intersection(families.index).sort_values()
    cells = cells.loc[common]
    families = families.loc[common]
    signals = pd.concat([cells, families], axis=1)
    if signals.shape[1] != 202 or signals.columns.duplicated().any():
        raise RuntimeError("0066 signal-unit identity drift")
    return cells, families, meta, signals


def _labels_and_support(bundle: ee.EventBundle, common: pd.DatetimeIndex) -> tuple[dict[tuple[str, str, int], pd.Series], dict[tuple[str, str, int], dict[str, Any]]]:
    labels: dict[tuple[str, str, int], pd.Series] = {}
    support: dict[tuple[str, str, int], dict[str, Any]] = {}
    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                key = (asset, target, h)
                labels[key] = ee.build_warning_labels(bundle, asset, target, h, common)
                support[key] = ee.unique_onset_support(bundle, asset, target, h, common)
    if len(labels) != 40:
        raise RuntimeError("warning track count drift")
    return labels, support


def _mature_training_index(common: pd.DatetimeIndex, label: pd.Series, market_index: pd.DatetimeIndex, refit: pd.Timestamp, horizon: int) -> pd.DatetimeIndex:
    market_pos = {d: i for i, d in enumerate(market_index)}
    refit_pos = market_pos.get(pd.Timestamp(refit))
    if refit_pos is None:
        raise ValueError("refit date absent from market calendar")
    out = []
    for d in common[common < refit]:
        pos = market_pos.get(pd.Timestamp(d))
        if pos is None:
            continue
        if pos + int(horizon) + MAX_EVENT_H < refit_pos and np.isfinite(label.get(d, np.nan)):
            out.append(d)
    return pd.DatetimeIndex(out)


def _period_index(common: pd.DatetimeIndex, start: pd.Timestamp, end: pd.Timestamp) -> pd.DatetimeIndex:
    return common[(common >= start) & (common <= end)]


def _walk_forward_classifier(
    architecture: str,
    params: Mapping[str, Any],
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    label: pd.Series,
    market_index: pd.DatetimeIndex,
    horizon: int,
    prediction_index: pd.DatetimeIndex,
    *,
    selected_signals: Sequence[str] | None = None,
) -> tuple[pd.Series, dict[str, Any]]:
    pred = pd.Series(np.nan, index=prediction_index, dtype=float)
    audit = {"refit_count": 0, "fit_failures": []}
    for start in range(0, len(prediction_index), REFIT_CADENCE):
        block = prediction_index[start:start + REFIT_CADENCE]
        if len(block) == 0:
            continue
        refit = pd.Timestamp(block[0])
        train_idx = _mature_training_index(cells.index, label, market_index, refit, horizon)
        ytrain = label.reindex(train_idx)
        train_idx = train_idx[ytrain.notna().to_numpy()]
        ytrain = ytrain.loc[train_idx]
        try:
            fitted = mdl.fit_classifier(
                architecture, params,
                cells.loc[train_idx], families.loc[train_idx], signals.loc[train_idx], ytrain,
                selected_signals=selected_signals,
            )
            pred.loc[block] = fitted.predict_proba(cells.loc[block], families.loc[block], signals.loc[block])
            audit["refit_count"] += 1
        except Exception as exc:
            audit["fit_failures"].append({"refit": refit.isoformat(), "error_type": type(exc).__name__, "error_message": str(exc)})
    return pred, audit


def _walk_forward_hazard(
    params: Mapping[str, Any],
    families: pd.DataFrame,
    labels_by_h: Mapping[int, pd.Series],
    market_index: pd.DatetimeIndex,
    prediction_index: pd.DatetimeIndex,
) -> tuple[dict[int, pd.Series], dict[str, Any]]:
    preds = {h: pd.Series(np.nan, index=prediction_index, dtype=float) for h in ee.WARNING_HORIZONS}
    audit = {"refit_count": 0, "fit_failures": []}
    pos = {d: i for i, d in enumerate(market_index)}
    for start in range(0, len(prediction_index), REFIT_CADENCE):
        block = prediction_index[start:start + REFIT_CADENCE]
        if len(block) == 0:
            continue
        refit = pd.Timestamp(block[0])
        refit_pos = pos.get(refit)
        if refit_pos is None:
            raise ValueError("hazard refit date absent from market calendar")
        union: list[pd.Timestamp] = []
        prepared: dict[int, pd.Series] = {}
        for h in ee.WARNING_HORIZONS:
            lab = labels_by_h[h].copy()
            eligible = []
            for d in families.index[families.index < refit]:
                p = pos.get(pd.Timestamp(d))
                if p is not None and p + h + MAX_EVENT_H < refit_pos and np.isfinite(lab.get(d, np.nan)):
                    eligible.append(d)
            eidx = pd.DatetimeIndex(eligible)
            tmp = pd.Series(np.nan, index=families.index, dtype=float)
            tmp.loc[eidx] = lab.loc[eidx]
            prepared[h] = tmp
            union.extend(list(eidx))
        train_idx = pd.DatetimeIndex(sorted(set(union)))
        try:
            fitted = mdl.fit_hazard(families.loc[train_idx], {h: prepared[h].loc[train_idx] for h in ee.WARNING_HORIZONS}, params)
            for h in ee.WARNING_HORIZONS:
                preds[h].loc[block] = fitted.predict(families.loc[block], h)
            audit["refit_count"] += 1
        except Exception as exc:
            audit["fit_failures"].append({"refit": refit.isoformat(), "error_type": type(exc).__name__, "error_message": str(exc)})
    return preds, audit


def _signal_family_map(meta: Mapping[str, Any], signal_columns: Sequence[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in signal_columns:
        if c in meta:
            out[c] = str(meta[c].family)
        elif c in mdl.FAMILY_ORDER:
            out[c] = c
        else:
            raise RuntimeError(f"unknown signal unit {c}")
    return out


def _train_orientation_and_calibration(signal: pd.Series, label: pd.Series, train_idx: pd.DatetimeIndex) -> tuple[float, float, float, float]:
    x = pd.to_numeric(signal.reindex(train_idx), errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(label.reindex(train_idx), errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 10 or len(np.unique(y)) < 2:
        return 1.0, 0.0, 1.0, 0.5
    corr = float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 0 and np.std(y) > 0 else 0.0
    orientation = -1.0 if np.isfinite(corr) and corr < 0 else 1.0
    xo = orientation * x
    mu = float(np.mean(xo))
    sd = float(np.std(xo, ddof=1))
    if not np.isfinite(sd) or sd <= 0:
        sd = 1.0
    prev = float(np.clip(np.mean(y), 1e-6, 1 - 1e-6))
    return orientation, mu, sd, prev


def _signal_metrics_with_fixed_calibration(signal: pd.Series, label: pd.Series, index: pd.DatetimeIndex, orientation: float, mu: float, sd: float, prevalence_train: float) -> dict[str, Any]:
    raw = pd.to_numeric(signal.reindex(index), errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(label.reindex(index), errors="coerce").to_numpy(dtype=float)
    score = orientation * raw
    prob = expit(logit(prevalence_train) + (score - mu) / sd)
    return mdl.binary_metrics(y, score, prob, include_blocks=True)


def build_indicator_warning_atlas(
    signals: pd.DataFrame,
    meta: Mapping[str, Any],
    labels: Mapping[tuple[str, str, int], pd.Series],
    support: Mapping[tuple[str, str, int], Mapping[str, Any]],
    market_indices: Mapping[str, pd.DatetimeIndex],
) -> tuple[dict[str, Any], dict[tuple[str, str, int], list[str]]]:
    family_map = _signal_family_map(meta, list(signals.columns))
    validation_idx = _period_index(signals.index, VALID_START, VALID_END)
    final_idx = _period_index(signals.index, FINAL_START, FINAL_END)
    rows: dict[str, Any] = {}
    screened: dict[tuple[str, str, int], list[str]] = {}
    final_pvalues: dict[str, float] = {}

    for asset in ee.ASSETS:
        market_index = market_indices[asset]
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                key = (asset, target, h)
                label = labels[key]
                train_idx = _mature_training_index(signals.index, label, market_index, VALID_START, h)
                candidates_for_screen: list[tuple[float, str]] = []
                for c in signals.columns:
                    orient, mu, sd, prev = _train_orientation_and_calibration(signals[c], label, train_idx)
                    vm = _signal_metrics_with_fixed_calibration(signals[c], label, validation_idx, orient, mu, sd, prev)
                    fm = _signal_metrics_with_fixed_calibration(signals[c], label, final_idx, orient, mu, sd, prev)
                    cell_key = f"{asset}|{target}|L{h}|{c}"
                    rows[cell_key] = {
                        "asset": asset, "target": target, "warning_horizon": h, "signal_id": c, "family": family_map[c],
                        "orientation": int(orient), "train_calibration_mean": mu, "train_calibration_sd": sd, "train_prevalence": prev,
                        "support": dict(support[key]), "validation": vm, "final": fm,
                    }
                    if vm.get("status") == "OK":
                        blocks = vm.get("chronological_blocks", [])
                        good = sum(b.get("status") == "OK" and float(b.get("PR_AUC_LIFT", -1.0)) > 0 for b in blocks)
                        if float(vm["PR_AUC_LIFT"]) > 0 and good >= 3:
                            candidates_for_screen.append((-float(vm["PR_AUC_LIFT"]), c))
                    if bool(support[key].get("support_pass")) and fm.get("status") == "OK":
                        yy = label.reindex(final_idx).to_numpy(dtype=float)
                        ss = orient * pd.to_numeric(signals[c].reindex(final_idx), errors="coerce").to_numpy(dtype=float)
                        final_pvalues[cell_key] = mdl.one_sided_auc_pvalue(yy, ss)

                candidates_for_screen.sort(key=lambda x: (x[0], x[1]))
                picked: list[str] = []
                per_family: dict[str, int] = {}
                for _, c in candidates_for_screen:
                    fam = family_map[c]
                    if per_family.get(fam, 0) >= 2:
                        continue
                    picked.append(c)
                    per_family[fam] = per_family.get(fam, 0) + 1
                    if len(picked) >= 12:
                        break
                screened[key] = picked

    holm = mdl.holm_adjust(final_pvalues)
    for k, v in holm.items():
        rows[k]["final_holm"] = v
    return {
        "declared_hypothesis_cells": 8080,
        "actual_cells_reported": len(rows),
        "supported_final_holm_family_size": len(holm),
        "holm_rejections_fwer_0_05": int(sum(bool(v["reject_fwer_0_05"]) for v in holm.values())),
        "cells": rows,
    }, screened


def _metrics_for_prediction(label: pd.Series, pred: pd.Series, index: pd.DatetimeIndex) -> dict[str, Any]:
    return mdl.binary_metrics(label.reindex(index).to_numpy(dtype=float), pred.reindex(index).to_numpy(dtype=float), pred.reindex(index).to_numpy(dtype=float), include_blocks=True)


def _tune_validation(
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    labels: Mapping[tuple[str, str, int], pd.Series],
    market_indices: Mapping[str, pd.DatetimeIndex],
    screened: Mapping[tuple[str, str, int], Sequence[str]],
) -> tuple[dict, dict, dict, dict, int]:
    configs = mdl.frozen_configurations()
    vidx = _period_index(cells.index, VALID_START, VALID_END)
    selected_params: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    validation_predictions: dict[tuple[str, str, str, int], pd.Series] = {}
    validation_metrics: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    audit: dict[str, Any] = {}
    attempts = 0

    for asset in ee.ASSETS:
        mi = market_indices[asset]
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                lab = labels[(asset, target, h)]
                for arch in mdl.BASE_ARCHITECTURES[:6]:
                    best: tuple | None = None
                    best_params: dict[str, Any] | None = None
                    best_pred: pd.Series | None = None
                    best_metric: dict[str, Any] | None = None
                    for params in configs[arch]:
                        attempts += 1
                        if attempts == 1 or attempts % 25 == 0:
                            print(f"[0066][validation] tuning_attempt={attempts}/1632 asset={asset} target={target} lead={h} arch={arch}", flush=True)
                        pred, pa = _walk_forward_classifier(
                            arch, params, cells, families, signals, lab, mi, h, vidx,
                            selected_signals=screened[(asset, target, h)] if arch == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT" else None,
                        )
                        m = _metrics_for_prediction(lab, pred, vidx)
                        rk = mdl.validation_rank_key(m, params)
                        audit[f"{arch}|{asset}|{target}|L{h}|{mdl.canonical_params(params)}"] = pa
                        if best is None or rk < best:
                            best, best_params, best_pred, best_metric = rk, dict(params), pred, m
                    if best_params is not None and best_pred is not None and best_metric is not None and best_metric.get("status") == "OK":
                        key = (arch, asset, target, h)
                        selected_params[key] = best_params
                        validation_predictions[key] = best_pred
                        validation_metrics[key] = best_metric

            # P07 is one pooled configuration choice per asset/target.
            best7: tuple | None = None
            best7_params: dict[str, Any] | None = None
            best7_preds: dict[int, pd.Series] | None = None
            best7_metrics: dict[int, dict[str, Any]] | None = None
            labels_by_h = {h: labels[(asset, target, h)] for h in ee.WARNING_HORIZONS}
            for params in configs["P07_DISCRETE_TIME_HAZARD_LOGIT"]:
                attempts += 1
                if attempts == 1 or attempts % 25 == 0:
                    print(f"[0066][validation] tuning_attempt={attempts}/1632 asset={asset} target={target} arch=P07_DISCRETE_TIME_HAZARD_LOGIT", flush=True)
                preds, pa = _walk_forward_hazard(params, families, labels_by_h, market_indices[asset], vidx)
                metrics = {h: _metrics_for_prediction(labels_by_h[h], preds[h], vidx) for h in ee.WARNING_HORIZONS}
                ok = [m for m in metrics.values() if m.get("status") == "OK"]
                if ok:
                    aggregate = {
                        "status": "OK",
                        "PR_AUC_LIFT": float(np.mean([m["PR_AUC_LIFT"] for m in ok])),
                        "ROC_AUC": float(np.mean([m["ROC_AUC"] for m in ok])),
                        "Brier": float(np.mean([m["Brier"] for m in ok])),
                    }
                else:
                    aggregate = {"status": "NOT_WELL_DEFINED"}
                rk = mdl.validation_rank_key(aggregate, params)
                audit[f"P07_DISCRETE_TIME_HAZARD_LOGIT|{asset}|{target}|POOLED|{mdl.canonical_params(params)}"] = pa
                if best7 is None or rk < best7:
                    best7, best7_params, best7_preds, best7_metrics = rk, dict(params), preds, metrics
            if best7_params is not None and best7_preds is not None and best7_metrics is not None:
                for h in ee.WARNING_HORIZONS:
                    if best7_metrics[h].get("status") == "OK":
                        key = ("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, h)
                        selected_params[key] = best7_params
                        validation_predictions[key] = best7_preds[h]
                        validation_metrics[key] = best7_metrics[h]

    if attempts != 1632:
        raise RuntimeError(f"validation tuning accounting drift: {attempts}")

    # P08 trackwise nonnegative validation-only stack.
    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                base = {}
                for arch in mdl.BASE_ARCHITECTURES:
                    key = (arch, asset, target, h)
                    if key in validation_predictions:
                        base[arch] = validation_predictions[key].reindex(vidx).to_numpy(dtype=float)
                if not base:
                    continue
                y = labels[(asset, target, h)].reindex(vidx).to_numpy(dtype=float)
                weights = mdl.stack_weights(base, y)
                stack = np.zeros(len(vidx), dtype=float)
                for arch, w in weights.items():
                    stack += float(w) * np.asarray(base[arch], dtype=float)
                p = pd.Series(stack, index=vidx, dtype=float)
                key8 = ("P08_STACKED_PROBABILITY_ENSEMBLE", asset, target, h)
                validation_predictions[key8] = p
                validation_metrics[key8] = _metrics_for_prediction(labels[(asset, target, h)], p, vidx)
                selected_params[key8] = {"stack_weights": weights}

    return selected_params, validation_predictions, validation_metrics, audit, attempts


def _preferred_selections(validation_metrics: Mapping[tuple[str, str, str, int], Mapping[str, Any]]) -> tuple[dict, dict, dict]:
    preferred_horizon: dict[tuple[str, str, str], int] = {}
    preferred_arch: dict[tuple[str, str], str] = {}
    exact_arch: dict[tuple[str, str, int], str] = {}
    for arch in mdl.ARCHITECTURES:
        for asset in ee.ASSETS:
            for target in TARGETS:
                rows = []
                for h in ee.WARNING_HORIZONS:
                    m = validation_metrics.get((arch, asset, target, h))
                    if m and m.get("status") == "OK":
                        rows.append((mdl.validation_rank_key(m, {}), -h, h))
                if rows:
                    rows.sort()
                    preferred_horizon[(arch, asset, target)] = rows[0][2]
    for asset in ee.ASSETS:
        for target in TARGETS:
            choices = []
            for arch in mdl.ARCHITECTURES:
                h = preferred_horizon.get((arch, asset, target))
                if h is None:
                    continue
                m = validation_metrics[(arch, asset, target, h)]
                choices.append((mdl.validation_rank_key(m, {}), arch))
            if choices:
                choices.sort(key=lambda x: (x[0], x[1]))
                preferred_arch[(asset, target)] = choices[0][1]
            for h in ee.WARNING_HORIZONS:
                exact = []
                for arch in mdl.ARCHITECTURES:
                    m = validation_metrics.get((arch, asset, target, h))
                    if m and m.get("status") == "OK":
                        exact.append((mdl.validation_rank_key(m, {}), arch))
                if exact:
                    exact.sort(key=lambda x: (x[0], x[1]))
                    exact_arch[(asset, target, h)] = exact[0][1]
    return preferred_horizon, preferred_arch, exact_arch


def _evaluate_selected_over_economic_period(
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    labels: Mapping[tuple[str, str, int], pd.Series],
    market_indices: Mapping[str, pd.DatetimeIndex],
    screened: Mapping[tuple[str, str, int], Sequence[str]],
    selected_params: Mapping[tuple[str, str, str, int], Mapping[str, Any]],
    validation_predictions: Mapping[tuple[str, str, str, int], pd.Series],
) -> tuple[dict[tuple[str, str, str, int], pd.Series], dict[str, Any]]:
    eidx = _period_index(cells.index, ECON_START, ECON_END)
    out: dict[tuple[str, str, str, int], pd.Series] = {}
    audit: dict[str, Any] = {}
    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                lab = labels[(asset, target, h)]
                for arch in mdl.BASE_ARCHITECTURES[:6]:
                    key = (arch, asset, target, h)
                    params = selected_params.get(key)
                    if params is None:
                        continue
                    p, pa = _walk_forward_classifier(
                        arch, params, cells, families, signals, lab, market_indices[asset], h, eidx,
                        selected_signals=screened[(asset, target, h)] if arch == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT" else None,
                    )
                    out[key] = p
                    audit[_atrack(arch, asset, target, h)] = pa
            p7 = selected_params.get(("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, 1))
            if p7 is None:
                # A valid P07 selection may first appear at another horizon but shares one pooled config.
                for h in ee.WARNING_HORIZONS:
                    p7 = selected_params.get(("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, h))
                    if p7 is not None:
                        break
            if p7 is not None:
                labels_by_h = {h: labels[(asset, target, h)] for h in ee.WARNING_HORIZONS}
                preds, pa = _walk_forward_hazard(p7, families, labels_by_h, market_indices[asset], eidx)
                for h in ee.WARNING_HORIZONS:
                    out[("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, h)] = preds[h]
                audit[f"P07_DISCRETE_TIME_HAZARD_LOGIT|{asset}|{target}|POOLED"] = pa

    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                key8 = ("P08_STACKED_PROBABILITY_ENSEMBLE", asset, target, h)
                params8 = selected_params.get(key8)
                if not params8:
                    continue
                weights = params8["stack_weights"]
                p = np.zeros(len(eidx), dtype=float)
                ok = True
                for arch, w in weights.items():
                    k = (arch, asset, target, h)
                    if k not in out:
                        ok = False
                        break
                    p += float(w) * out[k].reindex(eidx).to_numpy(dtype=float)
                if ok:
                    out[key8] = pd.Series(p, index=eidx, dtype=float)
    return out, audit


def _bootstrap_predictive_lcbs(
    tracks: Mapping[str, tuple[np.ndarray, np.ndarray]],
    *, block_length: int = BOOT_BLOCK, reps: int = BOOT_REPS, seed: int = BOOT_SEED,
) -> tuple[float | None, dict[str, float | None], dict[str, int]]:
    if not tracks:
        return None, {}, {}
    names = list(tracks)
    n = len(next(iter(tracks.values()))[0])
    if n < block_length:
        return None, {k: None for k in names}, {k: 0 for k in names}
    observed: dict[str, float] = {}
    for k, (y, p) in tracks.items():
        mask = np.isfinite(y) & np.isfinite(p)
        if mask.sum() and len(np.unique(y[mask])) >= 2:
            prev = float(np.mean(y[mask]))
            observed[k] = float(average_precision_score(y[mask], p[mask]) - prev)
    if not observed:
        return None, {k: None for k in names}, {k: 0 for k in names}
    rng = np.random.default_rng(seed)
    kk = int(math.ceil(n / block_length))
    max_start = n - block_length
    maxdiff: list[float] = []
    valid_counts = {k: 0 for k in observed}
    for _ in range(reps):
        starts = rng.integers(0, max_start + 1, size=kk)
        ix = np.concatenate([np.arange(s, s + block_length) for s in starts])[:n]
        diffs = []
        for k in observed:
            y, p = tracks[k]
            yy, pp = y[ix], p[ix]
            mask = np.isfinite(yy) & np.isfinite(pp)
            if mask.sum() == 0 or len(np.unique(yy[mask])) < 2:
                continue
            lift = float(average_precision_score(yy[mask], pp[mask]) - np.mean(yy[mask]))
            diffs.append(observed[k] - lift)
            valid_counts[k] += 1
        if diffs:
            maxdiff.append(float(max(diffs)))
    if not maxdiff:
        return None, {k: None for k in names}, valid_counts
    q95 = float(np.quantile(np.asarray(maxdiff), 0.95, method="linear"))
    lcbs = {k: (float(observed[k] - q95) if valid_counts[k] >= int(0.95 * reps) else None) for k in observed}
    return q95, lcbs, valid_counts


def _final_predictor_results(
    labels: Mapping[tuple[str, str, int], pd.Series],
    support: Mapping[tuple[str, str, int], Mapping[str, Any]],
    econ_predictions: Mapping[tuple[str, str, str, int], pd.Series],
    preferred_horizon: Mapping[tuple[str, str, str], int],
    common: pd.DatetimeIndex,
) -> tuple[dict[str, Any], dict[str, Any]]:
    fidx = _period_index(common, FINAL_START, FINAL_END)
    all_track_metrics: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    for key, pred in econ_predictions.items():
        arch, asset, target, h = key
        all_track_metrics[key] = _metrics_for_prediction(labels[(asset, target, h)], pred, fidx)

    preferred: dict[str, Any] = {}
    boot_tracks: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for arch in mdl.ARCHITECTURES:
        for asset in ee.ASSETS:
            for target in TARGETS:
                h = preferred_horizon.get((arch, asset, target))
                k = (arch, asset, target, h) if h is not None else None
                rid = f"{arch}|{asset}|{target}"
                if k is None or k not in all_track_metrics:
                    preferred[rid] = {"status": "MODEL_UNAVAILABLE", "passes_all_predictive_gates": False}
                    continue
                m = all_track_metrics[k]
                sup = dict(support[(asset, target, h)])
                blocks = m.get("chronological_blocks", []) if m.get("status") == "OK" else []
                good_blocks = sum(b.get("status") == "OK" and b.get("ROC_AUC", 0) > 0.5 and b.get("PR_AUC_LIFT", -1) > 0 for b in blocks)
                g2 = m.get("status") == "OK" and float(m.get("ROC_AUC", 0)) > 0.5 and float(m.get("PR_AUC_LIFT", -1)) > 0
                adjacent_ok = False
                for a, b in ((3, 5), (5, 10), (10, 20)):
                    ma = all_track_metrics.get((arch, asset, target, a), {})
                    mb = all_track_metrics.get((arch, asset, target, b), {})
                    if ma.get("status") == "OK" and mb.get("status") == "OK" and ma.get("ROC_AUC", 0) > 0.5 and ma.get("PR_AUC_LIFT", -1) > 0 and mb.get("ROC_AUC", 0) > 0.5 and mb.get("PR_AUC_LIFT", -1) > 0:
                        adjacent_ok = True
                g4 = bool(h >= 5 or adjacent_ok)
                preferred[rid] = {
                    "status": "EVALUATED", "architecture": arch, "asset": asset, "target": target, "preferred_warning_horizon": int(h),
                    "support": sup, "final_metrics": m, "G0_identity": True, "G1_support": bool(sup.get("support_pass")),
                    "G2_auc_and_pr_lift": bool(g2), "G3_temporal_recurrence": bool(good_blocks >= 3), "positive_metric_blocks": int(good_blocks),
                    "G4_early_warning_horizon": g4, "G5_simultaneous_pr_lift_lcb": False, "simultaneous_LCB": None,
                }
                if bool(sup.get("support_pass")) and m.get("status") == "OK":
                    boot_tracks[rid] = (labels[(asset, target, h)].reindex(fidx).to_numpy(dtype=float), econ_predictions[k].reindex(fidx).to_numpy(dtype=float))
    q95, lcbs, valid_counts = _bootstrap_predictive_lcbs(boot_tracks)
    for rid, row in preferred.items():
        if rid in lcbs:
            row["simultaneous_LCB"] = lcbs[rid]
            row["bootstrap_valid_replicates"] = int(valid_counts.get(rid, 0))
            row["G5_simultaneous_pr_lift_lcb"] = bool(lcbs[rid] is not None and lcbs[rid] > 0)
        row["passes_all_predictive_gates"] = bool(row.get("G0_identity") and row.get("G1_support") and row.get("G2_auc_and_pr_lift") and row.get("G3_temporal_recurrence") and row.get("G4_early_warning_horizon") and row.get("G5_simultaneous_pr_lift_lcb"))
    return preferred, {"block_length": BOOT_BLOCK, "replicates": BOOT_REPS, "seed": BOOT_SEED, "q95": q95, "valid_track_count": len(boot_tracks)}


def _cash_net(rf_daily: pd.Series) -> pd.Series:
    return CASH_REALIZATION * _series(rf_daily) - CASH_ANNUAL_FEE / 365.25


def _portfolio_returns(g: pd.Series, base_r: pd.Series, base_gross: pd.Series, cash: pd.Series) -> tuple[pd.Series, dict[str, float]]:
    g = _series(g)
    r = _series(base_r).reindex(g.index)
    gross = _series(base_gross).reindex(g.index)
    c = _series(cash).reindex(g.index)
    arrays = [x.to_numpy(dtype=float) for x in (g, r, gross, c)]
    if not all(np.isfinite(x).all() for x in arrays):
        raise ValueError("nonfinite portfolio input")
    gv, rv, bv, cv = arrays
    cash_fraction = 1.0 - gv * bv
    if np.min(cash_fraction) < -1e-12 or np.min(gv) < -1e-12 or np.max(gv) > 1 + 1e-12:
        raise ValueError("negative cash/leverage/invalid outer multiplier")
    prev = np.concatenate([[1.0], gv[:-1]])
    turnover = np.abs(gv - prev) * bv
    cost = OUTER_COST * turnover
    ret = gv * rv + cash_fraction * cv - cost
    return pd.Series(ret, index=g.index), {
        "average_outer_multiplier": float(np.mean(gv)), "average_total_gross": float(np.mean(gv * bv)),
        "average_cash_fraction": float(np.mean(cash_fraction)), "outer_turnover": float(np.sum(turnover)),
        "outer_transaction_cost_return_units": float(np.sum(cost)),
    }


def _nav(ret: pd.Series, initial: float = 10000.0) -> pd.Series:
    r = ret.to_numpy(dtype=float)
    if not np.isfinite(r).all() or np.any(r <= -1):
        raise ValueError("invalid return path")
    return pd.Series(initial * np.cumprod(1.0 + r), index=ret.index)


def _cagr(nav: pd.Series) -> float:
    if len(nav) < 2:
        return float("nan")
    days = (pd.Timestamp(nav.index[-1]) - pd.Timestamp(nav.index[0])).days
    return float((float(nav.iloc[-1]) / 10000.0) ** (365.25 / days) - 1.0) if days > 0 else float("nan")


def _mdd(nav: pd.Series) -> float:
    a = nav.to_numpy(dtype=float)
    return float(np.min(a / np.maximum.accumulate(a) - 1.0))


def _annualized_sharpe(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    sd = float(np.std(x, ddof=1))
    return float(math.sqrt(365.0) * np.mean(x) / sd) if len(x) > 1 and sd > 0 else float("nan")


def _economic_mbb(relative: Mapping[str, np.ndarray]) -> tuple[float | None, dict[str, float | None]]:
    if not relative:
        return None, {}
    names = list(relative)
    mat = np.column_stack([np.asarray(relative[n], dtype=float) for n in names])
    n = len(mat)
    if n < BOOT_BLOCK or not np.isfinite(mat).all():
        return None, {n: None for n in names}
    obs = mat.mean(axis=0)
    rng = np.random.default_rng(BOOT_SEED)
    k = int(math.ceil(n / BOOT_BLOCK))
    max_start = n - BOOT_BLOCK
    maxdiff = np.empty(BOOT_REPS, dtype=float)
    for b in range(BOOT_REPS):
        starts = rng.integers(0, max_start + 1, size=k)
        ix = np.concatenate([np.arange(s, s + BOOT_BLOCK) for s in starts])[:n]
        boot = mat[ix].mean(axis=0)
        maxdiff[b] = float(np.max(obs - boot))
    q95 = float(np.quantile(maxdiff, 0.95, method="linear"))
    return q95, {name: float(obs[i] - q95) for i, name in enumerate(names)}


def _pbo(controller_returns: Mapping[str, np.ndarray]) -> dict[str, Any]:
    names = list(controller_returns)
    if len(names) < 2:
        return {"status": "NOT_WELL_DEFINED"}
    mat = np.column_stack([np.asarray(controller_returns[n], dtype=float) for n in names])
    blocks = mdl.count_balanced_blocks(len(mat), 8)
    records, overfit = [], 0
    for combo in itertools.combinations(range(8), 4):
        ins = np.concatenate([blocks[i] for i in combo])
        outs = np.concatenate([blocks[i] for i in range(8) if i not in combo])
        sr_in = np.array([_annualized_sharpe(mat[ins, j]) for j in range(len(names))])
        sr_out = np.array([_annualized_sharpe(mat[outs, j]) for j in range(len(names))])
        if not np.isfinite(sr_in).all() or not np.isfinite(sr_out).all():
            continue
        win = int(np.argmax(sr_in))
        ranks = rankdata(sr_out, method="average")
        bad = bool(ranks[win] <= (len(names) + 1.0) / 2.0)
        overfit += int(bad)
        records.append({"in_slices": list(combo), "winner": names[win], "winner_oos_rank": float(ranks[win]), "overfit": bad})
    return {"status": "OK" if records else "NOT_WELL_DEFINED", "split_count": len(records), "pbo": float(overfit / len(records)) if records else None, "records": records}


def _validation_component_percentile(
    architecture: str, asset: str, target: str, h: int,
    validation_predictions: Mapping[tuple[str, str, str, int], pd.Series],
    economic_predictions: Mapping[tuple[str, str, str, int], pd.Series],
    econ_decision_index: pd.DatetimeIndex,
) -> pd.Series:
    key = (architecture, asset, target, h)
    if key not in validation_predictions or key not in economic_predictions:
        raise KeyError(f"component unavailable {key}")
    ref = validation_predictions[key].to_numpy(dtype=float)
    vals = economic_predictions[key].reindex(econ_decision_index).to_numpy(dtype=float)
    return pd.Series(mdl.empirical_percentile(vals, ref), index=econ_decision_index)


def _down_g(percentile: pd.Series) -> pd.Series:
    p = percentile.to_numpy(dtype=float)
    g = np.ones(len(p), dtype=float)
    g[p >= 0.90] = 0.50
    g[p >= 0.975] = 0.25
    return pd.Series(g, index=percentile.index)


def _side_g(percentile: pd.Series) -> pd.Series:
    p = percentile.to_numpy(dtype=float)
    return pd.Series(np.where(p >= 0.90, 0.75, 1.0), index=percentile.index)


def _shift_decision_to_portfolio(g_decision: pd.Series, portfolio_index: pd.DatetimeIndex) -> pd.Series:
    out = pd.Series(1.0, index=portfolio_index, dtype=float)
    for i in range(1, len(portfolio_index)):
        prev_date = portfolio_index[i - 1]
        if prev_date in g_decision.index and np.isfinite(g_decision.loc[prev_date]):
            out.iloc[i] = float(g_decision.loc[prev_date])
        else:
            out.iloc[i] = out.iloc[i - 1]
    return out


def _controller_paths(
    validation_predictions: Mapping[tuple[str, str, str, int], pd.Series],
    economic_predictions: Mapping[tuple[str, str, str, int], pd.Series],
    preferred_horizon: Mapping[tuple[str, str, str], int],
    preferred_arch: Mapping[tuple[str, str], str],
    exact_arch: Mapping[tuple[str, str, int], str],
    portfolio_index: pd.DatetimeIndex,
) -> dict[str, pd.Series]:
    decision_idx = portfolio_index[:-1]
    def comp(asset: str, target: str, h: int, arch: str | None = None) -> pd.Series:
        a = arch or exact_arch[(asset, target, h)]
        return _validation_component_percentile(a, asset, target, h, validation_predictions, economic_predictions, decision_idx)

    p_btc_d5 = comp("BTC", "T1_ANY_DOWN", 5)
    p_sol_d5 = comp("SOL", "T1_ANY_DOWN", 5)
    p_btc_m10 = comp("BTC", "T2_MAJOR_DOWN", 10)
    p_sol_m10 = comp("SOL", "T2_MAJOR_DOWN", 10)
    c: dict[str, pd.Series] = {}
    c["C01_BTC_ANY_DOWN_5D"] = _down_g(p_btc_d5)
    c["C02_SOL_ANY_DOWN_5D"] = _down_g(p_sol_d5)
    c["C03_MAX_BTC_SOL_ANY_DOWN_5D"] = _down_g(pd.concat([p_btc_d5, p_sol_d5], axis=1).max(axis=1))
    c["C04_BTC_MAJOR_DOWN_10D"] = _down_g(p_btc_m10)
    c["C05_MAX_BTC_SOL_MAJOR_DOWN_10D"] = _down_g(pd.concat([p_btc_m10, p_sol_m10], axis=1).max(axis=1))
    mult = [comp(asset, "T1_ANY_DOWN", h) for asset in ee.ASSETS for h in (3, 5, 10)]
    c["C06_MULTILEAD_DOWN_BLEND_3_5_10"] = _down_g(pd.concat(mult, axis=1).max(axis=1))

    down_pref, side_pref = [], []
    for asset in ee.ASSETS:
        for target in ("T1_ANY_DOWN", "T2_MAJOR_DOWN"):
            a = preferred_arch[(asset, target)]
            h = preferred_horizon[(a, asset, target)]
            down_pref.append(comp(asset, target, h, a))
        for target in ("T3_ANY_SIDEWAYS", "T4_LONG_SIDEWAYS"):
            a = preferred_arch[(asset, target)]
            h = preferred_horizon[(a, asset, target)]
            side_pref.append(comp(asset, target, h, a))
    dg = _down_g(pd.concat(down_pref, axis=1).max(axis=1))
    sg = _side_g(pd.concat(side_pref, axis=1).max(axis=1))
    c["C07_DOWN_PLUS_SIDEWAYS"] = pd.Series(np.minimum(dg.to_numpy(), sg.to_numpy()), index=decision_idx)

    p8down, p8side = [], []
    for asset in ee.ASSETS:
        for target in TARGETS:
            h = preferred_horizon[("P08_STACKED_PROBABILITY_ENSEMBLE", asset, target)]
            p = comp(asset, target, h, "P08_STACKED_PROBABILITY_ENSEMBLE")
            (p8down if target in {"T1_ANY_DOWN", "T2_MAJOR_DOWN"} else p8side).append(p)
    d8 = _down_g(pd.concat(p8down, axis=1).max(axis=1))
    s8 = _side_g(pd.concat(p8side, axis=1).max(axis=1))
    c["C08_STACKED_EVENT_RISK"] = pd.Series(np.minimum(d8.to_numpy(), s8.to_numpy()), index=decision_idx)
    return {name: _shift_decision_to_portfolio(c[name], portfolio_index) for name in CONTROLLERS}


def _economic_results(
    controller_g: Mapping[str, pd.Series], baseline_returns: pd.Series, baseline_gross: pd.Series, rf_daily: pd.Series,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    idx = pd.DatetimeIndex(next(iter(controller_g.values())).index)
    base_r = _series(baseline_returns).reindex(idx)
    base_g = _series(baseline_gross).reindex(idx)
    cash = _cash_net(rf_daily).reindex(idx)
    benchmark_g = pd.Series(1.0, index=idx)
    bench_r, bench_extra = _portfolio_returns(benchmark_g, base_r, base_g, cash)
    bench_nav = _nav(bench_r)
    benchmark = {"terminal_wealth": float(bench_nav.iloc[-1]), "calendar_CAGR": _cagr(bench_nav), "max_drawdown": _mdd(bench_nav), **bench_extra}
    results: dict[str, Any] = {}
    rel: dict[str, np.ndarray] = {}
    rets: dict[str, np.ndarray] = {}
    blocks = mdl.count_balanced_blocks(len(idx), 4)
    barr = bench_r.to_numpy(dtype=float)
    for name in CONTROLLERS:
        ret, extra = _portfolio_returns(controller_g[name], base_r, base_g, cash)
        nav = _nav(ret)
        rr = np.log1p(ret.to_numpy(dtype=float)) - np.log1p(barr)
        bsum = [float(np.sum(rr[ix])) for ix in blocks]
        results[name] = {
            "status": "EVALUATED", "terminal_wealth": float(nav.iloc[-1]), "calendar_CAGR": _cagr(nav), "max_drawdown": _mdd(nav),
            **extra, "four_block_relative_log_growth": bsum, "positive_block_count": int(sum(x > 0 for x in bsum)),
            "E0_contract": True, "E1_cagr_and_wealth": bool(float(nav.iloc[-1]) > benchmark["terminal_wealth"] and _cagr(nav) > benchmark["calendar_CAGR"]),
            "E2_drawdown_noninferior": bool(_mdd(nav) >= benchmark["max_drawdown"] - 1e-12), "E3_temporal_recurrence": bool(sum(x > 0 for x in bsum) >= 3),
            "E4_simultaneous_LCB": False, "E5_dependence_cost_timing": True, "simultaneous_LCB": None,
        }
        rel[name] = rr
        rets[name] = ret.to_numpy(dtype=float)
    q95, lcbs = _economic_mbb(rel)
    for name in CONTROLLERS:
        results[name]["simultaneous_LCB"] = lcbs.get(name)
        results[name]["E4_simultaneous_LCB"] = bool(lcbs.get(name) is not None and float(lcbs[name]) > 0)
        results[name]["passes_all_economic_gates"] = bool(all(results[name][k] for k in ("E0_contract", "E1_cagr_and_wealth", "E2_drawdown_noninferior", "E3_temporal_recurrence", "E4_simultaneous_LCB", "E5_dependence_cost_timing")))
    boot = {"block_length": BOOT_BLOCK, "replicates": BOOT_REPS, "seed": BOOT_SEED, "q95": q95}
    return benchmark, results, {"simultaneous_bootstrap": boot, "PBO_CSCV": _pbo(rets)}


def evaluate_program(
    frames: Mapping[str, pd.DataFrame],
    baseline_returns: pd.Series,
    baseline_gross: pd.Series,
    rf_daily: pd.Series,
    *,
    bootstrap_replicates: int = BOOT_REPS,
) -> dict[str, Any]:
    """Single top-level 0066 scientific call. No file I/O, network I/O, signer or order submission."""
    if bootstrap_replicates != BOOT_REPS:
        raise ValueError("historical execution must use frozen 4000 bootstrap replicates")
    print("[0066] phase=feature_build start", flush=True)
    frames = _naive_frames(frames)
    cells, families, meta, signals = _common_feature_objects(frames)
    print("[0066] phase=feature_build done", flush=True)
    print("[0066] phase=event_atlas start", flush=True)
    bundle = ee.build_event_atlas(frames)
    labels, support = _labels_and_support(bundle, cells.index)
    print("[0066] phase=event_atlas done", flush=True)
    print("[0066] phase=indicator_atlas start", flush=True)
    atlas, screened = build_indicator_warning_atlas(signals, meta, labels, support, {a: bundle.asset_indices[a] for a in ee.ASSETS})
    print("[0066] phase=indicator_atlas done", flush=True)
    print("[0066] phase=validation_tuning start declared_attempts=1632", flush=True)
    selected_params, validation_predictions, validation_metrics, tuning_audit, tuning_attempts = _tune_validation(cells, families, signals, labels, {a: bundle.asset_indices[a] for a in ee.ASSETS}, screened)
    print(f"[0066] phase=validation_tuning done actual_attempts={tuning_attempts}", flush=True)
    preferred_horizon, preferred_arch, exact_arch = _preferred_selections(validation_metrics)
    print("[0066] phase=economic_prediction_generation start", flush=True)
    economic_predictions, evaluation_audit = _evaluate_selected_over_economic_period(cells, families, signals, labels, {a: bundle.asset_indices[a] for a in ee.ASSETS}, screened, selected_params, validation_predictions)
    print("[0066] phase=economic_prediction_generation done", flush=True)
    print("[0066] phase=predictive_inference start", flush=True)
    predictor_results, predictor_boot = _final_predictor_results(labels, support, economic_predictions, preferred_horizon, cells.index)
    print("[0066] phase=predictive_inference done", flush=True)

    pidx = _series(baseline_returns).index
    pidx = pidx[(pidx >= ECON_START) & (pidx <= ECON_END)]
    if len(pidx) < 100:
        raise ValueError("economic portfolio support unavailable")
    controller_error = None
    try:
        controller_g = _controller_paths(validation_predictions, economic_predictions, preferred_horizon, preferred_arch, exact_arch, pidx)
        benchmark, controllers, econ_diag = _economic_results(controller_g, baseline_returns, baseline_gross, rf_daily)
    except Exception as exc:
        controller_error = {"error_type": type(exc).__name__, "error_message": str(exc)}
        benchmark = {}
        controllers = {name: {"status": "COMPONENT_UNAVAILABLE", "passes_all_economic_gates": False} for name in CONTROLLERS}
        econ_diag = {"simultaneous_bootstrap": {"block_length": BOOT_BLOCK, "replicates": BOOT_REPS, "seed": BOOT_SEED, "q95": None}, "PBO_CSCV": {"status": "NOT_EVALUATED"}}

    predictive_winners = [k for k, v in predictor_results.items() if v.get("passes_all_predictive_gates")]
    economic_winners = [k for k, v in controllers.items() if v.get("passes_all_economic_gates")]
    any_support = any(bool(v.get("support_pass")) for v in support.values())
    if predictive_winners and economic_winners:
        classification = "PASS_EVENT_EARLY_WARNING_AND_ECONOMIC_CONTROLLER"
    elif predictive_winners and controller_error is not None:
        classification = "PASS_EVENT_EARLY_WARNING_ONLY"
    elif predictive_winners:
        classification = "FAIL_NO_ROBUST_EVENT_CONTROLLER"
    elif any_support:
        classification = "FAIL_NO_ROBUST_EVENT_EARLY_WARNING"
    else:
        classification = "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_EVENT_SUPPORT"

    event_counts: dict[str, int] = {}
    for asset in ee.ASSETS:
        for etype in ("DOWN", "SIDEWAYS"):
            for grade in (list(ee.DOWN_GRADE_RANK) if etype == "DOWN" else list(ee.SIDEWAYS_GRADE_RANK)):
                if bundle.events.empty:
                    n = 0
                else:
                    n = int(((bundle.events["asset"] == asset) & (bundle.events["event_type"] == etype) & (bundle.events["duration_grade"] == grade)).sum())
                event_counts[f"{asset}|{etype}|{grade}"] = n

    primary = {
        "schema_version": 1,
        "research_id": RID,
        "classification": classification,
        "event_onset_count": int(len(bundle.events)),
        "event_counts_by_asset_type_grade": event_counts,
        "indicator_atlas_hypothesis_cells": 8080,
        "indicator_atlas_supported_holm_family_size": int(atlas["supported_final_holm_family_size"]),
        "indicator_atlas_holm_rejections": int(atlas["holm_rejections_fwer_0_05"]),
        "actual_validation_tuning_configs_evaluated": int(tuning_attempts),
        "final_predictor_track_count": 64,
        "final_controller_count": 8,
        "actual_variants_evaluated": 1704,
        "predictor_tracks": predictor_results,
        "predictive_winners": predictive_winners,
        "predictor_simultaneous_bootstrap": predictor_boot,
        "benchmark_0064_same_window": benchmark,
        "controllers": controllers,
        "economic_winners": economic_winners,
        "economic_simultaneous_bootstrap": econ_diag["simultaneous_bootstrap"],
        "PBO_CSCV": econ_diag["PBO_CSCV"],
        "controller_error": controller_error,
        "validation_preferred_horizons": {f"{a}|{asset}|{target}": int(h) for (a, asset, target), h in preferred_horizon.items()},
        "validation_preferred_architectures": {f"{asset}|{target}": a for (asset, target), a in preferred_arch.items()},
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    evidence = {
        "event_atlas": ee.event_records(bundle),
        "support": {_track(a, t, h): dict(v) for (a, t, h), v in support.items()},
        "indicator_warning_atlas": atlas,
        "validation_screened_signals": {_track(a, t, h): list(v) for (a, t, h), v in screened.items()},
        "validation_selected_hyperparameters": {_atrack(a, asset, target, h): dict(v) for (a, asset, target, h), v in selected_params.items()},
        "validation_metrics": {_atrack(a, asset, target, h): dict(v) for (a, asset, target, h), v in validation_metrics.items()},
        "tuning_audit": tuning_audit,
        "evaluation_audit": evaluation_audit,
        "controller_error": controller_error,
    }
    return {"primary_result": primary, "evidence": evidence}
