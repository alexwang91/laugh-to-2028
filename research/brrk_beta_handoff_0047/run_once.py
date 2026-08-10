from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from research.brrk_beta_handoff_0047.engine import (
    ASSETS,
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    DATASET_SLICE_ID,
    FROZEN_END,
    RESEARCH_ID,
    build_market_evidence_payload,
    evaluate_frozen_protocol,
    fetch_daily_frame,
    frames_from_market_evidence,
)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _write_create_only(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception as exc:  # pragma: no cover - execution environment failure
        raise RuntimeError(f"Could not bind execution to git HEAD: {exc}") from exc


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_data(output: Path) -> None:
    if output.exists():
        raise RuntimeError(f"Create-only market evidence already exists: {output}")
    frames = {asset: fetch_daily_frame(asset) for asset in ASSETS}
    evidence = build_market_evidence_payload(frames)
    _write_create_only(output, evidence)
    print(
        "BRRK_0047_MARKET_EVIDENCE="
        + json.dumps(
            {
                "path": str(output),
                "payload_sha256": evidence["payload_sha256"],
                "common_start": evidence["payload"]["common_start"],
                "common_end": evidence["payload"]["common_end"],
                "assets": evidence["payload"]["assets"],
            },
            sort_keys=True,
        )
    )


def evaluate(market: Path, output: Path, execution: Path, marker: Path, expected_head_sha: str | None) -> None:
    for path in (output, execution, marker):
        if path.exists():
            raise RuntimeError(f"Exactly-once output already exists: {path}")
    head = _git_head()
    if expected_head_sha is not None and head != expected_head_sha:
        raise RuntimeError(f"Git HEAD mismatch: expected {expected_head_sha}, got {head}")
    evidence = _load_json(market)
    frames = frames_from_market_evidence(evidence)
    market_sha = evidence["payload_sha256"]

    result = evaluate_frozen_protocol(frames, market_sha)
    result_sha = _sha256(result)
    _write_create_only(output, result)

    execution_record = {
        "research_id": RESEARCH_ID,
        "dataset_slice_id": DATASET_SLICE_ID,
        "git_head_sha": head,
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "market_evidence_path": str(market),
        "market_payload_sha256": market_sha,
        "primary_result_path": str(output),
        "primary_result_sha256": result_sha,
        "frozen_history_end": FROZEN_END.strftime("%Y-%m-%d"),
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "actual_variants_evaluated": 1,
        "result_status": result["classification"]["result_status"],
        "portfolio_economics_executed": False,
        "duration_aware_handoff_model_fitted": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    execution_sha = _sha256(execution_record)
    _write_create_only(execution, execution_record)

    marker_record = {
        "research_id": RESEARCH_ID,
        "status": "VALID_EXECUTION_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        "git_head_sha": head,
        "market_payload_sha256": market_sha,
        "primary_result_sha256": result_sha,
        "execution_sha256": execution_sha,
        "result_status": result["classification"]["result_status"],
        "same_id_rerun_allowed": False,
        "same_id_retuning_allowed": False,
        "same_id_rescue_allowed": False,
    }
    _write_create_only(marker, marker_record)
    print(
        "BRRK_0047_RESULT="
        + json.dumps(
            {
                "result_status": result["classification"]["result_status"],
                "market_payload_sha256": market_sha,
                "primary_result_sha256": result_sha,
                "execution_sha256": execution_sha,
                "git_head_sha": head,
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Frozen run-once interface for BRRK Beta Handoff 0047")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-data")
    prepare.add_argument("--output", required=True, type=Path)

    run = subparsers.add_parser("evaluate")
    run.add_argument("--market", required=True, type=Path)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--execution", required=True, type=Path)
    run.add_argument("--marker", required=True, type=Path)
    run.add_argument("--expected-head-sha", default=None)

    args = parser.parse_args()
    if args.command == "prepare-data":
        prepare_data(args.output)
    elif args.command == "evaluate":
        evaluate(args.market, args.output, args.execution, args.marker, args.expected_head_sha)
    else:  # pragma: no cover
        raise RuntimeError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
