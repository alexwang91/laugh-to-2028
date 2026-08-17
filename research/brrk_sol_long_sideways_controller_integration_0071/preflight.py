from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

RID = "BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071"
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESULT_BRANCH = "research/0071-result-v1"
RUNTIME = ("RUN_ATTEMPT.marker", "PRIMARY_RESULT.json", "EVIDENCE.json", "EXECUTION.json", "RUN_ONCE.marker")
PINNED = {
    "research/brrk_sol_long_sideways_controller_integration_0071/PREREGISTRATION.json": "f7810fcf1db723c0b84c71a5d74d4f74573c3830",
    "research/brrk_sol_long_sideways_controller_integration_0071/IMPLEMENTATION_CONTRACT.json": "f20564293dce526546e119681c7eba4e261da3d3",
    "research/brrk_sol_long_sideways_controller_integration_0071/engine.py": "26cac1ecd2e93b6954bed23737e8416893376c4d",
    "research/brrk_sol_long_sideways_controller_integration_0071/QUALIFICATION_RESULT.json": "9a782797b32430e36fd20316f5aa3030fa04e72d",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/PRIMARY_RESULT.json": "df00901c77d8d334d61c7c65a14b8d127e9ca8b6",
    "research/brrk_btc_sol_path_event_early_warning_execution_assured_0069/EVIDENCE.json": "6266e6a11205e21592766546342ca5bca1dd97f0",
    "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json": "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--boundary-sha", required=True)
    args = p.parse_args()
    head = git("rev-parse", "HEAD")
    if head != args.boundary_sha:
        raise SystemExit(f"FAIL exact merged-boundary mismatch: {head} != {args.boundary_sha}")
    bad = []
    for path, expected in PINNED.items():
        actual = git("rev-parse", f"HEAD:{path}")
        if actual != expected:
            bad.append({"path": path, "expected": expected, "actual": actual})
    if bad:
        raise SystemExit(f"FAIL pinned identity mismatch: {bad}")
    existing = [name for name in RUNTIME if (HERE / name).exists()]
    if existing:
        raise SystemExit(f"FAIL zero-result state violated: {existing}")
    remote_heads = git("ls-remote", "--heads", "origin", RESULT_BRANCH)
    if remote_heads:
        raise SystemExit(f"FAIL result branch already exists: {RESULT_BRANCH}")
    out = {
        "research_id": RID,
        "status": "PREFLIGHT_PASS_ZERO_RESULT_GIT_IDENTITY_ONLY",
        "boundary_sha": head,
        "controlled_reads": {"0069_PRIMARY_RESULT": 0, "0069_EVIDENCE": 0, "MARKET_EVIDENCE": 0, "DTB3": 0, "0070_RESULT_CONTENT": 0},
        "controlled_calls": {"market_loader": 0, "frozen_P02_prediction_reconstruction": 0, "cash_engine": 0, "network_fetch": 0},
        "controlled_attempt_consumed": 0,
        "runtime_artifacts_present": [],
        "result_branch_present": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
