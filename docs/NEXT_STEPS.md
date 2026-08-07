# Next Steps

> Read canonical sources in repository-defined order. GitHub actual state wins over stale prose.

## Current dependency

```text
P3.4 weekly contribution handling
```

P3.3 rebalance / turnover controls are PASS / TESTED / CI VERIFIED / MERGED by PR #78.

P3.3 merge commit:

`a503e64da4641e434620aa6a04bf9f6448d00135`

Final #78 evidence:

- Phase 0 #113 / run `31156709738`: SUCCESS, 204 execution tests passed and 5/5 research integration OK
- Research evidence #24 / run `31156709594`: SUCCESS
- P3.2 parity/golden #11 / run `31156709586`: SUCCESS
- final body-edit governance #147 / run `31156872098`: SUCCESS

## Frozen upstream interfaces

P3.4 must consume, not rewrite:

1. P3.2 `TargetCalculationResult` / `P3.2-BRRK0011-V1`;
2. P3.3 `RebalanceControlPlan` / `P3.3-L1-BAND-V1`.

Frozen role boundary:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
P3.2 gross    <= 1
short targets forbidden
```

P3.3 routine control remains:

```text
L1 target gap < 0.05  -> suppress routine churn
L1 target gap >= 0.05 -> desired state = full P3.2 target
```

Current short or gross >1 bypasses the routine band to restore the P3.2 target.

Legacy minimum trade notional remains downstream order feasibility only.

## P3.4 scope

P3.4 owns **weekly contribution handling** only.

Before coding, reread the exact P3.4 section of:

`docs/IMPLEMENTATION_ROADMAP_2026-08-05.md`

Do not infer contribution policy from older bot behavior or from the `$100/week` product assumption without checking the roadmap acceptance contract first.

The implementation must preserve the separation between:

- model target (P3.2);
- target-to-position churn control (P3.3);
- contribution handling (P3.4).

Any contribution-aware output must remain fully auditable and reference upstream target/control versions/digests.

## Explicit exclusions

Do not add in P3.4:

- F23 funding-response redesign;
- P4 leverage above 1 / operating-risk-budget freeze;
- P5 exit intelligence;
- short targets;
- XRP target exposure;
- new target-model logic;
- new P3.3 band semantics;
- production authorization.

## Required workflow

```text
finish this post-merge normalization PR
-> applicable CI / parity / governance
-> expected-head merge normalization
-> verify new main
-> create fresh P3.4 branch from latest main
-> reread exact P3.4 roadmap contract
-> implement P3.4 only
-> unit tests + upstream P3.2/P3.3 contract-preservation tests
-> CURRENT_STATE handoff
-> PR / CI / self-review
-> final-head evidence
-> newest governance GREEN
-> expected-head merge
-> post-merge normalization
-> P4
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
close post-P3.3 normalization
-> fresh P3.4 branch from latest main
-> reread P3.4 roadmap acceptance contract
-> implement weekly contribution handling only
```
