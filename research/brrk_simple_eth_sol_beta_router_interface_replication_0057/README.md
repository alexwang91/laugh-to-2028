# BRRK Simple ETH/SOL Beta Router Interface Replication 0057

Status: **NUMERICAL PREREGISTRATION / NOT IMPLEMENTED / NOT RUN**

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
numerical preregistration      FROZEN ON BRANCH / NOT YET MERGED
implementation                 ABSENT
controlled execution boundary  ABSENT
historical execution           NOT RUN
result                         PREREGISTERED_NOT_RUN
actual variants evaluated      0
canonical BRRK                 NO CHANGE
Phase 6                        NO CHANGE
production_authorized          false
signature_authorized           false
order_submission_authorized    false
```

No real historical portfolio evaluation is authorized until this preregistration merges, a separate implementation-only stage merges, and a separate controlled-execution boundary merges.
