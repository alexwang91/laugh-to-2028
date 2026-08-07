from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "research" / "leverage_0040" / "study_core.py"
spec = importlib.util.spec_from_file_location("leverage_0040_study_core", MODULE)
assert spec and spec.loader
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)


def _idx(n=5):
    return pd.date_range("2025-01-01", periods=n, freq="D")


def _frame(rows):
    return pd.DataFrame(rows, index=_idx(len(rows)), columns=core.ASSETS, dtype=float)


def test_defensive_scale_is_mechanical_ratio_and_bounded():
    v1 = _frame([[0.5, 0.3, 0.2, 0.0], [0.4, 0.0, 0.0, 0.0]])
    brrk = _frame([[0.25, 0.15, 0.10, 0.0], [0.1, 0.0, 0.0, 0.0]])
    got = core.recover_defensive_scale(v1, brrk)
    assert got.tolist() == pytest.approx([0.5, 0.25])


def test_candidate_formula_is_two_layer_and_cap1_identity():
    base = _frame([[0.4, 0.3, 0.2, 0.1], [0.2, 0.2, 0.1, 0.0]])
    d = pd.Series([1.0, 0.5], index=base.index)
    cap1 = core.construct_candidate_targets(base, d, 1.0)
    assert np.allclose(cap1, base)
    cap13 = core.construct_candidate_targets(base, d, 1.3)
    assert cap13.iloc[0].sum() == pytest.approx(1.3)
    assert cap13.iloc[1].sum() == pytest.approx(base.iloc[1].sum() * 1.15)


def test_p3_3_adapter_uses_drifted_current_weights_not_last_target():
    targets = _frame([[1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]])
    prices = _frame([[100, 100, 100, 100], [200, 100, 100, 100], [200, 100, 100, 100]])
    path = core.simulate_p3_3_economic_path(targets, prices, start=targets.index[0], end=targets.index[-1], cost_bps=0)
    assert path.current_weights_before_decision.iloc[1]["BTC"] == pytest.approx(1.0)
    assert path.turnover.iloc[1] == pytest.approx(0.0)


def test_band_preserves_current_weights_when_l1_gap_below_five_percent():
    targets = _frame([[0.50, 0.50, 0, 0], [0.51, 0.49, 0, 0], [0.51, 0.49, 0, 0]])
    prices = _frame([[100,100,100,100],[100,100,100,100],[100,100,100,100]])
    path = core.simulate_p3_3_economic_path(targets, prices, start=targets.index[0], end=targets.index[-1], cost_bps=0)
    assert path.turnover.iloc[0] == pytest.approx(1.0)
    assert path.turnover.iloc[1] == pytest.approx(0.0)
    assert path.held_weights.iloc[1].tolist() == pytest.approx([0.5,0.5,0,0])


def test_partial_fill_executes_half_delta_and_costs_only_execution():
    targets = _frame([[1,0,0,0],[1,0,0,0],[1,0,0,0]])
    prices = _frame([[100,100,100,100],[100,100,100,100],[100,100,100,100]])
    path = core.simulate_p3_3_economic_path(targets, prices, start=targets.index[0], end=targets.index[-1], cost_bps=10, fill_fraction=0.5)
    assert path.held_weights.iloc[0]["BTC"] == pytest.approx(0.5)
    assert path.turnover.iloc[0] == pytest.approx(0.5)
    assert path.transaction_cost_return.iloc[0] == pytest.approx(0.0005)


def test_primary_route_keeps_matched_btc_base_spot_and_only_extra_perp():
    perp = core.routed_perp_weights({"BTC":0.60,"ETH":0.20,"SOL":0.10,"BNB":0.05}, {"BTC":0.40,"ETH":0.10,"SOL":0.05,"BNB":0.02})
    assert perp == pytest.approx({"BTC":0.20,"ETH":0.20,"SOL":0.10,"BNB":0.05})


def test_funding_positive_rate_is_long_debit_and_spike_only_amplifies_debit():
    weights = _frame([[0.5,0,0,0],[0.5,0,0,0],[0.5,0,0,0]])
    prices = _frame([[100,100,100,100],[100,100,100,100],[100,100,100,100]])
    funding = {weights.index[1]: [{"BTC":0.001,"ETH":0.0,"SOL":0.0,"BNB":0.0}], weights.index[2]: [{"BTC":0.001,"ETH":0.0,"SOL":0.0,"BNB":0.0}]}
    path = core.simulate_p3_3_economic_path(weights, prices, start=weights.index[0], end=weights.index[-1], cost_bps=0, funding_blocks_by_session=funding, adverse_funding_spike_multiplier=2.0, matched_cap1_held=weights, all_perp=True)
    assert path.funding_return.iloc[0] == pytest.approx(-0.001)


def test_legacy_path_matches_frozen_target_vs_last_accepted_semantics():
    targets = _frame([[0.5,0,0,0], [0.52,0,0,0], [0.56,0,0,0]])
    held = core.legacy_apply_band(targets)
    assert held.iloc[0]["BTC"] == pytest.approx(0.5)
    assert held.iloc[1]["BTC"] == pytest.approx(0.5)
    assert held.iloc[2]["BTC"] == pytest.approx(0.56)


def test_synthetic_gap_uses_pre_gap_weights_no_same_day_rebalance():
    loss = core.synthetic_gap_return({"BTC":0.5,"ETH":0.25,"SOL":0.25,"BNB":0.0}, {"BTC":-0.4,"ETH":-0.2,"SOL":-0.5,"BNB":-0.1})
    assert loss == pytest.approx(-0.375)


def test_log_vol_stress_never_crosses_minus_one_for_valid_return():
    r = _frame([[-0.5,0,0,0]])
    stressed = core.stressed_log_returns(r, 3.0)
    assert stressed.iloc[0]["BTC"] == pytest.approx((1-0.5)**3 - 1)
    assert stressed.iloc[0]["BTC"] > -1.0


def test_operating_budget_is_smallest_candidate_covering_historical_drawdown():
    assert core.select_operating_budget([-0.337, -0.391]) == pytest.approx(0.40)
    assert core.select_operating_budget([-0.51]) is None


def test_broad_region_rejects_isolated_pass():
    assert not core.broad_region_eligible({1.1:True,1.2:False,1.3:False}, 1.1)
    assert core.broad_region_eligible({1.1:True,1.2:True,1.3:False}, 1.1)
    assert core.broad_region_eligible({1.1:False,1.2:True,1.3:True}, 1.2)
    assert not core.broad_region_eligible({1.1:True,1.2:True,1.3:True}, 1.0)


def test_stationary_bootstrap_is_deterministic_for_frozen_seed():
    a = core.stationary_bootstrap_indices(20, 7, resamples=5)
    b = core.stationary_bootstrap_indices(20, 7, resamples=5)
    assert np.array_equal(a, b)
    assert a.min() >= 0 and a.max() < 20


def test_paired_bootstrap_detects_strictly_better_constant_candidate():
    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    c = pd.Series(0.002, index=idx)
    b = pd.Series(0.001, index=idx)
    out = core.paired_bootstrap_stats(c, b, 7, resamples=200)
    assert out["terminal_outperformance_probability"] == pytest.approx(1.0)
    assert out["annualized_return_difference_p05"] > 0


def test_buy_and_hold_is_asset_units_not_daily_rebalanced_equal_weight():
    prices = _frame([[100,100,100,100],[200,100,100,100],[200,200,100,100]])
    r = core.buy_and_hold_returns(prices, {"BTC":0.5,"ETH":0.5})
    assert r.iloc[1] == pytest.approx(0.5)
    assert r.iloc[2] == pytest.approx(2/1.5 - 1)


@pytest.mark.parametrize("cap", [0.9,1.05,1.4])
def test_unregistered_cap_fails_closed(cap):
    d = pd.Series([0.5], index=_idx(1))
    with pytest.raises(core.StudyContractError):
        core.multiplier_from_defensive_scale(d, cap)


def test_study_implementation_contract_is_frozen_before_results():
    contract_path = ROOT / "research" / "leverage_0040" / "LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json"
    data = __import__("json").loads(contract_path.read_text(encoding="utf-8"))
    assert data["study_id"] == "LEVERAGE-0040"
    assert data["status"] == "FROZEN_BEFORE_FIRST_ECONOMIC_RUN"
    assert data["result_observed_before_freeze"] is False
    assert data["production_authorized"] is False
    assert data["candidate_construction"]["caps"] == [1.0, 1.1, 1.2, 1.3]
    assert data["p3_3_rebalance_adapter"]["l1_band"] == pytest.approx(0.05)
    assert data["bootstrap"]["resamples"] == 10000
    assert data["bootstrap"]["mean_block_days"] == [7, 21, 63]
    assert data["one_time_execution"]["marker_sha256"] == "f54cdf362f60cad19d6c429ac4e008047b45d2cb537a95c96e2bc6dac5ce733a"
    assert data["broad_region"]["isolated_pass"] == "no promotion"
