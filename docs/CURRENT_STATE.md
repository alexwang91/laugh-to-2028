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
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
Phase 7 readiness gate            IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 program state             MONITOR_ONLY
Phase 8 bear-short research       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Phase 0-8 drift audit             COMPLETE / PASS_FINAL_HEAD_VERIFIED / DRIFT_2 REMEDIATED
Program epistemic governance v1   PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT CLOSEOUT
Future research gate repair       MERGED #121 / GOVERNANCE ONLY / DRIFT_0
Future prereg validator repair    MERGED #122 / GOVERNANCE ONLY / DRIFT_0
Stablecoin liquidity research     STABLECOIN-LIQUIDITY-0001 / STAGE-1 ONE-SHOT CLAIMED + ARMED_NOT_EXECUTED / NO RESULT
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

Canonical P3.2 parity/golden vectors and zero-authority shadow implementation/replay passed. The shadow path can read account/market/order-book state and compute hypothetical routing, but it cannot sign or submit orders.

Actual elapsed evidence remains time-dependent. The frozen contract requires at least 14 elapsed calendar days, at least 10 scheduled decisions and the required live-shadow quality criteria before the live-observation state can change from:

```text
MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
```

No CI replay or historical replay may backfill that elapsed-time evidence.

Program-Level Epistemic Governance v1 is now implemented so future elapsed observations can enter the provenance/evidence model from inception. This does not create, accelerate or backfill Phase 6 elapsed evidence.

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
- `.github/workflows/research-governance.yml` — CI enforcement, including the governed Stablecoin data-contract/capture-gate regression suite. The temporary live one-shot executor used for the first capture has been removed after successful execution.

PG4 conservatively maps 17 `RETROSPECTIVE_LEGACY` research records. Six governance-debt classes remain explicit because historical trial counts, information releases, dataset consumption, lineage, informal researcher decisions and complete candidate universes cannot be reconstructed truthfully. `UNKNOWN` remains `UNKNOWN`.

The Edge Registry remains empty because no feature has yet passed governance-v1 incremental-information admission. Historical legacy dataset exposure remains unbackfilled where provenance is unknown; the new Stablecoin slice is the first prospectively recorded reconstructed-history validation exposure under this workflow.

Future formal result-bearing research must be prospectively covered by exactly one `PROGRAM_GOVERNED_V1` record with the frozen required fields, declared path ownership, variant budget, stopping rules, lineage/data references and `production_authorized=false`. Changed legacy formal research paths are treated as new post-boundary research activity and cannot bypass prospective registration or existing immutable-evidence correction rules.

PR #121 repaired the cross-gate conflict between future-research registration and the final no-drift regression without broadening the legacy allowlist. PR #122 repaired preregistration-only validator semantics so empty pre-result dataset/evidence arrays do not require fabricated placeholders. PR #123 prospectively registered `STABLECOIN-LIQUIDITY-0001`. PR #124 froze its source/data/PIT contract. PR #125 froze the one-shot first-capture gate. PR #126 split capture/persist from finalize so durable archival must precede parsing. PR #127 armed and executed the single governed capture on merge commit `824f58151bcef2203c320e4b94b8070dcac77dae` through GitHub Actions run `31261566204`; both governance and capture jobs completed successfully.

## STABLECOIN-LIQUIDITY-0001

`STABLECOIN-LIQUIDITY-0001` remains a `PROGRAM_GOVERNED_V1` Stage-1 external-information mechanism test asking whether a frozen stablecoin-liquidity information family adds predictive information about future 20-day canonical BRRK outcomes beyond the frozen P3.2 BRRK price/regime state.

Current state is strictly:

```text
result_status                 PREREGISTERED_NOT_RUN
promotion_state               NONE
production_authorized         false
declared_variant_budget       1
actual_variants_evaluated     0
governed_path_prefix          research/stablecoin_liquidity_0001/
formal research path          CREATED UNDER PROSPECTIVE OWNER
data contract                 STABLECOIN-LIQUIDITY-0001-DATA-CONTRACT-V1 / FROZEN
capture gate                  STABLECOIN-LIQUIDITY-0001-FIRST-CAPTURE-GATE-V1 / FROZEN CONTRACT
capture execution             STABLECOIN-LIQUIDITY-0001-FIRST-CAPTURE-EXECUTION-V1 / EXECUTED_ONCE_METADATA_ONLY
capture merge commit          824f58151bcef2203c320e4b94b8070dcac77dae
capture workflow run          31261566204 / SUCCESS
historical full capture       COMPLETE / 3175 DAILY ROWS / 2017-11-29 THROUGH 2026-08-08
historical classification     RECONSTRUCTED_HISTORY_RESEARCHER_EXPOSED_HISTORY
run interface                  STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1 / FROZEN_NOT_EXECUTED
stage1 run marker              RUN_ONCE_STAGE1.marker / CLAIMED_BEFORE_RESULT_BEARING_EXECUTION / IRREVERSIBLE IF MERGED
stage1 execution              STABLECOIN-LIQUIDITY-0001-STAGE1-RUN-V1 / ARMED_NOT_EXECUTED / PR CI NON-RESULT-BEARING
research-registry validation ref STABLECOIN-LIQUIDITY-0001-DEFILLAMA-HIST-V1
validation exposure ref         STABLECOIN-LIQUIDITY-0001-RAW-DATA-20260808T141719Z
real feature computation        NOT RUN
real BRRK Stage-1 state path    NOT RUN
Ridge fit                       NOT RUN
OOS predictions                 NONE
dataset exposure registry     STABLECOIN-LIQUIDITY-0001-DEFILLAMA-HIST-V1 / VALIDATION / CONSUMED / RESEARCHER_EXPOSED_HISTORY
dataset provenance evidence   research/stablecoin_liquidity_0001/FIRST_CAPTURE_EVIDENCE.json
research result evidence      NONE
edge admission                NONE
portfolio integration         NONE
```

The frozen source reference remains the official `DefiLlama/api-sdk` repository at commit `f0d43119c746dda0c1ad8460c37ac9e00e8e5161`, repository package version `0.1.4`, mapping `stablecoins.getAllCharts()` to `GET https://stablecoins.llama.fi/stablecoincharts/all`.

The single first capture was retrieved at `2026-08-08T14:17:19.736297Z`. Metadata-only validation established:

```text
raw_row_count        3175
historical_row_count 3175
historical_start     2017-11-29T00:00:00Z
historical_end       2026-08-08T00:00:00Z
historical_cutoff    2026-08-08T00:00:00Z
raw_size_bytes       1223275
raw_sha256           7cffe6fb3a21e891082c06c60e91491edfbc78e9c01e2d549805815a646d9ffd
manifest_sha256      ca6f68bab0f19957444dd2eb38bc4f171910851cf258d303725f1d31dff56d8d
research result      NO_RESEARCH_RESULT_CAPTURE_METADATA_ONLY
```

Exact raw bytes + manifest were uploaded before parsing to GitHub Actions artifact `9022927539`; receipt + metadata were archived as artifact `9022927785`. Exact raw/manifest/staging/receipt/metadata files were additionally mirrored out of repository to ChatGPT Library with hash identity preserved. The temporary live executor is removed in the current registration/closeout change so repository HEAD no longer contains a repeatable live first-capture job.

Historical rows expose observation timestamps but no verifiable original historical publication/first-seen timestamps. Historical data therefore remains reconstructed / `RESEARCHER_EXPOSED_HISTORY`; its frozen primary availability rule remains `available_at = metric_timestamp + 2 calendar days`. It cannot be relabeled pristine sealed data or `TEMPORALLY_UNSEEN`.

The Dataset Exposure Registry records this slice as `VALIDATION` because it belongs to a preregistered Stage-1 candidate comparison. The raw retrieval is explicitly recorded as a `RAW_DATA` exposure with `consumed=true`; this prevents later claims that the reconstructed history was an unseen holdout. Raw SHA256 remains in immutable provenance, not as an unregistered Dataset Registry property.

The primary feature definition remains aggregate USD-pegged stablecoin value 20-day log growth plus 20-day growth acceleration with exact lag-date matching. Missing dates are not interpolated or forward-filled. No real feature series has been computed, no Ridge model has been fit, no OOS predictions exist and no research performance result has been released.

`RUN_INTERFACE.json` freezes the 35-column continuous canonical P3.2 BRRK price/regime baseline state, exact LAG_2D Stablecoin alignment, future 20-calendar-day canonical BRRK net-return label, paired-row eligibility, minimum 365 fully realized expanding training rows, training-only StandardScaler, Ridge alpha=1.0 with no grid, one-sided Bartlett/Newey-West lag 19, minimum 730 OOS PASS threshold, primary-first release policy and a create-only pre-execution Stage-1 run marker. Baseline and augmented rows/labels/training dates are identical; augmented differs only by the two frozen Stablecoin columns. The interface is synthetic-tested only and has not executed real Stage-1 data/model logic.

The Stage-1 execution branch adds the irreversible marker claim and an armed push-only executor. Before any Ridge evaluation, it must verify the frozen Stablecoin raw SHA256, capture and durably archive exact Binance daily pages, archive a hash-bound durability receipt, build the canonical P3.2 batch state path, and match `calculate_target()` on all six frozen parity dates. Predictions/coefficients are never persisted; only the frozen primary-result JSON may be durably archived and released. A GitHub rerun is blocked by `github.run_attempt == 1`.

A Stage-1 PASS cannot modify BRRK, write an admitted edge, create a multiplier, authorize leverage/shorts, change Phase 7 or confer production authority. It can only make a separately preregistered robustness-stage research ID eligible to start. `ONCHAIN-HOLDER-COST-0001` remains backlog and is not registered or run.

The deterministic audit may report `WARNING` for real legacy governance debt; that is intentional and must not be converted into a false clean `PASS` by inventing history.

Final governance report: `docs/PROGRAM_LEVEL_EPISTEMIC_GOVERNANCE_V1_FINAL_REPORT_2026-08-08.md`.

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
RESUME REAL PHASE-6 ZERO-AUTHORITY ELAPSED OBSERVATION UNDER GOVERNANCE V1 PROVENANCE
ACCUMULATE GENUINELY FUTURE PHASE-6 EVIDENCE ONLY; DO NOT REBUILD OR BACKFILL ELAPSED TIME
KEEP signature_authorized = false AND order_submission_authorized = false
REQUIRE AT LEAST 14 ELAPSED CALENDAR DAYS AND 10 SCHEDULED DECISIONS PLUS FROZEN QUALITY CRITERIA
MERGE THE STABLECOIN STAGE-1 EXECUTION PR ONLY AFTER GOVERNANCE + SYNTHETIC EXECUTOR SELF-TEST + NO-DRIFT + P3.2 PARITY/GOLDEN + PHASE-6 SAFETY CHECKS PASS
KEEP THE TEMPORARY LIVE FIRST-CAPTURE EXECUTOR REMOVED AFTER THE SUCCESSFUL 824f5815 CAPTURE; DO NOT EXECUTE A SECOND FIRST CAPTURE
RUN INTERFACE STABLECOIN-LIQUIDITY-0001-RUN-INTERFACE-V1 REMAINS FROZEN_NOT_EXECUTED; THE EXECUTION PR MAY IMPLEMENT ONLY THAT FROZEN INTERFACE AND MAY NOT MODIFY ITS ECONOMIC/STATISTICAL DEGREES OF FREEDOM
RESEARCH REGISTRY BINDS STABLECOIN-LIQUIDITY-0001-DEFILLAMA-HIST-V1 AND VALIDATION EXPOSURE STABLECOIN-LIQUIDITY-0001-RAW-DATA-20260808T141719Z WHILE result_status REMAINS PREREGISTERED_NOT_RUN AND actual_variants_evaluated REMAINS 0
CURRENT STAGE-1 EXECUTION PR HAS CLAIMED RUN_ONCE_STAGE1.marker AND ARMED STABLECOIN-LIQUIDITY-0001-STAGE1-RUN-V1; IF MERGED THE CLAIM MAY NEVER BE DELETED EVEN IF EXECUTION FAILS OR INVALIDATES
PULL-REQUEST CI MUST NOT FIT RIDGE ON REAL DATA, CONSTRUCT REAL OOS PREDICTIONS, RUN STAGE-1 OR RELEASE A RESULT; PR CI IS SYNTHETIC/PREFLIGHT ONLY
ONLY A FULLY GREEN MERGE COMMIT CONTAINING [STABLECOIN_STAGE1_EXECUTE_V1] MAY RUN THE SINGLE STAGE-1 VARIANT, AND ONLY ON github.run_attempt == 1; NO RESCUE TUNING, NO AUTOMATIC OR MANUAL RERUN UNDER THIS RESEARCH ID
CLASSIFY HISTORICAL DATA AS RESEARCHER_EXPOSED_HISTORY; DO NOT CLAIM TEMPORALLY_UNSEEN FROM RECONSTRUCTED HISTORY
DO NOT SELECT OR TRIM THE HISTORICAL WINDOW BASED ON VALUES OR RESEARCH PERFORMANCE
START GENUINELY FORWARD RAW-VINTAGE COLLECTION ONLY UNDER A SEPARATELY FROZEN RECURRING-COLLECTION CONTRACT; DO NOT BACKFILL FIRST-SEEN HISTORY
KEEP ONCHAIN-HOLDER-COST-0001 AS BACKLOG UNTIL THE STABLECOIN INFORMATION TEST REACHES ITS FROZEN STOPPING POINT
DO NOT START SUPERTrend / FUNDING-OI / RELATIVE-STRENGTH / NEW-ALLOCATION RESEARCH AS PART OF PHASE-6 OBSERVATION
DO NOT CHANGE BRRK / BNB / PARAMETERS / COSTS / HISTORICAL EVIDENCE / PRODUCTION AUTHORITY
DO NOT ACTIVATE PHASE 7 WITHOUT THE COMPLETE CHECKLIST AND EXPLICIT OWNER APPROVAL
DO NOT RUN BEAR-SHORT-0001 ECONOMICS WITHOUT THE FROZEN CONFIRMED-BEAR TRIGGER
DO NOT AUTHORIZE A FIRST REAL SHORT WITHOUT THE SEPARATE HUMAN GATE
```
