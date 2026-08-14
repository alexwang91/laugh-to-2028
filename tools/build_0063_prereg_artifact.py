from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

RID = "BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063"
OWNER_SHA = "aeff95faa60f5e7f5c209c143a329e7e45545286"
DESIGN_SHA = "e1ac320e092e554c283ef6b88aaaa5f65aaf61ab"
CAPTURE_RUN = 31757177489
CAPTURE_ARTIFACT_ID = 9203157766
RAW_SHA256 = "4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879"
RAW_GIT_BLOB = "71d50e26f8a9afb6bcb88401d20b97d5fb0a891a"
DATASET_SLICE = "BRRK-IDLE-CASH-SWEEP-0063-DTB3-HIST-V1"
BASELINE_SLICE = "BRRK-WINNER-0001-CANONICAL-HIST-V1"
FORMAL = Path("research/brrk_idle_cash_sweep_robustness_0063")
CAPTURE = Path("/tmp/0063-capture")
OUT = Path("/tmp/0063-prereg-artifact")
PKG = OUT / "package"


def canon(x: object) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def chash(x: object) -> str:
    return hashlib.sha256(canon(x)).hexdigest()


def dump(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def prereg(raw_blob: str, capture_blob: str) -> dict:
    return {
        "schema_version": 1,
        "research_id": RID,
        "stage": "NUMERICAL_DATA_PREREGISTRATION_FROZEN_NOT_RUN",
        "design_ref": "research/governance/BRRK_IDLE_CASH_SWEEP_ROBUSTNESS_0063_DESIGN_FREEZE_2026-08-14.md",
        "design_merge_sha": DESIGN_SHA,
        "owner_first_commit_sha": OWNER_SHA,
        "hypothesis_origin": "RESULT_INFORMED_DEVELOPMENT_REPLICATION_OF_F27_R2_NOT_INDEPENDENT_OOS",
        "scientific_scope": "Mechanical idle-cash carry overlay on the unchanged committed BRRK-0011 path; no signal, target, risk-asset weight, gross, timing, re-entry, leverage or short modification.",
        "prior_exposure": {
            "F27_R2_status": "EXPOSED_DEVELOPMENT_MOTIVATION_ONLY",
            "F27_R2_ref": "research/results/idle_cash_credit_0027r2.json",
            "F27_R2_may_satisfy_0063_gate": False,
            "independent_oos": False
        },
        "baseline_contract": {
            "equity_path": "research/results/pit_disp_0015/daily_equity.csv",
            "equity_git_blob_sha": "82c87f8cb0ff01c728ffd3b717fff17cf5a364f2",
            "weights_path": "research/results/pit_disp_0015/daily_weights.csv",
            "weights_git_blob_sha": "2f6c8d3a8c25d3cafeaa0128f1c425dac248370b",
            "variant": "BRRK0011_BASELINE",
            "weight_prefix": "BRRK0011_BASELINE__",
            "known_starting_capital_usd": 10000.0,
            "expected_start": "2022-12-10",
            "expected_end": "2026-08-02",
            "expected_observations": 1332,
            "expected_calendar_span_days": 1331,
            "calendar_span_cagr_anchor": 0.6516609785339953,
            "calendar_span_cagr_abs_tolerance": 1e-6,
            "final_10k_anchor": 62247.38231294191,
            "final_10k_abs_tolerance": 1e-6,
            "return_reconstruction": "pct_change; first_return=first_equity/10000-1",
            "gross_formula": "sum(abs(BRRK0011_BASELINE__* weights), axis=1)",
            "gross_upper_bound": 1.000001,
            "idle_cash_formula": "clip(1-gross,0,1)",
            "strategy_refit_allowed": False,
            "weight_or_gross_change_allowed": False
        },
        "dtb3_contract": {
            "dataset_slice_id": DATASET_SLICE,
            "raw_path": str(FORMAL / "DTB3_RAW.csv"),
            "raw_git_blob_sha": raw_blob,
            "raw_sha256": RAW_SHA256,
            "capture_report_path": str(FORMAL / "CAPTURE_REPORT.json"),
            "capture_report_git_blob_sha": capture_blob,
            "capture_workflow_run": CAPTURE_RUN,
            "capture_artifact_id": CAPTURE_ARTIFACT_ID,
            "source_provider": "FRED",
            "series_id": "DTB3",
            "requested_start": "2022-11-30",
            "requested_end": "2026-08-02",
            "first_valid_date": "2022-11-30",
            "last_valid_date": "2026-07-31",
            "raw_row_count": 958,
            "valid_observation_count": 917,
            "scientific_run_network_fetch_allowed": False,
            "replacement_allowed": False,
            "independent_oos": False,
            "bank_discount_to_investment_basis": "d=DTB3_percent/100; BEY=365*d/(360-91*d)",
            "daily_return": "BEY/365",
            "calendarization": "reindex_to_exact_baseline_dates_then_causal_forward_fill_from_latest_valid_source_observation",
            "backfill_inside_strategy_window_allowed": False
        },
        "candidate_geometry": {
            "yield_realization": [0.25, 0.50, 0.75, 1.00],
            "sweep_friction_bps": [0, 5, 10, 20],
            "cell_count": 16,
            "primary_cell": {"yield_realization": 0.50, "sweep_friction_bps": 10},
            "core_stress_cells": {
                "yield_realization": [0.50, 0.75, 1.00],
                "sweep_friction_bps": [0, 5, 10],
                "cell_count": 9
            },
            "all_cells_losslessly_reported": True,
            "historical_argmax_authority": False,
            "multiple_testing_note": "Exactly one prospectively designated inferential primary hypothesis exists. The other 15 cells are deterministic robustness stresses and cannot promote independently."
        },
        "candidate_return_formula": "r_candidate[t]=r_baseline[t]+idle_cash[t]*yield_realization*rf_daily[t]-(sweep_friction_bps/10000)*abs(idle_cash[t]-idle_cash[t-1])",
        "first_observation_sweep_turnover": 0.0,
        "candidate_return_validity": "every daily return must be finite and strictly greater than -1",
        "metric_contract": {
            "calendar_year_days": 365.25,
            "cagr": "end_multiple**(1/((last_date-first_date).days/365.25))-1",
            "terminal_wealth": "10000*prod(1+r)",
            "max_drawdown": "min(nav/cummax(nav)-1)",
            "relative_log_increment": "d[t]=log1p(r_candidate[t])-log1p(r_baseline[t])",
            "relative_terminal_log_growth": "sum(d[t])",
            "primary_priority": ["net_terminal_wealth", "net_CAGR", "max_drawdown", "temporal_recurrence", "dependence_robustness", "stress_robustness"]
        },
        "common_support": {
            "exact_baseline_dates_required": True,
            "minimum_observations": 1332,
            "missing_preceding_DTB3_policy": "G0_DATA_IDENTITY_FAIL",
            "baseline_date_drop_allowed": False
        },
        "chronological_blocks": {
            "count": 4,
            "construction": "after common-support filtering, split ordered rows into count-balanced contiguous blocks; remainder rows allocated one each to earlier blocks",
            "block_statistic": "sum(relative_log_increment)",
            "pass_rule": "at least 3 of 4 block statistics strictly > 0"
        },
        "moving_block_bootstrap": {
            "series": "primary-cell relative_log_increment d[t]",
            "aligned": True,
            "circular": False,
            "overlapping_source_blocks": True,
            "block_length_sessions": 60,
            "replicates": 4000,
            "seed": 630063,
            "sampling": "for each replicate draw start indices uniformly with replacement from integers 0..N-L; concatenate contiguous length-L blocks until length>=N; truncate to N",
            "observed_statistic": "mu_obs=mean(d)",
            "bootstrap_statistic": "mu_b=mean(resampled_d)",
            "error": "mu_obs-mu_b",
            "quantile": "Type-7 linear 95th percentile of bootstrap errors",
            "lcb": "mu_obs-q95",
            "pass_rule": "LCB strictly > 0",
            "rerank_or_refit_in_resample": False
        },
        "gate_order": [
            "G0_CONTRACT_AND_DATA_IDENTITY",
            "G1_BASELINE_RECONSTRUCTION_AND_SUPPORT",
            "G2_PRIMARY_NET_TERMINAL_WEALTH_AND_CAGR",
            "G3_PRIMARY_MAX_DRAWDOWN_NONINFERIORITY",
            "G4_TEMPORAL_RECURRENCE",
            "G5_DEPENDENCE_AWARE_MBB_LCB",
            "G6_CORE_STRESS_ROBUSTNESS"
        ],
        "gates": {
            "G0_CONTRACT_AND_DATA_IDENTITY": "all pinned Git blobs/SHA256, capture metadata, no-network/no-replacement rules and finite schemas match exactly",
            "G1_BASELINE_RECONSTRUCTION_AND_SUPPORT": "exact window/1332 observations, CAGR anchor within 1e-6, final_10k anchor within 1e-6, gross<=1.000001, and every baseline date has a causally available DTB3 rate",
            "G2_PRIMARY_NET_TERMINAL_WEALTH_AND_CAGR": "primary terminal wealth > baseline terminal wealth AND primary CAGR > baseline CAGR",
            "G3_PRIMARY_MAX_DRAWDOWN_NONINFERIORITY": "primary MDD >= baseline MDD - 1e-12",
            "G4_TEMPORAL_RECURRENCE": "at least 3/4 chronological block relative log-growth sums strictly >0",
            "G5_DEPENDENCE_AWARE_MBB_LCB": "primary moving-block-bootstrap one-sided LCB strictly >0",
            "G6_CORE_STRESS_ROBUSTNESS": "all 9 core stress cells have relative terminal log-growth strictly >0"
        },
        "classification_precedence": [
            "INVALID_EXECUTION",
            "MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY",
            "FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS",
            "FAIL_IDLE_CASH_SWEEP_DRAWDOWN",
            "FAIL_IDLE_CASH_SWEEP_TEMPORAL_ROBUSTNESS",
            "FAIL_IDLE_CASH_SWEEP_DEPENDENCE_ROBUSTNESS",
            "FAIL_IDLE_CASH_SWEEP_STRESS_ROBUSTNESS",
            "PASS_IDLE_CASH_SWEEP_ROBUSTNESS"
        ],
        "classification_rules": {
            "INVALID_EXECUTION": "implementation, persistence, exactly-once, frozen-contract or boundary violation",
            "MEASUREMENT_INCONCLUSIVE_DATA_IDENTITY": "G0 or G1 cannot establish frozen input identity/support; no economic FAIL conclusion",
            "FAIL_IDLE_CASH_SWEEP_PRIMARY_ECONOMICS": "G0-G1 pass; G2 fails",
            "FAIL_IDLE_CASH_SWEEP_DRAWDOWN": "G0-G2 pass; G3 fails",
            "FAIL_IDLE_CASH_SWEEP_TEMPORAL_ROBUSTNESS": "G0-G3 pass; G4 fails",
            "FAIL_IDLE_CASH_SWEEP_DEPENDENCE_ROBUSTNESS": "G0-G4 pass; G5 fails",
            "FAIL_IDLE_CASH_SWEEP_STRESS_ROBUSTNESS": "G0-G5 pass; G6 fails",
            "PASS_IDLE_CASH_SWEEP_ROBUSTNESS": "G0 through G6 all pass"
        },
        "execution_budget": {
            "historical_attempts": 1,
            "scientific_engine_calls": 1,
            "frozen_stress_cells_inside_engine_call": 16,
            "actual_variants_evaluated_before_execution": 0,
            "same_id_rerun_allowed": False,
            "same_id_retune_allowed": False,
            "same_id_rescue_allowed": False,
            "marker_only_recovery": "allowed only when complete PRIMARY_RESULT.json and EXECUTION.json are already durably persisted and final marker alone is missing"
        },
        "forbidden": [
            "network fetch during scientific execution",
            "DTB3 replacement or alternate rate series",
            "yield/friction grid or primary-cell change",
            "BRRK-0011 signal/target/risk-asset weight/gross/window change",
            "cash timing or re-entry rule",
            "favorable-block or stress-cell pruning",
            "bootstrap/gate relaxation after outcome access",
            "same-ID rerun/recompute/retune/rescue",
            "production/signature/order authority"
        ],
        "authorization": {"canonical_BRRK_0011": "NO_CHANGE", "Phase_6": "NO_CHANGE", "production_authorized": False, "signature_authorized": False, "order_submission_authorized": False}
    }


def dataset_decl(raw_blob: str, capture_blob: str) -> dict:
    return {
        "schema_version": 1,
        "research_id": RID,
        "development_only": True,
        "independent_oos": False,
        "baseline": {
            "dataset_slice_id": BASELINE_SLICE,
            "equity_path": "research/results/pit_disp_0015/daily_equity.csv",
            "equity_git_blob_sha": "82c87f8cb0ff01c728ffd3b717fff17cf5a364f2",
            "weights_path": "research/results/pit_disp_0015/daily_weights.csv",
            "weights_git_blob_sha": "2f6c8d3a8c25d3cafeaa0128f1c425dac248370b",
            "variant": "BRRK0011_BASELINE",
            "expected_window": ["2022-12-10", "2026-08-02"],
            "replacement_allowed": False
        },
        "cash_rate": {
            "dataset_slice_id": DATASET_SLICE,
            "path": str(FORMAL / "DTB3_RAW.csv"),
            "git_blob_sha": raw_blob,
            "payload_sha256": RAW_SHA256,
            "capture_report_path": str(FORMAL / "CAPTURE_REPORT.json"),
            "capture_report_git_blob_sha": capture_blob,
            "capture_run": CAPTURE_RUN,
            "capture_artifact_id": CAPTURE_ARTIFACT_ID,
            "source": "FRED DTB3",
            "first_valid_date": "2022-11-30",
            "last_valid_date": "2026-07-31",
            "network_fetch_allowed": False,
            "replacement_allowed": False
        },
        "exposure_status": "RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS",
        "post_capture_substitution_allowed": False
    }


def current_state() -> str:
    return """# BRRK Current State

Last updated: 2026-08-14

Authoritative repository: `alexwang91/laugh-to-2028`.
Merged DESIGN: `e1ac320e092e554c283ef6b88aaaa5f65aaf61ab`.
Active branch: `research/0063-prereg-v1`.
The pre-0063 long-form handoff remains preserved by Git history at blob `dcc655864caf0a62a5123b38700047b77920e546`.

## Required closed-research anchors

BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic
workflow run                         31381953131 / attempt 1
7–14 day exhaustion-ranking signal appears feasible
ID 0043 is closed against result-informed pruning, reweighting, threshold rescue

## Research state

0062 = `FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION / CLOSED`; same-ID rerun/retune/rescue forbidden.
0063 = `PREREGISTERED / IMPLEMENTATION ABSENT / CONTROLLED BOUNDARY ABSENT / NOT RUN`.
Research ID = `BRRK-IDLE-CASH-SWEEP-ROBUSTNESS-0063`.
Owner-first commit = `aeff95faa60f5e7f5c209c143a329e7e45545286`.
Frozen DTB3 raw SHA256 = `4d8aee67dbd528ce38ff8482e9bb02dd5ccf2c6cd461f606fe90007151ab6879`.
Frozen yield-realization grid = 25%, 50%, 75%, 100%.
Frozen sweep-friction grid = 0, 5, 10, 20 bps.
Primary conservative cell = 50% realization / 10 bps.
MBB = L60 / 4000 reps / seed 630063 / aligned non-circular moving blocks.
Historical 0063 candidate economics = NOT COMPUTED.
Actual historical variants evaluated = 0.
RUN_ATTEMPT.marker = ABSENT.

## No-drift authority

production gross cap = 1.0
production_authorized_components = []
production_authorized = false
signature_authorized = false
order_submission_authorized = false

Canonical BRRK-0011 = NO CHANGE.
Phase 6 = NO CHANGE.

## Exact next step

After preregistration merges through fresh standing CI, implement the frozen 0063 formulas using synthetic/toy/contract tests only. Do not read real BRRK historical values or compute 0063 candidate economics until implementation and controlled-execution boundary are separately merged.
"""


def main() -> None:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if head != OWNER_SHA:
        raise SystemExit(f"expected owner-only HEAD {OWNER_SHA}, got {head}")
    raw = (CAPTURE / "DTB3_RAW.csv").read_bytes()
    report_bytes = (CAPTURE / "CAPTURE_REPORT.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != RAW_SHA256:
        raise SystemExit("DTB3 SHA256 mismatch")
    raw_blob = subprocess.check_output(["git", "hash-object", str(CAPTURE / "DTB3_RAW.csv")], text=True).strip()
    if raw_blob != RAW_GIT_BLOB:
        raise SystemExit(f"DTB3 git blob mismatch: {raw_blob}")
    report = json.loads(report_bytes)
    required_false = ["candidate_economics_computed", "baseline_equity_read", "baseline_weights_read"]
    if any(report.get(k) is not False for k in required_false):
        raise SystemExit("capture report violates result-blind invariants")
    if report.get("replacement_allowed") is not False or report.get("raw_sha256") != RAW_SHA256:
        raise SystemExit("capture identity/replacement invariant failed")

    # Formal files. This builder intentionally never opens the baseline equity or weights files.
    FORMAL.mkdir(parents=True, exist_ok=True)
    (FORMAL / "DTB3_RAW.csv").write_bytes(raw)
    (FORMAL / "CAPTURE_REPORT.json").write_bytes(report_bytes)
    capture_blob = subprocess.check_output(["git", "hash-object", str(FORMAL / "CAPTURE_REPORT.json")], text=True).strip()
    dump(FORMAL / "PREREGISTRATION.json", prereg(raw_blob, capture_blob))
    dump(FORMAL / "DATASET_DECLARATION.json", dataset_decl(raw_blob, capture_blob))

    # Register only the newly frozen raw cash-rate slice; preserve every existing record byte-semantically.
    dpath = Path("config/dataset_exposure_registry.json")
    dreg = json.loads(dpath.read_text(encoding="utf-8"))
    before_slices = [chash(x) for x in dreg["dataset_slices"]]
    before_events = [chash(x) for x in dreg["exposure_events"]]
    if any(x.get("dataset_slice_id") == DATASET_SLICE for x in dreg["dataset_slices"]):
        raise SystemExit("0063 DTB3 slice already exists in owner base")
    dreg["dataset_slices"].append({
        "dataset_slice_id": DATASET_SLICE,
        "dataset_id": "FRED-DTB3-3M-TBILL-BANK-DISCOUNT",
        "dataset_version": "first-valid-capture-20260814-sha256-" + RAW_SHA256,
        "source": "FRED_DTB3_RESULT_BLIND_FIRST_VALID_CAPTURE_RUN_31757177489",
        "assets": ["USD_CASH"],
        "fields": ["DTB3"],
        "resolution": "FRED_BUSINESS_DAY_RAW",
        "start": "2022-11-30T00:00:00Z",
        "end": "2026-07-31T00:00:00Z",
        "transformation": "IDENTITY_RAW_CAPTURE; 0063 downstream conversion to investment basis and causal daily forward-fill is frozen in PREREGISTRATION.json",
        "pit_publication_semantics": "PUBLIC HISTORICAL FRED OBSERVATIONS CAPTURED RESULT-BLIND AFTER 0063 DESIGN AND BEFORE ANY 0063 CANDIDATE ECONOMICS; captured payload is immutable for this ID; no later replacement or revision may be substituted",
        "data_budget": "DEVELOPMENT",
        "contamination_state": "RESEARCHER_EXPOSED_HISTORY",
        "consumed": True,
        "researcher_exposed_history": True,
        "provenance_status": "FACT",
        "evidence_refs": [str(FORMAL / "CAPTURE_REPORT.json"), str(FORMAL / "DTB3_RAW.csv")]
    })
    if [chash(x) for x in dreg["dataset_slices"][:-1]] != before_slices or [chash(x) for x in dreg["exposure_events"]] != before_events:
        raise SystemExit("preexisting dataset registry mutation detected")
    dump(dpath, dreg)

    Path("docs/CURRENT_STATE.md").write_text(current_state(), encoding="utf-8")
    if (FORMAL / "RUN_ATTEMPT.marker").exists() or (FORMAL / "PRIMARY_RESULT.json").exists():
        raise SystemExit("result/attempt artifact present during preregistration")

    subprocess.run(["python", "-m", "research.governance.validate"], check=True)
    subprocess.run(["python", "-m", "research.governance.enforce_future", "--base", OWNER_SHA], check=True)

    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    expected = sorted([
        "config/dataset_exposure_registry.json",
        "docs/CURRENT_STATE.md",
        str(FORMAL / "CAPTURE_REPORT.json"),
        str(FORMAL / "DATASET_DECLARATION.json"),
        str(FORMAL / "DTB3_RAW.csv"),
        str(FORMAL / "PREREGISTRATION.json")
    ])
    if sorted(changed) != expected:
        raise SystemExit(f"unexpected prereg diff: {changed}")

    if OUT.exists(): shutil.rmtree(OUT)
    PKG.mkdir(parents=True)
    for rel in expected:
        src = Path(rel); dst = PKG / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    build_report = {
        "schema_version": 1,
        "research_id": RID,
        "owner_first_commit_sha": OWNER_SHA,
        "design_merge_sha": DESIGN_SHA,
        "dtb3_raw_sha256": RAW_SHA256,
        "dtb3_raw_git_blob_sha": raw_blob,
        "capture_report_git_blob_sha": capture_blob,
        "candidate_economics_computed": False,
        "baseline_equity_read": False,
        "baseline_weights_read": False,
        "historical_variants_evaluated": 0,
        "run_attempt_marker_absent": not (FORMAL / "RUN_ATTEMPT.marker").exists(),
        "expected_changed_paths": expected,
        "dataset_preexisting_slices_unchanged": True,
        "dataset_preexisting_events_unchanged": True,
        "governance_validate": "PASS",
        "future_enforcement": "PASS"
    }
    dump(OUT / "BUILD_REPORT.json", build_report)
    print(json.dumps(build_report, sort_keys=True))


if __name__ == "__main__":
    main()
