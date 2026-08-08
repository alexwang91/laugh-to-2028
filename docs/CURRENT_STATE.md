# BRRK Current State

Last updated: 2026-08-08
Status: **authoritative current-state handoff**

## Executive state

```text
Phase 0-3                      COMPLETE / MERGED
Phase 4 leverage research      FAIL_STOP / no eligible >1 candidate
production gross cap           1.0
production_authorized_components []
P5.1 event taxonomy            COMPLETE / FROZEN
P5.2 feature evidence          COMPLETE / IMMUTABLE / DESCRIPTIVE CLOSEOUT
P5.3 V1                       COMPLETE / IMMUTABLE / ARCHITECTURE_FAIL
P5.3 V2                       COMPLETE / IMMUTABLE EVIDENCE / ARCHITECTURE_PASS
P5.4 behavior mapping          COMPLETE / FIXED 4-MAP FAMILY / PURE IMPLEMENTATION / NO SELECTION
P5.5 validation                PREREGISTERED / NO CANDIDATE ECONOMICS RUN
P5.6 integration               NOT STARTED
Phase 6 shadow                 NOT STARTED
Phase 7 limited-live readiness NOT STARTED / actual launch requires explicit approval
Phase 8 bear-short research    NOT STARTED
production authorization       NONE
```

## Frozen upstream

P5.3 V2 immutable summary SHA256: `05d5d68a59c8b13f1122d98ed75d03934defdc9d73c7dd92e038c92fd97d2e52`.

P5.4 canonical contract: `P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1` with four maps `HARD_ONLY / GENTLE / BALANCED / DEFENSIVE`. The pure implementation only scales total frozen BRRK gross and cannot change relative asset ranking, create shorts or exceed gross 1.0.

## P5.5 preregistration

Contract: `P5.5-JOINT-PROFILE-MAP-VALIDATION-V1`  
Pre-result semantic amendment: `P5.5-JOINT-PROFILE-MAP-VALIDATION-V1-R1`

P5.5 evaluates exactly 12 joint candidates:

```text
EARLY / BALANCED / CONSERVATIVE
x
HARD_ONLY / GENTLE / BALANCED / DEFENSIVE
```

`BRRK_NO_CYCLE_CONTROL` remains non-promotable comparator.

### Data boundary

The authoritative BRRK target builder freezes its economic evaluation start at `2022-12-10`. Therefore P5.5 explicitly separates:

1. **all-event behavior diagnostics** across the full P5.3 V2 history, including the 2021 terminal/second-wind/control events, with no candidate return claims; and
2. **authoritative BRRK economics** only from `2022-12-10` through `2026-08-02` using the frozen BRRK target authority.

No 2021 BRRK economic path may be fabricated.

### Economic semantics

P5.5 reuses repository-established mechanics:

- authoritative prices/targets from `run_leverage_0040_once_r1.py`;
- `simulate_p3_3_economic_path` timing/current-weight drift mechanics;
- 5% L1 rebalance band;
- cost grid `5 / 10 / 20 / 50 bps` per executed absolute weight change;
- matched same-target-source comparator;
- metrics: terminal multiple, CAGR, MaxDD, Sharpe, Calmar, turnover and gross.

R1 clarifies MaxDD sign semantics before any result: compare absolute drawdown magnitudes; candidate may worsen absolute MaxDD by at most 1 percentage point at 5/10 bps.

### Selection discipline

Primary objective: highest 5-bps after-cost CAGR **among candidates passing every hard gate**. Gates include:

- terminal-event partial de-risk timing;
- second-wind preservation;
- immutable 2021 false-FLAT visibility and <=10-day V2 episode;
- after-cost CAGR/Calmar/turnover/end-multiple constraints;
- four start-date robustness slices;
- six economic-window event-held-out checks;
- adjacent-policy robustness to prevent a knife-edge selection.

If no candidate is eligible: `NO_PROMOTION / FAIL_STOP`. No post-result profile or multiplier retuning is allowed.

## Frozen product boundaries

- BRRK-0011 relative ranking unchanged;
- P4.1 defensive scale `[0,1]` unchanged;
- production gross cap `1.0`;
- actual zero-exposure -> risk-on remains explicit-human-gated;
- no automated withdrawals/external transfers;
- no production authorization.

## Exact next action

```text
CI-VERIFY / MERGE P5.5 PREREGISTRATION
VERIFY NEW MAIN
IMPLEMENT P5.5 RUNNER / VALIDATOR WITHOUT CHANGING CONTRACT
RUN PRE-RUN INPUT/PARITY GATES
RUN P5.5 ONCE
COMMIT IMMUTABLE RESULT
SELECT ONLY IF EVERY FROZEN GATE PASSES
THEN P5.6 INTEGRATES ONLY AN ACCEPTED SELECTION; OTHERWISE FAIL-STOP/BLOCK
```
