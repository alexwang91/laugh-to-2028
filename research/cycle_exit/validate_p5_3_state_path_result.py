from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "research" / "results" / "p5_3_state_paths"
P52_DIGEST = ROOT / "research" / "results" / "p5_2_feature_evidence" / "summary.sha256"
CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_state_model_contract.json"
EVIDENCE_CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_state_path_evidence_contract.json"


class ValidationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> str:
    summary_path = RESULT_DIR / "summary.json"
    digest_path = RESULT_DIR / "summary.sha256"
    if not summary_path.exists() or not digest_path.exists():
        raise ValidationError("P5.3 summary/digest missing")

    digest = digest_path.read_text().strip()
    if sha256(summary_path) != digest:
        raise ValidationError("P5.3 summary digest mismatch")

    summary = json.loads(summary_path.read_text())
    state_contract = json.loads(CONTRACT.read_text())
    evidence_contract = json.loads(EVIDENCE_CONTRACT.read_text())

    if summary["status"] != "ONE_TIME_FROZEN_STATE_PATH_EVIDENCE_COMPLETE":
        raise ValidationError("unexpected P5.3 result status")
    if summary["state_model_contract"] != "P5.3-STATE-MODEL-STRUCTURE-V1":
        raise ValidationError("unexpected state-model contract")
    if summary["p5_2_summary_sha256"] != P52_DIGEST.read_text().strip():
        raise ValidationError("P5.2 immutable dependency drift")
    if summary["profiles"] != evidence_contract["profiles"]:
        raise ValidationError("profile set/order drift")
    if summary["state_vocabulary"] != state_contract["states"]:
        raise ValidationError("state vocabulary drift")
    if summary["selection"] != {
        "profile_selected": False,
        "state_model_production_selected": False,
        "status": "STATE_PATH_EVIDENCE_ONLY",
    }:
        raise ValidationError("P5.3 selection boundary violated")
    if summary["production_authorized"] is not False:
        raise ValidationError("P5.3 production boundary violated")

    required = set(evidence_contract["required_artifacts"]) - {"summary.json", "summary.sha256"}
    if set(summary["artifact_sha256"]) != required:
        raise ValidationError("artifact set differs from frozen evidence contract")
    for filename, expected in summary["artifact_sha256"].items():
        path = RESULT_DIR / filename
        if not path.exists() or sha256(path) != expected:
            raise ValidationError(f"artifact digest mismatch: {filename}")

    paths = pd.read_csv(RESULT_DIR / "daily_state_paths.csv", parse_dates=["date"])
    expected_states = set(state_contract["states"]) | {"DATA_INSUFFICIENT"}
    if set(paths["profile"].unique()) != set(evidence_contract["profiles"]):
        raise ValidationError("daily path profile set mismatch")
    if not set(paths["state"].unique()) <= expected_states:
        raise ValidationError("unknown state in daily paths")
    if int(len(paths)) != int(summary["daily_state_path_rows"]):
        raise ValidationError("daily path row count mismatch")

    # FLAT must be absorbing for every profile after its first occurrence.
    for profile, sub in paths.groupby("profile"):
        sub = sub.sort_values("date")
        flat = sub.index[sub["state"].eq("FLAT")]
        if len(flat):
            first_pos = int(flat[0])
            # group index is inherited from CSV; locate by positional date instead.
            first_date = sub.loc[first_pos, "date"] if first_pos in sub.index else sub.loc[sub["state"].eq("FLAT"), "date"].iloc[0]
            after = sub.loc[sub["date"] >= first_date, "state"]
            if not after.eq("FLAT").all():
                raise ValidationError(f"FLAT is not absorbing for {profile}")

    profile_summary = pd.read_csv(RESULT_DIR / "profile_summary.csv")
    if set(profile_summary["profile"]) != set(evidence_contract["profiles"]):
        raise ValidationError("profile summary mismatch")
    if profile_summary["initialization_date"].isna().any():
        raise ValidationError("missing profile initialization date")

    occupancy = pd.read_csv(RESULT_DIR / "event_state_occupancy.csv")
    taxonomy = json.loads((ROOT / "research" / "cycle_exit" / "p5_1_event_taxonomy.json").read_text())
    expected_occ = summary["resolved_event_count"] * len(evidence_contract["profiles"]) * len(
        taxonomy["evaluation_buckets_relative_to_anchor_calendar_days"]
    )
    if len(occupancy) != expected_occ or len(occupancy) != summary["event_occupancy_rows"]:
        raise ValidationError("event occupancy row-count mismatch")

    firsts = pd.read_csv(RESULT_DIR / "event_state_first_occurrence.csv")
    bucket_bounds = taxonomy["evaluation_buckets_relative_to_anchor_calendar_days"]
    for row in firsts.itertuples(index=False):
        lo, hi = bucket_bounds[row.bucket]
        if not (int(lo) <= int(row.offset_days) <= int(hi)):
            raise ValidationError("first-occurrence offset outside frozen bucket")
    if len(firsts) != summary["event_first_occurrence_rows"]:
        raise ValidationError("first-occurrence row-count mismatch")

    print(f"P5.3 immutable state-path result validation PASS sha256={digest}")
    return digest


if __name__ == "__main__":
    validate()
