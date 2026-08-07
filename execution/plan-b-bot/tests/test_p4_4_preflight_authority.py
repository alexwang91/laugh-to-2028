from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "research" / "leverage_0040" / "LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json"
R1 = ROOT / "research" / "leverage_0040" / "run_leverage_0040_once_r1.py"
CONTRACT_WORKFLOW = ROOT / ".github" / "workflows" / "p4-4-leverage-0040-contract.yml"


def _contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_published_banded_holdings_are_forbidden_as_defensive_scale_source():
    data = _contract()
    assert data["defensive_scale_recovery"]["published_banded_ratio_forbidden"] is True
    assert "rebuild" in data["defensive_scale_recovery"]["authority"]
    assert data["authoritative_inputs"]["published_daily_weights"]["role"].startswith(
        "legacy banded-holdings evidence only"
    )


def test_raw_target_authority_is_pinned_to_frozen_sources():
    source = _contract()["authoritative_inputs"]["raw_target_authority"]
    assert source["feature_assets"] == ["BTC", "ETH", "SOL", "BNB", "XRP"]
    assert source["target_assets"] == ["BTC", "ETH", "SOL", "BNB"]
    assert source["build_brrk0011_scale"]["blob_sha"] == "cdcedd24a343a625e7b34c317633f68533de9ef3"
    assert source["build_benchmark_v1_and_portfolio_timing"]["blob_sha"] == "13746a52e561f049ff2f5de4cd58c359a78fa143"
    assert source["feature_authority"]["blob_sha"] == "e36612f7f7c6bea8744b5753bc20611f6580f13a"
    assert source["corrected_tail_risk"]["blob_sha"] == "bdf7cd6cb32961765716e4cb07288739e869703e"


def test_evaluation_session_starts_one_day_after_first_decision():
    data = _contract()["historical_input"]
    assert data["first_full_brrk_decision_date"] == "2022-12-09"
    assert data["full_brrk_evaluation_sessions"][0] == "2022-12-10"
    assert "next UTC daily return session" in data["decision_timing"]


def test_corrections_were_pre_result_and_non_economic():
    corrections = _contract()["pre_result_corrections"]
    assert {row["id"] for row in corrections} == {
        "PREFLIGHT-RAW-TARGET-001",
        "PREFLIGHT-SESSION-TIMING-002",
    }
    assert all(row["economic_parameter_change"] is False for row in corrections)
    assert all(row["cap_gt_1_observed_before_correction"] is False for row in corrections)


def test_r1_entrypoint_exists_and_old_ratio_loader_is_not_authority():
    text = R1.read_text(encoding="utf-8")
    assert "build_brrk0011_scale" in text
    assert "build_features_no_dominance" in text
    assert "published_banded_weights_used_for_scale\": False" in text
    assert "evaluation_start - pd.Timedelta(days=1)" in text


def test_contract_ci_switches_from_preflight_to_immutable_validation_after_result():
    text = CONTRACT_WORKFLOW.read_text(encoding="utf-8")
    assert "if [[ -f research/results/leverage_0040/summary.json ]]" in text
    assert "python research/leverage_0040/validate_leverage_0040_result.py" in text
    assert "python research/leverage_0040/run_leverage_0040_once_r1.py" in text
    assert "--preflight-only" in text
    assert '"research/results/leverage_0040/**"' in text
    assert '"config/decision_registry.json"' in text
