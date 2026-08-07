# P3.4 Contribution Handling Contract

Status: candidate implementation contract
Date: 2026-08-07

## Roadmap authority

Canonical roadmap requirement:

> Manual deposit is detected as equity change and included at the next daily decision.

Acceptance:

1. deposit does not trigger unscheduled intraday risk increase;
2. new cash allocation follows the same target engine.

This is the complete P3.4 product boundary. P3.4 does not introduce a new alpha model, a contribution-specific allocation formula, a new rebalance band or an intraday strategy cycle.

## Core interpretation

Account equity alone cannot distinguish a manual deposit from mark-to-market PnL with source certainty.

Therefore P3.4 deliberately observes **signed account-equity change without source attribution**:

```text
observed equity - previous accepted daily-decision equity
```

A positive value is recorded as:

```text
CONTRIBUTION_CANDIDATE_NOT_CONFIRMED_TRANSFER
```

It is not asserted to be a confirmed transfer.

This interpretation matches the roadmap wording “detected as equity change” and avoids inventing a transfer-attribution model that is not part of P3.4.

## Machine policy

`config/contribution_policy.json`

Version:

`P3.4-EQUITY-CHANGE-DAILY-V1`

Frozen policy:

```text
equity reference:
  previous accepted daily-decision account equity

detection:
  observe signed equity change without source attribution

positive change:
  contribution candidate only

negative change:
  not a contribution candidate

intraday action:
  record only
  no target recalculation
  no risk increase

allocation time:
  next eligible 00:00 UTC daily decision

allocation path:
  P3.2-BRRK0011-V1
  -> P3.3-L1-BAND-V1
```

The product assumption of approximately `$100/week` is **not** a detection threshold and is **not** a scheduler trigger. A +$37 or +$250 equity change is treated by the same observation rule.

## Timing semantics

P3.4 distinguishes an observation from a daily allocation decision.

### Intraday observation

Example:

```text
last accepted daily decision: 2026-08-07 00:00 UTC
positive equity change seen:   2026-08-07 13:45 UTC
scheduled allocation:          2026-08-08 00:00 UTC
```

The 13:45 observation cannot trigger P3.2 or P3.3 and cannot authorize any risk increase.

### Observation exactly at a future daily boundary

If the previous accepted daily decision was `2026-08-07 00:00 UTC` and the equity change is observed at `2026-08-08 00:00 UTC` before that day's decision is accepted, it may be included in the `2026-08-08 00:00 UTC` decision.

### Observation at an already-accepted boundary

If the baseline itself is already the accepted `2026-08-08 00:00 UTC` decision, an observation timestamped at that same boundary must **not** cause a second 2026-08-08 decision. Its next eligible decision is `2026-08-09 00:00 UTC`.

This prevents a deposit/equity change from creating a second unscheduled strategy cycle at an already-consumed daily boundary.

## Why the contribution amount is diagnostic, not an allocation input

At the scheduled daily decision, P3.4 uses the **fresh full account equity** observed at that decision.

It does not allocate only the candidate contribution amount.

Example:

```text
previous accepted equity:       $2,000
intraday positive equity change: +$100 candidate
fresh next-day equity:           $2,135
```

The next daily P3.2 target is calculated using `$2,135`, not `$2,100` and not a separate `$100` sleeve.

This matters because the difference between $2,100 and $2,135 may be PnL or another equity change. P3.4 does not need to attribute it. It simply ensures the complete account state enters the same canonical daily decision engine.

## Same-engine allocation path

At the scheduled daily boundary, P3.4 calls the unchanged:

```text
P3.2 calculate_target(... fresh account equity ...)
-> P3.3 calculate_rebalance_control(... same fresh account equity ...)
```

There is no contribution-specific target formula.

Consequences:

- model target weights continue to come only from BRRK-0011 / P3.2;
- new cash changes position weights/notionals through current equity, not alpha logic;
- P3.3's existing L1 churn control remains authoritative after P3.2;
- P3.4 does not bypass the P3.3 band merely because cash was added;
- downstream minimum-order/precision/routing remains downstream.

## Inputs

### Equity-change observation

`observe_equity_change(...)` consumes:

- previous accepted daily-decision timestamp;
- previous accepted daily-decision account equity;
- observation timestamp;
- newly observed account equity;
- frozen P3.4 policy.

### Scheduled daily application

`apply_at_daily_decision(...)` consumes:

- the recorded equity-change observation;
- P3.1 canonical daily dataset for the scheduled decision;
- fresh account equity at that decision;
- signed current BTC/ETH/SOL/BNB notionals;
- approved ProductConfig;
- frozen P3.4 policy.

The daily dataset decision timestamp must exactly equal the observation's scheduled 00:00 UTC decision.

## Outputs and audit fields

### Observation

Every observation records:

- baseline decision timestamp;
- observation timestamp;
- baseline and observed equity;
- signed equity change;
- positive contribution-candidate amount;
- classification;
- `source_attributed = false`;
- scheduled daily-decision timestamp;
- whether observation itself occurred at a daily boundary;
- explicit `requires_intraday_action = false`;
- explicit `intraday_target_recalculation_allowed = false`;
- explicit `intraday_risk_increase_allowed = false`;
- deterministic canonical JSON / SHA-256 digest;
- no production authorization.

### Daily decision

The contribution-aware daily decision records:

- observation digest;
- observed equity change and contribution candidate;
- fresh decision account equity;
- P3.2 target-engine version and target digest;
- P3.3 control version and control digest;
- complete P3.2 target result;
- complete P3.3 control plan;
- deterministic canonical JSON / SHA-256 digest;
- no production authorization.

## Acceptance mapping

### “Deposit does not trigger unscheduled intraday risk increase”

Required regression evidence:

- intraday positive equity observation schedules next 00:00 UTC;
- observation exposes no target-recalculation permission and no risk-increase permission;
- applying at a non-00:00 timestamp fails closed;
- applying on the wrong daily boundary fails closed;
- an already-accepted baseline boundary cannot be reused for a second daily decision.

### “New cash allocation follows the same target engine”

Required regression evidence:

- scheduled daily application explicitly calls P3.2 target calculation;
- fresh full daily-decision equity is passed to P3.2;
- the resulting P3.2 target is passed unchanged to P3.3;
- the same fresh equity is used by P3.3 to convert target/current positions to weights/notionals;
- contribution amount is diagnostic only, not a separate target sleeve;
- `$100/week` is not used as a threshold.

## Explicit exclusions

P3.4 does not implement:

- bank/exchange transfer-source attribution;
- automatic deposit scheduling;
- a required weekday;
- a required `$100` amount;
- intraday target calculation;
- intraday risk increase;
- a contribution-specific alpha sleeve;
- changes to P3.2 target semantics;
- changes to P3.3 band/safety semantics;
- F23 funding-response redesign;
- P4 leverage above 1 or operating-risk-budget freeze;
- P5 exit intelligence;
- shorts;
- XRP targets;
- venue min-order/precision/routing/order submission;
- production authorization.
