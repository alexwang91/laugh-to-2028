# BRRK Simple ETH/SOL Beta Router Interface Replication 0057

Status: **CONTROLLED-EXECUTION BOUNDARY ON BRANCH / ZERO RESULT / REAL HISTORICAL RUN NOT RUN**

Research ID: `BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-INTERFACE-REPLICATION-0057`

## Purpose

0057 is the new-ID measurement-fix replication authorized after 0056 closed `INVALID_EXECUTION` before any portfolio-economic output. It asks the same economic question as 0056 and changes only the already-identified source-index representation bridge.

## Frozen interface correction

The immutable 0047/0048 source loader represents UTC daily dates as tz-naive `DatetimeIndex` values. The immutable 0056 portfolio engine requires timezone-aware `UTC` indexes.

0057 permits exactly one deterministic adapter:

```text
validate immutable tz-naive ETH/SOL source frames
copy frames
copied_frame.index = copied_frame.index.tz_localize("UTC")
prove row count / calendar labels / order / close values unchanged
pass adapted frames to immutable 0056 engine
```

`tz_convert`, time shifts, resampling, row mutation, fill/interpolation, refetch, alternate providers/loaders and portfolio-engine rewrites are forbidden.

## Scientific contract

All portfolio science is inherited unchanged from 0056:

- RM60 sign router only;
- exact-zero retain-prior rule with initial ETH fallback;
- completed close `t` decision, next close-to-close holding period;
- B0 static ETH, B1 static SOL, B2 initial 50/50 drifting buy-and-hold with no rebalancing;
- executed-L1 transaction costs: 5 bps primary, 10/20 bps stress;
- 2,122 held periods ending 2026-08-02;
- fixed chronological blocks 531/531/530/530;
- paired moving-block bootstrap length 60, 10,000 replicates, seed `1844716895`;
- strict tolerance `1e-12`;
- inherited G0-G4 classification precedence.

The immutable scientific calculator is 0056 `engine.py` blob `b0fc1ac267a66593e7e2c4687aff81491bfcdf5a`.

## Data authority

The only allowed market evidence is `research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json`, blob `64ebf5c6deaf3f34dbeac715378f196ff0f4fafe`, payload SHA256 `d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193`.

All history is researcher-exposed DEVELOPMENT history. It is not independent OOS and cannot authorize production.

## Current authority

```text
design                         MERGED AT 21f758260ea80040bbb38aec26e2091814e37fd9
central registry owner         REGISTERED BEFORE FORMAL PATH
numerical preregistration      MERGED AT bc61a6a2250d8deecf2f20d2fe2006b28ad4b819
implementation                 MERGED AT 6ea85e0b55566cc1aeed705eae35ad81f165e56d
controlled execution boundary  FROZEN ON BRANCH / ZERO RESULT
historical execution           NOT RUN
result                         PREREGISTERED_NOT_RUN
actual variants evaluated      0
canonical BRRK                 NO CHANGE
Phase 6                        NO CHANGE
production_authorized          false
signature_authorized           false
order_submission_authorized    false
```

Synthetic run `31611937198` passed 15 immutable 0056 engine tests plus 7 new 0057 adapter tests and a zero-result guard. No real market payload was loaded; actual historical variants remain 0. Real historical portfolio evaluation is still forbidden until this implementation stage merges and a separate controlled-execution boundary merges. Controlled-boundary run `31613546954` additionally passed 7 adapter tests plus 10 exactly-once/fault-contract tests and a second zero-result guard. The first boundary tooling run `31613437898` failed only because the test environment omitted `requests`; it produced no research output. Historical evaluation remains forbidden until this boundary is merged and an explicit unique execution is separately triggered.


## Immutable closeout

Unique DEVELOPMENT run `31618590484` completed exactly once with classification `FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE`. G0/G1/G3 passed; G2/G4 failed. The router is not eligible for promotion, same-ID recomputation is permanently forbidden, and the ETH/SOL micro-timing line is closed. See `PRIMARY_RESULT.json`, `EXECUTION.json`, `RUN_ONCE.marker`, `RESULT.md`, and `CLOSEOUT.json`.
