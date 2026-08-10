from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RID = "BRRK-EXHAUSTION-TRIGGER-0045"
VALID_RUN = 31391109057
ARTIFACT_ID = 9063704951
ARTIFACT_DIGEST = "sha256:0f8cd31ca3905d798194387622456fc8e59cb786376e57a6c135bdb2867c9c04"
FULL_RESULT_SHA = "06714848cbb8c812a655700c29362487fc9e77ef2638f57547c7340ee10a2682"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def finalize_registry() -> None:
    registry_path = ROOT / "config/research_registry.json"
    registry = load(registry_path)
    prereg = load(ROOT / "research/brrk_exhaustion_trigger_0045/PREREGISTRATION.json")
    result = load(ROOT / "research/brrk_exhaustion_trigger_0045/PRIMARY_RESULT.json")
    execution = load(ROOT / "research/brrk_exhaustion_trigger_0045/EXECUTION.json")
    interface = load(ROOT / "research/brrk_exhaustion_trigger_0045/RUN_INTERFACE.json")

    if result.get("result_status") != "FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY":
        raise SystemExit("unexpected immutable 0045 result")
    if execution.get("execution_status") != "VALID_RESULT_RELEASED_AND_CLOSED":
        raise SystemExit("0045 execution not closed")
    if interface.get("status") != "CLOSED_RESULT_USED":
        raise SystemExit("0045 interface not closed")
    vr = interface["valid_result_run"]
    if vr["workflow_run_id"] != VALID_RUN or vr["artifact_id"] != ARTIFACT_ID:
        raise SystemExit("0045 run binding mismatch")
    if vr["artifact_digest"] != ARTIFACT_DIGEST or vr["full_result_sha256"] != FULL_RESULT_SHA:
        raise SystemExit("0045 hash binding mismatch")

    matches = [i for i, r in enumerate(registry["records"]) if r.get("research_id") == RID]
    if len(matches) != 1:
        raise SystemExit("0045 registry ownership not unique")
    idx = matches[0]
    record = registry["records"][idx]
    if record.get("result_status") != "PREREGISTERED_NOT_RUN":
        raise SystemExit("0045 registry already result-mutated")

    frozen_keys = (
        "research_id", "research_family_id", "research_domain", "research_governance_version",
        "governance_mode", "objective_type", "created_at", "created_before_result", "question",
        "hypothesis", "hypothesis_origin", "economic_mechanism", "primary_target", "primary_metric",
        "secondary_metrics", "feature_families", "horizon", "universe", "development_dataset_refs",
        "validation_dataset_refs", "sealed_dataset_refs", "declared_variant_budget", "parameter_candidate_count",
        "stopping_rule", "success_criteria", "failure_criteria", "allowed_followup", "forbidden_followup",
        "researcher_decisions", "lineage_edges", "production_relevance", "production_authorized",
        "provenance_status", "governed_path_prefixes"
    )
    for key in frozen_keys:
        if record.get(key) != prereg.get(key):
            raise SystemExit(f"frozen prereg field drift: {key}")

    record["actual_variants_evaluated"] = 1
    record["research_process_complexity"]["actual_parameter_candidates_evaluated"] = [
        "TRIGGER_STATE_MACHINE_V1_FIXED_CORE4_S2_S3_HYSTERESIS"
    ]
    record["result_status"] = "FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY"
    record["failure_reason"] = (
        "Frozen state machine failed required sensitivity/timing gates: primary TRUE PRE14_7 WATCH/RISK 3/9, "
        "TRUE episode hit 2/5, severe TRUE PRE14_7 3/7, severe PRE7_POST3 RISK 2/7, and zero qualifying PRE21_0 onsets."
    )
    record["promotion_state"] = "NONE"
    record["evidence_refs"] = [
        "research/brrk_exhaustion_trigger_0045/PRIMARY_RESULT.json",
        "research/brrk_exhaustion_trigger_0045/EXECUTION.json",
        "research/brrk_exhaustion_trigger_0045/RUN_ONCE.marker"
    ]
    record["decision_refs"] = [
        "research/brrk_exhaustion_trigger_0045/RESULT.md",
        "research/brrk_exhaustion_trigger_0045/README.md",
        "docs/CURRENT_STATE.md"
    ]
    record["notes"] = list(prereg.get("notes", [])) + [
        "First one-shot workflow run 31390711467 failed before diagnostic execution because a static no-gross test over-matched the declaration key gross_mapping_defined; no artifact/result existed. The temporary workflow was removed and only the test expression was corrected.",
        "A new fully green pre-result baseline 669942a4bef3f32894f616b9b28e5001d81e82b9 was established before the valid result release.",
        "Unique valid result release was workflow run 31391109057 run number 2 attempt 1 from head f9d4fba80bd07b8a5c67c5c3928f9081332809c7; source taxonomy reproduced exactly and parent 0044 PASS binding matched.",
        "Specificity was strong: zero of six primary continuation events triggered WATCH/RISK in PRE14_0 and zero of six triggered RISK in PRE14_POST3.",
        "Sensitivity failed: primary TRUE PRE14_7 WATCH/RISK hit 3/9, TRUE episode hit 2/5, severe TRUE PRE14_7 hit 3/7 and severe PRE7_POST3 RISK confirmation 2/7.",
        "No primary TRUE event had a qualifying new WATCH/RISK transition onset in PRE21_0 because captured events were already in WATCH/RISK before that window; the premature-clear denominator was therefore zero and the preregistered gate failed.",
        "WATCH plus RISK occupied about 34.38 percent of all 1,332 sessions and non-HEALTHY states about 52.70 percent, so zero continuation-event false triggers must not be interpreted as a globally sparse operational risk state.",
        "Important user-anchor misses are preserved: 2023-12-25, 2024-03-31 and 2025-01-18 were genuine primary exhaustion events but had no PRE14_7 WATCH/RISK hit. 2025-10-08 had a PRE14_7 hit but did not confirm RISK in PRE7_POST3.",
        "0045 is permanently closed. Dynamic-gross research is not eligible from this result. Any alternative trigger architecture requires a new result-informed research ID and fresh preregistration."
    ]
    record["evidence_scorecard"] = {
        "temporal_novelty": "RESEARCHER_EXPOSED_DEVELOPMENT_HISTORY_2022-12-10_TO_2026-08-02_NOT_INDEPENDENT_OOS",
        "statistical_sufficiency": "EIGHT_USABLE_MACRO_EPISODES_FIVE_TRUE_EPISODES_FIVE_CONTINUATION_EPISODES_SPECIFICITY_PASS_BUT_MULTIPLE_FROZEN_SENSITIVITY_AND_TIMING_GATES_FAIL",
        "governance_integrity": "HIGH_ATOMIC_PREREGISTRATION_TWO_PRE_RESULT_BASELINES_AFTER_STATIC_TEST_REPAIR_ONE_VALID_RESULT_RELEASE_NO_RETUNING_NO_RESULT_RERUN",
        "operational_realism": "STATE_TRIGGER_DIAGNOSTIC_ONLY_NO_GROSS_MAPPING_WATCH_RISK_OCCUPANCY_34_38_PERCENT_REQUIRES_REDESIGN_BEFORE_ANY_PORTFOLIO_TRANSLATION",
        "derived_confidence": "HIGH_CONFIDENCE_CURRENT_TRIGGER_CANDIDATE_IS_NOT_ELIGIBLE_FOR_DYNAMIC_GROSS_STAGE",
        "confidence_rule_ref": "research/brrk_exhaustion_trigger_0045/RUN_INTERFACE.json"
    }
    registry["records"][idx] = record
    write(registry_path, registry)


def finalize_current_state() -> None:
    path = ROOT / "docs/CURRENT_STATE.md"
    text = path.read_text(encoding="utf-8")
    old_line = "BRRK exhaustion trigger 0045     IMPLEMENTED / NOT RUN / CONTRACT VALIDATION PENDING"
    new_line = "BRRK exhaustion trigger 0045     FAIL / NO DYNAMIC-GROSS ELIGIBILITY / CLOSED"
    if old_line not in text:
        raise SystemExit("0045 executive line missing")
    text = text.replace(old_line, new_line, 1)

    old_heading = "## BRRK-EXHAUSTION-TRIGGER-0045 — implemented, still not run\n"
    if old_heading not in text:
        raise SystemExit("0045 section heading missing")
    start = text.index(old_heading)
    end = text.index("## Dashboard V5\n", start)
    section = """## BRRK-EXHAUSTION-TRIGGER-0045 — FAIL, closed

PR #158 froze one trigger candidate before any result. PR #159 implemented it and released exactly one valid result after a fully green pre-result baseline. The historical evidence remains researcher-exposed DEVELOPMENT evidence, not independent OOS.

Execution binding:

```text
pre-result green SHA                 669942a4bef3f32894f616b9b28e5001d81e82b9
pre-result failed workflow run       31390711467 / NO DIAGNOSTIC / NO RESULT
unique valid result workflow run     31391109057 / run number 2 / attempt 1
trigger head SHA                     f9d4fba80bd07b8a5c67c5c3928f9081332809c7
artifact id                          9063704951
artifact digest                      sha256:0f8cd31ca3905d798194387622456fc8e59cb786376e57a6c135bdb2867c9c04
full result SHA256                   06714848cbb8c812a655700c29362487fc9e77ef2638f57547c7340ee10a2682
source taxonomy reproduction         MATCHED 0043 EXACTLY
parent 0044                          PASS_TRIGGER_STAGE_ELIGIBLE
```

Frozen trigger result:

```text
primary TRUE PRE14_7 WATCH/RISK            3 / 9 = 33.3% FAIL
primary CONT PRE14_0 false WATCH/RISK       0 / 6 = 0.0%  PASS
primary TRUE episode hit                    2 / 5 = 40.0% FAIL
primary CONT episode false                  0 / 5 = 0.0%  PASS
severe TRUE PRE14_7 WATCH/RISK              3 / 7 = 42.9% FAIL
severe TRUE PRE7_POST3 RISK                 2 / 7 = 28.6% FAIL
primary CONT PRE14_POST3 RISK               0 / 6 = 0.0%  PASS
qualifying TRUE PRE21_0 transition onsets             0    FAIL
premature-clear gate                         no denominator FAIL
result_status                       FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY
```

The candidate is specific but too insensitive and too persistent for the requested one-to-two-week action trigger. WATCH plus RISK occupies about `34.38%` of the 1,332-session history, while non-HEALTHY states occupy about `52.70%`. The three primary TRUE PRE14_7 hits were `2024-06-05`, `2024-07-21`, and `2025-10-08`; important genuine exhaustion events `2023-12-25`, `2024-03-31`, and `2025-01-18` were missed. `2025-10-08` was WATCH/RISK in PRE14_7 but did not confirm RISK in PRE7_POST3.

The zero PRE21_0 onset count is binding negative evidence: captured events were already in WATCH/RISK before the frozen lead window, so this machine acts more like a sticky risk regime than a precise 7–14 day transition trigger. No same-ID threshold, persistence, onset-window, S2-only, CORE4-weight or hysteresis rescue is allowed.

0045 is permanently closed and **does not authorize a dynamic-gross stage**. 0044's underlying state-discrimination PASS remains valid; what failed is this particular state-to-trigger translation. Any alternative trigger architecture requires a fresh result-informed research ID before evaluation.

Canonical BRRK-0011, the winner lineage, Phase 6, signing, order submission and production authority remain unchanged.

"""
    text = text[:start] + section + text[end:]

    drift = "## Current drift assessment\n"
    if drift not in text:
        raise SystemExit("drift heading missing")
    prefix = text.split(drift, 1)[0]
    tail = """## Current drift assessment

`DRIFT_0`.

PR #159 closes a research-only trigger diagnostic with a binding FAIL. It adds immutable 0045 evidence and advances research lifecycle metadata only. No `execution/**`, canonical BRRK mathematics, Phase-6 observation, leverage/shorting, signing, order submission or production authority changes occur.

## Exact next task

1. Merge PR #159 only after the temporary 0045 one-shot/finalizer workflows are removed and final governance/no-drift/P3.2/Phase-6/handoff CI is green.
2. Preserve `BRRK-EXHAUSTION-TRIGGER-0045` as closed `FAIL_NO_DYNAMIC_GROSS_STAGE_ELIGIBILITY`; never rerun, retune or rescue it.
3. Do **not** create or run `BRRK-DYNAMIC-GROSS-0046` from this lineage; 0045 did not earn eligibility.
4. Preserve the distinction: 0044 confirms useful exhaustion-state discrimination, while 0045 shows this first absolute percentile/persistence/hysteresis trigger translation is inadequate.
5. Any future alternative trigger architecture must be a new result-informed preregistration, explicitly acknowledging 0045's sensitivity failure, sticky WATCH/RISK occupancy and zero PRE21_0 onset evidence before evaluation.
6. Continue Phase-6 future-only observation independently. All production, signing and order-submission authority remains false.
"""
    text = prefix + tail
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    finalize_registry()
    finalize_current_state()


if __name__ == "__main__":
    main()
