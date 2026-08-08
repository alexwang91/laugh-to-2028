from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "research" / "cycle_exit" / "p5_4_behavior_map_contract.json"
V2_RESULT = ROOT / "research" / "results" / "p5_3_v2_market_state"

STATE_ORDER = [
    "NORMAL_BULL",
    "BTC_LEADERSHIP_MATURING",
    "LATE_BULL_ROTATION",
    "EXHAUSTION_WATCH",
    "DE_RISK_1",
    "DE_RISK_2",
    "FLAT",
]

EXPECTED = {
    "DE_RISK_ONLY": [1.0, 1.0, 1.0, 1.0, 0.65, 0.30, 0.0],
    "PROGRESSIVE": [1.0, 1.0, 0.95, 0.80, 0.55, 0.25, 0.0],
    "EARLY_DEFENSIVE": [1.0, 0.95, 0.90, 0.70, 0.45, 0.20, 0.0],
}


def test_p5_4_contract_binds_to_immutable_v2_and_no_profile_selected() -> None:
    c = json.loads(CONTRACT.read_text())
    assert c["contract_id"] == "P5.4-FIXED-GROSS-BEHAVIOR-CANDIDATES-V1"
    assert c["status"] == "FROZEN_BEFORE_P5_4_ECONOMIC_EVALUATION"
    assert c["base_main"] == "9c630c9b4b22146ffabd8fd3f62b08477f3da0f7"
    d = c["immutable_dependencies"]
    assert d["p5_3_v2_result_commit"] == "e732b7ebe570236bf43084caecb6ea15f7edecb8"
    assert d["p5_3_v2_summary_sha256"] == (V2_RESULT / "summary.sha256").read_text().strip()
    assert d["p5_3_v2_summary_sha256"] == "05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52"
    assert d["p5_3_selected_profile"] is None
    assert d["phase4_above_one_candidate_eligible"] is False
    assert float(d["production_gross_cap"]) == 1.0


def test_candidate_family_is_exact_small_and_not_a_grid_search() -> None:
    c = json.loads(CONTRACT.read_text())
    assert c["state_order"] == STATE_ORDER
    assert list(c["candidate_maps"]) == ["DE_RISK_ONLY", "PROGRESSIVE", "EARLY_DEFENSIVE"]
    assert c["candidate_family_design"] == {
        "candidate_count": 3,
        "continuous_grid_search_forbidden": True,
        "post_result_new_candidate_forbidden_under_same_contract": True,
        "purpose": "Coarse behavioral sensitivity family rather than numerical optimization. P5.5 evaluates all 3 P5.3 profiles x all 3 maps as a frozen 9-combination set.",
    }
    for name, expected in EXPECTED.items():
        got = [float(c["candidate_maps"][name]["multipliers"][state]) for state in STATE_ORDER]
        assert got == expected


def test_all_maps_are_monotone_bounded_and_preserve_late_bull_participation() -> None:
    c = json.loads(CONTRACT.read_text())
    for spec in c["candidate_maps"].values():
        values = [float(spec["multipliers"][state]) for state in STATE_ORDER]
        assert values[0] == 1.0
        assert values[-1] == 0.0
        assert all(0.0 <= value <= 1.0 for value in values)
        assert all(a >= b for a, b in zip(values, values[1:]))
        assert float(spec["multipliers"]["LATE_BULL_ROTATION"]) > 0.0


def test_composition_can_only_reduce_upstream_total_gross_and_not_relative_ranking() -> None:
    c = json.loads(CONTRACT.read_text())
    comp = c["composition_rule"]
    assert comp["formula"] == "p5_4_target_asset_weight = frozen_upstream_p4_1_brrk_target_asset_weight * cycle_gross_multiplier(MARKET_STATE)"
    assert comp["gross_formula"] == "p5_4_target_gross = frozen_upstream_p4_1_target_gross * cycle_gross_multiplier(MARKET_STATE)"
    assert comp["relative_ranking_unchanged"] is True
    assert comp["cycle_layer_can_increase_upstream_gross"] is False
    assert comp["freed_risk_budget_goes_to_cash"] is True
    assert comp["shorts_added"] is False
    assert comp["leverage_above_one_added"] is False


def test_data_insufficient_and_permission_boundaries_are_exact() -> None:
    c = json.loads(CONTRACT.read_text())
    di = c["data_insufficient_rule"]
    assert di["market_state"] == "DATA_INSUFFICIENT"
    assert di["mapping_defined"] is False
    assert di["p5_5_matched_economic_start"] == "2021-01-17"

    permission = c["risk_permission_boundary"]
    assert float(permission["flat_market_multiplier"]) == 0.0
    assert permission["actual_zero_exposure_requires_lock"] is True
    assert permission["lock_state"] == "LOCKED_PENDING_HUMAN_APPROVAL"
    assert permission["market_state_recovery_can_unlock"] is False
    assert permission["automatic_live_reentry_forbidden"] is True
    assert "RESEARCH_HYPOTHETICAL_REENTRY" in permission["research_economic_reentry_semantics"]
    assert permission["production_unlock_authority"] == "EXPLICIT_HUMAN_APPROVAL_ONLY"


def test_p5_5_handoff_is_frozen_nine_combinations_and_fail_stop() -> None:
    c = json.loads(CONTRACT.read_text())
    handoff = c["p5_5_handoff"]
    assert handoff["frozen_profile_set"] == ["EARLY", "BALANCED", "CONSERVATIVE"]
    assert handoff["frozen_map_set"] == ["DE_RISK_ONLY", "PROGRESSIVE", "EARLY_DEFENSIVE"]
    assert handoff["joint_candidate_count"] == 9
    assert handoff["baseline_without_cycle_overlay_required"] is True
    assert handoff["winner_selection_in_p5_4_forbidden"] is True
    assert handoff["winner_selection_owner"] == "P5.5"
    assert handoff["fail_stop_if_no_robust_candidate"] is True


def test_p5_4_has_no_selection_or_production_authority() -> None:
    c = json.loads(CONTRACT.read_text())
    assert c["selection"] == {
        "profile_selected": False,
        "behavior_map_selected": False,
        "production_behavior_selected": False,
        "production_authorized": False,
        "status": "FIXED_CANDIDATES_ONLY",
    }
    forbidden = set(c["forbidden"])
    assert "select a P5.3 profile in P5.4" in forbidden
    assert "select a winning P5.4 map before P5.5" in forbidden
    assert "add a fourth map after seeing P5.5 economics" in forbidden
    assert "allow any multiplier above 1.0" in forbidden
    assert "let MARKET_STATE recovery automatically unlock live risk" in forbidden
    assert "authorize production" in forbidden
