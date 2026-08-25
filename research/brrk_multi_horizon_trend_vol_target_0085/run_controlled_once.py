from __future__ import annotations

"""Unique authorized controlled RUN for BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085."""

from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

from research.brrk_multi_horizon_trend_vol_target_0085.controlled_archive_engine import ARM_EXECUTION_ENGINE
from research.governance.controlled_research_runner_v1 import (
    ControlledResearchRunnerV1,
    ManifestEntry,
    RunSpec,
    SourceManifest,
)
from research.governance.git_create_only_store_v1 import GitCreateOnlyStoreV1

ROOT = Path(__file__).resolve().parents[2]
RID = "BRRK-MULTI-HORIZON-TREND-VOL-TARGET-0085"
ATTEMPT = "attempt-1-of-1"
AUTHORIZATION_TIMESTAMP = "2026-08-25T12:03:00Z"
RUN_BRANCH = "research/0085-trend-run-v1"
BASE = ROOT / "research" / "brrk_multi_horizon_trend_vol_target_0085"
MARKER_KEY = "research/brrk_multi_horizon_trend_vol_target_0085/RUN_ATTEMPT.marker"
RESULT_KEY = "research/brrk_multi_horizon_trend_vol_target_0085/RESULT.json"
RUN_ONCE_KEY = "research/brrk_multi_horizon_trend_vol_target_0085/RUN_ONCE.marker"
MARKER_BRANCH = "research/0085-trend-attempt-marker-v1"
RESULT_BRANCH = "research/0085-trend-result-v1"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _artifact_member_name(staged_relative_path: str) -> str:
    prefix = "stage/"
    if not staged_relative_path.startswith(prefix):
        raise RuntimeError(f"UNEXPECTED_STAGED_RELATIVE_PATH:{staged_relative_path}")
    member = staged_relative_path[len(prefix):]
    if not member.startswith("payloads/"):
        raise RuntimeError(f"UNEXPECTED_ARTIFACT_MEMBER_PATH:{member}")
    return member


def _manifest(arm: dict) -> SourceManifest:
    parent_rel = arm["source_binding"]["parent_manifest_path"]
    parent_path = ROOT / parent_rel
    expected_parent = arm["source_binding"]["parent_manifest_sha256"]
    actual_parent = _sha256_file(parent_path)
    if actual_parent != expected_parent:
        raise RuntimeError(f"PARENT_MANIFEST_HASH_MISMATCH:{actual_parent}")

    parent = _read_json(parent_path)
    filt = arm["source_binding"]["filter"]
    assets = set(filt["assets"])
    symbols = set(filt["symbols"])
    first_month = filt["first_month"]
    last_month = filt["last_month"]
    rows = [
        row for row in parent["objects"]
        if row.get("archive_family") == filt["archive_family"]
        and row.get("asset") in assets
        and row.get("symbol") in symbols
        and first_month <= row.get("month", "") <= last_month
    ]
    rows.sort(key=lambda row: (row["asset"], row["month"], row["staged_relative_path"]))
    if len(rows) != arm["source_binding"]["expected_authorized_objects"]:
        raise RuntimeError(f"AUTHORIZED_OBJECT_COUNT_MISMATCH:{len(rows)}")
    names = [_artifact_member_name(row["staged_relative_path"]) for row in rows]
    if len(names) != len(set(names)):
        raise RuntimeError("DUPLICATE_FILTERED_OBJECT")
    if any(row.get("staging_status") != arm["source_binding"]["required_staging_status"] for row in rows):
        raise RuntimeError("STAGING_STATUS_MISMATCH")
    if any(row.get("scientific_content_read_budget") != 1 for row in rows):
        raise RuntimeError("READ_BUDGET_MISMATCH")

    entries = tuple(
        ManifestEntry(
            filename=_artifact_member_name(row["staged_relative_path"]),
            size=int(row["staged_byte_size"]),
            sha256=row["staged_sha256"],
        )
        for row in rows
    )
    artifact = arm["source_binding"]
    source_id = f"github-actions-artifact:{artifact['artifact_id']}:{artifact['artifact_digest']}"
    return SourceManifest(
        manifest_id=f"sha256:{expected_parent}#0085-perpetual-1d-kline-201",
        source_id=source_id,
        decision_timestamp=AUTHORIZATION_TIMESTAMP,
        archive_identity=source_id,
        entries=entries,
    )


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_controlled_once.py <artifact-zip>")
    archive = Path(sys.argv[1]).resolve()
    if not archive.is_file():
        raise RuntimeError("MISSING_ARTIFACT_ARCHIVE")

    arm = _read_json(BASE / "ARM_CONTRACT.json")
    if arm["research_id"] != RID or arm["attempt_consumed"] or arm["attempt"] != "0/1":
        raise RuntimeError("ARM_ATTEMPT_STATE_MISMATCH")
    if arm["common_runner"] != "CONTROLLED_RESEARCH_RUNNER_V1":
        raise RuntimeError("COMMON_RUNNER_MISMATCH")
    expected_interface = "research.brrk_multi_horizon_trend_vol_target_0085.controlled_archive_engine.ControlledArchiveTrendEngine"
    if arm["execution_interface"] != expected_interface:
        raise RuntimeError("EXECUTION_INTERFACE_MISMATCH")

    branch = os.environ.get("GITHUB_REF_NAME", RUN_BRANCH)
    if branch != RUN_BRANCH:
        raise RuntimeError(f"WRONG_RUN_BRANCH:{branch}")
    expected_head = os.environ.get("GITHUB_SHA", _head())
    actual_head = _head()
    if actual_head != expected_head:
        raise RuntimeError(f"CHECKOUT_HEAD_MISMATCH:{actual_head}:{expected_head}")

    manifest = _manifest(arm)
    store = GitCreateOnlyStoreV1(
        ROOT,
        base_sha=actual_head,
        key_branches={
            MARKER_KEY: MARKER_BRANCH,
            RESULT_KEY: RESULT_BRANCH,
            RUN_ONCE_KEY: RESULT_BRANCH,
        },
    )
    spec = RunSpec(
        research_id=RID,
        attempt_id=ATTEMPT,
        expected_head_sha=expected_head,
        actual_head_sha=actual_head,
        expected_source_id=manifest.source_id,
        manifest=manifest,
        archive_path=archive,
        result_key=RESULT_KEY,
        marker_key=MARKER_KEY,
        run_once_key=RUN_ONCE_KEY,
    )
    report = ControlledResearchRunnerV1(store).run(spec, ARM_EXECUTION_ENGINE())
    print(json.dumps(asdict(report), sort_keys=True, separators=(",", ":")))

    if report.classification == "EXECUTION_VALID" and report.scientific_result_admissible:
        return 0
    if not report.attempt_consumed:
        return 20
    return 30


if __name__ == "__main__":
    raise SystemExit(main())
