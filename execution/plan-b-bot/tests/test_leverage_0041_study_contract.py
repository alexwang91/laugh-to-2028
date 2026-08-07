from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import pandas as pd
import pytest
ROOT = Path(__file__).resolve().parents[3]
L0041 = ROOT / 'research' / 'leverage_0041'
if str(L0041) not in sys.path:
    sys.path.insert(0, str(L0041))
import study_core_0041 as core

def _load(name: str):
    return json.loads((L0041 / name).read_text(encoding='utf-8'))

def test_implementation_contract_is_frozen_pre_result_and_non_production():
    contract = _load('LEVERAGE-0041-STUDY-IMPLEMENTATION-V1.json')
    assert contract['contract_id'] == 'LEVERAGE-0041-STUDY-IMPLEMENTATION-V1'
    assert contract['study_id'] == 'LEVERAGE-0041'
    assert contract['status'] == 'FROZEN_BEFORE_FIRST_ECONOMIC_RUN'
    assert contract['result_observed_before_freeze'] is False
    assert contract['owner_run_once_authorized'] is True
    assert contract['production_authorized'] is False
    assert contract['base_main'] == 'baaa5776892411990734ef2121cf54a5dbbab047'
    assert contract['target_authority']['requested_target_formula'].endswith('frozen_raw_BRRK0011_target(asset,t) * cap')
    assert contract['architecture']['cash_collateral_reserve_fraction_of_nav'] == 0.25
    assert contract['architecture']['spot_financing_max_fraction_of_nav'] == 0.75
    assert contract['funding_reducer']['lookback_sessions'] == 7
    assert contract['funding_reducer']['full_overlay_max_debit_bps_day'] == 5.0
    assert contract['funding_reducer']['zero_overlay_min_debit_bps_day'] == 10.0
    assert contract['liquidation']['minimum_uniform_adverse_move_required'] == 0.55
    assert contract['risk_and_robustness']['bootstrap_base_seed'] == 20260807

def test_preregistration_remains_immutable_0040_separate_and_non_production():
    prereg = _load('LEVERAGE-0041.json')
    assert prereg['experiment_id'] == 'LEVERAGE-0041'
    assert prereg['status'] == 'PREREGISTERED_BEFORE_FIRST_RUN'
    assert prereg['research_integrity']['leverage_0040_result_is_immutable'] is True
    assert prereg['research_integrity']['leverage_0040_result_sha256'] == '3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0'
    assert prereg['candidate_research_caps'] == [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]
    assert prereg['focal_design_point'] == 1.2
    assert prereg['production_authorized'] is False

def test_cap1_target_is_exact_and_cap_scaling_preserves_relative_weights():
    idx = pd.date_range('2026-01-01', periods=2, freq='D')
    base = pd.DataFrame([{'BTC': 0.4, 'ETH': 0.2, 'SOL': 0.1, 'BNB': 0.1}, {'BTC': 0.2, 'ETH': 0.15, 'SOL': 0.05, 'BNB': 0.1}], index=idx)
    cap1 = core.construct_requested_targets(base, 1.0)
    pd.testing.assert_frame_equal(cap1, base.astype(float))
    cap12 = core.construct_requested_targets(base, 1.2)
    pd.testing.assert_frame_equal(cap12, base.astype(float) * 1.2)

def test_route_split_uses_25pct_reserve_75pct_spot_budget_and_bnb_perp_only():
    economic = {'BTC': 0.5, 'ETH': 0.3, 'SOL': 0.2, 'BNB': 0.2}
    base = {'BTC': 0.45, 'ETH': 0.28, 'SOL': 0.17, 'BNB': 0.1}
    route = core.split_routes(economic, base)
    assert route.cash_reserve == 0.25
    assert route.spot_gross <= 0.75 + 1e-12
    assert route.spot['BNB'] == 0.0
    for asset in core.ASSETS:
        assert route.spot[asset] + route.base_perp[asset] + route.incremental_perp[asset] == pytest.approx(economic[asset])

def test_funding_reducer_is_causal_monotone_and_fail_closed():
    assert core.overlay_scale_from_debit_bps(None) == 0.0
    assert core.overlay_scale_from_debit_bps(0.0) == 1.0
    assert core.overlay_scale_from_debit_bps(5.0) == 1.0
    assert core.overlay_scale_from_debit_bps(7.5) == pytest.approx(0.5)
    assert core.overlay_scale_from_debit_bps(10.0) == 0.0
    assert core.overlay_scale_from_debit_bps(20.0) == 0.0
    complete = [{'complete': True, 'funding_debit_return': 0.00025, 'perp_gross': 0.5} for _ in range(7)]
    assert core.funding_debit_bps_per_day(complete) == pytest.approx(5.0)
    missing = list(complete)
    missing[-1] = {'complete': False, 'funding_debit_return': 0.0, 'perp_gross': 0.5}
    assert core.funding_debit_bps_per_day(missing) is None

def test_effective_target_reducer_never_changes_base_or_relative_overlay_direction():
    base = {'BTC': 0.4, 'ETH': 0.2, 'SOL': 0.1, 'BNB': 0.1}
    req = {a: v * 1.2 for a, v in base.items()}
    full = core.effective_target_with_funding_reducer(base, req, 1.0)
    zero = core.effective_target_with_funding_reducer(base, req, 0.0)
    half = core.effective_target_with_funding_reducer(base, req, 0.5)
    assert full == pytest.approx(req)
    assert zero == pytest.approx(base)
    for asset in core.ASSETS:
        assert half[asset] == pytest.approx((base[asset] + req[asset]) / 2)

def test_broad_region_requires_both_neighbors_and_near_tie_prefers_lower_cap():
    pass_map = {1.0: True, 1.05: True, 1.1: True, 1.15: True, 1.2: True, 1.25: False, 1.3: False}
    region = core.qualifying_region_map(pass_map)
    assert region[1.05] is True
    assert region[1.1] is True
    assert region[1.15] is True
    assert region[1.2] is False
    rows = {1.05: {'final_research_pass': True, 'cagr': 0.695, 'calmar': 2.0, 'sharpe': 1.3, 'max_drawdown': -0.35}, 1.1: {'final_research_pass': True, 'cagr': 0.7, 'calmar': 2.0, 'sharpe': 1.3, 'max_drawdown': -0.36}, 1.15: {'final_research_pass': True, 'cagr': 0.704, 'calmar': 2.0, 'sharpe': 1.3, 'max_drawdown': -0.37}, 1.2: {'final_research_pass': False, 'cagr': 0.71, 'calmar': 2.0, 'sharpe': 1.3, 'max_drawdown': -0.38}, 1.25: {'final_research_pass': False, 'cagr': 0.72, 'calmar': 2.0, 'sharpe': 1.3, 'max_drawdown': -0.39}, 1.3: {'final_research_pass': False, 'cagr': 0.73, 'calmar': 2.0, 'sharpe': 1.3, 'max_drawdown': -0.4}}
    assert core.choose_sweet_spot(rows, pass_map) == 1.05

def test_prospective_p4_6_cap_is_next_lower_and_never_above_120():
    assert core.prospective_live_cap(1.05) == 1.0
    assert core.prospective_live_cap(1.2) == 1.15
    assert core.prospective_live_cap(1.25) == 1.2

def test_run_once_marker_hash_is_frozen_in_contract_but_marker_not_required_pre_run():
    contract = _load('LEVERAGE-0041-STUDY-IMPLEMENTATION-V1.json')
    assert contract['one_time_boundary']['marker_sha256'] == '55f06b1549593e847b42ae71c2e82d4c4a23931bdbfc671a6af9d05859e16ca5'
    marker = L0041 / 'RUN_ONCE_LEVERAGE_0041.marker'
    if marker.exists():
        assert hashlib.sha256(marker.read_bytes()).hexdigest() == contract['one_time_boundary']['marker_sha256']
