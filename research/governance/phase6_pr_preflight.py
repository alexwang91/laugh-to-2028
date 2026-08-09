from __future__ import annotations

"""PR-only wrapper for a real, non-crediting Phase-6 live preflight.

The canonical collector deliberately accepts only schedule/workflow_dispatch.
Pull-request execution therefore enters through this wrapper, which uses the
workflow-dispatch collector path solely to exercise the identical read-only
external-data chain and then rewrites the diagnostic metadata to the truthful
pull_request/preflight identity. No receipt is created and no scheduled-decision
or emergency-drill credit can be produced by this wrapper.
"""

import argparse
import json
from pathlib import Path

from .phase6_live_collector import collect


def _write_context(output_dir: Path, *, status: str, error: Exception | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "actual_event_name": "pull_request",
        "status": status,
        "preflight_only": True,
        "scheduled_decision_credit_candidate": False,
        "emergency_drill_candidate": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
    if error is not None:
        payload["error_type"] = type(error).__name__
        payload["error"] = str(error)
    (output_dir / "preflight_context.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def run_preflight(
    *,
    output_dir: Path,
    run_id: str,
    run_attempt: str,
    workflow_sha: str,
) -> dict[str, object]:
    _write_context(output_dir, status="RUNNING")
    metadata = collect(
        output_dir=output_dir,
        event_name="workflow_dispatch",
        run_id=run_id,
        run_attempt=run_attempt,
        workflow_sha=workflow_sha,
        emergency_drill=False,
    )
    metadata.update(
        {
            "event_name": "pull_request",
            "preflight_only": True,
            "scheduled_decision_credit_candidate": False,
            "emergency_drill_candidate": False,
            "pull_request_preflight": True,
            "credit_forbidden_reason": "PULL_REQUEST_IS_NOT_A_GENUINE_SCHEDULED_DECISION",
        }
    )
    path = output_dir / "evidence_metadata.json"
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_context(output_dir, status="PASS")
    return metadata


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run non-crediting Phase-6 PR live preflight")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--workflow-sha", required=True)
    args = parser.parse_args(argv)
    try:
        metadata = run_preflight(
            output_dir=args.output_dir,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            workflow_sha=args.workflow_sha,
        )
    except Exception as exc:
        _write_context(args.output_dir, status="FAIL_CLOSED", error=exc)
        print(f"Phase-6 PR live preflight: FAIL_CLOSED ({type(exc).__name__}: {exc})")
        return 1
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
