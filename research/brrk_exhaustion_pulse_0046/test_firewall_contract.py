from __future__ import annotations

import inspect
import json
from pathlib import Path

from research.brrk_exhaustion_pulse_0046 import calibration, detector, predictor_io, run_once, state_input
from research.brrk_exhaustion_state_0044 import run_once as s0044

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "research/brrk_exhaustion_pulse_0046"


def test_calibration_module_has_no_raw_market_nav_or_taxonomy_import_path() -> None:
    src = inspect.getsource(calibration)
    forbidden = (
        "brrk_exhaustion_event_study",
        "brrk_exhaustion_state_0044",
        "load_market",
        "load_canonical",
        "detect_candidates",
        "classify_event",
        "reproduce_0043_taxonomy",
        "assign_macro_episodes",
        "TRUE_EXHAUSTION",
        "CONTINUATION_FALSE_TOP",
        "PRE14_7",
        "PRE14_0",
        "PRE21_0",
    )
    for token in forbidden:
        assert token not in src
    assert "read_predictor_artifact" in src


def test_predictor_materializer_does_not_call_taxonomy_functions() -> None:
    src = inspect.getsource(state_input)
    for token in ("detect_candidates", "classify_event", "reproduce_0043_taxonomy", "assign_macro_episodes"):
        assert token not in src
    assert "e0043.build_features" in src
    assert "e0043.load_market" in src
    assert "e0043.load_canonical" in src


def test_s1_s4_construction_exactly_matches_0044_constants() -> None:
    assert tuple(predictor_io.PRIMARY_AXES) == tuple(s0044.PRIMARY_AXES)
    for axis in predictor_io.PRIMARY_AXES:
        assert tuple(state_input.AXIS_FEATURES[axis]) == tuple(s0044.AXIS_FEATURES[axis])
    assert state_input.FROZEN_EVAL_END == s0044.FROZEN_EVAL_END


def test_run_once_validates_lock_before_dynamic_evaluation_import() -> None:
    src = inspect.getsource(run_once.evaluate)
    validate_pos = src.index("calibration.validate_lock")
    import_pos = src.index('importlib.import_module("research.brrk_exhaustion_pulse_0046.evaluation")')
    assert validate_pos < import_pos
    assert "RUN_ONCE.marker" in src


def test_frozen_detector_and_calibration_constants() -> None:
    assert detector.BASELINE_LENGTH == 64
    assert (detector.MIN_CHANGE_AGE, detector.MAX_CHANGE_AGE) == (3, 32)
    assert detector.AXIS_COUNT == 4
    assert detector.VAR_FLOOR == 1e-8
    assert calibration.NULL_SEED == 460046
    assert calibration.BLOCK_LENGTH == 7
    assert calibration.NULL_PATHS == 5000
    assert calibration.BURN_IN == 256
    assert calibration.PATH_LENGTH == 1460
    assert calibration.ARL0_TARGET == 365.0
    assert calibration.BISECTION_ITERATIONS == 60
    assert calibration.NO_CROSSING_CENSOR == 1461


def test_var1_fit_and_bootstrap_are_deterministic() -> None:
    rng = __import__("numpy").random.default_rng(7)
    x = rng.normal(size=(300, 4))
    fitted = calibration.fit_var1(x)
    assert float(fitted["spectral_radius"]) >= 0.0
    residuals = fitted["residuals_centered"]
    r1 = calibration._bootstrap_residuals(residuals, __import__("numpy").random.default_rng(460046), 2)
    r2 = calibration._bootstrap_residuals(residuals, __import__("numpy").random.default_rng(460046), 2)
    assert __import__("numpy").array_equal(r1, r2)
    assert r1.shape == (2, calibration.TOTAL_SIM_STEPS, 4)


def test_stopping_time_clock_and_censor_are_frozen() -> None:
    np = __import__("numpy")
    scores = np.array([[np.nan, 0.1, 2.0], [np.nan, np.nan, np.nan]])
    times = calibration.stopping_times(scores, 1.0)
    assert times.tolist() == [3, 1461]


def test_run_interface_is_pre_result_zero_authority() -> None:
    interface = json.loads((PATH / "RUN_INTERFACE.json").read_text(encoding="utf-8"))
    assert interface["status"] == "IMPLEMENTED_PRE_RESULT_NOT_RUN"
    assert interface["frozen_prereg_merge_commit"] == "48a140a1d58cba859d537e7dee0ad399c541527a"
    assert interface["candidate_count"] == 1
    assert interface["actual_variants_evaluated"] == 0
    assert interface["pre_result_green_sha"] is None
    assert interface["pre_result_implementation_clarifications"]["alarm_spell_p90"] == "EMPIRICAL_NEAREST_RANK_CEIL_0_9_TIMES_N"
    authority = interface["authority"]
    for key in (
        "calibration_executed",
        "event_taxonomy_loaded_by_0046",
        "result_released",
        "future_only_pulse_validation_stage_eligible",
        "dynamic_gross_stage_eligible",
        "gross_mapping_defined",
        "portfolio_economics_executed",
        "canonical_strategy_changed",
        "phase6_observation_changed",
        "production_authorized",
        "signature_authorized",
        "order_submission_authorized",
    ):
        assert authority[key] is False


def test_pre_result_branch_contains_no_generated_predictor_lock_or_result_evidence() -> None:
    marker = PATH / "RUN_ONCE.marker"
    if marker.exists():
        result = json.loads((PATH / "PRIMARY_RESULT.json").read_text(encoding="utf-8"))
        execution = json.loads((PATH / "EXECUTION.json").read_text(encoding="utf-8"))
        run_marker = json.loads(marker.read_text(encoding="utf-8"))
        assert result["result_status"] == "FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY"
        assert execution["unique_valid_historical_result_count"] == 1
        assert run_marker["SAME_ID_RERUN_ALLOWED"] is False
        assert run_marker["SAME_ID_RESCUE_ALLOWED"] is False
        assert (PATH / "RESULT.md").exists()
        assert not (PATH / "PREDICTOR_PATH.json").exists()
        assert not (PATH / "CALIBRATION_LOCK.json").exists()
        return
    forbidden = (
        "PREDICTOR_PATH.json",
        "CALIBRATION_LOCK",
        "CALIBRATION_LOCK.json",
        "PRIMARY_RESULT.json",
        "EXECUTION.json",
        "RUN_ONCE.marker",
        "RESULT.md",
    )
    for name in forbidden:
        assert not (PATH / name).exists()
