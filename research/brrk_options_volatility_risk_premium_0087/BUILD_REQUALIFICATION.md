# BRRK Options / VRP 0087 BUILD requalification

Research ID: `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`
Gate: BUILD requalification after merged pre-exposure SPEC clarification
Evidence class: synthetic/nonhistorical only
Scientific evidence: none
Controlled attempt: `0/1`
Controlled reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`

## Purpose

Requalify the deterministic economic mechanics frozen by `PRE_EXPOSURE_SPEC_CLARIFICATION.md` before any ARM continuation. This gate does not inspect, fetch, decode, CRC-scan, decompress, or infer any controlled scientific payload.

## Mechanics requalified

- Source-native call and put deltas map deterministically to the underlying hedge target using only the ARM-bound contract multiplier and delta-unit scale.
- Missing, non-finite, or invalid source-native delta inputs fail closed. There is no Black-Scholes, mark-IV, interpolation, stale carry-forward, or alternate-provider fallback path.
- A straddle still alive at entry plus 30 calendar days closes at executable call and put asks through an explicit ask-side liability transform.
- Missing, non-finite, non-positive, or otherwise invalid day-30 executable asks fail closed.
- Residual hedge inventory unwinds at the executable side of the final frozen hedge quote.
- The day-30 option liability enters the same common-numeraire PnL core used by the expiry-settlement path.
- C1/C2 friction panels, candidate count, support minima, inference settings, and G1-G8 adjudication remain unchanged.

## Synthetic qualification tests

`test_pre_exposure_requalification.py` covers the mechanics above with synthetic values only. The tests do not represent a market observation and cannot support PASS, FAIL, or INCONCLUSIVE scientific classification.

## ARM continuation gate

Passing this BUILD requalification is necessary but insufficient for ARM continuation. 0087 remains fail-closed at `BLOCKED_NO_QUALIFYING_CONTROLLED_SOURCE_METADATA` until independently staged Deribit point-in-time source metadata/schema proves all frozen fields and conventions without controlled value inspection.

ARM must bind exact source-native delta fields, contract multiplier, delta-unit/numeraire mapping, hedge instrument identity, daily hedge timestamp, day-30 call/put executable ask identities, terminal timestamp, expiry settlement semantics, underlying executable bid/ask identities, and common accounting numeraire. ARM may not substitute a source after exposure.

## What did not change

- Deribit only; BTC and ETH only.
- Monday 08:00 UTC entry, 25-35 DTE nearest-30D selection, same-strike ATM pairing, and 20% spread gate remain frozen.
- Candidate count remains exactly 1; G1-G8, support minima, HAC lag 8, 8-week moving-block bootstrap, 4,000 replicates, seed `870087`, and C1/C2 cost panels remain frozen.
- 0087 attempt remains `0/1`; reads remain `0`; engine remains `0/1`; scientific values remain unexposed; no RUN marker exists.
- 0086 remains ARM-complete at attempt `0/1` and requires separate irreversible authorization before RUN. Factor L/S remains blocked unless 0086 validly PASSes.
- 0085 remains immutable INVALID_EXECUTION with attempt `1/1` consumed and no admissible Trend answer.
- 0076 remains sealed; 0072/0073 remain paused; 0083 remains immutable FAIL; Phase6 PASS closeout remains immutable.
- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- `ControlledResearchRunnerV1SourceQualified` remains mandatory for future controlled RUNs.
- Production/signature/order/withdrawal/transfer authority remains false.
