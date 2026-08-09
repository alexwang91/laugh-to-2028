# BRRK Next Steps

Last updated: 2026-08-09

## Current instruction

**Phase 6 remains 3/4 and identity-unbound. The docs-only F27/F7/Idle-Cash review is complete in its current branch, but it creates no live authority. The next operational dependency is still a future explicit compatible Hyperliquid master/subaccount identity satisfying `userRole=user/subAccount` and `userAbstraction=disabled`. Production remains unauthorized.**

## Immediate state

```text
Phase 6 implementation/replay          PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY / MERGED #109
Phase 6 live elapsed evidence          MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT / CLOCK NOT ARMED
Phase 6 durable evidence backend       FROZEN / MERGED #133
Phase 6 valuation contract             PHASE6-LIVE-VALUATION-V1 / MERGED #134
Phase 6 account-identity rules         PHASE6-LIVE-ACCOUNT-IDENTITY-V1 / MERGED #135 / UNBOUND
Phase 6 pre-arm dependencies           3/4 FROZEN
identity blocker                       COMPATIBLE EXPLICIT PUBLIC MASTER/SUBACCOUNT IDENTITY
collector_armed                        false
schedule_configured                    false
elapsed evidence credit                false
Phase 7                                MONITOR_ONLY / LAUNCH BLOCKED
Phase 8                                TRIGGER ABSENT / NOT RUN
production gross cap                   1.0
production_authorized_components = []
production_authorized                  false
signature_authorized                   false
order_submission_authorized            false
```

The PR #138 address must not be copied, inferred, reused or rebound from historical discussion.

## Completed docs-only corrections

### F27

`research/results/idle_cash_credit_0027r2.json` is authoritative; R1 is superseded but preserved unchanged.

Corrected BRRK R2 headline:

```text
mean idle cash                24.5700%
raw CAGR                      65.1661%
credited CAGR                 66.8068%
CAGR delta                    +1.6407 pp
rf=0 Sharpe raw -> credited   1.3532 -> 1.3756
excess Sharpe raw -> credited 1.3667 -> 1.4039
```

### F7

Status is **PARTIAL**. The shared calendar-span helper exists in `research/common/metrics.py`, but immutable historical studies retain frozen study-local conventions. Do not rewrite immutable results merely to normalize old metrics.

### LEVERAGE-0040

The P4.5 decision now documents that the 65.31% cap-1.00 comparator uses observation-count annualization, so it is not numerically identical to calendar-span F27 R2 BRRK CAGR `65.1661%`. Within-study comparisons remain valid and the immutable decision stays `FAIL_STOP / NO_PROMOTION`.

### Idle Cash execution feasibility

`docs/IDLE_CASH_EXECUTION_FEASIBILITY.md` concludes:

```text
NOT_FEASIBLE_ON_HYPERLIQUID_STANDARD
FUTURE_OPTION / NOT_AUTHORIZED
REQUIRES SEPARATE DESIGN + CONTRACT + APPROVAL
```

Do not implement the historical ~1.64 pp credit by silently switching to Portfolio Margin, HLP, HYPE staking, off-venue lending or another non-immediately-callable asset. Preserving V1 margin availability, liquidation distance and Standard valuation semantics takes precedence.

## Future identity action

Use `docs/PHASE6_ADDRESS_BINDING_REQUEST.md`.

A compatible future public identity must:

```text
be the exact observed master/subaccount
match 0x + 40 hex characters
not be an agent/API wallet
not be a vault
userRole = user OR subAccount
userAbstraction = disabled
fit PHASE6-LIVE-VALUATION-V1 Standard semantics
```

An incompatible role or abstraction yields `BLOCKED_INCOMPATIBLE`. Do not relax the contract to make an observed identity fit.

## What happens after identity binding

```text
compatible identity verified
-> non-secret provenance + raw-response digests persisted
-> identity frozen
-> dependencies 4/4
-> STOP
-> separate prospective ARM change
-> collector armed + schedule configured
-> first eligible 00:00 UTC decision strictly after ARM commit
-> future-only shadow evidence
```

`4/4 != CLOCK STARTED`, `IDENTITY BOUND != ARM`, and `ARM != HISTORICAL CREDIT`.

Frozen Phase-6 acceptance:

```text
minimum elapsed calendar days       14
minimum scheduled decisions         10
minimum emergency drills             1
critical reconciliation errors       0
unexplained target drift              0
schedule failures                     0
```

No historical backfill/replay, CI replay, rerun, duplicate timestamp or manual dispatch receives scheduled-decision credit.

## Prospective research admission rule

Any future new Research ID that can reduce canonical BRRK target gross must satisfy `docs/RIGHT_TAIL_PRESERVATION_GATE.md`:

```text
canonical best-20 log-growth retention >= 90%
net summed daily-return delta > 0
```

Both gates must pass. Best-10 and best-50 retention are mandatory reports but have no V1 hard threshold. Historical immutable evidence is excluded from retrospective rescoring.

## Human-control boundaries

Explicit human approval remains required for:

- the future compatible identity owner action;
- the separate Phase-6 ARM transition;
- Phase-7 launch;
- `MONITOR_ONLY -> ACTIVE`;
- `FLAT -> LONG`;
- `FLAT -> SHORT`;
- the first short exposure of a new confirmed bear phase.

Do not substitute Idle Cash implementation, Stablecoin rescue, leverage rescue, post-result cap tuning, short research, production deployment, identity probing, collector arming or clock backfill for the currently blocked Phase-6 identity dependency.
