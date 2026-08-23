"""Synthetic-only Stage4 qualification hooks for BRRK 0084.

No controlled historical payload, network access, or Stage8 marker is touched.
"""
from __future__ import annotations

from .engine import (
    DECLARED_TRIALS,
    ExecutionAccounting,
    fractional_ranks,
    holm_adjust,
    invert_rank,
    preprocess_rank,
    q1_q5_supported,
    replacement_fraction,
    terminal_classification,
)


def _synthetic_cross_section(n: int = 40) -> dict[str, float]:
    return {f"S{i:02d}": float(i) for i in range(n)}


def run_synthetic_qualification() -> dict[str, object]:
    checks: dict[str, bool] = {}

    raw = _synthetic_cross_section()
    ranked = preprocess_rank(raw)
    checks["declared_trials_exact"] = DECLARED_TRIALS == 64
    checks["rank_bounds"] = min(ranked.values()) == 0.0 and max(ranked.values()) == 1.0
    checks["q1_q5_support"] = q1_q5_supported(ranked)

    inv = invert_rank(ranked)
    checks["signed_counterpart"] = all(abs(inv[k] + ranked[k] - 1.0) < 1e-12 for k in ranked)

    ties = {f"T{i:02d}": float(i // 2) for i in range(40)}
    tie_ranks = fractional_ranks(ties)
    checks["ties_average_rank"] = all(tie_ranks[f"T{i:02d}"] == tie_ranks[f"T{i+1:02d}"] for i in range(0, 40, 2))

    adjusted = holm_adjust([0.001, 0.02, 0.2, 0.9])
    checks["holm_monotone_valid"] = all(0.0 <= p <= 1.0 for p in adjusted) and adjusted[0] <= adjusted[1] <= adjusted[2] <= adjusted[3]

    checks["replacement_accounting"] = abs(replacement_fraction({"A", "B", "C", "D"}, {"B", "C", "D", "E"}) - 0.25) < 1e-12

    valid = ExecutionAccounting(
        declared_trials=64,
        scientific_engine_calls=1,
        scientific_source_network_fetches=0,
        identity_valid=True,
        lookahead_valid=True,
        persistence_valid=True,
    )
    invalid = ExecutionAccounting(
        declared_trials=63,
        scientific_engine_calls=1,
        scientific_source_network_fetches=0,
        identity_valid=True,
        lookahead_valid=True,
        persistence_valid=True,
    )
    checks["terminal_pass"] = terminal_classification(
        accounting=valid, any_qualified=True, support_possible=True, inference_defined=True
    ) == "PASS"
    checks["terminal_fail"] = terminal_classification(
        accounting=valid, any_qualified=False, support_possible=True, inference_defined=True
    ) == "FAIL_NO_QUALIFIED_FACTOR"
    checks["terminal_inconclusive"] = terminal_classification(
        accounting=valid, any_qualified=False, support_possible=False, inference_defined=True
    ) == "INCONCLUSIVE_INSUFFICIENT_SUPPORT"
    checks["identity_or_accounting_drift_invalid"] = terminal_classification(
        accounting=invalid, any_qualified=True, support_possible=True, inference_defined=True
    ) == "INVALID_EXECUTION"

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
    print(json.dumps(run_synthetic_qualification(), sort_keys=True, indent=2))
