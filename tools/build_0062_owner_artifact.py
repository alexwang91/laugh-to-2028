from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

RID = "BRRK-BTC-RISK-SIGNAL-ATLAS-0062"
BASE_SHA = "aa3fa9c1814c4113918e0d012636db44a1f89659"
BASE_REGISTRY_BLOB = "b8c96a35afe96776e5dc34a93d11bf402c2c8603"
PREFIX = "research/brrk_btc_risk_signal_atlas_0062/"
DESIGN = "research/governance/BRRK_BTC_RISK_SIGNAL_ATLAS_0062_DESIGN_FREEZE_2026-08-13.md"
DEV_DATASET = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
OUT = Path("/tmp/0062-owner-artifact")
REG = Path("config/research_registry.json")

FAMILIES = [
    "F01_TREND_LEVEL_DIRECTION",
    "F02_TREND_SPREAD_DISAGREEMENT",
    "F03_TREND_ACCELERATION_DECELERATION",
    "F04_TREND_CROSS_TRANSITION",
    "F05_VOL_ADJUSTED_TREND_GUARDS",
    "F06_MOMENTUM_LEVEL",
    "F07_OVERBOUGHT_STRETCH",
    "F08_BEARISH_DIVERGENCE_EXHAUSTION",
    "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE",
    "F10_VOLATILITY_REGIME",
    "F11_DOWNSIDE_ASYMMETRY_TAIL",
    "F12_VOLUME_FLOW_CONFIRMATION",
    "F13_CROSS_CRYPTO_BREADTH",
    "F14_RELATIVE_CRYPTO_LEADERSHIP",
    "F21_SEQUENTIAL_CHANGE_DETECTION",
    "F23_MULTI_TIMESCALE_DISAGREEMENT",
    "F24_FIXED_LOW_ORDER_INTERACTIONS",
]


def canon(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def sha256(value: object) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def owner() -> dict:
    return {
        "research_id": RID,
        "research_family_id": "BRRK_BTC_TO_CASH_GROSS_RISK",
        "research_domain": "RISK_CONTROL",
        "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1",
        "objective_type": "MECHANISM_TEST",
        "created_at": "2026-08-13T22:10:00Z",
        "created_before_result": True,
        "question": "Which prospectively frozen market-internal signal families contain recurrent, dependence-aware information about BTC-vs-Cash opportunity cost, forward path damage, or future risk before any control law is defined?",
        "hypothesis": "At least one prospectively frozen Tier-A signal family-track will show positive full-sample sign coherence, temporal recurrence, broad parameter support and a simultaneous dependence-aware lower confidence bound above zero.",
        "hypothesis_origin": "RESULT_INFORMED_DEVELOPMENT_MECHANISM_FORMATION_NOT_INDEPENDENT_OOS",
        "economic_mechanism": "Risk information may arrive through trend, momentum, reversal/exhaustion, volatility, structure, volume, breadth, relative-crypto leadership or structural change; reactive risk information need not be a stable long-horizon return forecast.",
        "primary_target": "FAMILY_TRACK_INFORMATION_ATLAS_T1_T2_T3_OVER_FROZEN_5_10_20_40_SESSION_GEOMETRY",
        "primary_metric": "FAMILY_TRACK_MINIMUM_CONSTITUENT_SPEARMAN_WITH_4_BLOCK_RECURRENCE_PLATEAU_AND_SIMULTANEOUS_MBB_LCB",
        "secondary_metrics": [
            "cell_parameter_plateau_fraction",
            "representation_class_coverage",
            "family_redundancy",
            "data_source_coverage",
        ],
        "feature_families": FAMILIES,
        "horizon": [5, 10, 20, 40],
        "universe": ["BTC", "ETH", "SOL"],
        "development_dataset_refs": [DEV_DATASET],
        "validation_dataset_refs": [],
        "sealed_dataset_refs": [],
        "declared_variant_budget": 185,
        "actual_variants_evaluated": 0,
        "parameter_candidate_count": 185,
        "stopping_rule": "Exactly one governed historical execution attempt after preregistration, implementation and controlled-boundary merges; no result-dependent expansion or rescue.",
        "success_criteria": "At least one of 34 frozen family-track hypotheses passes support, full-sample sign, temporal recurrence, plateau and global simultaneous MBB-LCB gates.",
        "failure_criteria": "If support passes but no family-track passes all frozen gates, FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION; if common support fails, MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT.",
        "allowed_followup": "A passing family-track may motivate a NEW-ID geometry/refinement or conditional-state study; DATA_UNAVAILABLE families require separately frozen new-data research.",
        "forbidden_followup": "No same-ID rerun, retune, indicator addition, horizon/target pruning, reweighting, vendor substitution, gross-map translation or portfolio optimization after outcome exposure.",
        "researcher_decisions": "All 185 Tier-A cells, 34 family-track hypotheses, targets, horizons, support, recurrence, plateau and simultaneous-inference rules are frozen before 0062 historical outcomes.",
        "research_process_complexity": {
            "declared_parameter_candidates": 185,
            "actual_parameter_candidates_evaluated": 0,
            "universes_evaluated": 1,
            "horizons_evaluated": 4,
            "rebalance_variants": 0,
            "feature_representations": 185,
            "special_cases_introduced": 0,
            "validation_exposure_event_refs": [],
            "related_family_trials": 34,
        },
        "lineage_edges": [],
        "result_status": "PREREGISTERED_NOT_RUN",
        "failure_reason": None,
        "promotion_state": "NONE",
        "evidence_refs": [],
        "decision_refs": [
            DESIGN,
            "research/brrk_btc_risk_signal_atlas_0062/PREREGISTRATION.json",
            "research/brrk_btc_risk_signal_atlas_0062/DATASET_DECLARATION.json",
            "docs/CURRENT_STATE.md",
        ],
        "production_relevance": "DEVELOPMENT signal-information atlas only; no state-to-gross, canonical, Phase-6 or production authority.",
        "production_authorized": False,
        "provenance_status": "FACT",
        "governed_path_prefixes": [PREFIX],
        "notes": [
            "RSI, MACD, Supertrend and MA representations have no privileged winner status.",
            "0061 20-day positive signs are exposed DEVELOPMENT only; 0062 freezes 5/10/20/40 before outcome access.",
            "F15-F20 are explicit DATA_UNAVAILABLE under 0062 because no new immutable point-in-time panel is frozen before outcomes.",
            "F22 is not evaluated because no separate causal latent-state training/update semantics are frozen in this ID.",
        ],
    }


def main() -> None:
    if subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip() != BASE_SHA:
        raise SystemExit("builder must run against exact merged 0062 DESIGN SHA")
    base = json.loads(REG.read_text(encoding="utf-8"))
    if any(r.get("research_id") == RID for r in base["records"]):
        raise SystemExit("0062 already exists in base registry")

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
        "actual_variants_evaluated": clean["actual_variants_evaluated"],
        "production_authorized": clean["production_authorized"],
    }
    (OUT / "research_registry.json").write_bytes(REG.read_bytes())
    (OUT / "OWNER.json").write_text(json.dumps(clean, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    (OUT / "BUILD_REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
