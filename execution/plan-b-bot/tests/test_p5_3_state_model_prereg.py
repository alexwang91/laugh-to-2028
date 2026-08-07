from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_state_model_contract.json"
TAXONOMY = ROOT / "research" / "cycle_exit" / "p5_1_event_taxonomy.json"
P52_SUMMARY = ROOT / "research" / "results" / "p5_2_feature_evidence" / "summary.json"
P52_DIGEST = ROOT / "research" / "results" / "p5_2_feature_evidence" / "summary.sha256"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def test_p5_3_contract_dependencies_are_immutable_and_exact() -> None:
    c = json.loads(CONTRACT.read_text())
    p52 = json.loads(P52_SUMMARY.read_text())

    assert c["contract_id"] == "P5.3-STATE-MODEL-STRUCTURE-V1"
    assert c["status"] == "FROZEN_BEFORE_STATE_PATH_EVALUATION"
    assert c["base_main"] == "4b5f41b449b2e9ac3d8ec9125644bc0a10e36963"
    assert c["dependencies"]["p5_1_taxonomy_git_blob_sha"] == _git_blob_sha(TAXONOMY)
    assert c["dependencies"]["p5_2_result_summary_sha256"] == P52_DIGEST.read_text().strip()
    assert P52_DIGEST.read_text().strip() == "3f6dc3c512d22ac8f71d43ed155f2602cd40d5caf3d617c0e130e170727e0627"
    assert p52["status"] == "ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE"
    assert p52["selection"]["feature_set_selected"] is False
    assert p52["selection"]["state_thresholds_selected"] is False
    assert p52["production_authorized"] is False


def test_state_vocabulary_and_product_boundaries_are_exact() -> None:
    c = json.loads(CONTRACT.read_text())
    assert c["states"] == [
        "NORMAL_BULL",
        "BTC_LEADERSHIP_MATURING",
        "LATE_BULL_ROTATION",
        "EXHAUSTION_WATCH",
        "DE_RISK_1",
        "DE_RISK_2",
        "FLAT",
    ]
    integrity = c["research_integrity"]
    assert integrity["no_single_indicator_top_switch"] is True
    assert integrity["late_bull_rotation_not_automatically_bearish"] is True
    assert integrity["only_one_explicit_terminal_event_acknowledged"] is True
    assert integrity["no_missing_source_proxy_laundering"] is True
    assert integrity["brrk_relative_ranking_unchanged"] is True
    assert integrity["production_authorization"] == "NONE"
    assert c["transition_rules"]["flat_absorbing"] is True
    assert c["transition_rules"]["flat_exit"] == "EXPLICIT_HUMAN_APPROVAL_REQUIRED_OUTSIDE_P5.3"


def test_profiles_are_frozen_ordered_sensitivity_not_post_result_free_parameters() -> None:
    c = json.loads(CONTRACT.read_text())
    p = c["profiles"]
    assert list(p) == ["EARLY", "BALANCED", "CONSERVATIVE"]
    assert p["EARLY"] == {
        "moderate_high_percentile": 0.65,
        "strong_high_percentile": 0.80,
        "moderate_low_percentile": 0.35,
        "strong_low_percentile": 0.20,
        "escalation_persistence_days": 2,
        "deescalation_clear_days": 5,
    }
    assert p["BALANCED"] == {
        "moderate_high_percentile": 0.70,
        "strong_high_percentile": 0.85,
        "moderate_low_percentile": 0.30,
        "strong_low_percentile": 0.15,
        "escalation_persistence_days": 3,
        "deescalation_clear_days": 5,
    }
    assert p["CONSERVATIVE"] == {
        "moderate_high_percentile": 0.75,
        "strong_high_percentile": 0.90,
        "moderate_low_percentile": 0.25,
        "strong_low_percentile": 0.10,
        "escalation_persistence_days": 3,
        "deescalation_clear_days": 7,
    }
    assert p["EARLY"]["moderate_high_percentile"] < p["BALANCED"]["moderate_high_percentile"] < p["CONSERVATIVE"]["moderate_high_percentile"]
    assert p["EARLY"]["strong_high_percentile"] < p["BALANCED"]["strong_high_percentile"] < p["CONSERVATIVE"]["strong_high_percentile"]


def test_runtime_inputs_are_subset_of_immutable_p5_2_available_features() -> None:
    c = json.loads(CONTRACT.read_text())
    feature_panel = ROOT / "research" / "results" / "p5_2_feature_evidence" / "feature_panel.csv"
    header = feature_panel.read_text().splitlines()[0].split(",")
    available = set(header[1:])
    used = {f for family in c["runtime_feature_inputs"].values() for f in family}
    assert used <= available
    assert not (set(c["excluded_pending_inputs"]) & used)


def test_causal_normalization_and_missing_data_fail_closed() -> None:
    c = json.loads(CONTRACT.read_text())
    n = c["causal_normalization"]
    assert n == {
        "method": "TRAILING_EMPIRICAL_PERCENTILE",
        "lookback_completed_daily_observations": 365,
        "minimum_completed_observations": 252,
        "include_current_observation": True,
        "future_observations_allowed": False,
        "tie_method": "average",
        "missing_rule": "FAIL_CLOSED_NO_DEESCALATION",
    }
    assert "Missing required normalized evidence cannot cause de-escalation" in c["transition_rules"]["missing_data"]


def test_rotation_and_exhaustion_semantics_prevent_single_indicator_exit() -> None:
    c = json.loads(CONTRACT.read_text())
    atoms = c["evidence_atoms"]
    assert "not sufficient for de-risk" in atoms["MATURE_TEXTURE"]["purpose"]
    assert "not sufficient for de-risk alone" in atoms["ROTATION"]["purpose"]
    assert "At least 2 independent subchannels" in atoms["EXHAUSTION"]["rule"]
    priority = {x["state"]: x["rule"] for x in c["raw_candidate_state_priority"]}
    assert priority["FLAT"] == "STRONG_DAMAGE AND STRONG_EXHAUSTION"
    assert priority["DE_RISK_1"] == "DAMAGE AND EXHAUSTION"
    assert priority["LATE_BULL_ROTATION"] == "ROTATION AND NOT DAMAGE"
    assert priority["BTC_LEADERSHIP_MATURING"] == "MATURE_TEXTURE AND NOT DAMAGE"


def test_p5_3_does_not_claim_p5_4_or_production_authority() -> None:
    c = json.loads(CONTRACT.read_text())
    assert c["selection_rule"]["p5_3_final_production_state_model_selected"] is False
    forbidden = set(c["forbidden"])
    assert "select P5.4 gross multipliers" in forbidden
    assert "authorize production" in forbidden
    assert "automatically exit FLAT" in forbidden
