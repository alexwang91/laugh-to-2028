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

from research.cycle_exit import p5_3_v2_market_state as v2  # noqa: E402

CYCLE_DIR = ROOT / "research" / "cycle_exit"
RESULT_DIR = ROOT / "research" / "results" / "p5_3_v2_market_state"
V1_DIR = ROOT / "research" / "results" / "p5_3_state_paths"
P52_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"
EVIDENCE_CONTRACT = CYCLE_DIR / "p5_3_v2_state_path_evidence_contract.json"
TAXONOMY_PATH = CYCLE_DIR / "p5_1_event_taxonomy.json"
RESOLVED_EVENTS_PATH = P52_DIR / "resolved_events.csv"


class V2RunError(RuntimeError):
    pass


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evidence_contract() -> dict:
    c = json.loads(EVIDENCE_CONTRACT.read_text())
    if c["contract_id"] != "P5.3-V2-MARKET-STATE-PATH-EVIDENCE-V1":
        raise V2RunError("unexpected V2 evidence contract")
    if c["status"] != "FROZEN_BEFORE_FIRST_V2_STATE_PATH_RUN":
        raise V2RunError("V2 evidence contract not frozen")
    if git_blob_sha(v2.V2_CONTRACT_PATH) != c["architecture_contract_git_blob_sha"]:
        raise V2RunError("V2 architecture contract hash drift")
    if git_blob_sha(ROOT / "research" / "cycle_exit" / "p5_3_v2_market_state.py") != c["v2_engine_git_blob_sha"]:
        raise V2RunError("V2 engine hash drift")
    if (V1_DIR / "summary.sha256").read_text().strip() != c["immutable_v1_summary_sha256"]:
        raise V2RunError("V1 immutable digest drift")
    if (P52_DIR / "summary.sha256").read_text().strip() != c["immutable_p5_2_summary_sha256"]:
        raise V2RunError("P5.2 immutable digest drift")
    if RESULT_DIR.exists():
        raise V2RunError("V2 result directory already exists")
    return c


def write_csv(frame: pd.DataFrame, path: Path) -> str:
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")
    return sha256_file(path)


def indexed(frame: pd.DataFrame, name: str = "date") -> pd.DataFrame:
    out = frame.copy()
    out.index.name = name
    return out.reset_index()


def profile_summary(paths: pd.DataFrame, states: list[str], profiles: list[str]) -> pd.DataFrame:
    rows = []
    for profile in profiles:
        p = paths.loc[paths["profile"] == profile].sort_index()
        c = p.loc[p["market_state"] != "DATA_INSUFFICIENT"]
        transitions = int((c["market_state"] != c["market_state"].shift()).sum() - (1 if len(c) else 0))
        row = {
            "profile": profile,
            "initialization_date": c.index.min().date().isoformat() if len(c) else "",
            "classified_days": int(len(c)),
            "transition_count": transitions,
            "ever_flat": bool((c["market_state"] == "FLAT").any()),
            "first_flat_date": c.loc[c["market_state"] == "FLAT"].index.min().date().isoformat() if (c["market_state"] == "FLAT").any() else "",
            "final_market_state": str(c["market_state"].iloc[-1]) if len(c) else "",
        }
        denom = float(len(c)) if len(c) else np.nan
        for state in states:
            n = int((c["market_state"] == state).sum())
            row[f"{state.lower()}_days"] = n
            row[f"{state.lower()}_fraction"] = n / denom if np.isfinite(denom) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def flat_episodes(paths: pd.DataFrame, profiles: list[str]) -> pd.DataFrame:
    rows = []
    for profile in profiles:
        p = paths.loc[paths["profile"] == profile].sort_index()
        flat = p["market_state"].eq("FLAT")
        starts = flat & ~flat.shift(1, fill_value=False)
        ends = flat & ~flat.shift(-1, fill_value=False)
        start_dates = list(p.index[starts])
        end_dates = list(p.index[ends])
        for i, (start, end) in enumerate(zip(start_dates, end_dates), start=1):
            after = p.loc[p.index > end]
            recovery = after.loc[after["market_state"] != "FLAT"]
            rows.append({
                "profile": profile,
                "episode": i,
                "start_date": start.date().isoformat(),
                "end_date": end.date().isoformat(),
                "duration_days": int((end - start).days + 1),
                "first_nonflat_after_episode": recovery.index.min().date().isoformat() if len(recovery) else "",
            })
    return pd.DataFrame(rows)


def event_tables(paths: pd.DataFrame, taxonomy: dict, resolved: pd.DataFrame, states: list[str], profiles: list[str]):
    buckets = taxonomy["evaluation_buckets_relative_to_anchor_calendar_days"]
    occ_rows, first_rows = [], []
    severity = {s: i for i, s in enumerate(states)}
    for event in resolved.itertuples(index=False):
        anchor = pd.Timestamp(event.anchor_date)
        for profile in profiles:
            p = paths.loc[paths["profile"] == profile].sort_index()
            for bucket, bounds in buckets.items():
                start = anchor + pd.Timedelta(days=int(bounds[0]))
                end = anchor + pd.Timedelta(days=int(bounds[1]))
                sub = p.loc[start:end]
                c = sub.loc[sub["market_state"] != "DATA_INSUFFICIENT"]
                denom = float(len(c)) if len(c) else np.nan
                row = {
                    "event_id": event.event_id,
                    "event_class": event.event_class,
                    "terminal_label": bool(event.terminal_label),
                    "anchor_date": anchor.date().isoformat(),
                    "profile": profile,
                    "bucket": bucket,
                    "classified_rows": int(len(c)),
                }
                for state in states:
                    n = int((c["market_state"] == state).sum())
                    row[f"{state.lower()}_count"] = n
                    row[f"{state.lower()}_fraction"] = n / denom if np.isfinite(denom) else np.nan
                    hit = c.loc[c["market_state"] == state]
                    if len(hit):
                        dt = hit.index.min()
                        first_rows.append({
                            "event_id": event.event_id,
                            "event_class": event.event_class,
                            "terminal_label": bool(event.terminal_label),
                            "anchor_date": anchor.date().isoformat(),
                            "profile": profile,
                            "bucket": bucket,
                            "state": state,
                            "first_occurrence_date": dt.date().isoformat(),
                            "offset_days": int((dt - anchor).days),
                        })
                if len(c):
                    idx = c["market_state"].map(severity).astype(int)
                    row["de_risk_1_or_worse_fraction"] = float((idx >= severity["DE_RISK_1"]).mean())
                    row["flat_fraction"] = float((idx >= severity["FLAT"]).mean())
                else:
                    row["de_risk_1_or_worse_fraction"] = np.nan
                    row["flat_fraction"] = np.nan
                occ_rows.append(row)
    return pd.DataFrame(occ_rows), pd.DataFrame(first_rows)


def parity(paths: pd.DataFrame, pct: pd.DataFrame, counts: pd.DataFrame, profiles: list[str]) -> dict:
    v1 = pd.read_csv(V1_DIR / "daily_state_paths.csv", parse_dates=["date"]).set_index(["date", "profile"]).sort_index()
    v2i = paths.reset_index().set_index(["date", "profile"]).sort_index()
    signal_cols = [
        "raw_candidate_state", "ordinary_inputs_complete", "minimum_calibration_depth",
        "mature_texture", "rotation", "exhaustion", "strong_exhaustion", "damage", "strong_damage",
        "divergence_subchannel", "momentum_failure_subchannel", "breadth_transition_subchannel",
    ]
    same = 0
    total = 0
    atom_same = 0
    atom_total = 0
    atom_cols = [c for c in signal_cols if c not in {"raw_candidate_state", "ordinary_inputs_complete", "minimum_calibration_depth"}]
    for col in signal_cols:
        a = v2i[col]
        b = v1[col]
        if col == "minimum_calibration_depth":
            eq = a.astype(int).eq(b.astype(int))
        elif col == "raw_candidate_state":
            eq = a.astype(str).eq(b.astype(str))
        else:
            eq = a.astype(bool).eq(b.astype(bool))
        if col == "raw_candidate_state":
            raw_fraction = float(eq.mean())
        if col in atom_cols:
            atom_same += int(eq.sum()); atom_total += int(len(eq))
        same += int(eq.sum()); total += int(len(eq))

    frozen_pct = pd.read_csv(V1_DIR / "normalized_percentiles.csv", parse_dates=["date"]).set_index("date")
    frozen_counts = pd.read_csv(V1_DIR / "normalization_counts.csv", parse_dates=["date"]).set_index("date")
    normalization_equal = bool(np.allclose(pct.to_numpy(), frozen_pct.to_numpy(), rtol=0.0, atol=5e-12, equal_nan=True))
    counts_equal = bool(counts.astype(int).equals(frozen_counts.astype(int)))

    pre_parity = []
    first_flat_by_profile = {}
    for profile in profiles:
        v1p = v1.xs(profile, level="profile").sort_index()
        v2p = v2i.xs(profile, level="profile").sort_index()
        first_flat = v1p.loc[v1p["state"] == "FLAT"].index.min()
        first_flat_by_profile[profile] = first_flat.date().isoformat()
        mask = v1p.index <= first_flat
        pre_parity.extend(v2p.loc[mask, "market_state"].astype(str).eq(v1p.loc[mask, "state"].astype(str)).tolist())

    false_date = pd.Timestamp("2021-02-23")
    false_flat = bool((v2i.loc[(false_date, slice(None)), "raw_candidate_state"].astype(str) == "FLAT").all())
    post_nonflat = {
        p: bool((v2i.xs(p, level="profile").loc[lambda x: x.index > false_date, "market_state"] != "FLAT").any())
        for p in profiles
    }
    return {
        "raw_candidate_parity_fraction": raw_fraction,
        "atom_parity_fraction": float(atom_same / atom_total),
        "all_signal_field_parity_fraction": float(same / total),
        "normalization_parity": normalization_equal,
        "normalization_count_parity": counts_equal,
        "pre_first_flat_state_parity_fraction": float(np.mean(pre_parity)),
        "first_v1_flat_by_profile": first_flat_by_profile,
        "false_flat_reproduced": false_flat,
        "post_false_flat_nonflat_by_profile": post_nonflat,
    }


def run() -> dict:
    e = load_evidence_contract()
    arch = v2.load_v2_contract()
    paths, pct, counts = v2.evaluate_all_profiles_v2(v2_contract=arch)
    profiles = list(e["profiles"])
    states = list(arch["architecture_layers"]["MARKET_STATE"]["severity_order"])
    p = parity(paths, pct, counts, profiles)

    if p["raw_candidate_parity_fraction"] != 1.0 or p["atom_parity_fraction"] != 1.0:
        raise V2RunError("V1 signal parity failed")
    if not p["normalization_parity"] or not p["normalization_count_parity"]:
        raise V2RunError("V1 normalization parity failed")
    if p["pre_first_flat_state_parity_fraction"] != 1.0:
        raise V2RunError("pre-first-FLAT state parity failed")
    if not p["false_flat_reproduced"]:
        raise V2RunError("2021-02-23 false raw FLAT not reproduced")

    taxonomy = json.loads(TAXONOMY_PATH.read_text())
    resolved = pd.read_csv(RESOLVED_EVENTS_PATH)
    occupancy, first = event_tables(paths, taxonomy, resolved, states, profiles)
    later = resolved.loc[pd.to_datetime(resolved["anchor_date"]) > pd.Timestamp("2021-02-23")]
    later_ids = set(later["event_id"].astype(str))
    later_obs = occupancy.loc[occupancy["event_id"].astype(str).isin(later_ids)]
    later_events_observable = bool(len(later_ids) > 0 and (later_obs.groupby("event_id")["classified_rows"].max() > 0).all())
    post_nonflat_all = bool(all(p["post_false_flat_nonflat_by_profile"].values()))
    architecture_pass = bool(later_events_observable and post_nonflat_all)

    RESULT_DIR.mkdir(parents=True)
    hashes = {}
    hashes["daily_market_state_paths.csv"] = write_csv(indexed(paths), RESULT_DIR / "daily_market_state_paths.csv")
    hashes["normalized_percentiles.csv"] = write_csv(indexed(pct), RESULT_DIR / "normalized_percentiles.csv")
    hashes["normalization_counts.csv"] = write_csv(indexed(counts), RESULT_DIR / "normalization_counts.csv")
    hashes["profile_summary.csv"] = write_csv(profile_summary(paths, states, profiles), RESULT_DIR / "profile_summary.csv")
    hashes["flat_episodes.csv"] = write_csv(flat_episodes(paths, profiles), RESULT_DIR / "flat_episodes.csv")
    hashes["event_state_occupancy.csv"] = write_csv(occupancy, RESULT_DIR / "event_state_occupancy.csv")
    hashes["event_state_first_occurrence.csv"] = write_csv(first, RESULT_DIR / "event_state_first_occurrence.csv")
    parity_path = RESULT_DIR / "v1_v2_parity_summary.json"
    parity_path.write_text(json.dumps(p, indent=2, sort_keys=True) + "\n")
    hashes["v1_v2_parity_summary.json"] = sha256_file(parity_path)

    summary = {
        "study_id": e["contract_id"],
        "architecture_contract_id": arch["contract_id"],
        "status": "ONE_TIME_FROZEN_V2_MARKET_STATE_EVIDENCE_COMPLETE",
        "architecture_pass": architecture_pass,
        "raw_candidate_parity_fraction": p["raw_candidate_parity_fraction"],
        "atom_parity_fraction": p["atom_parity_fraction"],
        "normalization_parity": p["normalization_parity"],
        "normalization_count_parity": p["normalization_count_parity"],
        "pre_first_flat_state_parity_fraction": p["pre_first_flat_state_parity_fraction"],
        "false_flat_reproduced": p["false_flat_reproduced"],
        "post_false_flat_nonflat_exists": post_nonflat_all,
        "later_events_observable": later_events_observable,
        "profile_selected": False,
        "p5_4_mapping_selected": False,
        "risk_permission_unlock_authorized": False,
        "production_authorized": False,
        "artifact_sha256": hashes,
    }
    summary_path = RESULT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    digest = sha256_file(summary_path)
    (RESULT_DIR / "summary.sha256").write_text(digest + "\n")
    print(f"P5.3 V2 market-state evidence complete architecture_pass={architecture_pass} summary_sha256={digest}")
    return summary


if __name__ == "__main__":
    run()
