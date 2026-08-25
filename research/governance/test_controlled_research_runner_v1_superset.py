from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from research.governance.controlled_research_runner_v1 import (
    ControlledResearchRunnerV1, InMemoryCreateOnlyStore, ManifestEntry,
    RunSpec, SourceManifest,
)


class _EchoEngine:
    def execute(self, context):
        assert set(context.sources) == {"authorized.bin"}
        return {"rows": 1, "ok": True}


def test_superset_container_reads_only_manifest_members(tmp_path: Path) -> None:
    authorized = b"authorized scientific bytes"
    extra = b"unmanifested bytes that must never enter engine context"
    archive = tmp_path / "superset.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("authorized.bin", authorized)
        zf.writestr("extra.bin", extra)
    manifest = SourceManifest(
        manifest_id="m1", source_id="s1", decision_timestamp="2026-08-25T00:00:00Z",
        archive_identity="artifact:synthetic-superset",
        entries=(ManifestEntry(filename="authorized.bin", size=len(authorized), sha256=hashlib.sha256(authorized).hexdigest()),),
    )
    store = InMemoryCreateOnlyStore()
    spec = RunSpec(
        research_id="SYNTHETIC-SUPERSET", attempt_id="1",
        expected_head_sha="a" * 40, actual_head_sha="a" * 40, expected_source_id="s1",
        manifest=manifest, archive_path=archive, result_key="RESULT.json",
        marker_key="RUN_ATTEMPT.marker", run_once_key="RUN_ONCE.marker",
    )
    report = ControlledResearchRunnerV1(store).run(spec, _EchoEngine())
    assert report.classification == "EXECUTION_VALID"
    assert report.attempt_consumed is True
    assert report.source_reads == 1
    assert report.engine_invocations == 1
    assert report.scientific_result_admissible is True
    envelope = json.loads(store.objects["RESULT.json"])
    assert envelope["source_reads"] == 1
    assert envelope["engine_result"] == {"rows": 1, "ok": True}
