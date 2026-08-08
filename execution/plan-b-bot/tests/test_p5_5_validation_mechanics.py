from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.cycle_exit.p5_5_validation import (
    add_broad_policy_pass,
    annualized_cagr_from_returns,
    economic_gate_checks,
    held_out_relative_cagr,
    load_contracts,
    robustness_pass,
    select_candidate,
)


def metric_row(profile, behavior_map, cost, rel=0.01, dd_improve=0.03, cagr=0.20, calmar=1.5, sharpe=1.2, turnover=10.0):
    base_cagr = cagr - rel
    base_mdd = -0.30
    candidate_mdd = -(abs(base_mdd) - dd_improve)
    return {
        "profile": profile,
        "behavior_map": behavior_map,
        "cost_bps": float(cost),
        "candidate_end_multiple": 2.0,
        "baseline_end_multiple": 1.9,
        "end_multiple_ratio_vs_baseline": 2.0 / 1.9,
        "candidate_cagr": cagr,
        "baseline_cagr": base_cagr,
        "candidate_minus_baseline_cagr_pp": rel,
        "candidate_max_drawdown": candidate_mdd,
        "baseline_max_drawdown": base_mdd,
        "max_drawdown_improvement_abs": dd_improve,
        "max_drawdown_absolute_worsening": max(0.0, abs(candidate_mdd)-abs(base_mdd)),
        "candidate_calmar": calmar,
        "baseline_calmar": 1.2,
        "calmar_ratio_vs_baseline": calmar / 1.2,
        "candidate_sharpe": sharpe,
        "baseline_sharpe": 1.0,
        "candidate_turnover": turnover,
        "baseline_turnover": 10.0,
        "turnover_ratio_vs_baseline": turnover / 10.0,
    }


def test_annualized_cagr_is_factor_consistent():
    r = pd.Series([0.01, -0.005, 0.002])
    got = annualized_cagr_from_returns(r)
    expected = ((1.01 * 0.995 * 1.002) ** (365.25 / 3.0)) - 1.0
    assert abs(got - expected) < 1e-12


def test_held_out_uses_same_dates_for_candidate_and_baseline():
    idx = pd.date_range("2025-01-01", periods=100, freq="D")
    cand = pd.Series(0.001, index=idx)
    base = pd.Series(0.0005, index=idx)
    cc, bc, rel, n = held_out_relative_cagr(cand, base, exclude_start=idx[10], exclude_end=idx[19])
    assert n == 90
    assert cc > bc
    assert rel > 0


def test_economic_gates_pass_strong_candidate_and_fail_drawdown_worsening():
    c, r1, _ = load_contracts()
    rows = pd.DataFrame([metric_row("BALANCED", "GENTLE", cost) for cost in (5,10,20,50)])
    passed, checks = economic_gate_checks(rows, "BALANCED", "GENTLE", c, r1)
    assert passed and all(checks.values())

    bad = rows.copy()
    bad.loc[bad.cost_bps == 5, "max_drawdown_absolute_worsening"] = 0.02
    passed, checks = economic_gate_checks(bad, "BALANCED", "GENTLE", c, r1)
    assert not passed
    assert checks["dd_5"] is False


def test_robustness_gates_use_worst_and_median():
    c, _, _ = load_contracts()
    starts = pd.DataFrame({
        "profile": ["EARLY"]*4,
        "behavior_map": ["GENTLE"]*4,
        "relative_cagr_pp": [-0.01, 0.0, 0.01, 0.02],
    })
    held = pd.DataFrame({
        "profile": ["EARLY"]*6,
        "behavior_map": ["GENTLE"]*6,
        "relative_cagr_pp": [-0.01, -0.005, 0.0, 0.005, 0.01, 0.02],
    })
    passed, _ = robustness_pass(starts, held, "EARLY", "GENTLE", c)
    assert passed
    starts.loc[0, "relative_cagr_pp"] = -0.02
    passed, checks = robustness_pass(starts, held, "EARLY", "GENTLE", c)
    assert not passed and checks["start_worst"] is False


def test_broad_policy_requires_adjacent_non_selection_passer():
    c, _, _ = load_contracts()
    rows = []
    for profile in c["candidate_set"]["profiles"]:
        for behavior_map in c["candidate_set"]["behavior_maps"]:
            rows.append({"profile": profile, "behavior_map": behavior_map, "non_selection_pass": False})
    gates = pd.DataFrame(rows)
    gates.loc[(gates.profile == "BALANCED") & (gates.behavior_map == "GENTLE"), "non_selection_pass"] = True
    isolated = add_broad_policy_pass(gates, c)
    row = isolated.loc[(isolated.profile == "BALANCED") & (isolated.behavior_map == "GENTLE")].iloc[0]
    assert not bool(row.broad_policy_pass)

    gates.loc[(gates.profile == "EARLY") & (gates.behavior_map == "GENTLE"), "non_selection_pass"] = True
    broad = add_broad_policy_pass(gates, c)
    assert bool(broad.loc[(broad.profile == "BALANCED") & (broad.behavior_map == "GENTLE"), "eligible"].iloc[0])
    assert bool(broad.loc[(broad.profile == "EARLY") & (broad.behavior_map == "GENTLE"), "eligible"].iloc[0])


def test_selection_uses_cagr_then_frozen_near_tie_tiebreakers():
    c, _, _ = load_contracts()
    gates = pd.DataFrame([
        {"profile": "EARLY", "behavior_map": "GENTLE", "eligible": True},
        {"profile": "BALANCED", "behavior_map": "GENTLE", "eligible": True},
    ])
    metrics = pd.DataFrame([
        metric_row("EARLY", "GENTLE", 5, cagr=0.250, calmar=1.40, sharpe=1.2, turnover=9.0),
        metric_row("BALANCED", "GENTLE", 5, cagr=0.247, calmar=1.60, sharpe=1.1, turnover=10.0),
    ])
    selected = select_candidate(gates, metrics, c)
    assert selected["status"] == "PASS_RESEARCH_CANDIDATE"
    assert selected["profile_selected"] == "BALANCED"
    assert selected["behavior_map_selected"] == "GENTLE"
    assert selected["production_authorized"] is False


def test_no_eligible_candidate_fail_stops():
    c, _, _ = load_contracts()
    gates = pd.DataFrame([{"profile":"EARLY","behavior_map":"GENTLE","eligible":False}])
    metrics = pd.DataFrame([metric_row("EARLY","GENTLE",5)])
    selected = select_candidate(gates, metrics, c)
    assert selected["status"] == "NO_PROMOTION_FAIL_STOP"
    assert selected["profile_selected"] is None
    assert selected["production_authorized"] is False
