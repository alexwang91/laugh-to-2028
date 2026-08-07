# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.3 rebalance / turnover controls
```

P3.2 Target calculation API is PASS / TESTED / CI VERIFIED / MERGED by PR #76.

P3.2 merge commit:

`70e279bcb1e7f78cfed1d62376a7aa2fef17ac45`

Final P3.2 evidence:

- Phase 0 #108 / run `31154665875`: SUCCESS
- Research evidence #19 / run `31154665880`: SUCCESS
- P3.2 target research-live parity #6 / run `31154665888`: SUCCESS
  - independent research-vs-product parity SUCCESS
  - committed historical golden enforcement SUCCESS
- final body-edit PR governance #140 / run `31154835417`: SUCCESS

Committed P3.2 golden evidence:

`research/results/p3_2_target_parity/golden_v1.json`

## Frozen input from P3.2

P3.3 must consume the existing target contract rather than recompute or alter it.

Frozen target role boundary:

```text
target_assets  = BTC, ETH, SOL, BNB
feature_assets = XRP
strategy-signal daily payload = BTC, ETH, SOL, BNB, XRP
router-eligible assets         = BTC, ETH, SOL, BNB only
```

P3.2 output available to P3.3 includes:

- BTC/ETH/SOL/BNB target weights
- risky-sleeve relative weights
- cash share
- base gross target <= 1
- semantic risk state and posterior
- risk-off probability / meta scale / defensive scale
- regime refit session
- feature snapshot
- model / target-engine / data-contract versions
- canonical data digest

Timing remains:

- decision D 00:00 UTC consumes completed daily data through exactly D-1
- P3.2 emits the model target for that decision

## P3.3 scope

P3.3 owns **target-to-position rebalance and turnover controls only**.

The implementation should take:

- canonical P3.2 target
- actual current positions / equity
- approved execution/product configuration

and determine whether/how much of the target gap is actionable under the frozen P3.3 control policy.

Required outputs should be explicit and auditable, including at least:

- model target received from P3.2
- current position weights/notionals
- target gap by asset
- rebalance decision / reason
- post-control desired position or executable delta
- turnover/control version
- decision timestamp and upstream target digest/version

The exact P3.3 acceptance contract must be checked against the Implementation Roadmap before implementation begins.

## Critical separation from P3.2

The 5% band inside P3.2's frozen BRRK return-model calibration is **not** the P3.3 execution band. It exists only to reproduce the historical state-conditioned V1 return distribution used by BRRK-0011 risk scaling.

P3.3 must not alter:

- BRRK/V1 target weights
- HMM/PCA/state model
- defensive scale
- P3.1 data canonicalization
- P3.2 golden vectors

If a target-vs-held band or turnover policy is implemented, it must live after P3.2 target calculation and be separately versioned/tested.

## Explicit exclusions

Do not add in P3.3:

- P3.4 weekly contribution handling
- F23 funding-response redesign
- P4 leverage above 1 / operating-risk-budget freeze
- P5 cycle-exit intelligence
- short targets
- XRP target exposure
- production authorization

## Required workflow

```text
finish this post-merge normalization PR
-> required CI / parity / governance
-> expected-head merge normalization
-> verify new main
-> create fresh P3.3 branch from latest main
-> reread P3.3 roadmap acceptance contract
-> implement P3.3 only
-> unit tests + upstream P3.2 contract-preservation tests
-> CURRENT_STATE handoff
-> PR / CI / self-review
-> final-head evidence
-> newest governance GREEN
-> expected-head merge
-> post-merge normalization
-> P3.4
```

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

## Project drift audit

```text
DRIFT_0
```

## Exact next action

```text
close post-merge normalization
-> fresh P3.3 branch from latest main
-> implement target-to-position rebalance / turnover controls only
```
