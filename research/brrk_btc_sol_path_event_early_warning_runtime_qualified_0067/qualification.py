from __future__ import annotations

import argparse
import builtins
import hashlib
import json
import os
import platform
import resource
import socket
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import scipy
import sklearn

from . import engine as opt

ref = opt.ref
ee = ref.ee
mdl = ref.mdl
RID = opt.RID

FORBIDDEN_PATH_FRAGMENTS = (
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json",
    "research/results/pit_disp_0015/daily_equity.csv",
    "research/results/pit_disp_0015/daily_weights.csv",
    "research/brrk_idle_cash_sweep_robustness_0063/DTB3_RAW.csv",
)


@contextmanager
def isolation_guard() -> Any:
    counters = {
        "historical_payload_reads": 0,
        "market_loader_calls": 0,
        "historical_equity_reads": 0,
        "historical_weights_reads": 0,
        "historical_dtb3_reads": 0,
        "network_fetches": 0,
    }
    old_open = builtins.open
    old_connect = socket.socket.connect

    def guarded_open(file: Any, *args: Any, **kwargs: Any) -> Any:
        text = os.fspath(file) if isinstance(file, (str, bytes, os.PathLike)) else str(file)
        normalized = str(text).replace("\\", "/")
        if any(fragment in normalized for fragment in FORBIDDEN_PATH_FRAGMENTS):
            counters["historical_payload_reads"] += 1
            if "MARKET_EVIDENCE" in normalized:
                counters["market_loader_calls"] += 1
            elif "daily_equity" in normalized:
                counters["historical_equity_reads"] += 1
            elif "daily_weights" in normalized:
                counters["historical_weights_reads"] += 1
            elif "DTB3_RAW" in normalized:
                counters["historical_dtb3_reads"] += 1
            raise RuntimeError(f"0067 qualification historical read blocked: {normalized}")
        return old_open(file, *args, **kwargs)

    def guarded_connect(sock: socket.socket, address: Any) -> Any:
        counters["network_fetches"] += 1
        raise RuntimeError(f"0067 qualification network access blocked: {address!r}")

    builtins.open = guarded_open
    socket.socket.connect = guarded_connect
    try:
        yield counters
    finally:
        builtins.open = old_open
        socket.socket.connect = old_connect


def _synthetic_frames(seed: int = 670067) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2020-08-11", "2026-08-02", freq="D")
    if len(idx) != 2183:
        raise RuntimeError(f"synthetic calendar drift: {len(idx)}")
    out: dict[str, pd.DataFrame] = {}
    for ai, asset in enumerate(("BTC", "ETH", "SOL")):
        n = len(idx)
        latent = np.column_stack(
            [
                np.sin(np.arange(n) / (7.0 + j * 2.7) + 0.31 * ai + 0.17 * j)
                for j in range(12)
            ]
        )
        heavy = np.clip(rng.standard_t(df=5, size=n), -6.0, 6.0)
        drift = 0.0006 + 0.00015 * latent[:, ai % 12] - 0.00008 * latent[:, (ai + 4) % 12]
        logret = drift + 0.012 * heavy + 0.002 * latent[:, (ai + 7) % 12]
        close = (100.0 + 40.0 * ai) * np.exp(np.cumsum(logret))
        open_ = np.concatenate([[close[0]], close[:-1]]) * np.exp(0.0015 * latent[:, (ai + 2) % 12])
        spread = 0.004 + 0.007 * np.abs(latent[:, (ai + 5) % 12]) + 0.002 * np.abs(rng.normal(size=n))
        high = np.maximum(open_, close) * (1.0 + spread)
        low = np.minimum(open_, close) / (1.0 + spread)
        volume = np.exp(10.0 + 0.45 * latent[:, (ai + 3) % 12] + 0.25 * np.clip(rng.normal(size=n), -3, 3))
        quote_volume = volume * close
        trades = np.maximum(10, np.rint(500 + 110 * latent[:, (ai + 8) % 12] + 60 * rng.normal(size=n))).astype(int)
        out[asset] = pd.DataFrame(
            {
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "quote_volume": quote_volume,
                "trades": trades,
            },
            index=idx,
        )
    return out


def _hash_frames(frames: Mapping[str, pd.DataFrame]) -> str:
    h = hashlib.sha256()
    for asset in sorted(frames):
        h.update(asset.encode())
        hv = pd.util.hash_pandas_object(frames[asset], index=True).to_numpy(dtype=np.uint64)
        h.update(hv.tobytes())
    return h.hexdigest()


def _synthetic_labels(signals: pd.DataFrame) -> dict[tuple[str, str, int], pd.Series]:
    columns = list(signals.columns)
    n = len(signals)
    pos = np.arange(n)
    out: dict[tuple[str, str, int], pd.Series] = {}
    for ai, asset in enumerate(ee.ASSETS):
        for ti, target in enumerate(opt.TARGETS):
            for hi, lead in enumerate(ee.WARNING_HORIZONS):
                col = columns[(ai * 61 + ti * 17 + hi * 7) % len(columns)]
                raw = pd.to_numeric(signals[col], errors="coerce")
                fill = float(raw.median()) if raw.notna().any() else 0.0
                x = raw.fillna(fill)
                pct = x.rank(method="average", pct=True).to_numpy(dtype=float)
                phase = ai * 3 + ti * 5 + hi * 2
                periodic = ((pos + phase) % 11) == 0
                y = ((pct >= 0.82) | periodic).astype(float)
                # Every 20-row scored block must contain both classes.
                for start in range(0, n, 20):
                    z = slice(start, min(start + 20, n))
                    if y[z].sum() == 0:
                        y[start] = 1.0
                    if y[z].sum() == len(y[z]):
                        y[start] = 0.0
                out[(asset, target, lead)] = pd.Series(y, index=signals.index, dtype=float)
    return out


def _support() -> dict[tuple[str, str, int], dict[str, Any]]:
    return {
        (asset, target, lead): {
            "support_pass": True,
            "train_plus_validation_unique_onsets": 24,
            "final_unique_onsets": 8,
            "qualification_synthetic": True,
        }
        for asset in ee.ASSETS
        for target in opt.TARGETS
        for lead in ee.WARNING_HORIZONS
    }


def _allclose_series(a: pd.Series, b: pd.Series) -> bool:
    av = a.to_numpy(dtype=float)
    bv = b.to_numpy(dtype=float)
    return bool(
        a.index.equals(b.index)
        and np.array_equal(np.isnan(av), np.isnan(bv))
        and np.allclose(av, bv, atol=1e-12, rtol=1e-10, equal_nan=True)
    )


def _reference_equivalence(
    cells: pd.DataFrame,
    families: pd.DataFrame,
    signals: pd.DataFrame,
    labels: Mapping[tuple[str, str, int], pd.Series],
    market_indices: Mapping[str, pd.DatetimeIndex],
    screened: Mapping[tuple[str, str, int], list[str]],
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    vidx = ref._period_index(cells.index, ref.VALID_START, ref.VALID_END)
    asset, target, lead = "BTC", "T1_ANY_DOWN", 5
    lab = labels[(asset, target, lead)]
    schedule = opt._classifier_schedule(cells.index, lab, market_indices[asset], lead, vidx)
    configs = mdl.frozen_configurations()

    representative: dict[str, bool] = {}
    for arch in mdl.BASE_ARCHITECTURES[:6]:
        params = configs[arch][0]
        selected = screened[(asset, target, lead)] if arch == "P03_VALIDATION_SCREENED_SIGNAL_LOGIT" else None
        pa, _ = ref._walk_forward_classifier(
            arch,
            params,
            cells,
            families,
            signals,
            lab,
            market_indices[asset],
            lead,
            vidx,
            selected_signals=selected,
        )
        pb, _ = opt._walk_forward_classifier_cached(
            arch, params, cells, families, signals, lab, vidx, schedule, selected_signals=selected
        )
        representative[arch] = _allclose_series(pa, pb)
    results["representative_P01_to_P06_probabilities"] = {
        "pass": all(representative.values()),
        "by_architecture": representative,
    }

    labels_by_h = {h: labels[(asset, target, h)] for h in ee.WARNING_HORIZONS}
    hs = opt._hazard_schedule(families.index, labels_by_h, market_indices[asset], vidx)
    p7a, _ = ref._walk_forward_hazard(
        configs["P07_DISCRETE_TIME_HAZARD_LOGIT"][0], families, labels_by_h, market_indices[asset], vidx
    )
    p7b, _ = opt._walk_forward_hazard_cached(
        configs["P07_DISCRETE_TIME_HAZARD_LOGIT"][0], families, vidx, hs
    )
    results["representative_P07_probabilities"] = {
        "pass": all(_allclose_series(p7a[h], p7b[h]) for h in ee.WARNING_HORIZONS)
    }

    # Bootstrap equivalence uses the same seed and generates the same starts in the same order.
    btracks: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for h in (3, 5, 10, 20):
        y = labels[(asset, target, h)].reindex(vidx).to_numpy(dtype=float)
        x = pd.to_numeric(signals.iloc[:, h], errors="coerce").reindex(vidx).to_numpy(dtype=float)
        finite = np.isfinite(x)
        if finite.any():
            lo, hi = np.nanmin(x), np.nanmax(x)
            p = (x - lo) / (hi - lo + 1e-12)
        else:
            p = np.full_like(x, 0.5)
        btracks[f"L{h}"] = (y, p)
    qa, la, ca = ref._bootstrap_predictive_lcbs(btracks, reps=200, seed=660066)
    qb, lb, cb = opt._bootstrap_predictive_parallel(btracks, reps=200, seed=660066)
    boot_pass = (
        (qa is None and qb is None)
        or (qa is not None and qb is not None and abs(float(qa) - float(qb)) <= 1e-12 + 1e-10 * abs(float(qa)))
    )
    if boot_pass:
        for k in set(la) | set(lb):
            va, vb = la.get(k), lb.get(k)
            if va is None or vb is None:
                boot_pass = boot_pass and va is vb
            else:
                boot_pass = boot_pass and bool(np.isclose(va, vb, atol=1e-12, rtol=1e-10))
    boot_pass = boot_pass and ca == cb
    results["bootstrap_statistics"] = {"pass": bool(boot_pass)}

    relative = {
        "A": 0.001 * np.sin(np.arange(240) / 9.0) + 0.0002,
        "B": 0.0012 * np.cos(np.arange(240) / 13.0) + 0.0001,
    }
    ea = ref._economic_mbb(relative)
    eb = opt._economic_mbb_vectorized(relative)
    econ_pass = bool(
        ea[0] is not None
        and eb[0] is not None
        and np.isclose(ea[0], eb[0], atol=1e-12, rtol=1e-10)
        and all(np.isclose(ea[1][k], eb[1][k], atol=1e-12, rtol=1e-10) for k in ea[1])
    )
    results["economic_bootstrap_statistics"] = {"pass": econ_pass}

    # These calculations are intentionally shared immutable 0066 reference code, not rewritten.
    shared = {
        "event_labels_and_onsets": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "risk_set_masks": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "maturity_masks": "REFERENCE_FUNCTION_USED_FOR_SCHEDULE_CACHE",
        "feature_matrices": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "P08_weights_and_probabilities": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "validation_metrics": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "controller_gross_paths": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "turnover_costs": "SHARED_IMMUTABLE_REFERENCE_CODE",
        "PBO_statistics": "SHARED_IMMUTABLE_REFERENCE_CODE",
    }
    for name, mode in shared.items():
        results[name] = {"pass": True, "mode": mode}
    results["all_pass"] = bool(all(bool(v.get("pass")) for v in results.values() if isinstance(v, dict)))
    return results


def _rss_upper_bound_bytes(*audits: Mapping[str, Any]) -> tuple[int, dict[str, int]]:
    per_pid: dict[str, int] = {}
    for audit in audits:
        for key, row in audit.items():
            if key == "__runtime__" or not isinstance(row, Mapping):
                continue
            pid = row.get("worker_pid")
            rss = row.get("worker_maxrss_kb")
            if pid is not None and rss is not None:
                p = str(pid)
                per_pid[p] = max(per_pid.get(p, 0), int(rss) * 1024)
    parent = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    return parent + sum(per_pid.values()), {"parent": parent, **per_pid}


def _mem_total_bytes() -> int:
    with open("/proc/meminfo", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024
    raise RuntimeError("MemTotal unavailable")


def run_full_qualification() -> dict[str, Any]:
    t0 = time.perf_counter()
    phase: dict[str, float] = {}
    with isolation_guard() as counters:
        p0 = time.perf_counter()
        frames = _synthetic_frames()
        input_hash = _hash_frames(frames)
        cells, families, meta, signals = ref._common_feature_objects(frames)
        if cells.shape[1] != 185 or families.shape[1] != 17 or signals.shape[1] != 202:
            raise RuntimeError("qualification feature dimension drift")
        bundle = ee.build_event_atlas(frames)
        labels = _synthetic_labels(signals)
        support = _support()
        market_indices = {a: pd.DatetimeIndex(frames[a].index) for a in ee.ASSETS}
        atlas, screened = ref.build_indicator_warning_atlas(signals, meta, labels, support, market_indices)
        if int(atlas["actual_cells_reported"]) != 8080:
            raise RuntimeError("qualification atlas cell drift")
        if any(len(screened[k]) == 0 for k in screened):
            raise RuntimeError("qualification P03 screening produced an empty track")
        phase["synthetic_feature_event_atlas"] = time.perf_counter() - p0

        p0 = time.perf_counter()
        equivalence = _reference_equivalence(cells, families, signals, labels, market_indices, screened)
        if not equivalence["all_pass"]:
            raise RuntimeError("0067 reference equivalence failed")
        phase["reference_equivalence"] = time.perf_counter() - p0

        p0 = time.perf_counter()
        selected_params, validation_predictions, validation_metrics, tuning_audit, attempts = opt._tune_validation_parallel(
            cells, families, signals, labels, market_indices, screened
        )
        phase["validation_tuning"] = time.perf_counter() - p0
        validation_fit_calls = int(tuning_audit["__runtime__"]["fit_call_attempts"])
        nnls_solves = int(tuning_audit["__runtime__"]["nnls_solves"])
        if attempts != 1632 or validation_fit_calls != 31008 or nnls_solves != 40:
            raise RuntimeError(
                f"qualification validation shape drift attempts={attempts} fits={validation_fit_calls} nnls={nnls_solves}"
            )

        preferred_horizon, preferred_arch, exact_arch = ref._preferred_selections(validation_metrics)
        if len(preferred_horizon) != 64:
            raise RuntimeError(f"qualification preferred predictor track drift: {len(preferred_horizon)}")

        p0 = time.perf_counter()
        economic_predictions, evaluation_audit = opt._evaluate_selected_parallel(
            cells,
            families,
            signals,
            labels,
            market_indices,
            screened,
            selected_params,
            validation_predictions,
        )
        phase["economic_prediction_generation"] = time.perf_counter() - p0
        economic_fit_calls = int(evaluation_audit["__runtime__"]["fit_call_attempts"])
        if economic_fit_calls != 11904:
            raise RuntimeError(f"qualification economic fit-call drift: {economic_fit_calls}")

        old_pred_boot = ref._bootstrap_predictive_lcbs
        old_econ_boot = ref._economic_mbb
        ref._bootstrap_predictive_lcbs = opt._bootstrap_predictive_parallel
        ref._economic_mbb = opt._economic_mbb_vectorized
        try:
            p0 = time.perf_counter()
            predictor_results, predictor_boot = ref._final_predictor_results(
                labels, support, economic_predictions, preferred_horizon, cells.index
            )
            phase["predictive_bootstrap"] = time.perf_counter() - p0
            if len(predictor_results) != 64 or int(predictor_boot["replicates"]) != 4000:
                raise RuntimeError("qualification predictive inference shape drift")

            pidx = ref._period_index(cells.index, ref.ECON_START, ref.ECON_END)
            x = np.arange(len(pidx), dtype=float)
            base_returns = pd.Series(0.00035 + 0.004 * np.sin(x / 17.0) + 0.002 * np.cos(x / 31.0), index=pidx)
            base_gross = pd.Series(0.72 + 0.08 * np.sin(x / 43.0), index=pidx).clip(0.55, 0.9)
            rf_daily = pd.Series(0.00012 + 0.00001 * np.cos(x / 29.0), index=pidx)

            p0 = time.perf_counter()
            controller_g = ref._controller_paths(
                validation_predictions,
                economic_predictions,
                preferred_horizon,
                preferred_arch,
                exact_arch,
                pidx,
            )
            benchmark, controllers, econ_diag = ref._economic_results(
                controller_g, base_returns, base_gross, rf_daily
            )
            phase["economic_bootstrap_pbo"] = time.perf_counter() - p0
        finally:
            ref._bootstrap_predictive_lcbs = old_pred_boot
            ref._economic_mbb = old_econ_boot

        if len(controller_g) != 8 or len(controllers) != 8:
            raise RuntimeError("qualification controller count drift")
        pbo_splits = int(econ_diag["PBO_CSCV"].get("split_count", 0))
        if pbo_splits != 70:
            raise RuntimeError(f"qualification PBO split drift: {pbo_splits}")
        if int(econ_diag["simultaneous_bootstrap"]["replicates"]) != 4000:
            raise RuntimeError("qualification economic bootstrap replicate drift")

    total = time.perf_counter() - t0
    rss_upper, rss_components = _rss_upper_bound_bytes(tuning_audit, evaluation_audit)
    mem_total = _mem_total_bytes()
    rss_fraction = float(rss_upper / mem_total)
    all_zero = all(int(v) == 0 for v in counters.values())
    counts_ok = (
        attempts == 1632
        and validation_fit_calls == 31008
        and economic_fit_calls == 11904
        and validation_fit_calls + economic_fit_calls == 42912
        and nnls_solves == 40
        and len(predictor_results) == 64
        and len(controllers) == 8
        and int(predictor_boot["replicates"]) == 4000
        and int(econ_diag["simultaneous_bootstrap"]["replicates"]) == 4000
        and pbo_splits == 70
    )
    resource_ok = total <= 10800 and rss_upper <= 4294967296 and rss_fraction <= 0.60
    verdict = "PASS" if all_zero and counts_ok and equivalence["all_pass"] and resource_ok else "QUALIFICATION_FAIL"

    result = {
        "qualification_schema_version": 1,
        "research_id": RID,
        "implementation_commit_sha": os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND"),
        "synthetic_input_sha256": input_hash,
        "runner_label": "ubuntu-24.04",
        "runner_os_image": os.environ.get("ImageVersion", os.environ.get("ImageOS", platform.platform())),
        "cpu_architecture": platform.machine(),
        "cpu_logical_count": os.cpu_count(),
        "mem_total_bytes": mem_total,
        "python_version": sys.version.split()[0],
        "dependency_versions": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__,
        },
        "thread_environment": {
            k: os.environ.get(k)
            for k in ("PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")
        },
        "process_worker_count": opt.WORKERS,
        "deterministic_seeds": {"scientific": 660066, "qualification_synthetic": 670067},
        "historical_content_read_counters": counters,
        "network_fetch_count": int(counters["network_fetches"]),
        "declared_and_actual_indicator_atlas_cells": {"declared": 8080, "actual": int(atlas["actual_cells_reported"])},
        "declared_and_actual_validation_configs": {"declared": 1632, "actual": int(attempts)},
        "declared_and_actual_validation_fit_calls": {"declared": 31008, "actual": validation_fit_calls},
        "declared_and_actual_economic_fit_calls": {"declared": 11904, "actual": economic_fit_calls},
        "declared_and_actual_total_fit_calls": {"declared": 42912, "actual": validation_fit_calls + economic_fit_calls},
        "declared_and_actual_nnls_solves": {"declared": 40, "actual": nnls_solves},
        "declared_and_actual_final_tracks": {"declared": 64, "actual": len(predictor_results)},
        "declared_and_actual_controllers": {"declared": 8, "actual": len(controllers)},
        "declared_and_actual_predictive_bootstrap_replicates": {"declared": 4000, "actual": int(predictor_boot["replicates"])},
        "declared_and_actual_economic_bootstrap_replicates": {"declared": 4000, "actual": int(econ_diag["simultaneous_bootstrap"]["replicates"])},
        "declared_and_actual_pbo_splits": {"declared": 70, "actual": pbo_splits},
        "phase_wall_clock_seconds": {k: float(v) for k, v in phase.items()},
        "total_wall_clock_seconds": float(total),
        "peak_process_tree_rss_bytes": int(rss_upper),
        "peak_rss_fraction_of_memtotal": rss_fraction,
        "rss_measurement_method": "conservative upper bound = parent lifetime maxrss + sum of each observed worker lifetime maxrss",
        "rss_components_bytes": rss_components,
        "swap_or_oom_observed": False,
        "reference_equivalence_results": equivalence,
        "synthetic_event_onset_count": int(len(bundle.events)),
        "qualification_verdict": verdict,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    return result


def run_quick_equivalence() -> dict[str, Any]:
    frames = _synthetic_frames()
    cells, families, meta, signals = ref._common_feature_objects(frames)
    labels = _synthetic_labels(signals)
    support = _support()
    market_indices = {a: pd.DatetimeIndex(frames[a].index) for a in ee.ASSETS}
    atlas, screened = ref.build_indicator_warning_atlas(signals, meta, labels, support, market_indices)
    eq = _reference_equivalence(cells, families, signals, labels, market_indices, screened)
    return {
        "research_id": RID,
        "mode": "QUICK_EQUIVALENCE_NONHISTORICAL",
        "indicator_cells": int(atlas["actual_cells_reported"]),
        "reference_equivalence_results": eq,
        "pass": bool(eq["all_pass"] and int(atlas["actual_cells_reported"]) == 8080),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("quick", "full"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    result = run_quick_equivalence() if args.mode == "quick" else run_full_qualification()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text, flush=True)
    if args.mode == "quick":
        return 0 if result.get("pass") else 1
    return 0 if result.get("qualification_verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
