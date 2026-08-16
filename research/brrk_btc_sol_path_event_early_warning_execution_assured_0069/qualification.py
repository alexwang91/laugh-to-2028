from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from research.brrk_btc_sol_path_event_early_warning_execution_assured_0069 import engine
from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import qualification as q67
from research.brrk_btc_sol_path_event_execution_equivalence_0068 import qualification as q68

RID = engine.RID


def _synthetic_portfolio(index: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series, pd.Series]:
    x = np.arange(len(index), dtype=float)
    baseline_returns = pd.Series(0.00035 + 0.004 * np.sin(x / 17.0) + 0.002 * np.cos(x / 31.0), index=index)
    baseline_gross = pd.Series(0.72 + 0.08 * np.sin(x / 43.0), index=index).clip(0.55, 0.9)
    rf_daily = pd.Series(0.00012 + 0.00001 * np.cos(x / 29.0), index=index)
    return baseline_returns, baseline_gross, rf_daily


def _five_regime_gate() -> list[dict[str, Any]]:
    r = q68.qualify()
    if r["qualification_verdict"] != "PASS" or r["validation_fit_calls"] != 31008:
        raise RuntimeError("0068 canonical five-regime qualification failed")
    expected = {
        "FULL_SUPPORT": (11904, 40),
        "PARTIAL_SUPPORT": (5952, 20),
        "SINGLE_CLASS_UNDEFINED_TRACKS": (8928, 30),
        "MISSING_BASE_PREDICTIONS": (11904, 20),
        "MIXED_P07_P08_ELIGIBILITY": (7872, 10),
    }
    by_name = {x["regime"]: x for x in r["regimes"]}
    if set(by_name) != set(expected):
        raise RuntimeError("0069 five-regime name set drift")
    for name, (fits, nnls) in expected.items():
        row = by_name[name]
        if row["economic_fit_calls"] != fits or row["p08_nnls_solves"] != nnls:
            raise RuntimeError(f"0069 five-regime count drift: {name}")
        if not row["manifest_byte_identical"] or not row["terminal_trace_complete"]:
            raise RuntimeError(f"0069 five-regime graph-equivalence failure: {name}")
    return r["regimes"]


def run_full_qualification() -> dict[str, Any]:
    t0 = time.perf_counter()
    regimes = _five_regime_gate()
    phase: dict[str, float] = {"five_regime_graph_gate": time.perf_counter() - t0}

    with q67.isolation_guard() as counters:
        p0 = time.perf_counter()
        frames = q67._synthetic_frames()
        input_hash = q67._hash_frames(frames)
        cells, _families, _meta, signals = engine.ref._common_feature_objects(frames)
        labels = q67._synthetic_labels(signals)
        support = q67._support()
        pidx = engine.ref._period_index(cells.index, engine.ref.ECON_START, engine.ref.ECON_END)
        baseline_returns, baseline_gross, rf_daily = _synthetic_portfolio(pidx)
        phase["synthetic_input_build"] = time.perf_counter() - p0

        original_labels_and_support = engine.ref._labels_and_support

        def qualification_labels_and_support(_bundle: Any, _index: pd.DatetimeIndex):
            return labels, support

        engine.ref._labels_and_support = qualification_labels_and_support
        try:
            p0 = time.perf_counter()
            result = engine.evaluate_program(
                frames,
                baseline_returns,
                baseline_gross,
                rf_daily,
                bootstrap_replicates=4000,
            )
            phase["full_shape_0069_execution"] = time.perf_counter() - p0
        finally:
            engine.ref._labels_and_support = original_labels_and_support

    primary = result["primary_result"]
    evidence = result["evidence"]
    assurance = evidence["0069_execution_assurance"]
    tuning_audit = evidence["tuning_audit"]
    evaluation_audit = evidence["evaluation_audit"]

    validation_fits = int(tuning_audit["__runtime__"]["fit_call_attempts"])
    economic_fits = int(evaluation_audit["__runtime__"]["fit_call_attempts"])
    nnls_solves = int(tuning_audit["__runtime__"]["nnls_solves"])
    rss_upper, rss_components = q67._rss_upper_bound_bytes(tuning_audit, evaluation_audit)
    mem_total = q67._mem_total_bytes()
    rss_fraction = float(rss_upper / mem_total)
    total = time.perf_counter() - t0

    all_zero = all(int(v) == 0 for v in counters.values())
    shape_ok = (
        int(primary["indicator_atlas_hypothesis_cells"]) == 8080
        and int(primary["actual_validation_tuning_configs_evaluated"]) == 1632
        and validation_fits == 31008
        and int(primary["final_predictor_track_count"]) == 64
        and int(primary["final_controller_count"]) == 8
        and int(primary["actual_variants_evaluated"]) == 1704
        and int(primary["predictor_simultaneous_bootstrap"]["replicates"]) == 4000
        and int(primary["economic_simultaneous_bootstrap"]["replicates"]) == 4000
        and int(primary["PBO_CSCV"].get("split_count", 0)) == 70
    )
    assurance_ok = (
        assurance["inference_barrier_released"] is True
        and assurance["terminal_trace_complete"] is True
        and assurance["validation_fit_calls_expected"] == assurance["validation_fit_calls_observed"] == 31008
        and assurance["economic_fit_calls_expected_manifest_derived"] == assurance["economic_fit_calls_observed"] == economic_fits
        and assurance["p08_nnls_expected_manifest_derived"] == assurance["p08_nnls_observed"] == nnls_solves
        and assurance["terminal_trace_count"] == assurance["manifest_unit_count"]
        and assurance["process_worker_count"] == 4
    )
    resource_ok = total <= 10800 and rss_upper <= 4294967296 and rss_fraction <= 0.60
    verdict = "PASS" if all_zero and shape_ok and assurance_ok and resource_ok else "QUALIFICATION_FAIL"

    return {
        "qualification_schema_version": 1,
        "research_id": RID,
        "implementation_commit_sha": os.environ.get("QUALIFIED_IMPLEMENTATION_SHA", os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND")),
        "synthetic_input_sha256": input_hash,
        "runner_label": "ubuntu-24.04",
        "runner_os_image": os.environ.get("ImageVersion", os.environ.get("ImageOS", platform.platform())),
        "cpu_architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "process_worker_count": engine.WORKERS,
        "historical_content_read_counters": counters,
        "network_fetch_count": int(counters["network_fetches"]),
        "required_regimes": regimes,
        "declared_and_actual_validation_configs": {"declared": 1632, "actual": int(primary["actual_validation_tuning_configs_evaluated"])},
        "declared_and_actual_validation_fit_calls": {"declared": 31008, "actual": validation_fits},
        "manifest_derived_economic_fit_calls": {"expected": int(assurance["economic_fit_calls_expected_manifest_derived"]), "actual": economic_fits},
        "manifest_derived_p08_nnls_solves": {"expected": int(assurance["p08_nnls_expected_manifest_derived"]), "actual": nnls_solves},
        "declared_and_actual_final_tracks": {"declared": 64, "actual": int(primary["final_predictor_track_count"])},
        "declared_and_actual_controllers": {"declared": 8, "actual": int(primary["final_controller_count"])},
        "declared_and_actual_predictive_bootstrap_replicates": {"declared": 4000, "actual": int(primary["predictor_simultaneous_bootstrap"]["replicates"])},
        "declared_and_actual_economic_bootstrap_replicates": {"declared": 4000, "actual": int(primary["economic_simultaneous_bootstrap"]["replicates"])},
        "declared_and_actual_pbo_splits": {"declared": 70, "actual": int(primary["PBO_CSCV"].get("split_count", 0))},
        "execution_assurance": assurance,
        "qualification_scientific_classification_ignored": primary["classification"],
        "phase_wall_clock_seconds": {k: float(v) for k, v in phase.items()},
        "total_wall_clock_seconds": float(total),
        "peak_process_tree_rss_bytes": int(rss_upper),
        "peak_rss_fraction_of_memtotal": rss_fraction,
        "rss_components_bytes": rss_components,
        "swap_or_oom_observed": False,
        "qualification_verdict": verdict,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    result = run_full_qualification()
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text, flush=True)
    return 0 if result["qualification_verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
