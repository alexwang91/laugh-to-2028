from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import urllib.request
import warnings
import zipfile

from research.governance.controlled_research_runner_v1 import (
    ControlledResearchRunnerV1,
    DoubleEngineInvocation,
    EngineContext,
    EngineInvocationGuard,
    InMemoryCreateOnlyStore,
    ManifestEntry,
    PayloadArchive,
    PreflightRejected,
    RunSpec,
    SourceManifest,
)

HEAD = "a" * 40


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_zip(path: Path, rows: list[tuple[str, bytes]]) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as zf:
            for name, payload in rows:
                zf.writestr(name, payload)


def manifest_for(rows: list[tuple[str, bytes]], *, source_id: str = "SRC-1") -> SourceManifest:
    return SourceManifest(
        manifest_id="MANIFEST-1",
        source_id=source_id,
        decision_timestamp="2026-08-25T00:00:00Z",
        archive_identity="synthetic-source.zip",
        entries=tuple(ManifestEntry(filename=name, size=len(payload), sha256=sha(payload)) for name, payload in rows),
    )


def spec_for(root: Path, manifest: SourceManifest, *, attempt: str = "A1", expected_source: str = "SRC-1") -> RunSpec:
    return RunSpec(
        research_id="SYNTHETIC-RUNNER-QUALIFICATION",
        attempt_id=attempt,
        expected_head_sha=HEAD,
        actual_head_sha=HEAD,
        expected_source_id=expected_source,
        manifest=manifest,
        archive_path=root / "source.zip",
        result_key=f"results/{attempt}.json",
        marker_key=f"markers/{attempt}/RUN_ATTEMPT.marker",
        run_once_key=f"markers/{attempt}/RUN_ONCE.marker",
    )


class GoodEngine:
    def execute(self, context: EngineContext):
        return {
            "status": "PASS_SYNTHETIC",
            "bytes": sum(len(value) for value in context.sources.values()),
            "source_names": sorted(context.sources),
        }


class MarkerAwareEngine:
    def __init__(self, store: InMemoryCreateOnlyStore, marker_key: str) -> None:
        self.store = store
        self.marker_key = marker_key

    def execute(self, context: EngineContext):
        if not self.store.exists(self.marker_key):
            raise AssertionError("engine invoked before durable marker")
        return {"status": "PASS_SYNTHETIC", "source_count": len(context.sources)}


class CrashEngine:
    def execute(self, context: EngineContext):
        raise RuntimeError("synthetic crash after marker")


class NaNEngine:
    def execute(self, context: EngineContext):
        return {"status": "BAD", "metric": float("nan")}


class NetworkEngine:
    def execute(self, context: EngineContext):
        urllib.request.urlopen("https://example.invalid", timeout=1)
        return {"status": "SHOULD_NOT_REACH"}


class CountingEngine:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, context: EngineContext):
        self.calls += 1
        return {"status": "PASS", "calls": self.calls}


class SelectiveFailureStore(InMemoryCreateOnlyStore):
    def __init__(self, fail_key: str) -> None:
        super().__init__()
        self.fail_key = fail_key

    def create_only(self, key: str, payload: bytes) -> None:
        if key == self.fail_key:
            raise OSError("synthetic writer failure")
        super().create_only(key, payload)


class ControlledResearchRunnerV1Qualification(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.rows = [("alpha.bin", b"alpha"), ("beta.bin", b"beta")]
        write_zip(self.root / "source.zip", self.rows)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_good(self, *, attempt: str = "A1", store=None, engine=None, manifest=None, spec=None):
        manifest = manifest or manifest_for(self.rows)
        spec = spec or spec_for(self.root, manifest, attempt=attempt)
        store = store or InMemoryCreateOnlyStore()
        engine = engine or GoodEngine()
        report = ControlledResearchRunnerV1(store).run(spec, engine)
        return report, store, spec

    def test_happy_path_marker_before_read_exactly_once_and_create_only_chain(self):
        manifest = manifest_for(self.rows)
        spec = spec_for(self.root, manifest)
        store = InMemoryCreateOnlyStore()
        engine = MarkerAwareEngine(store, spec.marker_key)
        report = ControlledResearchRunnerV1(store).run(spec, engine)
        self.assertEqual(report.classification, "EXECUTION_VALID")
        self.assertTrue(report.attempt_consumed)
        self.assertTrue(report.marker_created)
        self.assertTrue(report.result_created)
        self.assertTrue(report.run_once_created)
        self.assertEqual(report.source_reads, 2)
        self.assertEqual(report.engine_invocations, 1)
        self.assertTrue(report.scientific_result_admissible)
        self.assertTrue(store.exists(spec.marker_key))
        self.assertTrue(store.exists(spec.result_key))
        self.assertTrue(store.exists(spec.run_once_key))

    def test_fault_corrupted_zip_crc_is_only_discovered_after_marker(self):
        path = self.root / "source.zip"
        raw = path.read_bytes()
        self.assertIn(b"alpha", raw)
        path.write_bytes(raw.replace(b"alpha", b"blpha", 1))
        report, store, spec = self.run_good()
        self.assertTrue(report.marker_created)
        self.assertTrue(report.attempt_consumed)
        self.assertFalse(report.scientific_result_admissible)
        self.assertIn("CORRUPTED_ZIP_OR_CRC", report.classification)
        self.assertTrue(store.exists(spec.result_key))
        self.assertTrue(store.exists(spec.run_once_key))

    def test_fault_missing_file_rejected_pre_marker(self):
        manifest = manifest_for(self.rows + [("missing.bin", b"missing")])
        report, _, _ = self.run_good(manifest=manifest)
        self.assertIn("ARCHIVE_FILE_SET_MISMATCH", report.classification)
        self.assertFalse(report.marker_created)
        self.assertEqual(report.source_reads, 0)

    def test_fault_wrong_hash_invalid_after_marker(self):
        manifest = SourceManifest(
            manifest_id="MANIFEST-1",
            source_id="SRC-1",
            decision_timestamp="2026-08-25T00:00:00Z",
            archive_identity="synthetic-source.zip",
            entries=(
                ManifestEntry("alpha.bin", 5, "0" * 64),
                ManifestEntry("beta.bin", 4, sha(b"beta")),
            ),
        )
        report, _, _ = self.run_good(manifest=manifest)
        self.assertTrue(report.marker_created)
        self.assertIn("PAYLOAD_HASH_MISMATCH", report.classification)

    def test_fault_duplicate_object_rejected_pre_marker(self):
        write_zip(self.root / "source.zip", [("alpha.bin", b"alpha"), ("alpha.bin", b"alpha")])
        manifest = SourceManifest(
            manifest_id="MANIFEST-1",
            source_id="SRC-1",
            decision_timestamp="2026-08-25T00:00:00Z",
            archive_identity="synthetic-source.zip",
            entries=(ManifestEntry("alpha.bin", 5, sha(b"alpha")),),
        )
        report, _, _ = self.run_good(manifest=manifest)
        self.assertEqual(report.classification, "PRECHECK_REJECTED:DUPLICATE_OBJECT")
        self.assertFalse(report.marker_created)

    def test_fault_stale_head_rejected_pre_marker(self):
        manifest = manifest_for(self.rows)
        spec = spec_for(self.root, manifest)
        spec = RunSpec(**{**spec.__dict__, "actual_head_sha": "b" * 40})
        report, _, _ = self.run_good(spec=spec)
        self.assertEqual(report.classification, "PRECHECK_REJECTED:STALE_HEAD")
        self.assertFalse(report.marker_created)

    def test_fault_existing_result_rejected_pre_marker(self):
        manifest = manifest_for(self.rows)
        spec = spec_for(self.root, manifest)
        store = InMemoryCreateOnlyStore()
        store.create_only(spec.result_key, b"existing")
        report, _, _ = self.run_good(store=store, spec=spec)
        self.assertEqual(report.classification, "PRECHECK_REJECTED:EXISTING_RESULT")
        self.assertFalse(report.marker_created)

    def test_fault_marker_push_failure_reads_nothing(self):
        manifest = manifest_for(self.rows)
        spec = spec_for(self.root, manifest)
        store = SelectiveFailureStore(spec.marker_key)
        report, _, _ = self.run_good(store=store, spec=spec)
        self.assertEqual(report.classification, "PRECHECK_REJECTED:MARKER_PUSH_FAILURE")
        self.assertFalse(report.attempt_consumed)
        self.assertEqual(report.source_reads, 0)
        self.assertEqual(report.engine_invocations, 0)

    def test_fault_crash_after_marker_is_sealed_invalid(self):
        report, store, spec = self.run_good(engine=CrashEngine())
        self.assertTrue(report.marker_created)
        self.assertTrue(report.attempt_consumed)
        self.assertIn("ENGINE_OR_RUNTIME_FAILURE:RuntimeError", report.classification)
        self.assertTrue(store.exists(spec.result_key))
        self.assertTrue(store.exists(spec.run_once_key))

    def test_fault_duplicate_read_guard_blocks_second_physical_payload_pass(self):
        archive = PayloadArchive(self.root / "source.zip", manifest_for(self.rows))
        archive.metadata_preflight()
        archive.read_verified_payloads()
        with self.assertRaisesRegex(Exception, "DUPLICATE_PAYLOAD_READ"):
            archive.read_verified_payloads()
        self.assertEqual(archive.read_count, 2)

    def test_fault_double_engine_invocation_guard_blocks_second_call(self):
        engine = CountingEngine()
        guard = EngineInvocationGuard(engine)
        context = EngineContext("R", "A", "2026-08-25T00:00:00Z", "M", "S", {})
        guard.invoke(context)
        with self.assertRaises(DoubleEngineInvocation):
            guard.invoke(context)
        self.assertEqual(engine.calls, 1)
        self.assertEqual(guard.invocations, 1)

    def test_fault_nan_result_is_invalid_and_sealed(self):
        report, store, spec = self.run_good(engine=NaNEngine())
        self.assertIn("NONFINITE_RESULT", report.classification)
        self.assertFalse(report.scientific_result_admissible)
        self.assertTrue(store.exists(spec.result_key))
        self.assertTrue(store.exists(spec.run_once_key))

    def test_fault_missing_timestamp_rejected_by_manifest_boundary(self):
        value = {
            "schema_version": 1,
            "manifest_id": "M",
            "source_id": "SRC-1",
            "decision_timestamp": None,
            "archive_identity": "x.zip",
            "entries": [{"filename": "alpha.bin", "size": 5, "sha256": sha(b"alpha")}],
        }
        with self.assertRaisesRegex(PreflightRejected, "MISSING_TIMESTAMP"):
            SourceManifest.from_mapping(value)

    def test_fault_schema_drift_rejected_by_manifest_boundary(self):
        value = {
            "schema_version": 2,
            "manifest_id": "M",
            "source_id": "SRC-1",
            "decision_timestamp": "2026-08-25T00:00:00Z",
            "archive_identity": "x.zip",
            "entries": [{"filename": "alpha.bin", "size": 5, "sha256": sha(b"alpha")}],
        }
        with self.assertRaisesRegex(PreflightRejected, "SCHEMA_DRIFT"):
            SourceManifest.from_mapping(value)

    def test_fault_writer_failure_consumes_attempt_but_never_admits_science(self):
        manifest = manifest_for(self.rows)
        spec = spec_for(self.root, manifest)
        store = SelectiveFailureStore(spec.result_key)
        report, _, _ = self.run_good(store=store, spec=spec)
        self.assertEqual(report.classification, "INVALID_EXECUTION_WRITER_FAILURE")
        self.assertTrue(report.attempt_consumed)
        self.assertTrue(report.marker_created)
        self.assertFalse(report.result_created)
        self.assertFalse(report.scientific_result_admissible)

    def test_fault_network_attempt_is_blocked_and_sealed_invalid(self):
        report, store, spec = self.run_good(engine=NetworkEngine())
        self.assertEqual(report.classification, "INVALID_EXECUTION_NETWORK_ATTEMPT")
        self.assertEqual(report.engine_invocations, 1)
        self.assertTrue(store.exists(spec.result_key))
        self.assertTrue(store.exists(spec.run_once_key))

    def test_fault_wrong_source_manifest_rejected_pre_marker(self):
        manifest = manifest_for(self.rows, source_id="WRONG-SOURCE")
        report, _, _ = self.run_good(manifest=manifest)
        self.assertEqual(report.classification, "PRECHECK_REJECTED:WRONG_SOURCE_MANIFEST")
        self.assertFalse(report.marker_created)

    def test_fault_wrong_execution_interface_rejected_pre_marker(self):
        report, _, _ = self.run_good(engine=object())
        self.assertEqual(report.classification, "PRECHECK_REJECTED:WRONG_EXECUTION_INTERFACE")
        self.assertFalse(report.marker_created)

    def test_exactly_once_second_attempt_same_identity_is_blocked(self):
        manifest = manifest_for(self.rows)
        spec = spec_for(self.root, manifest)
        store = InMemoryCreateOnlyStore()
        runner = ControlledResearchRunnerV1(store)
        first = runner.run(spec, GoodEngine())
        second = runner.run(spec, GoodEngine())
        self.assertEqual(first.classification, "EXECUTION_VALID")
        self.assertTrue(second.classification.startswith("PRECHECK_REJECTED:"))
        self.assertFalse(second.marker_created)
        self.assertEqual(second.source_reads, 0)
        self.assertEqual(second.engine_invocations, 0)

    def test_twenty_consecutive_synthetic_full_lifecycles_zero_unexpected_failure(self):
        manifest = manifest_for(self.rows)
        store = InMemoryCreateOnlyStore()
        runner = ControlledResearchRunnerV1(store)
        reports = []
        for index in range(20):
            attempt = f"SYNTH-{index:02d}"
            spec = spec_for(self.root, manifest, attempt=attempt)
            report = runner.run(spec, MarkerAwareEngine(store, spec.marker_key))
            reports.append(report)
        self.assertEqual(len(reports), 20)
        self.assertTrue(all(report.classification == "EXECUTION_VALID" for report in reports))
        self.assertTrue(all(report.source_reads == 2 for report in reports))
        self.assertTrue(all(report.engine_invocations == 1 for report in reports))
        self.assertTrue(all(report.marker_created and report.result_created and report.run_once_created for report in reports))
        self.assertTrue(all(report.scientific_result_admissible for report in reports))


if __name__ == "__main__":
    unittest.main()
