# BRRK Current State

Last updated: 2026-08-08  
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / no eligible >1 candidate
production gross cap              1.0
production_authorized_components = []
P5.1-P5.4                         COMPLETE / frozen
P5.5 validation                   COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6 cycle integration            BLOCKED / NO ELIGIBLE P5.5 CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 observation preactivation PREACTIVATION_BLOCKED_FAIL_CLOSED / GOVERNANCE V1
Phase 6 evidence backend          FROZEN / ACTIONS_ARTIFACT_V4 / RETENTION 90D / NO CREDIT
Phase 7 readiness gate            IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 program state             MONITOR_ONLY
Phase 8 bear-short research       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Phase 0-8 drift audit             COMPLETE / PASS_FINAL_HEAD_VERIFIED / DRIFT_2 REMEDIATED
Program epistemic governance v1   PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT CLOSEOUT
Future research gate repair       MERGED #121 / GOVERNANCE ONLY / DRIFT_0
Future prereg validator repair    MERGED #122 / GOVERNANCE ONLY / DRIFT_0
Stablecoin liquidity research     STABLECOIN-LIQUIDITY-0001 / STAGE-1 COMPLETE / FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP
Stablecoin terminal closeout      MERGED #131 / main 0d6cef33f556a745850470e237c5ba021cddaa80
Phase 6 preactivation gate        MERGED #132 / main c7b51625ca4ea990f8325b1abafc67c00daa0d74
production authorization          NONE
first real short authorization    NONE
```

## Phase 4

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. No research cap, operating drawdown budget or prospective production leverage cap was selected. Current production gross remains `1.0` and P4.6 remains blocked.

`LEVERAGE-0040` summary SHA256 remains:

```text
3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
```

## Phase 5

P5.5 immutable result commit `ae20890d87567c98e403e3558219d5de55daef67`; summary SHA256 `ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71`.

No profile/map combination passes the frozen validation stack. P5.6 remains `BLOCKED / NO ELIGIBLE CANDIDATE`; no cycle-risk multiplier is carried into Phase 6/7.

## Phase 6

Merged PR #109 at `1763d3c6f2c2d68f77f9e68b3cf9e252e4b799d4`.

Machine contract: `config/phase6_shadow_contract.json`.

Canonical P3.2 parity/golden vectors and zero-authority shadow implementation/replay passed. The shadow path can consume read-only account/market/order-book state and compute hypothetical routing, but it cannot sign or submit orders.

Actual elapsed evidence remains time-dependent. The frozen contract requires at least 14 elapsed calendar days, at least 10 scheduled decisions, at least one emergency drill and zero frozen quality violations before the live-observation state can change from:

```text
MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

No CI replay or historical replay may backfill that elapsed-time evidence.

A live-state audit after Stablecoin closeout found that `.github/workflows/phase6-integrated-shadow.yml` is implementation/replay safety CI only: it has PR/push/manual triggers, no scheduled future collector and no durable elapsed-evidence persistence. Therefore the Phase-6 real elapsed clock has **not** been automatically accumulating.

Governance v1 no-drift also keeps the canonical strategy/execution/config blobs byte-identical to the frozen boundary except for already-authorized governance/prospective research paths. The repair therefore does not add a new execution path under `beta_bot/` and does not weaken the no-drift allowlist.

The machine preactivation gate is:

- `research/governance/phase6_live_observation_gate.json`
- `research/governance/phase6_live_observation_gate.py`

The durable evidence contract is:

- `research/governance/phase6_live_evidence_contract.json`
- `research/governance/phase6_live_evidence.py`

Current gate state is:

```text
status                                      PREACTIVATION_BLOCKED_FAIL_CLOSED
collector_armed                             false
schedule_configured                         false
elapsed_evidence_credit_authorized          false
observation_account_identity_frozen         false
current_position_equity_valuation_frozen    false
durable_create_only_evidence_backend_frozen true
schedule_and_duplicate_credit_rule_frozen   true
production_authorized                       false
signature_authorized                        false
order_submission_authorized                 false
```

The evidence backend is prospectively frozen to `GITHUB_ACTIONS_ARTIFACT_V4` with `retention-days=90`, `overwrite=false`, hard failure on empty uploads, and required immutable `artifact-id` / `artifact-url` / `artifact-digest` outputs. Each future credited decision must first durably upload its evidence bundle, then create and separately upload a hash-bound receipt. Runner files, logs, step summaries, missing receipts, upload failures or artifacts that expire before acceptance review create zero credit. This storage contract is based on the already-successful Stablecoin Stage-1 artifact/receipt mechanism, but Stablecoin artifacts are precedent only and are not Phase-6 evidence.

Two pre-arm dependencies remain unresolved: one explicit read-only observation account identity and current-position/account-equity valuation semantics for the permitted observation surfaces. The schedule/duplicate rule and durable evidence backend are now frozen. No account state or valuation may be fabricated to close the remaining blockers.

The first eligible scheduled decision after a future arm is the first canonical `00:00 UTC` decision strictly after the arm commit timestamp. The preactivation/evidence contracts themselves start no clock and create no elapsed evidence.

## Phase 7

Readiness gate merged in PR #110. Machine contract: `config/phase7_launch_readiness.json`.

Current state is `MONITOR_ONLY`; production authorization is false. Launch is blocked at minimum by missing Phase 6 elapsed evidence and missing explicit owner approval. The gate also requires production-release, credential, monitoring, reconciliation and kill-switch evidence.

Human approval remains mandatory for:

```text
MONITOR_ONLY -> ACTIVE
FLAT -> LONG
FLAT -> SHORT
first short exposure of a new bear phase
```

## Phase 8

`BEAR-SHORT-0001` research package merged in PR #111. Machine contract: `research/bear_short_0001/BEAR-SHORT-0001.json`.

No canonical `CONFIRMED_BEAR_TRANSITION_ARTIFACT` exists, therefore:

```text
status                       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN
selection_status             NONE_TRIGGER_ABSENT
short_ready                  false
production_authorized        false
first_real_short_authorized  false
```

No subjective market judgment substitutes for the missing trigger and no trigger-dependent short economics has been run.

## Phase 0-8 drift audit

Machine contract: `config/phase0_8_drift_audit.json`. Evidence report: `docs/PHASE_0_8_DRIFT_AUDIT_2026-08-08.md`.

The audit is complete and remediated three drift classes without economic retuning:

1. **Legacy execution authority bypass** — normal risk increases are fail-closed behind explicit production authority.
2. **Legacy production-cap drift** — production-facing `NORMAL_BETA_CAP` default/ceiling is `1.0`.
3. **Authoritative handoff drift** — README/CURRENT_STATE/NEXT_STEPS reflect completed Phase 6/7/8 work.

Same-direction reductions and emergency flatten remain available. The audit status is `PASS_FINAL_HEAD_VERIFIED` and does not confer production authority.

## Program-Level Epistemic Governance v1

Governance v1 is complete across PG0-PG6 under the frozen prospective boundary:

```text
legacy_boundary_commit = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version = 1
```

The implementation extends rather than replaces existing experiment, decision and production governance. Canonical machine sources are:

- `config/research_governance_v1.json` — governance vocabulary/version/authority-plane semantics;
- `config/research_registry.json` — research records, typed lineage and governance debt;
- `config/dataset_exposure_registry.json` — future dataset slices and exposure events;
- `config/edge_registry.json` — evidence-admitted incremental edges only;
- `research/governance/validate.py` — fail-closed registry validation;
- `research/governance/audit.py` — deterministic program audit;
- `research/governance/future_policy.py` — shared future-path ownership and prospective-provenance policy;
- `research/governance/enforce_future.py` — exact-PR-diff prospective research registration enforcement;
- `research/governance/no_drift.py` — boundary-to-HEAD strategy/evidence/authority no-drift regression;
- `research/governance/phase6_live_observation_gate.py` — fail-closed Phase-6 future-elapsed preactivation control;
- `research/governance/phase6_live_evidence.py` — frozen durable Phase-6 evidence-backend validation;
- `.github/workflows/research-governance.yml` — CI enforcement, including Stablecoin regressions and the Phase-6 live-observation preactivation gate. Both temporary Stablecoin live executors (first capture and Stage-1 result execution) were removed immediately after their one-shot use.

PG4 conservatively maps 17 `RETROSPECTIVE_LEGACY` research records. Six governance-debt classes remain explicit because historical trial counts, information releases, dataset consumption, lineage, informal researcher decisions and complete candidate universes cannot be reconstructed truthfully. `UNKNOWN` remains `UNKNOWN`.

The Edge Registry remains empty because no feature has yet passed governance-v1 incremental-information admission. Historical legacy dataset exposure remains unbackfilled where provenance is unknown; the Stablecoin slice is the first prospectively recorded reconstructed-history validation exposure under this workflow. Therefore the Dataset Exposure Registry is not globally empty.

Future formal result-bearing research must be prospectively covered by exactly one `PROGRAM_GOVERNED_V1` record with the frozen required fields, declared path ownership, variant budget, stopping rules, lineage/data references and `production_authorized=false`. Changed legacy formal research paths are treated as new post-boundary research activity and cannot bypass prospective registration or existing immutable-evidence correction rules.

PR #121 repaired the cross-gate conflict between future-research registration and the final no-drift regression without broadening the legacy allowlist. PR #122 repaired preregistration-only validator semantics so empty pre-result dataset/evidence arrays do not require fabricated placeholders. PR #123 prospectively registered `STABLECOIN-LIQUIDITY-0001`. PR #124 froze its source/data/PIT contract. PR #125 froze the one-shot first-capture gate. PR #126 split capture/persist from finalize so durable archival must precede parsing. PR #127 armed and executed the single governed capture on merge commit `824f58151bcef2203c320e4b94b8070dcac77dae` through GitHub Actions run `31261566204`; both governance and capture jobs completed successfully. PR #128 registered the captured validation slice/exposure and removed the capture executor. PR #129 froze `STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1`. PR #130 irreversibly claimed and executed Stage-1 exactly once on merge `dd50ec35085eee2a2883dc1b29e3dd21ec52b043`, workflow run `31264048473`, producing the immutable primary FAIL result. PR #131 merged terminal closeout at `0d6cef33f556a745850470e237c5ba021cddaa80`, removed the completed Stage-1 live executor and made the FAIL_STOP authoritative on `main`. PR #132 merged the Phase-6 future-only live-observation preactivation gate at `c7b51625ca4ea990f8325b1abafc67c00daa0d74` without arming the clock or changing canonical execution/authority.

## STABLECOIN-LIQUIDITY-0001

`STABLECOIN-LIQUIDITY-0001` was a prospectively governed Stage-1 mechanism test asking whether the frozen `STABLECOIN_LIQUIDITY_STATE_V1` feature family adds predictive information about future 20-day canonical BRRK net returns beyond the frozen P3.2 BRRK price/regime state.

The research ID has reached its frozen stopping point:

```text
result_status                    FAIL_NO_INCREMENTAL_INFORMATION
failure_reason                   PRIMARY_MEAN_LOSS_DIFFERENTIAL_NONPOSITIVE
promotion_state                  NO_PROMOTION
production_authorized            false
declared_variant_budget          1
actual_variants_evaluated        1
run_interface                    STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1 / IMMUTABLE PRE-RESULT CONTRACT
run_once_marker                  RUN_ONCE_STAGE1.marker / PERMANENT / DO NOT DELETE
stage1 execution                 STABLECOIN-LIQUIDITY-0001-STAGE1-RUN-V1 / EXECUTED ONCE / TERMINAL FAIL_STOP
stage1 merge commit              dd50ec35085eee2a2883dc1b29e3dd21ec52b043
stage1 workflow run              31264048473 / run_attempt=1 / SUCCESS
validation dataset               STABLECOIN-LIQUIDITY-0001-DEFILLAMA-HIST-V1
validation exposure              STABLECOIN-LIQUIDITY-0001-RAW-DATA-20260808T141719Z
historical classification        RECONSTRUCTED_HISTORY_RESEARCHER_EXPOSED_HISTORY
primary result evidence          research/stablecoin_liquidity_0001/STAGE1_PRIMARY_RESULT.json
edge admission                   NONE
portfolio integration            NONE
stage2 robustness eligibility    NONE / PRIMARY STAGE-1 FAILED
```

### Immutable primary result

```text
valid_oos_prediction_count       933
mean_primary_loss_differential   -5430210.12771038
hac_max_lag                      19
hac_test_statistic               -1.2454264237630361
hac_one_sided_p_value            0.8935124773215692
primary_result_digest            d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff
classification                   FAIL_NO_INCREMENTAL_INFORMATION
```

The preregistered primary differential is `MSE_baseline - MSE_augmented`; therefore a non-positive mean is an immediate frozen failure condition. The observed mean is materially negative, so the augmented Stablecoin model did not demonstrate incremental predictive information beyond the frozen P3.2 BRRK state. The OOS count exceeds the 730 minimum, but the one-sided HAC result (`t=-1.2454264237630361`, `p=0.8935124773215692`) likewise provides no support for a positive incremental-information effect.

This is a **terminal research failure**, not an invitation to retune. LAG_1D/LAG_3D, alternative Ridge alpha, alternative horizon, alternative feature representation, secondary metrics, predictions and coefficient paths cannot be used to rescue this ID. No Stage-2 robustness research is eligible from this failed Stage-1. `RUN_ONCE_STAGE1.marker` remains permanently committed and the same research ID may never be rerun.

### Provenance and data state

The first Stablecoin capture remains the immutable reconstructed-history validation dataset:

```text
historical_start                 2017-11-29T00:00:00Z
historical_end                   2026-08-08T00:00:00Z
historical_rows                  3175
stablecoin_raw_sha256            7cffe6fb3a21e891082c06c60e91491edfbc78e9c01e2d549805815a646d9ffd
stablecoin_capture_run           31261566204
```

Historical publication/first-seen timestamps were unavailable, so the data remains `RESEARCHER_EXPOSED_HISTORY`, never sealed or `TEMPORALLY_UNSEEN`. The Stage-1 execution verified that raw hash, captured exact Binance input pages before model evaluation, durably archived those inputs and their receipt, passed the frozen six-date canonical P3.2 parity gate, then ran exactly one paired baseline/augmented walk-forward Ridge variant.

Stage-1 immutable artifacts from workflow run `31264048473` are:

```text
Binance input artifact ID        9023613464
Binance input digest             sha256:26748abdd75a7568872617b5bc2f6618b8b3a315cbcd785cf1175e4c606354db
Binance receipt artifact ID      9023613629
Binance receipt digest           sha256:bdf9ed3486c426c75f4b7cd9eed2e88bc2843c457459481b0eb56e14429ce9d3
primary result artifact ID       9023630485
primary result artifact digest   sha256:6eac38957c3592e18eb2cb4706e87be12daeca6cfe504065af19e944984674f1
```

The input ZIP, receipt ZIP, primary-result ZIP and primary JSON were also mirrored outside the repository to ChatGPT Library. Predictions, coefficients, feature importance and secondary metrics were not persisted/released.

The temporary Stage-1 live execution job is removed. `RUN_INTERFACE.json` itself is intentionally not rewritten after observing the result; it remains the immutable pre-result contract that governed the one-shot test.

### Authority consequence

The FAIL result creates no edge and no authority:

- Edge Registry remains empty.
- BRRK relative ranking, BTC/ETH/SOL/BNB universe and BNB membership remain unchanged.
- No Stablecoin multiplier or portfolio feature is created.
- Production gross cap remains `1.0`.
- `production_authorized_components = []`.
- Phase 6 elapsed observation is independent and unchanged.
- Phase 7 remains `MONITOR_ONLY` / launch blocked.
- Phase 8 bear-short remains trigger-absent/not-run.
- No leverage, short or first-real-short authority is created.

`ONCHAIN-HOLDER-COST-0001` remains only a separate backlog idea. Stablecoin has reached its stopping point, so Holder Cost may be considered later only through a **new prospective preregistration**; it is not started by this closeout.

## Frozen product boundaries

- BRRK relative ranking unchanged.
- BTC / ETH / SOL / BNB long universe unchanged; BNB remains included.
- Production gross cap remains 1.0.
- `production_authorized_components = []`.
- No >1 production leverage.
- No P5 cycle overlay.
- Transaction-cost assumptions unchanged.
- Historical immutable research evidence unchanged.
- No automated withdrawal/transfer.
- No live launch authorization.
- No real short authorization.
- Legacy credentials / `TRADING_MODE=trade` do not create production authority.

## Exact next action

```text
KEEP PHASE-6 LIVE ELAPSED STATUS AT MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT; THE CLOCK IS NOT ARMED
KEEP THE PHASE-6 PREACTIVATION GATE FAIL-CLOSED UNTIL ALL REQUIRED OPERATIONAL SEMANTICS ARE FROZEN
KEEP PHASE6-LIVE-EVIDENCE-BACKEND-V1 FROZEN AT ACTIONS_ARTIFACT_V4 / RETENTION 90D / OVERWRITE FALSE; THIS CONTRACT ALONE CREATES ZERO CREDIT
FREEZE ONE EXPLICIT READ-ONLY OBSERVATION ACCOUNT IDENTITY; DO NOT FABRICATE ACCOUNT STATE
FREEZE CURRENT-POSITION / ACCOUNT-EQUITY VALUATION SEMANTICS WITHOUT CHANGING P3.2/P3.3 ECONOMICS
THEN ARM THE FUTURE-ONLY COLLECTOR IN A SEPARATE PROSPECTIVE CHANGE
COUNT ONLY THE FIRST 00:00 UTC DECISION STRICTLY AFTER THE ARM COMMIT AND LATER GENUINE SCHEDULED DECISIONS
REQUIRE EVIDENCE BUNDLE + HASH-BOUND RECEIPT DURABLY UPLOADED BEFORE ANY DECISION CREDIT
DO NOT BACKFILL, REPLAY-CREDIT, RERUN-CREDIT OR DUPLICATE-CREDIT THE 14-DAY / 10-DECISION REQUIREMENT
KEEP signature_authorized = false AND order_submission_authorized = false AND production_authorized = false
KEEP STABLECOIN-LIQUIDITY-0001 AT FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION / TERMINAL STOP
KEEP RUN_ONCE_STAGE1.marker PERMANENT; DO NOT DELETE, RERUN, RETRY OR REUSE THIS RESEARCH ID
DO NOT TEST LAG_1D/LAG_3D, NEW RIDGE ALPHA, NEW HORIZON, NEW STABLECOIN REPRESENTATION OR SECONDARY-METRIC RESCUE UNDER THIS ID
DO NOT START A STABLECOIN STAGE-2 ROBUSTNESS ID BECAUSE STAGE-1 FAILED
KEEP EDGE REGISTRY EMPTY FOR STABLECOIN; DO NOT CREATE A MULTIPLIER OR PORTFOLIO INTEGRATION
KEEP THE COMPLETED STAGE-1 LIVE EXECUTOR REMOVED FROM CURRENT HEAD
AFTER PHASE-6 COLLECTION IS OPERATIONAL, IMPLEMENT THE FORMAL RESEARCH LIFECYCLE/STATE MACHINE, THEN RESEARCH QUEUE + TRIAL/OVERLAP ACCOUNTING
ONCHAIN-HOLDER-COST-0001 MAY ONLY BE CONSIDERED LATER AS A SEPARATE NEW PROSPECTIVE RESEARCH ID
DO NOT CHANGE BRRK / BNB / PARAMETERS / COSTS / HISTORICAL LEGACY EVIDENCE / PRODUCTION AUTHORITY
DO NOT ACTIVATE PHASE 7 WITHOUT THE COMPLETE CHECKLIST AND EXPLICIT OWNER APPROVAL
DO NOT RUN BEAR-SHORT-0001 ECONOMICS WITHOUT THE FROZEN CONFIRMED-BEAR TRIGGER
DO NOT AUTHORIZE A FIRST REAL SHORT WITHOUT THE SEPARATE HUMAN GATE
```
