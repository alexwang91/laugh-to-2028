from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "research" / "cycle_exit" / "p5_5_validation_contract.json"
R1_PATH = ROOT / "research" / "cycle_exit" / "p5_5_validation_contract_r1.json"
P54_PATH = ROOT / "research" / "cycle_exit" / "p5_4_behavior_mapping_contract.json"


class P55ValidationError(RuntimeError):
    pass


def load_contracts() -> tuple[dict, dict, dict]:
    c = json.loads(CONTRACT_PATH.read_text())
    r1 = json.loads(R1_PATH.read_text())
    p54 = json.loads(P54_PATH.read_text())
    if c.get("contract_id") != "P5.5-JOINT-PROFILE-MAP-VALIDATION-V1":
        raise P55ValidationError("unexpected P5.5 contract")
    if c.get("status") != "PREREGISTERED_BEFORE_ANY_P5_5_CANDIDATE_ECONOMICS":
        raise P55ValidationError("P5.5 contract not frozen")
    if r1.get("amendment_id") != "P5.5-JOINT-PROFILE-MAP-VALIDATION-V1-R1":
        raise P55ValidationError("missing P5.5 R1")
    if r1.get("result_observed_before_amendment") is not False:
        raise P55ValidationError("R1 was not frozen pre-result")
    if p54.get("contract_id") != "P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1":
        raise P55ValidationError("unexpected P5.4 dependency")
    return c, r1, p54


def annualized_cagr_from_returns(returns: pd.Series, annualization: float = 365.25) -> float:
    r = returns.dropna().astype(float)
    if len(r) == 0:
        raise P55ValidationError("empty return series")
    if (r <= -1.0).any():
        raise P55ValidationError("non-positive wealth factor")
    log_terminal = float(np.log1p(r).sum())
    return float(np.expm1(log_terminal * float(annualization) / float(len(r))))


def held_out_relative_cagr(
    candidate_returns: pd.Series,
    baseline_returns: pd.Series,
    *,
    exclude_start: pd.Timestamp,
    exclude_end: pd.Timestamp,
) -> tuple[float, float, float, int]:
    x = pd.concat(
        [candidate_returns.rename("candidate"), baseline_returns.rename("baseline")],
        axis=1,
        join="inner",
    ).dropna()
    mask = ~((x.index >= pd.Timestamp(exclude_start)) & (x.index <= pd.Timestamp(exclude_end)))
    kept = x.loc[mask]
    if len(kept) < 30:
        raise P55ValidationError("held-out sample too short")
    cc = annualized_cagr_from_returns(kept["candidate"])
    bc = annualized_cagr_from_returns(kept["baseline"])
    return cc, bc, cc - bc, int(len(kept))


def map_lookup(p54: dict) -> dict[str, dict[str, float]]:
    return {x["id"]: {k: float(v) for k, v in x["multipliers"].items()} for x in p54["candidate_maps"]}


def event_behavior_table(
    state_paths: pd.DataFrame,
    resolved_events: pd.DataFrame,
    taxonomy: dict,
    flat_episodes: pd.DataFrame,
    contract: dict,
    p54: dict,
) -> pd.DataFrame:
    buckets = taxonomy["evaluation_buckets_relative_to_anchor_calendar_days"]
    maps = map_lookup(p54)
    profiles = contract["candidate_set"]["profiles"]
    map_ids = contract["candidate_set"]["behavior_maps"]
    state_paths = state_paths.copy()
    state_paths["date"] = pd.to_datetime(state_paths["date"])
    rows: list[dict[str, object]] = []
    later_cutoff = pd.Timestamp("2021-02-23")

    for profile in profiles:
        p = state_paths.loc[state_paths["profile"] == profile].sort_values("date").set_index("date")
        if p.empty:
            raise P55ValidationError(f"missing V2 state path profile={profile}")
        profile_flat = flat_episodes.loc[flat_episodes["profile"] == profile].copy()
        false_episode = profile_flat.loc[profile_flat["start_date"].astype(str) == "2021-02-23"]
        false_present = len(false_episode) == 1
        false_duration = int(false_episode.iloc[0]["duration_days"]) if false_present else 10**9
        later_events = resolved_events.loc[pd.to_datetime(resolved_events["anchor_date"]) > later_cutoff]
        later_observable = True
        for ev in later_events.itertuples(index=False):
            anchor = pd.Timestamp(ev.anchor_date)
            lo, hi = buckets["near_event"]
            if len(p.loc[anchor + pd.Timedelta(days=int(lo)):anchor + pd.Timedelta(days=int(hi))]) == 0:
                later_observable = False
                break

        for map_id in map_ids:
            mapping = maps[map_id]
            for ev in resolved_events.itertuples(index=False):
                anchor = pd.Timestamp(ev.anchor_date)
                for bucket, bounds in buckets.items():
                    lo, hi = int(bounds[0]), int(bounds[1])
                    sub = p.loc[anchor + pd.Timedelta(days=lo):anchor + pd.Timedelta(days=hi)]
                    states = sub["market_state"].astype(str)
                    multipliers = states.map(lambda s: 0.0 if s == "DATA_INSUFFICIENT" else mapping[s])
                    rows.append({
                        "profile": profile,
                        "behavior_map": map_id,
                        "event_id": ev.event_id,
                        "event_class": ev.event_class,
                        "terminal_label": bool(ev.terminal_label),
                        "anchor_date": anchor.date().isoformat(),
                        "bucket": bucket,
                        "classified_days": int(len(sub)),
                        "mean_multiplier": float(multipliers.mean()) if len(multipliers) else float("nan"),
                        "minimum_multiplier": float(multipliers.min()) if len(multipliers) else float("nan"),
                        "zero_multiplier_days": int((multipliers <= 1e-12).sum()) if len(multipliers) else 0,
                        "false_flat_2021_present": false_present,
                        "false_flat_2021_episode_days": false_duration,
                        "later_events_observable": later_observable,
                    })
    return pd.DataFrame(rows)


def event_behavior_pass(rows: pd.DataFrame, profile: str, behavior_map: str, contract: dict) -> tuple[bool, dict[str, bool]]:
    x = rows.loc[(rows["profile"] == profile) & (rows["behavior_map"] == behavior_map)]
    g = contract["event_behavior_gates"]

    def mean_for(event_id: str, bucket: str) -> float:
        y = x.loc[(x["event_id"] == event_id) & (x["bucket"] == bucket), "mean_multiplier"]
        if len(y) != 1 or not np.isfinite(float(y.iloc[0])):
            return float("nan")
        return float(y.iloc[0])

    checks = {
        "terminal_target_lead": mean_for("P5E-2021-NOV-TERMINAL-TOP", "target_lead") <= float(g["terminal_2021_target_lead_mean_multiplier_max"]),
        "terminal_near_event": mean_for("P5E-2021-NOV-TERMINAL-TOP", "near_event") <= float(g["terminal_2021_near_event_mean_multiplier_max"]),
        "second_wind_2021": mean_for("P5E-2021-SUMMER-SECOND-WIND", "near_event") >= float(g["second_wind_2021_near_event_mean_multiplier_min"]),
        "second_wind_2025": mean_for("P5E-2025-AUG-NEW-HIGH", "near_event") >= float(g["second_wind_2025_near_event_mean_multiplier_min"]),
    }
    profile_rows = x.head(1)
    checks["false_flat_present"] = bool(len(profile_rows) and profile_rows.iloc[0]["false_flat_2021_present"])
    checks["false_flat_finite"] = bool(len(profile_rows) and int(profile_rows.iloc[0]["false_flat_2021_episode_days"]) <= int(g["false_flat_2021_max_market_state_episode_days"]))
    checks["later_events_observable"] = bool(len(profile_rows) and profile_rows.iloc[0]["later_events_observable"])
    return bool(all(checks.values())), checks


def economic_gate_checks(metrics_by_cost: pd.DataFrame, profile: str, behavior_map: str, contract: dict, r1: dict) -> tuple[bool, dict[str, bool]]:
    x = metrics_by_cost.loc[(metrics_by_cost["profile"] == profile) & (metrics_by_cost["behavior_map"] == behavior_map)].set_index("cost_bps")
    checks: dict[str, bool] = {}
    g = contract["economic_hard_gates"]
    dd = r1["replacement_semantics"]
    for required_cost in (5.0, 10.0, 20.0, 50.0):
        if required_cost not in x.index:
            raise P55ValidationError(f"missing cost row {required_cost} for {profile}/{behavior_map}")
    m5, m10, m20, m50 = (x.loc[c] for c in (5.0, 10.0, 20.0, 50.0))
    checks["cagr_5"] = float(m5["candidate_minus_baseline_cagr_pp"]) >= float(g["at_5bps"]["candidate_minus_baseline_cagr_pp_min"])
    checks["dd_5"] = float(m5["max_drawdown_absolute_worsening"]) <= float(dd["at_5bps_max_drawdown_absolute_worsening_max"])
    checks["calmar_5"] = np.isfinite(float(m5["calmar_ratio_vs_baseline"])) and float(m5["calmar_ratio_vs_baseline"]) >= float(g["at_5bps"]["calmar_ratio_vs_baseline_min"])
    checks["turnover_5"] = np.isfinite(float(m5["turnover_ratio_vs_baseline"])) and float(m5["turnover_ratio_vs_baseline"]) <= float(g["at_5bps"]["turnover_ratio_vs_baseline_max"])
    checks["cagr_10"] = float(m10["candidate_minus_baseline_cagr_pp"]) >= float(g["at_10bps"]["candidate_minus_baseline_cagr_pp_min"])
    checks["dd_10"] = float(m10["max_drawdown_absolute_worsening"]) <= float(dd["at_10bps_max_drawdown_absolute_worsening_max"])
    checks["end_20"] = float(m20["end_multiple_ratio_vs_baseline"]) >= float(g["at_20bps"]["end_multiple_ratio_vs_baseline_min"])
    checks["positive_50"] = float(m50["candidate_end_multiple"]) > 0.0
    useful = (
        float(m5["candidate_cagr"]) > float(m5["baseline_cagr"]) + 1e-12
        or float(m5["candidate_end_multiple"]) > float(m5["baseline_end_multiple"]) + 1e-12
        or (
            float(m5["max_drawdown_improvement_abs"]) >= float(dd["minimum_usefulness_drawdown_improvement_min"])
            and float(m5["candidate_minus_baseline_cagr_pp"]) >= -0.005
        )
    )
    checks["minimum_usefulness"] = bool(useful)
    checks["positive_nav_all_costs"] = bool((x["candidate_end_multiple"].astype(float) > 0.0).all())
    return bool(all(checks.values())), checks


def robustness_pass(start_rows: pd.DataFrame, held_rows: pd.DataFrame, profile: str, behavior_map: str, contract: dict) -> tuple[bool, dict[str, bool]]:
    s = start_rows.loc[(start_rows["profile"] == profile) & (start_rows["behavior_map"] == behavior_map), "relative_cagr_pp"].astype(float)
    h = held_rows.loc[(held_rows["profile"] == profile) & (held_rows["behavior_map"] == behavior_map), "relative_cagr_pp"].astype(float)
    sg = contract["start_date_robustness"]
    hg = contract["event_held_out_robustness"]
    if len(s) != len(sg["starts"]):
        raise P55ValidationError("missing start-date robustness rows")
    if len(h) != len(hg["economic_window_events"]):
        raise P55ValidationError("missing held-out robustness rows")
    checks = {
        "start_worst": float(s.min()) >= float(sg["worst_relative_cagr_pp_min"]),
        "start_median": float(s.median()) >= float(sg["median_relative_cagr_pp_min"]),
        "heldout_worst": float(h.min()) >= -0.015,
        "heldout_median": float(h.median()) >= -0.005,
    }
    return bool(all(checks.values())), checks


def add_broad_policy_pass(gates: pd.DataFrame, contract: dict) -> pd.DataFrame:
    out = gates.copy()
    profiles = contract["broad_policy_robustness"]["profile_order"]
    maps = contract["broad_policy_robustness"]["map_order"]
    base_pass = {(r.profile, r.behavior_map): bool(r.non_selection_pass) for r in out.itertuples(index=False)}

    def adjacent(items: list[str], value: str) -> Iterable[str]:
        i = items.index(value)
        if i > 0:
            yield items[i - 1]
        if i + 1 < len(items):
            yield items[i + 1]

    broad = []
    for r in out.itertuples(index=False):
        ok = False
        if bool(r.non_selection_pass):
            ok = any(base_pass.get((p, r.behavior_map), False) for p in adjacent(profiles, r.profile))
            ok = ok or any(base_pass.get((r.profile, m), False) for m in adjacent(maps, r.behavior_map))
        broad.append(bool(ok))
    out["broad_policy_pass"] = broad
    out["eligible"] = out["non_selection_pass"].astype(bool) & out["broad_policy_pass"].astype(bool)
    return out


def select_candidate(gates: pd.DataFrame, metrics_by_cost: pd.DataFrame, contract: dict) -> dict[str, object]:
    eligible = gates.loc[gates["eligible"].astype(bool), ["profile", "behavior_map"]].copy()
    if eligible.empty:
        return {
            "status": "NO_PROMOTION_FAIL_STOP",
            "profile_selected": None,
            "behavior_map_selected": None,
            "production_authorized": False,
        }
    m5 = metrics_by_cost.loc[metrics_by_cost["cost_bps"].astype(float) == 5.0].copy()
    pool = eligible.merge(m5, on=["profile", "behavior_map"], how="inner")
    if len(pool) != len(eligible):
        raise P55ValidationError("missing 5bps metrics for eligible candidates")
    best_cagr = float(pool["candidate_cagr"].max())
    threshold = float(contract["selection_rule"]["near_tie_threshold_annualized_cagr"])
    pool = pool.loc[pool["candidate_cagr"].astype(float) >= best_cagr - threshold - 1e-12].copy()
    map_order = {m: i for i, m in enumerate(contract["broad_policy_robustness"]["map_order"])}
    pool["map_order"] = pool["behavior_map"].map(map_order).astype(int)
    pool["balanced_profile_preference"] = (pool["profile"] != "BALANCED").astype(int)
    pool["abs_max_drawdown"] = pool["candidate_max_drawdown"].astype(float).abs()
    pool = pool.sort_values(
        ["candidate_calmar", "candidate_sharpe", "abs_max_drawdown", "candidate_turnover", "map_order", "balanced_profile_preference", "profile", "behavior_map"],
        ascending=[False, False, True, True, True, True, True, True],
        kind="stable",
    )
    win = pool.iloc[0]
    return {
        "status": "PASS_RESEARCH_CANDIDATE",
        "profile_selected": str(win["profile"]),
        "behavior_map_selected": str(win["behavior_map"]),
        "five_bps_cagr": float(win["candidate_cagr"]),
        "five_bps_calmar": float(win["candidate_calmar"]),
        "five_bps_sharpe": float(win["candidate_sharpe"]),
        "five_bps_max_drawdown": float(win["candidate_max_drawdown"]),
        "five_bps_turnover": float(win["candidate_turnover"]),
        "production_authorized": False,
    }
