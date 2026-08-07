# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 base data contract: PASS / MERGED
- PR #71: PASS / MERGED
- PR #72: PASS / MERGED
- PR #73: MERGED as `89b095d7a7d746b768afca8245b963ecf15ffabc`; its required PR governance CI was not recorded green before merge and must not be retroactively labeled CI VERIFIED
- PR #74: P3.1 schema-v2 XRP feature-input parity correction MERGED during the GitHub Actions incident; its own pre-merge workflow evidence was absent
- PR #75: post-merge P3.1 schema-v2 validation PASS / CI VERIFIED / MERGED as `c25b64fd42043bbaa61e264a8591bfdc813f5e40`
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Restored P3.1 validation evidence

PR #75 final code head:

`903fe99779435c8e30255afce77a45c6619eb66d`

Final evidence:

- `Phase 0 baseline contract` run `31152649985` (#101): SUCCESS
  - execution pytest: 187 passed
  - research integration contract: SUCCESS
- `Research evidence normalization` run `31152649957` (#13): SUCCESS
- final body-edit-triggered `PR handoff governance` run `31152716966` (#133): SUCCESS
- expected-head squash merge: `c25b64fd42043bbaa61e264a8591bfdc813f5e40`

The historical absence of #74 pre-merge CI remains recorded as fact; #75 provides the subsequent validation evidence on the merged schema-v2 state rather than retroactively rewriting #74 history.

## Current roadmap position

```text
P3.1 schema-v2 parity implementation   PASS / MERGED / VALIDATED BY #75
P3.2 Target calculation API            ACTIVE
P3.3 rebalance / turnover controls      BLOCKED UNTIL P3.2 MERGES
P3.4 contributions                     BLOCKED
P4 leverage / operating risk budget     BLOCKED
P5 exit intelligence                    BLOCKED
```

Current P3.2 candidate branch:

`p3-2/target-calculation-api-v3`

It was created fresh from main `c25b64fd42043bbaa61e264a8591bfdc813f5e40`. Do not reuse the earlier `p3-2/target-calculation-api-v2` branch.

## Frozen P3.1 / P3.2 asset-role boundary

Target / tradable assets remain exactly:

```text
BTC ETH SOL BNB
```

Frozen BRRK-0011 regime features additionally consume:

```text
XRPUSDT — feature-only
```

Schema v2 therefore remains:

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

XRP cannot receive a target weight and cannot enter funding/basis routing.

## Frozen BRRK-0011 chain

```text
four-asset frozen V1 rotation
-> normalize raw V1 gross to <= 1
-> build_features_no_dominance using BTC/ETH/SOL/BNB + feature-only XRP
-> RobustScaler(20,80)
-> whitened PCA4
-> sticky 4-state VariationalGaussianHMM
-> filtered_posterior
-> fit_state_v1_distribution on the frozen internally-banded V1 return series
-> sample_v1_paths (5000 x 20d, Student-t df=5)
-> choose_scale_corrected (CVaR95 + corrected CDaR95, budget 0.20)
-> meta_scale
-> final_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
-> BRRK_0011_TARGET = current V1 raw weights * final_scale
```

Frozen effective HMM caller parameters are `hmm_restarts=3`, `hmm_iter=250`, random seed `20260804`. `EXPOSURE-SMOOTH-0038` remains NOT PROMOTED / BASELINE UNCHANGED.

The internal V1 5% band and 5 bps turnover cost are used only to reproduce the historical V1 return distribution consumed by BRRK-0011 risk scaling. P3.2 does **not** apply that band to emitted targets; target-vs-position rebalance logic remains P3.3.

## P3.2 implementation state

Implemented on the active branch so far:

- product-owned `beta_bot/target_math.py`; no runtime import from `research/`
- canonical `beta_bot/target_engine.py`
- pinned scientific runtime dependencies for deterministic HMM/PCA behavior
- P3.2 unit tests for long-only/gross/cash/account-context boundaries
- independent `research/integration/p3_2_target_parity.py`
- dedicated `P3.2 target research-live parity` workflow

P3.2 API input:

- P3.1 canonical daily dataset at decision D 00:00 UTC, containing completed sessions through exactly D-1
- account equity
- current positions
- approved ProductConfig

P3.2 output includes:

- BTC/ETH/SOL/BNB target weights and relative weights
- cash share
- base gross target <= 1
- semantic risk state and posterior
- corrected defensive scale, risk-off probability and meta scale
- regime refit session
- model / target-engine / data-contract versions
- canonical data digest
- auditable feature snapshot

Current positions are accepted and audited as input context but do not alter P3.2 target calculation. Any target-vs-position banding, throttle or rebalance control belongs to P3.3.

## P3.2 timing convention

A target decision at `D 00:00 UTC` may use only completed P3.1 daily observations through `D-1`.

The V1 row computed from the `D-1` close becomes the decision-D target, matching the frozen research convention in which target row `t` is held over the following day's return. The BRRK defensive scale is the most recent valid 30-calendar-day refit scale active on `D-1`.

## Required P3.2 acceptance evidence still pending

```text
IMPLEMENTED:           IN PROGRESS
TESTED:                PENDING PR CI
CI VERIFIED:           NO
MERGED:                NO
PRODUCTION AUTHORIZED: NO_CHANGE
```

The major remaining gate is independent multi-date research/live parity. The dedicated parity test uses the shared P3.1 candle contract, then separates the paths:

- research reference: frozen `research/regime_kelly`, `research/hybrid_meta`, `research/risk_metric_fix`, frozen V1 core
- live candidate: product-owned `beta_bot.target_engine`

It compares historical per-asset targets, gross, cash, refit date, risk state/posterior, meta/defensive scale and feature snapshot. Early 2021 dates are covered at the V1 layer because the frozen BRRK model legitimately cannot have a regime refit before its 600-valid-row training threshold is satisfied.

## Explicit P3.2 exclusions

Do not add in P3.2:

- P3.3 target-vs-held rebalance/turnover bands
- P3.4 weekly contribution handling
- F23 funding-response redesign
- P4 gross > 1 leverage or operating-risk-budget freeze
- P5 cycle-exit intelligence
- short logic
- XRP target exposure
- any production authorization

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

P3.1 data/model input semantics and validation evidence are aligned. P3.2 is now the unique active implementation; no known upstream parity residual remains.

## Exact next action

```text
complete P3.2 candidate implementation
-> open PR from p3-2/target-calculation-api-v3
-> Phase 0 full pytest + research integration
-> P3.2 independent multi-date research/live parity workflow
-> inspect parity coverage and any real failures
-> correct in same PR
-> self-review + final-head CI
-> write final run IDs/results into PR body
-> require newest body-edit governance run GREEN
-> expected-head squash merge
-> verify new main
-> post-merge normalization
-> fresh P3.3 branch
```
