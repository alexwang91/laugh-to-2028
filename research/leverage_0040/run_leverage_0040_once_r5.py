from __future__ import annotations

"""R5 post-compute serialization/validator recovery for LEVERAGE-0040.

Run 31200299149 completed the full preregistered economic study but the result
validator rejected the generated JSON before commit.  The root cause is purely
serialization: Python bool is a subclass of int, while the base _json_safe
checked integer types before bool types, converting False/True into JSON 0/1.
The validator intentionally uses identity checks (`is False` / `is True`) for
production and retuning boundaries, so it correctly refused the malformed
serialization.

R5 changes no economic calculation. It restores native JSON booleans and adds
explicit provenance for this post-compute blinded recovery. The entire study is
recomputed deterministically with the same frozen inputs, seeds, caps, costs,
stresses and selection rules because the failed runner did not commit artifacts.
"""

import hashlib
import json
from pathlib import Path

import run_leverage_0040_once_r4 as r4

base = r4.base

CORRECTION_PATH = Path(__file__).with_name(
    "LEVERAGE-0040-POST-COMPUTE-CORRECTION-R5.json"
)


def _json_safe_r5(value):
    if isinstance(value, dict):
        return {str(k): _json_safe_r5(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_r5(v) for v in value]
    if isinstance(value, (base.pd.Timestamp, base.np.datetime64)):
        return base.pd.Timestamp(value).isoformat()
    # bool must precede int because bool is a subclass of int in Python.
    if isinstance(value, (base.np.bool_, bool)):
        return bool(value)
    if isinstance(value, (base.np.integer, int)):
        return int(value)
    if isinstance(value, (base.np.floating, float)):
        x = float(value)
        return None if base.math.isnan(x) or base.math.isinf(x) else x
    return value


def _augment_r5_evidence() -> None:
    summary = base.RESULT_DIR / "summary.json"
    digest_file = base.RESULT_DIR / "summary.sha256"
    if not summary.exists():
        return
    payload = json.loads(summary.read_text(encoding="utf-8"))
    evidence = payload.setdefault("input_evidence", {})
    evidence["runner_entrypoint"] = (
        "research/leverage_0040/run_leverage_0040_once_r5.py"
    )
    evidence["r5_correction_sha256"] = hashlib.sha256(
        CORRECTION_PATH.read_bytes()
    ).hexdigest()
    corrections = list(evidence.get("post_compute_corrections", []))
    if "POST-COMPUTE-SERIALIZATION-VALIDATOR-006" not in corrections:
        corrections.append("POST-COMPUTE-SERIALIZATION-VALIDATOR-006")
    evidence["post_compute_corrections"] = corrections

    provenance = payload.setdefault("execution_provenance", {})
    provenance["r5_post_compute_recovery"] = {
        "failed_run_id": 31200299149,
        "failed_head": "4cb336ef9d61c0230fd16b9dc29877a17ec2bb5a",
        "full_candidate_matrix_computed_before_validator_failure": True,
        "candidate_metrics_emitted_before_failure": False,
        "candidate_metrics_committed_before_failure": False,
        "failed_validator_message": "production/retuning boundary violated",
        "economic_logic_changed": False,
        "result_driven_retuning": False,
    }

    summary.write_text(
        json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    digest = hashlib.sha256(summary.read_bytes()).hexdigest()
    digest_file.write_text(digest + "\n", encoding="utf-8")
    print(f"LEVERAGE-0040 R5 immutable summary_sha256={digest}")


def main() -> None:
    base._json_safe = _json_safe_r5
    r4.main()
    _augment_r5_evidence()


if __name__ == "__main__":
    main()
