from __future__ import annotations

"""Public fail-closed runner for future controlled research attempts.

This module is prospective execution infrastructure only.  It never authorizes a
scientific attempt by itself.  Callers must arrive with an already-frozen source
manifest, exact expected git head, an externally authorized attempt identity and
a create-only persistence backend.

The critical ordering invariant is:

    metadata-only preflight -> durable RUN_ATTEMPT.marker -> payload reads ->
    exactly-one engine invocation -> create-only RESULT -> RUN_ONCE.marker

Before RUN_ATTEMPT.marker exists this module may inspect only archive identity,
filenames and central-directory metadata plus hashes/sizes declared in the
external manifest.  It deliberately never calls ZipFile.testzip(), read(),
open(), extract(), decompresses payloads, or performs a CRC payload scan before
the marker is durably created.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Protocol
import hashlib
import http.client
import json
import math
import socket
import urllib.request
import zipfile

RUNNER_ID = "CONTROLLED_RESEARCH_RUNNER_V1"
RUNNER_SCHEMA_VERSION = 1
MANIFEST_SCHEMA_VERSION = 1


class RunnerError(RuntimeError):
    """Base runner error."""


class PreflightRejected(RunnerError):
    """Rejected before an attempt marker.  No controlled payload may be read."""


class InvalidExecution(RunnerError):
    """Attempt was marked but execution became invalid."""


class DuplicatePayloadRead(InvalidExecution):
    pass


class DoubleEngineInvocation(InvalidExecution):
    pass


class NetworkAttemptBlocked(InvalidExecution):
    pass


class CreateOnlyStore(Protocol):
    def exists(self, key: str) -> bool: ...

    def create_only(self, key: str, payload: bytes) -> None: ...


class ControlledEngine(Protocol):
    def execute(self, context: "EngineContext") -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class ManifestEntry:
    filename: str
    size: int
    sha256: str

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ManifestEntry":
        filename = value.get("filename")
        size = value.get("size")
        digest = value.get("sha256")
        if not isinstance(filename, str) or not filename or filename.startswith("/") or ".." in Path(filename).parts:
            raise PreflightRejected("INVALID_MANIFEST_FILENAME")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise PreflightRejected("INVALID_MANIFEST_SIZE")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise PreflightRejected("INVALID_MANIFEST_SHA256")
        return cls(filename=filename, size=size, sha256=digest)


@dataclass(frozen=True)
class SourceManifest:
    manifest_id: str
    source_id: str
    decision_timestamp: str
    archive_identity: str
    entries: tuple[ManifestEntry, ...]
    schema_version: int = MANIFEST_SCHEMA_VERSION

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SourceManifest":
        if value.get("schema_version") != MANIFEST_SCHEMA_VERSION:
            raise PreflightRejected("SCHEMA_DRIFT")
        manifest_id = value.get("manifest_id")
        source_id = value.get("source_id")
        timestamp = value.get("decision_timestamp")
        archive_identity = value.get("archive_identity")
        raw_entries = value.get("entries")
        if not isinstance(manifest_id, str) or not manifest_id:
            raise PreflightRejected("MISSING_MANIFEST_ID")
        if not isinstance(source_id, str) or not source_id:
            raise PreflightRejected("MISSING_SOURCE_ID")
        if not isinstance(timestamp, str) or not timestamp:
            raise PreflightRejected("MISSING_TIMESTAMP")
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as exc:
            raise PreflightRejected("INVALID_TIMESTAMP") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise PreflightRejected("INVALID_TIMESTAMP")
        if not isinstance(archive_identity, str) or not archive_identity:
            raise PreflightRejected("MISSING_ARCHIVE_IDENTITY")
        if not isinstance(raw_entries, list) or not raw_entries:
            raise PreflightRejected("MISSING_MANIFEST_ENTRIES")
        entries = tuple(ManifestEntry.from_mapping(row) for row in raw_entries if isinstance(row, Mapping))
        if len(entries) != len(raw_entries):
            raise PreflightRejected("INVALID_MANIFEST_ENTRY")
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)):
            raise PreflightRejected("DUPLICATE_MANIFEST_OBJECT")
        return cls(
            manifest_id=manifest_id,
            source_id=source_id,
            decision_timestamp=timestamp,
            archive_identity=archive_identity,
            entries=entries,
        )


@dataclass(frozen=True)
class RunSpec:
    research_id: str
    attempt_id: str
    expected_head_sha: str
    actual_head_sha: str
    expected_source_id: str
    manifest: SourceManifest
    archive_path: Path
    result_key: str
    marker_key: str
    run_once_key: str


@dataclass(frozen=True)
class EngineContext:
    research_id: str
    attempt_id: str
    decision_timestamp: str
    manifest_id: str
    source_id: str
    sources: Mapping[str, bytes]


@dataclass(frozen=True)
class RunReport:
    runner_id: str
    classification: str
    attempt_consumed: bool
    marker_created: bool
    result_created: bool
    run_once_created: bool
    source_reads: int
    engine_invocations: int
    scientific_result_admissible: bool
    error: str | None = None


class InMemoryCreateOnlyStore:
    """Deterministic synthetic backend used by qualification and examples."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def exists(self, key: str) -> bool:
        return key in self.objects

    def create_only(self, key: str, payload: bytes) -> None:
        if key in self.objects:
            raise FileExistsError(key)
        self.objects[key] = bytes(payload)


class PayloadArchive:
    """Owns the single physical payload-read budget for one controlled archive."""

    def __init__(self, archive_path: Path, manifest: SourceManifest) -> None:
        self.archive_path = Path(archive_path)
        self.manifest = manifest
        self._read_called = False
        self.read_count = 0

    def metadata_preflight(self) -> None:
        """Central-directory metadata only.  No payload decompression or CRC scan."""
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zf:
                infos = zf.infolist()
        except (OSError, zipfile.BadZipFile) as exc:
            raise PreflightRejected("INVALID_ZIP_CENTRAL_DIRECTORY") from exc

        names = [info.filename for info in infos if not info.is_dir()]
        if len(names) != len(set(names)):
            raise PreflightRejected("DUPLICATE_OBJECT")
        expected = {entry.filename: entry for entry in self.manifest.entries}
        # A frozen source artifact may be a superset container shared by several
        # prospectively filtered research IDs.  Pre-marker we may inspect only
        # central-directory metadata, so require every authorized member and
        # validate its declared size while ignoring unmanifested members.  The
        # post-marker read path still opens only manifest entries, so extras
        # consume zero controlled-read budget and expose zero scientific values.
        missing = sorted(set(expected) - set(names))
        if missing:
            raise PreflightRejected(f"ARCHIVE_FILE_SET_MISMATCH missing={missing}")
        # file_size is central-directory metadata and is explicitly allowed pre-marker.
        for info in infos:
            if info.is_dir() or info.filename not in expected:
                continue
            if info.file_size != expected[info.filename].size:
                raise PreflightRejected(f"DECLARED_SIZE_MISMATCH:{info.filename}")

    def read_verified_payloads(self) -> Mapping[str, bytes]:
        if self._read_called:
            raise DuplicatePayloadRead("DUPLICATE_PAYLOAD_READ")
        self._read_called = True
        expected = {entry.filename: entry for entry in self.manifest.entries}
        payloads: dict[str, bytes] = {}
        try:
            with zipfile.ZipFile(self.archive_path, "r") as zf:
                for entry in self.manifest.entries:
                    # This is the first operation that decompresses/scans payload bytes.
                    # ZipExtFile verifies CRC while the complete entry is read.
                    with zf.open(entry.filename, "r") as handle:
                        payload = handle.read()
                    self.read_count += 1
                    if len(payload) != entry.size:
                        raise InvalidExecution(f"PAYLOAD_SIZE_MISMATCH:{entry.filename}")
                    if hashlib.sha256(payload).hexdigest() != entry.sha256:
                        raise InvalidExecution(f"PAYLOAD_HASH_MISMATCH:{entry.filename}")
                    payloads[entry.filename] = payload
        except InvalidExecution:
            raise
        except zipfile.BadZipFile as exc:
            raise InvalidExecution("CORRUPTED_ZIP_OR_CRC") from exc
        except (KeyError, OSError, RuntimeError) as exc:
            raise InvalidExecution("PAYLOAD_READ_FAILURE") from exc
        if set(payloads) != set(expected):
            raise InvalidExecution("PAYLOAD_SET_MISMATCH")
        return MappingProxyType(payloads)


class EngineInvocationGuard:
    def __init__(self, engine: ControlledEngine) -> None:
        self.engine = engine
        self.invocations = 0

    def invoke(self, context: EngineContext) -> Mapping[str, Any]:
        if self.invocations != 0:
            raise DoubleEngineInvocation("DOUBLE_ENGINE_INVOCATION")
        self.invocations += 1
        return self.engine.execute(context)


class NetworkGuard:
    """Blocks common Python network paths during the scientific engine call."""

    def __enter__(self) -> "NetworkGuard":
        self._socket_connect = socket.socket.connect
        self._create_connection = socket.create_connection
        self._urlopen = urllib.request.urlopen
        self._http_connect = http.client.HTTPConnection.connect
        self._https_connect = http.client.HTTPSConnection.connect

        def blocked(*_args: Any, **_kwargs: Any) -> Any:
            raise NetworkAttemptBlocked("NETWORK_ATTEMPT")

        socket.socket.connect = blocked  # type: ignore[assignment]
        socket.create_connection = blocked  # type: ignore[assignment]
        urllib.request.urlopen = blocked  # type: ignore[assignment]
        http.client.HTTPConnection.connect = blocked  # type: ignore[assignment]
        http.client.HTTPSConnection.connect = blocked  # type: ignore[assignment]
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        socket.socket.connect = self._socket_connect  # type: ignore[assignment]
        socket.create_connection = self._create_connection  # type: ignore[assignment]
        urllib.request.urlopen = self._urlopen  # type: ignore[assignment]
        http.client.HTTPConnection.connect = self._http_connect  # type: ignore[assignment]
        http.client.HTTPSConnection.connect = self._https_connect  # type: ignore[assignment]


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _contains_nonfinite(value: Any) -> bool:
    if isinstance(value, bool) or value is None or isinstance(value, (str, bytes, int)):
        return False
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, Mapping):
        return any(_contains_nonfinite(k) or _contains_nonfinite(v) for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_nonfinite(item) for item in value)
    return False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _valid_sha40(value: str) -> bool:
    return len(value) == 40 and all(c in "0123456789abcdef" for c in value)


class ControlledResearchRunnerV1:
    runner_id = RUNNER_ID

    def __init__(self, store: CreateOnlyStore) -> None:
        self.store = store

    def _preflight(self, spec: RunSpec, engine: ControlledEngine, archive: PayloadArchive) -> None:
        if not spec.research_id or not spec.attempt_id:
            raise PreflightRejected("MISSING_ATTEMPT_IDENTITY")
        if not _valid_sha40(spec.expected_head_sha) or not _valid_sha40(spec.actual_head_sha):
            raise PreflightRejected("INVALID_HEAD_SHA")
        if spec.actual_head_sha != spec.expected_head_sha:
            raise PreflightRejected("STALE_HEAD")
        if spec.manifest.source_id != spec.expected_source_id:
            raise PreflightRejected("WRONG_SOURCE_MANIFEST")
        if not hasattr(engine, "execute") or not callable(getattr(engine, "execute")):
            raise PreflightRejected("WRONG_EXECUTION_INTERFACE")
        if self.store.exists(spec.result_key):
            raise PreflightRejected("EXISTING_RESULT")
        if self.store.exists(spec.marker_key) or self.store.exists(spec.run_once_key):
            raise PreflightRejected("ATTEMPT_ALREADY_CLAIMED")
        archive.metadata_preflight()

    def _persist_envelope(self, spec: RunSpec, envelope: Mapping[str, Any]) -> None:
        self.store.create_only(spec.result_key, _canonical_json(envelope))

    def _seal_invalid(
        self,
        *,
        spec: RunSpec,
        classification: str,
        error: str,
        source_reads: int,
        engine_invocations: int,
    ) -> RunReport:
        envelope = {
            "schema_version": RUNNER_SCHEMA_VERSION,
            "runner_id": RUNNER_ID,
            "research_id": spec.research_id,
            "attempt_id": spec.attempt_id,
            "classification": classification,
            "scientific_result_admissible": False,
            "error": error,
            "source_reads": source_reads,
            "engine_invocations": engine_invocations,
            "produced_at": _utc_now(),
        }
        result_created = False
        run_once_created = False
        try:
            self._persist_envelope(spec, envelope)
            result_created = True
            self.store.create_only(
                spec.run_once_key,
                _canonical_json({
                    "runner_id": RUNNER_ID,
                    "research_id": spec.research_id,
                    "attempt_id": spec.attempt_id,
                    "classification": classification,
                    "result_key": spec.result_key,
                }),
            )
            run_once_created = True
        except Exception as persist_exc:  # the attempt marker still permanently consumes the attempt
            return RunReport(
                runner_id=RUNNER_ID,
                classification="INVALID_EXECUTION_WRITER_FAILURE",
                attempt_consumed=True,
                marker_created=True,
                result_created=result_created,
                run_once_created=run_once_created,
                source_reads=source_reads,
                engine_invocations=engine_invocations,
                scientific_result_admissible=False,
                error=f"{type(persist_exc).__name__}:{persist_exc}",
            )
        return RunReport(
            runner_id=RUNNER_ID,
            classification=classification,
            attempt_consumed=True,
            marker_created=True,
            result_created=result_created,
            run_once_created=run_once_created,
            source_reads=source_reads,
            engine_invocations=engine_invocations,
            scientific_result_admissible=False,
            error=error,
        )

    def run(self, spec: RunSpec, engine: ControlledEngine) -> RunReport:
        archive = PayloadArchive(spec.archive_path, spec.manifest)
        try:
            self._preflight(spec, engine, archive)
        except PreflightRejected as exc:
            return RunReport(
                runner_id=RUNNER_ID,
                classification=f"PRECHECK_REJECTED:{exc}",
                attempt_consumed=False,
                marker_created=False,
                result_created=False,
                run_once_created=False,
                source_reads=0,
                engine_invocations=0,
                scientific_result_admissible=False,
                error=str(exc),
            )

        marker = {
            "schema_version": RUNNER_SCHEMA_VERSION,
            "runner_id": RUNNER_ID,
            "research_id": spec.research_id,
            "attempt_id": spec.attempt_id,
            "expected_head_sha": spec.expected_head_sha,
            "manifest_id": spec.manifest.manifest_id,
            "source_id": spec.manifest.source_id,
            "decision_timestamp": spec.manifest.decision_timestamp,
            "created_at": _utc_now(),
        }
        try:
            self.store.create_only(spec.marker_key, _canonical_json(marker))
        except Exception as exc:
            return RunReport(
                runner_id=RUNNER_ID,
                classification="PRECHECK_REJECTED:MARKER_PUSH_FAILURE",
                attempt_consumed=False,
                marker_created=False,
                result_created=False,
                run_once_created=False,
                source_reads=0,
                engine_invocations=0,
                scientific_result_admissible=False,
                error=f"{type(exc).__name__}:{exc}",
            )

        invocation = EngineInvocationGuard(engine)
        try:
            sources = archive.read_verified_payloads()
            context = EngineContext(
                research_id=spec.research_id,
                attempt_id=spec.attempt_id,
                decision_timestamp=spec.manifest.decision_timestamp,
                manifest_id=spec.manifest.manifest_id,
                source_id=spec.manifest.source_id,
                sources=sources,
            )
            with NetworkGuard():
                engine_result = invocation.invoke(context)
            if not isinstance(engine_result, Mapping):
                raise InvalidExecution("ENGINE_RESULT_NOT_MAPPING")
            if _contains_nonfinite(engine_result):
                raise InvalidExecution("NONFINITE_RESULT")
            # json serializability and NaN rejection are part of the result schema boundary.
            json.dumps(engine_result, sort_keys=True, allow_nan=False)
        except NetworkAttemptBlocked as exc:
            return self._seal_invalid(
                spec=spec,
                classification="INVALID_EXECUTION_NETWORK_ATTEMPT",
                error=str(exc),
                source_reads=archive.read_count,
                engine_invocations=invocation.invocations,
            )
        except DoubleEngineInvocation as exc:
            return self._seal_invalid(
                spec=spec,
                classification="INVALID_EXECUTION_DOUBLE_ENGINE_INVOCATION",
                error=str(exc),
                source_reads=archive.read_count,
                engine_invocations=invocation.invocations,
            )
        except DuplicatePayloadRead as exc:
            return self._seal_invalid(
                spec=spec,
                classification="INVALID_EXECUTION_DUPLICATE_READ",
                error=str(exc),
                source_reads=archive.read_count,
                engine_invocations=invocation.invocations,
            )
        except Exception as exc:
            code = str(exc) if isinstance(exc, InvalidExecution) else f"ENGINE_OR_RUNTIME_FAILURE:{type(exc).__name__}"
            return self._seal_invalid(
                spec=spec,
                classification=f"INVALID_EXECUTION:{code}",
                error=f"{type(exc).__name__}:{exc}",
                source_reads=archive.read_count,
                engine_invocations=invocation.invocations,
            )

        envelope = {
            "schema_version": RUNNER_SCHEMA_VERSION,
            "runner_id": RUNNER_ID,
            "research_id": spec.research_id,
            "attempt_id": spec.attempt_id,
            "classification": "EXECUTION_VALID",
            "scientific_result_admissible": True,
            "manifest_id": spec.manifest.manifest_id,
            "source_id": spec.manifest.source_id,
            "decision_timestamp": spec.manifest.decision_timestamp,
            "source_reads": archive.read_count,
            "engine_invocations": invocation.invocations,
            "engine_result": dict(engine_result),
            "produced_at": _utc_now(),
        }
        try:
            self._persist_envelope(spec, envelope)
            self.store.create_only(
                spec.run_once_key,
                _canonical_json({
                    "runner_id": RUNNER_ID,
                    "research_id": spec.research_id,
                    "attempt_id": spec.attempt_id,
                    "classification": "EXECUTION_VALID",
                    "result_key": spec.result_key,
                }),
            )
        except Exception as exc:
            return RunReport(
                runner_id=RUNNER_ID,
                classification="INVALID_EXECUTION_WRITER_FAILURE",
                attempt_consumed=True,
                marker_created=True,
                result_created=self.store.exists(spec.result_key),
                run_once_created=self.store.exists(spec.run_once_key),
                source_reads=archive.read_count,
                engine_invocations=invocation.invocations,
                scientific_result_admissible=False,
                error=f"{type(exc).__name__}:{exc}",
            )

        return RunReport(
            runner_id=RUNNER_ID,
            classification="EXECUTION_VALID",
            attempt_consumed=True,
            marker_created=True,
            result_created=True,
            run_once_created=True,
            source_reads=archive.read_count,
            engine_invocations=invocation.invocations,
            scientific_result_admissible=True,
            error=None,
        )
