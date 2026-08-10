from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_exhaustion_state_0044 import run_once as s0044

RESEARCH_ID = "BRRK-EXHAUSTION-TRIGGER-0045"
FROZEN_EVAL_END = pd.Timestamp("2026-08-02")
LOOKBACK = 252
MIN_HISTORY = 60

STATE_ORDER = {"HEALTHY": 0, "DECELERATION": 1, "RECOVERY": 1, "WATCH": 2, "RISK": 3}
WATCH_STATES = {"WATCH", "RISK"}

DECEL_CORE = 0.60
DECEL_S2 = 0.60
WATCH_CORE = 0.65
WATCH_S2 = 0.65
RISK_CORE = 0.75
RISK_S2 = 0.80
RECOVERY_CORE = 0.45
RECOVERY_S2 = 0.45
RECOVERY_S3 = 0.50
HEALTHY_CORE = 0.55
HEALTHY_S2 = 0.55
HEALTHY_S3 = 0.55
ENTRY_LOOKBACK = 3
ENTRY_REQUIRED = 2
DECEL_CLEAR_CONSECUTIVE = 3
RECOVERY_ENTRY_CONSECUTIVE = 5
RECOVERY_MIN_HOLD = 5
HEALTHY_REPAIR_LOOKBACK = 5
HEALTHY_REPAIR_REQUIRED = 3

WINDOWS = {
    "PRE14_7": (-14, -7),
    "PRE14_0": (-14, 0),
    "PRE7_POST3": (-7, 3),
    "PRE14_POST3": (-14, 3),
    "PRE21_0": (-21, 0),
}

EXPECTED_0044_RESULT_STATUS = "PASS_TRIGGER_STAGE_ELIGIBLE"
EXPECTED_0044_ARTIFACT_DIGEST = "sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378"


class RunInvalid(RuntimeError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json_sha(obj: object) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def causal_percentile(series: pd.Series) -> pd.Series:
    out = pd.Series(np.nan, index=series.index, dtype=float)
    values = series.astype(float)
    for i in range(len(values)):
        cur = values.iloc[i]
        if not np.isfinite(cur):
            continue
        prior = values.iloc[max(0, i - LOOKBACK):i].dropna()
        if len(prior) < MIN_HISTORY:
            continue
        out.iloc[i] = float((prior <= cur).mean())
    return out


def _k_of_n(raw: pd.Series, pos: int, n: int, k: int) -> bool:
    if pos < n - 1:
        return False
    window = raw.iloc[pos - n + 1:pos + 1]
    return len(window) == n and int(window.fillna(False).astype(bool).sum()) >= k


def _all_false_consecutive(raw: pd.Series, pos: int, n: int) -> bool:
    if pos < n - 1:
        return False
    window = raw.iloc[pos - n + 1:pos + 1].fillna(False).astype(bool)
    return len(window) == n and not bool(window.any())


def _all_true_consecutive(raw: pd.Series, pos: int, n: int) -> bool:
    if pos < n - 1:
        return False
    window = raw.iloc[pos - n + 1:pos + 1].fillna(False).astype(bool)
    return len(window) == n and bool(window.all())


def build_percentiles(state_axes: pd.DataFrame) -> pd.DataFrame:
    required = ["CORE4", "S2_TREND_DISAGREEMENT", "S3_PRICE_STRUCTURE"]
    missing = [c for c in required if c not in state_axes.columns]
    if missing:
        raise RunInvalid(f"missing 0044 state inputs: {missing}")
    p = pd.DataFrame(index=state_axes.index)
    p["pct_CORE4"] = causal_percentile(state_axes["CORE4"])
    p["pct_S2"] = causal_percentile(state_axes["S2_TREND_DISAGREEMENT"])
    p["pct_S3"] = causal_percentile(state_axes["S3_PRICE_STRUCTURE"])
    return p


def run_state_machine(percentiles: pd.DataFrame) -> pd.DataFrame:
    p = percentiles.copy()
    p["decel_raw"] = (p["pct_CORE4"] >= DECEL_CORE) | (p["pct_S2"] >= DECEL_S2)
    p["watch_raw"] = (p["pct_CORE4"] >= WATCH_CORE) & (p["pct_S2"] >= WATCH_S2)
    p["risk_raw"] = (p["pct_CORE4"] >= RISK_CORE) & (p["pct_S2"] >= RISK_S2)
    p["recovery_entry_raw"] = (
        (p["pct_CORE4"] <= RECOVERY_CORE)
        & (p["pct_S2"] <= RECOVERY_S2)
        & (p["pct_S3"] <= RECOVERY_S3)
    )
    p["healthy_repair_raw"] = (
        (p["pct_CORE4"] <= HEALTHY_CORE)
        & (p["pct_S2"] <= HEALTHY_S2)
        & (p["pct_S3"] <= HEALTHY_S3)
    )

    states: list[str] = []
    recovery_age = 0
    for pos in range(len(p)):
        prev = states[-1] if states else "HEALTHY"
        dqual = _k_of_n(p["decel_raw"], pos, ENTRY_LOOKBACK, ENTRY_REQUIRED)
        wqual = _k_of_n(p["watch_raw"], pos, ENTRY_LOOKBACK, ENTRY_REQUIRED)
        rqual = _k_of_n(p["risk_raw"], pos, ENTRY_LOOKBACK, ENTRY_REQUIRED)
        recover_qual = _all_true_consecutive(p["recovery_entry_raw"], pos, RECOVERY_ENTRY_CONSECUTIVE)
        repair_qual = _k_of_n(p["healthy_repair_raw"], pos, HEALTHY_REPAIR_LOOKBACK, HEALTHY_REPAIR_REQUIRED)

        if prev == "HEALTHY":
            recovery_age = 0
            state = "RISK" if rqual else "WATCH" if wqual else "DECELERATION" if dqual else "HEALTHY"
        elif prev == "DECELERATION":
            recovery_age = 0
            if rqual:
                state = "RISK"
            elif wqual:
                state = "WATCH"
            elif _all_false_consecutive(p["decel_raw"], pos, DECEL_CLEAR_CONSECUTIVE):
                state = "HEALTHY"
            else:
                state = "DECELERATION"
        elif prev == "WATCH":
            recovery_age = 0
            if rqual:
                state = "RISK"
            elif recover_qual:
                state = "RECOVERY"
                recovery_age = 1
            else:
                state = "WATCH"
        elif prev == "RISK":
            recovery_age = 0
            if recover_qual:
                state = "RECOVERY"
                recovery_age = 1
            else:
                state = "RISK"
        elif prev == "RECOVERY":
            recovery_age += 1
            if rqual:
                state = "RISK"
                recovery_age = 0
            elif wqual:
                state = "WATCH"
                recovery_age = 0
            elif recovery_age >= RECOVERY_MIN_HOLD and repair_qual:
                state = "HEALTHY"
                recovery_age = 0
            else:
                state = "RECOVERY"
        else:
            raise RunInvalid(f"unexpected previous state {prev}")
        states.append(state)

    p["state"] = states
    p["is_watch_or_risk"] = p["state"].isin(WATCH_STATES)
    p["is_risk"] = p["state"].eq("RISK")
    p["transition"] = p["state"].ne(p["state"].shift(1)).fillna(True)
    return p


def _window_positions(index: pd.Index, peak: pd.Timestamp, bounds: tuple[int, int]) -> list[int]:
    if peak not in index:
        return []
    pos = int(index.get_loc(peak))
    lo = max(0, pos + bounds[0])
    hi = min(len(index) - 1, pos + bounds[1])
    if lo > hi:
        return []
    return list(range(lo, hi + 1))


def _any_state(machine: pd.DataFrame, peak: pd.Timestamp, bounds: tuple[int, int], allowed: set[str]) -> bool:
    positions = _window_positions(machine.index, peak, bounds)
    return any(str(machine.iloc[i]["state"]) in allowed for i in positions)


def _transition_onset(machine: pd.DataFrame, peak: pd.Timestamp) -> tuple[pd.Timestamp | None, int | None]:
    positions = _window_positions(machine.index, peak, WINDOWS["PRE21_0"])
    if not positions:
        return None, None
    peak_pos = int(machine.index.get_loc(peak))
    for pos in positions:
        state = str(machine.iloc[pos]["state"])
        if state not in WATCH_STATES:
            continue
        prev_state = str(machine.iloc[pos - 1]["state"]) if pos > 0 else "HEALTHY"
        if prev_state not in WATCH_STATES:
            return pd.Timestamp(machine.index[pos]), int(peak_pos - pos)
    return None, None


def _event_rows(panel_rows: list[dict[str, object]], episodes: dict[pd.Timestamp, int], machine: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for src in panel_rows:
        peak = pd.Timestamp(src["peak"])
        onset, lead = _transition_onset(machine, peak)
        row = {
            "peak": str(peak.date()),
            "episode_id": int(episodes[peak]),
            "label": str(src["label"]),
            "down_date": src["down_date"],
            "fresh_high_date": src["fresh_high_date"],
            "min_60d_return": src["min_60d_return"],
            "max_60d_return": src["max_60d_return"],
            "PRE14_7_watch_or_risk": _any_state(machine, peak, WINDOWS["PRE14_7"], WATCH_STATES),
            "PRE14_0_watch_or_risk": _any_state(machine, peak, WINDOWS["PRE14_0"], WATCH_STATES),
            "PRE7_POST3_risk": _any_state(machine, peak, WINDOWS["PRE7_POST3"], {"RISK"}),
            "PRE14_POST3_risk": _any_state(machine, peak, WINDOWS["PRE14_POST3"], {"RISK"}),
            "PRE21_0_onset_date": str(onset.date()) if onset is not None else None,
            "PRE21_0_onset_lead_sessions": lead,
        }
        premature = None
        if onset is not None and src["down_date"] is not None:
            down = pd.Timestamp(src["down_date"])
            if down in machine.index:
                a = int(machine.index.get_loc(onset)) + 1
                b = int(machine.index.get_loc(down)) - 1
                premature = False if b < a else any(str(machine.iloc[i]["state"]) in {"RECOVERY", "HEALTHY"} for i in range(a, b + 1))
        row["premature_clear_before_down_date"] = premature

        false_recovery = None
        if row["label"] == "CONTINUATION_FALSE_TOP" and row["PRE14_0_watch_or_risk"] and src["fresh_high_date"] is not None:
            fresh = pd.Timestamp(src["fresh_high_date"])
            if peak in machine.index and fresh in machine.index:
                a = int(machine.index.get_loc(peak)) + 1
                b = int(machine.index.get_loc(fresh)) - 1
                false_recovery = False if b < a else any(str(machine.iloc[i]["state"]) in {"RECOVERY", "HEALTHY"} for i in range(a, b + 1))
        row["false_trigger_recovery_before_fresh_high"] = false_recovery
        rows.append(row)
    return rows


def _rate(rows: list[dict[str, object]], label: str, key: str) -> dict[str, object]:
    selected = [r for r in rows if r["label"] == label]
    hits = [r for r in selected if bool(r[key])]
    return {"numerator": len(hits), "denominator": len(selected), "rate": (len(hits) / len(selected)) if selected else None, "peaks": [r["peak"] for r in hits]}


def _episode_rate(rows: list[dict[str, object]], label: str, key: str) -> dict[str, object]:
    by_ep: dict[int, list[dict[str, object]]] = defaultdict(list)
    for r in rows:
        if r["label"] == label:
            by_ep[int(r["episode_id"])].append(r)
    hit_eps = [eid for eid, rs in sorted(by_ep.items()) if any(bool(r[key]) for r in rs)]
    denom = len(by_ep)
    return {"numerator": len(hit_eps), "denominator": denom, "rate": (len(hit_eps) / denom) if denom else None, "episode_ids": hit_eps, "all_episode_ids": sorted(by_ep)}


def _premature_rate(rows: list[dict[str, object]]) -> dict[str, object]:
    selected = [r for r in rows if r["label"] == "TRUE_EXHAUSTION" and r["PRE21_0_onset_date"] is not None and r["premature_clear_before_down_date"] is not None]
    bad = [r for r in selected if bool(r["premature_clear_before_down_date"])]
    return {"numerator": len(bad), "denominator": len(selected), "rate": (len(bad) / len(selected)) if selected else None, "peaks": [r["peak"] for r in bad]}


def _lead_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    leads = [int(r["PRE21_0_onset_lead_sessions"]) for r in rows if r["label"] == "TRUE_EXHAUSTION" and r["PRE21_0_onset_lead_sessions"] is not None]
    return {"count": len(leads), "leads": leads, "median": float(np.median(leads)) if leads else None, "min": min(leads) if leads else None, "max": max(leads) if leads else None}


def _state_stats(machine: pd.DataFrame) -> dict[str, object]:
    counts = Counter(str(x) for x in machine["state"])
    transitions = Counter()
    prev = None
    for state in machine["state"].astype(str):
        if prev is not None and state != prev:
            transitions[f"{prev}->{state}"] += 1
        prev = state
    total = len(machine)
    return {"counts": dict(sorted(counts.items())), "fractions": {k: v / total for k, v in sorted(counts.items())}, "transitions": dict(sorted(transitions.items()))}


def _gate_ge(value: float | None, threshold: float) -> bool:
    return value is not None and np.isfinite(value) and float(value) >= threshold


def _gate_le(value: float | None, threshold: float) -> bool:
    return value is not None and np.isfinite(value) and float(value) <= threshold


def run() -> dict[str, object]:
    root = repo_root()
    prereg = json.loads((root / "research/brrk_exhaustion_trigger_0045/PREREGISTRATION.json").read_text())
    if prereg.get("research_id") != RESEARCH_ID or prereg.get("result_status") != "PREREGISTERED_NOT_RUN":
        raise RunInvalid("0045 preregistration identity/state mismatch")
    parent = json.loads((root / "research/brrk_exhaustion_state_0044/PRIMARY_RESULT.json").read_text())
    if parent.get("result_status") != EXPECTED_0044_RESULT_STATUS:
        raise RunInvalid("0044 parent result status mismatch")
    if parent.get("execution_binding", {}).get("artifact_digest") != EXPECTED_0044_ARTIFACT_DIGEST:
        raise RunInvalid("0044 parent artifact binding mismatch")
    if s0044.FROZEN_EVAL_END != FROZEN_EVAL_END:
        raise RunInvalid("0044 frozen end drift")

    market = s0044.e0043.load_market()
    nav, defensive = s0044.e0043.load_canonical()
    nav = nav.loc[nav.index <= FROZEN_EVAL_END]
    defensive = defensive.loc[defensive.index <= FROZEN_EVAL_END]
    score0043, _ = s0044.e0043.build_features(market, nav, defensive)
    axes = s0044.build_state_axes(score0043)
    candidates, panels, reproduction = s0044.reproduce_0043_taxonomy(nav)
    ep_map, ep_meta = s0044.assign_macro_episodes(nav, candidates)
    percentiles = build_percentiles(axes)
    machine = run_state_machine(percentiles)

    primary_rows = _event_rows(panels[0.15], ep_map, machine)
    severe_rows = _event_rows(panels[0.20], ep_map, machine)

    primary_true_watch = _rate(primary_rows, "TRUE_EXHAUSTION", "PRE14_7_watch_or_risk")
    primary_cont_watch = _rate(primary_rows, "CONTINUATION_FALSE_TOP", "PRE14_0_watch_or_risk")
    true_ep_watch = _episode_rate(primary_rows, "TRUE_EXHAUSTION", "PRE14_7_watch_or_risk")
    cont_ep_watch = _episode_rate(primary_rows, "CONTINUATION_FALSE_TOP", "PRE14_0_watch_or_risk")
    severe_true_watch = _rate(severe_rows, "TRUE_EXHAUSTION", "PRE14_7_watch_or_risk")
    severe_true_risk = _rate(severe_rows, "TRUE_EXHAUSTION", "PRE7_POST3_risk")
    primary_cont_risk = _rate(primary_rows, "CONTINUATION_FALSE_TOP", "PRE14_POST3_risk")
    lead = _lead_stats(primary_rows)
    premature = _premature_rate(primary_rows)

    true_eps = true_ep_watch["all_episode_ids"]
    cont_eps = cont_ep_watch["all_episode_ids"]
    usable_eps = sorted(set(true_eps) | set(cont_eps))
    diversity = len(usable_eps) >= 4 and len(true_eps) >= 2 and len(cont_eps) >= 2

    gates = {
        "episode_diversity": {"pass": diversity, "usable_episode_count": len(usable_eps), "true_episode_count": len(true_eps), "continuation_episode_count": len(cont_eps)},
        "primary_true_PRE14_7_watch_hit_ge_0_50": {"pass": _gate_ge(primary_true_watch["rate"], 0.50), "value": primary_true_watch["rate"]},
        "primary_cont_PRE14_0_watch_false_le_0_34": {"pass": _gate_le(primary_cont_watch["rate"], 0.34), "value": primary_cont_watch["rate"]},
        "primary_true_episode_watch_hit_ge_0_60": {"pass": _gate_ge(true_ep_watch["rate"], 0.60), "value": true_ep_watch["rate"]},
        "primary_cont_episode_watch_false_le_0_50": {"pass": _gate_le(cont_ep_watch["rate"], 0.50), "value": cont_ep_watch["rate"]},
        "severe_true_PRE14_7_watch_hit_ge_0_57": {"pass": _gate_ge(severe_true_watch["rate"], 0.57), "value": severe_true_watch["rate"]},
        "severe_true_PRE7_POST3_risk_ge_0_57": {"pass": _gate_ge(severe_true_risk["rate"], 0.57), "value": severe_true_risk["rate"]},
        "primary_cont_PRE14_POST3_risk_false_le_0_17": {"pass": _gate_le(primary_cont_risk["rate"], 0.17), "value": primary_cont_risk["rate"]},
        "true_onset_count_ge_4_and_median_7_to_21": {"pass": lead["count"] >= 4 and lead["median"] is not None and 7 <= float(lead["median"]) <= 21, "count": lead["count"], "median": lead["median"]},
        "premature_clear_le_0_25": {"pass": _gate_le(premature["rate"], 0.25), "value": premature["rate"], "denominator": premature["denominator"]},
        "construction_and_authority": {"pass": True, "variant_count": 1, "gross_mapping_defined": False, "portfolio_economics_executed": False, "canonical_strategy_changed": False, "phase6_observation_changed": False, "production_authorized": False, "signature_authorized": False, "order_submission_authorized": False},
    }

    if not diversity:
        status = "INSUFFICIENT_EPISODE_DIVERSITY"
    elif all(bool(g["pass"]) for g in gates.values()):
        status = "PASS_DYNAMIC_GROSS_STAGE_ELIGIBLE"
    else:
        status = "FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY"

    false_triggered_cont = [r for r in primary_rows if r["label"] == "CONTINUATION_FALSE_TOP" and r["PRE14_0_watch_or_risk"]]
    recovery_known = [r for r in false_triggered_cont if r["false_trigger_recovery_before_fresh_high"] is not None]
    recovery_hits = [r for r in recovery_known if r["false_trigger_recovery_before_fresh_high"]]

    result = {
        "research_id": RESEARCH_ID,
        "result_status": status,
        "window": {"start": str(machine.index.min().date()), "end": str(machine.index.max().date()), "sessions": int(len(machine))},
        "frozen_machine": {
            "lookback": LOOKBACK, "min_history": MIN_HISTORY,
            "deceleration": {"CORE4": DECEL_CORE, "S2": DECEL_S2, "logic": "OR", "persistence": "2_of_3"},
            "watch": {"CORE4": WATCH_CORE, "S2": WATCH_S2, "logic": "AND", "persistence": "2_of_3"},
            "risk": {"CORE4": RISK_CORE, "S2": RISK_S2, "logic": "AND", "persistence": "2_of_3"},
            "recovery_entry": {"CORE4": RECOVERY_CORE, "S2": RECOVERY_S2, "S3": RECOVERY_S3, "logic": "AND", "persistence": "5_consecutive"},
            "recovery_min_hold": RECOVERY_MIN_HOLD,
            "healthy_repair": {"CORE4": HEALTHY_CORE, "S2": HEALTHY_S2, "S3": HEALTHY_S3, "logic": "AND", "persistence": "3_of_5_after_hold"},
        },
        "source_integrity": {
            "0043_taxonomy_reproduction": reproduction,
            "0044_parent_result_status": parent["result_status"],
            "0044_parent_artifact_digest": parent["execution_binding"]["artifact_digest"],
            "0045_preregistration_sha256": hashlib.sha256((root / "research/brrk_exhaustion_trigger_0045/PREREGISTRATION.json").read_bytes()).hexdigest(),
        },
        "episodes": ep_meta,
        "primary_15pct_events": primary_rows,
        "severe_20pct_events": severe_rows,
        "metrics": {
            "primary_true_PRE14_7_watch_or_risk": primary_true_watch,
            "primary_cont_PRE14_0_watch_or_risk_false": primary_cont_watch,
            "primary_true_episode_PRE14_7_watch_or_risk": true_ep_watch,
            "primary_cont_episode_PRE14_0_watch_or_risk_false": cont_ep_watch,
            "severe_true_PRE14_7_watch_or_risk": severe_true_watch,
            "severe_true_PRE7_POST3_risk": severe_true_risk,
            "primary_cont_PRE14_POST3_risk_false": primary_cont_risk,
            "primary_true_onset_lead": lead,
            "primary_true_premature_clear": premature,
            "continuation_false_trigger_recovery_before_fresh_high": {"numerator": len(recovery_hits), "denominator": len(recovery_known), "rate": (len(recovery_hits) / len(recovery_known)) if recovery_known else None, "peaks": [r["peak"] for r in recovery_hits]},
            "state_occupancy": _state_stats(machine),
        },
        "gates": gates,
        "authority": {"researcher_exposed_development_only": True, "independent_oos": False, "dynamic_gross_stage_eligible": status == "PASS_DYNAMIC_GROSS_STAGE_ELIGIBLE", "gross_mapping_defined": False, "portfolio_economics_executed": False, "canonical_strategy_changed": False, "phase6_observation_changed": False, "production_authorized": False, "signature_authorized": False, "order_submission_authorized": False},
    }
    result["result_payload_sha256_without_self_hash"] = _json_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("BRRK_EXHAUSTION_TRIGGER_0045_RESULT=" + json.dumps({"research_id": result["research_id"], "result_status": result["result_status"], "metrics": result["metrics"], "gates": result["gates"], "authority": result["authority"]}, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
