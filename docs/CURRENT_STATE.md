# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 schema-v2 data contract: PASS / MERGED / validated by PR #75
- P3.2 Target calculation API: PASS / TESTED / CI VERIFIED / MERGED by PR #76
- PR #73 remains historically MERGED without a recorded green required PR-governance run before that merge; do not retroactively relabel it CI VERIFIED
- PR #74 remains historically MERGED during the GitHub Actions incident without its own pre-merge workflow evidence; PR #75 subsequently validated the merged schema-v2 state
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

P3.2 merge commit on main:

`70e279bcb1e7f78cfed1d62376a7aa2fef17ac45`

```text
P3.1 schema-v2 data contract           PASS / MERGED
P3.2 Target calculation API            PASS / MERGED
P3.3 rebalance / turnover controls      UNIQUE NEXT ROADMAP IMPLEMENTATION
P3.4 contributions                     BLOCKED UNTIL P3.3
P4 leverage / operating risk budget     BLOCKED
P5 exit intelligence                    BLOCKED
```

No pre-existing P3.3 branch is authoritative. P3.3 must start from the latest main only after this post-merge normalization PR itself closes.

## Frozen asset-role boundary

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

XRP remains feature-only. It cannot receive target exposure and cannot enter funding/basis routing.

## Frozen P3.2 target authority now on main

Product-owned runtime files:

- `execution/plan-b-bot/beta_bot/target_math.py`
- `execution/plan-b-bot/beta_bot/target_engine.py`

Frozen chain:

```text
four-asset V1 rotation
-> normalize raw V1 gross to <= 1
-> BTC/ETH/SOL/BNB + feature-only XRP price-state features
-> RobustScaler(20,80)
-> whitened PCA4
-> sticky 4-state VariationalGaussianHMM
-> filtered posterior
-> state-conditioned internally-banded V1 return distribution
-> 5000 x 20d Student-t(df=5) paths
-> corrected CVaR95 + CDaR95 allocator, risk budget 0.20
-> meta_scale
-> final_scale = 1 - P(RISK_OFF) * (1 - meta_scale)
-> target = current V1 raw weights * final_scale
```

Frozen effective model caller values:

```text
hmm_restarts = 3
hmm_iter     = 250
random_seed  = 20260804
```

Pinned numerical runtime:

```text
numpy         2.5.1
pandas        3.0.3
scipy         1.18.0
scikit-learn  1.9.0
hmmlearn      0.3.3
```

`EXPOSURE-SMOOTH-0038` remains MECHANISM VALIDATED / NOT PROMOTED / BASELINE UNCHANGED.

## P3.2 API boundary

Input:

- P3.1 canonical schema-v2 daily dataset
- account equity
- current positions
- approved ProductConfig

Timing:

- decision at D 00:00 UTC consumes completed observations exactly through D-1
- V1 row at D-1 becomes the decision-D target
- defensive scale is the latest valid frozen 30-calendar-day BRRK refit active on D-1

Output includes:

- BTC/ETH/SOL/BNB target weights and risky-sleeve relative weights
- cash share
- base gross target <= 1
- semantic risk state and posterior
- risk-off probability / meta scale / corrected defensive scale
- regime refit session
- feature snapshot
- model / target-engine / data-contract versions
- canonical data digest

Current positions are context/audit input only in P3.2. They do not band, throttle or change the target.

The internal 5% V1 band and 5 bps turnover cost exist only to reproduce the frozen historical V1 return distribution used by BRRK-0011 risk calibration. They are not P3.3 execution controls.

## PR #76 final evidence

Final PR head:

`351df262d9dfda6e7900f6acc74bdb0a67c5ae1c`

Final-head evidence:

- `Phase 0 baseline contract` run `31154665875` (#108): SUCCESS
- `Research evidence normalization` run `31154665880` (#19): SUCCESS
- `P3.2 target research-live parity` run `31154665888` (#6): SUCCESS
  - independent research-reference vs product historical parity: SUCCESS
  - committed historical golden enforcement: SUCCESS
- PR governance on final code/handoff head run `31154665874` (#139): SUCCESS
- final PR-body-edit governance run `31154835417` (#140): SUCCESS
- expected-head squash merge: `70e279bcb1e7f78cfed1d62376a7aa2fef17ac45`

Checkpoint Phase 0 run `31154475023` (#107) recorded 192 execution tests passed in 5.63s and 5/5 research integration tests OK.

## P3.2 historical parity / immutable golden evidence

Committed evidence:

`research/results/p3_2_target_parity/golden_v1.json`

Coverage:

```text
early V1-only decisions: 2
full BRRK decisions:     6
semantic states:         RISK_OFF / BTC_LEAD / MAJOR_ROTATION / ALT_EXPANSION
min defensive scale:     1.3453862979240228e-07
max defensive scale:     0.9999999939549142
```

The full BRRK dates span 2022-12 through 2026-08. The two 2021 V1 dates cover the period before the frozen 600-valid-row regime training threshold permits a legal BRRK refit.

The product-only golden comparator checks the committed data digests and target vectors independently of a newly calculated research reference. This prevents coordinated research + product edits from silently moving the frozen baseline while still passing pairwise parity.

## P3.2 closure status

```text
IMPLEMENTED:           YES
TESTED:                YES
CI VERIFIED:           YES
MERGED:                YES
PRODUCTION AUTHORIZED: NO_CHANGE
```

## P3.3 boundary

P3.3 is now the unique next implementation and owns target-to-position rebalance / turnover control only.

P3.3 must consume the P3.2 target contract; it must not rewrite the frozen BRRK target model.

P3.3 must not absorb:

- P3.4 contribution handling
- F23 funding-response redesign
- P4 gross > 1 leverage or operating-risk-budget freeze
- P5 exit intelligence
- shorts
- XRP targets
- production authorization

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

P3.1 data semantics and P3.2 target semantics are aligned, validated and merged. No known authority drift remains.

## Exact next action

```text
post-merge normalization PR
-> docs-only self-review
-> required CI / parity / governance on normalization head
-> write final run evidence into PR metadata
-> newest governance GREEN
-> expected-head merge normalization
-> verify main
-> create fresh P3.3 branch from that main
-> implement rebalance / turnover controls only
```
