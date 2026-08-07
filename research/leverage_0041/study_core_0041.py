from __future__ import annotations
'Pure LEVERAGE-0041 implementation mechanics.\n\nThis module is inert on import. It contains no network access and does not load\nhistorical candidate results. The semantics here are frozen before RUN_ONCE.\n'
from dataclasses import dataclass
import math
from typing import Mapping, Sequence
import numpy as np
import pandas as pd
ASSETS = ('BTC', 'ETH', 'SOL', 'BNB')
SPOT_ELIGIBLE = ('BTC', 'ETH', 'SOL')
CAPS = (1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3)
COST_GRID = (5.0, 10.0, 20.0, 50.0)
OPERATING_BUDGETS = (0.35, 0.4, 0.45, 0.5)
BOOTSTRAP_BLOCKS = (7, 21, 63)
BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_BASE_SEED = 20260807
REBALANCE_BAND = 0.05
SPOT_BUDGET = 0.75
CASH_RESERVE = 0.25
FUNDING_LOOKBACK_SESSIONS = 7
FUNDING_FULL_OVERLAY_MAX_BPS_DAY = 5.0
FUNDING_ZERO_OVERLAY_MIN_BPS_DAY = 10.0
LIQUIDATION_MIN_DISTANCE = 0.55
REFERENCE_EQUITY = 2000.0

class Study0041ContractError(ValueError):
    pass

@dataclass(frozen=True)
class RouteSplit:
    spot: dict[str, float]
    base_perp: dict[str, float]
    incremental_perp: dict[str, float]
    total_perp: dict[str, float]
    cash_reserve: float

    @property
    def spot_gross(self) -> float:
        return float(sum((abs(v) for v in self.spot.values())))

    @property
    def base_perp_gross(self) -> float:
        return float(sum((abs(v) for v in self.base_perp.values())))

    @property
    def incremental_perp_gross(self) -> float:
        return float(sum((abs(v) for v in self.incremental_perp.values())))

    @property
    def perp_gross(self) -> float:
        return float(sum((abs(v) for v in self.total_perp.values())))

@dataclass(frozen=True)
class Path0041:
    returns: pd.Series
    nav: pd.Series
    turnover: pd.Series
    gross_exposure: pd.Series
    held_weights: pd.DataFrame
    current_weights_before_decision: pd.DataFrame
    funding_return: pd.Series
    transaction_cost_return: pd.Series
    requested_gross: pd.Series
    effective_target_gross: pd.Series
    funding_overlay_scale: pd.Series
    funding_debit_bps_day: pd.Series
    routed_spot_weights: pd.DataFrame
    routed_base_perp_weights: pd.DataFrame
    routed_incremental_perp_weights: pd.DataFrame
    routed_perp_weights: pd.DataFrame
    cash_reserve_weight: pd.Series
    funding_data_complete: pd.Series

def _require_assets(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    missing = [a for a in ASSETS if a not in frame.columns]
    extra = [c for c in frame.columns if c not in ASSETS]
    if missing or extra:
        raise Study0041ContractError(f'{name} must contain exactly {ASSETS}; missing={missing} extra={extra}')
    out = frame.loc[:, ASSETS].astype(float).copy()
    if not np.isfinite(out.to_numpy()).all():
        raise Study0041ContractError(f'{name} contains non-finite values')
    return out

def construct_requested_targets(frozen_brrk_targets: pd.DataFrame, requested_cap: float) -> pd.DataFrame:
    base = _require_assets(frozen_brrk_targets, 'frozen_brrk_targets')
    cap = round(float(requested_cap), 2)
    if cap not in CAPS:
        raise Study0041ContractError(f'requested_cap must be one of {CAPS}')
    if (base < -1e-12).any().any():
        raise Study0041ContractError('LEVERAGE-0041 is long-only')
    if (base.abs().sum(axis=1) > 1.0 + 1e-09).any():
        raise Study0041ContractError('frozen BRRK gross exceeded 1.0')
    out = base * cap
    if (out.abs().sum(axis=1) > cap + 1e-09).any():
        raise Study0041ContractError('requested target exceeded preregistered cap')
    return out

def effective_target_with_funding_reducer(base_target: Mapping[str, float], requested_target: Mapping[str, float], overlay_scale: float) -> dict[str, float]:
    s = float(overlay_scale)
    if not math.isfinite(s) or not 0.0 <= s <= 1.0:
        raise Study0041ContractError('overlay_scale must be finite in [0,1]')
    out: dict[str, float] = {}
    for asset in ASSETS:
        b = float(base_target[asset])
        r = float(requested_target[asset])
        if not (math.isfinite(b) and math.isfinite(r)):
            raise Study0041ContractError('target contains non-finite values')
        if b < -1e-12 or r < b - 1e-10:
            raise Study0041ContractError('requested target may not be below frozen base')
        out[asset] = b + s * (r - b)
    return out

def split_routes(economic_weights: Mapping[str, float], base_reference: Mapping[str, float]) -> RouteSplit:
    e = {a: float(economic_weights[a]) for a in ASSETS}
    b = {a: float(base_reference[a]) for a in ASSETS}
    if any((not math.isfinite(v) or v < -1e-12 for v in e.values())):
        raise Study0041ContractError('economic weights must be finite long-only')
    if any((not math.isfinite(v) or v < -1e-12 for v in b.values())):
        raise Study0041ContractError('base reference must be finite long-only')
    base_component = {a: min(max(e[a], 0.0), max(b[a], 0.0)) for a in ASSETS}
    requested_spot = {a: base_component[a] for a in SPOT_ELIGIBLE}
    total_requested_spot = float(sum(requested_spot.values()))
    spot_scale = 1.0
    if total_requested_spot > SPOT_BUDGET:
        spot_scale = SPOT_BUDGET / total_requested_spot
    spot = {a: 0.0 for a in ASSETS}
    for a in SPOT_ELIGIBLE:
        spot[a] = requested_spot[a] * spot_scale
    base_perp = {a: 0.0 for a in ASSETS}
    for a in SPOT_ELIGIBLE:
        base_perp[a] = max(base_component[a] - spot[a], 0.0)
    base_perp['BNB'] = base_component['BNB']
    incremental = {a: max(e[a] - base_component[a], 0.0) for a in ASSETS}
    total_perp = {a: base_perp[a] + incremental[a] for a in ASSETS}
    reconstructed = {a: spot[a] + total_perp[a] for a in ASSETS}
    for a in ASSETS:
        if abs(reconstructed[a] - e[a]) > 1e-09:
            raise Study0041ContractError(f'route reconstruction failed for {a}')
    if sum(spot.values()) > SPOT_BUDGET + 1e-10:
        raise Study0041ContractError('spot budget exceeded 75% NAV')
    if abs(CASH_RESERVE + SPOT_BUDGET - 1.0) > 1e-12:
        raise Study0041ContractError('reserve/spot budget invariant broken')
    if spot['BNB'] != 0.0:
        raise Study0041ContractError('BNB spot route is forbidden')
    return RouteSplit(spot=spot, base_perp=base_perp, incremental_perp=incremental, total_perp=total_perp, cash_reserve=CASH_RESERVE)

def funding_debit_bps_per_day(history: Sequence[Mapping[str, float | bool]]) -> float | None:
    if len(history) < FUNDING_LOOKBACK_SESSIONS:
        return None
    window = list(history[-FUNDING_LOOKBACK_SESSIONS:])
    if any((bool(row.get('complete')) is not True for row in window)):
        return None
    debit = float(sum((max(float(row.get('funding_debit_return', 0.0)), 0.0) for row in window)))
    avg_perp = float(np.mean([max(float(row.get('perp_gross', 0.0)), 0.0) for row in window]))
    if avg_perp <= 1e-15:
        return 0.0
    return debit / avg_perp / FUNDING_LOOKBACK_SESSIONS * 10000.0

def overlay_scale_from_debit_bps(debit_bps_day: float | None) -> float:
    if debit_bps_day is None:
        return 0.0
    d = float(debit_bps_day)
    if not math.isfinite(d) or d < 0.0:
        raise Study0041ContractError('funding debit metric must be finite and non-negative')
    if d <= FUNDING_FULL_OVERLAY_MAX_BPS_DAY:
        return 1.0
    if d >= FUNDING_ZERO_OVERLAY_MIN_BPS_DAY:
        return 0.0
    return (FUNDING_ZERO_OVERLAY_MIN_BPS_DAY - d) / (FUNDING_ZERO_OVERLAY_MIN_BPS_DAY - FUNDING_FULL_OVERLAY_MAX_BPS_DAY)

def funding_return_from_blocks(perp_weights: Mapping[str, float], block_rates: Sequence[Mapping[str, float]] | None, *, adverse_spike_multiplier: float=1.0) -> float:
    if not block_rates:
        return 0.0
    multiplier = float(adverse_spike_multiplier)
    if not math.isfinite(multiplier) or multiplier < 1.0:
        raise Study0041ContractError('adverse funding multiplier must be >=1')
    factor = 1.0
    for block in block_rates:
        debit = 0.0
        for asset in ASSETS:
            rate = float(block.get(asset, 0.0))
            if not math.isfinite(rate):
                raise Study0041ContractError('non-finite funding rate')
            if rate > 0.0:
                rate *= multiplier
            debit += max(float(perp_weights[asset]), 0.0) * rate
        block_factor = 1.0 - debit
        if not math.isfinite(block_factor) or block_factor <= 0.0:
            raise Study0041ContractError('funding block factor became non-positive')
        factor *= block_factor
    return float(factor - 1.0)

def simulate_path(requested_targets: pd.DataFrame, base_targets: pd.DataFrame, close_prices: pd.DataFrame, *, start: str | pd.Timestamp, end: str | pd.Timestamp, cost_bps: float, funding_blocks_by_session: Mapping[pd.Timestamp, Sequence[Mapping[str, float]]] | None, apply_funding_reducer: bool=True, charge_native_funding: bool=True, adverse_funding_spike_multiplier: float=1.0, fill_fraction: float=1.0, transaction_cost_multiplier: float=1.0, band: float=REBALANCE_BAND) -> Path0041:
    requested = _require_assets(requested_targets, 'requested_targets')
    base = _require_assets(base_targets, 'base_targets')
    prices = _require_assets(close_prices, 'close_prices')
    if not requested.index.equals(base.index):
        raise Study0041ContractError('requested/base target indexes must match')
    if not 0.0 < float(fill_fraction) <= 1.0:
        raise Study0041ContractError('fill_fraction must be in (0,1]')
    if float(cost_bps) < 0.0 or float(transaction_cost_multiplier) < 0.0:
        raise Study0041ContractError('cost inputs must be non-negative')
    common_all = requested.index.intersection(prices.index).sort_values()
    start_ts, end_ts = (pd.Timestamp(start), pd.Timestamp(end))
    input_start = start_ts - pd.Timedelta(days=1)
    common = common_all[(common_all >= input_start) & (common_all <= end_ts)]
    if len(common) < 2 or input_start not in common:
        raise Study0041ContractError('session-start simulation requires prior decision day')
    px = prices.reindex(common)
    if px.isna().any().any():
        raise Study0041ContractError('missing prices inside simulation window')
    next_returns = px.pct_change()
    current = pd.Series(0.0, index=ASSETS, dtype=float)
    history: list[dict[str, float | bool]] = []
    rows: list[dict[str, float | bool]] = []
    before_rows: list[dict[str, float]] = []
    held_rows: list[dict[str, float]] = []
    spot_rows: list[dict[str, float]] = []
    base_perp_rows: list[dict[str, float]] = []
    incr_perp_rows: list[dict[str, float]] = []
    perp_rows: list[dict[str, float]] = []
    session_dates: list[pd.Timestamp] = []
    for i in range(1, len(common)):
        decision_date = common[i - 1]
        session_date = common[i]
        req = requested.loc[decision_date].astype(float)
        base_row = base.loc[decision_date].astype(float)
        debit_metric = funding_debit_bps_per_day(history)
        overlay_scale = overlay_scale_from_debit_bps(debit_metric) if apply_funding_reducer else 1.0
        effective = pd.Series(effective_target_with_funding_reducer(base_row.to_dict(), req.to_dict(), overlay_scale), index=ASSETS, dtype=float)
        if float(effective.abs().sum()) > max(CAPS) + 1e-09:
            raise Study0041ContractError('effective target exceeded preregistered max cap')
        before = current.copy()
        gap = float((effective - current).abs().sum())
        if gap >= float(band):
            accepted = current + float(fill_fraction) * (effective - current)
        else:
            accepted = current.copy()
        executed_turnover = float((accepted - current).abs().sum())
        cost_ret = executed_turnover * float(cost_bps) / 10000.0 * float(transaction_cost_multiplier)
        route = split_routes(accepted.to_dict(), base_row.to_dict())
        blocks = None
        complete = False
        if funding_blocks_by_session is not None:
            blocks = funding_blocks_by_session.get(pd.Timestamp(session_date))
            complete = bool(blocks) and len(blocks) == 3
        funding_ret = 0.0
        if charge_native_funding and complete:
            funding_ret = funding_return_from_blocks(route.total_perp, blocks, adverse_spike_multiplier=adverse_funding_spike_multiplier)
        r = next_returns.loc[session_date].fillna(0.0).astype(float)
        price_ret = float((accepted * r).sum())
        net_ret = price_ret - cost_ret + funding_ret
        factor = 1.0 + net_ret
        if not math.isfinite(factor) or factor <= 0.0:
            raise Study0041ContractError('path equity became non-positive')
        current = accepted.mul(1.0 + r) / factor
        session_dates.append(pd.Timestamp(session_date))
        before_rows.append(before.to_dict())
        held_rows.append({a: float(accepted[a]) for a in ASSETS})
        spot_rows.append(route.spot.copy())
        base_perp_rows.append(route.base_perp.copy())
        incr_perp_rows.append(route.incremental_perp.copy())
        perp_rows.append(route.total_perp.copy())
        rows.append({'return': float(net_ret), 'turnover': executed_turnover, 'gross_exposure': float(accepted.abs().sum()), 'funding_return': float(funding_ret), 'transaction_cost_return': float(cost_ret), 'requested_gross': float(req.abs().sum()), 'effective_target_gross': float(effective.abs().sum()), 'funding_overlay_scale': float(overlay_scale), 'funding_debit_bps_day': float('nan') if debit_metric is None else float(debit_metric), 'cash_reserve_weight': CASH_RESERVE, 'funding_data_complete': bool(complete)})
        history.append({'complete': bool(complete), 'funding_debit_return': max(-float(funding_ret), 0.0) if complete else 0.0, 'perp_gross': route.perp_gross})
    idx = pd.DatetimeIndex(session_dates)
    rec = pd.DataFrame(rows, index=idx)
    held = pd.DataFrame(held_rows, index=idx).loc[:, ASSETS]
    before = pd.DataFrame(before_rows, index=idx).loc[:, ASSETS]
    spot = pd.DataFrame(spot_rows, index=idx).loc[:, ASSETS]
    base_perp = pd.DataFrame(base_perp_rows, index=idx).loc[:, ASSETS]
    incr_perp = pd.DataFrame(incr_perp_rows, index=idx).loc[:, ASSETS]
    perp = pd.DataFrame(perp_rows, index=idx).loc[:, ASSETS]
    nav = (1.0 + rec['return']).cumprod()
    return Path0041(returns=rec['return'], nav=nav, turnover=rec['turnover'], gross_exposure=rec['gross_exposure'], held_weights=held, current_weights_before_decision=before, funding_return=rec['funding_return'], transaction_cost_return=rec['transaction_cost_return'], requested_gross=rec['requested_gross'], effective_target_gross=rec['effective_target_gross'], funding_overlay_scale=rec['funding_overlay_scale'], funding_debit_bps_day=rec['funding_debit_bps_day'], routed_spot_weights=spot, routed_base_perp_weights=base_perp, routed_incremental_perp_weights=incr_perp, routed_perp_weights=perp, cash_reserve_weight=rec['cash_reserve_weight'], funding_data_complete=rec['funding_data_complete'].astype(bool))

def path_metrics(path: Path0041, annualization: float=365.25) -> dict[str, float]:
    r = path.returns.astype(float)
    nav = path.nav.astype(float)
    if len(r) == 0:
        raise Study0041ContractError('empty path')
    years = len(r) / float(annualization)
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(r.std())
    mdd = float(dd.min())
    finite_debit = path.funding_debit_bps_day.replace([np.inf, -np.inf], np.nan).dropna()
    return {'end_multiple': float(nav.iloc[-1]), 'cagr': cagr, 'max_drawdown': mdd, 'sharpe': float(r.mean() / std * math.sqrt(365.0)) if std > 0 else float('nan'), 'calmar': float(cagr / abs(mdd)) if mdd < 0 else float('nan'), 'turnover': float(path.turnover.sum()), 'avg_gross_exposure': float(path.gross_exposure.mean()), 'avg_effective_target_gross': float(path.effective_target_gross.mean()), 'avg_overlay_scale': float(path.funding_overlay_scale.mean()), 'avg_spot_gross': float(path.routed_spot_weights.abs().sum(axis=1).mean()), 'avg_perp_gross': float(path.routed_perp_weights.abs().sum(axis=1).mean()), 'avg_funding_debit_bps_day_when_defined': float(finite_debit.mean()) if len(finite_debit) else float('nan')}

def select_operating_budget(max_drawdowns: Sequence[float]) -> float | None:
    worst = max((abs(float(x)) for x in max_drawdowns)) if max_drawdowns else 0.0
    for budget in OPERATING_BUDGETS:
        if worst <= budget + 1e-12:
            return budget
    return None

def qualifying_region_map(pass_by_cap: Mapping[float, bool]) -> dict[float, bool]:
    rounded = {round(float(k), 2): bool(v) for k, v in pass_by_cap.items()}
    out: dict[float, bool] = {}
    for i, cap in enumerate(CAPS):
        if cap <= 1.0 or i == 0 or i == len(CAPS) - 1:
            out[cap] = False
            continue
        out[cap] = bool(rounded.get(round(CAPS[i - 1], 2), False) and rounded.get(round(cap, 2), False) and rounded.get(round(CAPS[i + 1], 2), False))
    return out

def contiguous_pass_component(pass_by_cap: Mapping[float, bool], cap: float) -> tuple[float, ...]:
    rounded = {round(float(k), 2): bool(v) for k, v in pass_by_cap.items()}
    target = round(float(cap), 2)
    if not rounded.get(target, False):
        return ()
    idx = list(CAPS).index(target)
    lo = idx
    hi = idx
    while lo - 1 >= 0 and rounded.get(round(CAPS[lo - 1], 2), False):
        lo -= 1
    while hi + 1 < len(CAPS) and rounded.get(round(CAPS[hi + 1], 2), False):
        hi += 1
    return tuple(CAPS[lo:hi + 1])

def choose_sweet_spot(rows_by_cap: Mapping[float, Mapping[str, object]], pass_by_cap: Mapping[float, bool]) -> float | None:
    region_map = qualifying_region_map(pass_by_cap)
    eligible = [cap for cap in CAPS if cap > 1.0 and region_map.get(cap, False) and bool(rows_by_cap[cap]['final_research_pass'])]
    if not eligible:
        return None
    best = max(eligible, key=lambda c: (float(rows_by_cap[c]['cagr']), float(rows_by_cap[c]['calmar']), float(rows_by_cap[c]['sharpe']), float(rows_by_cap[c]['max_drawdown']), -c))
    component = set(contiguous_pass_component(pass_by_cap, best))
    best_cagr = float(rows_by_cap[best]['cagr'])
    close = [c for c in eligible if c in component and best_cagr - float(rows_by_cap[c]['cagr']) <= 0.01 + 1e-12]
    return min(close) if close else best

def prospective_live_cap(selected_research_cap: float | None) -> float | None:
    if selected_research_cap is None:
        return None
    cap = round(float(selected_research_cap), 2)
    idx = list(CAPS).index(cap)
    if idx <= 0:
        return None
    return min(float(CAPS[idx - 1]), 1.2)
