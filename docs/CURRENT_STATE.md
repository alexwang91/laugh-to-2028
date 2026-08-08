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
Stablecoin liquidity research     STABLECOIN-LIQUIDITY-0001 / ONE-SHOT CAPTURE EXECUTION ARMED / NO FULL HISTORY / NO RESULT
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
- `.github/workflows/research-governance.yml` — CI enforcement plus the push-only one-shot Stablecoin capture executor; pull-request CI can never execute the live capture job.

PG4 conservatively maps 17 `RETROSPECTIVE_LEGACY` research records. Six governance-debt classes remain explicit because historical trial counts, information releases, dataset consumption, lineage, informal researcher decisions and complete candidate universes cannot be reconstructed truthfully. `UNKNOWN` remains `UNKNOWN`.

The Dataset Exposure Registry remains empty for retrospective history rather than inventing release/consumption events. The Edge Registry remains empty because no legacy feature was retroactively declared a governance-v1 independent/incremental edge.

Future formal result-bearing research must be prospectively covered by exactly one `PROGRAM_GOVERNED_V1` record with the frozen required fields, declared path ownership, variant budget, stopping rules, lineage/data references and `production_authorized=false`. Changed legacy formal research paths are treated as new post-boundary research activity and cannot bypass prospective registration or existing immutable-evidence correction rules.

PR #121 repairs the cross-gate conflict between future-research registration and the final no-drift regression without broadening the legacy allowlist. A post-boundary formal `research/**` path is eligible only when exactly one valid `PROGRAM_GOVERNED_V1` record owns it, its governed prefix did not exist at the legacy boundary, and the registration already existed at the path's first introduction commit. Rename/copy laundering of legacy research and post-hoc registration remain blocking. This repair changes governance enforcement only and creates no research, strategy, evidence or production authority.

PR #122 repairs a second preregistration-only validator contradiction. Required future fields must be present, while pre-result accounting arrays such as secondary metrics, dataset refs, lineage and evidence refs may truthfully remain empty. `PREREGISTERED_NOT_RUN` explicitly blocks result evidence, evaluated variants and promotion. This prevents fake placeholder provenance while keeping result-bearing states fail-closed. The repair changes governance validation only and does not itself preregister or run research.

PR #123 prospectively registered `STABLECOIN-LIQUIDITY-0001` before its governed formal path existed. That registration remains the frozen Stage-1 hypothesis/metric/variant boundary; the data-contract work below does not alter its research result criteria.

PR #124 froze the Stablecoin source/data/PIT contract and created the prospectively owned formal path without retrieving full history or releasing a result. PR #125 froze the one-shot first-capture gate without executing it. PR #126 split the gate into capture/persist and finalize phases so a durable external archive receipt must exist before any raw payload parsing. The current execution PR arms a push-only GitHub Actions executor; it remains non-executing on pull requests and only runs after a main push whose head commit contains the frozen execution token.

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
capture gate                  STABLECOIN-LIQUIDITY-0001-FIRST-CAPTURE-GATE-V1 / FROZEN_NOT_EXECUTED / TWO-STAGE DURABLE RECEIPT REQUIRED
capture execution             STABLECOIN-LIQUIDITY-0001-FIRST-CAPTURE-EXECUTION-V1 / ARMED_NOT_EXECUTED / MAIN-PUSH TOKEN ONLY
primary source                DEFILLAMA-STABLECOIN-ALL-CHARTS-V1
source endpoint               https://stablecoins.llama.fi/stablecoincharts/all
historical full capture       NOT RUN
real feature computation      NOT RUN
dataset refs                  []
dataset exposure registry     NO STABLECOIN SLICE YET
research evidence             NONE
edge admission                NONE
portfolio integration         NONE
```

The frozen source reference is the official `DefiLlama/api-sdk` repository at commit `f0d43119c746dda0c1ad8460c37ac9e00e8e5161`, repository package version `0.1.4`. The official SDK maps `stablecoins.getAllCharts()` to `GET https://stablecoins.llama.fi/stablecoincharts/all` and exposes the Stage-1 raw value as `totalCirculatingUSD.peggedUSD` with observation time in the `date` Unix-timestamp string.

The reviewed source schema exposes observation time but no historical per-row publication timestamp or original historical first-seen vintage. Historical data therefore remains `RECONSTRUCTED_HISTORY / RESEARCHER_EXPOSED_HISTORY`; the preregistered primary availability rule remains `available_at = metric_timestamp + 2 calendar days`. Later source revisions cannot be backdated into earlier decision views.

Historical coverage is frozen before retrieval rather than selected after performance inspection:

```text
cutoff = 2026-08-08T00:00:00Z
start  = earliest schema-valid row returned by the frozen endpoint
end    = latest schema-valid row <= cutoff
use every valid row in the frozen coverage; no result-driven date selection
```

Concrete historical `start/end` and dataset version are intentionally not fabricated in `config/dataset_exposure_registry.json`. They become knowable only after the first immutable full-history capture and must then be registered before result-bearing model evaluation.

Raw-vintage semantics are frozen as exact-response-byte SHA256 plus create-only local staging and durable external versioned archival. Raw source payloads are gitignored. Schema drift, duplicate timestamps, non-200 captures, raw-hash mismatch and silent overwrite are hard failures.

The first-capture gate requires the strict order `FETCH ONCE -> PERSIST RAW -> PERSIST MANIFEST -> VERIFY -> ARCHIVE RAW+MANIFEST TO DURABLE EXTERNAL STORE -> CREATE DURABILITY RECEIPT -> VERIFY RECEIPT -> PARSE PERSISTED BYTES -> SELECT FROZEN COVERAGE -> EMIT METADATA ONLY`. The capture stage deliberately stops before parsing. If any first-capture artifact already exists, another fetch is blocked until manual reconciliation.

The armed executor uses `GITHUB_ACTIONS_ARTIFACT_V4` as the first durable external archive. It is conditioned on a `push` to `main` whose head commit contains `[STABLECOIN_FIRST_CAPTURE_EXECUTE_V1]`; pull-request events cannot execute it. Exact raw + manifest + staging metadata are uploaded with `overwrite=false` before any parsing. The returned artifact ID/URL is bound into the create-only durability receipt. A same-run rerun that finds the raw artifact hard-fails before source fetch. The executor releases only provenance/coverage metadata and cannot mutate the Dataset Registry, compute features, fit Ridge, run Stage 1, change BRRK or confer production authority.

Governance-v1 Dataset Registry schema does not contain a `raw_hash` dataset-slice property and rejects unregistered properties. Dataset slice identity therefore records source/field/resolution/start/end/transformation/PIT/budget/contamination semantics; exact raw SHA256, byte length, retrieval time, response headers, raw object identity and parser version remain immutable manifest/provenance properties. Durable backend/object references and manifest SHA256 remain durability-receipt provenance.

The primary feature definition remains aggregate USD-pegged stablecoin value 20-day log growth plus 20-day growth acceleration with exact lag-date matching. Missing dates are not interpolated or forward-filled. No real feature series, model, prediction, backtest or performance result has been produced by the data-contract or capture-gate work.

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
MERGE THE STABLECOIN ONE-SHOT EXECUTION PR WITH THE EXACT [STABLECOIN_FIRST_CAPTURE_EXECUTE_V1] HEAD-COMMIT TOKEN ONLY AFTER ALL PR CI IS GREEN
ON THAT SINGLE MAIN PUSH, EXECUTE EXACTLY ONE FROZEN-SOURCE FETCH INTO OUT-OF-REPO CREATE-ONLY RUNNER STAGING AND VERIFY RAW + MANIFEST WITHOUT PARSING
UPLOAD EXACT RAW + MANIFEST TO GITHUB_ACTIONS_ARTIFACT_V4 WITH overwrite=false BEFORE ANY PARSE; BIND RETURNED ARTIFACT ID/URL INTO A CREATE-ONLY DURABILITY RECEIPT
ONLY AFTER THE RECEIPT IS VERIFIED, PARSE THE PERSISTED BYTES AND EMIT METADATA-ONLY COVERAGE/PROVENANCE
DO NOT AUTOMATICALLY RERUN A FAILED CAPTURE; IF A RAW ARTIFACT EXISTS FOR THE RUN, REFUSE ANY SECOND FETCH AND REQUIRE MANUAL RECONCILIATION
AFTER SUCCESS, MIRROR THE RAW/PROVENANCE ARTIFACT INTO CHATGPT LIBRARY WHEN AVAILABLE WITHOUT ALTERING ITS HASH IDENTITY
MATERIALIZE THE TRUTHFUL HISTORICAL DATASET SLICE IDENTITY ONLY AFTER THE CAPTURE ESTABLISHES OBSERVED START/END; KEEP RAW SHA256 IN IMMUTABLE MANIFEST/PROVENANCE, NOT AS AN UNREGISTERED DATASET-SLICE PROPERTY
CLASSIFY HISTORICAL DATA AS RESEARCHER_EXPOSED_HISTORY; DO NOT CLAIM TEMPORALLY_UNSEEN FROM RECONSTRUCTED HISTORY
DO NOT SELECT OR TRIM THE HISTORICAL WINDOW BASED ON VALUES OR RESEARCH PERFORMANCE
DO NOT FIT RIDGE, CONSTRUCT OOS PREDICTIONS, RUN THE STAGE-1 INFORMATION TEST, GENERATE A SIGNAL OR RELEASE A RESULT UNTIL THE DATASET SLICE AND RUN INTERFACE ARE FROZEN
START GENUINELY FORWARD RAW-VINTAGE COLLECTION ONLY WITH DURABLE CREATE-ONLY/VERSIONED STORAGE; DO NOT BACKFILL FIRST-SEEN HISTORY
KEEP ONCHAIN-HOLDER-COST-0001 AS BACKLOG UNTIL THE STABLECOIN INFORMATION TEST REACHES ITS FROZEN STOPPING POINT
DO NOT START SUPERTrend / FUNDING-OI / RELATIVE-STRENGTH / NEW-ALLOCATION RESEARCH AS PART OF PHASE-6 OBSERVATION
DO NOT CHANGE BRRK / BNB / PARAMETERS / COSTS / HISTORICAL EVIDENCE / PRODUCTION AUTHORITY
DO NOT ACTIVATE PHASE 7 WITHOUT THE COMPLETE CHECKLIST AND EXPLICIT OWNER APPROVAL
DO NOT RUN BEAR-SHORT-0001 ECONOMICS WITHOUT THE FROZEN CONFIRMED-BEAR TRIGGER
DO NOT AUTHORIZE A FIRST REAL SHORT WITHOUT THE SEPARATE HUMAN GATE
```
