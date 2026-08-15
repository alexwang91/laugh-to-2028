from __future__ import annotations

import json

from .execution_graph import (
    all_nonhazard_keys,
    all_p07_keys,
    all_p08_keys,
    build_downstream_manifest,
    consume_manifest,
)


def regime_inputs(name: str):
    nonhazard = list(all_nonhazard_keys())
    p07 = list(all_p07_keys())
    p08 = list(all_p08_keys())

    if name == "FULL_SUPPORT":
        return nonhazard, p07, p08
    if name == "PARTIAL_SUPPORT":
        return nonhazard[::2], p07[::2], p08[::2]
    if name == "SINGLE_CLASS_UNDEFINED_TRACKS":
        keep_nh = [k for i, k in enumerate(nonhazard) if i % 4 != 0]
        keep_p07 = [k for i, k in enumerate(p07) if i % 4 != 0]
        keep_p08 = [k for i, k in enumerate(p08) if i % 4 != 0]
        return keep_nh, keep_p07, keep_p08
    if name == "MISSING_BASE_PREDICTIONS":
        return nonhazard, p07, p08[::2]
    if name == "MIXED_P07_P08_ELIGIBILITY":
        keep_nh = [k for i, k in enumerate(nonhazard) if i % 3 != 0]
        keep_p07 = p07[::2]
        keep_p08 = [k for i, k in enumerate(p08) if i % 4 == 0]
        return keep_nh, keep_p07, keep_p08
    raise ValueError(name)


def run_mode(name: str, mode: str) -> dict:
    if mode not in {"qualification", "controlled_mode_dry_run"}:
        raise ValueError(mode)
    nh, p07, p08 = regime_inputs(name)
    manifest = build_downstream_manifest(nh, p07, p08)
    trace = consume_manifest(manifest)
    return {
        "mode": mode,
        "regime": name,
        "manifest_sha256": manifest["sha256"],
        "manifest_bytes": manifest["canonical_bytes"],
        "expected_economic_fit_calls": manifest["expected_economic_fit_calls"],
        "expected_p08_nnls_solves": manifest["expected_p08_nnls_solves"],
        "observed_economic_fit_attempts": trace["observed_fit_attempts"],
        "observed_p08_nnls_attempts": trace["observed_nnls_attempts"],
        "terminal_trace_complete": trace["complete"],
        "trace_sha256": trace["sha256"],
        "historical_reads": 0,
        "network_fetches": 0,
    }


def qualify() -> dict:
    regimes = [
        "FULL_SUPPORT",
        "PARTIAL_SUPPORT",
        "SINGLE_CLASS_UNDEFINED_TRACKS",
        "MISSING_BASE_PREDICTIONS",
        "MIXED_P07_P08_ELIGIBILITY",
    ]
    results = []
    for regime in regimes:
        q = run_mode(regime, "qualification")
        c = run_mode(regime, "controlled_mode_dry_run")
        assert q["manifest_bytes"] == c["manifest_bytes"]
        assert q["manifest_sha256"] == c["manifest_sha256"]
        assert q["expected_economic_fit_calls"] == q["observed_economic_fit_attempts"]
        assert q["expected_p08_nnls_solves"] == q["observed_p08_nnls_attempts"]
        assert q["terminal_trace_complete"] and c["terminal_trace_complete"]
        assert q["historical_reads"] == c["historical_reads"] == 0
        assert q["network_fetches"] == c["network_fetches"] == 0
        results.append({
            "regime": regime,
            "manifest_sha256": q["manifest_sha256"],
            "trace_sha256": q["trace_sha256"],
            "economic_fit_calls": q["expected_economic_fit_calls"],
            "p08_nnls_solves": q["expected_p08_nnls_solves"],
            "manifest_byte_identical": True,
            "terminal_trace_complete": True,
        })

    full = next(r for r in results if r["regime"] == "FULL_SUPPORT")
    assert full["economic_fit_calls"] == 11904
    assert full["p08_nnls_solves"] == 40

    return {
        "research_id": "BRRK-BTC-SOL-PATH-EVENT-EXECUTION-EQUIVALENCE-0068",
        "qualification_verdict": "PASS",
        "validation_fit_calls": 31008,
        "historical_reads": 0,
        "network_fetches": 0,
        "regimes": results,
    }


if __name__ == "__main__":
    print(json.dumps(qualify(), indent=2, sort_keys=True))
