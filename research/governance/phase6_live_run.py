from __future__ import annotations

"""CLI entrypoint that applies source-boundary normalization then delegates to
`phase6_live_collector` without changing the frozen canonical data contract.
"""

import argparse
import json
from pathlib import Path

from . import phase6_live_collector as collector
from .phase6_live_source_adapters import canonicalize_hyperliquid_funding_history


# Bind only the external Hyperliquid source adapter. Raw bytes have already been
# preserved by RawCapture before this function is called.
collector.canonicalize_funding_history = canonicalize_hyperliquid_funding_history


def collect_live(**kwargs: object) -> dict[str, object]:
    return collector.collect(**kwargs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Phase-6 live collector with source adapters")
    sub = parser.add_subparsers(dest="command", required=True)

    collect_parser = sub.add_parser("collect")
    collect_parser.add_argument("--output-dir", type=Path, required=True)
    collect_parser.add_argument("--event-name", required=True)
    collect_parser.add_argument("--run-id", required=True)
    collect_parser.add_argument("--run-attempt", required=True)
    collect_parser.add_argument("--workflow-sha", required=True)
    collect_parser.add_argument("--emergency-drill", action="store_true")

    args = parser.parse_args(argv)
    try:
        metadata = collect_live(
            output_dir=args.output_dir,
            event_name=args.event_name,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            workflow_sha=args.workflow_sha,
            emergency_drill=args.emergency_drill,
        )
    except Exception as exc:
        collector._write_failure(args.output_dir / "collector_failure.json", exc)
        print(f"Phase-6 live collector: FAIL_CLOSED ({type(exc).__name__}: {exc})")
        return 1
    print(json.dumps(metadata, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
