from research.brrk_btc_sol_path_event_execution_equivalence_0068.execution_graph import (
    all_nonhazard_keys,
    all_p07_keys,
    all_p08_keys,
    build_downstream_manifest,
    consume_manifest,
)
from research.brrk_btc_sol_path_event_execution_equivalence_0068.qualification import qualify, run_mode


def test_full_support_counts():
    m = build_downstream_manifest(all_nonhazard_keys(), all_p07_keys(), all_p08_keys())
    assert m["expected_economic_fit_calls"] == 11904
    assert m["expected_p08_nnls_solves"] == 40
    t = consume_manifest(m)
    assert t["observed_fit_attempts"] == 11904
    assert t["observed_nnls_attempts"] == 40
    assert t["complete"]


def test_modes_are_manifest_identical_for_all_regimes():
    for regime in [
        "FULL_SUPPORT",
        "PARTIAL_SUPPORT",
        "SINGLE_CLASS_UNDEFINED_TRACKS",
        "MISSING_BASE_PREDICTIONS",
        "MIXED_P07_P08_ELIGIBILITY",
    ]:
        q = run_mode(regime, "qualification")
        c = run_mode(regime, "controlled_mode_dry_run")
        assert q["manifest_bytes"] == c["manifest_bytes"]
        assert q["manifest_sha256"] == c["manifest_sha256"]
        assert q["expected_economic_fit_calls"] == q["observed_economic_fit_attempts"]
        assert q["expected_p08_nnls_solves"] == q["observed_p08_nnls_attempts"]


def test_partial_support_contracts_only_expected_actions():
    full = run_mode("FULL_SUPPORT", "qualification")
    partial = run_mode("PARTIAL_SUPPORT", "qualification")
    assert partial["expected_economic_fit_calls"] < full["expected_economic_fit_calls"]
    assert partial["expected_p08_nnls_solves"] < full["expected_p08_nnls_solves"]


def test_missing_base_predictions_contracts_nnls_without_economic_drop():
    full = run_mode("FULL_SUPPORT", "qualification")
    missing = run_mode("MISSING_BASE_PREDICTIONS", "qualification")
    assert missing["expected_economic_fit_calls"] == full["expected_economic_fit_calls"]
    assert missing["expected_p08_nnls_solves"] < full["expected_p08_nnls_solves"]


def test_qualification_passes_and_has_zero_historical_authority():
    result = qualify()
    assert result["qualification_verdict"] == "PASS"
    assert result["validation_fit_calls"] == 31008
    assert result["historical_reads"] == 0
    assert result["network_fetches"] == 0
