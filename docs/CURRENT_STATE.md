# BRRK Current State

Last updated: 2026-08-08  
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                         COMPLETE / MERGED
Phase 4 leverage research         FAIL_STOP / NO_PROMOTION
P5.5                              COMPLETE / IMMUTABLE / NO_PROMOTION / FAIL_STOP
P5.6                              BLOCKED / NO ELIGIBLE CANDIDATE
Phase 6 implementation/replay     PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence     MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 evidence backend          FROZEN / MERGED #133
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / PR #134 CANDIDATE
Phase 6 pre-arm dependencies      3/4 FROZEN IN #134 CANDIDATE / ACCOUNT IDENTITY UNRESOLVED
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Stablecoin Stage-1               FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP
production gross cap              1.0
production_authorized_components = []
first real short authority        NONE
```

Authoritative `main` before PR #134: `af8ff7c6ce3bf16dd81ab9f510393d38fc790b63`.

## Frozen product / authority boundaries

```text
directional core                 BRRK-0011
long universe                    BTC / ETH / SOL / BNB
XRP                              feature-only
primary venue                    Hyperliquid
decision boundary                00:00 UTC
P3.2 target engine               P3.2-BRRK0011-V1
P3.3 rebalance control           P3.3-L1-BAND-V1 / aggregate L1 0.05
BNB route policy                 PERP_ONLY_DEFAULT
production gross cap             1.0
production_authorized_components []
P5 cycle overlay                 none promoted
production leverage >1           none promoted
first real short authority       none
```

Credentials, `TRADING_MODE=trade`, historical confirmations or shadow implementation do not create production authority. Automated withdrawal/external-transfer authority remains outside scope.

## Immutable research closeout

`LEVERAGE-0040` and `LEVERAGE-0041` remain immutable `NO_PROMOTION`; P5.5 remains immutable `NO_PROMOTION_FAIL_STOP`; P5.6 remains blocked.

Stablecoin primary result remains:

```text
result_status                    FAIL_NO_INCREMENTAL_INFORMATION
valid_oos_prediction_count       933
mean_primary_loss_differential   -5430210.12771038
hac_test_statistic               -1.2454264237630361
hac_one_sided_p_value            0.8935124773215692
primary_result_digest            d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff
promotion_state                  NO_PROMOTION
edge admission                   NONE
stage2 robustness eligibility    NONE
```

`RUN_ONCE_STAGE1.marker` remains permanent; no same-ID rerun/rescue is permitted.

## Governance v1

```text
legacy_boundary_commit      896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version 1
```

Decision, research, dataset-exposure, edge and phase/live authority remain separated. Future result-bearing research must be prospectively registered; historical unknowns remain explicit governance debt.

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

Historical replay, CI replay, reruns and duplicate decision timestamps create no elapsed credit.

### Durable evidence backend — merged #133

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` is frozen to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity and a separately uploaded hash-bound receipt. The backend creates zero elapsed credit by itself.

### Valuation contract — PR #134 candidate

Machine authority:

- `research/governance/phase6_live_valuation_contract.json`
- `research/governance/phase6_live_valuation.py`

V1 supports only explicit Hyperliquid Standard mode:

```text
userAbstraction = disabled
```

Unsupported Unified Account, Portfolio Margin, `default`, DEX abstraction and unsupported account surfaces fail closed.

Canonical mapping:

```text
perp component = sign(szi) * abs(positionValue)
spot component = balances[].total * verified spot markPx
current_positions_notional_usd = spot + perp by economic asset
```

Spot identities remain `BTC->UBTC`, `ETH->UETH`, `SOL->USOL`; BNB spot remains forbidden.

Standard-mode equity is first-perp-dex `marginSummary.accountValue` + spot USDC + permitted canonical spot mark-to-market. Unknown nonzero assets, duplicate identities, invalid marks, nonpositive equity and unsupported surfaces hard fail.

### Four pre-arm dependencies

```text
1. observation account identity              UNRESOLVED
2. current-position/equity valuation         PR #134 CANDIDATE / TESTED
3. durable create-only evidence backend      FROZEN / MERGED #133
4. schedule + duplicate-credit rule          FROZEN
```

#134 therefore represents **3/4 candidate readiness**, but nothing is armed:

```text
collector_armed                    false
schedule_configured                false
elapsed_evidence_credit_authorized false
dependencies_ready                 false
production_authorized              false
signature_authorized               false
order_submission_authorized        false
```

If #134 passes final CI and merges, the only remaining pre-arm dependency is one exact verified public read-only Hyperliquid master/subaccount address compatible with Standard mode. Do not invent or derive that address from a private key.

## Phase 7 / 8

Phase 7 remains `MONITOR_ONLY`, launch-blocked and `production_authorized=false`.

Phase 8 remains trigger-absent/not-run with `short_ready=false`, `production_authorized=false` and `first_real_short_authorized=false`.

## Drift status for PR #134

The first candidate governance run passed valuation unit tests, preactivation gate, registry validation and future-research enforcement. Its only no-drift failure was two temporary candidate `docs/**` paths outside the Governance-v1 allowlist. They were removed; the allowlist was not broadened.

Canonical product/strategy/economic/production authority remains unchanged. Final merge requires a fresh green final-head governance/no-drift/parity/Phase-6 safety matrix; intermediate failures are not relabeled as PASS.

## Exact next action

```text
1. RUN FINAL #134 CI/GOVERNANCE
2. EXPECTED-HEAD MERGE #134 ONLY IF REQUIRED CHECKS ARE GREEN
3. VERIFY NEW MAIN + NO-DRIFT INVARIANTS
4. FREEZE ONE EXACT PUBLIC READ-ONLY HYPERLIQUID MASTER/SUBACCOUNT ADDRESS
5. VERIFY userAbstraction=disabled + PHASE6-LIVE-VALUATION-V1 COMPATIBILITY
6. DO NOT USE/DERIVE A PRIVATE KEY TO ESTABLISH OBSERVATION IDENTITY
7. ONLY AT 4/4 DEPENDENCIES CREATE A SEPARATE PROSPECTIVE ARM CHANGE
8. FIRST CREDITED DECISION = FIRST 00:00 UTC STRICTLY AFTER ARM COMMIT
9. NEVER BACKFILL / REPLAY-CREDIT / RERUN-CREDIT / DUPLICATE-CREDIT
10. KEEP PHASE 7 MONITOR_ONLY AND ALL PRODUCTION/SIGNATURE/SUBMISSION AUTHORITY FALSE
```

After genuine Phase-6 collection becomes operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting.