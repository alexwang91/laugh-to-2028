from __future__ import annotations

"""Execute the exactly-one preregistered BRRK-WINNER-0001 development candidate.

The runner reuses the frozen BRRK raw-target authority and the exact matched P3.3
5 bps / 5% L1-band simulator used by the prior attribution audit. It must abort
before candidate metric release if canonical baseline reproduction fails.
"""

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

from research.governance import run_dual_layer_fusion_sanity_once as fusion


RESEARCH_ID = "BRRK-WINNER-0001"
RUN_INTERFACE_ID = "BRRK-WINNER-0001-RUN-ONCE-V1"
ASSETS = tuple(fusion.ASSETS)
ALTS = tuple(a for a in ASSETS if a != "BTC")
EPS = 1e-10
BTC_SHARE = 0.40
WINNER_SHARE = 0.60


class RunError(RuntimeError):
    pass


def _slice_authority() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series]:
    prices = fusion.authority._fetch_prices_corrected()
    v1_all, brrk_all, scale_all = fusion.authority._load_frozen_targets_corrected()
    decision_start = fusion.EVALUATION_SESSION_START - pd.Timedelta(days=1)
    mask = (brrk_all.index >= decision_start) & (brrk_all.index <= fusion.EVALUATION_SESSION_END)
    v1 = v1_all.loc[mask, list(ASSETS)].copy().astype(float)
    brrk = brrk_all.loc[mask, list(ASSETS)].copy().astype(float)
    scale = scale_all.loc[v1.index].astype(float)
    prices = prices.loc[(prices.index >= decision_start) & (prices.index <= fusion.EVALUATION_SESSION_END), list(ASSETS)].copy().astype(float)
    if not v1.index.equals(brrk.index) or not brrk.index.equals(prices.index):
        raise RunError("canonical V1/BRRK/price decision index mismatch")
    return prices, v1, brrk, scale


def _single_alt_mask(v1: pd.DataFrame) -> tuple[pd.Series, dict[pd.Timestamp, str]]:
    mask = pd.Series(False, index=v1.index)
    winner: dict[pd.Timestamp, str] = {}
    for dt, row in v1.iterrows():
        active_alts = [a for a in ALTS if float(row[a]) > EPS]
        if float(row["BTC"]) <= EPS or len(active_alts) != 1:
            continue
        alt = active_alts[0]
        gross = float(row[list(ASSETS)].sum())
        if gross <= EPS:
            raise RunError(f"single-alt V1 row has nonpositive gross: {dt}")
        btc_share = float(row["BTC"] / gross)
        alt_share = float(row[alt] / gross)
        if not math.isclose(btc_share, 0.50, rel_tol=0.0, abs_tol=1e-9) or not math.isclose(alt_share, 0.50, rel_tol=0.0, abs_tol=1e-9):
            raise RunError(
                f"single-alt branch composition drift at {pd.Timestamp(dt).date()}: "
                f"BTC={btc_share:.12f} {alt}={alt_share:.12f}"
            )
        mask.loc[dt] = True
        winner[pd.Timestamp(dt)] = alt
    if not bool(mask.any()):
        raise RunError("no frozen single-alt rows found")
    return mask, winner


def _candidate_targets(v1: pd.DataFrame, brrk: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict[str, int]]:
    single, winner = _single_alt_mask(v1)
    out = brrk.copy()
    counts = {a: 0 for a in ALTS}
    for dt in v1.index[single]:
        gross = float(brrk.loc[dt, list(ASSETS)].sum())
        alt = winner[pd.Timestamp(dt)]
        out.loc[dt, list(ASSETS)] = 0.0
        out.loc[dt, "BTC"] = BTC_SHARE * gross
        out.loc[dt, alt] = WINNER_SHARE * gross
        counts[alt] += 1

    non_single = ~single
    residual = float((out.loc[non_single, list(ASSETS)] - brrk.loc[non_single, list(ASSETS)]).abs().to_numpy().max()) if bool(non_single.any()) else 0.0
    if residual > EPS:
        raise RunError(f"non-single-alt target row changed: max residual={residual}")
    if (out < -EPS).any().any():
        raise RunError("candidate target became short")
    gross = out.sum(axis=1)
    if (gross > 1.0 + 1e-9).any():
        raise RunError(f"candidate target gross exceeded 1.0: max={float(gross.max())}")
    base_gross = brrk.sum(axis=1)
    if float((gross - base_gross).abs().max()) > 1e-9:
        raise RunError("candidate changed BRRK defensive gross")
    return out, single, counts


def _top20_capture(base_returns: pd.Series, candidate_returns: pd.Series) -> tuple[float, list[str], float, float]:
    dates = base_returns.nlargest(20).index
    base_log = float(np.log1p(base_returns.loc[dates].astype(float)).sum())
    candidate_log = float(np.log1p(candidate_returns.loc[dates].astype(float)).sum())
    if base_log <= 0:
        raise RunError("canonical best-20 log-growth denominator is nonpositive")
    return float(candidate_log / base_log), [str(pd.Timestamp(x).date()) for x in dates], base_log, candidate_log


def _gate_payload(base: dict[str, float], cand: dict[str, float], capture: float, target_gross_max: float, target_min_weight: float) -> tuple[dict[str, object], bool]:
    cagr_delta_pp = float((cand["cagr"] - base["cagr"]) * 100.0)
    mdd_deterioration_pp = float(max(0.0, (base["max_drawdown"] - cand["max_drawdown"]) * 100.0))
    turnover_ratio = float(cand["turnover"] / base["turnover"])
    gates: dict[str, object] = {
        "cagr_delta_pp_min_3": {"value": cagr_delta_pp, "threshold": 3.0, "pass": cagr_delta_pp >= 3.0 - 1e-12},
        "max_drawdown_deterioration_pp_max_4": {"value": mdd_deterioration_pp, "threshold": 4.0, "pass": mdd_deterioration_pp <= 4.0 + 1e-12},
        "calmar_not_below_baseline": {"value": float(cand["calmar"] / base["calmar"]), "threshold": 1.0, "pass": cand["calmar"] >= base["calmar"] - 1e-12},
        "canonical_best20_log_growth_capture_min_0_98": {"value": capture, "threshold": 0.98, "pass": capture >= 0.98 - 1e-12},
        "turnover_ratio_max_1_25": {"value": turnover_ratio, "threshold": 1.25, "pass": turnover_ratio <= 1.25 + 1e-12},
        "long_only": {"value": target_min_weight, "threshold": 0.0, "pass": target_min_weight >= -EPS},
        "gross_max_1": {"value": target_gross_max, "threshold": 1.0, "pass": target_gross_max <= 1.0 + 1e-9},
    }
    passed = all(bool(v["pass"]) for v in gates.values())
    return gates, passed


def run() -> dict[str, object]:
    prices, v1, base_targets, defensive_scale = _slice_authority()

    # Fail closed before candidate construction/metric release if baseline parity is lost.
    base_path = fusion.simulate(base_targets, prices)
    base_metrics = fusion.metric_payload(base_path)
    fusion.assert_baseline_reproduction(base_metrics)

    candidate_targets, single_mask, winner_counts = _candidate_targets(v1, base_targets)
    candidate_path = fusion.simulate(candidate_targets, prices)
    candidate_metrics = fusion.metric_payload(candidate_path)

    capture, top20_dates, top20_base_log, top20_candidate_log = _top20_capture(
        base_path.returns.astype(float), candidate_path.returns.astype(float)
    )
    target_gross = candidate_targets.sum(axis=1)
    gates, all_pass = _gate_payload(
        base_metrics,
        candidate_metrics,
        capture,
        float(target_gross.max()),
        float(candidate_targets.min().min()),
    )

    return {
        "schema_version": 1,
        "research_id": RESEARCH_ID,
        "run_interface_id": RUN_INTERFACE_ID,
        "result_status": "PASS_ROBUSTNESS_STAGE_ELIGIBLE" if all_pass else "FAIL_NO_PROMOTION",
        "baseline_reproduced": True,
        "variant_budget": 1,
        "actual_variants_evaluated": 1,
        "retuning_performed": False,
        "evaluation": {
            "session_start": str(fusion.EVALUATION_SESSION_START.date()),
            "session_end": str(fusion.EVALUATION_SESSION_END.date()),
            "cost_bps": fusion.COST_BPS,
            "p3_3_l1_band": fusion.BAND,
        },
        "candidate_definition": {
            "single_alt_btc_share": BTC_SHARE,
            "single_alt_winner_share": WINNER_SHARE,
            "same_defensive_gross": True,
            "single_alt_decision_rows": int(single_mask.sum()),
            "single_alt_winner_counts": winner_counts,
            "other_decision_rows_unchanged": int((~single_mask).sum()),
        },
        "input_evidence": {
            "target_authority": fusion.authority._target_authority_meta,
            "canonical_brrk_target_frame_sha256": fusion.frame_sha256(base_targets),
            "candidate_target_frame_sha256": fusion.frame_sha256(candidate_targets),
            "defensive_scale_min": float(defensive_scale.min()),
            "defensive_scale_max": float(defensive_scale.max()),
            "historical_role": "RESEARCHER_EXPOSED_DEVELOPMENT",
        },
        "baseline": base_metrics,
        "candidate": candidate_metrics,
        "delta": {k: float(candidate_metrics[k] - base_metrics[k]) for k in base_metrics},
        "right_tail": {
            "canonical_best20_dates": top20_dates,
            "canonical_best20_log_growth": top20_base_log,
            "candidate_log_growth_on_same_dates": top20_candidate_log,
            "capture_ratio": capture,
        },
        "hard_gates": gates,
        "all_hard_gates_pass": all_pass,
        "execution_evidence": {
            "github_run_id": os.getenv("GITHUB_RUN_ID"),
            "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "workflow_sha": os.getenv("GITHUB_SHA"),
            "head_ref": os.getenv("GITHUB_REF_NAME"),
        },
        "promotion_authority": "ROBUSTNESS_STAGE_ELIGIBILITY_ONLY" if all_pass else "NONE",
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
