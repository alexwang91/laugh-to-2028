import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "research" / "cycle_exit" / "p5_5_validation_contract.json"
R1 = ROOT / "research" / "cycle_exit" / "p5_5_validation_contract_r1.json"
V2_DIGEST = ROOT / "research" / "results" / "p5_3_v2_market_state" / "summary.sha256"


def load(path):
    return json.loads(path.read_text())


def test_contract_identity_and_pre_result_freeze():
    c = load(BASE)
    assert c["contract_id"] == "P5.5-JOINT-PROFILE-MAP-VALIDATION-V1"
    assert c["status"] == "PREREGISTERED_BEFORE_ANY_P5_5_CANDIDATE_ECONOMICS"
    assert c["base_main"] == "a03b575ccc9cfce38590f05b1a76b5f62d46d863"
    assert c["production_authorized"] is False
    assert V2_DIGEST.read_text().strip() == c["upstream"]["p5_3_v2_result_summary_sha256"]


def test_candidate_set_is_exactly_canonical_12():
    c = load(BASE)["candidate_set"]
    assert c["profiles"] == ["EARLY", "BALANCED", "CONSERVATIVE"]
    assert c["behavior_maps"] == ["HARD_ONLY", "GENTLE", "BALANCED", "DEFENSIVE"]
    assert c["promotable_combinations"] == 12
    assert c["non_promotable_comparator"] == "BRRK_NO_CYCLE_CONTROL"


def test_does_not_fabricate_pre_brrk_economics():
    c = load(BASE)
    econ = c["evaluation_layers"]["authoritative_brrk_economics"]
    assert econ["evaluation_session_start"] == "2022-12-10"
    assert econ["first_decision_date"] == "2022-12-09"
    assert econ["cost_bps_per_abs_weight_change"] == [5.0, 10.0, 20.0, 50.0]
    assert econ["rebalance_band_l1"] == 0.05
    assert "No 2021 BRRK economic path may be fabricated" in econ["reason"]
    assert c["evaluation_layers"]["all_event_behavior_diagnostics"]["uses_candidate_returns"] is False


def test_objective_is_cagr_under_constraints_not_min_drawdown():
    c = load(BASE)
    assert "Maximize long-run after-cost compounded wealth/CAGR" in c["objective"]
    assert c["selection_rule"]["primary"] == "highest 5 bps after-cost CAGR"
    assert c["selection_rule"]["no_eligible_candidate"] == "NO_PROMOTION / FAIL_STOP"
    assert c["selection_rule"]["production_authorized"] is False


def test_event_behavior_gates_preserve_terminal_second_wind_and_false_flat():
    g = load(BASE)["event_behavior_gates"]
    assert g["terminal_2021_target_lead_mean_multiplier_max"] == 0.90
    assert g["terminal_2021_near_event_mean_multiplier_max"] == 0.90
    assert g["second_wind_2021_near_event_mean_multiplier_min"] == 0.85
    assert g["second_wind_2025_near_event_mean_multiplier_min"] == 0.70
    assert g["false_flat_2021_must_remain_present"] is True
    assert g["false_flat_2021_max_market_state_episode_days"] == 10


def test_start_and_event_holdout_robustness_are_frozen():
    c = load(BASE)
    assert c["start_date_robustness"]["starts"] == ["2022-12-10", "2023-06-01", "2024-01-01", "2025-01-01"]
    assert c["start_date_robustness"]["cost_bps"] == 5.0
    assert len(c["event_held_out_robustness"]["economic_window_events"]) == 6
    assert c["broad_policy_robustness"]["map_order"] == ["HARD_ONLY", "GENTLE", "BALANCED", "DEFENSIVE"]


def test_r1_fixes_only_drawdown_sign_semantics_before_results():
    r = load(R1)
    assert r["amendment_id"] == "P5.5-JOINT-PROFILE-MAP-VALIDATION-V1-R1"
    assert r["status"] == "FROZEN_BEFORE_ANY_P5_5_CANDIDATE_ECONOMICS"
    assert r["result_observed_before_amendment"] is False
    s = r["replacement_semantics"]
    assert s["at_5bps_max_drawdown_absolute_worsening_max"] == 0.01
    assert s["at_10bps_max_drawdown_absolute_worsening_max"] == 0.01
    assert s["minimum_usefulness_drawdown_improvement_min"] == 0.02
    assert r["production_authorized"] is False


def test_forbidden_rules_block_post_result_rescue_and_live_authority():
    text = "\n".join(load(BASE)["forbidden"])
    for phrase in [
        "change P5.4 multiplier values after observing P5.5 economics",
        "add a new candidate after observing P5.5 economics",
        "fabricate BRRK target economics before 2022-12-10",
        "drop the 2021 false FLAT",
        "authorize production/live trading",
    ]:
        assert phrase in text
