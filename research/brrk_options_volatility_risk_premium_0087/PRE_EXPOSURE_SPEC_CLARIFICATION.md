# BRRK Options / VRP 0087 pre-exposure SPEC clarification

Research ID: `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`
Status: prospective same-ID clarification before any controlled scientific value exposure
Controlled attempt: `0/1`
Controlled reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`

This clarification resolves two scientific-mechanism ambiguities identified after merged SPEC_FREEZE but before any controlled value read. It is normative for any future 0087 BUILD requalification, ARM continuation, or RUN. It does not authorize a controlled attempt.

## Frozen daily delta hedge semantics

For each selected call and put, every daily hedge observation must use the Deribit source-native option delta field at the exact daily UTC hedge timestamp bound at ARM.

The short-straddle aggregate source delta is the source-native call delta plus source-native put delta after applying the frozen contract multiplier and frozen numeraire conversion bound at ARM. The hedge target in underlying units is exactly the negative of that aggregate short-straddle delta.

No Black-Scholes delta recomputation, mark-IV-derived delta, alternate Greek provider, stale carry-forward, interpolation across missing timestamps, or discretionary fallback is permitted. If either required source-native delta or the frozen contract/numeraire mapping is unavailable or invalid at a required hedge timestamp, that underlying-week is unsupported under the frozen support rules.

ARM must prove, using metadata/schema only before any controlled payload value read, the exact source-native delta field semantics, contract multiplier, numeraire conversion, hedge instrument identity, and daily hedge timestamp convention.

## Frozen terminal mechanics

Economic holding still ends at the earlier of expiry settlement or entry plus exactly 30 calendar days.

If the selected options remain alive at entry plus 30 calendar days, the engine must close both short option legs mechanically at executable ask quotes at the frozen terminal UTC timestamp. The engine may not use midpoint, mark, reconstructed spread, later quote, or model value. If either required ask is missing, non-finite, non-positive, or otherwise invalid under the frozen schema, that underlying-week is unsupported.

At the same terminal timestamp, the engine must close any residual underlying hedge inventory at the executable side using the same frozen hedge instrument and source schema. For expiry-settled observations, the option legs use the source-native settlement convention proven at ARM, and the engine closes residual hedge inventory at the frozen terminal hedge timestamp using executable quotes.

ARM must prove, using metadata/schema only before exposure, the day-30 option bid/ask identities, terminal timestamp convention, expiry settlement semantics, underlying hedge executable bid/ask identities, and the common accounting numeraire.

## BUILD requalification requirement

Before any ARM continuation, BUILD must requalify on synthetic/nonhistorical fixtures that exercise at least:

- source-native call plus put delta to hedge-target conversion;
- rejection of missing or invalid source-native deltas;
- rejection of stale/interpolated/fallback delta inputs;
- live-at-day-30 option close at executable asks;
- rejection of missing/invalid day-30 asks;
- residual hedge unwind at executable side;
- expiry-settlement path with the frozen source-native settlement convention;
- invariance of G1-G8, C1/C2 cost panels, support minima, candidate count, inference, and terminal rules.

Synthetic outcomes remain zero scientific evidence.

## Stop rule

0087 remains blocked from ARM continuation and RUN until both conditions hold: BUILD passes the requalification above, and independently staged qualifying Deribit point-in-time source metadata/schema can satisfy the frozen source requirements without controlled value inspection. Source availability cannot choose or alter these mechanics.

## What did not change

- Venue remains Deribit only; underlyings remain exactly BTC and ETH.
- Entry remains Monday 08:00 UTC with the frozen 25-35 DTE nearest-30D same-strike ATM selection and 20% spread gate.
- Candidate count remains exactly 1; sign direction, G1-G8, support minima, HAC lag 8, 8-week MBB, 4,000 replicates, seed `870087`, and C1/C2 cost panels do not change.
- 0087 controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine remains `0/1`; scientific values remain unexposed.
- 0086 remains ARM-complete at attempt `0/1` and still requires separate irreversible authorization before RUN. Factor L/S remains blocked unless 0086 validly PASSes.
- 0085 remains immutable `INVALID_EXECUTION`, attempt `1/1` consumed, with no admissible Trend result.
- 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; Phase6 PASS closeout remains immutable.
- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- `ControlledResearchRunnerV1SourceQualified` remains mandatory for any future controlled RUN.
- Production/signature/order/withdrawal/transfer authority remains false.
