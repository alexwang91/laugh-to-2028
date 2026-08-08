from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from research.cycle_exit.p5_3_state_model import TransitionMemory
from research.cycle_exit.p5_3_v2_market_state import (
    evaluate_signal_only,
    load_v2_contract,
    market_state_transition_step,
)

V1_RESULT = ROOT / "research" / "results" / "p5_3_state_paths"


def test_signal_only_normalization_and_counts_match_immutable_v1_without_v2_state_path() -> None:
    _, pct, counts = evaluate_signal_only()

    frozen_pct = pd.read_csv(V1_RESULT / "normalized_percentiles.csv", parse_dates=["date"]).set_index("date")
    frozen_counts = pd.read_csv(V1_RESULT / "normalization_counts.csv", parse_dates=["date"]).set_index("date")

    assert list(pct.columns) == list(frozen_pct.columns)
    assert pct.index.equals(frozen_pct.index)
    assert np.allclose(pct.to_numpy(), frozen_pct.to_numpy(), rtol=0.0, atol=5e-12, equal_nan=True)

    assert list(counts.columns) == list(frozen_counts.columns)
    assert counts.index.equals(frozen_counts.index)
    pd.testing.assert_frame_equal(counts.astype(int), frozen_counts.astype(int), check_dtype=False)


def test_signal_only_atoms_and_raw_candidates_match_immutable_v1() -> None:
    signal, _, _ = evaluate_signal_only()
    frozen = pd.read_csv(V1_RESULT / "daily_state_paths.csv", parse_dates=["date"]).set_index(["date", "profile"]).sort_index()

    columns = [
        "raw_candidate_state",
        "ordinary_inputs_complete",
        "minimum_calibration_depth",
        "mature_texture",
        "rotation",
        "exhaustion",
        "strong_exhaustion",
        "damage",
        "strong_damage",
        "divergence_subchannel",
        "momentum_failure_subchannel",
        "breadth_transition_subchannel",
    ]
    assert signal.index.equals(frozen.index)
    for column in columns:
        if column == "minimum_calibration_depth":
            assert signal[column].astype(int).equals(frozen[column].astype(int))
        elif column == "raw_candidate_state":
            assert signal[column].astype(str).equals(frozen[column].astype(str))
        else:
            assert signal[column].astype(bool).equals(frozen[column].astype(bool))

    false_flat = signal.loc[(pd.Timestamp("2021-02-23"), slice(None)), "raw_candidate_state"]
    assert set(false_flat.astype(str)) == {"FLAT"}


def test_market_state_flat_recovers_one_step_after_existing_clear_period() -> None:
    c = load_v2_contract()
    profile = c["profiles"]["EARLY"]
    severity = c["architecture_layers"]["MARKET_STATE"]["severity_order"]
    memory = TransitionMemory(current_state="FLAT")

    for _ in range(4):
        state = market_state_transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True)
        assert state == "FLAT"

    state = market_state_transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True)
    assert state == "DE_RISK_2"
    assert memory.deescalation_count == 0

    for _ in range(5):
        state = market_state_transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True)
    assert state == "DE_RISK_1"


def test_raw_flat_is_still_immediate_and_resets_recovery() -> None:
    c = load_v2_contract()
    profile = c["profiles"]["BALANCED"]
    severity = c["architecture_layers"]["MARKET_STATE"]["severity_order"]
    memory = TransitionMemory(current_state="FLAT")

    for _ in range(4):
        assert market_state_transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True) == "FLAT"

    assert memory.deescalation_count == 4
    assert market_state_transition_step(memory, "FLAT", profile, severity, ordinary_inputs_complete=True) == "FLAT"
    assert memory.deescalation_count == 0

    memory.current_state = "DE_RISK_1"
    assert market_state_transition_step(memory, "FLAT", profile, severity, ordinary_inputs_complete=True) == "FLAT"


def test_missing_data_holds_market_state_and_resets_counters() -> None:
    c = load_v2_contract()
    profile = c["profiles"]["CONSERVATIVE"]
    severity = c["architecture_layers"]["MARKET_STATE"]["severity_order"]
    memory = TransitionMemory(current_state="FLAT", deescalation_count=6)

    state = market_state_transition_step(
        memory,
        "NORMAL_BULL",
        profile,
        severity,
        ordinary_inputs_complete=False,
        hard_flat_proven=False,
    )
    assert state == "FLAT"
    assert memory.deescalation_count == 0
    assert memory.escalation_raw_indices == []


def test_market_state_has_no_permission_unlock_authority() -> None:
    c = load_v2_contract()
    permission = c["architecture_layers"]["RISK_PERMISSION_LOCK"]
    assert permission["market_state_has_unlock_authority"] is False
    assert permission["automatic_unlock_forbidden"] is True
    assert permission["unlock_authority"] == "EXPLICIT_HUMAN_APPROVAL_ONLY"
    assert "does not simulate a historical permission-lock path" in permission["research_simulation_rule"]
