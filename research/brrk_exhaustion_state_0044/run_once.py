from __future__ import annotations

"""Exactly-once diagnostic runner for BRRK-EXHAUSTION-STATE-0044.

This module implements only the frozen low-dimensional exhaustion-state study.
It does not define a trading trigger, alter targets, simulate portfolio gross,
or create any production/signing/order authority.
"""

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from research.governance import brrk_exhaustion_event_study as e0043

RESEARCH_ID = "BRRK-EXHAUSTION-STATE-0044"
FROZEN_EVAL_END = pd.Timestamp("2026-08-02")
PRIMARY_DOWNSIDE = 0.15
SEVERE_DOWNSIDE = 0.20
DOWNSIDE_PANELS = (0.10, 0.15, 0.20)
EXPECTED_0043_CANDIDATE_COUNT = 16
EXPECTED_0043_PANEL_COUNTS = {
    0.10: {"TRUE_EXHAUSTION": 12, "CONTINUATION_FALSE_TOP": 4, "AMBIGUOUS": 0},
    0.15: {"TRUE_EXHAUSTION": 9, "CONTINUATION_FALSE_TOP": 6, "AMBIGUOUS": 1},
    0.20: {"TRUE_EXHAUSTION": 7, "CONTINUATION_FALSE_TOP": 6, "AMBIGUOUS": 3},
}

AXIS_FEATURES = {
    "S1_MOMENTUM_DECELERATION": (
        "f1_trend_decay7",
        "f1_macd_hist_decay5",
    ),
    "S2_TREND_DISAGREEMENT": (
        "f7_slow_fast_disagreement",
        "f7_disagreement_persistence",
    ),
    "S3_PRICE_STRUCTURE": (
        "f2_prior_peak_shortfall",
        "f2_days_since_high60",
        "f2_ma20_slope10",
    ),
    "S4_VOL_DOWNSIDE": (
        "f4_rv10_vs_rv30",
        "f4_down_up_semivol",
        "f4_pnl_dd_duration_interaction",
    ),
    "S5_VOLUME_CONFIRMATION": (
        "f3_down_up_volume_ratio",
        "f3_price_obv_divergence20",
    ),
}
PRIMARY_AXES = (
    "S1_MOMENTUM_DECELERATION",
    "S2_TREND_DISAGREEMENT",
    "S3_PRICE_STRUCTURE",
    "S4_VOL_DOWNSIDE",
)
SECONDARY_AXES = PRIMARY_AXES + ("S5_VOLUME_CONFIRMATION",)
WINDOWS = {
    "PRE14_7": (-14, -7),
    "PRE7_0": (-7, 0),
}


class RunInvalid(RuntimeError):
    """Execution-invalid condition; it is not a research PASS/FAIL result."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json_sha(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _series_sha(series: pd.Series) -> str:
    clean = series.sort_index().astype(float)
    rows = [[str(pd.Timestamp(idx).date()), None if not np.isfinite(value) else float(value)] for idx, value in clean.items()]
    return _json_sha(rows)


def _market_sha(market: dict[str, pd.DataFrame]) -> dict[str, str]:
    result: dict[str, str] = {}
    for asset in e0043.ASSETS:
        frame = market[asset].loc[market[asset].index <= FROZEN_EVAL_END, ["open", "high", "low", "close", "volume"]].copy()
        rows = []
        for idx, row in frame.iterrows():
            rows.append(
                [
                    str(pd.Timestamp(idx).date()),
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    float(row["volume"]),
                ]
            )
        result[asset] = _json_sha(rows)
    return result


def build_state_axes(scores_0043: pd.DataFrame) -> pd.DataFrame:
    z = scores_0043.attrs.get("z_features")
    if not isinstance(z, pd.DataFrame):
        raise RunInvalid("0043 z_features missing from build_features output")
    state = pd.DataFrame(index=z.index)
    for axis, cols in AXIS_FEATURES.items():
        missing = [c for c in cols if c not in z.columns]
        if missing:
            raise RunInvalid(f"missing frozen raw-z feature(s) for {axis}: {missing}")
        state[axis] = z[list(cols)].mean(axis=1, skipna=True)
    state["CORE4"] = state[list(PRIMARY_AXES)].mean(axis=1, skipna=True)
    state["CORE5"] = state[list(SECONDARY_AXES)].mean(axis=1, skipna=True)
    return state


def reproduce_0043_taxonomy(nav: pd.Series) -> tuple[list[pd.Timestamp], dict[float, list[dict[str, object]]], dict[str, object]]:
    nav = nav.loc[nav.index <= FROZEN_EVAL_END].dropna().sort_index()
    candidates = e0043.detect_candidates(nav)
    if len(candidates) != EXPECTED_0043_CANDIDATE_COUNT:
        raise RunInvalid(
            f"0043 candidate reproduction mismatch: expected {EXPECTED_0043_CANDIDATE_COUNT}, got {len(candidates)}"
        )
    panels: dict[float, list[dict[str, object]]] = {}
    observed_counts: dict[str, dict[str, int]] = {}
    for downside in DOWNSIDE_PANELS:
        rows: list[dict[str, object]] = []
        counts = {"TRUE_EXHAUSTION": 0, "CONTINUATION_FALSE_TOP": 0, "AMBIGUOUS": 0}
        for peak in candidates:
            classified = e0043.classify_event(nav, peak, downside)
            label = str(classified["label"])
            counts[label] += 1
            rows.append({"peak": peak, **classified})
        if counts != EXPECTED_0043_PANEL_COUNTS[downside]:
            raise RunInvalid(
                f"0043 label reproduction mismatch at downside={downside}: expected {EXPECTED_0043_PANEL_COUNTS[downside]}, got {counts}"
            )
        panels[downside] = rows
        observed_counts[f"down_{int(downside * 100)}pct"] = counts
    reproduction = {
        "candidate_peak_count": len(candidates),
        "candidate_peaks": [str(p.date()) for p in candidates],
        "panel_counts": observed_counts,
        "status": "MATCHED_0043_FROZEN_TAXONOMY",
    }
    return candidates, panels, reproduction


def assign_macro_episodes(nav: pd.Series, candidates: list[pd.Timestamp]) -> tuple[dict[pd.Timestamp, int], list[dict[str, object]]]:
    nav = nav.loc[nav.index <= FROZEN_EVAL_END].dropna().sort_index()
    mapping: dict[pd.Timestamp, int] = {}
    metadata: list[dict[str, object]] = []
    episode_id = -1
    anchor: pd.Timestamp | None = None
    recovery: pd.Timestamp | None = None

    for peak in sorted(candidates):
        if anchor is None or (recovery is not None and peak > recovery):
            episode_id += 1
            anchor = peak
            anchor_nav = float(nav.loc[anchor])
            future = nav.loc[anchor:].iloc[1:]
            hits = future.index[future >= anchor_nav * 1.02]
            recovery = pd.Timestamp(hits[0]) if len(hits) else None
            metadata.append(
                {
                    "episode_id": episode_id,
                    "anchor_peak": str(anchor.date()),
                    "anchor_nav": anchor_nav,
                    "recovery_plus2pct_date": str(recovery.date()) if recovery is not None else None,
                }
            )
        mapping[peak] = episode_id
    for item in metadata:
        eid = int(item["episode_id"])
        item["candidate_peaks"] = [str(p.date()) for p in sorted(candidates) if mapping[p] == eid]
    return mapping, metadata


def _window_mean(series: pd.Series, peak: pd.Timestamp, bounds: tuple[int, int]) -> float | None:
    value = e0043.window_mean(series, peak, bounds[0], bounds[1])
    if value is None or not np.isfinite(value):
        return None
    return float(value)


def build_event_rows(
    panel_rows: list[dict[str, object]],
    state: pd.DataFrame,
    episodes: dict[pd.Timestamp, int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    columns = list(PRIMARY_AXES) + ["S5_VOLUME_CONFIRMATION", "CORE4", "CORE5"]
    for source in panel_rows:
        peak = pd.Timestamp(source["peak"])
        row: dict[str, object] = {
            "peak": str(peak.date()),
            "episode_id": int(episodes[peak]),
            "label": source["label"],
            "down_date": source["down_date"],
            "fresh_high_date": source["fresh_high_date"],
            "min_60d_return": source["min_60d_return"],
            "max_60d_return": source["max_60d_return"],
        }
        for window, bounds in WINDOWS.items():
            for column in columns:
                row[f"{window}__{column}"] = _window_mean(state[column], peak, bounds)
        rows.append(row)
    return rows


def ordinary_auc(rows: list[dict[str, object]], score_key: str) -> dict[str, object]:
    usable = [
        r for r in rows
        if r["label"] in {"TRUE_EXHAUSTION", "CONTINUATION_FALSE_TOP"}
        and r.get(score_key) is not None
        and np.isfinite(float(r[score_key]))
    ]
    true_rows = [r for r in usable if r["label"] == "TRUE_EXHAUSTION"]
    cont_rows = [r for r in usable if r["label"] == "CONTINUATION_FALSE_TOP"]
    if not true_rows or not cont_rows:
        auc = None
    else:
        y = [1 if r["label"] == "TRUE_EXHAUSTION" else 0 for r in usable]
        x = [float(r[score_key]) for r in usable]
        auc = float(roc_auc_score(y, x))
    return {
        "auc": auc,
        "n_true": len(true_rows),
        "n_continuation": len(cont_rows),
        "true_episode_ids": sorted({int(r["episode_id"]) for r in true_rows}),
        "continuation_episode_ids": sorted({int(r["episode_id"]) for r in cont_rows}),
    }


def _concordance(true_values: list[float], cont_values: list[float]) -> float:
    vals: list[float] = []
    for t in true_values:
        for c in cont_values:
            vals.append(1.0 if t > c else 0.5 if t == c else 0.0)
    if not vals:
        raise RunInvalid("empty concordance pair")
    return float(np.mean(vals))


def cross_episode_auc(
    rows: list[dict[str, object]],
    score_key: str,
    excluded_episodes: set[int] | None = None,
) -> dict[str, object]:
    excluded = excluded_episodes or set()
    true_by_ep: dict[int, list[float]] = defaultdict(list)
    cont_by_ep: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        eid = int(row["episode_id"])
        if eid in excluded or row.get(score_key) is None:
            continue
        value = float(row[score_key])
        if not np.isfinite(value):
            continue
        if row["label"] == "TRUE_EXHAUSTION":
            true_by_ep[eid].append(value)
        elif row["label"] == "CONTINUATION_FALSE_TOP":
            cont_by_ep[eid].append(value)

    pair_rows: list[dict[str, object]] = []
    for true_ep in sorted(true_by_ep):
        for cont_ep in sorted(cont_by_ep):
            if true_ep == cont_ep:
                continue
            pair_rows.append(
                {
                    "true_episode_id": true_ep,
                    "continuation_episode_id": cont_ep,
                    "concordance": _concordance(true_by_ep[true_ep], cont_by_ep[cont_ep]),
                    "n_true_events": len(true_by_ep[true_ep]),
                    "n_continuation_events": len(cont_by_ep[cont_ep]),
                }
            )
    auc = float(np.mean([r["concordance"] for r in pair_rows])) if pair_rows else None
    return {
        "auc": auc,
        "episode_pair_count": len(pair_rows),
        "true_episode_ids": sorted(true_by_ep),
        "continuation_episode_ids": sorted(cont_by_ep),
        "pair_details": pair_rows,
    }


def leave_one_episode_out(rows: list[dict[str, object]], score_key: str) -> dict[str, object]:
    episode_ids = sorted({int(r["episode_id"]) for r in rows if r["label"] in {"TRUE_EXHAUSTION", "CONTINUATION_FALSE_TOP"}})
    checks: list[dict[str, object]] = []
    valid_values: list[float] = []
    for eid in episode_ids:
        metric = cross_episode_auc(rows, score_key, {eid})
        value = metric["auc"]
        checks.append({"excluded_episode_id": eid, "auc": value, "episode_pair_count": metric["episode_pair_count"]})
        if value is not None:
            valid_values.append(float(value))
    return {
        "checks": checks,
        "valid_check_count": len(valid_values),
        "min_auc": float(np.min(valid_values)) if valid_values else None,
        "median_auc": float(np.median(valid_values)) if valid_values else None,
        "max_auc": float(np.max(valid_values)) if valid_values else None,
    }


def axis_correlation(state: pd.DataFrame) -> dict[str, object]:
    axes = state[list(SECONDARY_AXES)].dropna(how="any")
    corr = axes.corr()
    eig = np.linalg.eigvalsh(corr.to_numpy(dtype=float)) if len(axes) else np.array([], dtype=float)
    eig = eig[eig > 1e-12]
    effective_rank = float((eig.sum() ** 2) / np.square(eig).sum()) if len(eig) else None
    return {
        "complete_daily_rows": int(len(axes)),
        "pairwise_correlation": {
            a: {b: float(corr.loc[a, b]) for b in corr.columns}
            for a in corr.index
        },
        "effective_rank_participation_ratio": effective_rank,
    }


def _gate(value: float | None, minimum: float) -> bool:
    return value is not None and np.isfinite(value) and float(value) >= minimum


def run() -> dict[str, object]:
    root = repo_root()
    prereg = json.loads((root / "research/brrk_exhaustion_state_0044/PREREGISTRATION.json").read_text(encoding="utf-8"))
    if prereg.get("research_id") != RESEARCH_ID or prereg.get("result_status") != "PREREGISTERED_NOT_RUN":
        raise RunInvalid("frozen preregistration identity/state mismatch")
    if e0043.EVAL_END != FROZEN_EVAL_END:
        raise RunInvalid(f"0043 EVAL_END drifted: {e0043.EVAL_END}")
    if e0043.DOWNSIDE_PANELS != DOWNSIDE_PANELS or e0043.PRIMARY_DOWNSIDE != PRIMARY_DOWNSIDE or e0043.FRESH_HIGH != 0.02:
        raise RunInvalid("0043 frozen event taxonomy constants drifted")

    market = e0043.load_market()
    nav, defensive_scale = e0043.load_canonical()
    nav = nav.loc[nav.index <= FROZEN_EVAL_END]
    defensive_scale = defensive_scale.loc[defensive_scale.index <= FROZEN_EVAL_END]

    scores_0043, _ = e0043.build_features(market, nav, defensive_scale)
    state = build_state_axes(scores_0043)
    candidates, panels, reproduction = reproduce_0043_taxonomy(nav)
    episode_map, episode_metadata = assign_macro_episodes(nav, candidates)

    panel_output: dict[str, object] = {}
    for downside in DOWNSIDE_PANELS:
        name = f"down_{int(downside * 100)}pct"
        rows = build_event_rows(panels[downside], state, episode_map)
        metrics: dict[str, object] = {}
        for window in WINDOWS:
            metrics[window] = {}
            for score in (*PRIMARY_AXES, "S5_VOLUME_CONFIRMATION", "CORE4", "CORE5"):
                key = f"{window}__{score}"
                metrics[window][score] = {
                    "event_level": ordinary_auc(rows, key),
                    "cross_episode": cross_episode_auc(rows, key),
                }
        panel_output[name] = {"events": rows, "metrics": metrics}

    primary_rows = panel_output["down_15pct"]["events"]
    primary_metric = panel_output["down_15pct"]["metrics"]["PRE14_7"]["CORE4"]
    severe_metric = panel_output["down_20pct"]["metrics"]["PRE14_7"]["CORE4"]
    primary_pre7 = panel_output["down_15pct"]["metrics"]["PRE7_0"]["CORE4"]
    core5_pre14 = panel_output["down_15pct"]["metrics"]["PRE14_7"]["CORE5"]
    core5_pre7 = panel_output["down_15pct"]["metrics"]["PRE7_0"]["CORE5"]
    loeo = leave_one_episode_out(primary_rows, "PRE14_7__CORE4")

    primary_event = primary_metric["event_level"]
    primary_cross = primary_metric["cross_episode"]
    severe_cross = severe_metric["cross_episode"]
    true_eps = primary_event["true_episode_ids"]
    cont_eps = primary_event["continuation_episode_ids"]
    usable_eps = sorted(set(true_eps) | set(cont_eps))
    diversity_pass = len(usable_eps) >= 4 and len(true_eps) >= 2 and len(cont_eps) >= 2

    gates = {
        "episode_diversity": {
            "pass": diversity_pass,
            "usable_episode_count": len(usable_eps),
            "true_episode_count": len(true_eps),
            "continuation_episode_count": len(cont_eps),
        },
        "primary_cross_episode_auc_ge_0_70": {
            "pass": _gate(primary_cross["auc"], 0.70),
            "value": primary_cross["auc"],
        },
        "primary_event_auc_ge_0_68": {
            "pass": _gate(primary_event["auc"], 0.68),
            "value": primary_event["auc"],
        },
        "severe_cross_episode_auc_ge_0_75": {
            "pass": _gate(severe_cross["auc"], 0.75),
            "value": severe_cross["auc"],
        },
        "loeo_min_ge_0_55": {"pass": _gate(loeo["min_auc"], 0.55), "value": loeo["min_auc"]},
        "loeo_median_ge_0_68": {"pass": _gate(loeo["median_auc"], 0.68), "value": loeo["median_auc"]},
        "construction_and_authority": {
            "pass": len(PRIMARY_AXES) == 4,
            "primary_axes": list(PRIMARY_AXES),
            "equal_weight": True,
            "fitted_weights": False,
            "portfolio_economics_executed": False,
            "trigger_defined": False,
            "canonical_strategy_changed": False,
            "phase6_observation_changed": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }

    if not diversity_pass:
        result_status = "INSUFFICIENT_EPISODE_DIVERSITY"
    elif all(bool(item["pass"]) for item in gates.values()):
        result_status = "PASS_TRIGGER_STAGE_ELIGIBLE"
    else:
        result_status = "FAIL_NO_TRIGGER_STAGE_ELIGIBILITY"

    core4_pre14_value = primary_cross["auc"]
    core5_pre14_value = core5_pre14["cross_episode"]["auc"]
    core4_pre7_value = primary_pre7["cross_episode"]["auc"]
    core5_pre7_value = core5_pre7["cross_episode"]["auc"]

    result: dict[str, object] = {
        "research_id": RESEARCH_ID,
        "result_status": result_status,
        "window": {"start": str(scores_0043.index.min().date()), "end": str(scores_0043.index.max().date()), "sessions": int(len(scores_0043))},
        "frozen_construction": {
            "axis_features": {k: list(v) for k, v in AXIS_FEATURES.items()},
            "primary_axes": list(PRIMARY_AXES),
            "core4": "EQUAL_WEIGHT_MEAN_OF_S1_S2_S3_S4",
            "core5": "EQUAL_WEIGHT_MEAN_OF_S1_S2_S3_S4_S5_SECONDARY_ONLY",
            "normalization": "0043_TRAILING_252_MIN60_Z_CLIP_MINUS3_PLUS3",
            "trigger_defined": False,
            "portfolio_economics_executed": False,
        },
        "source_integrity": {
            "0043_taxonomy_reproduction": reproduction,
            "market_ohlcv_sha256": _market_sha(market),
            "canonical_nav_sha256": _series_sha(nav),
            "canonical_defensive_scale_sha256": _series_sha(defensive_scale),
            "preregistration_sha256": hashlib.sha256((root / "research/brrk_exhaustion_state_0044/PREREGISTRATION.json").read_bytes()).hexdigest(),
        },
        "episodes": episode_metadata,
        "panels": panel_output,
        "primary_summary": {
            "primary_15_PRE14_7_CORE4_cross_episode_auc": primary_cross["auc"],
            "primary_15_PRE14_7_CORE4_event_auc": primary_event["auc"],
            "severe_20_PRE14_7_CORE4_cross_episode_auc": severe_cross["auc"],
            "primary_15_PRE7_0_CORE4_cross_episode_auc": primary_pre7["cross_episode"]["auc"],
            "loeo_primary_PRE14_7_CORE4": loeo,
            "CORE5_incremental_cross_episode_auc": {
                "PRE14_7_CORE4": core4_pre14_value,
                "PRE14_7_CORE5": core5_pre14_value,
                "PRE14_7_delta_CORE5_minus_CORE4": None if core4_pre14_value is None or core5_pre14_value is None else float(core5_pre14_value - core4_pre14_value),
                "PRE7_0_CORE4": core4_pre7_value,
                "PRE7_0_CORE5": core5_pre7_value,
                "PRE7_0_delta_CORE5_minus_CORE4": None if core4_pre7_value is None or core5_pre7_value is None else float(core5_pre7_value - core4_pre7_value),
            },
        },
        "state_axis_correlation": axis_correlation(state),
        "gates": gates,
        "authority": {
            "researcher_exposed_development_only": True,
            "independent_oos": False,
            "trigger_stage_eligible": result_status == "PASS_TRIGGER_STAGE_ELIGIBLE",
            "portfolio_economics_executed": False,
            "canonical_strategy_changed": False,
            "phase6_observation_changed": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }
    result["result_payload_sha256_without_self_hash"] = _json_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("BRRK_EXHAUSTION_STATE_0044_RESULT=" + json.dumps({
        "research_id": result["research_id"],
        "result_status": result["result_status"],
        "primary_summary": result["primary_summary"],
        "gates": result["gates"],
        "authority": result["authority"],
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
