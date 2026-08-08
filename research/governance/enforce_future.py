from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Iterable, Sequence

from .future_policy import (
    FUTURE_PRESENCE_FIELDS,
    FuturePolicyFinding,
    enforce_current_paths,
    normalize_path,
)
from .validate import has_failures, repo_root_from_module, validate_repo

EnforcementFinding = FuturePolicyFinding


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
    return sorted(set(normalize_path(path) for path in paths if normalize_path(path)))


def _load_registry(root: Path) -> dict:
    return json.loads((root / "config/research_registry.json").read_text(encoding="utf-8"))


def enforce_changed_paths(root: Path, changed_paths: Sequence[str]) -> list[EnforcementFinding]:
    return enforce_current_paths(_load_registry(root), changed_paths)


def enforce_repo(
    root: Path | None = None,
    base: str | None = None,
    changed_paths: Iterable[str] | None = None,
) -> tuple[list[EnforcementFinding], list]:
    root = Path(root or repo_root_from_module())
    if changed_paths is None:
        if not base:
            raise ValueError("base is required when changed_paths is not supplied")
        changed_paths = changed_paths_from_git(root, base)
    path_findings = enforce_changed_paths(root, list(changed_paths))
    registry_findings = validate_repo(root)
    return path_findings, registry_findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on unregistered post-boundary formal research changes"
    )
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--base", help="PR base commit SHA/ref used for git diff base...HEAD")
    parser.add_argument(
        "--changed-path",
        action="append",
        default=None,
        help="Test/diagnostic override; may be repeated",
    )
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
