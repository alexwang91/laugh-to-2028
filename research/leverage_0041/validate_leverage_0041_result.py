from __future__ import annotations
import hashlib
import json
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
LEVERAGE = ROOT / 'research' / 'leverage_0041'
RESULT = ROOT / 'research' / 'results' / 'leverage_0041'
OLD_RESULT = ROOT / 'research' / 'results' / 'leverage_0040'
SUMMARY = RESULT / 'summary.json'
DIGEST = RESULT / 'summary.sha256'
PREREG = LEVERAGE / 'LEVERAGE-0041.json'
CONTRACT = LEVERAGE / 'LEVERAGE-0041-STUDY-IMPLEMENTATION-V1.json'
MARKER = LEVERAGE / 'RUN_ONCE_LEVERAGE_0041.marker'
CAPS = ('1.00', '1.05', '1.10', '1.15', '1.20', '1.25', '1.30')
EXPECTED_0040_DIGEST = '3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0'
EXPECTED_MARKER_SHA = '55f06b1549593e847b42ae71c2e82d4c4a23931bdbfc671a6af9d05859e16ca5'

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fail(message: str):
    raise SystemExit(message)

def main() -> None:
    required = [SUMMARY, DIGEST, RESULT / 'candidate_table.csv', RESULT / 'route_split_daily.csv', RESULT / 'liquidation_table.csv', RESULT / 'router_vwap_slippage.csv']
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        fail(f'LEVERAGE-0041 immutable result artifacts missing: {missing}')
    expected = DIGEST.read_text(encoding='utf-8').strip()
    actual = sha256(SUMMARY)
    if expected != actual:
        fail('LEVERAGE-0041 summary digest mismatch')
    if not MARKER.exists() or sha256(MARKER) != EXPECTED_MARKER_SHA:
        fail('RUN_ONCE marker missing or changed')
    data = json.loads(SUMMARY.read_text(encoding='utf-8'))
    if data.get('study_id') != 'LEVERAGE-0041' or data.get('status') != 'ONE_TIME_PREREGISTERED_STUDY_COMPLETE':
        fail('result identity/status mismatch')
    if data.get('production_authorized') is not False:
        fail('study cannot production-authorize')
    constraints = data.get('constraints', {})
    if constraints.get('production_authorized_components') != []:
        fail('production authorization components changed')
    if constraints.get('post_result_retuning_allowed') is not False:
        fail('post-result retuning boundary violated')
    if constraints.get('search_caps') != [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]:
        fail('candidate grid changed')
    if constraints.get('cash_collateral_reserve_fraction') != 0.25:
        fail('collateral reserve changed')
    if constraints.get('spot_financing_max_fraction') != 0.75:
        fail('spot financing budget changed')
    if constraints.get('funding_lookback_sessions') != 7:
        fail('funding lookback changed')
    if constraints.get('funding_full_overlay_max_bps_day') != 5.0:
        fail('funding full-overlay threshold changed')
    if constraints.get('funding_zero_overlay_min_bps_day') != 10.0:
        fail('funding zero-overlay threshold changed')
    if constraints.get('liquidation_min_distance') != 0.55:
        fail('liquidation threshold changed')
    if constraints.get('bootstrap_base_seed') != 20260807:
        fail('bootstrap seed changed')
    evidence = data.get('input_evidence', {})
    if evidence.get('preregistration_sha256') != sha256(PREREG):
        fail('preregistration digest mismatch')
    if evidence.get('implementation_contract_sha256') != sha256(CONTRACT):
        fail('implementation contract digest mismatch')
    if evidence.get('immutable_leverage_0040_summary_sha256') != EXPECTED_0040_DIGEST:
        fail('LEVERAGE-0040 comparator digest mismatch')
    if sha256(OLD_RESULT / 'summary.json') != EXPECTED_0040_DIGEST:
        fail('LEVERAGE-0040 immutable summary changed')
    if evidence.get('owner_run_once_authorized_pre_result') is not True:
        fail('owner RUN_ONCE authority evidence missing')
    authority = evidence.get('raw_target_authority', {})
    if authority.get('feature_assets') != ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']:
        fail('feature universe mismatch')
    if authority.get('target_assets') != ['BTC', 'ETH', 'SOL', 'BNB']:
        fail('target universe mismatch')
    if authority.get('published_banded_weights_used_for_scale') is not False:
        fail('raw-target authority mismatch')
    matrix = data.get('candidate_matrix')
    if not isinstance(matrix, dict) or tuple(sorted(matrix)) != CAPS:
        fail('candidate matrix mismatch')
    table = pd.read_csv(RESULT / 'candidate_table.csv')
    if [f'{float(x):.2f}' for x in table['cap'].tolist()] != list(CAPS):
        fail('candidate table cap grid mismatch')
    route = pd.read_csv(RESULT / 'route_split_daily.csv')
    required_route_cols = {'date', 'cap', 'overlay_scale', 'cash_reserve', 'spot_gross', 'base_perp_gross', 'incremental_perp_gross', 'perp_gross'}
    if not required_route_cols.issubset(route.columns):
        fail('route split artifact incomplete')
    if len(route) == 0:
        fail('route split artifact empty')
    if (route['cash_reserve'] != 0.25).any():
        fail('route split reserve drift')
    if (route['spot_gross'] > 0.75 + 1e-09).any():
        fail('spot budget exceeded')
    if ((route['overlay_scale'] < -1e-12) | (route['overlay_scale'] > 1.0 + 1e-12)).any():
        fail('overlay scale left [0,1]')
    liq_table = pd.read_csv(RESULT / 'liquidation_table.csv')
    if [f'{float(x):.2f}' for x in liq_table['cap'].tolist()] != list(CAPS):
        fail('liquidation table cap grid mismatch')
    if (liq_table['cross_margin_equity_usd'] != 500.0).any():
        fail('liquidation account mapping did not use explicit 25% reserve')
    for cap in CAPS:
        row = matrix[cap]
        if float(row.get('cap')) != float(cap):
            fail(f'cap identity mismatch {cap}')
        costs = row.get('architecture_metrics_by_cost_bps', {})
        if set(costs) != {'5.0', '10.0', '20.0', '50.0'}:
            fail(f'cost grid mismatch {cap}')
        if cap != '1.00':
            gate = row.get('gate', {})
            if not {'pass_pre_broad_region', 'broad_region_pass', 'final_research_pass'}.issubset(gate):
                fail(f'gate bookkeeping missing {cap}')
    selection = data.get('selection', {})
    status = selection.get('status')
    if status not in {'NO_PROMOTION', 'RESEARCH_PROMOTION_CANDIDATE_NOT_PRODUCTION_AUTHORIZED'}:
        fail('selection status invalid')
    if selection.get('production_authorized') is not False:
        fail('selection cannot production-authorize')
    if status == 'NO_PROMOTION':
        if selection.get('selected_research_cap') is not None:
            fail('NO_PROMOTION selected a research cap')
        if selection.get('prospective_live_cap_if_separately_authorized') is not None:
            fail('NO_PROMOTION has a prospective live cap')
    else:
        selected = f"{float(selection['selected_research_cap']):.2f}"
        if selected not in {'1.05', '1.10', '1.15', '1.20', '1.25'}:
            fail('selected cap is not an interior preregistered candidate')
        if matrix[selected]['gate'].get('final_research_pass') is not True:
            fail('selected cap failed frozen gate')
        prospective = float(selection['prospective_live_cap_if_separately_authorized'])
        grid = [1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]
        idx = grid.index(float(selection['selected_research_cap']))
        expected_live = min(grid[idx - 1], 1.2)
        if abs(prospective - expected_live) > 1e-12:
            fail('prospective P4.6 cap rule mismatch')
    print(f'LEVERAGE-0041 immutable result validation PASS sha256={actual}')
if __name__ == '__main__':
    main()
