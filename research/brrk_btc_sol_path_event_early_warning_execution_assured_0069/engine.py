from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from research.brrk_btc_sol_path_event_early_warning_0066 import engine as ref
from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import engine as opt
from research.brrk_btc_sol_path_event_execution_equivalence_0068 import execution_graph as graph

RID = "BRRK-BTC-SOL-PATH-EVENT-EARLY-WARNING-EXECUTION-ASSURED-0069"
WORKERS = 4

_ARCH_MAP = {
    "P01_FAMILY_RIDGE_LOGIT": "P01",
    "P02_RAW_ELASTIC_NET_LOGIT": "P02",
    "P03_VALIDATION_SCREENED_SIGNAL_LOGIT": "P03",
    "P04_PCR_LOGIT": "P04",
    "P05_THEORY_QUADRATIC_LOGIT": "P05",
    "P06_SHALLOW_GBDT_CLASSIFIER": "P06",
}
_TARGET_MAP = {
    "T1_ANY_DOWN": "ANY_DOWN",
    "T2_MAJOR_DOWN": "MAJOR_DOWN",
    "T3_ANY_SIDEWAYS": "ANY_SIDEWAYS",
    "T4_LONG_SIDEWAYS": "LONG_SIDEWAYS",
}


class ExecutionAssuranceError(RuntimeError):
    pass


def _manifest_from_selected_params(selected_params: Mapping[tuple[str, str, str, int], Mapping[str, Any]]) -> dict:
    selected_nonhazard: set[tuple[str, str, int, str]] = set()
    selected_p07: set[tuple[str, str]] = set()
    eligible_p08: set[tuple[str, str, int]] = set()
    for architecture, asset, target, horizon in selected_params:
        gtarget = _TARGET_MAP[target]
        if architecture in _ARCH_MAP:
            selected_nonhazard.add((asset, gtarget, int(horizon), _ARCH_MAP[architecture]))
        elif architecture == "P07_DISCRETE_TIME_HAZARD_LOGIT":
            selected_p07.add((asset, gtarget))
        elif architecture == "P08_STACKED_PROBABILITY_ENSEMBLE":
            eligible_p08.add((asset, gtarget, int(horizon)))
    return graph.build_downstream_manifest(selected_nonhazard, selected_p07, eligible_p08)


def _runtime_accounting(tuning_audit: Mapping[str, Any], evaluation_audit: Mapping[str, Any], manifest: dict) -> dict[str, Any]:
    validation_observed = int(tuning_audit.get("__runtime__", {}).get("fit_call_attempts", 0))
    economic_observed = int(evaluation_audit.get("__runtime__", {}).get("fit_call_attempts", 0))
    nnls_observed = int(tuning_audit.get("__runtime__", {}).get("nnls_solves", 0))
    expected_economic = int(manifest["expected_economic_fit_calls"])
    expected_nnls = int(manifest["expected_p08_nnls_solves"])
    if validation_observed != 31008:
        raise ExecutionAssuranceError(f"validation physical accounting mismatch expected=31008 observed={validation_observed}")
    if economic_observed != expected_economic:
        raise ExecutionAssuranceError(f"economic physical accounting mismatch expected={expected_economic} observed={economic_observed}")
    if nnls_observed != expected_nnls:
        raise ExecutionAssuranceError(f"P08 NNLS accounting mismatch expected={expected_nnls} observed={nnls_observed}")
    trace = graph.consume_manifest(manifest)
    if not trace["complete"] or len(trace["payload"]["traces"]) != len(manifest["payload"]["units"]):
        raise ExecutionAssuranceError("terminal trace incomplete")
    return {
        "manifest_sha256": manifest["sha256"],
        "manifest_unit_count": len(manifest["payload"]["units"]),
        "terminal_trace_sha256": trace["sha256"],
        "terminal_trace_count": len(trace["payload"]["traces"]),
        "terminal_trace_complete": True,
        "validation_fit_calls_expected": 31008,
        "validation_fit_calls_observed": validation_observed,
        "economic_fit_calls_expected_manifest_derived": expected_economic,
        "economic_fit_calls_observed": economic_observed,
        "p08_nnls_expected_manifest_derived": expected_nnls,
        "p08_nnls_observed": nnls_observed,
        "process_worker_count": WORKERS,
        "inference_barrier_released": True,
    }


def evaluate_program(frames: Mapping[str, pd.DataFrame], baseline_returns: pd.Series, baseline_gross: pd.Series, rf_daily: pd.Series, *, bootstrap_replicates: int = ref.BOOT_REPS) -> dict[str, Any]:
    if WORKERS != 4:
        raise ExecutionAssuranceError("0069 worker-count drift")
    if bootstrap_replicates != 4000:
        raise ValueError("historical execution must use frozen 4000 bootstrap replicates")

    frames = ref._naive_frames(frames)
    cells, families, meta, signals = ref._common_feature_objects(frames)
    bundle = ref.ee.build_event_atlas(frames)
    labels, support = ref._labels_and_support(bundle, cells.index)
    atlas, screened = ref.build_indicator_warning_atlas(signals, meta, labels, support, {a: bundle.asset_indices[a] for a in ref.ee.ASSETS})

    selected_params, validation_predictions, validation_metrics, tuning_audit, tuning_attempts = opt._tune_validation_parallel(
        cells, families, signals, labels, {a: bundle.asset_indices[a] for a in ref.ee.ASSETS}, screened
    )
    if tuning_attempts != 1632:
        raise ExecutionAssuranceError(f"validation tuning configuration drift: {tuning_attempts}")
    preferred_horizon, preferred_arch, exact_arch = ref._preferred_selections(validation_metrics)
    manifest = _manifest_from_selected_params(selected_params)
    economic_predictions, evaluation_audit = opt._evaluate_selected_parallel(
        cells, families, signals, labels, {a: bundle.asset_indices[a] for a in ref.ee.ASSETS}, screened, selected_params, validation_predictions
    )

    assurance = _runtime_accounting(tuning_audit, evaluation_audit, manifest)
    predictor_results, predictor_boot = ref._final_predictor_results(labels, support, economic_predictions, preferred_horizon, cells.index)

    pidx = ref._series(baseline_returns).index
    pidx = pidx[(pidx >= ref.ECON_START) & (pidx <= ref.ECON_END)]
    if len(pidx) < 100:
        raise ValueError("economic portfolio support unavailable")
    controller_error = None
    try:
        controller_g = ref._controller_paths(validation_predictions, economic_predictions, preferred_horizon, preferred_arch, exact_arch, pidx)
        benchmark, controllers, econ_diag = ref._economic_results(controller_g, baseline_returns, baseline_gross, rf_daily)
    except Exception as exc:
        controller_error = {"error_type": type(exc).__name__, "error_message": str(exc)}
        benchmark = {}
        controllers = {name: {"status": "COMPONENT_UNAVAILABLE", "passes_all_economic_gates": False} for name in ref.CONTROLLERS}
        econ_diag = {
            "simultaneous_bootstrap": {"block_length": ref.BOOT_BLOCK, "replicates": ref.BOOT_REPS, "seed": ref.BOOT_SEED, "q95": None},
            "PBO_CSCV": {"status": "NOT_EVALUATED"},
        }

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
    for asset in ref.ee.ASSETS:
        for etype in ("DOWN", "SIDEWAYS"):
            grades = list(ref.ee.DOWN_GRADE_RANK) if etype == "DOWN" else list(ref.ee.SIDEWAYS_GRADE_RANK)
            for grade in grades:
                n = 0 if bundle.events.empty else int(((bundle.events["asset"] == asset) & (bundle.events["event_type"] == etype) & (bundle.events["duration_grade"] == grade)).sum())
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
        "predictive_summary": {"winner_count": len(predictive_winners), "winners": predictive_winners},
        "controller_summary": {"winner_count": len(economic_winners), "winners": economic_winners},
        "economic_summary": {"benchmark": benchmark, "controllers": controllers, "simultaneous_bootstrap": econ_diag["simultaneous_bootstrap"]},
        "selection_risk": econ_diag["PBO_CSCV"],
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    evidence = {
        "event_atlas": ref.ee.event_records(bundle),
        "support": {ref._track(a, t, h): dict(v) for (a, t, h), v in support.items()},
        "indicator_warning_atlas": atlas,
        "validation_screened_signals": {ref._track(a, t, h): list(v) for (a, t, h), v in screened.items()},
        "validation_selected_hyperparameters": {ref._atrack(a, asset, target, h): dict(v) for (a, asset, target, h), v in selected_params.items()},
        "validation_metrics": {ref._atrack(a, asset, target, h): dict(v) for (a, asset, target, h), v in validation_metrics.items()},
        "tuning_audit": tuning_audit,
        "evaluation_audit": evaluation_audit,
        "controller_error": controller_error,
        "0069_execution_assurance": assurance,
    }
    return {"primary_result": primary, "evidence": evidence}


__all__ = ["RID", "WORKERS", "evaluate_program", "_manifest_from_selected_params"]
