from __future__ import annotations

import math
import multiprocessing as mp
import os
import warnings
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from research.brrk_btc_sol_path_event_early_warning_0066 import engine as ref

RID = "BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-RUNTIME-QUALIFIED-0067"
WORKERS = 4

ee = ref.ee
mdl = ref.mdl
TARGETS = ref.TARGETS

warnings.filterwarnings("ignore", category=FutureWarning, module=r"sklearn(\..*)?$")

_WORKER_STATE: dict[str, Any] = {}
_BOOT_STATE: dict[str, Any] = {}


def _fork_context() -> mp.context.BaseContext:
    methods = mp.get_all_start_methods()
    if "fork" not in methods:
        raise RuntimeError("0067 pinned ubuntu-24.04 implementation requires fork start method")
    return mp.get_context("fork")


def _classifier_schedule(
    common: pd.DatetimeIndex,
    label: pd.Series,
    market_index: pd.DatetimeIndex,
    horizon: int,
    prediction_index: pd.DatetimeIndex,
) -> dict[pd.Timestamp, pd.DatetimeIndex]:
    out: dict[pd.Timestamp, pd.DatetimeIndex] = {}
    for start in range(0, len(prediction_index), ref.REFIT_CADENCE):
        block = prediction_index[start : start + ref.REFIT_CADENCE]
        if len(block) == 0:
            continue
        refit = pd.Timestamp(block[0])
        train_idx = ref._mature_training_index(common, label, market_index, refit, horizon)
        ytrain = label.reindex(train_idx)
        train_idx = train_idx[ytrain.notna().to_numpy()]
        out[refit] = train_idx
    return out


def _hazard_schedule(
    families_index: pd.DatetimeIndex,
    labels_by_h: Mapping[int, pd.Series],
    market_index: pd.DatetimeIndex,
    prediction_index: pd.DatetimeIndex,
) -> dict[pd.Timestamp, tuple[pd.DatetimeIndex, dict[int, pd.Series]]]:
    pos = {d: i for i, d in enumerate(market_index)}
    out: dict[pd.Timestamp, tuple[pd.DatetimeIndex, dict[int, pd.Series]]] = {}
    for start in range(0, len(prediction_index), ref.REFIT_CADENCE):
        block = prediction_index[start : start + ref.REFIT_CADENCE]
        if len(block) == 0:
            continue
        refit = pd.Timestamp(block[0])
        refit_pos = pos.get(refit)
        if refit_pos is None:
            raise ValueError("hazard refit date absent from market calendar")
        eligible_by_h: dict[int, pd.DatetimeIndex] = {}
        union: list[pd.Timestamp] = []
        for h in ee.WARNING_HORIZONS:
            lab = labels_by_h[h]
            eligible: list[pd.Timestamp] = []
            for d in families_index[families_index < refit]:
                p = pos.get(pd.Timestamp(d))
                if p is not None and p + h + ref.MAX_EVENT_H < refit_pos and np.isfinite(lab.get(d, np.nan)):
                    eligible.append(pd.Timestamp(d))
            eidx = pd.DatetimeIndex(eligible)
            eligible_by_h[h] = eidx
            union.extend(list(eidx))
        train_idx = pd.DatetimeIndex(sorted(set(union)))
        prepared: dict[int, pd.Series] = {}
        for h in ee.WARNING_HORIZONS:
            tmp = pd.Series(np.nan, index=train_idx, dtype=float)
            eidx = eligible_by_h[h]
            if len(eidx):
                common_h = train_idx.intersection(eidx)
                tmp.loc[common_h] = labels_by_h[h].reindex(common_h).to_numpy(dtype=float)
            prepared[h] = tmp
        out[refit] = (train_idx, prepared)
    return out


def _walk_forward_classifier_cached(
    architecture: str,
    params: Mapping[str, Any],
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    label: pd.Series,
    prediction_index: pd.DatetimeIndex,
    schedule: Mapping[pd.Timestamp, pd.DatetimeIndex],
    *,
    selected_signals: Sequence[str] | None = None,
) -> tuple[pd.Series, dict[str, Any]]:
    pred = pd.Series(np.nan, index=prediction_index, dtype=float)
    audit: dict[str, Any] = {"refit_count": 0, "fit_call_attempts": 0, "fit_failures": []}
    for start in range(0, len(prediction_index), ref.REFIT_CADENCE):
        block = prediction_index[start : start + ref.REFIT_CADENCE]
        if len(block) == 0:
            continue
        refit = pd.Timestamp(block[0])
        train_idx = schedule[refit]
        ytrain = label.reindex(train_idx)
        audit["fit_call_attempts"] += 1
        try:
            fitted = mdl.fit_classifier(
                architecture,
                params,
                cells.loc[train_idx],
                families.loc[train_idx],
                signals.loc[train_idx],
                ytrain,
                selected_signals=selected_signals,
            )
            pred.loc[block] = fitted.predict_proba(cells.loc[block], families.loc[block], signals.loc[block])
            audit["refit_count"] += 1
        except Exception as exc:
            audit["fit_failures"].append(
                {"refit": refit.isoformat(), "error_type": type(exc).__name__, "error_message": str(exc)}
            )
    return pred, audit


def _walk_forward_hazard_cached(
    params: Mapping[str, Any],
    families: pd.DataFrame,
    prediction_index: pd.DatetimeIndex,
    schedule: Mapping[pd.Timestamp, tuple[pd.DatetimeIndex, dict[int, pd.Series]]],
) -> tuple[dict[int, pd.Series], dict[str, Any]]:
    preds = {h: pd.Series(np.nan, index=prediction_index, dtype=float) for h in ee.WARNING_HORIZONS}
    audit: dict[str, Any] = {"refit_count": 0, "fit_call_attempts": 0, "fit_failures": []}
    for start in range(0, len(prediction_index), ref.REFIT_CADENCE):
        block = prediction_index[start : start + ref.REFIT_CADENCE]
        if len(block) == 0:
            continue
        refit = pd.Timestamp(block[0])
        train_idx, prepared = schedule[refit]
        audit["fit_call_attempts"] += 1
        try:
            fitted = mdl.fit_hazard(families.loc[train_idx], prepared, params)
            for h in ee.WARNING_HORIZONS:
                preds[h].loc[block] = fitted.predict(families.loc[block], h)
            audit["refit_count"] += 1
        except Exception as exc:
            audit["fit_failures"].append(
                {"refit": refit.isoformat(), "error_type": type(exc).__name__, "error_message": str(exc)}
            )
    return preds, audit


def _validation_worker(task: tuple[Any, ...]) -> tuple[Any, ...]:
    kind = task[0]
    s = _WORKER_STATE
    if kind == "clf":
        _, seq, asset, target, h, arch, params = task
        lab = s["labels"][(asset, target, h)]
        pred, pa = _walk_forward_classifier_cached(
            arch,
            params,
            s["cells"],
            s["families"],
            s["signals"],
            lab,
            s["prediction_index"],
            s["classifier_schedules"][(asset, target, h)],
            selected_signals=s["screened"][(asset, target, h)]
            if arch == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT"
            else None,
        )
        m = ref._metrics_for_prediction(lab, pred, s["prediction_index"])
        rk = mdl.validation_rank_key(m, params)
        return (kind, seq, asset, target, h, arch, dict(params), pred, pa, m, rk)

    if kind == "hazard":
        _, seq, asset, target, params = task
        labels_by_h = {h: s["labels"][(asset, target, h)] for h in ee.WARNING_HORIZONS}
        preds, pa = _walk_forward_hazard_cached(
            params,
            s["families"],
            s["prediction_index"],
            s["hazard_schedules"][(asset, target)],
        )
        metrics = {
            h: ref._metrics_for_prediction(labels_by_h[h], preds[h], s["prediction_index"])
            for h in ee.WARNING_HORIZONS
        }
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
        return (kind, seq, asset, target, dict(params), preds, pa, metrics, rk)
    raise RuntimeError(f"unknown validation task kind {kind}")


def _run_validation_tasks(tasks: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    if not tasks:
        return []
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=_fork_context()) as pool:
        return list(pool.map(_validation_worker, tasks, chunksize=1))


def _tune_validation_parallel(
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    labels: Mapping[tuple[str, str, int], pd.Series],
    market_indices: Mapping[str, pd.DatetimeIndex],
    screened: Mapping[tuple[str, str, int], Sequence[str]],
) -> tuple[dict, dict, dict, dict, int]:
    configs = mdl.frozen_configurations()
    vidx = ref._period_index(cells.index, ref.VALID_START, ref.VALID_END)
    classifier_schedules: dict[tuple[str, str, int], dict[pd.Timestamp, pd.DatetimeIndex]] = {}
    hazard_schedules: dict[tuple[str, str], dict[pd.Timestamp, tuple[pd.DatetimeIndex, dict[int, pd.Series]]]] = {}
    for asset in ee.ASSETS:
        for target in TARGETS:
            labels_by_h = {h: labels[(asset, target, h)] for h in ee.WARNING_HORIZONS}
            for h in ee.WARNING_HORIZONS:
                classifier_schedules[(asset, target, h)] = _classifier_schedule(
                    cells.index,
                    labels[(asset, target, h)],
                    market_indices[asset],
                    h,
                    vidx,
                )
            hazard_schedules[(asset, target)] = _hazard_schedule(
                families.index, labels_by_h, market_indices[asset], vidx
            )

    tasks: list[tuple[Any, ...]] = []
    seq = 0
    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                for arch in mdl.BASE_ARCHITECTURES[:6]:
                    for params in configs[arch]:
                        seq += 1
                        tasks.append(("clf", seq, asset, target, h, arch, dict(params)))
            for params in configs["P07_DISCRETE_TIME_HAZARD_LOGIT"]:
                seq += 1
                tasks.append(("hazard", seq, asset, target, dict(params)))
    if seq != 1632:
        raise RuntimeError(f"validation tuning task accounting drift: {seq}")

    global _WORKER_STATE
    _WORKER_STATE = {
        "cells": cells,
        "families": families,
        "signals": signals,
        "labels": labels,
        "screened": screened,
        "prediction_index": vidx,
        "classifier_schedules": classifier_schedules,
        "hazard_schedules": hazard_schedules,
    }
    results = _run_validation_tasks(tasks)
    _WORKER_STATE = {}

    selected_params: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    validation_predictions: dict[tuple[str, str, str, int], pd.Series] = {}
    validation_metrics: dict[tuple[str, str, str, int], dict[str, Any]] = {}
    audit: dict[str, Any] = {}
    best_clf: dict[tuple[str, str, str, int], tuple[Any, dict[str, Any], pd.Series, dict[str, Any]]] = {}
    best_hazard: dict[tuple[str, str], tuple[Any, dict[str, Any], dict[int, pd.Series], dict[int, dict[str, Any]]]] = {}

    attempts = 0
    for row in results:
        attempts += 1
        if attempts == 1 or attempts % 25 == 0:
            print(f"[0067][validation] completed_task={attempts}/1632", flush=True)
        if row[0] == "clf":
            _, _, asset, target, h, arch, params, pred, pa, m, rk = row
            audit[f"{arch}|{asset}|{target}|L{h}|{mdl.canonical_params(params)}"] = pa
            key = (arch, asset, target, h)
            old = best_clf.get(key)
            if old is None or rk < old[0]:
                best_clf[key] = (rk, params, pred, m)
        else:
            _, _, asset, target, params, preds, pa, metrics, rk = row
            audit[
                f"P07_DISCRETE_TIME_HAZARD_LOGIT|{asset}|{target}|POOLED|{mdl.canonical_params(params)}"
            ] = pa
            key7 = (asset, target)
            old7 = best_hazard.get(key7)
            if old7 is None or rk < old7[0]:
                best_hazard[key7] = (rk, params, preds, metrics)

    if attempts != 1632:
        raise RuntimeError(f"validation tuning accounting drift: {attempts}")

    for key, (_, params, pred, metric) in best_clf.items():
        if metric.get("status") == "OK":
            selected_params[key] = dict(params)
            validation_predictions[key] = pred
            validation_metrics[key] = metric

    for (asset, target), (_, params, preds, metrics) in best_hazard.items():
        for h in ee.WARNING_HORIZONS:
            if metrics[h].get("status") == "OK":
                key = ("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, h)
                selected_params[key] = dict(params)
                validation_predictions[key] = preds[h]
                validation_metrics[key] = metrics[h]

    nnls_solves = 0
    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                base: dict[str, np.ndarray] = {}
                for arch in mdl.BASE_ARCHITECTURES:
                    key = (arch, asset, target, h)
                    if key in validation_predictions:
                        base[arch] = validation_predictions[key].reindex(vidx).to_numpy(dtype=float)
                if not base:
                    continue
                y = labels[(asset, target, h)].reindex(vidx).to_numpy(dtype=float)
                weights = mdl.stack_weights(base, y)
                nnls_solves += 1
                stack = np.zeros(len(vidx), dtype=float)
                for arch, w in weights.items():
                    stack += float(w) * np.asarray(base[arch], dtype=float)
                p = pd.Series(stack, index=vidx, dtype=float)
                key8 = ("P08_STACKED_PROBABILITY_ENSEMBLE", asset, target, h)
                validation_predictions[key8] = p
                validation_metrics[key8] = ref._metrics_for_prediction(labels[(asset, target, h)], p, vidx)
                selected_params[key8] = {"stack_weights": weights}

    audit["__runtime__"] = {
        "fit_call_attempts": int(
            sum(int(v.get("fit_call_attempts", 0)) for k, v in audit.items() if k != "__runtime__")
        ),
        "nnls_solves": int(nnls_solves),
        "worker_count": WORKERS,
    }
    return selected_params, validation_predictions, validation_metrics, audit, attempts


def _economic_worker(task: tuple[Any, ...]) -> tuple[Any, ...]:
    kind = task[0]
    s = _WORKER_STATE
    if kind == "clf":
        _, seq, asset, target, h, arch, params = task
        lab = s["labels"][(asset, target, h)]
        p, pa = _walk_forward_classifier_cached(
            arch,
            params,
            s["cells"],
            s["families"],
            s["signals"],
            lab,
            s["prediction_index"],
            s["classifier_schedules"][(asset, target, h)],
            selected_signals=s["screened"][(asset, target, h)]
            if arch == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT"
            else None,
        )
        return (kind, seq, asset, target, h, arch, p, pa)
    if kind == "hazard":
        _, seq, asset, target, params = task
        preds, pa = _walk_forward_hazard_cached(
            params,
            s["families"],
            s["prediction_index"],
            s["hazard_schedules"][(asset, target)],
        )
        return (kind, seq, asset, target, preds, pa)
    raise RuntimeError(f"unknown economic task kind {kind}")


def _evaluate_selected_parallel(
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    labels: Mapping[tuple[str, str, int], pd.Series],
    market_indices: Mapping[str, pd.DatetimeIndex],
    screened: Mapping[tuple[str, str, int], Sequence[str]],
    selected_params: Mapping[tuple[str, str, str, int], Mapping[str, Any]],
    validation_predictions: Mapping[tuple[str, str, str, int], pd.Series],
) -> tuple[dict[tuple[str, str, str, int], pd.Series], dict[str, Any]]:
    eidx = ref._period_index(cells.index, ref.ECON_START, ref.ECON_END)
    classifier_schedules: dict[tuple[str, str, int], dict[pd.Timestamp, pd.DatetimeIndex]] = {}
    hazard_schedules: dict[tuple[str, str], dict[pd.Timestamp, tuple[pd.DatetimeIndex, dict[int, pd.Series]]]] = {}
    for asset in ee.ASSETS:
        for target in TARGETS:
            labels_by_h = {h: labels[(asset, target, h)] for h in ee.WARNING_HORIZONS}
            for h in ee.WARNING_HORIZONS:
                classifier_schedules[(asset, target, h)] = _classifier_schedule(
                    cells.index,
                    labels[(asset, target, h)],
                    market_indices[asset],
                    h,
                    eidx,
                )
            hazard_schedules[(asset, target)] = _hazard_schedule(
                families.index, labels_by_h, market_indices[asset], eidx
            )

    tasks: list[tuple[Any, ...]] = []
    seq = 0
    for asset in ee.ASSETS:
        for target in TARGETS:
            for h in ee.WARNING_HORIZONS:
                for arch in mdl.BASE_ARCHITECTURES[:6]:
                    key = (arch, asset, target, h)
                    params = selected_params.get(key)
                    if params is None:
                        continue
                    seq += 1
                    tasks.append(("clf", seq, asset, target, h, arch, dict(params)))
            p7 = selected_params.get(("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, 1))
            if p7 is None:
                for h in ee.WARNING_HORIZONS:
                    p7 = selected_params.get(("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, h))
                    if p7 is not None:
                        break
            if p7 is not None:
                seq += 1
                tasks.append(("hazard", seq, asset, target, dict(p7)))

    global _WORKER_STATE
    _WORKER_STATE = {
        "cells": cells,
        "families": families,
        "signals": signals,
        "labels": labels,
        "screened": screened,
        "prediction_index": eidx,
        "classifier_schedules": classifier_schedules,
        "hazard_schedules": hazard_schedules,
    }
    if tasks:
        with ProcessPoolExecutor(max_workers=WORKERS, mp_context=_fork_context()) as pool:
            results = list(pool.map(_economic_worker, tasks, chunksize=1))
    else:
        results = []
    _WORKER_STATE = {}

    out: dict[tuple[str, str, str, int], pd.Series] = {}
    audit: dict[str, Any] = {}
    for row in results:
        if row[0] == "clf":
            _, _, asset, target, h, arch, p, pa = row
            out[(arch, asset, target, h)] = p
            audit[ref._atrack(arch, asset, target, h)] = pa
        else:
            _, _, asset, target, preds, pa = row
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

    audit["__runtime__"] = {
        "fit_call_attempts": int(
            sum(int(v.get("fit_call_attempts", 0)) for k, v in audit.items() if k != "__runtime__")
        ),
        "worker_count": WORKERS,
    }
    return out, audit


def _predictive_boot_worker(span: tuple[int, int]) -> tuple[int, list[float | None], dict[str, int]]:
    start, end = span
    s = _BOOT_STATE
    names: list[str] = s["names"]
    observed: dict[str, float] = s["observed"]
    tracks: Mapping[str, tuple[np.ndarray, np.ndarray]] = s["tracks"]
    starts_matrix: np.ndarray = s["starts_matrix"]
    block_length: int = s["block_length"]
    n: int = s["n"]
    vals: list[float | None] = []
    counts = {k: 0 for k in observed}
    offsets = np.arange(block_length, dtype=np.int64)
    for b in range(start, end):
        starts = starts_matrix[b]
        ix = (starts[:, None] + offsets[None, :]).reshape(-1)[:n]
        diffs: list[float] = []
        for k in names:
            if k not in observed:
                continue
            y, p = tracks[k]
            yy, pp = y[ix], p[ix]
            mask = np.isfinite(yy) & np.isfinite(pp)
            if mask.sum() == 0 or len(np.unique(yy[mask])) < 2:
                continue
            lift = float(average_precision_score(yy[mask], pp[mask]) - np.mean(yy[mask]))
            diffs.append(observed[k] - lift)
            counts[k] += 1
        vals.append(float(max(diffs)) if diffs else None)
    return start, vals, counts


def _bootstrap_predictive_parallel(
    tracks: Mapping[str, tuple[np.ndarray, np.ndarray]],
    *,
    block_length: int = ref.BOOT_BLOCK,
    reps: int = ref.BOOT_REPS,
    seed: int = ref.BOOT_SEED,
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
    starts_matrix = np.empty((reps, kk), dtype=np.int64)
    for b in range(reps):
        starts_matrix[b] = rng.integers(0, max_start + 1, size=kk)

    batch = int(math.ceil(reps / (WORKERS * 4)))
    spans = [(a, min(a + batch, reps)) for a in range(0, reps, batch)]
    global _BOOT_STATE
    _BOOT_STATE = {
        "names": names,
        "observed": observed,
        "tracks": tracks,
        "starts_matrix": starts_matrix,
        "block_length": block_length,
        "n": n,
    }
    with ProcessPoolExecutor(max_workers=WORKERS, mp_context=_fork_context()) as pool:
        parts = list(pool.map(_predictive_boot_worker, spans, chunksize=1))
    _BOOT_STATE = {}

    maxdiff: list[float] = []
    valid_counts = {k: 0 for k in observed}
    for _, vals, counts in sorted(parts, key=lambda x: x[0]):
        maxdiff.extend(float(v) for v in vals if v is not None)
        for k, c in counts.items():
            valid_counts[k] += int(c)
    if not maxdiff:
        return None, {k: None for k in names}, valid_counts
    q95 = float(np.quantile(np.asarray(maxdiff), 0.95, method="linear"))
    lcbs = {
        k: (float(observed[k] - q95) if valid_counts[k] >= int(0.95 * reps) else None)
        for k in observed
    }
    return q95, lcbs, valid_counts


def _economic_mbb_vectorized(
    relative: Mapping[str, np.ndarray],
) -> tuple[float | None, dict[str, float | None]]:
    if not relative:
        return None, {}
    names = list(relative)
    mat = np.column_stack([np.asarray(relative[n], dtype=float) for n in names])
    n = len(mat)
    if n < ref.BOOT_BLOCK or not np.isfinite(mat).all():
        return None, {name: None for name in names}
    obs = mat.mean(axis=0)
    rng = np.random.default_rng(ref.BOOT_SEED)
    k = int(math.ceil(n / ref.BOOT_BLOCK))
    max_start = n - ref.BOOT_BLOCK
    starts = np.empty((ref.BOOT_REPS, k), dtype=np.int64)
    for b in range(ref.BOOT_REPS):
        starts[b] = rng.integers(0, max_start + 1, size=k)
    offsets = np.arange(ref.BOOT_BLOCK, dtype=np.int64)
    maxdiff = np.empty(ref.BOOT_REPS, dtype=float)
    chunk = 200
    for a in range(0, ref.BOOT_REPS, chunk):
        z = min(a + chunk, ref.BOOT_REPS)
        ix = (starts[a:z, :, None] + offsets[None, None, :]).reshape(z - a, -1)[:, :n]
        boot = mat[ix].mean(axis=1)
        maxdiff[a:z] = np.max(obs[None, :] - boot, axis=1)
    q95 = float(np.quantile(maxdiff, 0.95, method="linear"))
    return q95, {name: float(obs[i] - q95) for i, name in enumerate(names)}


def _runtime_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    ta = evidence.get("tuning_audit", {})
    ea = evidence.get("evaluation_audit", {})
    vt = int(ta.get("__runtime__", {}).get("fit_call_attempts", 0))
    et = int(ea.get("__runtime__", {}).get("fit_call_attempts", 0))
    nnls = int(ta.get("__runtime__", {}).get("nnls_solves", 0))
    return {
        "worker_count": WORKERS,
        "validation_fit_call_attempts": vt,
        "economic_fit_call_attempts": et,
        "total_fit_call_attempts": vt + et,
        "stacking_nnls_solves": nnls,
    }


def evaluate_program(
    frames: Mapping[str, pd.DataFrame],
    baseline_returns: pd.Series,
    baseline_gross: pd.Series,
    rf_daily: pd.Series,
    *,
    bootstrap_replicates: int = ref.BOOT_REPS,
) -> dict[str, Any]:
    """Single scientific call using frozen 0066 semantics with deterministic runtime optimization.

    No file/network/signer/order I/O occurs here. Historical authorization belongs to a later
    controlled runner. Scientific seed, grids, labels, selection, controllers and inference are
    inherited unchanged from the frozen 0066 semantics.
    """
    if WORKERS != 4:
        raise RuntimeError("0067 worker-count drift")
    if bootstrap_replicates != 4000:
        raise ValueError("historical execution must use frozen 4000 bootstrap replicates")

    old_rid = ref.RID
    old_tune = ref._tune_validation
    old_eval = ref._evaluate_selected_over_economic_period
    old_pred_boot = ref._bootstrap_predictive_lcbs
    old_econ_boot = ref._economic_mbb
    ref.RID = RID
    ref._tune_validation = _tune_validation_parallel
    ref._evaluate_selected_over_economic_period = _evaluate_selected_parallel
    ref._bootstrap_predictive_lcbs = _bootstrap_predictive_parallel
    ref._economic_mbb = _economic_mbb_vectorized
    try:
        print("[0067] optimized scientific call start workers=4", flush=True)
        out = ref.evaluate_program(
            frames,
            baseline_returns,
            baseline_gross,
            rf_daily,
            bootstrap_replicates=bootstrap_replicates,
        )
        out["primary_result"]["research_id"] = RID
        out["evidence"]["0067_runtime_accounting"] = _runtime_summary(out["evidence"])
        print("[0067] optimized scientific call complete", flush=True)
        return out
    finally:
        ref.RID = old_rid
        ref._tune_validation = old_tune
        ref._evaluate_selected_over_economic_period = old_eval
        ref._bootstrap_predictive_lcbs = old_pred_boot
        ref._economic_mbb = old_econ_boot


__all__ = [
    "RID",
    "WORKERS",
    "evaluate_program",
    "_tune_validation_parallel",
    "_evaluate_selected_parallel",
    "_bootstrap_predictive_parallel",
    "_economic_mbb_vectorized",
]
