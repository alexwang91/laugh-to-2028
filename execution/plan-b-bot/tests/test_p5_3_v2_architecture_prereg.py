from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_v2_architecture_contract.json"
V1_CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_state_model_contract.json"
V1_EVIDENCE_CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_state_path_evidence_contract.json"
V1_RESULT = ROOT / "research" / "results" / "p5_3_state_paths"
P52_DIGEST = ROOT / "research" / "results" / "p5_2_feature_evidence" / "summary.sha256"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def test_v2_dependencies_bind_exactly_to_immutable_v1_and_p52() -> None:
    c = json.loads(CONTRACT.read_text())
    d = c["immutable_dependencies"]
    assert c["contract_id"] == "P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2"
    assert c["status"] == "FROZEN_BEFORE_V2_STATE_PATH_EVALUATION"
    assert c["base_main"] == "5b0cac61a45c13d28680e641dd434db4d9a6a2db"
    assert c["study_type"] == "ARCHITECTURE_ISOLATION_ONLY"
    assert d["v1_state_model_contract_git_blob_sha"] == _git_blob_sha(V1_CONTRACT)
    assert d["v1_state_path_evidence_contract_git_blob_sha"] == _git_blob_sha(V1_EVIDENCE_CONTRACT)
    assert d["p5_2_summary_sha256"] == P52_DIGEST.read_text().strip()
    assert d["v1_result_summary_sha256"] == (V1_RESULT / "summary.sha256").read_text().strip()
    assert d["v1_result_summary_sha256"] == "a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f"
    assert d["v1_result_commit"] == "7703b3ffec906a9d2ea58b33ee7feea5cd2f0a89"


def test_v2_preserves_v1_signal_layer_exactly() -> None:
    c = json.loads(CONTRACT.read_text())
    inherit = c["signal_layer_inheritance"]
    assert inherit == {
        "inherit_exactly_from_v1": True,
        "runtime_feature_inputs_unchanged": True,
        "evidence_atoms_unchanged": True,
        "raw_candidate_priority_unchanged": True,
        "causal_percentile_normalization_unchanged": True,
        "profiles_and_thresholds_unchanged": True,
        "persistence_and_clear_period_values_unchanged": True,
        "missing_data_semantics_unchanged_except_flat_is_no_longer_absorbing_market_state": True,
        "raw_candidate_and_atom_parity_required_vs_v1": True,
    }
    v1 = json.loads(V1_CONTRACT.read_text())
    assert c["profiles"] == v1["profiles"]


def test_v2_separates_market_state_from_permission_lock() -> None:
    c = json.loads(CONTRACT.read_text())
    market = c["architecture_layers"]["MARKET_STATE"]
    permission = c["architecture_layers"]["RISK_PERMISSION_LOCK"]
    assert market["state_vocabulary"] == market["severity_order"]
    assert market["state_vocabulary"][-1] == "FLAT"
    assert market["flat_absorbing"] is False
    assert market["authority"] == "RESEARCH_CLASSIFICATION_ONLY"
    assert permission["states"] == ["UNLOCKED", "LOCKED_PENDING_HUMAN_APPROVAL"]
    assert permission["market_state_has_unlock_authority"] is False
    assert permission["automatic_unlock_forbidden"] is True
    assert permission["unlock_authority"] == "EXPLICIT_HUMAN_APPROVAL_ONLY"
    assert "does not simulate a historical permission-lock path" in permission["research_simulation_rule"]


def test_v2_changes_only_flat_market_state_absorption() -> None:
    c = json.loads(CONTRACT.read_text())
    delta = c["market_state_transition_delta_from_v1"]
    assert "Remove the V1 current_state != FLAT exclusion" in delta["single_architecture_change"]
    assert "profile.deescalation_clear_days" in delta["flat_recovery_rule"]
    assert "exactly one severity step to DE_RISK_2" in delta["flat_recovery_rule"]
    assert "fresh profile.deescalation_clear_days streak" in delta["flat_recovery_rule"]
    assert "zero authority" in delta["permission_independence_rule"]
    unchanged = set(delta["unchanged_rules"])
    assert "same immediate fully-evaluated raw FLAT escalation" in unchanged
    assert "same one-severity-step de-escalation after each fresh clear period" in unchanged


def test_v2_must_reproduce_false_flat_and_v1_raw_evidence() -> None:
    c = json.loads(CONTRACT.read_text())
    failure = c["v1_failure_must_remain_visible"]
    assert failure["false_flat_date"] == "2021-02-23"
    assert failure["event_id"] == "P5C-2021-JAN-FEB-HIGH-VOL"
    assert failure["event_class"] == "HIGH_VOLATILITY_NON_TOP_CONTROL"
    assert abs(float(failure["near_event_flat_fraction_v1"]) - 6.0 / 7.0) < 1e-12
    parity = c["pre_run_parity_requirements"]
    assert all(parity.values())


def test_v2_architecture_pass_is_not_signal_or_production_promotion() -> None:
    c = json.loads(CONTRACT.read_text())
    evaluation = c["architecture_evaluation"]
    assert evaluation["p5_4_status_until_v2_closeout"] == "BLOCKED"
    assert "all pre-run parity requirements pass" in evaluation["architecture_pass_requires"]
    assert "the 2021-02-23 false raw FLAT remains present" in evaluation["architecture_pass_requires"]
    assert "signal quality is accepted" in evaluation["architecture_pass_does_not_mean"]
    assert "production is authorized" in evaluation["architecture_pass_does_not_mean"]
    selection = c["selection"]
    assert selection == {
        "profile_selected": False,
        "production_state_model_selected": False,
        "p5_4_mapping_selected": False,
        "production_authorized": False,
        "status": "PREREGISTRATION_ONLY",
    }


def test_v2_forbidden_set_prevents_post_result_rescue() -> None:
    c = json.loads(CONTRACT.read_text())
    forbidden = set(c["forbidden"])
    required = {
        "modify or rerun immutable P5.3 V1 result",
        "change P5.1 events, anchors or buckets",
        "change P5.2 immutable evidence",
        "add or remove V1 runtime signal features",
        "change V1 evidence atoms or raw candidate priority",
        "change V1 percentile thresholds or normalization",
        "change EARLY/BALANCED/CONSERVATIVE profile values",
        "change persistence or clear-period values",
        "hide, relabel or tune away the 2021-02-23 false raw FLAT",
        "allow MARKET_STATE recovery to unlock operational risk",
        "select P5.4 gross-risk multipliers",
        "authorize production",
    }
    assert required <= forbidden
