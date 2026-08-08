import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "research" / "cycle_exit" / "p5_4_behavior_mapping_contract.json"
V2_DIGEST = ROOT / "research" / "results" / "p5_3_v2_market_state" / "summary.sha256"


def load():
    return json.loads(CONTRACT.read_text())


def test_contract_is_preregistered_before_p5_5_economics():
    c = load()
    assert c["contract_id"] == "P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1"
    assert c["status"] == "PREREGISTERED_BEFORE_ANY_P5_5_ECONOMIC_EVALUATION"
    assert c["production_authorized"] is False
    assert V2_DIGEST.read_text().strip() == c["upstream"]["p5_3_v2_summary_sha256"]


def test_candidate_family_is_small_and_frozen():
    c = load()
    assert [x["id"] for x in c["candidate_maps"]] == ["HARD_ONLY", "GENTLE", "BALANCED", "DEFENSIVE"]
    assert c["p5_5_candidate_cartesian_product"]["total_promotable_combinations_before_validation"] == 12
    assert c["p5_5_candidate_cartesian_product"]["profiles"] == ["EARLY", "BALANCED", "CONSERVATIVE"]
    assert c["selection"] == {
        "profile_selected": False,
        "behavior_map_selected": False,
        "combination_selected": False,
        "production_authorized": False,
    }


def test_all_overlay_maps_are_monotone_and_never_above_one():
    c = load()
    order = c["state_order"]
    for candidate in c["candidate_maps"]:
        vals = [candidate["multipliers"][s] for s in order]
        assert vals[0] == 1.0
        assert all(0.0 <= v <= 1.0 for v in vals)
        assert all(a >= b for a, b in zip(vals, vals[1:]))
        assert candidate["multipliers"]["LATE_BULL_ROTATION"] > 0.0
        assert candidate["multipliers"]["FLAT"] == 0.0


def test_brrk_control_is_non_promotable_and_unscaled():
    c = load()
    comparator = c["non_promotable_comparator"]
    assert comparator["id"] == "BRRK_NO_CYCLE_CONTROL"
    assert set(comparator["multipliers"].values()) == {1.0}
    assert "never" in comparator["purpose"]


def test_mapping_only_scales_total_gross_not_relative_ranking():
    c = load()
    comp = c["composition"]
    assert comp["relative_ranking_change"] is False
    assert comp["new_asset_targets"] is False
    assert comp["gross_above_one_allowed"] is False
    assert "frozen_brrk_target" in comp["formula"]
    assert comp["data_insufficient_multiplier"] == 0.0


def test_reentry_is_research_counterfactual_not_permission():
    c = load()
    text = c["research_only_reentry_semantics"]
    assert "counterfactual" in text
    assert "does not unlock RISK_PERMISSION_LOCK" in text
    assert "not a production re-entry rule" in text


def test_forbidden_rules_prevent_post_result_grid_search():
    forbidden = "\n".join(load()["forbidden"])
    for text in [
        "change candidate numerical multipliers after P5.5 economic results",
        "add candidate maps after seeing P5.5 results",
        "select a P5.4 winner inside P5.4",
        "permit gross above 1.0",
        "alter BRRK relative asset ranking",
        "authorize production/live trading",
    ]:
        assert text in forbidden
