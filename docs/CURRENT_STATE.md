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
Stablecoin liquidity research     STABLECOIN-LIQUIDITY-0001 / PREREGISTERED_NOT_RUN / NO DATASET BOUND / NO RESULT
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
- `.github/workflows/research-governance.yml` — CI enforcement.

PG4 conservatively maps 17 `RETROSPECTIVE_LEGACY` research records. Six governance-debt classes remain explicit because historical trial counts, information releases, dataset consumption, lineage, informal researcher decisions and complete candidate universes cannot be reconstructed truthfully. `UNKNOWN` remains `UNKNOWN`.

The Dataset Exposure Registry remains empty for retrospective history rather than inventing release/consumption events. The Edge Registry remains empty because no legacy feature was retroactively declared a governance-v1 independent/incremental edge.

Future formal result-bearing research must be prospectively covered by exactly one `PROGRAM_GOVERNED_V1` record with the frozen required fields, declared path ownership, variant budget, stopping rules, lineage/data references and `production_authorized=false`. Changed legacy formal research paths are treated as new post-boundary research activity and cannot bypass prospective registration or existing immutable-evidence correction rules.

PR #121 repairs the cross-gate conflict between future-research registration and the final no-drift regression without broadening the legacy allowlist. A post-boundary formal `research/**` path is eligible only when exactly one valid `PROGRAM_GOVERNED_V1` record owns it, its governed prefix did not exist at the legacy boundary, and the registration already existed at the path's first introduction commit. Rename/copy laundering of legacy research and post-hoc registration remain blocking. This repair changes governance enforcement only and creates no research, strategy, evidence or production authority.

PR #122 repairs a second preregistration-only validator contradiction. Required future fields must be present, while pre-result accounting arrays such as secondary metrics, dataset refs, lineage and evidence refs may truthfully remain empty. `PREREGISTERED_NOT_RUN` explicitly blocks result evidence, evaluated variants and promotion. This prevents fake placeholder provenance while keeping result-bearing states fail-closed. The repair changes governance validation only and does not itself preregister or run research.

## STABLECOIN-LIQUIDITY-0001

`STABLECOIN-LIQUIDITY-0001` is prospectively registered under `PROGRAM_GOVERNED_V1` as a Stage-1 external-information mechanism test. It asks whether a frozen stablecoin-liquidity information family adds predictive information about future 20-day canonical BRRK outcomes beyond the frozen P3.2 BRRK price/regime state.

Current state is strictly:

```text
result_status              PREREGISTERED_NOT_RUN
promotion_state            NONE
production_authorized      false
declared_variant_budget    1
actual_variants_evaluated  0
governed_path_prefix       research/stablecoin_liquidity_0001/
formal research path       NOT CREATED YET
dataset refs               []
dataset source             NOT BOUND YET
dataset exposure registry  EMPTY
research evidence          NONE
edge admission             NONE
portfolio integration      NONE
```

The preregistration freezes a 20-day Stage-1 incremental-information question, a single fixed Ridge estimator (`alpha=1.0`), training-only expanding normalization, 20-day label purging, and a primary reconstructed-history availability proxy of `metric_date + 2 days` when historical publication timestamps are unverifiable. LAG_1D/LAG_3D are not rescue alternatives for this research ID; they are reserved for a separately preregistered robustness stage if Stage 1 passes.

The primary feature representation is frozen as aggregate USD-pegged stablecoin supply 20-day log growth plus 20-day growth acceleration. DefiLlama remains only a source candidate from the pre-run source audit. No source, exact fields, coverage window, raw payload identity or PIT publication semantics have yet been bound into `config/dataset_exposure_registry.json`; placeholder dataset slices are prohibited.

Historical third-party data without verifiable publication timestamps must remain `RESEARCHER_EXPOSED_HISTORY` / reconstructed history. Only genuinely new raw snapshots collected after a frozen data contract, with immutable retrieval/hash provenance, may later qualify as `TEMPORALLY_UNSEEN`.

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
MERGE THE STABLECOIN-LIQUIDITY-0001 REGISTRY-ONLY PR BEFORE CREATING research/stablecoin_liquidity_0001/
NEXT STABLECOIN PR MUST FREEZE EXACT SOURCE / ENDPOINT / FIELDS / UNIT / COVERAGE / TRANSFORMATION / RAW-VINTAGE IDENTITY / PIT PUBLICATION SEMANTICS / FORWARD-SNAPSHOT IMMUTABILITY BEFORE FULL HISTORICAL RETRIEVAL
KEEP config/dataset_exposure_registry.json EMPTY UNTIL THOSE SLICE IDENTITIES CAN BE FROZEN TRUTHFULLY; DO NOT INVENT PLACEHOLDER SLICES
DO NOT DOWNLOAD FULL STABLECOIN OR HOLDER-COST HISTORY IN THE PREREGISTRATION PR
DO NOT RUN A BACKTEST, FIT A MODEL, GENERATE A SIGNAL, CALCULATE RESEARCH PERFORMANCE OR RELEASE A RESEARCH RESULT BEFORE THE DATA CONTRACT AND RUN INTERFACE ARE FROZEN
KEEP ONCHAIN-HOLDER-COST-0001 AS BACKLOG UNTIL THE STABLECOIN INFORMATION TEST REACHES ITS FROZEN STOPPING POINT
DO NOT START SUPERTrend / FUNDING-OI / RELATIVE-STRENGTH / NEW-ALLOCATION RESEARCH AS PART OF PHASE-6 OBSERVATION
DO NOT CHANGE BRRK / BNB / PARAMETERS / COSTS / HISTORICAL EVIDENCE / PRODUCTION AUTHORITY
DO NOT ACTIVATE PHASE 7 WITHOUT THE COMPLETE CHECKLIST AND EXPLICIT OWNER APPROVAL
DO NOT RUN BEAR-SHORT-0001 ECONOMICS WITHOUT THE FROZEN CONFIRMED-BEAR TRIGGER
DO NOT AUTHORIZE A FIRST REAL SHORT WITHOUT THE SEPARATE HUMAN GATE
```
