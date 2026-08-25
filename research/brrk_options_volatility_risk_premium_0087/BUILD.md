# BRRK Options Volatility Risk Premium 0087 — BUILD

Research ID: `BRRK-OPTIONS-VOLATILITY-RISK-PREMIUM-0087`
Gate: `BUILD`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Scientific values exposed: `false`
Production/signature/order/withdrawal/transfer authority: `false`

## Build scope

This gate implements the merged SPEC_FREEZE using synthetic/nonhistorical fixtures only. BUILD does not bind a controlled Deribit source, download controlled history, inspect historical payload values, create a RUN marker, or invoke a scientific controlled engine.

The frozen scientific and economic core lives in `research/brrk_options_volatility_risk_premium_0087/engine.py`. ARM may add only the exact source/schema adapter required to construct the normalized inputs consumed by this core. ARM cannot change the scientific adjudication or hedge-accounting formulas implemented here.

## Exact implementation frozen here

- same-strike ATM selection requires positive finite bid/ask, `ask >= bid`, relative spread at most `0.20`, and mechanically chooses the strike minimizing `abs(log(K/S_t))`;
- `ATM_IVAR30` is the square of the arithmetic mean of the selected call and put contemporaneous source IVs;
- `RV30` uses exactly 31 index closes / 30 close-to-close log returns and annualizes squared returns by 365;
- normalized weekly rows are keyed uniquely by `(underlying, week)` and duplicate identities fail closed;
- the primary weekly series equal-weights BTC and ETH when both exist and uses the single supported underlying otherwise;
- support requires at least 52 distinct supported weekly timestamps in total, at least 20 supported observations each for BTC and ETH, and at least two calendar years;
- HAC uses lag 8 and a two-sided large-sample normal test of the mean;
- moving-block bootstrap uses block length 8 weeks, 4,000 replicates, deterministic seed `870087`, and a 95% percentile interval;
- four chronological blocks use deterministic rounded boundaries `round(i*n/4)`;
- G1-G8 implement the merged SPEC_FREEZE literally;
- adequate valid support with all G1-G8 true returns `PASS_OPTIONS_VRP_STRUCTURE`; adequate valid support with any gate false returns `FAIL_NO_ROBUST_OPTIONS_VRP`; support failure returns `INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT`;
- declared candidate count remains exactly `1`.

## Frozen economic core

BUILD now freezes the delta-hedged short-straddle accounting independently of any historical source schema:

- entry premium equals executable selected call bid plus executable selected put bid;
- option payoff at settlement is the same-strike call payoff plus put payoff;
- the hedge target at each daily UTC hedge point equals source-native `call_delta + put_delta`, which offsets the delta of the short call-plus-put position;
- hedge inventory accrues spot PnL between adjacent daily hedge points;
- each rebalance pays executable-side slippage relative to contemporaneous spot and one-way friction on absolute traded hedge notional;
- the final hedge point must coincide with settlement and the hedge inventory is mechanically unwound there;
- normalized PnL equals option PnL plus hedge PnL divided by absolute initial option premium;
- `C1_REALISTIC` applies 5 bps one-way hedge friction and `C2_STRESS` applies 15 bps.

ARM must bind a qualifying point-in-time source that can mechanically supply each weekly observation from executable option bid/ask, contemporaneous source IV, expiry/strike metadata, underlying index closes, source-native option deltas and executable daily hedge quotes. ARM may freeze field names and schema mappings only if metadata/schema evidence supports them before controlled value exposure. If it cannot, 0087 stops before RUN. It may not substitute midpoint marks, reconstructed spreads, a different venue, maturity, hedge cadence, post-exposure delta model, or alternate PnL accounting.

## Synthetic qualification

`research/governance/test_0087_options_vrp_build.py` uses generated values only and covers:

- exact bootstrap/HAC constants;
- same-strike ATM selection and spread rejection;
- source-IV `ATM_IVAR30`;
- exact 30-return realized variance window;
- distinct-week support counting rather than underlying-row counting;
- pure short-straddle economic accounting and stress-cost monotonicity;
- valid insufficient-support classification;
- full synthetic PASS across all G1-G8;
- adequate-support scientific FAIL;
- duplicate underlying-week fail-closed behavior.

Synthetic PASS/FAIL outcomes carry no scientific evidence and consume no attempt budget.

## ARM boundary

ARM must bind exact controlled Deribit option, index and hedge artifact/object identities; declared hashes and sizes; source keys; point-in-time timestamps; required schema fields; source-qualified runner interface; read budget; marker/result/RUN_ONCE paths; and exactly-one engine invocation budget.

Before the durable marker, ARM/RUN preflight may inspect only Git/artifact identity, filenames, central-directory metadata, declared hashes and sizes. It must not call `testzip()`, decompress controlled payloads, CRC-scan payload contents, parse historical rows, or expose scientific values.

Any future controlled RUN must use `ControlledResearchRunnerV1SourceQualified` and requires a separate explicit irreversible user authorization.

## What did not change

- 0087 still tests exactly one Deribit BTC/ETH ATM 30D VRP candidate with the merged venue, maturity, timing, cost panels, support gates, inference settings and terminal rules.
- Controlled attempt remains `0/1`; controlled reads remain `0`; scientific engine calls remain `0/1`; scientific values remain unexposed.
- 0086 remains ARM-complete at attempt `0/1` and still requires separate irreversible authorization before RUN. Factor L/S remains blocked unless 0086 returns a valid PASS.
- 0085 remains immutable `INVALID_EXECUTION`, attempt `1/1` consumed, with no admissible Trend result and no same-ID rerun/rescue/recompute.
- 0076 remains sealed at its pre-marker read-boundary incident. 0072/0073 remain paused. 0083 remains immutable FAIL.
- Phase6 remains immutable PASS closeout and is not evidence for a future final-candidate shadow.
- `CONTROLLED_RESEARCH_RUNNER_V1` source-qualified interface remains mandatory for 0086+ controlled RUNs.
- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- No production, signing, order, withdrawal, or transfer authority is granted.
