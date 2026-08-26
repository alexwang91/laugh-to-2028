from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .future_policy import authorize_future_research_path, is_formal_research_path
from .validate import repo_root_from_module

# Only files introduced or intentionally maintained by Program-Level Epistemic
# Governance v1 may differ from the verified pre-governance main. Everything
# else, including strategy code/configs and historical research/evidence, must
# remain byte-identical at the git-blob level. New formal research is handled
# separately through the prospective PROGRAM_GOVERNED_V1 authorization path.
ALLOWED_EXACT_PATHS = {
    ".github/workflows/0072-access-probe.yml",
    ".github/workflows/0072-capture-0002.yml",
    ".github/workflows/0085-unique-controlled-run.yml",
    ".github/workflows/0086-unique-controlled-run.yml",
    ".github/workflows/0088-unique-controlled-run.yml",
    ".github/workflows/research-governance.yml",
    ".github/workflows/research-owner-first-0073.yml",
    "config/dataset_exposure_registry.json",
    "config/edge_registry.json",
    "config/research_governance_v1.json",
    "config/research_registry.json",
    "README.md",
    "docs/BACKLOG_ROADMAP_CROSSWALK_2026-08-06.md",
    "docs/CURRENT_STATE.md",
    "docs/IDLE_CASH_EXECUTION_FEASIBILITY.md",
    "docs/LEVERAGE_0040_P4_5_DECISION_2026-08-07.md",
    "docs/NEXT_STEPS.md",
    "docs/PHASE6_ADDRESS_BINDING_REQUEST.md",
    "docs/RIGHT_TAIL_PRESERVATION_GATE.md",
    "docs/PROJECT_GOVERNANCE_2026-08-05.md",
    "docs/PROGRAM_GOVERNANCE_PG0_REPOSITORY_AUDIT_2026-08-08.md",
    "docs/PROGRAM_GOVERNANCE_PG4_RETROSPECTIVE_MAPPING_2026-08-08.md",
    "docs/PROGRAM_GOVERNANCE_V1_SPEC_2026-08-08.md",
    "docs/PROGRAM_LEVEL_EPISTEMIC_GOVERNANCE_V1_FINAL_REPORT_2026-08-08.md",
}
ALLOWED_PREFIXES = ("research/governance/",)

# These high-value historical/economic authority files receive explicit blob
# parity checks in addition to the repository-wide changed-path allowlist.
BLOB_PARITY_PATHS = (
    "config/product.json",
    "config/decision_registry.json",
    "config/phase0_8_drift_audit.json",
    "config/phase6_shadow_contract.json",
    "config/phase7_launch_readiness.json",
    "research/bear_short_0001/BEAR-SHORT-0001.json",
    "research/exposure_smooth_0038/EXPOSURE-SMOOTH-0038.json",
    "research/leverage_0039/LEVERAGE-0039.json",
    "research/leverage_0040/LEVERAGE-0040.json",
    "research/leverage_0041/LEVERAGE-0041.json",
    "research/cycle_exit/p5_2_feature_contract.json",
    "research/cycle_exit/p5_3_state_model_contract.json",
    "research/cycle_exit/p5_3_v2_architecture_contract.json",
    "research/cycle_exit/p5_4_behavior_mapping_contract.json",
    "research/cycle_exit/p5_5_validation_contract.json",
)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


def _run(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, text=True, capture_output=True
    ).stdout.strip()


def _normalize(path: str) -> str:
    value = path.strip()
    while value.startswith("./"):
        value = value[2:]
    value = value.lstrip("/")
    value = str(PurePosixPath(value))
    return "" if value == "." else value


def path_is_allowed(path: str) -> bool:
    """Static no-drift allowlist only.

    Formal future research is deliberately not broadly allowlisted here. It is
    authorized per path by authorize_future_research_path(), which checks a
    narrow PROGRAM_GOVERNED_V1 owner and prospective git provenance.
    """
    path = _normalize(path)
    return path in ALLOWED_EXACT_PATHS or any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def changed_paths(root: Path, boundary: str) -> list[str]:
    raw = _run(root, "diff", "--name-status", "--find-renames", f"{boundary}...HEAD")
    result: set[str] = set()
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            result.update(_normalize(path) for path in parts[1:3])
        elif len(parts) >= 2:
            result.add(_normalize(parts[1]))
    return sorted(path for path in result if path)


def blob_sha(root: Path, ref: str, path: str) -> str:
    return _run(root, "rev-parse", f"{ref}:{path}")


def load_json(root: Path, path: str) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def _decision(decision_registry: dict[str, Any], decision_id: str) -> dict[str, Any] | None:
    for item in decision_registry.get("decisions", []):
        if isinstance(item, dict) and item.get("id") == decision_id:
            return item
    return None


def semantic_checks(root: Path) -> list[Check]:
    product = load_json(root, "config/product.json")
    decisions = load_json(root, "config/decision_registry.json")
    p6 = load_json(root, "config/phase6_shadow_contract.json")
    p7 = load_json(root, "config/phase7_launch_readiness.json")
    p8 = load_json(root, "research/bear_short_0001/BEAR-SHORT-0001.json")

    product_universe = product.get("long_universe")
    p3_decision = _decision(decisions, "DATA-CONTRACT-P3.1") or {}
    leverage_decision = _decision(decisions, "PRODUCT-LEVERAGE-2026-08-05") or {}
    bnb_decision = _decision(decisions, "ROUTER-BNB-PERP-ONLY-2026-08-06") or {}

    return [
        Check(
            "canonical_directional_core",
            product.get("production", {}).get("model_version") == "BRRK-0011_FROZEN_RESEARCH_TARGET",
            repr(product.get("production", {}).get("model_version")),
        ),
        Check("long_universe_exact", product_universe == ["BTC", "ETH", "SOL", "BNB"], repr(product_universe)),
        Check("bnb_present", isinstance(product_universe, list) and "BNB" in product_universe, repr(product_universe)),
        Check(
            "xrp_feature_only",
            "XRP remains feature-only" in str(p3_decision.get("decision", "")),
            str(p3_decision.get("decision", "")),
        ),
        Check(
            "primary_venue_hyperliquid",
            str(product.get("primary_venue", "")).lower() == "hyperliquid",
            repr(product.get("primary_venue")),
        ),
        Check(
            "daily_boundary_0000_utc",
            product.get("canonical_timezone") == "UTC" and product.get("daily_boundary_utc") == "00:00",
            f"{product.get('canonical_timezone')} {product.get('daily_boundary_utc')}",
        ),
        Check(
            "production_components_empty",
            decisions.get("production_authorized_components") == [],
            repr(decisions.get("production_authorized_components")),
        ),
        Check("production_gross_cap_phase6_1_0", p6.get("production_gross_cap") == 1.0, repr(p6.get("production_gross_cap"))),
        Check("production_gross_cap_phase7_1_0", p7.get("production_gross_cap") == 1.0, repr(p7.get("production_gross_cap"))),
        Check(
            "leverage_decision_still_1_0",
            "Current production gross cap remains 1.0" in str(leverage_decision.get("decision", "")),
            str(leverage_decision.get("decision", "")),
        ),
        Check("bnb_perp_policy_present", "BNB" in str(bnb_decision.get("decision", "")), str(bnb_decision.get("decision", ""))),
        Check("phase6_production_false", p6.get("production_authorized") is False, repr(p6.get("production_authorized"))),
        Check("phase6_signature_false", p6.get("signature_authorized") is False, repr(p6.get("signature_authorized"))),
        Check("phase6_submit_false", p6.get("order_submission_authorized") is False, repr(p6.get("order_submission_authorized"))),
        Check(
            "phase6_elapsed_days_14",
            p6.get("acceptance", {}).get("live_shadow_observation", {}).get("minimum_elapsed_calendar_days") == 14,
            repr(p6.get("acceptance", {}).get("live_shadow_observation", {}).get("minimum_elapsed_calendar_days")),
        ),
        Check(
            "phase6_scheduled_decisions_10",
            p6.get("acceptance", {}).get("live_shadow_observation", {}).get("minimum_scheduled_decisions") == 10,
            repr(p6.get("acceptance", {}).get("live_shadow_observation", {}).get("minimum_scheduled_decisions")),
        ),
        Check("phase7_monitor_only", p7.get("current_program_state") == "MONITOR_ONLY", repr(p7.get("current_program_state"))),
        Check("phase7_production_false", p7.get("production_authorized") is False, repr(p7.get("production_authorized"))),
        Check(
            "phase8_trigger_absent",
            p8.get("status") == "PREREGISTERED_TRIGGER_ABSENT_NOT_RUN" and p8.get("trigger_present") is False,
            f"{p8.get('status')} trigger={p8.get('trigger_present')}",
        ),
        Check(
            "phase8_no_short_authority",
            p8.get("short_ready") is False
            and p8.get("production_authorized") is False
            and p8.get("first_real_short_authorized") is False,
            (
                f"short_ready={p8.get('short_ready')} "
                f"production={p8.get('production_authorized')} "
                f"first_real={p8.get('first_real_short_authorized')}"
            ),
        ),
    ]


def no_drift_snapshot(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or repo_root_from_module())
    governance = load_json(root, "config/research_governance_v1.json")
    current_registry = load_json(root, "config/research_registry.json")
    boundary = str(governance.get("legacy_boundary_commit", ""))
    head = _run(root, "rev-parse", "HEAD")
    paths = changed_paths(root, boundary)

    unauthorized: list[str] = []
    future_authorizations: list[dict[str, Any]] = []
    for path in paths:
        if path_is_allowed(path):
            continue
        if is_formal_research_path(path):
            authorization = authorize_future_research_path(
                root,
                boundary,
                path,
                current_registry=current_registry,
            )
            future_authorizations.append(authorization.as_dict())
            if authorization.allowed:
                continue
        unauthorized.append(path)

    blob_checks: list[dict[str, Any]] = []
    for path in BLOB_PARITY_PATHS:
        try:
            before = blob_sha(root, boundary, path)
            after = blob_sha(root, "HEAD", path)
            blob_checks.append({
                "path": path,
                "boundary_blob": before,
                "head_blob": after,
                "unchanged": before == after,
            })
        except subprocess.CalledProcessError as exc:
            blob_checks.append({
                "path": path,
                "boundary_blob": None,
                "head_blob": None,
                "unchanged": False,
                "error": exc.stderr.strip(),
            })

    semantics = semantic_checks(root)
    passed = (
        not unauthorized
        and all(item.get("unchanged") is True for item in blob_checks)
        and all(check.passed for check in semantics)
    )
    return {
        "title": "Program-Level Epistemic Governance v1 No-Drift Regression",
        "legacy_boundary_commit": boundary,
        "head": head,
        "changed_paths_since_boundary": paths,
        "unauthorized_changed_paths": unauthorized,
        "future_research_authorizations": future_authorizations,
        "allowed_change_scope": {
            "exact_paths": sorted(ALLOWED_EXACT_PATHS),
            "prefixes": list(ALLOWED_PREFIXES),
            "future_research_rule": (
                "Formal post-boundary research/** paths require exactly one valid "
                "PROGRAM_GOVERNED_V1 owner plus prospective git provenance; legacy "
                "research trees remain immutable."
            ),
        },
        "blob_parity": blob_checks,
        "semantic_invariants": [check.as_dict() for check in semantics],
        "existing_ci_required": [
            "P3.2 research-live parity and committed golden vectors",
            "Phase 0-8 drift audit",
            "Phase 6 shadow contract/safety",
            "Phase 7 readiness gate",
            "Phase 8 bear-short trigger gate",
            "historical research contract/result checks",
        ],
        "result": "PASS" if passed else "FAIL",
    }


def render_text(snapshot: dict[str, Any]) -> str:
    lines = [
        snapshot["title"],
        f"Legacy boundary: {snapshot['legacy_boundary_commit']}",
        f"HEAD: {snapshot['head']}",
        f"Changed paths since boundary: {len(snapshot['changed_paths_since_boundary'])}",
        f"Unauthorized changed paths: {len(snapshot['unauthorized_changed_paths'])}",
    ]
    for path in snapshot["unauthorized_changed_paths"]:
        lines.append(f"  BLOCKING_PATH {path}")

    authorizations = snapshot.get("future_research_authorizations", [])
    if authorizations:
        lines.append("Future research authorizations:")
        for item in authorizations:
            lines.append(
                f"  {'PASS' if item['allowed'] else 'FAIL'} "
                f"{item['path']} owner={item.get('research_id')} "
                f"intro={item.get('introduction_commit')}"
            )
            for finding in item.get("findings", []):
                lines.append(
                    f"    {finding['code']} {finding['subject']}: {finding['message']}"
                )

    lines.append("Blob parity:")
    for item in snapshot["blob_parity"]:
        lines.append(f"  {'PASS' if item['unchanged'] else 'FAIL'} {item['path']}")
    lines.append("Semantic invariants:")
    for item in snapshot["semantic_invariants"]:
        lines.append(f"  {'PASS' if item['passed'] else 'FAIL'} {item['name']}: {item['detail']}")
    lines.append(f"Result: {snapshot['result']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prove Program-Level Epistemic Governance v1 introduced no strategy/evidence/authority drift"
    )
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        snapshot = no_drift_snapshot(args.root)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"No-drift regression: FAIL ({exc})")
        return 1
    if args.as_json:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    else:
        print(render_text(snapshot), end="")
    return 0 if snapshot["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
