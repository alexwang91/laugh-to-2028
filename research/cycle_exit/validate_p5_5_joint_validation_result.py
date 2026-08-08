from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research" / "results" / "p5_5_joint_validation"
REQUIRED_ARTIFACTS = {
    "input_manifest.json",
    "candidate_metrics_by_cost.csv",
    "event_behavior.csv",
    "start_date_robustness.csv",
    "event_held_out_robustness.csv",
    "candidate_gate_matrix.csv",
    "selected_candidate.json",
}


class ValidationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> str:
    summary_path = RESULT / "summary.json"
    digest_path = RESULT / "summary.sha256"
    if not summary_path.exists() or not digest_path.exists():
        raise ValidationError("missing P5.5 summary artifacts")
    actual = sha256(summary_path)
    expected = digest_path.read_text().strip()
    if actual != expected:
        raise ValidationError("P5.5 summary digest mismatch")

    s = json.loads(summary_path.read_text())
    if s.get("status") != "ONE_TIME_FROZEN_P5_5_VALIDATION_COMPLETE":
        raise ValidationError("unexpected P5.5 status")
    if int(s.get("candidate_count", -1)) != 12:
        raise ValidationError("candidate count drift")
    if s.get("production_authorized") is not False:
        raise ValidationError("production authorization forbidden")
    if s.get("risk_permission_unlock_authorized") is not False:
        raise ValidationError("risk permission unlock forbidden")
    if s.get("p5_5_r2_applied") is not True or s.get("common_observable_end") != "2026-02-28":
        raise ValidationError("P5.5 R2 common-coverage correction missing")
    if s.get("event_diagnostics_include_2021_without_fabricated_brrk_economics") is not True:
        raise ValidationError("2021 diagnostics/economics boundary drift")

    selection = json.loads((RESULT / "selected_candidate.json").read_text())
    if selection.get("production_authorized") is not False:
        raise ValidationError("selected candidate authorized production")
    if selection.get("status") not in {"PASS_RESEARCH_CANDIDATE", "NO_PROMOTION_FAIL_STOP"}:
        raise ValidationError("unexpected selection status")
    if selection.get("status") == "NO_PROMOTION_FAIL_STOP":
        if selection.get("profile_selected") is not None or selection.get("behavior_map_selected") is not None:
            raise ValidationError("no-promotion result selected a candidate")
        if s.get("p5_6_integration_eligible") is not False:
            raise ValidationError("P5.6 eligible despite no selection")
    else:
        if selection.get("profile_selected") not in {"EARLY", "BALANCED", "CONSERVATIVE"}:
            raise ValidationError("invalid selected profile")
        if selection.get("behavior_map_selected") not in {"HARD_ONLY", "GENTLE", "BALANCED", "DEFENSIVE"}:
            raise ValidationError("invalid selected map")
        if s.get("p5_6_integration_eligible") is not True:
            raise ValidationError("selected research candidate not handed to P5.6")

    artifacts = s.get("artifact_sha256", {})
    if set(artifacts) != REQUIRED_ARTIFACTS:
        raise ValidationError("unexpected P5.5 artifact set")
    for name, digest in artifacts.items():
        path = RESULT / name
        if not path.exists() or sha256(path) != digest:
            raise ValidationError(f"P5.5 artifact digest mismatch: {name}")

    metrics = pd.read_csv(RESULT / "candidate_metrics_by_cost.csv")
    if len(metrics) != 48:
        raise ValidationError("expected 12 candidates x 4 cost rows")
    if set(metrics["cost_bps"].astype(float)) != {5.0, 10.0, 20.0, 50.0}:
        raise ValidationError("cost grid drift")
    if (metrics["candidate_end_multiple"].astype(float) <= 0.0).any():
        raise ValidationError("nonpositive candidate wealth")

    event = pd.read_csv(RESULT / "event_behavior.csv")
    if len(event) != 12 * 11 * 5:
        raise ValidationError("event behavior row count drift")
    if not bool(event["false_flat_2021_present"].astype(bool).all()):
        raise ValidationError("known 2021 false FLAT hidden")

    starts = pd.read_csv(RESULT / "start_date_robustness.csv")
    held = pd.read_csv(RESULT / "event_held_out_robustness.csv")
    gates = pd.read_csv(RESULT / "candidate_gate_matrix.csv")
    if len(starts) != 12 * 4 or len(held) != 12 * 6 or len(gates) != 12:
        raise ValidationError("robustness/gate row count drift")
    eligible_count = int(gates["eligible"].astype(bool).sum())
    if eligible_count != int(s.get("eligible_candidate_count", -1)):
        raise ValidationError("eligible candidate count mismatch")

    manifest = json.loads((RESULT / "input_manifest.json").read_text())
    if manifest.get("evaluation_session_start") != "2022-12-10":
        raise ValidationError("economic start drift")
    if manifest.get("evaluation_session_end") != "2026-02-28":
        raise ValidationError("effective economic end drift")
    correction = manifest.get("common_observable_end_correction", {})
    if correction.get("forward_fill_market_state") is not False or correction.get("fabricated_state_extension") is not False:
        raise ValidationError("forbidden state extension")

    print(f"P5.5 immutable validation PASS sha256={actual} selection={selection.get('status')}")
    return actual


if __name__ == "__main__":
    validate()
