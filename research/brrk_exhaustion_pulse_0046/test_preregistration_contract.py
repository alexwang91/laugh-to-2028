from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RID = "BRRK-EXHAUSTION-PULSE-0046"
DATASET_ID = "BRRK-EXHAUSTION-0046-EXPOSED-HIST-V1"
EXPOSURE_ID = "BRRK-EXHAUSTION-PULSE-0046-DEVELOPMENT-DATA-REGISTRATION-20260810T161900Z"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_record():
    registry = _load(ROOT / "config" / "research_registry.json")
    matches = [r for r in registry["records"] if r.get("research_id") == RID]
    assert len(matches) == 1
    return matches[0]


def test_formal_preregistration_matches_central_record_exactly():
    prereg = _load(HERE / "PREREGISTRATION.json")
    assert prereg == _registry_record()
    assert prereg["governance_mode"] == "PROGRAM_GOVERNED_V1"
    assert prereg["created_before_result"] is True
    assert prereg["result_status"] == "PREREGISTERED_NOT_RUN"
    assert prereg["declared_variant_budget"] == 1
    assert prereg["actual_variants_evaluated"] == 0
    assert prereg["parameter_candidate_count"] == 1
    assert prereg["production_authorized"] is False
    assert prereg["governed_path_prefixes"] == ["research/brrk_exhaustion_pulse_0046/"]


def test_dataset_declaration_matches_central_exposure_registry_exactly():
    declaration = _load(HERE / "DATASET_DECLARATION.json")
    registry = _load(ROOT / "config" / "dataset_exposure_registry.json")
    slices = [x for x in registry["dataset_slices"] if x.get("dataset_slice_id") == DATASET_ID]
    events = [x for x in registry["exposure_events"] if x.get("exposure_id") == EXPOSURE_ID]
    assert len(slices) == 1
    assert len(events) == 1
    assert declaration["dataset_slice"] == slices[0]
    assert declaration["exposure_event"] == events[0]
    assert slices[0]["end"] == "2026-08-02T00:00:00Z"
    assert slices[0]["data_budget"] == "DEVELOPMENT"
    assert slices[0]["contamination_state"] == "RESEARCHER_EXPOSED_HISTORY"
    assert slices[0]["researcher_exposed_history"] is True


def test_frozen_detector_parameters_and_firewall_are_present():
    prereg = _load(HERE / "PREREGISTRATION.json")
    params = set(prereg["research_process_complexity"]["declared_parameter_candidates"])
    required = {
        "PRIMARY_AXES=S1_S2_S3_S4_FIXED_FROM_0044",
        "PRECHANGE_BASELINE=OLS_64",
        "CHANGE_AGE_SCAN=3_TO_32_INCLUSIVE",
        "AXIS_SCORE=ONE_SIDED_SLOPE_WORKING_GLR",
        "SUBSET_AGGREGATION=ALL_15_NONEMPTY_SUBSETS_EQUAL_WEIGHT",
        "NULL_MODEL=VAR1_OLS_INTERCEPT",
        "NULL_RESIDUAL_BOOTSTRAP=CIRCULAR_MOVING_BLOCK_LENGTH_7",
        "NULL_PATHS=5000",
        "NULL_SEED=460046",
        "NULL_BURN_IN=256",
        "NULL_PATH_LENGTH=1460",
        "ARL0_TRUNC_TARGET=365",
        "THRESHOLD_BISECTION_ITERATIONS=60",
        "PULSE=THRESHOLD_UPCROSSING_ONLY",
        "EVENT_CLUSTER_BOOTSTRAP=10000_SEED_460047",
        "DAILY_BLOCK_BOOTSTRAP=10000_BLOCK21_SEED_460048",
    }
    assert required <= params
    decisions = "\n".join(prereg["researcher_decisions"])
    assert "CALIBRATION_LOCK" in decisions
    assert "must not access TRUE_EXHAUSTION/CONTINUATION/AMBIGUOUS labels" in decisions
    assert "spectral radius is >=1" in decisions
    assert "seed 460046" in decisions
    assert "5,000 null paths" in decisions
    assert "Transition Pulse P_t is an upcrossing" in decisions
    assert "There is no WATCH/RISK state" in decisions


def test_parent_evidence_remains_immutable_and_0045_does_not_create_dynamic_gross():
    registry = _load(ROOT / "config" / "research_registry.json")
    by_id = {r.get("research_id"): r for r in registry["records"]}
    assert by_id["BRRK-EXHAUSTION-STATE-0044"]["result_status"] == "PASS_TRIGGER_STAGE_ELIGIBLE"
    assert by_id["BRRK-EXHAUSTION-TRIGGER-0045"]["result_status"] == "FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY"
    assert (ROOT / "research" / "brrk_exhaustion_state_0044" / "RUN_ONCE.marker").exists()
    assert (ROOT / "research" / "brrk_exhaustion_trigger_0045" / "RUN_ONCE.marker").exists()
    forbidden_text = "\n".join(_registry_record()["forbidden_followup"])
    assert "A 0046 PASS does not create dynamic-gross eligibility" in forbidden_text


def test_preregistration_stage_has_no_runner_lock_or_result_files():
    forbidden = {
        "run_once.py",
        "RUN_INTERFACE.json",
        "CALIBRATION_LOCK",
        "CALIBRATION_LOCK.json",
        "PRIMARY_RESULT.json",
        "EXECUTION.json",
        "RUN_ONCE.marker",
        "RESULT.md",
    }
    existing = {p.name for p in HERE.iterdir() if p.is_file()}
    assert forbidden.isdisjoint(existing)


def test_zero_authority_and_no_portfolio_translation():
    prereg = _load(HERE / "PREREGISTRATION.json")
    all_text = json.dumps(prereg, sort_keys=True)
    assert prereg["production_authorized"] is False
    assert "No same-ID gross mapping" in all_text
    assert "No same-ID gross mapping, portfolio weights" in all_text
    assert "Phase 6 modification" in all_text
    assert "signing" in all_text
    assert "order submission" in all_text
