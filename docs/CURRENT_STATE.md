# BRRK Current State

Last updated: 2026-08-08  
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / no eligible >1 candidate
production gross cap              1.0
production_authorized_components = []
P5.1-P5.4                         COMPLETE / FROZEN
P5.5 validation                   COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6 cycle integration            BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 observation preactivation PREACTIVATION_BLOCKED_FAIL_CLOSED
Phase 6 durable evidence backend  FROZEN / ACTIONS_ARTIFACT_V4 / 90D / NO CREDIT / MERGED #133
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / CANDIDATE #134 / STANDARD MODE ONLY
Phase 6 pre-arm dependencies      3 OF 4 FROZEN IN #134 CANDIDATE / ACCOUNT IDENTITY UNRESOLVED
Phase 7 readiness gate            IMPLEMENTED / MERGED #110 / LAUNCH BLOCKED
Phase 7 program state             MONITOR_ONLY
Phase 8 bear-short research       PREREGISTERED_TRIGGER_ABSENT_NOT_RUN / MERGED #111
Program epistemic governance v1   PG0-PG6 COMPLETE / CI-ENFORCED / NO-DRIFT
Stablecoin liquidity Stage-1      FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION / TERMINAL STOP
production authorization          NONE
first real short authorization    NONE
```

Current authoritative `main` before PR #134: `af8ff7c6ce3bf16dd81ab9f510393d38fc790b63`.

## Frozen product / authority boundaries

- directional core: `BRRK-0011`;
- target/tradable long universe: `BTC / ETH / SOL / BNB`;
- XRP remains feature-only;
- primary venue: Hyperliquid;
- canonical daily decision boundary: `00:00 UTC`;
- P3.2 target engine remains `P3.2-BRRK0011-V1`;
- P3.3 control remains `P3.3-L1-BAND-V1`, aggregate L1 band `0.05`;
- production gross cap remains `1.0`;
- no P5 cycle overlay was promoted;
- no >1 production leverage was promoted;
- no production component is authorized;
- no automated withdrawal/external-transfer authority;
- credentials or `TRADING_MODE=trade` do not create production authority;
- first transition from zero exposure to risk-on remains human-gated;
- no first real short is authorized.

## Immutable research closeout

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`. P5.5 remains immutable `NO_PROMOTION_FAIL_STOP`; P5.6 is ineligible.

```text
LEVERAGE-0040 summary SHA256  3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0
P5.5 result commit             ae20890d87567c98e403e3558219d5de55daef67
P5.5 summary SHA256            ccbdc067f9f7f1277e6eecaa2f74f31f84e3a1882ccef418e097b2ea66bf6e71
```

`STABLECOIN-LIQUIDITY-0001` remains terminal:

```text
result_status                    FAIL_NO_INCREMENTAL_INFORMATION
failure_reason                   PRIMARY_MEAN_LOSS_DIFFERENTIAL_NONPOSITIVE
promotion_state                  NO_PROMOTION
valid_oos_prediction_count       933
mean_primary_loss_differential   -5430210.12771038
hac_test_statistic               -1.2454264237630361
hac_one_sided_p_value            0.8935124773215692
primary_result_digest            d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff
stage1 workflow run              31264048473 / SUCCESS
edge admission                   NONE
stage2 robustness eligibility    NONE
```

`RUN_ONCE_STAGE1.marker` remains permanent; no rerun/rescue under the same ID is allowed.

## Program-Level Epistemic Governance v1

```text
legacy_boundary_commit      = 896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version = 1
```

Authority planes remain separated across decision, research, dataset-exposure, edge and Phase 6/7/8 machine contracts. Future result-bearing research must be prospectively registered; historical unknowns remain explicit governance debt rather than fabricated facts.

## Phase 6 — elapsed evidence remains unstarted

Merged implementation/replay:

```text
status                       PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
production_authorized        false
signature_authorized         false
order_submission_authorized  false
```

Real elapsed acceptance remains:

```text
status                       MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
minimum elapsed days         14
minimum scheduled decisions  10
minimum emergency drills     1
critical reconciliation      0 required
unexplained target drift     0 required
schedule failures            0 required
```

Replay, CI rerun, historical backfill and duplicate timestamps create no elapsed credit.

### Preactivation gate

Machine authority:

- `research/governance/phase6_live_observation_gate.json`
- `research/governance/phase6_live_observation_gate.py`

PR #134 candidate state:

```text
collector_armed                             false
schedule_configured                         false
elapsed_evidence_credit_authorized          false
observation_account_identity_frozen         false
current_position_equity_valuation_frozen    true
durable_create_only_evidence_backend_frozen true
schedule_and_duplicate_credit_rule_frozen   true
dependencies_ready                          false
production_authorized                       false
signature_authorized                        false
order_submission_authorized                 false
```

### Durable evidence backend — merged #133

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` is frozen to GitHub Actions Artifact v4, 90-day retention, `overwrite=false`, immutable artifact identity and a separately uploaded hash-bound receipt. The storage contract creates zero elapsed credit by itself.

### Valuation contract — PR #134 candidate

Machine authority:

- `research/governance/phase6_live_valuation_contract.json`
- `research/governance/phase6_live_valuation.py`

`PHASE6-LIVE-VALUATION-V1` accepts only explicit Hyperliquid Standard mode:

```text
userAbstraction = disabled
```

Unsupported Unified/Portfolio-Margin/default/DEX-abstraction states fail closed.

Canonical mapping:

```text
perp component = sign(szi) * abs(positionValue)
spot component = balances[].total * verified spot markPx
P3.3 current_positions_notional_usd = spot + perp by economic asset
```

Spot identities remain:

```text
BTC -> UBTC
ETH -> UETH
SOL -> USOL
BNB -> PERP_ONLY_DEFAULT / spot forbidden
```

Standard-mode equity is first-perp-dex `marginSummary.accountValue` + spot USDC + permitted canonical spot mark-to-market. Unknown nonzero assets, duplicate identities, invalid marks, nonpositive equity and unsupported surfaces hard fail.

### Four pre-arm dependencies

```text
1. observation account identity              UNRESOLVED
2. current-position/equity valuation         FROZEN IN #134 CANDIDATE
3. durable create-only evidence backend      FROZEN / MERGED #133
4. schedule + duplicate-credit rule          FROZEN
```

Therefore #134 moves the candidate state to **3/4** but does not arm the collector. If #134 merges after final green CI, only one external dependency remains: one exact verified public read-only Hyperliquid master/subaccount address compatible with Standard mode. Do not invent or derive that address from a private key.

## Phase 7 / 8

Phase 7 remains `MONITOR_ONLY`, launch-blocked and `production_authorized=false`.

Phase 8 remains `PREREGISTERED_TRIGGER_ABSENT_NOT_RUN`, `short_ready=false`, `production_authorized=false`, `first_real_short_authorized=false`.

## Drift status for PR #134

The first candidate governance run passed the valuation unit tests, preactivation gate, registry validation and prospective-research enforcement. Its only no-drift failure was two temporary new documentation paths outside the Governance-v1 allowlist. Those paths were removed; the allowlist was not broadened.

Canonical strategy/economic/authority state remains unchanged:

```text
BRRK-0011                         unchanged
BTC/ETH/SOL/BNB long universe    unchanged
XRP feature-only                 unchanged
Hyperliquid primary venue        unchanged
00:00 UTC decision boundary      unchanged
P3.2 target engine               unchanged
P3.3 L1 band                     unchanged
production gross cap = 1.0       unchanged
production_authorized_components []
Phase 7 MONITOR_ONLY             unchanged
Phase 8 short authority          none
Stablecoin terminal FAIL         unchanged
```

Final #134 merge requires a fresh green final-head protection matrix. Historical/intermediate failures are not relabeled as PASS.

## Exact next action

```text
1. RUN FINAL #134 CI/GOVERNANCE
2. EXPECTED-HEAD MERGE #134 ONLY IF ALL REQUIRED CHECKS ARE GREEN
3. VERIFY NEW MAIN AND CANONICAL NO-DRIFT INVARIANTS
4. FREEZE ONE EXACT PUBLIC READ-ONLY HYPERLIQUID MASTER/SUBACCOUNT ADDRESS
5. VERIFY userAbstraction=disabled AND PHASE6-LIVE-VALUATION-V1 COMPATIBILITY
6. DO NOT USE/DERIVE A PRIVATE KEY TO ESTABLISH OBSERVATION IDENTITY
7. ONLY AT 4/4 PRE-ARM DEPENDENCIES, CREATE A SEPARATE PROSPECTIVE ARM CHANGE
8. FIRST ELIGIBLE SCHEDULED DECISION = FIRST 00:00 UTC STRICTLY AFTER ARM COMMIT
9. NEVER BACKFILL / REPLAY-CREDIT / RERUN-CREDIT / DUPLICATE-CREDIT
10. KEEP PHASE 7 MONITOR_ONLY AND ALL PRODUCTION/SIGNATURE/SUBMISSION AUTHORITY FALSE
```

After Phase-6 collection is genuinely operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting. Do not substitute new result-bearing research for the remaining Phase-6 dependency.