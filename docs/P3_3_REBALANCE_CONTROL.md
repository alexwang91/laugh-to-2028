# P3.3 Rebalance / Turnover Control Contract

Status: candidate implementation contract
Date: 2026-08-07

## Scope

P3.3 is a deterministic control layer **after** the frozen P3.2 Target calculation API and **before** venue sizing/routing/order submission.

It answers one question:

> Given the immutable P3.2 model target and the actually observed portfolio state, is the target deviation large enough to justify a portfolio rebalance, and what post-control desired state should downstream execution receive?

P3.3 does not calculate alpha, regime state, BRRK scale, funding response, leverage policy or contributions.

## Upstream authority

P3.3 must consume the P3.2 `TargetCalculationResult` unchanged.

Frozen target universe:

```text
BTC ETH SOL BNB
```

XRP remains feature-only upstream and is not a P3.3 position/target asset.

P3.3 rejects:

- a target from any target-engine version other than `P3.2-BRRK0011-V1`;
- a target containing shorts;
- a target with gross above 1;
- current-position assets outside BTC/ETH/SOL/BNB.

## Registered policy

Machine-readable policy:

`config/rebalance_policy.json`

Version:

`P3.3-L1-BAND-V1`

Metric:

```text
L1 target gap = Σ_asset |target_weight(asset) - current_weight(asset)|
```

Band:

```text
0.05
```

Boundary:

```text
rebalance when L1 target gap >= 0.05
suppress routine rebalance when L1 target gap < 0.05
```

The 0.05 value is a continuity migration of the existing Plan B **execution** rebalance control that was migrated into the repository on 2026-08-04 and documented by the legacy BTC execution service.

It is **not** derived from or justified by the separate 5% band used internally by P3.2 to reproduce the historical V1 return distribution for BRRK risk calibration. The numerical values happen to match; their roles and authority are separate.

## Minimum trade notional

Legacy execution also has `MIN_TRADE_USD=100`.

P3.3 explicitly does **not** use minimum trade notional to decide whether the portfolio should rebalance. The roadmap acceptance condition requires explicit banding rather than ad-hoc minimum-size suppression.

Therefore:

```text
P3.3 portfolio gate: L1 weight band
minimum trade notional: downstream order feasibility only
```

A P3.3 control plan may recommend a $60 delta if the aggregate L1 target gap is outside the band. A later execution layer may still determine that an individual venue order cannot be placed because of exchange constraints; that execution fact must not be rewritten as “the model did not need a rebalance.”

## Safety overrides

The routine churn band must not preserve a portfolio state that already violates frozen pre-P4 boundaries.

P3.3 bypasses the band and restores the P3.2 target if either is observed:

1. any current BTC/ETH/SOL/BNB position weight is negative;
2. current absolute gross weight exceeds 1.

These are control-boundary repairs, not new short or leverage logic.

## Inputs

`calculate_rebalance_control(...)` consumes:

- immutable P3.2 `TargetCalculationResult`;
- point-in-time account equity in USD;
- signed current BTC/ETH/SOL/BNB notionals;
- registered `RebalancePolicy` (default loader reads `config/rebalance_policy.json`).

Equity is used only to convert between notionals and weights at this control snapshot. P3.3 does not implement weekly contribution scheduling or contribution-aware target policy; that remains P3.4.

## Outputs / audit requirements

Every plan exposes both the theoretical model deviation and the post-control action state.

Required fields include:

- decision timestamp;
- upstream P3.2 target digest / target-engine version / model authority;
- P3.3 policy and control version;
- account equity;
- immutable model target weights and notionals;
- current position weights and notionals;
- theoretical per-asset gap weights and notionals;
- aggregate L1 target gap;
- theoretical turnover weight;
- current/target gross and net weights;
- safety override reasons;
- `should_rebalance` and reason;
- post-control desired weights and notionals;
- proposed per-asset deltas;
- actual control turnover weight after band suppression;
- suppressed theoretical gap when no action occurs;
- explicit statement that minimum-notional handling is downstream;
- deterministic P3.3 plan SHA-256 digest;
- `production_authorized = false`.

Crucially, when the band suppresses action the theoretical target gap is **not discarded**. This satisfies the roadmap requirement that every deviation from theoretical target remain measurable.

## Control semantics

### Inside band

If:

```text
L1 gap < 0.05
```

and there is no safety override:

- `should_rebalance = false`;
- post-control desired positions remain the current positions;
- proposed delta is zero;
- theoretical gaps remain fully recorded;
- suppressed gaps are explicitly exposed.

### At / outside band

If:

```text
L1 gap >= 0.05
```

or a safety override is active:

- `should_rebalance = true`;
- post-control desired positions equal the immutable P3.2 target at current control equity;
- proposed deltas equal target notionals minus current notionals;
- control turnover is the full L1 move to target.

P3.3 does not partially move toward target, optimize turnover, slice orders, apply route costs, or round quantities.

## Explicit exclusions

P3.3 does not implement:

- P3.4 weekly contribution handling;
- F23 funding-response redesign;
- P4 leverage above 1 or operating-risk-budget freeze;
- P5 exit intelligence;
- short targets;
- XRP targets;
- order precision;
- minimum-order enforcement;
- route selection;
- slippage/capacity policy;
- order slicing;
- actual order submission;
- production authorization.

## Acceptance mapping

Roadmap acceptance: **“no unnecessary churn from tiny target changes.”**

Evidence required:

- exact/no-op target test;
- inside-band suppression test;
- exact boundary test;
- multi-asset aggregate L1 test where every single-asset gap is below 5% but aggregate gap reaches 5%.

Roadmap acceptance: **“all deviations from theoretical target measurable.”**

Evidence required:

- theoretical per-asset gaps and aggregate L1 are present even when action is suppressed;
- suppressed gap fields preserve the deviation;
- upstream target digest/version is carried unchanged;
- control plan itself is deterministically digestible.

Additional safety/regression evidence:

- legacy `$100` min-trade value does not act as the P3.3 portfolio gate;
- current short exposure bypasses band;
- current gross > 1 bypasses band;
- unknown assets fail closed;
- upstream P3.2 target remains unchanged;
- production authorization remains false.
