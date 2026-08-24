"""Synthetic-only Stage4 qualification hooks for BRRK 0084.

No controlled historical payload, network access, or Stage8 marker is touched.
"""
from __future__ import annotations

from datetime import date

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
from .orchestration import (
    calendar_year_partition,
    declared_trial_manifest,
    family_holm,
    leave_one_group_out,
    median_split_partition,
    parse_staged_rows,
    pit_universe_by_date,
    trend_partition,
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

    staged = [
        {"session": "2026-01-02", "symbol": "aaa", "close": 10.0, "volume": 100.0, "source_object": "OBJ1"},
        {"session": "2026-01-02", "symbol": "bbb", "close": 20.0, "volume": 200.0, "source_object": "OBJ1"},
        {"session": "2026-01-03", "symbol": "aaa", "close": 11.0, "volume": 110.0, "source_object": "OBJ1"},
    ]
    parsed = parse_staged_rows(staged, {"OBJ1"})
    checks["staged_parser_deterministic"] = (
        len(parsed) == 3
        and parsed[0].symbol == "AAA"
        and parsed[-1].session == date(2026, 1, 3)
    )
    try:
        parse_staged_rows(staged, {"OTHER"})
    except ValueError:
        checks["staged_parser_unauthorized_fail_closed"] = True
    else:
        checks["staged_parser_unauthorized_fail_closed"] = False

    pit = pit_universe_by_date(
        parsed,
        {"AAA": date(2026, 1, 1), "BBB": date(2026, 1, 3)},
        {"AAA": None, "BBB": None},
    )
    checks["pit_universe_respects_eligibility"] = (
        pit[date(2026, 1, 2)] == ("AAA",)
        and pit[date(2026, 1, 3)] == ("AAA",)
    )

    manifest = declared_trial_manifest()
    checks["trial_manifest_exact_unique"] = len(manifest) == 64 and len(set(manifest)) == 64
    raw_p = {key: 0.01 + (i % 10) * 0.005 for i, key in enumerate(manifest)}
    adjusted_family = family_holm(raw_p)
    checks["family_holm_manifest_preserved"] = set(adjusted_family) == set(manifest) and all(
        0.0 <= p <= 1.0 for p in adjusted_family.values()
    )

    trend = trend_partition(
        {
            date(2026, 1, 1): 100.0,
            date(2026, 1, 2): 90.0,
            date(2026, 1, 3): 80.0,
        },
        lookback_sessions=1,
    )
    checks["trend_partition_strictly_lagged"] = (
        date(2026, 1, 1) not in trend
        and trend[date(2026, 1, 2)] == "BULL"
        and trend[date(2026, 1, 3)] == "BEAR"
    )

    med = median_split_partition(
        {
            date(2026, 2, 1): 2.0,
            date(2026, 2, 2): 1.0,
            date(2026, 2, 3): 3.0,
        },
        "HIGH",
        "LOW",
    )
    checks["median_partition_strictly_lagged"] = (
        date(2026, 2, 1) not in med
        and med[date(2026, 2, 2)] == "LOW"
        and med[date(2026, 2, 3)] == "HIGH"
    )

    years = calendar_year_partition([date(2025, 12, 31), date(2026, 1, 1)])
    checks["calendar_partition_exact"] = years == {
        date(2025, 12, 31): "2025",
        date(2026, 1, 1): "2026",
    }

    loo = leave_one_group_out({"LARGE": {"A", "B"}, "MID": {"C"}, "SMALL": {"D"}})
    checks["leave_size_group_out_exact"] = (
        loo["LARGE"] == ("C", "D")
        and loo["MID"] == ("A", "B", "D")
        and loo["SMALL"] == ("A", "B", "C")
    )

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
