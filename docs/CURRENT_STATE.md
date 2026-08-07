# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 base data contract: PASS / MERGED
- PR #71: PASS / MERGED
- PR #72: PASS / MERGED
- PR #73: MERGED as `89b095d7a7d746b768afca8245b963ecf15ffabc`; its required PR governance CI was not recorded green before merge and must not be retroactively labeled CI VERIFIED
- PR #74 P3.1 feature-input parity correction: MERGED as current main `277eb777b4b28d32bb24c201bba1155b08686c71`
- PR #74 head `22a00c894b2ae54a7e1d45ebeefb996e8597182f` had zero recorded workflow runs before merge; current merge SHA also has zero recorded workflow runs during the GitHub Actions incident
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current roadmap position

```text
P3.1 schema-v2 parity implementation   MERGED
P3.1 post-merge validation             REQUIRED / ACTIVE NEXT GATE
P3.2 Target calculation API            BLOCKED UNTIL VALIDATION GATE CLOSES
P3.3+                                  BLOCKED
```

The earlier branch `p3-2/target-calculation-api-v2` was created before the XRP feature-input residual was corrected and contains no P3.2 implementation. Do not reuse it. After the validation gate closes, create a new P3.2 branch from then-current main.

## P3.1 schema-v2 correction now on main

Frozen product target/tradable assets remain exactly:

```text
BTC ETH SOL BNB
```

Frozen BRRK-0011 regime features additionally consume:

```text
XRPUSDT — feature-only
```

Schema v2 therefore distinguishes:

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

The merged correction also preserves fail-closed daily-gap behavior across all five signal series and rejects XRP from funding/basis routing. No BRRK parameter, weight formula, regime parameter, risk budget or risk-scaling rule changed.

## Evidence status for PR #74

```text
IMPLEMENTED:           YES
TESTED:                NOT YET VERIFIED AFTER MERGE
CI VERIFIED:           NO
MERGED:                YES
PRODUCTION AUTHORIZED: NO_CHANGE
```

The lack of CI evidence is an infrastructure/evidence gap, not a claim that tests failed. GitHub Actions was in a major outage and neither the PR head nor the resulting main SHA received a workflow run.

## Frozen BRRK-0011 chain

```text
build_brrk0011_scale
-> fit_variational_regime_model_nd
-> filtered_posterior
-> fit_state_v1_distribution
-> sample_v1_paths
-> choose_scale_corrected
-> meta_scale
-> final_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
-> BRRK_0011_BASELINE = v1_raw.mul(final_scale, axis=0)
```

Frozen target assets remain BTC/ETH/SOL/BNB. Gross/risk scale remains in `[0, 1]`. `EXPOSURE-SMOOTH-0038` remains NOT PROMOTED / BASELINE UNCHANGED.

## P3.2 boundary retained

Once P3.1 v2 validation is green, P3.2 remains target calculation only and must expose at least:

- BTC/ETH/SOL/BNB target/relative weights;
- cash share;
- base gross target <= 1;
- risk state and corrected defensive scale;
- economic decision timestamp;
- feature snapshot;
- model/data-contract/target-engine versions and data digest.

P3.2 must not add P3.3 rebalance/turnover bands, P3.4 contributions, F23 funding-response redesign, P4 >1 leverage, P5 exit intelligence, shorts, XRP target exposure, or production authorization.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_1
```

Reason: the P3.1 feature-input parity implementation is now on main, but the merge occurred with no recorded test or CI run because GitHub Actions/webhook processing was disrupted. Product scope and research authority are aligned; evidence closure is still required before P3.2.

## Exact next action

```text
post-merge P3.1-v2 validation PR
-> Phase 0 full execution pytest + research integration contract
-> PR handoff governance
-> merge validation/handoff normalization
-> verify new main
-> create NEW fresh P3.2 branch
-> implement frozen BRRK-0011 Target calculation API only
-> deterministic multi-date research/live golden parity
```
