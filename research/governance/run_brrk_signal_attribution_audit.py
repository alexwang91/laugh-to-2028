from __future__ import annotations

"""Non-promotable attribution audit for canonical BRRK and the frozen external-fusion diagnostic.

This runner reuses the exact BRRK target authority and P3.3 economic simulator already
used by the prior frozen diagnostics. It does not optimize, fit, or alter any strategy rule.
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.governance import run_dual_layer_fusion_sanity_once as fusion


CONTRACT_ID = "BRRK-SIGNAL-ATTRIBUTION-AUDIT-V1"
EPS_RETURN = 1e-15
EPS_GROSS = 1e-12
EPS_TURNOVER = 1e-12
TOP_NS = (10, 20, 50)


class AuditError(RuntimeError):
    pass


def _safe_ratio(a: float, b: float) -> float | None:
    return float(a / b) if math.isfinite(a) and math.isfinite(b) and abs(b) > 0.0 else None


def distribution_metrics(returns: pd.Series, gross: pd.Series | None = None) -> dict[str, object]:
    r = returns.astype(float)
    if gross is not None:
        mask = gross.reindex(r.index).astype(float) > EPS_GROSS
        r = r.loc[mask]
    pos = r[r > EPS_RETURN]
    neg = r[r < -EPS_RETURN]
    zero = r[(r >= -EPS_RETURN) & (r <= EPS_RETURN)]
    nonzero = len(pos) + len(neg)
    return {
        "session_count": int(len(r)),
        "positive_sessions": int(len(pos)),
        "negative_sessions": int(len(neg)),
        "zero_sessions": int(len(zero)),
        "positive_session_rate_all": float(len(pos) / len(r)) if len(r) else None,
        "win_rate_excluding_zero": float(len(pos) / nonzero) if nonzero else None,
        "mean_positive_return": float(pos.mean()) if len(pos) else None,
        "mean_negative_return": float(neg.mean()) if len(neg) else None,
        "median_positive_return": float(pos.median()) if len(pos) else None,
        "median_negative_return": float(neg.median()) if len(neg) else None,
        "payoff_ratio_mean_win_to_abs_mean_loss": _safe_ratio(float(pos.mean()) if len(pos) else float("nan"), abs(float(neg.mean())) if len(neg) else float("nan")),
        "profit_factor_sum_wins_to_abs_sum_losses": _safe_ratio(float(pos.sum()) if len(pos) else 0.0, abs(float(neg.sum())) if len(neg) else 0.0),
    }


def cycle_metrics(path) -> dict[str, object]:
    r = path.returns.astype(float)
    turnover = path.turnover.reindex(r.index).astype(float)
    cycle_id = (turnover > EPS_TURNOVER).astype(int).cumsum()
    if int(cycle_id.iloc[0]) == 0:
        cycle_id = cycle_id + 1
    cycle_returns = r.groupby(cycle_id).apply(lambda x: float(np.prod(1.0 + x.to_numpy()) - 1.0))
    pos = cycle_returns[cycle_returns > EPS_RETURN]
    neg = cycle_returns[cycle_returns < -EPS_RETURN]
    zero = cycle_returns[(cycle_returns >= -EPS_RETURN) & (cycle_returns <= EPS_RETURN)]
    nonzero = len(pos) + len(neg)
    return {
        "cycle_count": int(len(cycle_returns)),
        "positive_cycles": int(len(pos)),
        "negative_cycles": int(len(neg)),
        "zero_cycles": int(len(zero)),
        "cycle_win_rate_excluding_zero": float(len(pos) / nonzero) if nonzero else None,
        "mean_positive_cycle_return": float(pos.mean()) if len(pos) else None,
        "mean_negative_cycle_return": float(neg.mean()) if len(neg) else None,
        "cycle_payoff_ratio": _safe_ratio(float(pos.mean()) if len(pos) else float("nan"), abs(float(neg.mean())) if len(neg) else float("nan")),
        "cycle_profit_factor": _safe_ratio(float(pos.sum()) if len(pos) else 0.0, abs(float(neg.sum())) if len(neg) else 0.0),
    }


def cagr_from_returns(r: pd.Series) -> float:
    arr = r.astype(float).to_numpy()
    if len(arr) == 0:
        raise AuditError("empty returns")
    multiple = float(np.prod(1.0 + arr))
    years = len(arr) / 365.25
    return float(multiple ** (1.0 / years) - 1.0)


def concentration_metrics(r: pd.Series) -> dict[str, object]:
    r = r.astype(float)
    total_log = float(np.log1p(r).sum())
    out: dict[str, object] = {"total_log_growth": total_log}
    for n in TOP_NS:
        best_idx = r.nlargest(n).index
        worst_idx = r.nsmallest(n).index
        best_log = float(np.log1p(r.loc[best_idx]).sum())
        worst_log = float(np.log1p(r.loc[worst_idx]).sum())
        no_best = r.copy(); no_best.loc[best_idx] = 0.0
        no_worst = r.copy(); no_worst.loc[worst_idx] = 0.0
        out[f"best_{n}"] = {
            "log_growth_contribution": best_log,
            "share_of_total_log_growth": _safe_ratio(best_log, total_log),
            "same_horizon_cagr_if_zeroed": cagr_from_returns(no_best),
        }
        out[f"worst_{n}"] = {
            "log_growth_contribution": worst_log,
            "share_of_total_log_growth": _safe_ratio(worst_log, total_log),
            "same_horizon_cagr_if_zeroed": cagr_from_returns(no_worst),
        }
    return out


def state_for_sessions(base_targets: pd.DataFrame, supply: pd.Series, sessions: pd.DatetimeIndex) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    if len(base_targets.index) != len(sessions) + 1:
        raise AuditError("decision/session index length mismatch")
    state_map: dict[pd.Timestamp, str] = {}
    cap_map: dict[pd.Timestamp, float] = {}
    base_gross_map: dict[pd.Timestamp, float] = {}
    fused_gross_map: dict[pd.Timestamp, float] = {}
    for decision_dt, session_dt in zip(base_targets.index[:-1], sessions):
        state = fusion.external_state_for_decision(supply, pd.Timestamp(decision_dt))
        base_row = base_targets.loc[decision_dt, list(fusion.ASSETS)].astype(float)
        fused_row = fusion.apply_external_gross_cap(base_row.to_dict(), state)
        state_map[pd.Timestamp(session_dt)] = state.state
        cap_map[pd.Timestamp(session_dt)] = float(state.gross_cap)
        base_gross_map[pd.Timestamp(session_dt)] = float(base_row.sum())
        fused_gross_map[pd.Timestamp(session_dt)] = float(sum(fused_row.values()))
    return (
        pd.Series(state_map).sort_index(),
        pd.Series(cap_map).sort_index(),
        pd.Series(base_gross_map).sort_index(),
        pd.Series(fused_gross_map).sort_index(),
    )


def external_attribution(base_path, fused_path, state: pd.Series, cap: pd.Series, base_target_gross: pd.Series, fused_target_gross: pd.Series) -> dict[str, object]:
    b = base_path.returns.astype(float)
    f = fused_path.returns.reindex(b.index).astype(float)
    if f.isna().any():
        raise AuditError("fused return index mismatch")
    delta = f - b
    intervention = (base_target_gross - fused_target_gross) > EPS_GROSS
    rows: dict[str, object] = {}
    for s in ("SUPPORTIVE", "NEUTRAL", "RESTRICTIVE"):
        m = state == s
        br = b.loc[m]
        fr = f.loc[m]
        rows[s] = {
            "session_count": int(m.sum()),
            "baseline_mean_return": float(br.mean()),
            "baseline_win_rate_excluding_zero": distribution_metrics(br)["win_rate_excluding_zero"],
            "baseline_compounded_return_over_state_sessions": float(np.prod(1.0 + br.to_numpy()) - 1.0),
            "fused_compounded_return_over_state_sessions": float(np.prod(1.0 + fr.to_numpy()) - 1.0),
            "mean_baseline_target_gross": float(base_target_gross.loc[m].mean()),
            "mean_fused_target_gross": float(fused_target_gross.loc[m].mean()),
            "frozen_cap": float(cap.loc[m].iloc[0]) if bool(m.any()) else None,
            "fraction_canonical_target_already_at_or_below_cap": float((base_target_gross.loc[m] <= cap.loc[m] + EPS_GROSS).mean()) if bool(m.any()) else None,
            "intervention_session_count": int(intervention.loc[m].sum()),
            "sum_session_return_delta_fused_minus_baseline": float(delta.loc[m].sum()),
        }

    positive = b > EPS_RETURN
    negative = b < -EPS_RETURN
    impacted = delta.abs() > 1e-15
    top_missed = delta.nsmallest(10)
    top_saved = delta.nlargest(10)
    def detail(series: pd.Series) -> list[dict[str, object]]:
        out = []
        for dt, d in series.items():
            out.append({
                "date": str(pd.Timestamp(dt).date()),
                "state": str(state.loc[dt]),
                "baseline_return": float(b.loc[dt]),
                "fused_return": float(f.loc[dt]),
                "delta": float(d),
                "baseline_target_gross": float(base_target_gross.loc[dt]),
                "fused_target_gross": float(fused_target_gross.loc[dt]),
            })
        return out
    return {
        "by_external_state": rows,
        "actual_path_delta_decomposition": {
            "sum_delta_on_baseline_positive_sessions": float(delta.loc[positive].sum()),
            "sum_delta_on_baseline_negative_sessions": float(delta.loc[negative].sum()),
            "sum_delta_on_baseline_zero_sessions": float(delta.loc[~positive & ~negative].sum()),
            "impacted_session_count": int(impacted.sum()),
            "harmful_delta_session_count": int((delta < -1e-15).sum()),
            "beneficial_delta_session_count": int((delta > 1e-15).sum()),
            "net_sum_daily_return_delta": float(delta.sum()),
        },
        "largest_missed_upside_or_added_loss_days": detail(top_missed),
        "largest_avoided_loss_or_added_upside_days": detail(top_saved),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stablecoin-raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    supply = fusion.load_stablecoin_supply(args.stablecoin_raw)
    prices = fusion.authority._fetch_prices_corrected()
    _, brrk_targets_all, _ = fusion.authority._load_frozen_targets_corrected()
    decision_start = fusion.EVALUATION_SESSION_START - pd.Timedelta(days=1)
    mask = (brrk_targets_all.index >= decision_start) & (brrk_targets_all.index <= fusion.EVALUATION_SESSION_END)
    base_targets = brrk_targets_all.loc[mask, list(fusion.ASSETS)].copy()
    prices = prices.loc[(prices.index >= decision_start) & (prices.index <= fusion.EVALUATION_SESSION_END), list(fusion.ASSETS)].copy()
    if not base_targets.index.equals(prices.index):
        raise AuditError("canonical target/price index mismatch")

    fused_targets, _ = fusion.apply_external_path(base_targets, supply)
    base_path = fusion.simulate(base_targets, prices)
    fused_path = fusion.simulate(fused_targets, prices)
    fusion.assert_baseline_reproduction(fusion.metric_payload(base_path))
    state, cap, base_target_gross, fused_target_gross = state_for_sessions(base_targets, supply, base_path.returns.index)

    result = {
        "schema_version": 1,
        "contract_id": CONTRACT_ID,
        "classification": "NON_PROMOTABLE_DIAGNOSTIC_AUDIT",
        "evaluation": {
            "session_start": str(fusion.EVALUATION_SESSION_START.date()),
            "session_end": str(fusion.EVALUATION_SESSION_END.date()),
            "cost_bps": fusion.COST_BPS,
            "p3_3_band": fusion.BAND,
        },
        "canonical_baseline_reproduced": True,
        "canonical_metrics": fusion.metric_payload(base_path),
        "daily_distribution": distribution_metrics(base_path.returns),
        "active_daily_distribution": distribution_metrics(base_path.returns, base_path.gross_exposure),
        "holding_cycle_distribution": cycle_metrics(base_path),
        "return_concentration": concentration_metrics(base_path.returns),
        "external_fusion_attribution": external_attribution(base_path, fused_path, state, cap, base_target_gross, fused_target_gross),
        "interpretation_boundary": "Descriptive attribution only. No threshold, state, cap, BRRK, P3.3, routing, or execution parameter was searched or changed.",
        "promotion_eligible": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
