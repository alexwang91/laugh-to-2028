import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_state_model_v2_contract.json"
V1_RESULT_DIGEST = ROOT / "research" / "results" / "p5_3_state_paths" / "summary.sha256"


def load():
    return json.loads(CONTRACT.read_text())


def test_v2_is_new_preregistered_architecture_only():
    c = load()
    assert c["contract_id"] == "P5.3-STATE-MODEL-ARCHITECTURE-V2"
    assert c["status"] == "PREREGISTERED_BEFORE_ANY_V2_STATE_PATH_RUN"
    assert c["base_main"] == "5b0cac61a45c13d28680e641dd434db4d9a6a2db"
    assert c["production_authorized"] is False
    assert "Architecture isolation only" in c["scope"]


def test_v1_dependencies_and_immutable_digest_are_frozen():
    c = load()
    d = c["dependencies"]
    assert d["p5_3_v1_contract_git_blob_sha"] == "400ec97f8a0e522c5776ce1f6a98fc6d7e069267"
    assert d["p5_3_v1_engine_git_blob_sha"] == "4fd760440ae88c25070fa0cf1ee2d499cc89ab3f"
    assert d["p5_3_v1_result_commit"] == "7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89"
    digest = V1_RESULT_DIGEST.read_text().strip()
    assert digest == d["p5_3_v1_summary_sha256"]


def test_signal_semantics_are_explicitly_not_retuned():
    c = load()
    frozen = "\n".join(c["frozen_from_v1_without_change"])
    for required in [
        "runtime feature set",
        "causal percentile normalization",
        "MATURE_TEXTURE atom",
        "ROTATION atom",
        "EXHAUSTION atom",
        "STRONG_EXHAUSTION atom",
        "DAMAGE atom",
        "STRONG_DAMAGE atom",
        "raw candidate state priority",
        "EARLY profile",
        "BALANCED profile",
        "CONSERVATIVE profile",
    ]:
        assert required in frozen


def test_market_state_is_nonabsorbing_but_hard_flat_still_immediate():
    c = load()
    m = c["architecture"]["MARKET_STATE"]
    assert m["flat_absorbing"] is False
    assert "immediately" in m["hard_flat_entry"]
    assert "deescalation_clear_days" in m["flat_recovery"]
    assert "exactly one severity step" in m["flat_recovery"]


def test_permission_lock_remains_human_gated_and_absorbing_without_approval():
    c = load()
    lock = c["architecture"]["RISK_PERMISSION_LOCK"]
    assert lock["states"] == ["RISK_ADD_ALLOWED", "HUMAN_REAUTH_REQUIRED"]
    assert lock["automatic_unlock"] is False
    assert "Explicit human approval" in lock["unlock"]
    assert lock["production_authorization"] == "NONE"


def test_architecture_acceptance_requires_exact_v1_parity():
    c = load()
    g = c["architecture_acceptance_gates"]
    assert g["raw_candidate_parity_fraction"] == 1.0
    assert g["pre_first_flat_final_state_parity_fraction"] == 1.0
    assert g["v1_false_flat_must_remain_visible"] is True
    assert g["first_false_flat_date_must_equal"] == "2021-02-23"
    assert g["post_false_flat_nonflat_market_state_must_exist"] is True
    assert g["later_p5_1_events_must_be_classifiable"] is True
    assert g["no_profile_selection_in_v2_architecture_run"] is True
    assert g["no_behavior_multiplier_selection"] is True
    assert g["no_production_authorization"] is True


def test_forbidden_rules_prevent_post_result_rescue():
    forbidden = "\n".join(load()["forbidden"])
    for text in [
        "change any V1 feature",
        "change any V1 percentile threshold",
        "change any V1 atom rule",
        "change any V1 profile persistence",
        "hide or relabel the 2021-02-23 false FLAT",
        "select P5.4 gross-risk multipliers",
        "automatically unlock RISK_PERMISSION_LOCK",
        "authorize production",
    ]:
        assert text in forbidden
