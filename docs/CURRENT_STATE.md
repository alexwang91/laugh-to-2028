# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0.1 / P0.2: PASS / MERGED
- P1.1 through P1.8: PASS / MERGED; Phase 1 COMPLETE
- P2.1 through P2.4: PASS / MERGED; Phase 2 COMPLETE
- P3.1 schema-v2 data contract: PASS / MERGED / validated by PR #75
- P3.2 Target calculation API: PASS / TESTED / CI VERIFIED / MERGED by PR #76
- P3.3 rebalance / turnover controls: PASS / TESTED / CI VERIFIED / MERGED by PR #78
- P3.4 weekly/manual contribution handling: PASS / TESTED / CI VERIFIED / MERGED by PR #80
- **Phase 3 COMPLETE**
- PR #73 remains historically MERGED without a recorded green required PR-governance run before merge; do not retroactively relabel it CI VERIFIED
- PR #74 remains historically MERGED during the GitHub Actions incident without its own pre-merge workflow evidence; PR #75 subsequently validated the merged schema-v2 state
- Historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

Current main after P3.4 merge:

`949fb9f1d079df7c2462a4b13b0eb778e91bb3ae`

```text
P3.1 schema-v2 data contract           PASS / MERGED
P3.2 Target calculation API            PASS / MERGED
P3.3 rebalance / turnover controls     PASS / MERGED
P3.4 weekly contribution handling      PASS / MERGED
PHASE 3                                 COMPLETE
P4 leverage / operating risk budget    UNIQUE NEXT ROADMAP PHASE
P5 exit intelligence                   BLOCKED UNTIL P4
```

No P4 implementation should begin from memory. The exact P4 roadmap section must be reread from `docs/IMPLEMENTATION_ROADMAP_2026-08-05.md` after this normalization merges.

## Frozen Phase 3 production-quality daily chain

```text
P3.1 canonical daily data
-> P3.2-BRRK0011-V1 target
-> P3.3-L1-BAND-V1 target-to-position control
-> P3.4-EQUITY-CHANGE-DAILY-V1 contribution timing/equity handling
```

Frozen boundaries remain:

```text
target assets = BTC, ETH, SOL, BNB
feature-only  = XRP
P3.2 gross    <= 1
short targets forbidden
P3.3 routine L1 band = 0.05
P3.4 intraday contribution observation = record only / no risk increase
```

P3.2 committed golden vectors remain unchanged at `research/results/p3_2_target_parity/golden_v1.json`.

## P3.4 merged semantics

Machine policy:

`config/contribution_policy.json`

Version:

`P3.4-EQUITY-CHANGE-DAILY-V1`

Roadmap authority:

> Manual deposit is detected as equity change and included at the next daily decision.

Merged behavior:

- account-equity change is observed relative to the previous accepted daily-decision equity;
- positive change is a contribution candidate, not confirmed transfer-source attribution;
- intraday observation never recalculates target and never authorizes risk increase;
- a candidate is included only at the next eligible 00:00 UTC daily decision;
- an already-accepted 00:00 boundary cannot be replayed;
- fresh full account equity at the scheduled decision is passed through unchanged P3.2 and P3.3;
- the approximately `$100/week` assumption is not a detection threshold, fixed weekday, or scheduler trigger;
- contribution amount is diagnostic only; there is no contribution-specific allocation sleeve;
- deterministic observation and daily-decision digests preserve auditability;
- production authorization remains false/unchanged.

## PR #80 final evidence

Final PR head:

`f8069823428879e05309995870af8f293ce4289b`

Final-head evidence:

- `Phase 0 baseline contract` run `31159909523` (#121): **SUCCESS**
  - execution pytest: **215 passed in 7.58s**
  - research integration contract: **5 tests / OK**
- `Research evidence normalization` run `31159909467` (#32): **SUCCESS**
- `P3.2 target research-live parity` run `31159909468` (#19): **SUCCESS**
  - independent multi-date BRRK target parity: SUCCESS
  - committed historical golden enforcement: SUCCESS
- final PR-body governance run `31160307257` (#159): **SUCCESS**
- expected-head squash merge: `949fb9f1d079df7c2462a4b13b0eb778e91bb3ae`

Same-PR correction history is preserved in PR #80. The only initial Phase-0 failure was a test fixture/assertion using a stale product ID; runtime P3.4 logic was unchanged. The canonical product ID fixture was normalized, all 215 execution tests passed, and the final head was fully revalidated. A final no-op commit changed no file content and was also fully revalidated before merge.

## P3.4 closure status

```text
IMPLEMENTED:           YES
TESTED:                YES
CI VERIFIED:           YES
MERGED:                YES
PRODUCTION AUTHORIZED: NO_CHANGE
```

## P4 boundary

P4 is now the unique next roadmap phase, but it remains **unimplemented** in this normalization.

Before any P4 branch/code/research mutation:

1. reread the exact P4 roadmap section;
2. preserve the current 0–1 corrected CVaR/CDaR scaler as baseline;
3. do not treat the 70% catastrophe tolerance as an operating target;
4. keep >1 gross exposure unauthorized until the P4 preregistration/evidence/governance sequence explicitly permits it;
5. keep F23 funding-response redesign separate unless a registered P4 experiment explicitly owns a defined dependency;
6. keep P5 exit intelligence blocked.

## Production authorization

```text
NO_CHANGE
production_authorized_components = []
```

No P3.4 merge or normalization action authorizes live trading, leverage >1, shorts, withdrawals, or master-wallet-key use.

## Project drift audit

```text
DRIFT_0
```

Phase 3 is complete without altering the frozen BRRK-0011 directional authority or production authorization.

## Exact next action

```text
post-P3.4 normalization PR
-> docs-only self-review
-> applicable CI / P3.2 parity / governance
-> record exact final-head evidence in PR metadata
-> newest body-edit governance GREEN
-> expected-head merge normalization
-> verify new main
-> reread exact P4 roadmap section
-> only then create a fresh P4 branch and execute the registered P4 sequence
```
