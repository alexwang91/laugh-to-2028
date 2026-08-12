# BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-INTERFACE-REPLICATION-0057 — Design Freeze

Date: 2026-08-12

Status: **DESIGN-ONLY / NO NUMERICAL PREREG / NOT IMPLEMENTED / NOT RUN**

## 1. Research identity and purpose

New research ID:

`BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-INTERFACE-REPLICATION-0057`

0057 is a new-ID, prospectively governed interface-corrected replication of the economic question that 0056 failed to measure. It is not a rerun, rescue or repair of 0056 under the same ID.

0056 is immutable at `INVALID_EXECUTION / CLOSED`. Its unique run stopped at G0 because the frozen 0047/0048 market loader emits UTC-normalized tz-naive daily indexes while the frozen 0056 validator requires timezone-aware UTC. 0056 produced no terminal wealth, CAGR, G1-G4 statistic or evidence for or against RM60 economic efficacy.

0057 asks the same unresolved scientific question:

> Does one fixed, simple, causal 60-day ETH/SOL relative-trend router improve net full-cycle terminal wealth and net CAGR versus each frozen static Beta holding after realistic switching costs, once the already-identified source/validator timezone representation mismatch is corrected by one deterministic interface adapter?

The purpose of 0057 is measurement, not model search.

## 2. Binding prior evidence

0057 treats all 0056 governance and invalid-execution evidence as exposed.

Binding facts:

- 0056 design/prereg/implementation/boundary are immutable.
- 0056 unique execution used controlled HEAD `186a7f7d57c957c98798ecd828533ffe20dedb83`.
- 0056 final status is `INVALID_EXECUTION_CLOSED`.
- The only observed scientific failure was `RouterProtocolError: price index timezone must be UTC` at G0.
- 0056 produced no router/static NAV paths, no terminal wealth/CAGR and no G1-G4 economic result.
- 0047/0048 source loader explicitly requires UTC-normalized tz-naive daily `DatetimeIndex` values.
- Frozen 0056 `validate_price_frames()` explicitly requires timezone-aware `UTC` indexes.

Therefore the timezone representation mismatch may be corrected under a new ID without using any exposed economic outcome, because no economic outcome exists.

## 3. Frozen scientific mechanism — no change from 0056

The economic mechanism is not reopened for design selection.

The intended numerical preregistration must inherit the complete 0056 economic contract without scientific change, including:

```text
z_t                    = log(SOL_t / ETH_t)
RM60_t                 = z_t - z_(t-60)
RM60_t > 0             -> SOL
RM60_t < 0             -> ETH
RM60_t = 0             -> retain prior holding
first routable zero    -> ETH fallback
causal timing          completed close t -> next t to t+1 close-to-close return
Beta sleeve            100% ETH or 100% SOL
variant budget         exactly 1
```

No 20/30/90/120-day sweep, EMA, MACD, RSI, threshold, deadband, minimum hold, CORE4 overlay, probability model, ML model, BTC timing, cash timing, leverage, shorting or oracle rule is opened.

## 4. Frozen benchmark and portfolio family — no change from 0056

The intended numerical preregistration must preserve exactly:

- B0: static 100% ETH, one initial entry then buy-and-hold.
- B1: static 100% SOL, one initial entry then buy-and-hold.
- B2: initial 50/50 ETH/SOL, then both components drift naturally with no periodic rebalance.
- candidate: fully invested one-hot ETH/SOL router.
- starting NAV: 1.0 cash immediately before the first entry.
- no BTC or cash allocation after entry.

Primary objective remains terminal wealth / net CAGR. MDD remains diagnostic rather than an optimization target.

## 5. Frozen data family — no new data freedom

0057 may reuse only the same immutable researcher-exposed daily DEVELOPMENT history used by 0056:

```text
source wrapper       research/brrk_beta_handoff_0047/evidence/MARKET_EVIDENCE.json
source git blob      64ebf5c6deaf3f34dbeac715378f196ff0f4fafe
payload SHA256       d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193
common rows          2183
common window        2020-08-11 through 2026-08-02
contamination        RESEARCHER_EXPOSED_HISTORY
independent OOS      false
```

No refetch, provider substitution, row extension, row removal, gap filling, resampling, intraday substitution or alternate payload is permitted.

## 6. Sole allowed interface correction

0057 freezes exactly one source-to-scientific-engine adapter architecture.

The adapter must:

1. Load the immutable market evidence using the existing frozen 0047/0048 loader semantics.
2. Select only ETH and SOL frames for the Beta router.
3. Verify both indexes are `DatetimeIndex`, tz-naive, midnight-normalized, identical, unique and strictly increasing.
4. Verify row count, date labels, row ordering and close arrays before adaptation.
5. Create copies of the ETH/SOL frames.
6. Apply only `index.tz_localize("UTC")` to each copied index.
7. Verify after localization that calendar date labels, row count, ordering and every close value are unchanged.
8. Pass the adapted ETH/SOL frames to the immutable 0056 scientific mechanics.

Forbidden adapter operations:

- `tz_convert`;
- any time shift or date offset;
- resampling;
- row drop/add/reorder;
- forward/back fill;
- interpolation;
- close/value transformation;
- network fetch;
- alternate market loader;
- scientific-engine modification.

The adapter is a representation bridge only. It has zero authority to change portfolio logic or economic gates.

## 7. Immutable scientific-engine dependency

The intended 0057 implementation must delegate the portfolio-economic calculation to the immutable 0056 engine blob:

```text
path      research/brrk_simple_eth_sol_beta_router_0056/engine.py
blob      b0fc1ac267a66593e7e2c4687aff81491bfcdf5a
```

0057 must not edit that file.

A thin 0057 wrapper may provide 0057 research identity and adapter integrity attestations around the upstream measurement, but may not alter upstream numeric outputs, gates, benchmark paths, bootstrap statistics or classification precedence.

## 8. Numerical contract inheritance requirement

Design does not authorize execution. A separate numerical/data preregistration must still merge before implementation.

That preregistration must explicitly bind, without relaxation, the 0056 values for:

- exact evaluation window and 2,122 held periods;
- 5 bps primary and 10/20 bps stress executed-L1 costs;
- strict `1e-12` economic dominance tolerance;
- B0/B1/B2 semantics and deterministic tie priority;
- fixed 531/531/530/530 temporal blocks;
- 3-of-4 temporal gate;
- paired moving-block bootstrap block length 60;
- 10,000 replicates;
- seed `1844716895`;
- Type-7/NumPy-linear 95th percentile;
- simultaneous lower-bound construction;
- complete G0-G4 classification hierarchy;
- same secondary diagnostics;
- same FAIL/PASS stop semantics.

No numerical parameter may be changed merely because 0056 was invalid.

## 9. New G0 interface-integrity surface

0057 G0 must additionally prove, before any economic interpretation:

- exact immutable source wrapper/blob/payload identity;
- source indexes satisfy the frozen tz-naive 0047/0048 contract;
- adapter operation is exactly `tz_localize("UTC")`;
- pre/post adapter row count, calendar labels, ordering and close arrays are identical;
- adapted frames satisfy the immutable 0056 engine's UTC-aware input contract;
- immutable 0056 scientific engine blob matches the frozen dependency;
- no extra variant, strategy parameter or data path is present.

Failure of this interface-integrity layer is an invalid execution and cannot be interpreted economically.

## 10. Stop rule

0057 is a new research ID because 0056 permanently lost recomputation authority after its durable attempt marker.

Once 0057 later produces a valid result, the same no-rerun rule applies: no same-ID rerun, retuning, alternate lookback, indicator substitution, threshold rescue, adapter substitution, benchmark replacement, cost reinterpretation, temporal repartition or bootstrap change.

If the valid 0057 economic result fails the inherited economic gates, stop the ETH/SOL micro-timing line and move any continuation to a new-ID Beta-to-BTC continuation-value question.

If 0057 passes, any BTC-anchor plus routed-Beta integration still requires a new research ID.

If 0057 itself is invalid for a different implementation/protocol reason, preserve the invalid result; no same-ID rerun is authorized after a durable attempt.

## 11. Production and canonical authority

0057 is DEVELOPMENT research only.

```text
Canonical BRRK-0011              NO CHANGE
Phase 6                          NO CHANGE
production_authorized_components []
production_authorized            false
signature_authorized             false
order_submission_authorized      false
```

No design outcome authorizes trading or production promotion.

## 12. Stage boundary

This file is design-only.

At this stage:

```text
0057 numerical preregistration     ABSENT
0057 central registry owner        ABSENT
0057 implementation                ABSENT
0057 controlled execution boundary ABSENT
0057 historical execution          NOT RUN
0057 result                        ABSENT
0057 actual variants evaluated     0
```

The only allowed next step after design merge is a separate numerical/data preregistration that freezes the inherited 0056 economic contract and the exact one-adapter interface-integrity rules before implementation.
