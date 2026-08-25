from __future__ import annotations

"""Prospective source-key qualification for CONTROLLED_RESEARCH_RUNNER_V1.

0085 proved that checking only for a callable ``execute`` method is insufficient:
the runner can present a frozen manifest key namespace that the configured engine
cannot parse.  This module strengthens the common runner prospectively without
changing any already-consumed attempt or historical result.

The added check is metadata-only.  It passes only the exact manifest filenames
that the runner will later expose as ``EngineContext.sources`` keys.  It never
opens, reads, decompresses, hashes, or CRC-scans controlled payload bytes.
"""

from typing import Any, Protocol, Sequence

from research.governance.controlled_research_runner_v1 import (
    ControlledEngine,
    ControlledResearchRunnerV1,
    PayloadArchive,
    PreflightRejected,
    RunSpec,
)


class SourceKeyQualifiedEngine(ControlledEngine, Protocol):
    def validate_source_keys(self, source_keys: Sequence[str]) -> None: ...


class ControlledResearchRunnerV1SourceQualified(ControlledResearchRunnerV1):
    """V1 runner with mandatory pre-marker engine/source-key compatibility."""

    def _preflight(self, spec: RunSpec, engine: ControlledEngine, archive: PayloadArchive) -> None:
        super()._preflight(spec, engine, archive)
        validator = getattr(engine, "validate_source_keys", None)
        if not callable(validator):
            raise PreflightRejected("WRONG_EXECUTION_INTERFACE:MISSING_VALIDATE_SOURCE_KEYS")

        # These are exactly the keys read_verified_payloads() will use after the
        # durable marker.  They come from frozen manifest metadata only.
        runtime_source_keys = tuple(entry.filename for entry in spec.manifest.entries)
        try:
            outcome = validator(runtime_source_keys)
        except PreflightRejected:
            raise
        except Exception as exc:
            raise PreflightRejected(
                f"EXECUTION_INTERFACE_MISMATCH:{type(exc).__name__}:{exc}"
            ) from exc
        if outcome is not None:
            raise PreflightRejected("EXECUTION_INTERFACE_MISMATCH:VALIDATOR_MUST_RETURN_NONE")


def require_prefix(prefix: str, source_keys: Sequence[str]) -> None:
    """Small synthetic/nonhistorical helper for adapter qualification tests."""
    if not prefix:
        raise ValueError("prefix must be non-empty")
    bad = [key for key in source_keys if not key.startswith(prefix)]
    if bad:
        raise ValueError(f"SOURCE_KEY_NAMESPACE_MISMATCH expected_prefix={prefix} first={bad[0]}")
