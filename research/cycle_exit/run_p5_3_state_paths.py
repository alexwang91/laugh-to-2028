from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

import p5_3_state_model as model

ROOT = Path(__file__).resolve().parents[2]
CYCLE_DIR = ROOT / "research" / "cycle_exit"
EVIDENCE_CONTRACT_PATH = CYCLE_DIR / "p5_3_state_path_evidence_contract.json"
TAXONOMY_PATH = CYCLE_DIR / "p5_1_event_taxonomy.json"
P52_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"
P52_SUMMARY_DIGEST = P52_DIR / "summary.sha256"
RESOLVED_EVENTS_PATH = P52_DIR / "resolved_events.csv"
RESULT_DIR = ROOT / "research" / "results" / "p5_3_state_paths"


class P53RunError(RuntimeError):
    pass


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def load_evidence_contract() -> dict:
    c = json.loads(EVIDENCE_CONTRACT_PATH.read_text(encoding="utf-8"))
    if c.get("contract_id") != "P5.3-STATE-PATH-EVIDENCE-V1":
        raise P53RunError("unexpected P5.3 evidence contract")
    if c.get("status") != "FROZEN_BEFORE_FIRST_STATE_PATH_RUN":
        raise P53RunError("P5.3 evidence contract is not frozen")
    if c["research_integrity"].get("production_authorization") != "NONE":
        raise P53RunError("P5.3 evidence run cannot authorize production")
    if _git_blob_sha(model.CONTRACT_PATH) != c["state_model_contract_git_blob_sha"]:
        raise P53RunError("state-model contract blob differs from frozen evidence dependency")
    if P52_SUMMARY_DIGEST.read_text().strip() != c["p5_2_summary_sha256"]:
        raise P53RunError("P5.2 immutable summary digest differs from frozen dependency")
    return c


def _write_csv(frame: pd.DataFrame, path: Path) -> str:
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _with_index_column(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    out = frame.copy()
    out.index.name = name
    return out.reset_index()


def _profile_summary(paths: pd.DataFrame, contract: dict) -> pd.DataFrame:
    states = contract["severity_order"]
    rows: list[dict] = []
    for profile in contract["profiles"]:
        sub = paths.loc[paths["profile"] == profile].sort_index()
        classified = sub.loc[sub["state"] != model.DIAGNOSTIC_DATA_INSUFFICIENT]
        init_date = classified.index.min() if len(classified) else pd.NaT
        transitions = int((classified["state"] != classified["state"].shift()).sum() - (1 if len(classified) else 0))
        row = {
            "profile": profile,
            "initialization_date": init_date.date().isoformat() if pd.notna(init_date) else "",
            "data_insufficient_days": int((sub["state"] == model.DIAGNOSTIC_DATA_INSUFFICIENT).sum()),
            "classified_days": int(len(classified)),
            "post_initialization_incomplete_input_days": int((classified["ordinary_inputs_complete"] == False).sum()),  # noqa: E712
            "transition_count": transitions,
            "ever_flat": bool((classified["state"] == "FLAT").any()),
            "first_flat_date": (
                classified.loc[classified["state"] == "FLAT"].index.min().date().isoformat()
                if (classified["state"] == "FLAT").any()
                else ""
            ),
            "final_state": str(classified["state"].iloc[-1]) if len(classified) else "",
        }
        denom = float(len(classified)) if len(classified) else float("nan")
        for state in states:
            count = int((classified["state"] == state).sum())
            row[f"{state.lower()}_days"] = count
            row[f"{state.lower()}_fraction"] = count / denom if np.isfinite(denom) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def _event_tables(paths: pd.DataFrame, taxonomy: dict, resolved: pd.DataFrame, contract: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    states = contract["severity_order"]
    severity = {state: i for i, state in enumerate(states)}
    buckets = taxonomy["evaluation_buckets_relative_to_anchor_calendar_days"]
    occupancy_rows: list[dict] = []
    first_rows: list[dict] = []

    for event in resolved.itertuples(index=False):
        anchor = pd.Timestamp(event.anchor_date)
        for profile in contract["profiles"]:
            p = paths.loc[paths["profile"] == profile].sort_index()
            for bucket_name, bounds in buckets.items():
                start = anchor + pd.Timedelta(days=int(bounds[0]))
                end = anchor + pd.Timedelta(days=int(bounds[1]))
                sub = p.loc[start:end]
                classified = sub.loc[sub["state"] != model.DIAGNOSTIC_DATA_INSUFFICIENT]
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
                    "data_insufficient_rows": int((sub["state"] == model.DIAGNOSTIC_DATA_INSUFFICIENT).sum()),
                    "classified_rows": int(len(classified)),
                }
                for state in states:
                    count = int((classified["state"] == state).sum())
                    row[f"{state.lower()}_count"] = count
                    row[f"{state.lower()}_fraction"] = count / denom if np.isfinite(denom) else float("nan")
                    occur = classified.loc[classified["state"] == state]
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
                                "state": state,
                                "first_occurrence_date": first_date.date().isoformat(),
                                "offset_days": int((first_date - anchor).days),
                            }
                        )
                if len(classified):
                    indices = classified["state"].map(severity).astype(int)
                    row["de_risk_1_or_worse_fraction"] = float((indices >= severity["DE_RISK_1"]).mean())
                    row["de_risk_2_or_worse_fraction"] = float((indices >= severity["DE_RISK_2"]).mean())
                    row["flat_fraction"] = float((indices >= severity["FLAT"]).mean())
                else:
                    row["de_risk_1_or_worse_fraction"] = float("nan")
                    row["de_risk_2_or_worse_fraction"] = float("nan")
                    row["flat_fraction"] = float("nan")
                occupancy_rows.append(row)

    return pd.DataFrame(occupancy_rows), pd.DataFrame(first_rows)


def run() -> dict:
    evidence_contract = load_evidence_contract()
    state_contract = model.load_contract()
    feature_panel = model.load_feature_panel()

    if RESULT_DIR.exists():
        raise P53RunError("P5.3 result directory already exists")

    percentiles, counts, min_depth = model.causal_percentiles(feature_panel, state_contract)
    paths = pd.concat(
        [
            model.evaluate_profile(feature_panel, percentiles, counts, min_depth, state_contract, profile)
            for profile in evidence_contract["profiles"]
        ]
    ).sort_index()

    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    resolved = pd.read_csv(RESOLVED_EVENTS_PATH)
    occupancy, first_occurrence = _event_tables(paths, taxonomy, resolved, state_contract)
    profile_summary = _profile_summary(paths, state_contract)

    RESULT_DIR.mkdir(parents=True)
    hashes: dict[str, str] = {}
    hashes["normalized_percentiles.csv"] = _write_csv(
        _with_index_column(percentiles, "date"), RESULT_DIR / "normalized_percentiles.csv"
    )
    hashes["normalization_counts.csv"] = _write_csv(
        _with_index_column(counts, "date"), RESULT_DIR / "normalization_counts.csv"
    )
    hashes["daily_state_paths.csv"] = _write_csv(
        _with_index_column(paths, "date"), RESULT_DIR / "daily_state_paths.csv"
    )
    hashes["profile_summary.csv"] = _write_csv(profile_summary, RESULT_DIR / "profile_summary.csv")
    hashes["event_state_occupancy.csv"] = _write_csv(occupancy, RESULT_DIR / "event_state_occupancy.csv")
    hashes["event_state_first_occurrence.csv"] = _write_csv(
        first_occurrence, RESULT_DIR / "event_state_first_occurrence.csv"
    )

    initialization_dates = {
        str(row.profile): str(row.initialization_date) for row in profile_summary.itertuples(index=False)
    }
    payload = {
        "study_id": evidence_contract["contract_id"],
        "status": "ONE_TIME_FROZEN_STATE_PATH_EVIDENCE_COMPLETE",
        "state_model_contract": state_contract["contract_id"],
        "state_model_contract_git_blob_sha": evidence_contract["state_model_contract_git_blob_sha"],
        "p5_2_summary_sha256": evidence_contract["p5_2_summary_sha256"],
        "profiles": evidence_contract["profiles"],
        "state_vocabulary": state_contract["states"],
        "initialization_dates": initialization_dates,
        "daily_feature_rows": int(len(feature_panel)),
        "daily_state_path_rows": int(len(paths)),
        "resolved_event_count": int(len(resolved)),
        "event_occupancy_rows": int(len(occupancy)),
        "event_first_occurrence_rows": int(len(first_occurrence)),
        "selection": {
            "profile_selected": False,
            "state_model_production_selected": False,
            "status": "STATE_PATH_EVIDENCE_ONLY",
        },
        "production_authorized": False,
        "artifact_sha256": hashes,
    }
    summary_path = RESULT_DIR / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    (RESULT_DIR / "summary.sha256").write_text(digest + "\n", encoding="utf-8")
    print(f"P5.3 frozen state-path evidence complete summary_sha256={digest}")
    return payload


if __name__ == "__main__":
    run()
