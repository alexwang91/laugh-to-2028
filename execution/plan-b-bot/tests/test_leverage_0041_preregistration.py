from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research" / "leverage_0041" / "LEVERAGE-0041.json"
DECISIONS = ROOT / "config" / "decision_registry.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_leverage_0041_is_new_preregistered_experiment_on_merged_p4_5_base():
    data = _load(PREREG)
    assert data["experiment_id"] == "LEVERAGE-0041"
    assert data["status"] == "PREREGISTERED_BEFORE_FIRST_RUN"
    assert data["base_main"] == "14dd9f2fb828d860b8552816814982dc4bd89b10"
    assert data["follows"] == "LEVERAGE-0040"
    assert data["research_integrity"]["leverage_0040_result_sha256"] == (
        "3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0"
    )
    assert data["research_integrity"]["no_0040_retuning"] is True
    assert data["production_authorized"] is False


def test_candidate_grid_is_frozen_around_120_without_preselecting_it():
    data = _load(PREREG)
    assert data["candidate_research_caps"] == [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]
    assert data["focal_design_point"] == 1.2
    assert "no favorable selection treatment" in data["focal_point_rule"]
    assert data["robustness"]["broad_region_rule"].startswith(
        "A selected cap must belong to a contiguous region of at least three"
    )
    assert "immediate lower and immediate higher" in data["robustness"]["broad_region_rule"]


def test_spot_first_perp_overlay_architecture_and_reserve_are_frozen():
    data = _load(PREREG)
    architecture = data["implementation_architecture"]
    assert architecture["name"] == "SPOT_FIRST_BASE_PLUS_PERP_OVERLAY_V1"
    assert architecture["cash_collateral_reserve_fraction_of_nav"] == 0.25
    assert "75 percent" in architecture["spot_cash_budget_rule"]
    assert "perp-only" in architecture["incremental_overlay_rule"]
    assert "PERP_ONLY_DEFAULT" in architecture["base_long_routing"]["BNB"]
    assert architecture["no_external_capital"] is True


def test_funding_logic_can_only_reduce_incremental_overlay():
    data = _load(PREREG)
    funding = data["funding_aware_overlay_reducer"]
    assert funding["lookback_hours"] == 168
    assert funding["full_overlay_max_debit_bps_per_day"] == 5.0
    assert funding["zero_overlay_min_debit_bps_per_day"] == 10.0
    assert "never raise gross exposure" in funding["monotonicity"]
    assert funding["threshold_optimization"] == "FORBIDDEN_AFTER_PREREGISTRATION"


def test_hard_tail_and_liquidation_boundaries_are_not_relaxed():
    data = _load(PREREG)
    assert data["tail_risk"]["scenario_cvar_cdar_budget"] == 0.20
    assert data["catastrophic_drawdown_limit"] == 0.70
    assert data["synthetic_market_stress"]["uniform_one_day_gap_returns"][-1] == -0.50
    assert ">55 percent" in data["liquidation_distance"]["acceptance"]
    assert data["liquidation_distance"]["missing_or_invalid_model_rule"] == (
        "FAIL_CLOSED_NO_PROMOTION"
    )


def test_preregistration_does_not_authorize_run_or_production():
    data = _load(PREREG)
    assert data["run_authority"]["status"] == "NOT_AUTHORIZED_BY_PREREGISTRATION_ALONE"
    assert "explicit owner RUN_ONCE" in data["run_authority"]["rule"]
    assert data["prospective_deployment_cap_rule"]["research_only"] is True
    assert "Separate explicit production decision" not in data["prospective_deployment_cap_rule"]["authorization"]
    assert "separate explicit production decision" in data["prospective_deployment_cap_rule"]["authorization"]


def test_decision_registry_registers_0041_without_production_authorization():
    registry = _load(DECISIONS)
    assert registry["production_authorized_components"] == []
    decisions = {row["id"]: row for row in registry["decisions"]}
    assert decisions["LEVERAGE-0040"]["status"] == "REJECTED_STOPPED"
    assert decisions["LEVERAGE-0041"]["status"] == "ACCEPTED_RESEARCH_TARGET"
    assert "preregistered" in decisions["LEVERAGE-0041"]["decision"].lower()
    assert "not run-authorized" in decisions["LEVERAGE-0041"]["decision"].lower()
