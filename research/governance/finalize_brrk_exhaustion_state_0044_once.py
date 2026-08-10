from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RID = "BRRK-EXHAUSTION-STATE-0044"
VALID_RUN = 31388103016
ARTIFACT_ID = 9062525981
ARTIFACT_DIGEST = "sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378"
FULL_RESULT_SHA = "687ff49d8db8baf54a1cfafcf8863c848011800b6c74689ab0534796ac86ff29"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def finalize_registry() -> None:
    path = ROOT / "config/research_registry.json"
    registry = load(path)
    prereg = load(ROOT / "research/brrk_exhaustion_state_0044/PREREGISTRATION.json")
    result = load(ROOT / "research/brrk_exhaustion_state_0044/PRIMARY_RESULT.json")
    execution = load(ROOT / "research/brrk_exhaustion_state_0044/EXECUTION.json")
    interface = load(ROOT / "research/brrk_exhaustion_state_0044/RUN_INTERFACE.json")

    if result.get("result_status") != "PASS_TRIGGER_STAGE_ELIGIBLE":
        raise SystemExit("unexpected immutable 0044 result status")
    if execution.get("execution_status") != "VALID_RESULT_RELEASED_AND_CLOSED":
        raise SystemExit("0044 execution is not closed")
    if interface.get("status") != "CLOSED_RESULT_USED":
        raise SystemExit("0044 run interface is not closed")
    if interface["valid_result_run"]["workflow_run_id"] != VALID_RUN:
        raise SystemExit("0044 valid run binding mismatch")
    if interface["valid_result_run"]["artifact_id"] != ARTIFACT_ID:
        raise SystemExit("0044 artifact id mismatch")
    if interface["valid_result_run"]["artifact_digest"] != ARTIFACT_DIGEST:
        raise SystemExit("0044 artifact digest mismatch")
    if interface["valid_result_run"]["full_result_sha256"] != FULL_RESULT_SHA:
        raise SystemExit("0044 full result hash mismatch")

    matches = [i for i, r in enumerate(registry["records"]) if r.get("research_id") == RID]
    if len(matches) != 1:
        raise SystemExit("0044 registry ownership is not unique")
    idx = matches[0]
    record = registry["records"][idx]
    if record.get("result_status") != "PREREGISTERED_NOT_RUN":
        raise SystemExit("0044 registry was already result-mutated")

    # The immutable preregistration remains unchanged on disk. Only lifecycle/result fields
    # in the canonical registry are advanced after the unique result release.
    for key in (
        "research_id", "research_family_id", "research_domain", "research_governance_version",
        "governance_mode", "objective_type", "created_at", "created_before_result", "question",
        "hypothesis", "hypothesis_origin", "economic_mechanism", "primary_target", "primary_metric",
        "secondary_metrics", "feature_families", "horizon", "universe", "development_dataset_refs",
        "validation_dataset_refs", "sealed_dataset_refs", "declared_variant_budget", "parameter_candidate_count",
        "stopping_rule", "success_criteria", "failure_criteria", "allowed_followup", "forbidden_followup",
        "researcher_decisions", "lineage_edges", "production_relevance", "production_authorized",
        "provenance_status", "governed_path_prefixes"
    ):
        if record.get(key) != prereg.get(key):
            raise SystemExit(f"frozen preregistration field drift before closeout: {key}")

    record["actual_variants_evaluated"] = 2
    complexity = record["research_process_complexity"]
    complexity["actual_parameter_candidates_evaluated"] = [
        "CORE4_EQUAL=S1_S2_S3_S4_FIXED_EQUAL_WEIGHT",
        "CORE5_VOLUME_DIAGNOSTIC=S1_S2_S3_S4_S5_FIXED_EQUAL_WEIGHT_SECONDARY_ONLY"
    ]
    record["result_status"] = "PASS_TRIGGER_STAGE_ELIGIBLE"
    record["failure_reason"] = None
    record["promotion_state"] = "NONE"
    record["evidence_refs"] = [
        "research/brrk_exhaustion_state_0044/PRIMARY_RESULT.json",
        "research/brrk_exhaustion_state_0044/EXECUTION.json",
        "research/brrk_exhaustion_state_0044/RUN_ONCE.marker"
    ]
    record["decision_refs"] = [
        "research/brrk_exhaustion_state_0044/RESULT.md",
        "research/brrk_exhaustion_state_0044/README.md",
        "docs/CURRENT_STATE.md"
    ]
    record["notes"] = list(prereg.get("notes", [])) + [
        "Pre-result implementation baseline f6fd1fc3425fefdc6bd024fa032a065accab7c6e passed Research governance core, final no-drift, P3.2 parity, Phase 6 shadow safety and standing repository contracts before any result was released.",
        "Workflow run 31387906469 failed before the diagnostic step because the temporary workflow file was correctly blocked by no_drift; it produced no artifact and is retained as a pre-result infrastructure failure, not a research result.",
        "Unique valid result release was workflow run 31388103016 run number 2 attempt 1 from head 9affc7572dd0feefb14fe41e2aea7904c3a132ba after proving only the temporary workflow differed from the green pre-result head and rerunning original no-drift against that exact baseline.",
        "The 0043 taxonomy reproduced exactly: 16 candidate peaks and fixed 10/15/20 percent panel label counts matched before 0044 scoring.",
        "CORE4 passed all frozen gates: primary 15 percent PRE14_7 cross-episode AUC 0.750, event AUC 0.7778, severe 20 percent PRE14_7 cross-episode AUC 0.750, LOEO minimum 0.6538 and median 0.7386 with seven usable macro episodes.",
        "Preserved negative evidence: secondary CORE5 with volume confirmation reduced cross-episode AUC from 0.750 to 0.6759 in PRE14_7 and from 0.7361 to 0.6065 in PRE7_0; S5 volume confirmation alone was 0.500 in primary PRE14_7.",
        "S2 trend disagreement was the strongest exposed state axis: cross-episode AUC 0.7440 in primary PRE14_7, 0.8929 in primary PRE7_0 and 0.8333 in severe PRE14_7. This may inform a new research ID but cannot be used to reweight or rescue 0044.",
        "PASS creates eligibility only for a separately preregistered trigger-design stage. 0044 is permanently closed to rerun, reweighting, feature rescue, threshold search, persistence search and gross mapping."
    ]
    record["evidence_scorecard"] = {
        "temporal_novelty": "RESEARCHER_EXPOSED_DEVELOPMENT_HISTORY_2022-12-10_TO_2026-08-02_NOT_INDEPENDENT_OOS",
        "statistical_sufficiency": "SEVEN_USABLE_MACRO_EPISODES_FIVE_TRUE_EPISODES_FOUR_CONTINUATION_EPISODES_PRIMARY_CROSS_EPISODE_AUC_0_750_LOEO_MIN_0_654_MEDIAN_0_739_ALL_FROZEN_GATES_PASS",
        "governance_integrity": "HIGH_ATOMIC_PREREGISTRATION_PRE_RESULT_GREEN_BASELINE_ONE_VALID_RESULT_RELEASE_SOURCE_REPRODUCTION_BEFORE_SCORING_NO_RETUNING_NO_RESULT_RERUN",
        "operational_realism": "SIGNAL_STATE_DIAGNOSTIC_ONLY_NO_TRIGGER_NO_PORTFOLIO_TRANSLATION_NO_TRANSACTION_COST_OR_EXECUTION_ECONOMICS",
        "derived_confidence": "MEDIUM_SIGNAL_STRUCTURE_PASS_TRIGGER_DESIGN_AND_FUTURE_VALIDATION_STILL_REQUIRED",
        "confidence_rule_ref": "research/brrk_exhaustion_state_0044/RUN_INTERFACE.json"
    }
    registry["records"][idx] = record
    write(path, registry)


def finalize_current_state() -> None:
    path = ROOT / "docs/CURRENT_STATE.md"
    text = path.read_text(encoding="utf-8")
    old = "BRRK exhaustion state 0044       IMPLEMENTED / NOT RUN / CONTRACT VALIDATION PENDING"
    new = "BRRK exhaustion state 0044       PASS / TRIGGER STAGE ELIGIBLE / CLOSED"
    if old not in text:
        raise SystemExit("0044 executive-state pre-result line missing")
    text = text.replace(old, new, 1)

    old_heading = "## BRRK-EXHAUSTION-STATE-0044 — implemented, still not run\n"
    if old_heading not in text:
        raise SystemExit("0044 pre-result heading missing")
    start = text.index(old_heading)
    end = text.index("## Dashboard V5\n", start)
    replacement = """## BRRK-EXHAUSTION-STATE-0044 — PASS, closed

PR #156 froze 0044 before result release. PR #157 implemented the frozen runner and released exactly one valid result after a fully green pre-result baseline. The historical evidence remains researcher-exposed DEVELOPMENT evidence, not independent OOS.

Execution binding:

```text
pre-result green SHA                 f6fd1fc3425fefdc6bd024fa032a065accab7c6e
pre-result failed workflow run       31387906469 / NO DIAGNOSTIC / NO RESULT
unique valid result workflow run     31388103016 / run number 2 / attempt 1
trigger head SHA                     9affc7572dd0feefb14fe41e2aea7904c3a132ba
artifact id                          9062525981
artifact digest                      sha256:b109b610710b00904c924680a63305579f3f3c4c799d539906e0853629ddd378
full result SHA256                   687ff49d8db8baf54a1cfafcf8863c848011800b6c74689ab0534796ac86ff29
source taxonomy reproduction         MATCHED 0043 EXACTLY
```

Frozen CORE4 gate result:

```text
usable macro episodes                         7   PASS
TRUE / CONTINUATION episode coverage        5 / 4 PASS
15% PRE14_7 cross-episode AUC              0.750 PASS
15% PRE14_7 event AUC                      0.778 PASS
20% PRE14_7 cross-episode AUC              0.750 PASS
LOEO minimum / median AUC                  0.654 / 0.739 PASS
result_status                              PASS_TRIGGER_STAGE_ELIGIBLE
```

Result-informed component evidence is preserved without same-ID reweighting. S2 trend disagreement was strongest (`0.744` cross-episode AUC at PRE14_7, `0.893` at PRE7_0, `0.833` for severe PRE14_7). Secondary S5 volume confirmation was negative evidence: adding it reduced CORE4 cross-episode AUC from `0.750` to `0.676` at PRE14_7 and from `0.736` to `0.606` at PRE7_0; S5 alone was `0.500` at primary PRE14_7.

0044 therefore establishes that a frozen low-dimensional exhaustion state retains useful advance discrimination after macro-episode dependence control. It **does not** define a trading trigger or gross-risk response. `RUN_ONCE.marker` is permanent and 0044 may not be rerun, reweighted, pruned, rescued or used for same-ID threshold/gross search.

The only authorized research continuation is a new, separately preregistered trigger-stage ID. Canonical BRRK-0011, the 40/60 winner lineage, Phase 6 and all production/security authority remain unchanged.

"""
    text = text[:start] + replacement + text[end:]

    drift = "## Current drift assessment\n"
    if drift not in text:
        raise SystemExit("CURRENT_STATE drift heading missing")
    prefix = text.split(drift, 1)[0]
    tail = """## Current drift assessment

`DRIFT_0`.

PR #157 closes a research-only state diagnostic. It adds immutable 0044 evidence and updates research lifecycle metadata only. No `execution/**`, canonical BRRK mathematics, Phase-6 observation, leverage/shorting, signing, order submission or production authority changes occur.

## Exact next task

1. Merge PR #157 only after the temporary 0044 execution/finalizer workflows are removed and final governance/no-drift/P3.2/Phase-6/handoff CI is green.
2. Preserve `BRRK-EXHAUSTION-STATE-0044` as closed `PASS_TRIGGER_STAGE_ELIGIBLE`; never rerun or retune it.
3. If continuing, preregister a new `BRRK-EXHAUSTION-TRIGGER` research ID before defining HEALTHY/DECELERATION/WATCH/RISK/RECOVERY transitions, persistence, thresholds or asymmetric re-entry rules.
4. Treat S2 strength and S5 negative volume evidence as result-informed DEVELOPMENT inputs only; do not retrospectively modify CORE4.
5. Do not run dynamic-gross portfolio economics until a separately frozen trigger stage passes. Phase 6 continues independently and all production/signing/order-submission authority remains false.
"""
    text = prefix + tail
    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    finalize_registry()
    finalize_current_state()


if __name__ == "__main__":
    main()
