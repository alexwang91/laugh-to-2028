from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

EXCLUDED_RESEARCH_PREFIXES = ("research/governance/", "research/common/")
DISALLOWED_GOVERNED_PREFIXES = {
    "research", "research/", "research/results", "research/results/",
    "research/governance", "research/governance/",
    "research/common", "research/common/",
}
FUTURE_PRESENCE_FIELDS = (
    "research_id", "research_family_id", "research_governance_version", "governance_mode",
    "objective_type", "research_domain", "created_at", "created_before_result", "question",
    "hypothesis", "hypothesis_origin", "economic_mechanism", "primary_target", "primary_metric",
    "secondary_metrics", "feature_families", "horizon", "universe", "development_dataset_refs",
    "validation_dataset_refs", "sealed_dataset_refs", "declared_variant_budget",
    "actual_variants_evaluated", "stopping_rule", "success_criteria", "failure_criteria",
    "allowed_followup", "forbidden_followup", "researcher_decisions", "research_process_complexity",
    "lineage_edges", "result_status", "failure_reason", "promotion_state", "evidence_refs",
    "production_relevance", "production_authorized", "provenance_status", "governed_path_prefixes",
)


@dataclass(frozen=True)
class FuturePolicyFinding:
    code: str
    subject: str
    message: str


@dataclass(frozen=True)
class FuturePathAuthorization:
    path: str
    allowed: bool
    research_id: str | None
    findings: tuple[FuturePolicyFinding, ...]
    introduction_commit: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "allowed": self.allowed,
            "research_id": self.research_id,
            "introduction_commit": self.introduction_commit,
            "findings": [item.__dict__ for item in self.findings],
        }


def normalize_path(path: str) -> str:
    value = str(PurePosixPath(path.strip().lstrip("./")))
    return "" if value == "." else value


def normalize_prefix(prefix: str) -> str:
    value = normalize_path(prefix)
    return value.rstrip("/") + "/" if value else ""


def is_formal_research_path(path: str) -> bool:
    path = normalize_path(path)
    return path.startswith("research/") and not any(
        path.startswith(prefix) for prefix in EXCLUDED_RESEARCH_PREFIXES
    )


def prefix_owns(prefix: str, path: str) -> bool:
    prefix = normalize_prefix(prefix)
    path = normalize_path(path)
    return bool(prefix) and (path == prefix.rstrip("/") or path.startswith(prefix))


def _future_records(registry: dict[str, Any]) -> list[dict[str, Any]]:
    records = registry.get("records", [])
    return [
        item for item in records
        if isinstance(item, dict) and item.get("governance_mode") == "PROGRAM_GOVERNED_V1"
    ] if isinstance(records, list) else []


def validate_future_record(record: dict[str, Any]) -> list[FuturePolicyFinding]:
    rid = str(record.get("research_id", "<missing>"))
    out: list[FuturePolicyFinding] = []
    for field in FUTURE_PRESENCE_FIELDS:
        if field not in record:
            out.append(FuturePolicyFinding(
                "MISSING_FUTURE_FIELD", rid,
                f"PROGRAM_GOVERNED_V1 record must contain field {field!r}.",
            ))
    if record.get("research_governance_version") != 1:
        out.append(FuturePolicyFinding(
            "INVALID_FUTURE_GOVERNANCE_VERSION", rid,
            "PROGRAM_GOVERNED_V1 research must use governance version 1.",
        ))
    if record.get("created_before_result") is not True:
        out.append(FuturePolicyFinding(
            "NOT_CREATED_BEFORE_RESULT", rid,
            "Future formal research must be frozen before result release.",
        ))
    if record.get("production_authorized") is not False:
        out.append(FuturePolicyFinding(
            "ILLEGAL_RESEARCH_PRODUCTION_AUTHORIZATION", rid,
            "Research cannot confer production authority.",
        ))

    prefixes = record.get("governed_path_prefixes")
    if not isinstance(prefixes, list) or not prefixes:
        out.append(FuturePolicyFinding(
            "MISSING_GOVERNED_PATH_PREFIX", rid,
            "PROGRAM_GOVERNED_V1 research must declare a governed research path prefix.",
        ))
        return sorted(out, key=lambda item: (item.code, item.subject, item.message))

    seen: set[str] = set()
    for raw in prefixes:
        if not isinstance(raw, str):
            out.append(FuturePolicyFinding("INVALID_GOVERNED_PATH_PREFIX", rid, repr(raw)))
            continue
        prefix = normalize_prefix(raw)
        invalid = (
            not prefix
            or prefix in DISALLOWED_GOVERNED_PREFIXES
            or not prefix.startswith("research/")
            or any(prefix.startswith(excluded) for excluded in EXCLUDED_RESEARCH_PREFIXES)
        )
        if invalid:
            out.append(FuturePolicyFinding(
                "INVALID_GOVERNED_PATH_PREFIX", rid,
                f"Prefix {raw!r} is outside formal research scope, reserved, or too broad.",
            ))
        elif prefix in seen:
            out.append(FuturePolicyFinding("DUPLICATE_GOVERNED_PATH_PREFIX", rid, prefix))
        else:
            seen.add(prefix)
    return sorted(out, key=lambda item: (item.code, item.subject, item.message))


def ownership_pairs(registry: dict[str, Any]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for record in _future_records(registry):
        rid = str(record.get("research_id", "<missing>"))
        prefixes = record.get("governed_path_prefixes")
        if not isinstance(prefixes, list):
            continue
        for raw in prefixes:
            if not isinstance(raw, str):
                continue
            prefix = normalize_prefix(raw)
            if (
                prefix
                and prefix not in DISALLOWED_GOVERNED_PREFIXES
                and prefix.startswith("research/")
                and not any(prefix.startswith(excluded) for excluded in EXCLUDED_RESEARCH_PREFIXES)
            ):
                pairs.append((rid, prefix))
    return pairs


def owners_for_path(registry: dict[str, Any], path: str) -> list[str]:
    return sorted({rid for rid, prefix in ownership_pairs(registry) if prefix_owns(prefix, path)})


def _record(registry: dict[str, Any], rid: str) -> dict[str, Any] | None:
    for item in _future_records(registry):
        if item.get("research_id") == rid:
            return item
    return None


def enforce_current_paths(
    registry: dict[str, Any], changed_paths: Sequence[str]
) -> list[FuturePolicyFinding]:
    out: list[FuturePolicyFinding] = []
    for record in _future_records(registry):
        out.extend(validate_future_record(record))
    for path in sorted({normalize_path(p) for p in changed_paths if normalize_path(p)}):
        if not is_formal_research_path(path):
            continue
        owners = owners_for_path(registry, path)
        if not owners:
            out.append(FuturePolicyFinding(
                "UNREGISTERED_FORMAL_RESEARCH_PATH", path,
                "Changed research path has no PROGRAM_GOVERNED_V1 owner.",
            ))
        elif len(owners) > 1:
            out.append(FuturePolicyFinding(
                "AMBIGUOUS_RESEARCH_PATH_OWNERSHIP", path,
                "Changed research path has multiple owners: " + ", ".join(owners),
            ))
    return sorted(out, key=lambda item: (item.code, item.subject, item.message))


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=check, text=True, capture_output=True)


def _git_text(root: Path, *args: str) -> str:
    return _git(root, *args).stdout.strip()


def _exists_at(root: Path, ref: str, path: str) -> bool:
    return _git(root, "cat-file", "-e", f"{ref}:{normalize_path(path)}", check=False).returncode == 0


def _registry_at(root: Path, ref: str) -> dict[str, Any]:
    value = json.loads(_git_text(root, "show", f"{ref}:config/research_registry.json"))
    if not isinstance(value, dict):
        raise ValueError("research registry must be a JSON object")
    return value


def _first_commit(root: Path, boundary: str, path: str) -> str | None:
    raw = _git_text(root, "log", "--reverse", "--format=%H", f"{boundary}..HEAD", "--", path)
    commits = [line for line in raw.splitlines() if line]
    return commits[0] if commits else None


def _intro_status(root: Path, commit: str, path: str) -> str | None:
    parents = _git_text(root, "show", "-s", "--format=%P", commit).split()
    if not parents:
        return "A"
    raw = _git_text(
        root, "diff-tree", "--no-commit-id", "--name-status", "-r", "-M", "-C",
        parents[0], commit,
    )
    path = normalize_path(path)
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and path in [normalize_path(value) for value in parts[1:]]:
            return parts[0]
    return None


def authorize_future_research_path(
    root: Path,
    boundary: str,
    path: str,
    *,
    current_registry: dict[str, Any] | None = None,
) -> FuturePathAuthorization:
    root, path = Path(root), normalize_path(path)
    out: list[FuturePolicyFinding] = []
    if not is_formal_research_path(path):
        out.append(FuturePolicyFinding(
            "NOT_FORMAL_FUTURE_RESEARCH_PATH", path,
            "Path is not eligible for future formal research authorization.",
        ))
        return FuturePathAuthorization(path, False, None, tuple(out))

    registry = current_registry or json.loads(
        (root / "config/research_registry.json").read_text(encoding="utf-8")
    )
    owners = owners_for_path(registry, path)
    if len(owners) != 1:
        code = "UNREGISTERED_FORMAL_RESEARCH_PATH" if not owners else "AMBIGUOUS_RESEARCH_PATH_OWNERSHIP"
        out.append(FuturePolicyFinding(code, path, f"HEAD owners={owners!r}; exactly one is required."))
        return FuturePathAuthorization(path, False, None, tuple(out))

    rid = owners[0]
    record = _record(registry, rid)
    assert record is not None
    out.extend(validate_future_record(record))

    for raw in record.get("governed_path_prefixes", []):
        if isinstance(raw, str) and prefix_owns(raw, path):
            prefix = normalize_prefix(raw).rstrip("/")
            if _exists_at(root, boundary, prefix):
                out.append(FuturePolicyFinding(
                    "GOVERNED_PREFIX_EXISTED_AT_LEGACY_BOUNDARY", rid,
                    f"Governed prefix {prefix!r} already existed at legacy boundary.",
                ))

    if _exists_at(root, boundary, path):
        out.append(FuturePolicyFinding(
            "FUTURE_PATH_EXISTED_AT_LEGACY_BOUNDARY", path,
            "Future research cannot reuse a file that existed at the legacy boundary.",
        ))

    intro = _first_commit(root, boundary, path)
    if intro is None:
        out.append(FuturePolicyFinding(
            "FUTURE_PATH_INTRODUCTION_NOT_FOUND", path,
            "No post-boundary introduction commit could be identified.",
        ))
        return FuturePathAuthorization(path, False, rid, tuple(sorted(
            out, key=lambda item: (item.code, item.subject, item.message)
        )))

    status = _intro_status(root, intro, path)
    if status is None:
        out.append(FuturePolicyFinding(
            "FUTURE_PATH_INTRODUCTION_STATUS_UNKNOWN", path,
            f"Could not determine git status at introduction commit {intro}.",
        ))
    elif status.startswith(("R", "C")):
        out.append(FuturePolicyFinding(
            "FUTURE_PATH_INTRODUCED_BY_RENAME_OR_COPY", path,
            f"Path first appeared via {status}; rename/copy cannot launder legacy research.",
        ))
    elif not status.startswith("A"):
        out.append(FuturePolicyFinding(
            "FUTURE_PATH_NOT_ADDED_PROSPECTIVELY", path,
            f"First post-boundary status was {status!r}, expected an additive introduction.",
        ))

    try:
        intro_registry = _registry_at(root, intro)
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as exc:
        out.append(FuturePolicyFinding(
            "INTRODUCTION_REGISTRY_UNREADABLE", path,
            f"Cannot read research registry at introduction commit {intro}: {exc}",
        ))
    else:
        intro_owners = owners_for_path(intro_registry, path)
        if intro_owners != [rid]:
            out.append(FuturePolicyFinding(
                "REGISTRATION_NOT_PRESENT_AT_PATH_INTRODUCTION", path,
                f"Introduction commit must already contain exactly owner {rid!r}; found {intro_owners!r}.",
            ))
        else:
            intro_record = _record(intro_registry, rid)
            if intro_record is None:
                out.append(FuturePolicyFinding(
                    "INTRODUCTION_OWNER_RECORD_MISSING", rid,
                    "Owner record is absent at the path introduction commit.",
                ))
            else:
                for finding in validate_future_record(intro_record):
                    out.append(FuturePolicyFinding(
                        "INTRODUCTION_" + finding.code,
                        finding.subject,
                        finding.message,
                    ))

    out = sorted(out, key=lambda item: (item.code, item.subject, item.message))
    return FuturePathAuthorization(path, not out, rid, tuple(out), intro)
