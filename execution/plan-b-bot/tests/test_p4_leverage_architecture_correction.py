from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
STOPPED_0039 = ROOT / "research" / "leverage_0039" / "LEVERAGE-0039.json"
PREREG_0040 = ROOT / "research" / "leverage_0040" / "LEVERAGE-0040.json"
DECISIONS = ROOT / "config" / "decision_registry.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_leverage_0039_is_permanently_stopped_before_first_run():
    data = _load(STOPPED_0039)
    assert data["experiment_id"] == "LEVERAGE-0039"
    assert data["status"] == "STOPPED_PRE_RUN"
    assert data["result_status"] == "NO_RESULT_EVER_PRODUCED"
    assert data["search_run"] is False
    assert data["candidate_matrix_generated"] is False
    assert data["selection_made"] is False
    assert data["superseded_by"] == "LEVERAGE-0040"
    assert data["production_authorized"] is False


def test_leverage_0040_uses_master_plan_two_layer_architecture():
    data = _load(PREREG_0040)
    assert data["experiment_id"] == "LEVERAGE-0040"
    assert data["status"] == "PREREGISTERED_BEFORE_FIRST_RUN"
    architecture = data["architecture"]
    assert architecture["frozen_defensive_scale_domain"] == [0.0, 1.0]
    assert architecture["final_scale_rule"] == (
        "final_scale = frozen_defensive_scale * leverage_multiplier"
    )
    assert data["candidate_research_caps"] == [1.0, 1.1, 1.2, 1.3]
    assert data["only_structural_change"]["component"] == (
        "separate post-defensive leverage multiplier"
    )
    assert "Do not extend" in data["only_structural_change"]["rule"]
    assert data["tail_risk"]["scenario_cvar_cdar_budget"] == 0.20
    assert data["catastrophic_drawdown_limit"] == 0.70
    assert data["production_authorized"] is False


def test_cap_one_is_structurally_exact_baseline_parity():
    data = _load(PREREG_0040)
    domain = data["architecture"]["leverage_multiplier_domain_by_cap"]
    assert domain["1.00"] == [1.0, 1.0]
    assert "reproduce the frozen BRRK-0011 <=1 baseline" in data["architecture"]["cap_1_parity_gate"]


def test_master_plan_benchmarks_are_mandatory():
    data = _load(PREREG_0040)
    ids = [row["id"] for row in data["mandatory_benchmarks"]]
    assert ids == [
        "BTC_BUY_AND_HOLD",
        "BRRK_EQUAL_WEIGHT_BUY_AND_HOLD",
        "P4_1_FROZEN_BRRK_0_1",
    ]
    assert "all three mandatory benchmarks" in data["benchmark_rule"]


def test_funding_spike_and_degraded_fill_stresses_are_preregistered():
    data = _load(PREREG_0040)
    funding = data["funding_treatment"]
    assert funding["signal_use"] == "FORBIDDEN"
    assert funding["threshold_optimization"] == "FORBIDDEN"
    assert funding["funding_spike_stress"]["multipliers"] == [2.0, 3.0, 5.0]

    degraded = data["degraded_fill_stress"]
    assert degraded["required"] is True
    names = [row["name"] for row in degraded["scenarios"]]
    assert names == ["DEPTH_50_PCT", "DEPTH_25_PCT", "PARTIAL_FILL_50_PCT"]
    assert "fails" in degraded["capacity_rule"]


def test_liquidation_snapshot_is_reused_without_re_capture_requirement():
    data = _load(PREREG_0040)
    assert data["liquidation_distance"]["snapshot"] == (
        "research/leverage_0039/hyperliquid_margin_snapshot.json"
    )
    assert data["liquidation_distance"]["missing_model_rule"] == "FAIL_CLOSED_NO_PROMOTION"


def test_decision_registry_preserves_closed_leverage_history_without_authorization():
    registry = _load(DECISIONS)
    assert registry["production_authorized_components"] == []
    decisions = {row["id"]: row for row in registry["decisions"]}

    assert decisions["LEVERAGE-0039"]["status"] == "REJECTED_STOPPED"

    closed_0040 = decisions["LEVERAGE-0040"]
    assert closed_0040["status"] == "REJECTED_STOPPED"
    assert "NO_PROMOTION" in closed_0040["decision"]
    assert "no production leverage was authorized" in closed_0040["decision"]

    follow_on = decisions["P4-LEVERAGE-SWEET-SPOT-2026-08-07"]
    assert follow_on["status"] == "SUPERSEDED"
    assert "consumed by preregistered LEVERAGE-0041" in follow_on["decision"]
    assert "new registered hypothesis and experiment ID" in follow_on["decision"]

    closed_0041 = decisions["LEVERAGE-0041"]
    assert closed_0041["status"] == "REJECTED_STOPPED"
    assert "NO_PROMOTION" in closed_0041["decision"]
    assert "production_authorized=false" in closed_0041["decision"]
