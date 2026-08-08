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
Phase 6 identity-binding rules    PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / MERGED #135 / ADDRESS UNBOUND
Phase 6 pre-arm dependencies      3/4 FROZEN / ACCOUNT IDENTITY UNRESOLVED
Dual-layer architecture sanity    COMPLETE NON-PROMOTABLE DIAGNOSTIC / #136 CANDIDATE
Phase 7                           MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                           TRIGGER ABSENT / NOT RUN
Stablecoin Stage-1               FAIL_NO_INCREMENTAL_INFORMATION / TERMINAL STOP
production gross cap              1.0
production_authorized_components = []
first real short authority        NONE
```

Authoritative main before PR #136:

```text
112a2373e0f9d75d85e04c1d58b0a96e45713eac
```

## Frozen product / authority boundaries

```text
directional core                  BRRK-0011
long universe                     BTC / ETH / SOL / BNB
XRP                               feature-only
primary venue                     Hyperliquid
decision boundary                 00:00 UTC
P3.2 target engine                P3.2-BRRK0011-V1
P3.3 rebalance control            P3.3-L1-BAND-V1 / aggregate L1 0.05
BNB route policy                  PERP_ONLY_DEFAULT
production gross cap              1.0
production_authorized_components = []
P5 cycle overlay                  none promoted
production leverage >1            none promoted
first real short authority        none
```

Credentials, `TRADING_MODE=trade`, research results, shadow implementation or elapsed evidence do not create production authority. Automated withdrawal/external-transfer authority remains outside scope.

## Immutable negative research closeout

- `LEVERAGE-0040` / `LEVERAGE-0041`: immutable `NO_PROMOTION`;
- P5.5: immutable `NO_PROMOTION_FAIL_STOP`; P5.6 blocked;
- `STABLECOIN-LIQUIDITY-0001`: terminal `FAIL_NO_INCREMENTAL_INFORMATION / NO_PROMOTION`;
- Stablecoin OOS `933`, mean primary loss differential `-5430210.12771038`, HAC p `0.8935124773215692`;
- Stablecoin primary-result digest `d920d45397d45ae5636a2f3c682600778d4d087d97e035ba911844cca65821ff`;
- no same-ID Stablecoin rerun/rescue, Stage-2 eligibility, edge admission or direct portfolio integration.

## Program governance v1

```text
legacy_boundary_commit       896cbd123b7a0c38943815dd802f0f9dcd12e1c2
research_governance_version  1
```

Decision, research, dataset exposure, edge and phase/live authority remain separated. Historical unknowns remain explicit governance debt; they are not reconstructed from guesses.

## Phase 6 — live clock remains unstarted

```text
implementation/replay                PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY
live elapsed status                  MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT
minimum elapsed days                 14
minimum genuine scheduled decisions 10
minimum emergency drills             1
critical reconciliation errors       0 required
unexplained target drift              0 required
schedule failures                     0 required
collector_armed                       false
schedule_configured                   false
elapsed_evidence_credit_authorized    false
production_authorized                 false
signature_authorized                  false
order_submission_authorized           false
```

Historical replay, CI replay, reruns and duplicate decision timestamps create no elapsed credit.

### Durable evidence backend — merged #133

`PHASE6-LIVE-EVIDENCE-BACKEND-V1` is frozen to GitHub Actions Artifact v4 with 90-day retention, `overwrite=false`, immutable artifact identity and separately uploaded hash-bound receipt. The backend creates zero elapsed credit by itself.

### Valuation contract — merged #134

`PHASE6-LIVE-VALUATION-V1` supports only explicit Hyperliquid Standard mode (`userAbstraction=disabled`). It maps allowed spot plus signed perp exposure into the already-frozen P3.3 inputs. BTC/ETH/SOL spot identities remain UBTC/UETH/USOL; BNB spot remains forbidden. Unsupported modes/assets fail closed.

### Account identity binding rules — merged #135

`PHASE6-LIVE-ACCOUNT-IDENTITY-V1` is merged, but no observation account is bound:

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

The rules require a real 42-character Hyperliquid master/subaccount public address. Agent/API wallet substitution and private-key discovery are forbidden. A future valid binding must persist non-secret provenance and raw `userRole` / `userAbstraction` response digests.

### Four pre-arm dependencies

```text
1. observation account identity              UNRESOLVED / ADDRESS NOT PROVIDED
2. current-position/equity valuation         FROZEN / MERGED #134
3. durable create-only evidence backend      FROZEN / MERGED #133
4. schedule + duplicate-credit rule          FROZEN
```

Phase 6 remains **3/4** and `dependencies_ready=false`. Even after 4/4, a separate prospective arm change is required; the first eligible scheduled decision is the first canonical `00:00 UTC` decision strictly after the arm commit.

## Dual-layer architecture sanity — PR #136 candidate

The original Internal BRRK + External Structural Signal architecture has now been tested as a **non-promotable mechanical diagnostic** without modifying P3.1, P3.2, P3.3, router, executor or Phase-6 runtime.

Frozen composition before economics:

```text
Internal engine                 canonical BRRK-0011 / P3.2 unchanged
External development input      already-exposed Stablecoin history only
External SUPPORTIVE cap          1.00
External NEUTRAL cap             0.80
External RESTRICTIVE cap         0.60
External may increase gross      false
Relative asset ranking change    false
New assets / shorts / >1 gross   false / false / false
Variant budget                   1
Post-result retuning             forbidden
Promotion eligibility            false
```

The one-shot diagnostic reused the same authoritative BRRK target reconstruction and the same P3.3 economic simulator used by P5.5. Before candidate economics were accepted, the matched P3.3 baseline was required to reproduce the frozen reference exactly.

Matched 2022-12-10 through 2026-08-02, 5 bps, P3.3 L1 band 0.05:

```text
metric               baseline            fused               fused - baseline
CAGR                 65.3056777%         57.2191846%         -8.0864931 pp
Max drawdown        -33.5292296%        -32.5723083%         +0.9569213 pp
Sharpe                1.3561161           1.3556295           -0.0004867
Calmar                1.9477238           1.7566819           -0.1910419
Average gross         0.7543536           0.6522044           -0.1021493
Turnover             91.0866089         103.1500774          +12.0634684
End multiple          6.2525274           5.2073862           -1.0451412
```

External target-row states were `SUPPORTIVE=514`, `NEUTRAL=546`, `RESTRICTIVE=273`.

Result classification:

```text
mechanical fusion changes timing/exposure   true
CAGR improvement                            false
MDD improvement                             small only
risk-adjusted improvement                   false
turnover improvement                        false
promotion_eligible                          false
production_authorized                       false
```

This result demonstrates that the external layer is mechanically capable of changing buy/sell and exposure timing, but **this frozen Stablecoin state-to-cap mapping is not an acceptable integration candidate**. The roughly 8.09 percentage-point CAGR loss is not justified by roughly 0.96 percentage-point MDD improvement, and turnover worsens. Do not retune the observed 1.00/0.80/0.60 mapping in the same diagnostic.

Evidence is frozen in `research/governance/dual_layer_fusion_sanity_result.json`. Because the Stablecoin history was already researcher-exposed and its original research ID is terminal FAIL, this diagnostic cannot validate or promote an external edge and does not rescue `STABLECOIN-LIQUIDITY-0001`.

## Phase 7 / 8

Phase 7 remains `MONITOR_ONLY`, launch-blocked and `production_authorized=false`.

Phase 8 remains trigger-absent/not-run with `short_ready=false`, `production_authorized=false` and `first_real_short_authorized=false`.

## Current drift assessment

PR #136 is intended to remain `DRIFT_0` at the canonical product/economic-authority layer:

- no canonical BRRK target mathematics changed;
- no P3.2/P3.3/router/executor/Phase-6 runtime changed;
- no Stablecoin terminal result changed;
- no candidate was promoted;
- no production/signature/submission authority changed;
- the temporary diagnostic CI wiring was restored to the canonical workflow blob before final-head review.

## Exact next action

```text
1. COMPLETE FINAL-HEAD GOVERNANCE / NO-DRIFT / HANDOFF CI FOR #136
2. MERGE #136 ONLY IF THE FINAL HEAD IS GREEN AND CORE EXECUTION BLOBS REMAIN UNCHANGED
3. DO NOT RETUNE THE OBSERVED STABLECOIN STATE/CAPS
4. RETURN TO THE UNIQUE PHASE-6 PRE-ARM BLOCKER: ONE EXACT PUBLIC HYPERLIQUID MASTER/SUBACCOUNT ADDRESS
5. VERIFY userRole=user OR subAccount AND userAbstraction=disabled
6. ONLY AFTER VALID IDENTITY BINDING REACHES 4/4, STOP AGAIN BEFORE A SEPARATE PROSPECTIVE ARM CHANGE
7. ANY FUTURE DUAL-LAYER EDGE STUDY MUST USE A NEW PROSPECTIVE RESEARCH ID AND INDEPENDENT/UNEXPOSED EVIDENCE
8. KEEP PHASE 7 MONITOR_ONLY AND ALL PRODUCTION/SIGNATURE/SUBMISSION AUTHORITY FALSE
```
