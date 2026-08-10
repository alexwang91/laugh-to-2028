from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RID = "BRRK-BETA-HANDOFF-EVENT-STUDY-0047"
DATASET_ID = "BRRK-BETA-HANDOFF-0047-EXPOSED-HIST-V1"
EXPOSURE_ID = "BRRK-BETA-HANDOFF-0047-DEVELOPMENT-DATA-REGISTRATION-20260810T232616Z"
DESIGN = ROOT / "research" / "governance" / "BRRK_BETA_HANDOFF_EVENT_STUDY_0047_DESIGN_FREEZE_2026-08-11.md"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_record():
    registry = _load(ROOT / "config" / "research_registry.json")
    matches = [r for r in registry["records"] if r.get("research_id") == RID]
    assert len(matches) == 1
    return matches[0]


def test_design_boundary_exists_and_formal_prereg_matches_central_record_exactly():
    assert DESIGN.exists()
    design_text = DESIGN.read_text(encoding="utf-8")
    assert "DESIGN FROZEN / NOT PREREGISTERED / NOT RUN" in design_text
    assert "398b7ec3f78f602461787b1b45e8d5041729e126" not in design_text  # design predates merge SHA

    prereg = _load(HERE / "PREREGISTRATION.json")
    assert prereg == _registry_record()
    assert prereg["governance_mode"] == "PROGRAM_GOVERNED_V1"
    assert prereg["objective_type"] == "MECHANISM_TEST"
    assert prereg["research_domain"] == "RELATIVE_VALUE"
    assert prereg["created_before_result"] is True
    assert prereg["result_status"] == "PREREGISTERED_NOT_RUN"
    assert prereg["declared_variant_budget"] == 1
    assert prereg["actual_variants_evaluated"] == 0
    assert prereg["parameter_candidate_count"] == 1
    assert prereg["production_authorized"] is False
    assert prereg["governed_path_prefixes"] == ["research/brrk_beta_handoff_0047/"]


def test_dataset_declaration_matches_central_registry_exactly_and_is_exposed_development():
    declaration = _load(HERE / "DATASET_DECLARATION.json")
    registry = _load(ROOT / "config" / "dataset_exposure_registry.json")
    slices = [x for x in registry["dataset_slices"] if x.get("dataset_slice_id") == DATASET_ID]
    events = [x for x in registry["exposure_events"] if x.get("exposure_id") == EXPOSURE_ID]
    assert len(slices) == 1
    assert len(events) == 1
    assert declaration["dataset_slice"] == slices[0]
    assert declaration["exposure_event"] == events[0]
    assert slices[0]["assets"] == ["BTC", "ETH", "SOL"]
    assert slices[0]["start"] == "2020-08-01T00:00:00Z"
    assert slices[0]["end"] == "2026-08-02T00:00:00Z"
    assert slices[0]["data_budget"] == "DEVELOPMENT"
    assert slices[0]["contamination_state"] == "RESEARCHER_EXPOSED_HISTORY"
    assert slices[0]["researcher_exposed_history"] is True
    assert events[0]["result_informed_followup"] is True


def test_frozen_method_families_are_present_without_candidate_tournament():
    prereg = _load(HERE / "PREREGISTRATION.json")
    params = set(prereg["research_process_complexity"]["declared_parameter_candidates"])
    required = {
        "UNIVERSE=BTC_ETH_SOL",
        "TREND_HORIZONS=20_60_120_240",
        "FAST_WEIGHTS=0.15_0.25_0.30_0.30",
        "SLOW_WEIGHTS=0.10_0.20_0.30_0.40",
        "BTC_POSITIVE_EPISODE=MAX_CONTIGUOUS_BTC_FAST_GTE_0",
        "RELATIVE_ACCEL=REL_FAST_MINUS_REL_SLOW",
        "BETA_BREADTH=TWO_ASSET_ABSFAST_AND_RELFAST_POSITIVE_SHARE",
        "PARTICIPATION=LOG_TRADES_MINUS_TRAILING60_MEDIAN",
        "REALIZED_TARGET_HORIZONS=20_60",
        "PRIMARY_EVENT=EARLIEST_DURABLE_HANDOFF_PER_EPISODE",
        "CROSS_CORRELATION_LAGS=-14_TO_14",
        "TRANSMISSION_MODEL=POOLED_EPISODE_PRESERVING_VAR7_WITH_EPISODE_INTERCEPTS",
        "GRANGER_PANEL=ALL_SIX_DIRECTED_PAIRS",
        "IRF=GENERALIZED_BTC_SHOCK_HORIZONS_0_TO_14",
        "EPISODE_BOOTSTRAP=10000_SEED_470047",
        "ORACLE=ONE_SWITCH_BTC_TO_ETH_OR_SOL_5BPS_PER_ABS_WEIGHT_CHANGE",
    }
    assert required <= params
    assert prereg["research_process_complexity"]["actual_parameter_candidates_evaluated"] == []
    assert prereg["actual_variants_evaluated"] == 0


def test_hindsight_target_is_separate_and_censoring_is_not_negative():
    text = "\n".join(_load(HERE / "PREREGISTRATION.json")["researcher_decisions"])
    assert "same Beta asset to strictly beat BTC and the other Beta asset at both horizons" in text
    assert "BTC forward return>0 at both horizons" in text
    assert "right-censored/target-unavailable rather than negative" in text
    assert "earliest target-available durable handoff date" in text


def test_transmission_and_uncertainty_preserve_episode_dependence():
    prereg = _load(HERE / "PREREGISTRATION.json")
    text = "\n".join(prereg["researcher_decisions"])
    assert "lags exactly -14 through +14" in text
    assert "VAR(7)" in text
    assert "all six directed pairs" in text
    assert "Generalized rather than Cholesky-ordered" in text
    assert "10,000 times with seed 470047" in text
    assert "not treated as independent observations" in text


def test_oracle_is_firewalled_and_not_a_gate():
    prereg = _load(HERE / "PREREGISTRATION.json")
    text = json.dumps(prereg, sort_keys=True)
    assert "HINDSIGHT_OPPORTUNITY_BOUND / NOT_TRADABLE / NOT_OOS" in text
    assert "never a hard PASS gate" in text
    assert "No use of the hindsight one-switch oracle to choose labels" in text


def test_preregistration_stage_has_no_runner_model_or_result_files():
    forbidden = {
        "run_once.py",
        "RUN_INTERFACE.json",
        "PRIMARY_RESULT.json",
        "EXECUTION.json",
        "RUN_ONCE.marker",
        "RESULT.md",
        "handoff_model.py",
        "hazard_model.py",
    }
    existing = {p.name for p in HERE.iterdir() if p.is_file()}
    assert forbidden.isdisjoint(existing)


def test_portfolio_translation_and_authority_remain_forbidden():
    prereg = _load(HERE / "PREREGISTRATION.json")
    all_text = json.dumps(prereg, sort_keys=True)
    assert prereg["production_authorized"] is False
    assert "No same-ID 40/60, 20/80, 0/100" in all_text
    assert "No same-ID CAGR" in all_text
    assert "No same-ID hazard model" in all_text
    assert "No canonical BRRK modification" in all_text
    assert "Phase 6 modification" in all_text
    assert "signing" in all_text
    assert "order submission" in all_text
