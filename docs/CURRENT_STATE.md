# BRRK Current State

Last updated: 2026-08-07
Status: authoritative cross-chat handoff snapshot

## Authoritative baseline

- P0 / P1 / P2: PASS / MERGED; Phases 0–2 complete
- P3.1 through P3.4: PASS / TESTED / CI VERIFIED / MERGED; **Phase 3 COMPLETE**
- P4.1 corrected 0–1 baseline freeze: PASS / TESTED / CI VERIFIED / MERGED by PR #82
- P4.2 `LEVERAGE-0039` preregistration: PASS / TESTED / CI VERIFIED / MERGED by PR #82
- historical stale-main PR #70: INVALID / CLOSED / DO NOT REVIVE

## Current main and roadmap position

P4.1/P4.2 merge on main:

`6d0e497583607e09991593588e62df7fb418087c`

```text
P4.1 preserve corrected 0-1 scaler   PASS / MERGED
P4.2 preregister leverage study      PASS / MERGED
P4.3 generalized selector / runner   UNIQUE NEXT IMPLEMENTATION
P4.4 stress execution                BLOCKED UNTIL P4.3
P4.5 promotion decision              BLOCKED
P4.6 deployment cap                  BLOCKED
P5 exit intelligence                 BLOCKED
```

**LEVERAGE SEARCH RUN: NO. RESULT SELECTED: NO. OPERATING BUDGET FROZEN: NO. >1 RUNTIME IMPLEMENTED: NO.**

## P4.1 frozen baseline now on main

Machine freeze:

`research/leverage_0039/P4_1_BASELINE_FREEZE.json`

Freeze ID:

`P4.1-BRRK0011-CORRECTED-0-1-V1`

Frozen base authority:

- source base `fee2ebd34e71f62fb8aaa9e11787aa7413f122cd`;
- corrected risk blob `bdf7cd6cb32961765716e4cb07288739e869703e`;
- product target-math blob `4a0b26943438045f2baacbe06d92650a486a8967`;
- regime config blob `eecd092ac45c5fa86992a8de2f31d470405e6b5a`;
- corrected BRRK-0011 result blob `40cd0e90a357a2c2e5be0b9de69feaf0f1e75eaf`;
- F27 R2 blob `46b509bf1b59a9d87a9092f9708eb41e5f8e50af`.

Frozen risk layer remains:

```text
scale domain                 0.0 .. 1.0
scenario CVaR/CDaR budget    20%
production gross cap         1.0
operating risk budget        UNFROZEN
catastrophic DD boundary     70% termination boundary, not operating target
```

Corrected BRRK-0011 reference remains CAGR 65.104%, MDD -33.715%, Sharpe 1.3532, Calmar 1.9310, realized path CDaR95 31.781%, average gross 0.75430. F27 R2's raw calendar-span CAGR remains separately labeled at 65.16609785339962%; the metric conventions are not silently reconciled.

## P4.2 preregistration now on main

Machine preregistration:

`research/leverage_0039/LEVERAGE-0039.json`

Status remains:

`PREREGISTERED_BEFORE_FIRST_RUN`

Frozen first-study search domain:

```text
research caps              1.00 / 1.10 / 1.20 / 1.30
operating MDD constraints  35% / 40% / 45% / 50%
matched cost grid          5 / 10 / 20 / 50 bps
scenario CVaR/CDaR budget  20%
catastrophe boundary       70%
```

Only allowed structural change is the upper bound of the same corrected CVaR/CDaR selector. Cap=1.00 exact baseline parity is mandatory before any >1 result is valid. Search above 1.30 requires a new experiment ID.

Funding remains exogenous cost only: Hyperliquid native common-window evidence is mandatory, Binance funding is proxy/stress-only, missing native funding is not zero-filled, and no funding signal/threshold is allowed. F23 remains separate.

Historical/synthetic stress, liquidation-distance fail-closed, start-date robustness and stationary-block bootstrap requirements remain exactly preregistered. Early periods that fail the frozen BRRK training-eligibility rule remain explicitly labeled conservative pre-BRRK stress proxies.

## PR #82 final evidence

Final head:

`fb76346eac2964a5b41215001b0c6441a22c2e27`

- Phase 0 run `31163656193` (#126): **SUCCESS**, **224 passed in 7.87s**, 5/5 integration OK
- Research evidence run `31163656181` (#37): **SUCCESS**
- P3.2 parity/golden run `31163656179` (#24): **SUCCESS**, independent parity + committed golden
- final body-edit governance run `31163843751` (#166): **SUCCESS**
- expected-head squash merge: `6d0e497583607e09991593588e62df7fb418087c`

Same-PR provenance correction: self-review found the correction-result path was correct but its initially pinned blob SHA was wrong. The live frozen-base SHA `40cd0e90...` was corrected and exact authority-blob regression coverage was added before final-head validation. No leverage search or model result was produced.

## P4.3 boundary

P4.3 is now the unique next implementation, but **LEVERAGE-0039 must still not be executed yet**.

Required order:

1. fresh branch from post-normalization main;
2. snapshot/hash canonical Hyperliquid margin/leverage-tier inputs used for liquidation-distance modeling;
3. implement a generalized corrected selector/runner without changing BRRK relative targets, HMM, Student-t model, P3.3/P3.4 semantics or 20% scenario tail budget;
4. prove cap=1 exact baseline parity first;
5. only after those inputs and parity are frozen may `LEVERAGE-0039` be executed exactly once;
6. no post-result retuning under the same experiment ID.

## Explicit boundaries

Still forbidden before evidence/governance permits them:

- production gross >1;
- production leverage authorization;
- search above 1.30 under `LEVERAGE-0039`;
- EXPOSURE-SMOOTH-0038 promotion;
- F23 funding-response logic;
- shorts / XRP targets;
- P5 exit intelligence;
- historical BRRK result overwrite.

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
merge this docs-only post-P4.1/P4.2 normalization
-> verify main
-> fresh P4.3 branch
-> snapshot/hash Hyperliquid margin/leverage-tier inputs
-> implement generalized corrected selector / runner
-> cap=1 exact baseline parity
-> only then execute LEVERAGE-0039 exactly once
```
