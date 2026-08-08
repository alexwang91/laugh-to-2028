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
Phase 6 valuation contract        PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 identity-binding rules    PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / CANDIDATE / ADDRESS UNBOUND
Phase 6 pre-arm dependencies      3/4 FROZEN / ACCOUNT IDENTITY UNRESOLVED
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Stablecoin Stage-1               FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP
production gross cap              1.0
production_authorized_components = []
first real short authority        NONE
```

Authoritative main after PR #134:

```text
4df87148418000c08582319cb395310bc7acdc07
```

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
production_authorized_components = []
P5 cycle overlay                 none promoted
production leverage >1           none promoted
first real short authority       none
```

Credentials, `TRADING_MODE=trade`, historical confirmations or shadow implementation do not create production authority. Automated withdrawal/external-transfer authority remains outside scope.

## Immutable research closeout

- `LEVERAGE-0040` / `LEVERAGE-0041`: immutable `NO_PROMOTION`;
- P5.5: immutable `NO_PROMOTION_FAIL_STOP`; P5.6 blocked;
- `STABLECOIN-LIQUIDITY-0001`: terminal `FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION`;
- Stablecoin OOS `933`, mean primary loss differential `-5430210.12771038`, HAC p `0.8935124773215692`;
- Stablecoin primary-result digest `d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff`;
- no same-ID Stablecoin rerun/rescue, Stage-2 eligibility, edge admission or portfolio integration.

## Governance v1

```text
legacy_boundary_commit      896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version 1
```

Decision, research, dataset-exposure, edge and phase/live authority remain separated. Future result-bearing research must be prospectively registered; historical unknowns remain explicit governance debt.

## Phase 6 — elapsed evidence remains unstarted

```text
implementation/replay              PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
live elapsed status                MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
minimum elapsed days               14
minimum genuine scheduled decisions 10
minimum emergency drills           1
critical reconciliation errors     0 required
unexplained target drift            0 required
schedule failures                   0 required
collector_armed                     false
schedule_configured                 false
elapsed_evidence_credit_authorized  false
production_authorized               false
signature_authorized                false
order_submission_authorized         false
```

Historical replay, CI replay, reruns and duplicate decision timestamps create no elapsed credit.

### Durable evidence backend — merged #133

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` is frozen to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity and a separately uploaded hash-bound receipt. The backend creates zero elapsed credit by itself.

### Valuation contract — merged #134

`PHASE6-LIVE-VALUATION-V1` supports only explicit Hyperliquid Standard mode (`userAbstraction=disabled`). It maps canonical spot + signed perp economic exposure into the existing P3.3 inputs. BTC/ETH/SOL spot identities remain UBTC/UETH/USOL; BNB spot remains forbidden. Unsupported modes/assets fail closed.

### Account identity binding — current candidate

Machine authority:

- `research/governance/phase6_live_account_identity_contract.json`
- `research/governance/phase6_live_account_identity.py`

Current state intentionally remains unbound:

```text
status                         AWAITING_EXPLICIT_PUBLIC_ADDRESS
account_address                null
identity_frozen                false
binding_evidence               null
accepted userRole              user / subAccount
rejected userRole              agent / vault / missing
required userAbstraction       disabled
production_authorized          false
signature_authorized           false
order_submission_authorized    false
elapsed_evidence_credit        false
```

The rules require a real 42-character Hyperliquid master/subaccount public address. An API/agent wallet is not an observation account. For a subaccount, the returned master address is preserved as evidence but cannot silently replace the queried subaccount identity. Private-key input or private-key derivation to discover the address is forbidden.

A future bound identity must persist non-secret address provenance, exact `userRole` / `userAbstraction` observations and raw-response SHA256 digests before `identity_frozen=true` is valid.

### Four pre-arm dependencies

```text
1. observation account identity              UNRESOLVED / ADDRESS NOT PROVIDED
2. current-position/equity valuation         FROZEN / MERGED #134
3. durable create-only evidence backend      FROZEN / MERGED #133
4. schedule + duplicate-credit rule          FROZEN
```

The identity-rule candidate does not change the dependency count. Phase 6 remains **3/4** and `dependencies_ready=false`.

Even after a future valid identity binding completes 4/4, the collector remains unarmed until a separate prospective arm change. The first eligible scheduled decision remains the first canonical `00:00 UTC` decision strictly after the arm commit timestamp.

## Phase 7 / 8

Phase 7 remains `MONITOR_ONLY`, launch-blocked and `production_authorized=false`.

Phase 8 remains trigger-absent/not-run with `short_ready=false`, `production_authorized=false` and `first_real_short_authorized=false`.

## Current drift assessment

After #134, the final full protection matrix was green, including Governance core, Phase 0-8 drift audit, P3.2 research/live parity, Phase-6 integrated-shadow safety and Phase-7/8 contracts. Current account-identity work is confined to the existing `research/governance/**` control plane plus authoritative handoff documents.

No BRRK economics, universe, BNB policy, target/rebalance logic, transaction-cost assumptions, research result, phase acceptance threshold or production authority is changed by the identity-rule candidate.

## Exact next action

```text
1. RUN FINAL CI/GOVERNANCE FOR THE ACCOUNT-IDENTITY-RULE CANDIDATE
2. MERGE ONLY WITH EXPECTED-HEAD PROTECTION IF ALL REQUIRED CHECKS ARE GREEN
3. VERIFY NEW MAIN + NO-DRIFT INVARIANTS
4. OBTAIN ONE EXACT PUBLIC READ-ONLY HYPERLIQUID MASTER/SUBACCOUNT ADDRESS
5. QUERY userRole; ACCEPT ONLY user OR subAccount
6. QUERY userAbstraction; REQUIRE disabled
7. PERSIST NON-SECRET PROVENANCE + RAW-RESPONSE DIGESTS; ONLY THEN SET identity_frozen=true
8. DO NOT USE OR DERIVE A PRIVATE KEY TO DISCOVER THE ADDRESS
9. AT 4/4 DEPENDENCIES, STOP AGAIN BEFORE A SEPARATE PROSPECTIVE ARM CHANGE
10. KEEP PHASE 7 MONITOR_ONLY AND ALL PRODUCTION/SIGNATURE/SUBMISSION AUTHORITY FALSE
```

After genuine Phase-6 collection becomes operational, resume the infrastructure roadmap: formal research lifecycle/state-machine enforcement, then Research Queue / trial-overlap accounting.