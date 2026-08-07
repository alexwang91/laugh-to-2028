from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.cycle_exit import p5_3_state_model as v1_model  # noqa: E402
from research.cycle_exit import p5_3_v2_market_state as v2_model  # noqa: E402

CYCLE_DIR = ROOT / "research" / "cycle_exit"
EVIDENCE_CONTRACT_PATH = CYCLE_DIR / "p5_3_v2_evidence_contract.json"
ARCHITECTURE_CONTRACT_PATH = CYCLE_DIR / "p5_3_v2_architecture_contract.json"
TAXONOMY_PATH = CYCLE_DIR / "p5_1_event_taxonomy.json"
P52_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"
RESOLVED_EVENTS_PATH = P52_DIR / "resolved_events.csv"
V1_RESULT_DIR = ROOT / "research" / "results" / "p5_3_state_paths"
RESULT_DIR = ROOT / "research" / "results" / "p5_3_v2_market_state"


class P53V2RunError(RuntimeError):
    pass


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evidence_contract() -> dict:
    c = json.loads(EVIDENCE_CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("contract_id") != "P5.3-V2-MARKET-STATE-EVIDENCE-V1":
        raise P53V2RunError("unexpected V2 evidence contract")
    if c.get("status") != "FROZEN_BEFORE_FIRST_V2_STATE_PATH_RUN":
        raise P53V2RunError("V2 evidence contract is not frozen")
    if _git_blob_sha(ARCHITECTURE_CONTRACT_PATH) != c["architecture_contract_git_blob_sha"]:
        raise P53V2RunError("V2 architecture-contract blob drift")
    if (V1_RESULT_DIR / "summary.sha256").read_text().strip() != c["v1_result_summary_sha256"]:
        raise P53V2RunError("immutable V1 result digest drift")
    if (P52_DIR / "summary.sha256").read_text().strip() != c["p5_2_summary_sha256"]:
        raise P53V2RunError("immutable P5.2 digest drift")
    if c["architecture_evaluation"]["production_authorization"] != "NONE":
        raise P53V2RunError("V2 evidence cannot authorize production")
    return c


def _write_csv(frame: pd.DataFrame, path: Path) -> str:
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")
    return _sha256(path)


def _write_json(payload: dict, path: Path) -> str:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _sha256(path)


def _signal_parity() -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    signal, pct, counts = v2_model.evaluate_signal_only()

    frozen_pct = pd.read_csv(V1_RESULT_DIR / "normalized_percentiles.csv", parse_dates=["date"]).set_index("date")
    frozen_counts = pd.read_csv(V1_RESULT_DIR / "normalization_counts.csv", parse_dates=["date"]).set_index("date")
    frozen_paths = pd.read_csv(V1_RESULT_DIR / "daily_state_paths.csv", parse_dates=["date"]).set_index(["date", "profile"]).sort_index()

    pct_ok = (
        list(pct.columns) == list(frozen_pct.columns)
        and pct.index.equals(frozen_pct.index)
        and np.allclose(pct.to_numpy(), frozen_pct.to_numpy(), rtol=0.0, atol=5e-12, equal_nan=True)
    )
    counts_ok = (
        list(counts.columns) == list(frozen_counts.columns)
        and counts.index.equals(frozen_counts.index)
        and counts.astype(int).equals(frozen_counts.astype(int))
    )

    exact_columns = [
        "raw_candidate_state",
        "ordinary_inputs_complete",
        "minimum_calibration_depth",
        "mature_texture",
        "rotation",
        "exhaustion",
        "strong_exhaustion",
        "damage",
        "strong_damage",
        "divergence_subchannel",
        "momentum_failure_subchannel",
        "breadth_transition_subchannel",
    ]
    signal_ok = signal.index.equals(frozen_paths.index)
    mismatches: dict[str, int] = {}
    if signal_ok:
        for column in exact_columns:
            if column == "minimum_calibration_depth":
                equal = signal[column].astype(int).eq(frozen_paths[column].astype(int))
            elif column == "raw_candidate_state":
                equal = signal[column].astype(str).eq(frozen_paths[column].astype(str))
            else:
                equal = signal[column].astype(bool).eq(frozen_paths[column].astype(bool))
            mismatches[column] = int((~equal).sum())
            signal_ok = signal_ok and bool(equal.all())
    else:
        mismatches["index"] = 1

    false_flat_rows = signal.loc[(pd.Timestamp("2021-02-23"), slice(None)), "raw_candidate_state"]
    false_flat_ok = len(false_flat_rows) == 3 and set(false_flat_rows.astype(str)) == {"FLAT"}

    parity = {
        "normalized_feature_values_pass": bool(pct_ok),
        "normalization_counts_pass": bool(counts_ok),
        "signal_atoms_and_raw_candidate_pass": bool(signal_ok),
        "signal_column_mismatch_counts": mismatches,
        "false_flat_2021_02_23_reproduced": bool(false_flat_ok),
        "all_signal_parity_pass": bool(pct_ok and counts_ok and signal_ok and false_flat_ok),
    }
    if not parity["all_signal_parity_pass"]:
        raise P53V2RunError(f"V1 signal parity failed: {parity}")
    return parity, signal, pct, counts


def _profile_summary(paths: pd.DataFrame, severity: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    for profile, sub in paths.groupby("profile"):
        sub = sub.sort_index()
        classified = sub.loc[sub["market_state"] != v1_model.DIAGNOSTIC_DATA_INSUFFICIENT]
        transitions = int((classified["market_state"] != classified["market_state"].shift()).sum() - 1) if len(classified) else 0
        first_flat = classified.loc[classified["market_state"] == "FLAT"].index.min() if (classified["market_state"] == "FLAT").any() else pd.NaT
        after_first_flat = classified.loc[classified.index > first_flat] if pd.notna(first_flat) else classified.iloc[0:0]
        recovery = after_first_flat.loc[after_first_flat["market_state"] != "FLAT"].index.min() if len(after_first_flat) else pd.NaT
        row = {
            "profile": profile,
            "initialization_date": classified.index.min().date().isoformat() if len(classified) else "",
            "classified_days": int(len(classified)),
            "transition_count": transitions,
            "first_flat_date": first_flat.date().isoformat() if pd.notna(first_flat) else "",
            "recovered_after_first_flat": bool(pd.notna(recovery)),
            "first_recovery_date": recovery.date().isoformat() if pd.notna(recovery) else "",
            "final_market_state": str(classified["market_state"].iloc[-1]) if len(classified) else "",
        }
        denom = float(len(classified)) if len(classified) else float("nan")
        for state in severity:
            count = int((classified["market_state"] == state).sum())
            row[f"{state.lower()}_days"] = count
            row[f"{state.lower()}_fraction"] = count / denom if np.isfinite(denom) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows).sort_values("profile")


def _flat_episodes(paths: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for profile, sub in paths.groupby("profile"):
        classified = sub.loc[sub["market_state"] != v1_model.DIAGNOSTIC_DATA_INSUFFICIENT].sort_index()
        in_episode = False
        start: pd.Timestamp | None = None
        episode_number = 0
        dates: list[pd.Timestamp] = []
        for dt, row in classified.iterrows():
            is_flat = row["market_state"] == "FLAT"
            if is_flat and not in_episode:
                in_episode = True
                start = dt
                dates = [dt]
                episode_number += 1
            elif is_flat and in_episode:
                dates.append(dt)
            elif (not is_flat) and in_episode:
                rows.append(
                    {
                        "profile": profile,
                        "episode_number": episode_number,
                        "start_date": start.date().isoformat(),
                        "end_date": dates[-1].date().isoformat(),
                        "duration_days": len(dates),
                        "recovered": True,
                        "recovery_date": dt.date().isoformat(),
                        "recovery_state": row["market_state"],
                    }
                )
                in_episode = False
                start = None
                dates = []
        if in_episode and start is not None:
            rows.append(
                {
                    "profile": profile,
                    "episode_number": episode_number,
                    "start_date": start.date().isoformat(),
                    "end_date": dates[-1].date().isoformat(),
                    "duration_days": len(dates),
                    "recovered": False,
                    "recovery_date": "",
                    "recovery_state": "",
                }
            )
    return pd.DataFrame(rows)


def _event_tables(paths: pd.DataFrame, taxonomy: dict, resolved: pd.DataFrame, profiles: list[str], severity: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    severity_index = {state: i for i, state in enumerate(severity)}
    occupancy_rows: list[dict] = []
    first_rows: list[dict] = []
    buckets = taxonomy["evaluation_buckets_relative_to_anchor_calendar_days"]

    for event in resolved.itertuples(index=False):
        anchor = pd.Timestamp(event.anchor_date)
        for profile in profiles:
            p = paths.loc[paths["profile"] == profile].sort_index()
            for bucket_name, bounds in buckets.items():
                start = anchor + pd.Timedelta(days=int(bounds[0]))
                end = anchor + pd.Timedelta(days=int(bounds[1]))
                sub = p.loc[start:end]
                classified = sub.loc[sub["market_state"] != v1_model.DIAGNOSTIC_DATA_INSUFFICIENT]
                denom = float(len(classified)) if len(classified) else float("nan")
                row = {
                    "event_id": event.event_id,
                    "event_class": event.event_class,
                    "terminal_label": bool(event.terminal_label),
                    "anchor_date": anchor.date().isoformat(),
                    "profile": profile,
                    "bucket": bucket_name,
                    "bucket_start": start.date().isoformat(),
                    "bucket_end": end.date().isoformat(),
                    "total_rows": int(len(sub)),
                    "data_insufficient_rows": int((sub["market_state"] == v1_model.DIAGNOSTIC_DATA_INSUFFICIENT).sum()),
                    "classified_rows": int(len(classified)),
                }
                for state in severity:
                    count = int((classified["market_state"] == state).sum())
                    row[f"{state.lower()}_count"] = count
                    row[f"{state.lower()}_fraction"] = count / denom if np.isfinite(denom) else float("nan")
                    occur = classified.loc[classified["market_state"] == state]
                    if len(occur):
                        first_date = occur.index.min()
                        first_rows.append(
                            {
                                "event_id": event.event_id,
                                "event_class": event.event_class,
                                "terminal_label": bool(event.terminal_label),
                                "anchor_date": anchor.date().isoformat(),
                                "profile": profile,
                                "bucket": bucket_name,
                                "market_state": state,
                                "first_occurrence_date": first_date.date().isoformat(),
                                "offset_days": int((first_date - anchor).days),
                            }
                        )
                if len(classified):
                    idx = classified["market_state"].map(severity_index).astype(int)
                    row["de_risk_1_or_worse_fraction"] = float((idx >= severity_index["DE_RISK_1"]).mean())
                    row["de_risk_2_or_worse_fraction"] = float((idx >= severity_index["DE_RISK_2"]).mean())
                    row["flat_fraction"] = float((idx >= severity_index["FLAT"]).mean())
                else:
                    row["de_risk_1_or_worse_fraction"] = float("nan")
                    row["de_risk_2_or_worse_fraction"] = float("nan")
                    row["flat_fraction"] = float("nan")
                occupancy_rows.append(row)

    return pd.DataFrame(occupancy_rows), pd.DataFrame(first_rows)


def run() -> dict:
    evidence = load_evidence_contract()
    v2_contract = v2_model.load_v2_contract()
    v1_contract = v2_model.inherited_v1_contract(v2_contract)
    feature_panel = v1_model.load_feature_panel()

    if RESULT_DIR.exists():
        raise P53V2RunError("P5.3 V2 result directory already exists")

    parity, _, pct, counts = _signal_parity()
    paths, pct_from_run, counts_from_run = v2_model.evaluate_all_profiles_v2(feature_panel, v2_contract)
    if not pct.equals(pct_from_run) or not counts.equals(counts_from_run):
        raise P53V2RunError("V2 run normalization differs from parity normalization")

    frozen_v1 = pd.read_csv(V1_RESULT_DIR / "daily_state_paths.csv", parse_dates=["date"]).set_index(["date", "profile"]).sort_index()
    v2_indexed = paths.reset_index().set_index(["date", "profile"]).sort_index()
    first_flat_date = pd.Timestamp(evidence["parity"]["required_false_flat_date"])
    v1_through = frozen_v1.loc[(slice(None, first_flat_date), slice(None)), "state"]
    v2_through = v2_indexed.loc[(slice(None, first_flat_date), slice(None)), "market_state"]
    market_state_prefix_parity = v1_through.astype(str).equals(v2_through.astype(str))
    if not market_state_prefix_parity:
        raise P53V2RunError("V2 MARKET_STATE differs from V1 before/at first FLAT")

    comparison = v2_indexed[["market_state", "raw_candidate_state"]].copy()
    comparison["v1_state"] = frozen_v1["state"]
    comparison["state_changed_vs_v1"] = comparison["market_state"].astype(str) != comparison["v1_state"].astype(str)
    comparison = comparison.reset_index()

    severity = list(v2_contract["architecture_layers"]["MARKET_STATE"]["severity_order"])
    profile_summary = _profile_summary(paths, severity)
    flat_episodes = _flat_episodes(paths)
    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    resolved = pd.read_csv(RESOLVED_EVENTS_PATH)
    occupancy, first_occurrence = _event_tables(paths, taxonomy, resolved, evidence["profiles"], severity)

    false_flat_rows = v2_indexed.loc[(first_flat_date, slice(None)), "raw_candidate_state"]
    false_flat_reproduced = len(false_flat_rows) == 3 and set(false_flat_rows.astype(str)) == {"FLAT"}
    recovered_all = bool(profile_summary["recovered_after_first_flat"].all())
    later_occupancy = occupancy.loc[pd.to_datetime(occupancy["bucket_start"]) > first_flat_date]
    later_buckets_all_classified = bool(len(later_occupancy) and (later_occupancy["classified_rows"] > 0).all())
    architecture_pass = bool(
        parity["all_signal_parity_pass"]
        and market_state_prefix_parity
        and false_flat_reproduced
        and recovered_all
        and later_buckets_all_classified
        and evidence["permission_boundary"]["market_state_can_unlock_operational_risk"] is False
    )

    parity_payload = {
        **parity,
        "market_state_matches_v1_through_first_flat_inclusive": bool(market_state_prefix_parity),
        "false_flat_date": first_flat_date.date().isoformat(),
    }

    RESULT_DIR.mkdir(parents=True)
    hashes: dict[str, str] = {}
    hashes["daily_market_state_paths.csv"] = _write_csv(paths.reset_index(), RESULT_DIR / "daily_market_state_paths.csv")
    hashes["profile_summary.csv"] = _write_csv(profile_summary, RESULT_DIR / "profile_summary.csv")
    hashes["flat_episodes.csv"] = _write_csv(flat_episodes, RESULT_DIR / "flat_episodes.csv")
    hashes["event_market_state_occupancy.csv"] = _write_csv(occupancy, RESULT_DIR / "event_market_state_occupancy.csv")
    hashes["event_market_state_first_occurrence.csv"] = _write_csv(first_occurrence, RESULT_DIR / "event_market_state_first_occurrence.csv")
    hashes["v1_v2_daily_comparison.csv"] = _write_csv(comparison, RESULT_DIR / "v1_v2_daily_comparison.csv")
    hashes["parity_summary.json"] = _write_json(parity_payload, RESULT_DIR / "parity_summary.json")

    summary = {
        "study_id": evidence["contract_id"],
        "status": "ONE_TIME_FROZEN_V2_MARKET_STATE_EVIDENCE_COMPLETE",
        "architecture_contract": evidence["architecture_contract"],
        "architecture_contract_git_blob_sha": evidence["architecture_contract_git_blob_sha"],
        "v1_result_commit": evidence["v1_result_commit"],
        "v1_result_summary_sha256": evidence["v1_result_summary_sha256"],
        "p5_2_summary_sha256": evidence["p5_2_summary_sha256"],
        "profiles": evidence["profiles"],
        "state_vocabulary": severity,
        "daily_market_state_rows": int(len(paths)),
        "resolved_event_count": int(len(resolved)),
        "event_occupancy_rows": int(len(occupancy)),
        "event_first_occurrence_rows": int(len(first_occurrence)),
        "flat_episode_rows": int(len(flat_episodes)),
        "parity": parity_payload,
        "architecture_evaluation": {
            "architecture_pass": architecture_pass,
            "false_flat_2021_02_23_reproduced": bool(false_flat_reproduced),
            "all_profiles_recovered_below_first_flat": recovered_all,
            "later_event_buckets_all_classified": later_buckets_all_classified,
            "market_state_can_unlock_operational_risk": False,
            "signal_quality_accepted": False,
            "profile_selected": False,
            "p5_4_mapping_selected": False,
        },
        "selection": evidence["selection"],
        "production_authorized": False,
        "artifact_sha256": hashes,
    }
    summary_path = RESULT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = _sha256(summary_path)
    (RESULT_DIR / "summary.sha256").write_text(digest + "\n", encoding="utf-8")
    print(f"P5.3 V2 frozen MARKET_STATE evidence complete summary_sha256={digest}")
    return summary


if __name__ == "__main__":
    run()
