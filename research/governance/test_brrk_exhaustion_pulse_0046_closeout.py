from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "research/brrk_exhaustion_pulse_0046"
RID = "BRRK-EXHAUSTION-PULSE-0046"
FAIL = "FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_0046_central_registry_is_closed_fail_once_only():
    registry = _load(ROOT / "config/research_registry.json")
    matches = [r for r in registry["records"] if r.get("research_id") == RID]
    assert len(matches) == 1
    record = matches[0]
    assert record["governance_mode"] == "PROGRAM_GOVERNED_V1"
    assert record["declared_variant_budget"] == 1
    assert record["actual_variants_evaluated"] == 1
    assert record["result_status"] == FAIL
    assert record["promotion_state"] == "NONE"
    assert record["production_authorized"] is False


def test_0046_permanent_result_execution_and_marker_bind_valid_run():
    result = _load(PATH / "PRIMARY_RESULT.json")
    execution = _load(PATH / "EXECUTION.json")
    marker = _load(PATH / "RUN_ONCE.marker")
    assert result["result_status"] == FAIL
    assert result["valid_result_workflow"]["run_id"] == 31419044159
    assert result["valid_result_workflow"]["head_sha"] == "88f7c7e769352ea9d7b4cac881d2836678576b8e"
    assert result["full_artifact_binding"]["artifact_id"] == 9074623455
    assert result["full_artifact_binding"]["artifact_digest"] == "sha256:2938e8c0a776255848b13990200cd77bec85ab15e143596a477fc08f3b63c2a0"
    assert result["full_artifact_binding"]["full_primary_result_file_sha256"] == "5c0e9aa4864b0044d5033573be78cdee3c0802db2d8b98d24fc0afcc21abbf8c"
    assert execution["unique_valid_historical_result_count"] == 1
    assert execution["run_1"]["research_result_released"] is False
    assert execution["valid_result_run"]["run1_full_calibration_reproduced_before_labels"] is True
    assert marker["valid_result_run_id"] == 31419044159
    assert marker["result_status"] == FAIL
    assert marker["SAME_ID_RERUN_ALLOWED"] is False
    assert marker["SAME_ID_RESCUE_ALLOWED"] is False


def test_0046_binding_negative_gates_are_preserved():
    result = _load(PATH / "PRIMARY_RESULT.json")
    metrics = result["point_metrics"]
    assert metrics["primary_true_PRE14_7"]["numerator"] == 0
    assert metrics["primary_true_PRE14_7"]["denominator"] == 9
    assert metrics["primary_true_episode_PRE14_7"]["numerator"] == 0
    assert metrics["primary_true_episode_PRE14_7"]["denominator"] == 5
    assert metrics["severe_true_PRE14_7"]["numerator"] == 0
    assert metrics["severe_true_PRE14_7"]["denominator"] == 7
    assert metrics["primary_true_PRE21_0_onsets"]["count"] == 0
    assert result["alarm_path"]["total_pulse_count"] == 1
    assert result["alarm_path"]["pulse_dates"] == ["2025-11-22"]
    assert result["gates"]["primary_true_event_PRE14_7_ge_0_50"]["pass"] is False
    assert result["gates"]["primary_true_episode_PRE14_7_ge_0_60"]["pass"] is False
    assert result["gates"]["severe_true_event_PRE14_7_ge_0_57"]["pass"] is False
    assert result["gates"]["primary_true_PRE21_0_onsets_ge_4"]["pass"] is False
    assert result["gates"]["raw_alarm_occupancy_le_0_175"]["pass"] is True
    assert result["gates"]["calibration_arl0_ge_365"]["pass"] is True


def test_0046_run1_calibration_and_repair_history_are_not_erased():
    result = _load(PATH / "PRIMARY_RESULT.json")
    execution = _load(PATH / "EXECUTION.json")
    assert result["run1_infrastructure_failure"]["run_id"] == 31417259266
    assert result["run1_infrastructure_failure"]["artifact_count"] == 0
    assert result["calibration_reproduction"]["run1_lock_hash_reproduced"] == "cba7aa3406c58ec80e391c389ea076439912d6bc3abecdfb89911739be1f2445"
    assert execution["repair"]["pr"] == 165
    assert execution["repair"]["detector_changed"] is False
    assert execution["repair"]["calibration_changed"] is False
    assert execution["repair"]["hard_gates_changed"] is False
    assert execution["repair"]["denominators_changed"] is False


def test_0046_zero_authority_and_no_persisted_calibration_inputs():
    result = _load(PATH / "PRIMARY_RESULT.json")
    authority = result["authority"]
    assert authority["future_only_pulse_validation_stage_eligible"] is False
    assert authority["dynamic_gross_stage_eligible"] is False
    assert authority["portfolio_economics_executed"] is False
    assert authority["canonical_strategy_changed"] is False
    assert authority["phase6_observation_changed"] is False
    assert authority["production_authorized"] is False
    assert authority["signature_authorized"] is False
    assert authority["order_submission_authorized"] is False
    assert not (PATH / "PREDICTOR_PATH.json").exists()
    assert not (PATH / "CALIBRATION_LOCK.json").exists()


def test_temporary_result_and_metadata_workflows_are_not_part_of_final_tree():
    workflows = ROOT / ".github/workflows"
    forbidden = {
        "brrk-exhaustion-pulse-0046-once.yml",
        "brrk-exhaustion-pulse-0046-once-v2.yml",
        "brrk-exhaustion-pulse-0046-closeout-metadata-once.yml",
        "brrk-exhaustion-pulse-0046-closeout-cleanup-once.yml",
        "brrk-exhaustion-pulse-0046-closeout-finalize-once.yml",
    }
    existing = {p.name for p in workflows.iterdir() if p.is_file()}
    assert forbidden.isdisjoint(existing)
