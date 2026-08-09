from __future__ import annotations

"""Deterministic, read-only diagnostic attribution for frozen BRRK history.

This module is intentionally a governance/observability audit, not a new strategy
experiment and not promotion evidence.  It reads only committed historical
artifacts and does not modify canonical BRRK mathematics, Phase-6 observation,
or production authority.

The audit separates quantities that are mechanically measurable from the frozen
artifacts from quantities that are not reconstructable without inventing missing
historical state:

* V1 -> BRRK defensive scaling: measurable when normalized target mixes match.
* target concentration / cap signatures / BTC reserve: measurable structurally.
* target-vector change frequency: measurable structurally.
* signal-speed causal attribution: unavailable because historical P3.2 feature
  snapshots are not persisted in PIT-DISP-0015.
* historical P3.3 execution-band attribution: unavailable because account
  position weights / l1_target_gap / controller plans are not persisted.
"""

from dataclasses import dataclass
from pathlib import Path
import json
import math
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_PATH = ROOT / "research/results/pit_disp_0015/daily_weights.csv"
EQUITY_PATH = ROOT / "research/results/pit_disp_0015/daily_equity.csv"
ASSETS = ("BTC", "ETH", "SOL", "BNB")
EPS = 1e-9
MIX_TOL = 1e-6


@dataclass(frozen=True)
class SeriesStats:
    total_return: float
    cagr: float
    max_drawdown: float


def _calendar_years(index: pd.DatetimeIndex) -> float:
    if len(index) < 2:
        return float("nan")
    days = (index[-1] - index[0]).total_seconds() / 86400.0
    return days / 365.25 if days > 0 else float("nan")


def _series_stats(nav: pd.Series) -> SeriesStats:
    nav = nav.dropna().astype(float)
    years = _calendar_years(pd.DatetimeIndex(nav.index))
    total = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    cagr = float((nav.iloc[-1] / nav.iloc[0]) ** (1.0 / years) - 1.0) if years > 0 else float("nan")
    dd = nav / nav.cummax() - 1.0
    return SeriesStats(total, cagr, float(dd.min()))


def _gap_days(mask: pd.Series) -> dict[str, float | int | None]:
    idx = pd.DatetimeIndex(mask.index[mask.astype(bool)])
    if len(idx) < 2:
        return {"events": int(len(idx)), "median_days": None, "p90_days": None, "max_days": None}
    gaps = np.diff(idx.values).astype("timedelta64[D]").astype(float)
    return {
        "events": int(len(idx)),
        "median_days": float(np.median(gaps)),
        "p90_days": float(np.quantile(gaps, 0.90)),
        "max_days": float(np.max(gaps)),
    }


def _safe_ratio(a: float, b: float) -> float | None:
    return float(a / b) if math.isfinite(a) and math.isfinite(b) and abs(b) > EPS else None


def run_audit() -> dict[str, Any]:
    w = pd.read_csv(WEIGHTS_PATH, parse_dates=["date"]).set_index("date").sort_index()
    e = pd.read_csv(EQUITY_PATH, parse_dates=["date"]).set_index("date").sort_index()

    v1_cols = [f"V1_BASELINE__{asset}" for asset in ASSETS]
    brrk_cols = [f"BRRK0011_BASELINE__{asset}" for asset in ASSETS]
    required_w = set(v1_cols + brrk_cols)
    required_e = {"V1_BASELINE", "BRRK0011_BASELINE"}
    missing_w = sorted(required_w.difference(w.columns))
    missing_e = sorted(required_e.difference(e.columns))
    if missing_w or missing_e:
        raise RuntimeError(f"missing canonical columns weights={missing_w} equity={missing_e}")

    v1 = w[v1_cols].copy()
    v1.columns = list(ASSETS)
    brrk = w[brrk_cols].copy()
    brrk.columns = list(ASSETS)
    v1_gross = v1.abs().sum(axis=1)
    brrk_gross = brrk.abs().sum(axis=1)

    overlap = (v1_gross > EPS) & (brrk_gross > EPS)
    v1_mix = v1.loc[overlap].div(v1_gross.loc[overlap], axis=0)
    brrk_mix = brrk.loc[overlap].div(brrk_gross.loc[overlap], axis=0)
    residual = (v1_mix - brrk_mix).abs()
    max_mix_residual = float(residual.to_numpy().max()) if len(residual) else float("nan")
    p999_mix_residual = float(np.quantile(residual.to_numpy().ravel(), 0.999)) if len(residual) else float("nan")
    decomposition_valid = bool(len(residual) and max_mix_residual <= MIX_TOL)

    scale = (brrk_gross.loc[overlap] / v1_gross.loc[overlap]).replace([np.inf, -np.inf], np.nan).dropna()
    cash_created = (v1_gross - brrk_gross).loc[overlap]

    v1_stats = _series_stats(e["V1_BASELINE"])
    brrk_stats = _series_stats(e["BRRK0011_BASELINE"])
    defensive_cagr_delta_pp = 100.0 * (brrk_stats.cagr - v1_stats.cagr)
    defensive_mdd_delta_pp = 100.0 * (brrk_stats.max_drawdown - v1_stats.max_drawdown)

    v1_ret = e["V1_BASELINE"].pct_change(fill_method=None)
    brrk_ret = e["BRRK0011_BASELINE"].pct_change(fill_method=None)
    common_ret = pd.concat({"v1": v1_ret, "brrk": brrk_ret}, axis=1).dropna()
    top_n = min(20, len(common_ret))
    bottom_n = min(20, len(common_ret))
    top_idx = common_ret["v1"].nlargest(top_n).index
    bottom_idx = common_ret["v1"].nsmallest(bottom_n).index
    top_v1_log = float(np.log1p(common_ret.loc[top_idx, "v1"]).sum())
    top_brrk_log = float(np.log1p(common_ret.loc[top_idx, "brrk"]).sum())
    bottom_v1_log = float(np.log1p(common_ret.loc[bottom_idx, "v1"]).sum())
    bottom_brrk_log = float(np.log1p(common_ret.loc[bottom_idx, "brrk"]).sum())

    alt_total = v1[["ETH", "SOL", "BNB"]].abs().sum(axis=1)
    alt_active = (v1_gross > EPS) & (alt_total > EPS)
    btc_share = (v1.loc[alt_active, "BTC"] / v1_gross.loc[alt_active]).replace([np.inf, -np.inf], np.nan).dropna()
    asset_share = v1.div(v1_gross.replace(0.0, np.nan), axis=0)

    cap_levels = {"ETH": 0.50, "SOL": 0.35, "BNB": 0.25}
    cap_signature: dict[str, Any] = {}
    for asset, cap in cap_levels.items():
        active = asset_share[asset].notna() & (v1[asset].abs() > EPS)
        values = asset_share.loc[active, asset]
        hit = (values - cap).abs() <= 1e-6
        cap_signature[asset] = {
            "active_days": int(active.sum()),
            "cap_share_of_gross": cap,
            "exact_cap_signature_days": int(hit.sum()),
            "exact_cap_signature_rate_active": float(hit.mean()) if len(hit) else None,
            "median_share_of_gross_when_active": float(values.median()) if len(values) else None,
            "p90_share_of_gross_when_active": float(values.quantile(0.90)) if len(values) else None,
        }

    v1_l1 = v1.diff().abs().sum(axis=1).fillna(v1.abs().sum(axis=1))
    brrk_l1 = brrk.diff().abs().sum(axis=1).fillna(brrk.abs().sum(axis=1))
    v1_change = v1_l1 > EPS
    brrk_change = brrk_l1 > EPS

    report: dict[str, Any] = {
        "audit_id": "BRRK-OPPORTUNITY-COST-AUDIT-0042",
        "status": "DIAGNOSTIC_ONLY_NO_PROMOTION_AUTHORITY",
        "source_paths": [str(WEIGHTS_PATH.relative_to(ROOT)), str(EQUITY_PATH.relative_to(ROOT))],
        "window": {"start": str(w.index.min().date()), "end": str(w.index.max().date()), "rows": int(len(w))},
        "mechanical_decomposition": {
            "v1_to_brrk_normalized_mix_match": decomposition_valid,
            "overlap_days": int(overlap.sum()),
            "v1_active_brrk_zero_days": int(((v1_gross > EPS) & (brrk_gross <= EPS)).sum()),
            "max_abs_normalized_weight_mix_residual": max_mix_residual,
            "p999_abs_normalized_weight_mix_residual": p999_mix_residual,
            "interpretation": (
                "When true, BRRK target composition matches V1 composition and the observable difference is gross defensive scaling."
                if decomposition_valid
                else "Frozen artifacts do not support treating V1->BRRK as pure scalar exposure attribution on all overlap days."
            ),
        },
        "defensive_scaling": {
            "scale_mean": float(scale.mean()) if len(scale) else None,
            "scale_median": float(scale.median()) if len(scale) else None,
            "scale_p10": float(scale.quantile(0.10)) if len(scale) else None,
            "scale_p90": float(scale.quantile(0.90)) if len(scale) else None,
            "share_days_scale_lt_0_95": float((scale < 0.95).mean()) if len(scale) else None,
            "share_days_scale_lt_0_75": float((scale < 0.75).mean()) if len(scale) else None,
            "share_days_scale_lt_0_50": float((scale < 0.50).mean()) if len(scale) else None,
            "mean_gross_reduction_v1_minus_brrk": float(cash_created.mean()) if len(cash_created) else None,
            "v1_cagr": v1_stats.cagr,
            "brrk_cagr": brrk_stats.cagr,
            "brrk_minus_v1_cagr_pp": defensive_cagr_delta_pp,
            "v1_max_drawdown": v1_stats.max_drawdown,
            "brrk_max_drawdown": brrk_stats.max_drawdown,
            "brrk_minus_v1_max_drawdown_pp": defensive_mdd_delta_pp,
            "top20_v1_days_log_growth_capture_ratio": _safe_ratio(top_brrk_log, top_v1_log),
            "bottom20_v1_days_log_loss_ratio": _safe_ratio(bottom_brrk_log, bottom_v1_log),
        },
        "portfolio_structure": {
            "alt_active_days": int(alt_active.sum()),
            "btc_share_of_gross_on_alt_active_days_median": float(btc_share.median()) if len(btc_share) else None,
            "btc_share_of_gross_on_alt_active_days_p25": float(btc_share.quantile(0.25)) if len(btc_share) else None,
            "btc_share_of_gross_on_alt_active_days_p75": float(btc_share.quantile(0.75)) if len(btc_share) else None,
            "share_alt_active_days_btc_ge_25pct_gross": float((btc_share >= 0.25 - 1e-6).mean()) if len(btc_share) else None,
            "share_alt_active_days_btc_ge_50pct_gross": float((btc_share >= 0.50 - 1e-6).mean()) if len(btc_share) else None,
            "cap_signatures": cap_signature,
        },
        "target_inertia": {
            "v1_target_change": _gap_days(v1_change),
            "brrk_target_change": _gap_days(brrk_change),
            "v1_change_day_share": float(v1_change.mean()),
            "brrk_change_day_share": float(brrk_change.mean()),
            "v1_l1_change_median_on_change_days": float(v1_l1[v1_change].median()) if v1_change.any() else None,
            "brrk_l1_change_median_on_change_days": float(brrk_l1[brrk_change].median()) if brrk_change.any() else None,
        },
        "unavailable_attribution": {
            "signal_speed_causal_attribution": "UNAVAILABLE_HISTORICAL_P3_2_SIGNAL_SNAPSHOTS_NOT_PERSISTED",
            "historical_p3_3_5pct_band_return_attribution": "UNAVAILABLE_ACCOUNT_POSITION_WEIGHTS_AND_L1_GAP_NOT_PERSISTED",
            "winner_cap_return_counterfactual": "NOT_RUN_THIS_AUDIT_STRUCTURAL_FREQUENCY_ONLY",
        },
        "authority": {
            "canonical_strategy_changed": False,
            "phase6_observation_changed": False,
            "production_authorized": False,
            "promotion_authority": False,
        },
    }
    return report


def main() -> int:
    print(json.dumps(run_audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
