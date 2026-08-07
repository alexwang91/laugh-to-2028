from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "research" / "cycle_exit" / "p5_3_state_model.py"
CONTRACT_PATH = ROOT / "research" / "cycle_exit" / "p5_3_state_model_contract.json"

spec = importlib.util.spec_from_file_location("p5_3_state_model", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text())


def test_average_rank_percentile_exact_formula_and_ties() -> None:
    assert m._average_rank_percentile(pd.Series([1.0, 2.0, 3.0])) == 1.0
    assert m._average_rank_percentile(pd.Series([3.0, 2.0, 1.0])) == 0.0
    # Current value=2 ties the middle observation: average rank 2.5 of N=4 -> 0.5.
    assert m._average_rank_percentile(pd.Series([1.0, 2.0, 3.0, 2.0])) == 0.5


def test_causal_percentile_at_t_is_unchanged_by_future_values() -> None:
    c = contract()
    continuous, raw = m.runtime_features(c)
    dates = pd.date_range("2020-01-01", periods=30, freq="D")
    panel = pd.DataFrame(index=dates)
    for j, feature in enumerate(continuous):
        panel[feature] = np.arange(30, dtype=float) + j
    for feature in raw:
        panel[feature] = 0.75

    p1, _, _ = m.causal_percentiles(panel, c)
    changed = panel.copy()
    changed.loc[dates[25]:, continuous] = -999999.0
    p2, _, _ = m.causal_percentiles(changed, c)
    pd.testing.assert_series_equal(p1.loc[dates[24]], p2.loc[dates[24]])


def _base_percentile_row(value: float = 0.5) -> pd.Series:
    c = contract()
    continuous, _ = m.runtime_features(c)
    return pd.Series({f: value for f in continuous}, dtype=float)


def test_rotation_without_damage_is_late_bull_not_derisk() -> None:
    c = contract()
    p = _base_percentile_row(0.5)
    profile = c["profiles"]["BALANCED"]
    p["eth_btc_log_return_20d"] = 0.90
    p["eth_btc_log_return_40d"] = 0.90
    raw = pd.Series({"canonical5_outperformance_breadth_20d": 1.0})
    atoms = m.evidence_atoms(p, raw, profile)
    assert atoms.rotation is True
    assert atoms.damage is False
    assert m.raw_candidate(atoms) == "LATE_BULL_ROTATION"


def test_exhaustion_requires_two_independent_subchannels() -> None:
    c = contract()
    profile = c["profiles"]["BALANCED"]
    raw = pd.Series({"canonical5_outperformance_breadth_20d": 0.5})

    p = _base_percentile_row(0.5)
    p["btc_price_rsi_rank_divergence_20d"] = 0.95
    atoms = m.evidence_atoms(p, raw, profile)
    assert atoms.divergence_subchannel is True
    assert atoms.exhaustion is False

    p["btc_rsi14_failure_from_14d_max"] = 0.90
    atoms = m.evidence_atoms(p, raw, profile)
    assert atoms.momentum_failure_subchannel is True
    assert atoms.exhaustion is True


def test_damage_plus_exhaustion_produces_derisk_candidate() -> None:
    c = contract()
    profile = c["profiles"]["BALANCED"]
    p = _base_percentile_row(0.5)
    raw = pd.Series({"canonical5_outperformance_breadth_20d": 0.5})

    p["btc_kama_gap"] = 0.20
    p["btc_log_return_20d"] = 0.20
    p["btc_price_rsi_rank_divergence_20d"] = 0.80
    p["btc_rsi14_failure_from_14d_max"] = 0.80
    atoms = m.evidence_atoms(p, raw, profile)
    assert atoms.damage is True
    assert atoms.exhaustion is True
    assert m.raw_candidate(atoms) in {"DE_RISK_1", "DE_RISK_2", "FLAT"}


def test_initialization_is_normal_unless_raw_flat() -> None:
    c = contract()
    profile = c["profiles"]["EARLY"]
    severity = c["severity_order"]
    memory = m.TransitionMemory()
    state = m.transition_step(memory, "EXHAUSTION_WATCH", profile, severity, ordinary_inputs_complete=True)
    assert state == "NORMAL_BULL"
    assert memory.current_state == "NORMAL_BULL"

    memory2 = m.TransitionMemory()
    state2 = m.transition_step(memory2, "FLAT", profile, severity, ordinary_inputs_complete=True)
    assert state2 == "FLAT"


def test_escalation_uses_minimum_continuously_supported_raw_severity() -> None:
    c = contract()
    profile = c["profiles"]["EARLY"]  # 2-day persistence
    severity = c["severity_order"]
    memory = m.TransitionMemory(current_state="NORMAL_BULL")

    assert m.transition_step(memory, "DE_RISK_2", profile, severity, ordinary_inputs_complete=True) == "NORMAL_BULL"
    # Second day supports only EXHAUSTION_WATCH; minimum severity across [DR2, EW] is EW.
    assert m.transition_step(memory, "EXHAUSTION_WATCH", profile, severity, ordinary_inputs_complete=True) == "EXHAUSTION_WATCH"


def test_deescalation_moves_exactly_one_step_per_fresh_clear_period() -> None:
    c = contract()
    profile = c["profiles"]["EARLY"]  # 5-day clear
    severity = c["severity_order"]
    memory = m.TransitionMemory(current_state="DE_RISK_2")
    for _ in range(4):
        assert m.transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True) == "DE_RISK_2"
    assert m.transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True) == "DE_RISK_1"
    # Fresh clear period is required for another step.
    assert m.transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True) == "DE_RISK_1"


def test_equal_candidate_resets_both_counters() -> None:
    c = contract()
    profile = c["profiles"]["EARLY"]
    severity = c["severity_order"]
    memory = m.TransitionMemory(current_state="EXHAUSTION_WATCH", escalation_raw_indices=[5], deescalation_count=3)
    state = m.transition_step(memory, "EXHAUSTION_WATCH", profile, severity, ordinary_inputs_complete=True)
    assert state == "EXHAUSTION_WATCH"
    assert memory.escalation_raw_indices == []
    assert memory.deescalation_count == 0


def test_missing_data_holds_state_and_resets_counters() -> None:
    c = contract()
    profile = c["profiles"]["EARLY"]
    severity = c["severity_order"]
    memory = m.TransitionMemory(current_state="DE_RISK_1", escalation_raw_indices=[5], deescalation_count=2)
    state = m.transition_step(
        memory,
        "NORMAL_BULL",
        profile,
        severity,
        ordinary_inputs_complete=False,
        hard_flat_proven=False,
    )
    assert state == "DE_RISK_1"
    assert memory.escalation_raw_indices == []
    assert memory.deescalation_count == 0


def test_hard_flat_is_immediate_and_absorbing() -> None:
    c = contract()
    profile = c["profiles"]["CONSERVATIVE"]
    severity = c["severity_order"]
    memory = m.TransitionMemory(current_state="NORMAL_BULL")
    assert m.transition_step(memory, "FLAT", profile, severity, ordinary_inputs_complete=True) == "FLAT"
    assert m.transition_step(memory, "NORMAL_BULL", profile, severity, ordinary_inputs_complete=True) == "FLAT"


def test_preinitialization_missing_emits_data_insufficient() -> None:
    c = contract()
    profile = c["profiles"]["BALANCED"]
    memory = m.TransitionMemory()
    state = m.transition_step(memory, "NORMAL_BULL", profile, c["severity_order"], ordinary_inputs_complete=False)
    assert state == "DATA_INSUFFICIENT"
    assert memory.current_state is None
