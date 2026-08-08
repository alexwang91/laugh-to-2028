from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

from .validate import has_failures, repo_root_from_module, validate_repo

EXCLUDED_RESEARCH_PREFIXES = (
    "research/governance/",
    "research/common/",
)
DISALLOWED_GOVERNED_PREFIXES = {
    "research",
    "research/",
    "research/results",
    "research/results/",
    "research/governance",
    "research/governance/",
    "research/common",
    "research/common/",
}
FUTURE_PRESENCE_FIELDS = (
    "research_id",
    "research_family_id",
    "research_governance_version",
    "governance_mode",
    "objective_type",
    "research_domain",
    "created_at",
    "created_before_result",
    "question",
    "hypothesis",
    "hypothesis_origin",
    "economic_mechanism",
    "primary_target",
    "primary_metric",
    "secondary_metrics",
    "feature_families",
    "horizon",
    "universe",
    "development_dataset_refs",
    "validation_dataset_refs",
    "sealed_dataset_refs",
    "declared_variant_budget",
    "actual_variants_evaluated",
    "stopping_rule",
    "success_criteria",
    "failure_criteria",
    "allowed_followup",
    "forbidden_followup",
    "researcher_decisions",
    "research_process_complexity",
    "lineage_edges",
    "result_status",
    "failure_reason",
    "promotion_state",
    "evidence_refs",
    "production_relevance",
    "production_authorized",
    "provenance_status",
    "governed_path_prefixes",
)


@dataclass(frozen=True)
class EnforcementFinding:
    code: str
    subject: str
    message: str


def _normalize(path: str) -> str:
    value = str(PurePosixPath(path.strip().lstrip("./")))
    return "" if value == "." else value


def _normalize_prefix(prefix: str) -> str:
    value = _normalize(prefix)
    return value.rstrip("/") + "/" if value else ""


def _is_formal_research_path(path: str) -> bool:
    path = _normalize(path)
    if not path.startswith("research/"):
        return False
    return not any(path.startswith(prefix) for prefix in EXCLUDED_RESEARCH_PREFIXES)


def _prefix_owns(prefix: str, path: str) -> bool:
    prefix = _normalize_prefix(prefix)
    path = _normalize(path)
    return bool(prefix) and (path == prefix.rstrip("/") or path.startswith(prefix))


def changed_paths_from_git(root: Path, base: str) -> list[str]:
    command = ["git", "diff", "--name-status", "--find-renames", f"{base}...HEAD"]
    result = subprocess.run(command, cwd=root, check=True, text=True, capture_output=True)
    paths: list[str] = []
    for raw in result.stdout.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            paths.extend(parts[1:3])
        elif len(parts) >= 2:
            paths.append(parts[1])
    return sorted(set(_normalize(path) for path in paths if _normalize(path)))


def _load_registry(root: Path) -> dict:
    return json.loads((root / "config/research_registry.json").read_text(encoding="utf-8"))


def enforce_changed_paths(root: Path, changed_paths: Sequence[str]) -> list[EnforcementFinding]:
    registry = _load_registry(root)
    records = [item for item in registry.get("records", []) if isinstance(item, dict)]
    future = [item for item in records if item.get("governance_mode") == "PROGRAM_GOVERNED_V1"]
    findings: list[EnforcementFinding] = []

    ownership: list[tuple[str, str]] = []
    for record in future:
        rid = str(record.get("research_id", "<missing>"))
        for field in FUTURE_PRESENCE_FIELDS:
            if field not in record:
                findings.append(EnforcementFinding(
                    "MISSING_FUTURE_FIELD",
                    rid,
                    f"PROGRAM_GOVERNED_V1 record must contain field {field!r}; failure_reason may be null before a result, but the key must exist.",
                ))

        prefixes = record.get("governed_path_prefixes")
        if not isinstance(prefixes, list) or not prefixes:
            findings.append(EnforcementFinding(
                "MISSING_GOVERNED_PATH_PREFIX",
                rid,
                "PROGRAM_GOVERNED_V1 research must declare at least one governed research path prefix.",
            ))
            continue

        seen: set[str] = set()
        for raw_prefix in prefixes:
            if not isinstance(raw_prefix, str):
                findings.append(EnforcementFinding("INVALID_GOVERNED_PATH_PREFIX", rid, repr(raw_prefix)))
                continue
            normalized = _normalize_prefix(raw_prefix)
            if not normalized or normalized in DISALLOWED_GOVERNED_PREFIXES or not normalized.startswith("research/"):
                findings.append(EnforcementFinding(
                    "INVALID_GOVERNED_PATH_PREFIX",
                    rid,
                    f"Prefix {raw_prefix!r} is absent, outside research/, or too broad/reserved.",
                ))
                continue
            if any(normalized.startswith(prefix) for prefix in EXCLUDED_RESEARCH_PREFIXES):
                findings.append(EnforcementFinding(
                    "INVALID_GOVERNED_PATH_PREFIX",
                    rid,
                    f"Prefix {raw_prefix!r} points at governance/common infrastructure rather than a formal research line.",
                ))
                continue
            if normalized in seen:
                findings.append(EnforcementFinding("DUPLICATE_GOVERNED_PATH_PREFIX", rid, normalized))
                continue
            seen.add(normalized)
            ownership.append((rid, normalized))

    for path in sorted(set(_normalize(path) for path in changed_paths if _normalize(path))):
        if not _is_formal_research_path(path):
            continue
        owners = sorted({rid for rid, prefix in ownership if _prefix_owns(prefix, path)})
        if not owners:
            findings.append(EnforcementFinding(
                "UNREGISTERED_FORMAL_RESEARCH_PATH",
                path,
                "Changed research path is not covered by any PROGRAM_GOVERNED_V1 record. Register/freeze the research before this path can merge.",
            ))
        elif len(owners) > 1:
            findings.append(EnforcementFinding(
                "AMBIGUOUS_RESEARCH_PATH_OWNERSHIP",
                path,
                "Changed research path is covered by multiple PROGRAM_GOVERNED_V1 records: " + ", ".join(owners),
            ))

    return sorted(findings, key=lambda item: (item.code, item.subject, item.message))


def enforce_repo(root: Path | None = None, base: str | None = None, changed_paths: Iterable[str] | None = None) -> tuple[list[EnforcementFinding], list]:
    root = Path(root or repo_root_from_module())
    if changed_paths is None:
        if not base:
            raise ValueError("base is required when changed_paths is not supplied")
        changed_paths = changed_paths_from_git(root, base)
    path_findings = enforce_changed_paths(root, list(changed_paths))
    registry_findings = validate_repo(root)
    return path_findings, registry_findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail closed on unregistered post-boundary formal research changes")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--base", help="PR base commit SHA/ref used for git diff base...HEAD")
    parser.add_argument("--changed-path", action="append", default=None, help="Test/diagnostic override; may be repeated")
    args = parser.parse_args(argv)

    root = Path(args.root or repo_root_from_module())
    try:
        path_findings, registry_findings = enforce_repo(root, args.base, args.changed_path)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"[BLOCKING] FUTURE_ENFORCEMENT_ERROR: {exc}")
        return 1

    for item in path_findings:
        print(f"[BLOCKING] {item.code} {item.subject}: {item.message}")
    for item in registry_findings:
        print(f"[{item.severity}] {item.code} {item.subject}: {item.message}".rstrip())

    failed = bool(path_findings) or has_failures(registry_findings)
    print("Future research governance enforcement: " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
