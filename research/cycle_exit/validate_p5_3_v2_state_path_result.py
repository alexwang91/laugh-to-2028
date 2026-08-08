from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research" / "results" / "p5_3_v2_market_state"


class ValidationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> str:
    summary_path = RESULT / "summary.json"
    digest_path = RESULT / "summary.sha256"
    if not summary_path.exists() or not digest_path.exists():
        raise ValidationError("missing P5.3 V2 summary artifacts")
    expected = digest_path.read_text().strip()
    actual = sha256(summary_path)
    if expected != actual:
        raise ValidationError("summary digest mismatch")

    s = json.loads(summary_path.read_text())
    if s.get("status") != "ONE_TIME_FROZEN_V2_MARKET_STATE_EVIDENCE_COMPLETE":
        raise ValidationError("unexpected V2 status")
    if s.get("raw_candidate_parity_fraction") != 1.0:
        raise ValidationError("raw candidate parity not exact")
    if s.get("atom_parity_fraction") != 1.0:
        raise ValidationError("atom parity not exact")
    if s.get("normalization_parity") is not True or s.get("normalization_count_parity") is not True:
        raise ValidationError("normalization parity failed")
    if s.get("pre_first_flat_state_parity_fraction") != 1.0:
        raise ValidationError("pre-first-FLAT state parity not exact")
    if s.get("false_flat_reproduced") is not True:
        raise ValidationError("false FLAT evidence missing")
    if s.get("profile_selected") is not False:
        raise ValidationError("profile selection forbidden in V2 architecture run")
    if s.get("p5_4_mapping_selected") is not False:
        raise ValidationError("P5.4 mapping selection forbidden")
    if s.get("risk_permission_unlock_authorized") is not False:
        raise ValidationError("market state cannot unlock risk permission")
    if s.get("production_authorized") is not False:
        raise ValidationError("production authorization forbidden")

    artifacts = s.get("artifact_sha256", {})
    required = {
        "daily_market_state_paths.csv",
        "normalized_percentiles.csv",
        "normalization_counts.csv",
        "profile_summary.csv",
        "flat_episodes.csv",
        "event_state_occupancy.csv",
        "event_state_first_occurrence.csv",
        "v1_v2_parity_summary.json",
    }
    if set(artifacts) != required:
        raise ValidationError("unexpected artifact set")
    for name, digest in artifacts.items():
        path = RESULT / name
        if not path.exists() or sha256(path) != digest:
            raise ValidationError(f"artifact digest mismatch: {name}")

    print(f"P5.3 V2 immutable validation PASS sha256={actual} architecture_pass={s.get('architecture_pass')}")
    return actual


if __name__ == "__main__":
    validate()
