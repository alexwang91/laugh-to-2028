from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import run_p5_5_joint_validation as base

ROOT = Path(__file__).resolve().parents[2]
R2_PATH = ROOT / "research" / "cycle_exit" / "p5_5_validation_contract_r2.json"
P52_SUMMARY = ROOT / "research" / "results" / "p5_2_feature_evidence" / "summary.json"
V2_PROFILE = ROOT / "research" / "results" / "p5_3_v2_market_state" / "profile_summary.csv"
EXPECTED_R2_BLOB = "57073e6948e0c7540c453f193a1be7c21979b7d5"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_r2() -> dict:
    if git_blob_sha(R2_PATH) != EXPECTED_R2_BLOB:
        raise RuntimeError("P5.5 R2 hash drift")
    r2 = json.loads(R2_PATH.read_text())
    if r2["status"] != "FROZEN_BEFORE_ANY_P5_5_CANDIDATE_ECONOMICS":
        raise RuntimeError("P5.5 R2 not frozen")
    if r2["result_observed_before_amendment"] is not False:
        raise RuntimeError("P5.5 R2 was not pre-result")
    p52 = json.loads(P52_SUMMARY.read_text())
    if p52["data_window"][1] != r2["coverage_evidence"]["p5_2_data_window_end"]:
        raise RuntimeError("P5.2 coverage evidence drift")
    profiles = V2_PROFILE.read_text().splitlines()[1:]
    if not profiles or any(",1869," not in row for row in profiles):
        raise RuntimeError("P5.3 V2 classified-day coverage drift")
    return r2


def main() -> None:
    r2 = load_r2()
    original_load = base.load_contracts

    def corrected_load_contracts():
        contract, r1, p54 = original_load()
        contract = copy.deepcopy(contract)
        contract["evaluation_layers"]["authoritative_brrk_economics"]["evaluation_session_end"] = r2["replacement_semantics"]["authoritative_brrk_economics_end"]
        return contract, r1, p54

    base.load_contracts = corrected_load_contracts
    base.main()

    result = base.RESULT_DIR
    manifest_path = result / "input_manifest.json"
    summary_path = result / "summary.json"
    digest_path = result / "summary.sha256"
    manifest = json.loads(manifest_path.read_text())
    manifest["p5_5_r2_git_blob_sha"] = git_blob_sha(R2_PATH)
    manifest["common_observable_end_correction"] = {
        "effective_end": r2["replacement_semantics"]["authoritative_brrk_economics_end"],
        "rule": r2["replacement_semantics"]["common_observable_end_rule"],
        "forward_fill_market_state": False,
        "fabricated_state_extension": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n")

    summary = json.loads(summary_path.read_text())
    summary["p5_5_r2_applied"] = True
    summary["common_observable_end"] = r2["replacement_semantics"]["authoritative_brrk_economics_end"]
    summary["artifact_sha256"]["input_manifest.json"] = sha256_file(manifest_path)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    digest = sha256_file(summary_path)
    digest_path.write_text(digest + "\n")
    print(f"P5.5 R2 immutable summary_sha256={digest} common_observable_end={summary['common_observable_end']}")


if __name__ == "__main__":
    main()
