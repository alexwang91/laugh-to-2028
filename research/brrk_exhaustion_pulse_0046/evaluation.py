from __future__ import annotations

"""Outcome evaluation for 0046. This module is imported only after lock proof."""

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_exhaustion_state_0044 import run_once as s0044
from research.governance import brrk_exhaustion_event_study as e0043

from . import detector
from .predictor_io import PRIMARY_AXES, PredictorArtifact, read_predictor_artifact

RESEARCH_ID = "BRRK-EXHAUSTION-PULSE-0046"
FROZEN_EVAL_END = pd.Timestamp("2026-08-02")
WINDOWS = {"PRE14_7": (-14, -7), "PRE14_0": (-14, 0), "PRE21_0": (-21, 0)}
PRIMARY_DOWNSIDE = 0.15
SEVERE_DOWNSIDE = 0.20
EVENT_BOOTSTRAP_REPLICATES = 10_000
EVENT_BOOTSTRAP_SEED = 460047
DAILY_BOOTSTRAP_REPLICATES = 10_000
DAILY_BOOTSTRAP_SEED = 460048
DAILY_BLOCK_LENGTH = 21
CI_LOW = 2.5
CI_HIGH = 97.5


class EvaluationInvalid(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json_sha(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _window_positions(index: pd.Index, peak: pd.Timestamp, bounds: tuple[int, int]) -> list[int]:
    if peak not in index:
        raise EvaluationInvalid(f"frozen event peak missing from detector index: {peak.date()}")
    pos = int(index.get_loc(peak))
    lo = pos + bounds[0]
    hi = pos + bounds[1]
    if lo < 0 or hi >= len(index):
        raise EvaluationInvalid(f"incomplete frozen session window {bounds} for peak {peak.date()}")
    return list(range(lo, hi + 1))


def _any_pulse(pulse: np.ndarray, index: pd.Index, peak: pd.Timestamp, bounds: tuple[int, int]) -> bool:
    return any(bool(pulse[i]) for i in _window_positions(index, peak, bounds))


def _earliest_pulse(
    pulse: np.ndarray, index: pd.Index, peak: pd.Timestamp, bounds: tuple[int, int]
) -> tuple[str | None, int | None]:
    peak_pos = int(index.get_loc(peak))
    for pos in _window_positions(index, peak, bounds):
        if bool(pulse[pos]):
            return str(pd.Timestamp(index[pos]).date()), int(peak_pos - pos)
    return None, None


def _event_rows(
    panel_rows: list[dict[str, object]],
    episode_map: dict[pd.Timestamp, int],
    pulse: np.ndarray,
    index: pd.Index,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for src in panel_rows:
        peak = pd.Timestamp(src["peak"])
        onset_date, lead = _earliest_pulse(pulse, index, peak, WINDOWS["PRE21_0"])
        rows.append(
            {
                "peak": str(peak.date()),
                "episode_id": int(episode_map[peak]),
                "label": str(src["label"]),
                "down_date": src["down_date"],
                "fresh_high_date": src["fresh_high_date"],
                "PRE14_7_pulse": _any_pulse(pulse, index, peak, WINDOWS["PRE14_7"]),
                "PRE14_0_pulse": _any_pulse(pulse, index, peak, WINDOWS["PRE14_0"]),
                "PRE21_0_onset_date": onset_date,
                "PRE21_0_onset_lead_sessions": lead,
            }
        )
    return rows


def _rate(rows: list[dict[str, object]], label: str, key: str) -> dict[str, object]:
    selected = [r for r in rows if r["label"] == label]
    hits = [r for r in selected if bool(r[key])]
    return {
        "numerator": len(hits),
        "denominator": len(selected),
        "rate": (len(hits) / len(selected)) if selected else None,
        "peaks": [r["peak"] for r in hits],
    }


def _episode_rate(rows: list[dict[str, object]], label: str, key: str) -> dict[str, object]:
    by_ep: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        if row["label"] == label:
            by_ep.setdefault(int(row["episode_id"]), []).append(row)
    hit_eps = [eid for eid, rs in sorted(by_ep.items()) if any(bool(r[key]) for r in rs)]
    return {
        "numerator": len(hit_eps),
        "denominator": len(by_ep),
        "rate": (len(hit_eps) / len(by_ep)) if by_ep else None,
        "hit_episode_ids": hit_eps,
        "all_episode_ids": sorted(by_ep),
    }


def _lead_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    leads = [
        int(r["PRE21_0_onset_lead_sessions"])
        for r in rows
        if r["label"] == "TRUE_EXHAUSTION" and r["PRE21_0_onset_lead_sessions"] is not None
    ]
    return {
        "count": len(leads),
        "leads": leads,
        "median": float(np.median(leads)) if leads else None,
        "min": min(leads) if leads else None,
        "max": max(leads) if leads else None,
    }


def _spell_summary(alarm: np.ndarray, eligible: np.ndarray) -> dict[str, object]:
    spells = detector.alarm_spell_lengths(alarm, eligible)
    return {
        "spell_count": len(spells),
        "durations": spells,
        "median": float(np.median(spells)) if spells else 0.0,
        "p90_empirical_nearest_rank": detector.empirical_nearest_rank(spells, 0.90) if spells else 0.0,
    }


def _safe_percentile(values: list[float], q: float) -> float | None:
    finite = np.asarray([v for v in values if np.isfinite(v)], dtype=np.float64)
    return float(np.percentile(finite, q)) if len(finite) else None


def _ci(values: list[float]) -> dict[str, object]:
    return {
        "replicates_with_value": int(sum(np.isfinite(values))),
        "p2_5": _safe_percentile(values, CI_LOW),
        "median": _safe_percentile(values, 50.0),
        "p97_5": _safe_percentile(values, CI_HIGH),
    }


def _episode_cluster_bootstrap(
    primary_rows: list[dict[str, object]],
    severe_rows: list[dict[str, object]],
    episode_ids: list[int],
) -> dict[str, object]:
    rng = np.random.default_rng(EVENT_BOOTSTRAP_SEED)
    p_by = {eid: [r for r in primary_rows if int(r["episode_id"]) == eid] for eid in episode_ids}
    s_by = {eid: [r for r in severe_rows if int(r["episode_id"]) == eid] for eid in episode_ids}
    metrics = {k: [] for k in ("primary_true_event", "primary_cont_event", "primary_true_episode", "primary_cont_episode", "severe_true_event")}

    def event_parts(rows: list[dict[str, object]], label: str, key: str) -> tuple[int, int]:
        selected = [r for r in rows if r["label"] == label]
        return sum(bool(r[key]) for r in selected), len(selected)

    for _ in range(EVENT_BOOTSTRAP_REPLICATES):
        sampled = rng.choice(episode_ids, size=len(episode_ids), replace=True)
        num_te = den_te = num_ce = den_ce = num_se = den_se = 0
        num_tep = den_tep = num_cep = den_cep = 0
        for eid_raw in sampled:
            eid = int(eid_raw)
            p_rows = p_by[eid]
            s_rows = s_by[eid]
            n, d = event_parts(p_rows, "TRUE_EXHAUSTION", "PRE14_7_pulse"); num_te += n; den_te += d
            n, d = event_parts(p_rows, "CONTINUATION_FALSE_TOP", "PRE14_0_pulse"); num_ce += n; den_ce += d
            n, d = event_parts(s_rows, "TRUE_EXHAUSTION", "PRE14_7_pulse"); num_se += n; den_se += d
            true_rows = [r for r in p_rows if r["label"] == "TRUE_EXHAUSTION"]
            cont_rows = [r for r in p_rows if r["label"] == "CONTINUATION_FALSE_TOP"]
            if true_rows:
                den_tep += 1; num_tep += int(any(bool(r["PRE14_7_pulse"]) for r in true_rows))
            if cont_rows:
                den_cep += 1; num_cep += int(any(bool(r["PRE14_0_pulse"]) for r in cont_rows))
        metrics["primary_true_event"].append(num_te / den_te if den_te else np.nan)
        metrics["primary_cont_event"].append(num_ce / den_ce if den_ce else np.nan)
        metrics["primary_true_episode"].append(num_tep / den_tep if den_tep else np.nan)
        metrics["primary_cont_episode"].append(num_cep / den_cep if den_cep else np.nan)
        metrics["severe_true_event"].append(num_se / den_se if den_se else np.nan)
    return {
        "method": "MACRO_EPISODE_CLUSTER_BOOTSTRAP_COMPLETE_EPISODES_WITH_REPLACEMENT",
        "replicates": EVENT_BOOTSTRAP_REPLICATES,
        "seed": EVENT_BOOTSTRAP_SEED,
        "ci_percentiles": [CI_LOW, CI_HIGH],
        "intervals": {k: _ci(v) for k, v in metrics.items()},
    }


def _daily_block_bootstrap(alarm_eligible: np.ndarray) -> dict[str, object]:
    a = np.asarray(alarm_eligible, dtype=bool)
    n = len(a)
    if n == 0:
        raise EvaluationInvalid("no eligible daily alarm path for block bootstrap")
    rng = np.random.default_rng(DAILY_BOOTSTRAP_SEED)
    blocks = int(np.ceil(n / DAILY_BLOCK_LENGTH))
    offsets = np.arange(DAILY_BLOCK_LENGTH, dtype=np.int64)
    occupancy: list[float] = []
    medians: list[float] = []
    p90s: list[float] = []
    for _ in range(DAILY_BOOTSTRAP_REPLICATES):
        starts = rng.integers(0, n, size=blocks, endpoint=False)
        idx = ((starts[:, None] + offsets[None, :]) % n).reshape(-1)[:n]
        sample = a[idx]
        spells = detector.alarm_spell_lengths(sample)
        occupancy.append(float(sample.mean()))
        medians.append(float(np.median(spells)) if spells else 0.0)
        p90s.append(float(detector.empirical_nearest_rank(spells, 0.90)) if spells else 0.0)
    return {
        "method": "CIRCULAR_MOVING_BLOCK_BOOTSTRAP_DAILY_ALARM_PATH",
        "replicates": DAILY_BOOTSTRAP_REPLICATES,
        "seed": DAILY_BOOTSTRAP_SEED,
        "block_length": DAILY_BLOCK_LENGTH,
        "ci_percentiles": [CI_LOW, CI_HIGH],
        "intervals": {
            "raw_alarm_occupancy": _ci(occupancy),
            "median_alarm_spell": _ci(medians),
            "p90_alarm_spell_empirical_nearest_rank": _ci(p90s),
        },
    }


def _point_metrics(primary_rows: list[dict[str, object]], severe_rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "primary_true_PRE14_7": _rate(primary_rows, "TRUE_EXHAUSTION", "PRE14_7_pulse"),
        "primary_cont_PRE14_0": _rate(primary_rows, "CONTINUATION_FALSE_TOP", "PRE14_0_pulse"),
        "primary_true_episode_PRE14_7": _episode_rate(primary_rows, "TRUE_EXHAUSTION", "PRE14_7_pulse"),
        "primary_cont_episode_PRE14_0": _episode_rate(primary_rows, "CONTINUATION_FALSE_TOP", "PRE14_0_pulse"),
        "severe_true_PRE14_7": _rate(severe_rows, "TRUE_EXHAUSTION", "PRE14_7_pulse"),
        "primary_true_PRE21_0_onsets": _lead_stats(primary_rows),
    }


def _loeo(primary_rows: list[dict[str, object]], severe_rows: list[dict[str, object]], episode_ids: list[int]) -> list[dict[str, object]]:
    out = []
    for eid in episode_ids:
        p = [r for r in primary_rows if int(r["episode_id"]) != eid]
        s = [r for r in severe_rows if int(r["episode_id"]) != eid]
        out.append({"excluded_episode_id": eid, "metrics": _point_metrics(p, s)})
    return out


def run_locked(predictor_path: Path, lock: dict[str, object]) -> dict[str, object]:
    if lock.get("calibration_status") != "CALIBRATION_LOCKED":
        raise EvaluationInvalid("evaluation requires successful CALIBRATION_LOCK")
    if lock.get("label_data_accessed") is not False or lock.get("event_taxonomy_loaded") is not False:
        raise EvaluationInvalid("lock does not establish pre-label firewall")
    predictor: PredictorArtifact = read_predictor_artifact(predictor_path)
    if predictor.predictor_digest != lock.get("predictor_digest"):
        raise EvaluationInvalid("predictor digest differs from locked calibration input")
    if predictor.artifact_payload_sha256 != lock.get("predictor_artifact_payload_sha256"):
        raise EvaluationInvalid("predictor artifact payload hash differs from lock")

    threshold_obj = lock.get("threshold")
    if not isinstance(threshold_obj, dict):
        raise EvaluationInvalid("locked threshold missing")
    threshold = float(threshold_obj["ieee754_float"])
    det = detector.compute_detector(predictor.axes[list(PRIMARY_AXES)].to_numpy(dtype=float), details=True)
    eligible, alarm, pulse = detector.raw_alarm_and_pulse(det.score, threshold)

    # Outcome information begins only here, after detector, threshold and lock are fixed.
    nav, _ = e0043.load_canonical()
    nav = nav.loc[nav.index <= FROZEN_EVAL_END].dropna().sort_index()
    candidates, panels, reproduction = s0044.reproduce_0043_taxonomy(nav)
    episode_map, episode_metadata = s0044.assign_macro_episodes(nav, candidates)
    primary_rows = _event_rows(panels[PRIMARY_DOWNSIDE], episode_map, pulse, predictor.axes.index)
    severe_rows = _event_rows(panels[SEVERE_DOWNSIDE], episode_map, pulse, predictor.axes.index)

    point = _point_metrics(primary_rows, severe_rows)
    true_eps = point["primary_true_episode_PRE14_7"]["all_episode_ids"]
    cont_eps = point["primary_cont_episode_PRE14_0"]["all_episode_ids"]
    usable_eps = sorted(set(true_eps) | set(cont_eps))
    diversity = len(usable_eps) >= 4 and len(true_eps) >= 2 and len(cont_eps) >= 2

    occupancy = float(alarm[eligible].mean()) if bool(eligible.any()) else np.nan
    spells = _spell_summary(alarm, eligible)
    leads = point["primary_true_PRE21_0_onsets"]
    gates = {
        "episode_diversity": {"pass": diversity, "usable": len(usable_eps), "true": len(true_eps), "continuation": len(cont_eps)},
        "primary_true_event_PRE14_7_ge_0_50": {"pass": point["primary_true_PRE14_7"]["rate"] is not None and point["primary_true_PRE14_7"]["rate"] >= 0.50, "value": point["primary_true_PRE14_7"]["rate"]},
        "primary_cont_event_PRE14_0_le_0_34": {"pass": point["primary_cont_PRE14_0"]["rate"] is not None and point["primary_cont_PRE14_0"]["rate"] <= 0.34, "value": point["primary_cont_PRE14_0"]["rate"]},
        "primary_true_episode_PRE14_7_ge_0_60": {"pass": point["primary_true_episode_PRE14_7"]["rate"] is not None and point["primary_true_episode_PRE14_7"]["rate"] >= 0.60, "value": point["primary_true_episode_PRE14_7"]["rate"]},
        "primary_cont_episode_PRE14_0_le_0_50": {"pass": point["primary_cont_episode_PRE14_0"]["rate"] is not None and point["primary_cont_episode_PRE14_0"]["rate"] <= 0.50, "value": point["primary_cont_episode_PRE14_0"]["rate"]},
        "severe_true_event_PRE14_7_ge_0_57": {"pass": point["severe_true_PRE14_7"]["rate"] is not None and point["severe_true_PRE14_7"]["rate"] >= 0.57, "value": point["severe_true_PRE14_7"]["rate"]},
        "primary_true_PRE21_0_onsets_ge_4": {"pass": int(leads["count"]) >= 4, "value": leads["count"]},
        "median_onset_lead_7_to_21": {"pass": leads["median"] is not None and 7 <= float(leads["median"]) <= 21, "value": leads["median"]},
        "raw_alarm_occupancy_le_0_175": {"pass": np.isfinite(occupancy) and occupancy <= 0.175, "value": occupancy},
        "median_alarm_spell_le_7": {"pass": float(spells["median"]) <= 7.0, "value": spells["median"]},
        "p90_alarm_spell_le_14": {"pass": float(spells["p90_empirical_nearest_rank"]) <= 14.0, "value": spells["p90_empirical_nearest_rank"]},
        "calibration_arl0_ge_365": {"pass": float(threshold_obj["arl0_trunc"]) >= 365.0, "value": threshold_obj["arl0_trunc"]},
        "construction_and_authority": {
            "pass": True,
            "post_result_retuning": False,
            "portfolio_economics_executed": False,
            "dynamic_gross_stage_eligible": False,
            "canonical_strategy_changed": False,
            "phase6_observation_changed": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }
    if not diversity:
        result_status = "INSUFFICIENT_EPISODE_DIVERSITY"
    elif all(bool(g["pass"]) for g in gates.values()):
        result_status = "PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE"
    else:
        result_status = "FAIL_NO_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBILITY"

    eligible_pos = np.flatnonzero(eligible)
    daily = []
    age_counter: Counter[int] = Counter()
    for pos in eligible_pos:
        age = int(det.selected_age[pos])
        age_counter[age] += 1
        daily.append(
            {
                "date": str(pd.Timestamp(predictor.axes.index[pos]).date()),
                "score": float(det.score[pos]),
                "raw_alarm": bool(alarm[pos]),
                "transition_pulse": bool(pulse[pos]),
                "selected_change_age": age,
                "axis_ell": {axis: float(det.selected_axis_contributions[pos, j]) for j, axis in enumerate(PRIMARY_AXES)},
            }
        )

    result: dict[str, object] = {
        "research_id": RESEARCH_ID,
        "result_status": result_status,
        "calibration_lock_binding": {
            "lock_payload_sha256": lock["lock_payload_sha256_without_self_hash"],
            "code_sha": lock["code_sha"],
            "predictor_digest": lock["predictor_digest"],
            "threshold": threshold_obj,
            "lock_validated_before_evaluation_module_import": True,
            "labels_loaded_only_after_locked_detector_evaluated": True,
        },
        "taxonomy_reproduction": reproduction,
        "episodes": episode_metadata,
        "primary_events": primary_rows,
        "severe_events": severe_rows,
        "point_metrics": point,
        "alarm_path": {
            "eligible_sessions": int(eligible.sum()),
            "raw_alarm_sessions": int(alarm[eligible].sum()),
            "raw_alarm_occupancy": occupancy,
            "spell_summary": spells,
            "total_pulse_count": int(pulse.sum()),
            "pulse_dates": [str(pd.Timestamp(predictor.axes.index[i]).date()) for i in np.flatnonzero(pulse)],
        },
        "change_age_distribution": {str(k): v for k, v in sorted(age_counter.items())},
        "daily_detector": daily,
        "uncertainty": {
            "event_cluster": _episode_cluster_bootstrap(primary_rows, severe_rows, [int(x["episode_id"]) for x in episode_metadata]),
            "daily_block": _daily_block_bootstrap(alarm[eligible]),
            "intervals_are_descriptive_not_gating": True,
            "daily_iid_p_values": False,
        },
        "leave_one_macro_episode_out": _loeo(primary_rows, severe_rows, [int(x["episode_id"]) for x in episode_metadata]),
        "gates": gates,
        "authority": {
            "researcher_exposed_development_only": True,
            "independent_oos": False,
            "future_only_pulse_validation_stage_eligible": result_status == "PASS_FUTURE_ONLY_PULSE_VALIDATION_ELIGIBLE",
            "dynamic_gross_stage_eligible": False,
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
