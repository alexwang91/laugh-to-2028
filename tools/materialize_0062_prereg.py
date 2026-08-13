from __future__ import annotations

import json
import subprocess
from pathlib import Path

RID = "BRRK-BTC-RISK-SIGNAL-ATLAS-0062"
ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "config/research_registry.json"
BASE = "research/brrk_btc_risk_signal_atlas_0062"
DESIGN = "research/governance/BRRK_BTC_RISK_SIGNAL_ATLAS_0062_DESIGN_FREEZE_2026-08-13.md"
MARKET = "research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json"
MARKET_BLOB = "64ebf5c6deaf3f34dbeac715378f196ff0f4fafe"
MARKET_PAYLOAD_SHA = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
SOURCE_LOADER_BLOB = "059b55961e279dab41ba29b5b017de0922e4f33c"
DESIGN_MERGE = "aa3fa9c1814c4113918e0d012636db44a1f89659"
CREATED_AT = "2026-08-13T22:10:00Z"


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def candidate_manifest() -> dict:
    # Every cell below is frozen before any 0062 outcome read. Larger oriented score means more BTC risk.
    return {
        "F01_TREND_LEVEL_DIRECTION": {
            "classes": {
                "NEG_LOG_PRICE_OVER_EMA": {"lookbacks": [10, 20, 40, 80, 160]},
                "NEG_ROLLING_LOG_PRICE_SLOPE_TSTAT": {"lookbacks": [10, 20, 40, 80]},
            }, "candidate_count": 9,
        },
        "F02_TREND_SPREAD_DISAGREEMENT": {
            "classes": {"NEG_LOG_EMA_FAST_OVER_SLOW": {"pairs": [[5,20],[10,40],[20,80],[40,160]]}},
            "candidate_count": 4,
        },
        "F03_TREND_ACCELERATION_DECELERATION": {
            "classes": {
                "NEG_PPO_HISTOGRAM_LEVEL": {"fast_slow_signal": [[6,18,5],[8,24,6],[12,26,9],[16,48,12]]},
                "NEG_PPO_HISTOGRAM_5D_CHANGE": {"fast_slow_signal": [[6,18,5],[8,24,6],[12,26,9],[16,48,12]]},
            }, "candidate_count": 8,
        },
        "F04_TREND_CROSS_TRANSITION": {
            "classes": {
                "BEARISH_PPO_ZERO_CROSS_RECENCY": {"fast_slow_signal": [[6,18,5],[8,24,6],[12,26,9],[16,48,12]], "half_lives": [5,20]},
                "BEARISH_PRICE_EMA_CROSS_RECENCY": {"ema_lookbacks": [10,20,40,80], "half_lives": [5,20]},
            }, "candidate_count": 16,
        },
        "F05_VOL_ADJUSTED_TREND_GUARDS": {
            "classes": {
                "SUPERTREND_BEARISH_DISTANCE": {"atr_lookbacks": [7,10,14,21], "multipliers": [1.5,2.0,3.0,4.0]},
                "CHANDELIER_BEARISH_DISTANCE": {"lookbacks": [10,20,40], "atr_multipliers": [2.0,3.0,4.0]},
            }, "candidate_count": 25,
        },
        "F06_MOMENTUM_LEVEL": {
            "classes": {
                "NEG_RSI_CENTERED": {"lookbacks": [5,7,10,14,21,28]},
                "NEG_LOG_ROC": {"lookbacks": [5,10,20,40]},
                "NEG_CMO": {"lookbacks": [5,10,20,40]},
            }, "candidate_count": 14,
        },
        "F07_OVERBOUGHT_STRETCH": {
            "classes": {
                "RSI_UPPER_TAIL": {"lookbacks": [5,7,10,14,21,28]},
                "STOCHASTIC_UPPER_TAIL": {"lookbacks": [7,14,28]},
                "WILLIAMS_R_UPPER_TAIL": {"lookbacks": [7,14,28]},
                "BOLLINGER_PERCENT_B_UPPER_TAIL": {"lookbacks": [10,20,40], "std_multiplier": 2.0},
            }, "candidate_count": 15,
        },
        "F08_BEARISH_DIVERGENCE_EXHAUSTION": {
            "classes": {
                "PRICE_MINUS_RSI_MOMENTUM_DIVERGENCE": {"lookbacks": [10,20,40,80]},
                "PRICE_MINUS_PPO_MOMENTUM_DIVERGENCE": {"fast_slow_signal": [[6,18,5],[8,24,6],[12,26,9],[16,48,12]]},
            }, "candidate_count": 8,
        },
        "F09_BREAKDOWN_FAILED_BREAK_STRUCTURE": {
            "classes": {
                "NEG_DONCHIAN_RANGE_LOCATION": {"lookbacks": [10,20,40,80]},
                "LOG_RECENT_HIGH_OVER_CLOSE": {"lookbacks": [20,60,120]},
                "FAILED_UP_BREAK_RETURN_INSIDE_RANGE": {"lookbacks": [10,20,40,80]},
            }, "candidate_count": 11,
        },
        "F10_VOLATILITY_REGIME": {
            "classes": {
                "LOG_RV_SHORT_OVER_LONG": {"pairs": [[5,20],[10,40],[20,80],[40,160]]},
                "ATR_OVER_CLOSE": {"lookbacks": [7,14,28]},
                "VOL_OF_VOL": {"rv_lookback": 10, "outer_lookbacks": [10,20,40]},
            }, "candidate_count": 10,
        },
        "F11_DOWNSIDE_ASYMMETRY_TAIL": {
            "classes": {
                "LOG_DOWNSIDE_OVER_UPSIDE_SEMIVOL": {"lookbacks": [10,20,40]},
                "NEGATIVE_RETURN_SHARE": {"lookbacks": [10,20,40]},
                "DRAWDOWN_VELOCITY": {"lookbacks": [5,10,20]},
            }, "candidate_count": 9,
        },
        "F12_VOLUME_FLOW_CONFIRMATION": {
            "classes": {
                "LOG_VOLUME_SHORT_OVER_LONG": {"pairs": [[5,20],[10,40],[20,80],[40,160]]},
                "NEG_OBV_SLOPE": {"lookbacks": [5,10,20,40]},
                "NEG_MFI_CENTERED": {"lookbacks": [7,14,28]},
                "NEG_CMF": {"lookbacks": [10,20,40]},
            }, "candidate_count": 14,
        },
        "F13_CROSS_CRYPTO_BREADTH": {
            "classes": {
                "ONE_MINUS_FRACTION_ABOVE_EMA": {"assets": ["BTC","ETH","SOL"], "lookbacks": [10,20,40,80]},
                "NEG_BREADTH_MOMENTUM": {"assets": ["BTC","ETH","SOL"], "lookbacks": [5,10,20]},
                "RETURN_DISPERSION": {"assets": ["BTC","ETH","SOL"], "lookbacks": [5,10,20]},
                "CORRELATION_CONCENTRATION": {"assets": ["BTC","ETH","SOL"], "lookbacks": [10,20,40]},
            }, "candidate_count": 13,
        },
        "F14_RELATIVE_CRYPTO_LEADERSHIP": {
            "classes": {
                "NEG_ETH_BTC_LOG_MOMENTUM": {"lookbacks": [5,10,20,40,80]},
                "NEG_SOL_BTC_LOG_MOMENTUM": {"lookbacks": [5,10,20,40,80]},
                "BETA_WEAKNESS_BREADTH": {"assets": ["ETH","SOL"], "lookbacks": [5,10,20,40,80]},
            }, "candidate_count": 15,
        },
        "F21_SEQUENTIAL_CHANGE_DETECTION": {
            "classes": {"NEG_STANDARDIZED_RETURN_MEAN_SHIFT": {"short_long_pairs": [[5,20],[10,40],[20,80],[40,160]]}},
            "candidate_count": 4,
        },
        "F23_MULTI_TIMESCALE_DISAGREEMENT": {
            "classes": {"FAST_BEARISH_MINUS_SLOW_BEARISH_TREND": {"fast_slow_pairs": [[5,20],[10,40],[20,80],[40,160]]}},
            "candidate_count": 4,
        },
        "F24_FIXED_LOW_ORDER_INTERACTIONS": {
            "classes": {"POSITIVE_PART_PRODUCT": {"pairs": [
                ["F01_TREND_LEVEL_DIRECTION","F10_VOLATILITY_REGIME"],
                ["F06_MOMENTUM_LEVEL","F10_VOLATILITY_REGIME"],
                ["F13_CROSS_CRYPTO_BREADTH","F10_VOLATILITY_REGIME"],
                ["F14_RELATIVE_CRYPTO_LEADERSHIP","F01_TREND_LEVEL_DIRECTION"],
                ["F05_VOL_ADJUSTED_TREND_GUARDS","F10_VOLATILITY_REGIME"],
                ["F08_BEARISH_DIVERGENCE_EXHAUSTION","F07_OVERBOUGHT_STRETCH"],
            ]}}, "candidate_count": 6,
        },
    }


def make_prereg() -> dict:
    manifest = candidate_manifest()
    assert sum(v["candidate_count"] for v in manifest.values()) == 185
    directional = [
        "F01_TREND_LEVEL_DIRECTION","F02_TREND_SPREAD_DISAGREEMENT","F03_TREND_ACCELERATION_DECELERATION",
        "F04_TREND_CROSS_TRANSITION","F05_VOL_ADJUSTED_TREND_GUARDS","F06_MOMENTUM_LEVEL",
        "F07_OVERBOUGHT_STRETCH","F08_BEARISH_DIVERGENCE_EXHAUSTION","F09_BREAKDOWN_FAILED_BREAK_STRUCTURE",
        "F12_VOLUME_FLOW_CONFIRMATION","F13_CROSS_CRYPTO_BREADTH","F14_RELATIVE_CRYPTO_LEADERSHIP",
        "F21_SEQUENTIAL_CHANGE_DETECTION","F23_MULTI_TIMESCALE_DISAGREEMENT","F24_FIXED_LOW_ORDER_INTERACTIONS",
    ]
    risk = ["F10_VOLATILITY_REGIME","F11_DOWNSIDE_ASYMMETRY_TAIL"]
    return {
        "schema_version": 1,
        "research_id": RID,
        "stage": "NUMERICAL_DATA_PREREGISTRATION_FROZEN_NOT_RUN",
        "design_ref": DESIGN,
        "design_merge_sha": DESIGN_MERGE,
        "hypothesis_origin": "RESULT_INFORMED_DEVELOPMENT_MECHANISM_FORMATION_NOT_INDEPENDENT_OOS",
        "scientific_scope": "Tier-A market-internal family-level information atlas only; no trading rule, gross map, re-entry optimization, strategy NAV or portfolio economics.",
        "dataset": {
            "tier": "A_EXISTING_IMMUTABLE_MARKET_INTERNAL",
            "path": MARKET,
            "git_blob_sha": MARKET_BLOB,
            "payload_sha256": MARKET_PAYLOAD_SHA,
            "dataset_slice_id": "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1",
            "history_start": "2020-08-11T00:00:00Z",
            "history_end": "2026-08-02T00:00:00Z",
            "common_rows": 2183,
            "resolution": "1D",
            "assets_exact": ["BTC","ETH","SOL"],
            "fields_exact": ["open","high","low","close","volume","quote_volume","trades"],
            "source_loader_module": "research.brrk_beta_handoff_0047.engine",
            "source_loader_function": "frames_from_market_evidence",
            "source_loader_git_blob_sha": SOURCE_LOADER_BLOB,
            "network_fetch_allowed": False,
            "replacement_allowed": False,
            "independent_oos": False,
        },
        "unavailable_or_deferred_design_families": {
            "F15_DERIVATIVES_LEVERAGE_CROWDING": "DATA_UNAVAILABLE_NO_NEW_IMMUTABLE_DAILY_PIT_PANEL_FROZEN_FOR_0062",
            "F16_OPTIONS_IMPLIED_RISK": "DATA_UNAVAILABLE_NO_NEW_IMMUTABLE_DAILY_PIT_PANEL_FROZEN_FOR_0062",
            "F17_ONCHAIN_HOLDER_STATE": "DATA_UNAVAILABLE_NO_NEW_IMMUTABLE_DAILY_PIT_PANEL_FROZEN_FOR_0062",
            "F18_CRYPTO_LIQUIDITY_STABLECOIN_DEPTH": "DATA_UNAVAILABLE_NO_NEW_IMMUTABLE_DAILY_PIT_PANEL_FROZEN_FOR_0062",
            "F19_CROSS_ASSET_MACRO": "DATA_UNAVAILABLE_NO_NEW_IMMUTABLE_PIT_VINTAGE_PANEL_FROZEN_FOR_0062",
            "F20_SENTIMENT_ATTENTION_FLOW": "DATA_UNAVAILABLE_NO_NEW_IMMUTABLE_PIT_PANEL_FROZEN_FOR_0062",
            "F22_LATENT_REGIME_STATE_SPACE": "NOT_EVALUATED_NO_SEPARATELY_FROZEN_CAUSAL_TRAINING_UPDATE_SEMANTICS_IN_0062",
        },
        "candidate_manifest": manifest,
        "candidate_cell_count": 185,
        "family_count_evaluated": 17,
        "normalization": {
            "raw_signal_construction": "CAUSAL_ONLY_USING_DATA_AT_OR_BEFORE_ORIGIN",
            "rolling_z_window_sessions": 252,
            "rolling_z_min_sessions": 60,
            "z_ddof": 1,
            "clip": [-3.0, 3.0],
            "zero_variance_policy": "CELL_MISSING_AT_ORIGIN",
            "family_score": "EQUAL_WEIGHT_MEAN_OF_ALL_AVAILABLE_PREREGISTERED_ORIENTED_CELL_ZS_WITH_MINIMUM_60_PERCENT_CELL_COVERAGE",
            "no_historical_cell_selection": True,
        },
        "targets": {
            "T1_CASH_ADVANTAGE": {"formula": "-log(BTC_close[t+h]/BTC_close[t])", "horizons_sessions": [5,10,20,40]},
            "T2_MAX_ADVERSE_EXCURSION": {"formula": "max(0,max_{j=1..h}(-log(BTC_close[t+j]/BTC_close[t])))", "horizons_sessions": [5,10,20,40]},
            "T3_FORWARD_REALIZED_VOL": {"formula": "sqrt(365)*sqrt(mean(r[t+1:t+h]^2))", "horizons_sessions": [5,10,20,40]},
            "T3_FORWARD_DOWNSIDE_SEMIVOL": {"formula": "sqrt(365)*sqrt(mean(min(r[t+1:t+h],0)^2))", "horizons_sessions": [5,10,20,40]},
            "T4_REVERSAL_EXHAUSTION": "NOT_EVALUATED_IN_0062_TIER_A_TO_AVOID_NEW_RESULT_SENSITIVE_EVENT_LABEL_ENGINEERING",
            "T5_RECOVERY_REENTRY": "NOT_EVALUATED_IN_0062; REENTRY_TRANSLATION_FORBIDDEN",
        },
        "horizon_groups": {
            "SHORT_REACTION": [5,10],
            "SWING_ADJUSTMENT": [20,40],
            "note": "20 sessions is retained only inside a prospectively frozen 5/10/20/40 geometry; 0061 20d positivity is exposed DEVELOPMENT and has no single-horizon authority.",
        },
        "family_track_mapping": {
            "directional_family_ids": directional,
            "risk_intensity_family_ids": risk,
            "directional_tracks": {
                "D_SHORT": ["T1_CASH_ADVANTAGE@5","T2_MAX_ADVERSE_EXCURSION@5","T1_CASH_ADVANTAGE@10","T2_MAX_ADVERSE_EXCURSION@10"],
                "D_SWING": ["T1_CASH_ADVANTAGE@20","T2_MAX_ADVERSE_EXCURSION@20","T1_CASH_ADVANTAGE@40","T2_MAX_ADVERSE_EXCURSION@40"],
            },
            "risk_tracks": {
                "R_SHORT": ["T3_FORWARD_REALIZED_VOL@5","T3_FORWARD_DOWNSIDE_SEMIVOL@5","T3_FORWARD_REALIZED_VOL@10","T3_FORWARD_DOWNSIDE_SEMIVOL@10"],
                "R_SWING": ["T3_FORWARD_REALIZED_VOL@20","T3_FORWARD_DOWNSIDE_SEMIVOL@20","T3_FORWARD_REALIZED_VOL@40","T3_FORWARD_DOWNSIDE_SEMIVOL@40"],
            },
            "family_track_hypothesis_count": 34,
        },
        "common_origin_policy": {
            "use_single_common_panel_across_all_185_cells_and_all_targets": True,
            "origin_requires_all_17_family_scores_and_all_4_horizon_targets": True,
            "minimum_origins": 1200,
            "chronological_blocks": 4,
            "minimum_origins_per_block": 250,
            "block_rule": "four contiguous count-balanced blocks after common-origin filtering; earlier blocks receive remainder first",
        },
        "measurement": {
            "association": "Spearman rank correlation; expected sign strictly positive after frozen signal orientation",
            "family_track_statistic": "minimum of the four constituent Spearman correlations",
            "temporal_recurrence_gate": "at least 3 of 4 chronological blocks have all four constituent Spearman correlations strictly positive",
            "cell_plateau": {
                "cell_favorable": "all four constituent Spearman correlations for the track are strictly positive",
                "minimum_family_favorable_cell_fraction": 0.50,
                "representation_class_coverage_rule": "if family has >=2 representation classes, at least 2 classes must each have favorable-cell fraction >=0.40; single-class families use only family favorable-cell fraction",
            },
            "fixed_score_bootstrap": {
                "rank_transform": "full-common-panel average-tie ranks standardized once; resamples never rerank",
                "resampling": "aligned moving-block bootstrap over origin rows",
                "block_length_sessions": 60,
                "replicates": 4000,
                "seed": 620062,
                "simultaneous_control": "for each replicate compute each of 34 track minimum constituent correlations; global q95 is Type-7 quantile of max_h(observed_min_h-bootstrap_min_h); LCB_h=observed_min_h-q95",
                "family_track_gate": "simultaneous_LCB_strictly_positive",
            },
        },
        "hard_gate_order": [
            "G0_CONTRACT_AND_DATA_IDENTITY",
            "G1_COMMON_SUPPORT",
            "G2_FULL_SAMPLE_SIGN_COHERENCE",
            "G3_TEMPORAL_RECURRENCE",
            "G4_PARAMETER_PLATEAU",
            "G5_SIMULTANEOUS_DEPENDENCE_AWARE_LCB",
        ],
        "classification": {
            "PASS_SIGNAL_ATLAS_FAMILY_INFORMATION": "at least one of 34 preregistered family-track hypotheses passes G0-G5",
            "FAIL_NO_SIGNAL_ATLAS_FAMILY_INFORMATION": "G0/G1 pass but no family-track passes all G2-G5",
            "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT": "G0 passes but G1 fails",
            "INVALID_EXECUTION": "contract, identity, implementation, persistence or exactly-once boundary violation",
        },
        "lossless_outputs_required": [
            "common-origin dates and block IDs",
            "family scores",
            "all 185 cell scores or sufficient lossless cell-by-target association tables",
            "all target values",
            "family/cell full-sample associations",
            "four-block associations",
            "plateau diagnostics",
            "all 34 observed track minima and simultaneous LCBs",
            "data-unavailable family statuses",
        ],
        "forbidden": [
            "historical argmax indicator or parameter promotion",
            "dropping unfavorable horizons or targets",
            "post-result family pruning/reweighting",
            "adding indicators/interactions after outcomes",
            "vendor substitution after outcome access",
            "threshold/gross/re-entry tuning",
            "strategy NAV or portfolio economics",
            "same-ID rerun/retune/rescue after RUN_ATTEMPT.marker",
        ],
        "authorization": {
            "information_atlas_only": True,
            "state_to_gross_translation_eligible_from_prereg_only": False,
            "portfolio_economics": False,
            "canonical_brrk_change": False,
            "phase6_change": False,
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }


def make_dataset_decl() -> dict:
    return {
        "schema_version": 1,
        "research_id": RID,
        "dataset_tier": "A_EXISTING_IMMUTABLE_MARKET_INTERNAL",
        "development_dataset_ref": "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1",
        "path": MARKET,
        "git_blob_sha": MARKET_BLOB,
        "payload_sha256": MARKET_PAYLOAD_SHA,
        "assets_exact": ["BTC","ETH","SOL"],
        "fields_exact": ["open","high","low","close","volume","quote_volume","trades"],
        "history_start": "2020-08-11T00:00:00Z",
        "history_end": "2026-08-02T00:00:00Z",
        "common_rows": 2183,
        "resolution": "1D",
        "stored_index_representation": "TZ_NAIVE_UTC_NORMALIZED_DAILY_DATES",
        "source_loader_module": "research.brrk_beta_handoff_0047.engine",
        "source_loader_function": "frames_from_market_evidence",
        "source_loader_git_blob_sha": SOURCE_LOADER_BLOB,
        "network_fetch_allowed": False,
        "replacement_allowed": False,
        "independent_oos": False,
        "exposure_status": "RESEARCHER_EXPOSED_DEVELOPMENT_NOT_INDEPENDENT_OOS",
        "tier_b_c_rule": "No new Tier-B/C payload is frozen for 0062; F15-F20 are explicit DATA_UNAVAILABLE tracks, not silently omitted reserves.",
    }


def make_owner(registry: dict) -> dict:
    src = next(x for x in registry["records"] if x.get("research_id") == "BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061")
    owner = dict(src)
    owner.update({
        "research_id": RID,
        "research_family_id": "BRRK_BTC_TO_CASH_GROSS_RISK",
        "research_domain": "RISK_CONTROL",
        "research_governance_version": 1,
        "governance_mode": "PROGRAM_GOVERNED_V1",
        "objective_type": "MECHANISM_TEST",
        "created_at": CREATED_AT,
        "created_before_result": True,
        "question": "Which prospectively frozen market-internal signal families contain recurrent, dependence-aware information about BTC-vs-Cash opportunity cost, forward path damage, or future risk before any control law is defined?",
        "hypothesis": "At least one prospectively frozen Tier-A signal family-track will show positive full-sample sign coherence, temporal recurrence, broad parameter support and a simultaneous dependence-aware lower confidence bound above zero.",
        "hypothesis_origin": "RESULT_INFORMED_DEVELOPMENT_MECHANISM_FORMATION_NOT_INDEPENDENT_OOS",
        "economic_mechanism": "Risk information may arrive through trend, momentum, reversal/exhaustion, volatility, structure, volume, breadth, relative-crypto leadership or structural change; reactive risk information need not be a stable long-horizon return forecast.",
        "primary_target": "FAMILY_TRACK_INFORMATION_ATLAS_T1_T2_T3_OVER_FROZEN_5_10_20_40_SESSION_GEOMETRY",
        "primary_metric": "FAMILY_TRACK_MINIMUM_CONSTITUENT_SPEARMAN_WITH_4_BLOCK_RECURRENCE_PLATEAU_AND_SIMULTANEOUS_MBB_LCB",
        "secondary_metrics": ["cell_parameter_plateau_fraction","representation_class_coverage","family_redundancy","data_source_coverage"],
        "feature_families": list(candidate_manifest().keys()),
        "horizon": [5,10,20,40],
        "universe": ["BTC","ETH","SOL"],
        "development_dataset_refs": ["BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"],
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
        "lineage_edges": [
            {"from":"BRRK-EXHAUSTION-STATE-0044","relation":"EXPOSED_DEVELOPMENT_MOTIVATION_ONLY"},
            {"from":"BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061","relation":"EXPOSED_DEVELOPMENT_DIFFERENT_MECHANISM_QUESTION"},
        ],
        "result_status": "PREREGISTERED_NOT_RUN",
        "failure_reason": None,
        "promotion_state": "NO_PROMOTION",
        "evidence_refs": [],
        "decision_refs": [DESIGN, f"{BASE}/PREREGISTRATION.json", f"{BASE}/DATASET_DECLARATION.json", "docs/CURRENT_STATE.md"],
        "production_relevance": "DEVELOPMENT signal-information atlas only; no state-to-gross, canonical, Phase-6 or production authority.",
        "production_authorized": False,
        "provenance_status": "FACT",
        "governed_path_prefixes": [BASE + "/"],
        "notes": [
            "RSI, MACD, Supertrend and MA representations have no privileged winner status.",
            "0061 20-day positive signs are exposed DEVELOPMENT only; 0062 freezes 5/10/20/40 before outcome access.",
            "F15-F20 are explicit DATA_UNAVAILABLE under 0062 because no new immutable point-in-time panel is frozen before outcomes.",
            "F22 is not evaluated because no separate causal latent-state training/update semantics are frozen in this ID.",
        ],
    })
    # Clear optional result-derived confidence state inherited from 0061 if present.
    for key in list(owner):
        if key.startswith("confidence_") or key in {"evidence_confidence", "derived_confidence"}:
            owner.pop(key, None)
    return owner


def update_current_state() -> None:
    path = ROOT / "docs/CURRENT_STATE.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("Last updated: **2026-08-13**", "Last updated: **2026-08-14**", 1)
    import re
    text = re.sub(r"Current `main` research merge: \*\*`[^`]+`\*\*", f"Current `main` research merge: **`{DESIGN_MERGE}`**", text, count=1)
    text = re.sub(r"Current research branch: \*\*`[^`]+`\*\*", "Current research branch: **`research/0062-prereg-v1`**", text, count=1)
    old = "BRRK BTC risk signal atlas 0062        DESIGN FROZEN / PREREG ABSENT / NOT RUN"
    new = "BRRK BTC risk signal atlas 0062        PREREGISTERED / IMPLEMENTATION ABSENT / NOT RUN"
    if old not in text:
        raise RuntimeError("0062 CURRENT_STATE status line not found")
    text = text.replace(old, new, 1)
    insert = """

## 0062 numerical/data preregistration handoff

```text
research id                             BRRK-BTC-RISK-SIGNAL-ATLAS-0062
design merge                            aa3fa9c1814c4113918e0d012636db44a1f89659
stage                                   PREREGISTERED / NOT RUN
Tier-A family count                     17
frozen candidate cells                  185
frozen family-track hypotheses          34
horizons                                5 / 10 / 20 / 40 sessions
Tier-B/C F15-F20                        DATA_UNAVAILABLE / NOT SUBSTITUTABLE POST HOC
F22 latent-state                        NOT EVALUATED IN 0062
historical 0062 outcomes                NOT COMPUTED
actual variants evaluated               0
RUN_ATTEMPT.marker                      ABSENT
portfolio economics                     FORBIDDEN
canonical BRRK-0011                     NO CHANGE
Phase 6                                 NO CHANGE
production_authorized                   false
signature_authorized                    false
order_submission_authorized             false
```

Exact candidate geometry, target formulas, family-track mapping, support gates, temporal recurrence, plateau gate and dependence-aware simultaneous MBB inference are frozen in `research/brrk_btc_risk_signal_atlas_0062/PREREGISTRATION.json`. The immutable Tier-A evidence wrapper remains researcher-exposed DEVELOPMENT history and is not independent OOS. No 0062 historical target, signal association or family ranking was computed during preregistration.
"""
    marker = "\n---\n\n## 2. 0048 immutable scientific result"
    if marker not in text:
        raise RuntimeError("CURRENT_STATE insertion marker not found")
    text = text.replace(marker, insert + marker, 1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if run("git", "rev-parse", "HEAD") != DESIGN_MERGE:
        raise RuntimeError("clean prereg branch must start exactly at merged 0062 DESIGN")
    registry = json.loads(REG.read_text(encoding="utf-8"))
    if any(x.get("research_id") == RID for x in registry["records"]):
        raise RuntimeError("0062 owner already exists")
    registry["records"].append(make_owner(registry))
    write_json(REG, registry)
    run("python", "-m", "research.governance.validate")
    run("git", "add", "config/research_registry.json")
    run("git", "commit", "-m", "research: register 0062 prereg owner")

    write_json(ROOT / BASE / "PREREGISTRATION.json", make_prereg())
    write_json(ROOT / BASE / "DATASET_DECLARATION.json", make_dataset_decl())
    update_current_state()
    # Validate the final tree and formal-path ownership before push.
    run("python", "-m", "research.governance.validate")
    run("python", "-m", "research.governance.enforce_future", "--changed-path", f"{BASE}/PREREGISTRATION.json", "--changed-path", f"{BASE}/DATASET_DECLARATION.json")
    run("git", "add", f"{BASE}/PREREGISTRATION.json", f"{BASE}/DATASET_DECLARATION.json", "docs/CURRENT_STATE.md")
    run("git", "commit", "-m", "research: freeze 0062 numerical and data preregistration")

    # Strong local invariants before publishing formal branch.
    registry2 = json.loads(REG.read_text(encoding="utf-8"))
    owners = [x for x in registry2["records"] if x.get("research_id") == RID]
    if len(owners) != 1 or owners[0].get("actual_variants_evaluated") != 0:
        raise RuntimeError("0062 owner invariant failed")
    prereg = json.loads((ROOT / BASE / "PREREGISTRATION.json").read_text())
    if prereg["candidate_cell_count"] != 185 or prereg["family_track_mapping"]["family_track_hypothesis_count"] != 34:
        raise RuntimeError("prereg count invariant failed")
    if (ROOT / BASE / "RUN_ATTEMPT.marker").exists():
        raise RuntimeError("illegal attempt marker during prereg")
    run("git", "push", "origin", "HEAD:research/0062-prereg-v1")


if __name__ == "__main__":
    main()
