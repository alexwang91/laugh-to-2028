# BRRK Options Volatility Risk Premium 0087 — SPEC_FREEZE

Research ID: `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`
Gate: `SPEC_FREEZE`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`
Production/signature/order/withdrawal/transfer authority: `false`

## Scientific question

Does a single prospectively fixed 30-calendar-day at-the-money crypto options volatility-risk-premium mechanism for BTC and ETH exhibit persistent point-in-time variance compensation and positive delta-hedged short-volatility economics after frozen transaction and hedge costs, without result-informed family selection or rescue?

0087 is independent from 0085 Trend and 0086 Factor Atlas. It inherits zero lifecycle credit, attempt credit, source-selection credit, scientific value, parameter choice, or result from any earlier ID.

## Frozen venue and instrument universe

The eligible options venue is Deribit only. Eligible underlyings are exactly `BTC` and `ETH`. No SOL, altcoin, inverse venue substitution, CME, Binance options, OTC data, volatility-token data, or post-exposure venue addition is permitted.

At each weekly decision timestamp, the candidate option pair for each underlying is selected mechanically from point-in-time listed European options:

1. expiry must have `25 <= DTE <= 35` calendar days;
2. choose the expiry with minimum absolute distance from 30 DTE, tie-breaking to the earlier expiry;
3. within that expiry choose one call and one put with strike minimizing absolute log-moneyness `abs(log(K / S_t))`, where `S_t` is the contemporaneous frozen underlying index level;
4. require both bid and ask to be finite and strictly positive and require ask >= bid;
5. require each leg's relative bid-ask spread `(ask-bid)/mid <= 0.20`;
6. require the selected call and put to share the same strike; if the mechanically nearest strike lacks a valid pair, that underlying-week is unsupported rather than replaced by a different rule.

No delta bucket, skew wing, calendar spread, risk reversal, butterfly, or maturity family is tested in 0087.

## Frozen decision and maturity timing

Decision time is Monday 08:00 UTC. If Monday is unsupported, there is no within-week fallback timestamp. Option information timestamped after the decision time cannot affect that decision.

Each observation uses the mechanically selected 25–35 DTE pair at the decision timestamp. Economic holding continues until the earlier of expiry settlement or 30 calendar days after entry. No early close rule is allowed except mechanical invalid-source termination, which makes the observation unsupported rather than discretionary.

## Frozen volatility definitions

For each supported underlying-week:

- option mid = `(bid + ask) / 2`;
- call and put implied volatilities use the source's contemporaneous point-in-time IV field only if its schema and provenance are frozen at ARM; 0087 will not re-solve IV with an alternate model after exposure;
- `ATM_IV30` = arithmetic mean of the selected call and put IVs;
- `ATM_IVAR30` = `ATM_IV30^2`;
- future realized variance `RV30` uses exactly 30 calendar-day-equivalent daily close-to-close log returns from the frozen underlying index, annualized with factor 365;
- `VRP30` = `ATM_IVAR30 - RV30`.

A positive `VRP30` means implied variance exceeded subsequently realized variance. This is an ex-post scientific outcome, never an input available at the decision timestamp.

## Frozen economic implementation

The economic diagnostic is one delta-hedged short ATM straddle per supported underlying-week:

- sell one selected call plus one selected put at entry using executable bid prices, never midpoint;
- size each underlying sleeve to equal ex-ante option-premium notional contribution, then equal-weight BTC and ETH when both are supported;
- hedge option delta once per UTC day using the same frozen underlying/perpetual hedge instrument identity bound at ARM;
- hedge trades use the frozen executable price side and frozen fee/slippage panel;
- no gamma scalping timing variants, intraday hedge variants, discretionary hedge thresholds, leverage overlays, stop-losses, profit targets, or volatility targeting are permitted;
- expiry settlement follows the source's frozen contract settlement convention.

Primary economic output is net delta-hedged straddle PnL normalized by initial option premium paid/received in absolute value. Gross PnL is diagnostic only.

## Frozen cost panels

Exactly two implementation panels are evaluated, with no selection between them:

- `C1_REALISTIC`: actual option bid/ask execution plus 5 bps one-way hedge-instrument fee/slippage on hedge notional;
- `C2_STRESS`: actual option bid/ask execution plus 15 bps one-way hedge-instrument fee/slippage on hedge notional.

If the bound controlled source cannot supply point-in-time executable bid/ask prices for the selected option legs, 0087 cannot substitute marks or reconstructed spreads and must stop before RUN.

## Frozen support minimum

A valid scientific execution requires:

- at least 52 supported weekly observations in total;
- at least 20 supported weekly observations for BTC;
- at least 20 supported weekly observations for ETH;
- at least two distinct calendar years represented;
- every evaluated statistic finite.

Failure of these support minima with otherwise valid execution produces `INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT`.

## Frozen primary tests and trial budget

0087 has exactly one scientific candidate family and one sign direction: positive 30D ATM VRP / profitable delta-hedged short-volatility compensation.

The primary scientific series is the equal-weight cross-underlying weekly `VRP30` series when both underlyings are supported, otherwise the single supported underlying for that week. No asset weighting variant is tested.

Primary gates:

1. mean weekly `VRP30 > 0`;
2. two-sided HAC test of mean `VRP30 = 0` has `p < 0.05`;
3. moving-block bootstrap 95% CI for mean `VRP30` excludes zero on the positive side;
4. BTC and ETH standalone mean `VRP30` are both positive;
5. at least 3/4 chronological blocks have positive mean `VRP30`;
6. `C1_REALISTIC` mean normalized delta-hedged short-straddle PnL is positive;
7. `C2_STRESS` mean normalized PnL is non-negative;
8. at least 3/4 chronological blocks have positive `C1_REALISTIC` mean PnL.

Because only one predeclared candidate family exists, no cross-family multiplicity correction is applied. The declared parameter-candidate count is exactly 1. Per-underlying and block outputs are confirmation gates, not selectable trials.

## Frozen inference

Use a weekly moving-block bootstrap with block length 8 weeks, 4,000 replicates, deterministic seed `870087`. Use the same support rows for scientific and economic block diagnostics. HAC lag is 8 weeks.

No bootstrap seed, block length, HAC lag, confidence level, candidate definition, or threshold may change after controlled exposure.

## Terminal classifications

`PASS_OPTIONS_VRP_STRUCTURE` requires valid execution, all support minima, and every frozen primary gate G1–G8 to pass.

`FAIL_NO_ROBUST_OPTIONS_VRP` requires valid execution and adequate support but at least one frozen primary gate fails.

`INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT` requires valid execution but one or more frozen support minima fail before scientific PASS/FAIL adjudication.

`INVALID_EXECUTION` applies to any source identity/hash/schema violation, post-ARM source substitution, timestamp/lookahead violation, unsupported unrecorded fallback, non-finite persistence, candidate-count drift, network fetch during controlled execution, marker-order violation, duplicate controlled read, source-interface violation, engine invocation count other than exactly one, create-only result violation, or common-runner execution failure.

## Five-gate lifecycle and stopping rule

- `SPEC_FREEZE`: this file freezes science before any controlled value exposure.
- `BUILD`: implementation and tests may use synthetic/nonhistorical fixtures only.
- `ARM`: must bind exact options and hedge source identities, schemas, source keys, hashes/sizes, object selection rules, read budgets, result paths, and `ControlledResearchRunnerV1SourceQualified`; metadata only before marker.
- `RUN`: requires a separate explicit irreversible user authorization and may consume at most one attempt.
- `SEAL`: persists classification and evidence without scientific reread or recomputation.

If ARM cannot bind qualifying point-in-time Deribit BTC/ETH option bid/ask, IV, expiry/strike metadata, underlying index data, and hedge-price identities without controlled scientific value inspection or network substitution, 0087 stops before RUN. It may not switch venue, relax the spread gate, replace bid/ask with mark, change maturity, or create a replacement retry chain from that failure.

## What did not change

- 0076 remains sealed at its pre-marker read-boundary incident; no replacement, retroactive marker, same-ID continuation, rerun, retune, rescue, or recomputation is authorized.
- Phase6 remains immutable PASS closeout and is not evidence for any future final candidate shadow.
- `CONTROLLED_RESEARCH_RUNNER_V1` and its source-qualified interface remain the mandatory common runner for 0086+ controlled RUNs.
- 0085 remains immutable `INVALID_EXECUTION`, attempt 1/1 consumed, with no admissible Trend result.
- 0086 remains ARM-complete with controlled attempt 0/1, controlled reads 0, scientific engine 0/1, values unexposed, and requires separate irreversible authorization before RUN.
- Factor L/S remains blocked unless 0086 returns a valid PASS.
- 0072/0073 remain paused and 0083 remains immutable FAIL.
- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- No production, signing, order, withdrawal, or transfer authority is granted.
