from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from research.governance.controlled_research_runner_v1 import (
    EngineContext,
    InMemoryCreateOnlyStore,
    ManifestEntry,
    RunSpec,
    SourceManifest,
)
from research.governance.controlled_research_runner_v1_source_interface import (
    ControlledResearchRunnerV1SourceQualified,
    require_prefix,
)

HEAD = "b" * 40
RUNTIME_KEY = "payloads/data__futures__um__monthly__klines__BTCUSDT__1d__BTCUSDT-1d-2021-01.zip"


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def make_fixture(root: Path) -> tuple[SourceManifest, RunSpec]:
    payload = b"synthetic-nonhistorical-kline-fixture"
    archive = root / "source.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr(RUNTIME_KEY, payload)
    manifest = SourceManifest(
        manifest_id="SYNTHETIC-SOURCE-KEY-INTERFACE",
        source_id="SYNTHETIC-SOURCE",
        decision_timestamp="2026-08-25T00:00:00Z",
        archive_identity="synthetic-source.zip",
        entries=(ManifestEntry(RUNTIME_KEY, len(payload), digest(payload)),),
    )
    spec = RunSpec(
        research_id="SYNTHETIC-SOURCE-KEY-QUALIFICATION",
        attempt_id="A1",
        expected_head_sha=HEAD,
        actual_head_sha=HEAD,
        expected_source_id="SYNTHETIC-SOURCE",
        manifest=manifest,
        archive_path=archive,
        result_key="results/A1.json",
        marker_key="markers/A1/RUN_ATTEMPT.marker",
        run_once_key="markers/A1/RUN_ONCE.marker",
    )
    return manifest, spec


class PayloadPrefixEngine:
    def validate_source_keys(self, source_keys):
        require_prefix("payloads/", source_keys)

    def execute(self, context: EngineContext):
        return {"status": "PASS_SYNTHETIC", "keys": sorted(context.sources)}


class StagePrefixEngine:
    """Models the exact namespace assumption that invalidated 0085."""

    def validate_source_keys(self, source_keys):
        require_prefix("stage/payloads/", source_keys)

    def execute(self, context: EngineContext):
        raise AssertionError("must never execute when source-key qualification fails")


class MissingValidatorEngine:
    def execute(self, context: EngineContext):
        return {"status": "SHOULD_NOT_RUN"}


class ControlledRunnerSourceInterfaceQualification(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_0085_namespace_regression_rejects_before_marker_and_reads(self):
        _, spec = make_fixture(self.root)
        store = InMemoryCreateOnlyStore()
        report = ControlledResearchRunnerV1SourceQualified(store).run(spec, StagePrefixEngine())
        self.assertTrue(report.classification.startswith("PRECHECK_REJECTED:EXECUTION_INTERFACE_MISMATCH:"))
        self.assertIn("expected_prefix=stage/payloads/", report.classification)
        self.assertFalse(report.attempt_consumed)
        self.assertFalse(report.marker_created)
        self.assertEqual(report.source_reads, 0)
        self.assertEqual(report.engine_invocations, 0)
        self.assertFalse(store.exists(spec.marker_key))
        self.assertFalse(store.exists(spec.result_key))
        self.assertFalse(store.exists(spec.run_once_key))

    def test_missing_source_key_validator_is_wrong_execution_interface_pre_marker(self):
        _, spec = make_fixture(self.root)
        report = ControlledResearchRunnerV1SourceQualified(InMemoryCreateOnlyStore()).run(
            spec, MissingValidatorEngine()
        )
        self.assertEqual(
            report.classification,
            "PRECHECK_REJECTED:WRONG_EXECUTION_INTERFACE:MISSING_VALIDATE_SOURCE_KEYS",
        )
        self.assertFalse(report.marker_created)
        self.assertEqual(report.source_reads, 0)
        self.assertEqual(report.engine_invocations, 0)

    def test_exact_runtime_payload_namespace_passes_full_lifecycle(self):
        _, spec = make_fixture(self.root)
        report = ControlledResearchRunnerV1SourceQualified(InMemoryCreateOnlyStore()).run(
            spec, PayloadPrefixEngine()
        )
        self.assertEqual(report.classification, "EXECUTION_VALID")
        self.assertTrue(report.attempt_consumed)
        self.assertTrue(report.marker_created)
        self.assertEqual(report.source_reads, 1)
        self.assertEqual(report.engine_invocations, 1)
        self.assertTrue(report.scientific_result_admissible)

    def test_twenty_consecutive_source_qualified_full_lifecycles(self):
        manifest, base = make_fixture(self.root)
        store = InMemoryCreateOnlyStore()
        runner = ControlledResearchRunnerV1SourceQualified(store)
        reports = []
        for index in range(20):
            attempt = f"SOURCE-QUAL-{index:02d}"
            spec = RunSpec(
                research_id=base.research_id,
                attempt_id=attempt,
                expected_head_sha=HEAD,
                actual_head_sha=HEAD,
                expected_source_id=base.expected_source_id,
                manifest=manifest,
                archive_path=base.archive_path,
                result_key=f"results/{attempt}.json",
                marker_key=f"markers/{attempt}/RUN_ATTEMPT.marker",
                run_once_key=f"markers/{attempt}/RUN_ONCE.marker",
            )
            reports.append(runner.run(spec, PayloadPrefixEngine()))
        self.assertEqual(len(reports), 20)
        self.assertTrue(all(r.classification == "EXECUTION_VALID" for r in reports))
        self.assertTrue(all(r.source_reads == 1 for r in reports))
        self.assertTrue(all(r.engine_invocations == 1 for r in reports))
        self.assertTrue(all(r.marker_created and r.result_created and r.run_once_created for r in reports))
        self.assertTrue(all(r.scientific_result_admissible for r in reports))


if __name__ == "__main__":
    unittest.main()
