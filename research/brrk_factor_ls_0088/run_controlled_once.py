from __future__ import annotations

"""Unique authorized controlled RUN for BRRK-FACTOR-LS-0088."""

from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

from research.brrk_factor_ls_0088.engine import FactorLS0088Engine
from research.governance.controlled_research_runner_v1 import ManifestEntry, RunSpec, SourceManifest
from research.governance.controlled_research_runner_v1_source_interface import ControlledResearchRunnerV1SourceQualified
from research.governance.git_create_only_store_v1 import GitCreateOnlyStoreV1

ROOT = Path(__file__).resolve().parents[2]
RID = "BRRK-FACTOR-LS-0088"
ATTEMPT = "attempt-1-of-1"
RUN_BRANCH = "research/0088-factor-ls-run-v1"
BASE = ROOT / "research" / "brrk_factor_ls_0088"
SUBMANIFEST = ROOT / "research" / "brrk_crypto_cross_sectional_ls_0076" / "AUTHORIZED_OBJECT_SUBMANIFEST.json"
MARKER_KEY = "research/brrk_factor_ls_0088/RUN_ATTEMPT.marker"
RESULT_KEY = "research/brrk_factor_ls_0088/PRIMARY_RESULT.json"
RUN_ONCE_KEY = "research/brrk_factor_ls_0088/RUN_ONCE.marker"
MARKER_BRANCH = "research/0088-factor-ls-attempt-marker-v1"
RESULT_BRANCH = "research/0088-factor-ls-result-v1"
KLINE_FAMILY = "USD_M_MONTHLY_1D_PERPETUAL_KLINE"
FUNDING_FAMILY = "USD_M_MONTHLY_FUNDING_RATE"


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


def _runtime_key(staged_relative_path: str) -> str:
    """Map immutable staging namespace to the frozen GitHub artifact namespace."""
    if staged_relative_path.startswith("stage/payloads/"):
        return staged_relative_path[len("stage/") :]
    if staged_relative_path.startswith("payloads/"):
        return staged_relative_path
    raise RuntimeError(f"UNKNOWN_STAGED_SOURCE_KEY:{staged_relative_path}")


def _authorization() -> dict:
    auth = _read_json(BASE / "RUN_AUTHORIZATION.json")
    if auth.get("research_id") != RID:
        raise RuntimeError("AUTHORIZATION_RESEARCH_ID_MISMATCH")
    if auth.get("attempt") != "1/1" or auth.get("authorization") != "AUTHORIZED":
        raise RuntimeError("AUTHORIZATION_STATE_MISMATCH")
    if auth.get("attempt_consumed") is not False:
        raise RuntimeError("AUTHORIZATION_ALREADY_CONSUMED")
    if auth.get("controlled_values_exposed") is not False:
        raise RuntimeError("AUTHORIZATION_EXPOSURE_STATE_MISMATCH")
    authorized_at = auth.get("authorized_at")
    if not isinstance(authorized_at, str) or not authorized_at.endswith("Z"):
        raise RuntimeError("AUTHORIZATION_TIMESTAMP_MISSING")
    return auth


def _manifest(arm: dict, auth: dict) -> SourceManifest:
    expected_sha = str(arm["manifests"]["submanifest_sha256"])
    actual_sha = _sha256_file(SUBMANIFEST)
    if actual_sha != expected_sha:
        raise RuntimeError(f"SUBMANIFEST_HASH_MISMATCH:{actual_sha}")

    parent = _read_json(SUBMANIFEST)
    selection = arm["selection"]
    if parent.get("authorized_payload_objects") != selection["total_objects"]:
        raise RuntimeError("AUTHORIZED_OBJECT_COUNT_MISMATCH")

    allowed = {KLINE_FAMILY, FUNDING_FAMILY}
    rows = [
        row
        for row in parent.get("objects", [])
        if row.get("source_family") in allowed
        and selection["candidate_month_start"] <= row.get("month", "") <= selection["candidate_month_end"]
    ]
    rows.sort(key=lambda row: (row["source_family"], row["symbol"], row["month"], row["staged_relative_path"]))
    if len(rows) != selection["total_objects"]:
        raise RuntimeError(f"SELECTED_OBJECT_COUNT_MISMATCH:{len(rows)}")
    family_counts = {
        KLINE_FAMILY: sum(row.get("source_family") == KLINE_FAMILY for row in rows),
        FUNDING_FAMILY: sum(row.get("source_family") == FUNDING_FAMILY for row in rows),
    }
    if family_counts[KLINE_FAMILY] != selection["kline_objects"]:
        raise RuntimeError(f"KLINE_OBJECT_COUNT_MISMATCH:{family_counts[KLINE_FAMILY]}")
    if family_counts[FUNDING_FAMILY] != selection["funding_objects"]:
        raise RuntimeError(f"FUNDING_OBJECT_COUNT_MISMATCH:{family_counts[FUNDING_FAMILY]}")
    symbols = {str(row["symbol"]) for row in rows}
    if len(symbols) != selection["eligible_symbols"]:
        raise RuntimeError(f"ELIGIBLE_SYMBOL_COUNT_MISMATCH:{len(symbols)}")
    if selection.get("require_btcusdt") is True and "BTCUSDT" not in symbols:
        raise RuntimeError("MISSING_BTCUSDT_SOURCE")
    if any(row.get("staging_status") != "STAGED_HASH_VERIFIED_OFFLINE_READABLE" for row in rows):
        raise RuntimeError("STAGING_STATUS_MISMATCH")
    if any(row.get("scientific_content_read_budget") != 1 for row in rows):
        raise RuntimeError("READ_BUDGET_MISMATCH")
    if any(row.get("payload_sha256") is None for row in rows):
        raise RuntimeError("MISSING_DECLARED_PAYLOAD_HASH")
    if any(row.get("staged_byte_size") is None for row in rows):
        raise RuntimeError("MISSING_DECLARED_BYTE_SIZE")

    entries = tuple(
        ManifestEntry(
            filename=_runtime_key(str(row["staged_relative_path"])),
            size=int(row["staged_byte_size"]),
            sha256=str(row["payload_sha256"]),
        )
        for row in rows
    )
    names = [entry.filename for entry in entries]
    if len(names) != len(set(names)):
        raise RuntimeError("DUPLICATE_RUNTIME_OBJECT")
    FactorLS0088Engine().validate_source_keys(names)

    artifact = arm["artifact"]
    source_id = f"github-actions-artifact:{artifact['artifact_id']}:{artifact['digest']}"
    return SourceManifest(
        manifest_id=f"sha256:{expected_sha}#0088-usdm-kline-funding-{len(entries)}",
        source_id=source_id,
        decision_timestamp=auth["authorized_at"],
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
    auth = _authorization()
    if arm.get("research_id") != RID or arm.get("gate") != "ARM":
        raise RuntimeError("ARM_IDENTITY_MISMATCH")
    if arm.get("controlled_attempt") != "0/1" or arm.get("controlled_reads") != 0:
        raise RuntimeError("ARM_ATTEMPT_OR_READ_STATE_MISMATCH")
    if arm.get("engine_calls") != "0/1" or arm.get("scientific_values_exposed") is not False:
        raise RuntimeError("ARM_ENGINE_OR_EXPOSURE_STATE_MISMATCH")
    execution = arm.get("execution", {})
    if execution.get("runner") != "ControlledResearchRunnerV1SourceQualified":
        raise RuntimeError("COMMON_RUNNER_MISMATCH")
    if execution.get("engine") != "FactorLS0088Engine":
        raise RuntimeError("ENGINE_IDENTITY_MISMATCH")
    if execution.get("attempt_budget") != 1 or execution.get("expected_engine_calls") != 1:
        raise RuntimeError("ARM_EXECUTION_BUDGET_MISMATCH")

    branch = os.environ.get("GITHUB_REF_NAME", RUN_BRANCH)
    if branch != RUN_BRANCH:
        raise RuntimeError(f"WRONG_RUN_BRANCH:{branch}")
    expected_head = os.environ.get("GITHUB_SHA", _head())
    actual_head = _head()
    if actual_head != expected_head:
        raise RuntimeError(f"CHECKOUT_HEAD_MISMATCH:{actual_head}:{expected_head}")

    manifest = _manifest(arm, auth)
    if len(manifest.entries) != execution["expected_controlled_reads"]:
        raise RuntimeError("MANIFEST_OBJECT_COUNT_MISMATCH")

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
    report = ControlledResearchRunnerV1SourceQualified(store).run(spec, FactorLS0088Engine())
    print(json.dumps(asdict(report), sort_keys=True, separators=(",", ":")))

    if report.classification == "EXECUTION_VALID" and report.scientific_result_admissible:
        return 0
    if not report.attempt_consumed:
        return 20
    return 30


if __name__ == "__main__":
    raise SystemExit(main())
