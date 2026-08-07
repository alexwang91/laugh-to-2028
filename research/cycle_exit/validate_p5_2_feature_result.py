from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"
SUMMARY = RESULT_DIR / "summary.json"
DIGEST = RESULT_DIR / "summary.sha256"


class ValidationError(RuntimeError):
    pass


def validate() -> str:
    if not SUMMARY.exists() or not DIGEST.exists():
        raise ValidationError("missing P5.2 summary or digest")
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if payload.get("study_id") != "P5.2-FEATURE-FAMILIES-V1":
        raise ValidationError("unexpected study id")
    if payload.get("status") != "ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE":
        raise ValidationError("unexpected result status")
    if payload.get("production_authorized") is not False:
        raise ValidationError("P5.2 must not authorize production")
    selection = payload.get("selection", {})
    if selection.get("feature_set_selected") is not False:
        raise ValidationError("P5.2 must not select final feature set")
    if selection.get("state_thresholds_selected") is not False:
        raise ValidationError("P5.2 must not select state thresholds")
    if selection.get("status") != "DESCRIPTIVE_EVIDENCE_ONLY":
        raise ValidationError("unexpected selection status")
    if payload.get("taxonomy_contract") != "P5.1-EVENT-TAXONOMY-V1":
        raise ValidationError("taxonomy contract drift")
    if payload.get("feature_contract") != "P5.2-FEATURE-FAMILIES-V1":
        raise ValidationError("feature contract drift")
    if payload.get("available_feature_count") != 29:
        raise ValidationError("unexpected available feature count")
    if payload.get("resolved_event_count") != 11:
        raise ValidationError("unexpected resolved event count")
    if payload.get("control_event_count") != 4:
        raise ValidationError("unexpected control event count")
    if payload.get("coverage_all_pass") is not True:
        raise ValidationError("available feature coverage did not pass")
    if payload.get("pending_feature_count", 0) < 6:
        raise ValidationError("pending data-source gaps were unexpectedly removed")

    for name, expected in payload.get("artifact_sha256", {}).items():
        path = RESULT_DIR / name
        if not path.exists():
            raise ValidationError(f"missing artifact: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValidationError(f"artifact hash mismatch: {name}")

    coverage = pd.read_csv(RESULT_DIR / "feature_coverage.csv")
    if len(coverage) != 29 or set(coverage["status"]) != {"PASS"}:
        raise ValidationError("feature coverage artifact invalid")
    pending = pd.read_csv(RESULT_DIR / "pending_features.csv")
    if not (pending["status"] == "DATA_SOURCE_PENDING").all():
        raise ValidationError("pending feature status drift")
    resolved = pd.read_csv(RESULT_DIR / "resolved_events.csv")
    if int(resolved["terminal_label"].astype(bool).sum()) != 1:
        raise ValidationError("terminal-event discipline violated")
    terminal = resolved.loc[resolved["terminal_label"].astype(bool), "event_id"].tolist()
    if terminal != ["P5E-2021-NOV-TERMINAL-TOP"]:
        raise ValidationError("unexpected terminal event")

    actual_digest = hashlib.sha256(SUMMARY.read_bytes()).hexdigest()
    expected_digest = DIGEST.read_text(encoding="utf-8").strip()
    if actual_digest != expected_digest:
        raise ValidationError("summary digest mismatch")
    return actual_digest


if __name__ == "__main__":
    digest = validate()
    print(f"P5.2 immutable feature-evidence validation PASS sha256={digest}")
