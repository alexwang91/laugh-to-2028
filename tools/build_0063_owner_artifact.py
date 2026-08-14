from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

RID = "BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063"
BASE_SHA = "e1ac320e092e554c283ef6b88aaaa5f65aaf61ab"
BASE_REGISTRY_BLOB = "a1e34c10d8dadfeea27cff16310199472a2d1ef7"
PREFIX = "research/brrk_idle_cash_sweep_robustness_0063/"
DESIGN = "research/governance/BRRK_IDLE_CASH_SWEEP_ROBUSTNESS_0063_DESIGN_FREEZE_2026-08-14.md"
OUT = Path("/tmp/0063-owner-artifact")
REG = Path("config/research_registry.json")


def canon(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha256(value: object) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def owner() -> dict:
    return {
        "research_id": RID,
        "research_family_id": "IDLE_CASH_CARRY",
        "research_domain": "RISK_CONTROL",
        "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1",
        "objective_type": "MECHANISM_TEST",
        "created_at": "2026-08-14T00:25:00Z",
        "created_before_result": True,
        "question": "Does a mechanically yield-bearing idle-cash sleeve on the unchanged canonical BRRK-0011 path retain a positive full-cycle net wealth/CAGR advantage after prospectively frozen conservative yield-realization and sweep-friction stresses without worsening drawdown?",
        "hypothesis": "The frozen 50%-DTB3-realization/10-bps-sweep-friction primary cell will improve full-cycle net terminal wealth and CAGR versus unchanged BRRK-0011, preserve drawdown, recur temporally, pass a dependence-aware lower-confidence gate, and remain positive across the frozen core stress neighborhood.",
        "hypothesis_origin": "RESULT_INFORMED_DEVELOPMENT_REPLICATION_OF_F27_R2_NOT_INDEPENDENT_OOS",
        "economic_mechanism": "Capital already left idle by BRRK-0011 may earn short-duration cash yield without changing directional signals, weights or gross exposure; conservative realization haircuts and explicit cash-sleeve transition friction test whether the uplift is robust rather than a frictionless accounting artifact.",
        "primary_target": "FULL_CYCLE_NET_TERMINAL_WEALTH_AND_CALENDAR_SPAN_CAGR_VERSUS_UNCHANGED_BRRK_0011",
        "primary_metric": "PRIMARY_50_PERCENT_DTB3_REALIZATION_10_BPS_SWEEP_FRICTION_PAIRED_RELATIVE_LOG_GROWTH_WITH_ECONOMIC_TEMPORAL_AND_MBB_GATES",
        "secondary_metrics": [
            "max_drawdown",
            "cash_sweep_turnover",
            "total_sweep_friction",
            "chronological_block_relative_log_growth",
            "stress_grid_relative_terminal_wealth",
        ],
        "feature_families": ["IDLE_CASH_FRACTION", "FRED_DTB3_SHORT_RATE"],
        "horizon": "FULL_COMMITTED_BRRK0011_WINDOW",
        "universe": ["BTC", "ETH", "SOL", "BNB", "CASH"],
        "development_dataset_refs": [
            "PIT-DISP-0015-BRRK0011-COMMITTED-PATH",
            "FRED-DTB3-0063-FIRST-VALID-CAPTURE",
        ],
        "validation_dataset_refs": [],
        "sealed_dataset_refs": [],
        "declared_variant_budget": 16,
        "actual_variants_evaluated": 0,
        "parameter_candidate_count": 16,
        "stopping_rule": "Exactly one governed historical execution attempt after preregistration, implementation and controlled-boundary merges; all 16 frozen stress cells are evaluated in one scientific engine call with no result-dependent rerun or rescue.",
        "success_criteria": "The preregistered conservative primary cell passes data identity, net terminal wealth/CAGR, drawdown, temporal recurrence and dependence-aware MBB gates, and all preregistered core stress-neighborhood cells retain positive relative terminal wealth.",
        "failure_criteria": "Ordered preregistered failure taxonomy binds at the first failed gate; data-identity failure is inconclusive/invalid rather than economic failure.",
        "allowed_followup": "A PASS may motivate a NEW-ID future-only validation or integration study; a FAIL may motivate a scientifically distinct NEW-ID mechanism only after immutable closeout.",
        "forbidden_followup": "No same-ID rate-series substitution, yield/friction-grid change, primary-cell change, BRRK signal/weight/gross modification, favorable-block selection, gate relaxation, rerun, recomputation, retune or rescue after outcome exposure.",
        "researcher_decisions": "The unchanged BRRK-0011 path, first-valid DTB3 capture contract, 4x4 stress grid, conservative primary cell and minimum robustness substance were frozen at DESIGN before 0063 candidate economics.",
        "research_process_complexity": {
            "declared_parameter_candidates": 16,
            "actual_parameter_candidates_evaluated": 0,
            "universes_evaluated": 1,
            "horizons_evaluated": 1,
            "rebalance_variants": 0,
            "feature_representations": 2,
            "special_cases_introduced": 1,
            "validation_exposure_event_refs": [],
            "related_family_trials": 1,
        },
        "lineage_edges": [],
        "result_status": "PREREGISTERED_NOT_RUN",
        "failure_reason": None,
        "promotion_state": "NONE",
        "evidence_refs": [],
        "decision_refs": [
            DESIGN,
            "research/brrk_idle_cash_sweep_robustness_0063/PREREGISTRATION.json",
            "research/brrk_idle_cash_sweep_robustness_0063/DATASET_DECLARATION.json",
            "docs/CURRENT_STATE.md",
        ],
        "production_relevance": "DEVELOPMENT cash-carry robustness replication only; no canonical BRRK-0011, Phase-6, production, signer or order-submission authority.",
        "production_authorized": False,
        "provenance_status": "FACT",
        "governed_path_prefixes": [PREFIX],
        "notes": [
            "F27 R2 is exposed DEVELOPMENT motivation only and cannot satisfy 0063 gates.",
            "0063 changes no BRRK-0011 risk-asset signal, target, weight or gross exposure.",
            "The first-valid DTB3 raw capture is immutable and replacement is forbidden.",
            "All 16 stress cells are reported; only the prospectively frozen primary hypothesis can promote.",
        ],
    }


def main() -> None:
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != BASE_SHA:
        raise SystemExit("builder must run against exact merged 0063 DESIGN SHA")
    base = json.loads(REG.read_text(encoding="utf-8"))
    if any(r.get("research_id") == RID for r in base["records"]):
        raise SystemExit("0063 already exists in base registry")
    before_hashes = [sha256(r) for r in base["records"]]
    clean = owner()
    forbidden = {"evidence_scorecard", "confidence_level", "confidence_components", "derived_confidence"}
    leaked = forbidden.intersection(clean)
    if leaked:
        raise SystemExit(f"illegal result-derived prereg owner fields: {sorted(leaked)}")
    patched = json.loads(json.dumps(base))
    patched["records"].append(clean)
    after_old_hashes = [sha256(r) for r in patched["records"][:-1]]
    if before_hashes != after_old_hashes:
        raise SystemExit("pre-existing registry record mutation detected")
    if len(patched["records"]) != len(base["records"]) + 1:
        raise SystemExit("record-count invariant failed")
    OUT.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(patched, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    subprocess.run(["python", "-m", "research.governance.validate"], check=True)
    output_blob = subprocess.check_output(["git", "hash-object", str(REG)], text=True).strip()
    report = {
        "schema_version": 1,
        "research_id": RID,
        "base_commit_sha": BASE_SHA,
        "base_registry_blob_sha": BASE_REGISTRY_BLOB,
        "base_record_count": len(base["records"]),
        "output_record_count": len(patched["records"]),
        "preexisting_records_unchanged": before_hashes == after_old_hashes,
        "new_owner_sha256": sha256(clean),
        "new_owner_has_evidence_scorecard": "evidence_scorecard" in clean,
        "output_registry_git_blob_sha": output_blob,
        "result_status": clean["result_status"],
        "promotion_state": clean["promotion_state"],
        "actual_variants_evaluated": clean["actual_variants_evaluated"],
        "production_authorized": clean["production_authorized"],
    }
    (OUT / "research_registry.json").write_bytes(REG.read_bytes())
    (OUT / "OWNER.json").write_text(json.dumps(clean, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    (OUT / "BUILD_REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
