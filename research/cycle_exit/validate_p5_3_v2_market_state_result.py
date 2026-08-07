from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "research" / "results" / "p5_3_v2_market_state"
EVIDENCE_CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_v2_evidence_contract.json"
ARCHITECTURE_CONTRACT = ROOT / "research" / "cycle_exit" / "p5_3_v2_architecture_contract.json"
V1_RESULT = ROOT / "research" / "results" / "p5_3_state_paths"


class ValidationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> str:
    summary_path = RESULT_DIR / "summary.json"
    digest_path = RESULT_DIR / "summary.sha256"
    if not summary_path.exists() or not digest_path.exists():
        raise ValidationError("P5.3 V2 summary/digest missing")

    digest = digest_path.read_text().strip()
    if sha256(summary_path) != digest:
        raise ValidationError("P5.3 V2 summary digest mismatch")

    summary = json.loads(summary_path.read_text())
    evidence = json.loads(EVIDENCE_CONTRACT.read_text())
    architecture = json.loads(ARCHITECTURE_CONTRACT.read_text())

    if summary["status"] != "ONE_TIME_FROZEN_V2_MARKET_STATE_EVIDENCE_COMPLETE":
        raise ValidationError("unexpected V2 result status")
    if summary["study_id"] != evidence["contract_id"]:
        raise ValidationError("V2 evidence contract mismatch")
    if summary["architecture_contract"] != architecture["contract_id"]:
        raise ValidationError("V2 architecture contract mismatch")
    if summary["v1_result_summary_sha256"] != (V1_RESULT / "summary.sha256").read_text().strip():
        raise ValidationError("immutable V1 dependency drift")
    if summary["profiles"] != evidence["profiles"]:
        raise ValidationError("V2 profile set/order drift")
    if summary["state_vocabulary"] != architecture["architecture_layers"]["MARKET_STATE"]["state_vocabulary"]:
        raise ValidationError("V2 state vocabulary drift")
    if summary["selection"] != evidence["selection"]:
        raise ValidationError("V2 selection boundary drift")
    if summary["production_authorized"] is not False:
        raise ValidationError("V2 production boundary violated")

    parity = summary["parity"]
    required_parity = [
        "normalized_feature_values_pass",
        "normalization_counts_pass",
        "signal_atoms_and_raw_candidate_pass",
        "false_flat_2021_02_23_reproduced",
        "all_signal_parity_pass",
        "market_state_matches_v1_through_first_flat_inclusive",
    ]
    if not all(parity.get(k) is True for k in required_parity):
        raise ValidationError("V2 parity gate failed")

    evaluation = summary["architecture_evaluation"]
    if evaluation["false_flat_2021_02_23_reproduced"] is not True:
        raise ValidationError("V2 hid immutable false FLAT")
    if evaluation["market_state_can_unlock_operational_risk"] is not False:
        raise ValidationError("V2 MARKET_STATE gained operational unlock authority")
    if evaluation["signal_quality_accepted"] is not False:
        raise ValidationError("V2 architecture evidence improperly accepted signal quality")
    if evaluation["profile_selected"] is not False or evaluation["p5_4_mapping_selected"] is not False:
        raise ValidationError("V2 evidence improperly selected downstream behavior")

    expected_artifacts = set(evidence["required_artifacts"]) - {"summary.json", "summary.sha256"}
    if set(summary["artifact_sha256"]) != expected_artifacts:
        raise ValidationError("V2 artifact set differs from frozen evidence contract")
    for filename, expected in summary["artifact_sha256"].items():
        path = RESULT_DIR / filename
        if not path.exists() or sha256(path) != expected:
            raise ValidationError(f"V2 artifact digest mismatch: {filename}")

    paths = pd.read_csv(RESULT_DIR / "daily_market_state_paths.csv", parse_dates=["date"])
    allowed = set(summary["state_vocabulary"]) | {"DATA_INSUFFICIENT"}
    if set(paths["profile"].unique()) != set(evidence["profiles"]):
        raise ValidationError("V2 daily path profile mismatch")
    if not set(paths["market_state"].unique()) <= allowed:
        raise ValidationError("unknown V2 market state")
    if len(paths) != int(summary["daily_market_state_rows"]):
        raise ValidationError("V2 daily path row-count mismatch")

    false_flat = paths.loc[paths["date"].eq(pd.Timestamp("2021-02-23"))]
    if len(false_flat) != 3 or set(false_flat["raw_candidate_state"].astype(str)) != {"FLAT"}:
        raise ValidationError("required 2021-02-23 false raw FLAT missing")

    episodes = pd.read_csv(RESULT_DIR / "flat_episodes.csv")
    if len(episodes) != int(summary["flat_episode_rows"]):
        raise ValidationError("V2 flat-episode row-count mismatch")
    if len(episodes):
        if (episodes["duration_days"].astype(int) <= 0).any():
            raise ValidationError("invalid V2 FLAT episode duration")

    occupancy = pd.read_csv(RESULT_DIR / "event_market_state_occupancy.csv")
    if len(occupancy) != int(summary["event_occupancy_rows"]):
        raise ValidationError("V2 occupancy row-count mismatch")

    firsts = pd.read_csv(RESULT_DIR / "event_market_state_first_occurrence.csv")
    if len(firsts) != int(summary["event_first_occurrence_rows"]):
        raise ValidationError("V2 first-occurrence row-count mismatch")

    comparison = pd.read_csv(RESULT_DIR / "v1_v2_daily_comparison.csv", parse_dates=["date"])
    through = comparison.loc[comparison["date"] <= pd.Timestamp("2021-02-23")]
    if not through["state_changed_vs_v1"].astype(bool).eq(False).all():
        raise ValidationError("V2 differs from V1 before/at first FLAT")

    print(f"P5.3 V2 immutable MARKET_STATE result validation PASS sha256={digest}")
    return digest


if __name__ == "__main__":
    validate()
