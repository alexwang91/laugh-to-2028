"""Synthetic-only qualification for BRRK 0084 Stage4 integration.

This module uses constructed evidence only. It performs no file I/O, network
access, controlled historical read, marker creation, or scientific source fetch.
"""
from __future__ import annotations

from .engine import ExecutionAccounting
from .execution_interface import TrialEvidence
from .integration import IntegratedTrialInput, integrate_trial_evidence
from .orchestration import declared_trial_manifest
from .persistence import ExecutionCounters


def _passing_evidence() -> TrialEvidence:
    return TrialEvidence(
        valid_dates=300,
        median_universe=40.0,
        mean_ic=0.05,
        mean_spread=0.04,
        holm_ic_p=1.0,
        holm_spread_p=1.0,
        declared_direction=1,
        calendar_year_ics={"2023": 0.04, "2024": 0.05, "2025": 0.06},
        bull_ic=0.05,
        bull_dates=100,
        bear_ic=0.04,
        bear_dates=100,
        high_vol_ic=0.05,
        high_vol_dates=100,
        low_vol_ic=0.04,
        low_vol_dates=100,
        high_liquidity_ic=0.05,
        high_liquidity_dates=100,
        low_liquidity_ic=0.04,
        low_liquidity_dates=100,
        leave_year_out_ics={"2023": 0.04, "2024": 0.05, "2025": 0.06},
        leave_size_out_ics={"LARGE": 0.04, "MID": 0.05, "SMALL": 0.06},
        median_q1_count=8.0,
        median_q5_count=8.0,
        median_replacement_fraction=0.25,
    )


def _valid_accounting() -> ExecutionAccounting:
    return ExecutionAccounting(
        declared_trials=64,
        scientific_engine_calls=1,
        scientific_source_network_fetches=0,
        identity_valid=True,
        lookahead_valid=True,
        persistence_valid=True,
    )


def _terminal_counters() -> ExecutionCounters:
    return ExecutionCounters(
        attempt_markers_created=1,
        controlled_objects_authorized=0,
        controlled_object_reads={},
        scientific_engine_calls=1,
        scientific_source_network_fetches=0,
        declared_trials=64,
    )


def run_integration_qualification() -> dict[str, object]:
    manifest = declared_trial_manifest()
    trials = tuple(
        IntegratedTrialInput(
            key=key,
            evidence=_passing_evidence(),
            raw_ic_p=1e-6,
            raw_spread_p=1e-6,
        )
        for key in manifest
    )
    kwargs = dict(
        trials=trials,
        accounting=_valid_accounting(),
        counters=_terminal_counters(),
        support_possible=True,
        inference_defined=True,
        provenance={"fixture": "synthetic-only"},
    )
    first = integrate_trial_evidence(**kwargs)
    second = integrate_trial_evidence(**kwargs)

    checks: dict[str, bool] = {
        "exact_manifest": len(manifest) == 64 and len(set(manifest)) == 64,
        "pass_classification": first.classification == "PASS",
        "all_trials_qualified": len(first.qualified_trials) == 64,
        "exact_trial_results": len(first.trial_results) == 64,
        "deterministic_bundle": first.bundle == second.bundle,
        "deterministic_digest": first.bundle_sha256 == second.bundle_sha256,
        "execution_gate_true": first.gate_summary.get("execution_valid") is True,
        "qualified_count_exact": first.gate_summary.get("qualified_trial_count") == 64,
    }

    try:
        integrate_trial_evidence(**{**kwargs, "trials": trials[:-1]})
    except ValueError:
        checks["missing_trial_fail_closed"] = True
    else:
        checks["missing_trial_fail_closed"] = False

    drift_accounting = ExecutionAccounting(
        declared_trials=63,
        scientific_engine_calls=1,
        scientific_source_network_fetches=0,
        identity_valid=True,
        lookahead_valid=True,
        persistence_valid=True,
    )
    invalid = integrate_trial_evidence(**{**kwargs, "accounting": drift_accounting})
    checks["accounting_drift_invalid"] = invalid.classification == "INVALID_EXECUTION"

    passed = all(checks.values())
    return {
        "qualification": "PASS" if passed else "FAIL",
        "controlled_history_reads": 0,
        "scientific_source_network_fetches": 0,
        "stage8_attempt_consumed": 0,
        "checks": checks,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_integration_qualification(), sort_keys=True, indent=2))
