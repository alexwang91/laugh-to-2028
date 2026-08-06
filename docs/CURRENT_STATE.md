# BRRK Current State

Last updated: 2026-08-06
Status: authoritative cross-chat handoff snapshot for candidate branch `fix/p3-1-feature-input-parity`

## Authoritative main baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 original data contract: PASS / MERGED
- PR #71: PASS / MERGED
- PR #72: PASS / MERGED as `6edaff4bb62bba8316722265dd216ba6e5e7d541`
- PR #73: **MERGED MANUALLY** as `89b095d7a7d746b768afca8245b963ecf15ffabc`; required governance CI was not recorded green before the manual merge and must not be retroactively labeled CI VERIFIED
- Current authoritative `main`: `89b095d7a7d746b768afca8245b963ecf15ffabc`
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current roadmap position

```text
P3.1 base          PASS / MERGED
P3.1 parity fix    ACTIVE CANDIDATE — REQUIRED BEFORE P3.2
P3.2               BLOCKED ON PARITY FIX
P3.3+              BLOCKED
```

A fresh P3.2 branch `p3-2/target-calculation-api-v2` was created from `89b095d7...`, but **no P3.2 code was committed** before the dependency mismatch below was discovered. Do not continue that branch after this correction merges; create another fresh P3.2 branch from then-current main.

## Newly discovered P3.1 parity defect

During recovery of the exact frozen BRRK-0011 target chain, GitHub source proved that the frozen regime feature model consumes five Binance spot daily series:

```text
BTC  target/tradable
ETH  target/tradable
SOL  target/tradable
BNB  target/tradable
XRP  feature-only
```

The original P3.1 canonical contract exposed only BTC/ETH/SOL/BNB and described those four as the complete frozen strategy input. That is inconsistent with the actual BRRK-0011 HMM feature implementation:

- `RegimeKellyConfig` includes XRP in the major/alt feature panels;
- `features_no_dominance.py` uses those panels for breadth, relative-strength dispersion and BTC-correlation features;
- `build_brrk0011_scale()` consumes those features before fitting the regime model.

Therefore exact research/live BRRK-0011 golden parity is impossible from the P3.1 v1 payload.

This is an implementation/data-contract parity correction, **not** a new research hypothesis and not an expansion of the product universe.

## Candidate correction

Branch:

```text
fix/p3-1-feature-input-parity
base = 89b095d7a7d746b768afca8245b963ecf15ffabc
```

Implemented candidate behavior:

- canonical target/tradable assets remain exactly BTC/ETH/SOL/BNB;
- add `strategy_feature_assets = [XRP]`;
- canonical strategy-signal daily payload requires BTC/ETH/SOL/BNB/XRP complete UTC daily history;
- XRP source mapping is frozen as `XRPUSDT`;
- common-history and missing-data fail-closed rules apply across all five signal series;
- router funding/basis canonicalizers remain restricted to BTC/ETH/SOL/BNB and reject XRP;
- contract schema advances from v1 to v2 because payload role/content and digest semantics change;
- no BRRK parameter, weight formula, HMM parameter, risk budget or risk-scaling rule changes.

## Frozen BRRK-0011 chain recovered

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

Frozen target assets remain BTC/ETH/SOL/BNB. Frozen risk scaler remains 0–1. `EXPOSURE-SMOOTH-0038` remains NOT PROMOTED / BASELINE UNCHANGED.

## P3.2 boundary retained

After the parity correction is merged, P3.2 remains target calculation only. It must output at least:

- BTC/ETH/SOL/BNB target/relative weights;
- cash share;
- base gross target <= 1;
- risk state and corrected defensive scale;
- decision timestamp;
- feature snapshot;
- model/data-contract/target-engine versions and data digest.

P3.2 must not add P3.3 rebalance/turnover bands, P3.4 contributions, F23 funding-response redesign, P4 >1 leverage, P5 exit intelligence, shorts, XRP target exposure, or production authorization.

## Evidence status for active correction

```text
IMPLEMENTED:          IN PROGRESS / CORE CONTRACT + TEST UPDATES WRITTEN
TESTED:               NOT YET CLAIMED
CI VERIFIED:          NO
MERGED:               NO
PRODUCTION AUTHORIZED:NO_CHANGE
```

`production_authorized_components = []`

## Project drift audit

```text
DRIFT_1
```

Reason: the original P3.1 contract omitted a feature-only series actually consumed by the frozen BRRK-0011 regime model. The correction restores parity without changing product scope or research authority.

## Exact next action

```text
finish P3.1 parity correction docs/tests
-> run local/CI tests
-> self-review diff
-> open correction PR with normal governance
-> final-head CI
-> expected-head merge
-> post-merge handoff normalization
-> create a NEW fresh P3.2 branch from then-current main
-> implement frozen BRRK-0011 Target calculation API only
-> deterministic multi-date research/live golden parity
```
