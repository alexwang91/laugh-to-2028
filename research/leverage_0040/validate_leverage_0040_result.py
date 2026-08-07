from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research" / "results" / "leverage_0040"
LEVERAGE = ROOT / "research" / "leverage_0040"
SUMMARY = RESULT / "summary.json"
DIGEST = RESULT / "summary.sha256"
CONTRACT = LEVERAGE / "LEVERAGE-0040-STUDY-IMPLEMENTATION-V1.json"
PREREG = LEVERAGE / "LEVERAGE-0040.json"
ADDENDUM = LEVERAGE / "LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json"
R2_CORRECTION = LEVERAGE / "LEVERAGE-0040-PRE-RESULT-CORRECTION-R2.json"
R3_CORRECTION = LEVERAGE / "LEVERAGE-0040-PRE-RESULT-CORRECTION-R3.json"
R4_CORRECTION = LEVERAGE / "LEVERAGE-0040-BLINDED-RUN-CORRECTION-R4.json"
R5_CORRECTION = LEVERAGE / "LEVERAGE-0040-POST-COMPUTE-CORRECTION-R5.json"
CAPS = ("1.00", "1.10", "1.20", "1.30")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not SUMMARY.exists() or not DIGEST.exists():
        raise SystemExit("LEVERAGE-0040 immutable result files are missing")
    expected = DIGEST.read_text().strip()
    actual = sha256(SUMMARY)
    if expected != actual:
        raise SystemExit("summary digest mismatch")

    data = json.loads(SUMMARY.read_text())
    if (
        data.get("study_id") != "LEVERAGE-0040"
        or data.get("status") != "ONE_TIME_PREREGISTERED_STUDY_COMPLETE"
    ):
        raise SystemExit("result identity/status mismatch")

    # These are native JSON booleans by contract, not integer lookalikes.
    if (
        data.get("production_authorized") is not False
        or data.get("constraints", {}).get("production_authorized_components") != []
        or data.get("constraints", {}).get("post_result_retuning_allowed") is not False
    ):
        raise SystemExit("production/retuning boundary violated")

    matrix = data.get("candidate_matrix")
    if not isinstance(matrix, dict) or tuple(sorted(matrix)) != CAPS:
        raise SystemExit("candidate matrix mismatch")

    ev = data.get("input_evidence", {})
    if (
        ev.get("implementation_contract_sha256") != sha256(CONTRACT)
        or ev.get("preregistration_sha256") != sha256(PREREG)
        or ev.get("pre_run_addendum_sha256") != sha256(ADDENDUM)
    ):
        raise SystemExit("frozen input digest mismatch")

    authority = ev.get("raw_target_authority")
    if not isinstance(authority, dict):
        raise SystemExit("raw target authority evidence missing")
    if authority.get("feature_assets") != ["BTC", "ETH", "SOL", "BNB", "XRP"]:
        raise SystemExit("feature universe mismatch")
    if authority.get("target_assets") != ["BTC", "ETH", "SOL", "BNB"]:
        raise SystemExit("target universe mismatch")
    if authority.get("first_decision_date") != "2022-12-09":
        raise SystemExit("first decision date mismatch")
    if authority.get("evaluation_start_session") != "2022-12-10":
        raise SystemExit("evaluation session start mismatch")
    if authority.get("published_banded_weights_used_for_scale") is not False:
        raise SystemExit("banded holdings were incorrectly used as scale authority")

    if ev.get("runner_entrypoint") != "research/leverage_0040/run_leverage_0040_once_r5.py":
        raise SystemExit("R5 runner entrypoint evidence missing")
    if ev.get("preflight_corrections") != [
        "PREFLIGHT-RAW-TARGET-001",
        "PREFLIGHT-SESSION-TIMING-002",
        "PREFLIGHT-GAP-CROSS-EQUITY-003",
        "PREFLIGHT-LIQUIDATION-START-004",
    ]:
        raise SystemExit("preflight correction evidence mismatch")
    if ev.get("blinded_post_start_corrections") != ["BLINDED-FUNDING-SESSION-005"]:
        raise SystemExit("blinded post-start correction evidence mismatch")
    if ev.get("post_compute_corrections") != [
        "POST-COMPUTE-SERIALIZATION-VALIDATOR-006"
    ]:
        raise SystemExit("post-compute correction evidence mismatch")
    if ev.get("r2_correction_sha256") != sha256(R2_CORRECTION):
        raise SystemExit("R2 correction digest mismatch")
    if ev.get("r3_correction_sha256") != sha256(R3_CORRECTION):
        raise SystemExit("R3 correction digest mismatch")
    if ev.get("r4_correction_sha256") != sha256(R4_CORRECTION):
        raise SystemExit("R4 correction digest mismatch")
    if ev.get("r5_correction_sha256") != sha256(R5_CORRECTION):
        raise SystemExit("R5 correction digest mismatch")

    provenance = data.get("execution_provenance", {})
    r4 = provenance.get("r4_blinded_recovery", {})
    if (
        r4.get("cap_gt_1_partial_computation_occurred") is not True
        or r4.get("candidate_metrics_emitted_before_failure") is not False
        or r4.get("candidate_metrics_committed_before_failure") is not False
        or r4.get("result_driven_retuning") is not False
    ):
        raise SystemExit("R4 blinded provenance mismatch")
    r5 = provenance.get("r5_post_compute_recovery", {})
    if (
        r5.get("full_candidate_matrix_computed_before_validator_failure") is not True
        or r5.get("candidate_metrics_emitted_before_failure") is not False
        or r5.get("candidate_metrics_committed_before_failure") is not False
        or r5.get("economic_logic_changed") is not False
        or r5.get("result_driven_retuning") is not False
    ):
        raise SystemExit("R5 post-compute provenance mismatch")

    for cap in CAPS:
        row = matrix[cap]
        if float(row.get("cap")) != float(cap):
            raise SystemExit(f"cap mismatch {cap}")
        if set(row.get("price_only_metrics_by_cost_bps", {})) != {
            "5.0",
            "10.0",
            "20.0",
            "50.0",
        }:
            raise SystemExit(f"cost grid mismatch {cap}")
        if cap != "1.00" and not {
            "final_research_pass",
            "broad_region_pass",
        }.issubset(row.get("gate", {})):
            raise SystemExit(f"gate bookkeeping missing {cap}")

    selection = data.get("selection", {})
    status = selection.get("status")
    if (
        status
        not in {"NO_PROMOTION", "RESEARCH_PROMOTION_CANDIDATE_NOT_PRODUCTION_AUTHORIZED"}
        or selection.get("production_authorized") is not False
    ):
        raise SystemExit("selection status invalid")
    if status == "NO_PROMOTION" and selection.get("selected_research_cap") is not None:
        raise SystemExit("NO_PROMOTION selected cap")
    if status != "NO_PROMOTION":
        selected = f"{float(selection['selected_research_cap']):.2f}"
        if (
            selected not in {"1.10", "1.20", "1.30"}
            or matrix[selected]["gate"].get("final_research_pass") is not True
        ):
            raise SystemExit("selected cap failed frozen gate")

    print(f"LEVERAGE-0040 immutable result validation PASS sha256={actual}")


if __name__ == "__main__":
    main()
