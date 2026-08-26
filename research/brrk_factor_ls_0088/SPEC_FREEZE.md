# BRRK Factor Long/Short 0088 — SPEC FREEZE

Research ID: `BRRK-FACTOR-LS-0088`
Lifecycle: `PROSPECTIVE_FIVE_GATE_LIFECYCLE_V1`
Current gate: `SPEC_FREEZE`
Controlled attempt: `0/1`
Controlled value reads: `0`
Scientific engine calls: `0/1`
Production/signature/order/withdrawal/transfer authority: `false`

## Scientific question

Can one prospectively fixed long/short portfolio built only from the three immutable 0086 passing factor directions produce positive, robust weekly net returns after turnover, funding, stressed costs, concentration, capacity, and market-beta checks?

0088 is a new downstream research ID unlocked by the immutable 0086 PASS. It is not a replacement, retry, continuation, rescue, or reinterpretation of 0076. It inherits zero lifecycle credit, attempt credit, portfolio-rule credit, or scientific result from 0076 or any other historical Factor L/S line.

## Owner-first boundary and immutable dependency

The central owner record for `BRRK-FACTOR-LS-0088` was committed to `config/research_registry.json` before this governed path existed.

0088 may use exactly these immutable 0086 outputs and no others:

- `MOM60_RAW`: sign `-1`;
- `RVOL20_RAW`: sign `-1`;
- `LIQ30_RAW`: sign `+1`.

The factor identities and signs come from the sealed 0086 `PRIMARY_RESULT.json` and `CLOSEOUT.md`. 0088 may not remove a factor, change a sign, add a factor, fit coefficients, optimize weights, or choose a subset after seeing portfolio results.

## Frozen point-in-time universe

At each weekly decision time:

1. venue is Binance USD-M USDT perpetuals only;
2. an instrument must have at least 120 completed daily sessions before the decision session closes;
3. eligibility uses only information available through that completed decision session;
4. rank eligible instruments by trailing 30 completed-session median quote volume;
5. select the point-in-time top 30;
6. require all three frozen factor values finite for an instrument;
7. require at least 21 eligible instruments after finite-data checks or that portfolio week is invalid;
8. later listings, delistings, symbol changes, or future liquidity cannot alter past membership.

No survivorship-based terminal universe is allowed.

## Frozen decision timing and holding horizon

- decision cadence: Monday UTC daily-session close only;
- factor observation window ends at completed decision session `t`;
- portfolio weights become effective after close `t`;
- holding outcome uses close `t` to fully matured close `t+5` simple perpetual price return;
- incomplete final horizons are excluded mechanically;
- no intraday price information enters factor or price-return construction.

## Frozen composite score

For each valid weekly cross-section and each frozen factor:

1. compute the exact 0086 raw factor definition;
2. rank finite values using average ranks for ties;
3. convert rank to centered percentile `p=(rank-1)/(n-1)-0.5`;
4. multiply by the immutable 0086 sign;
5. define `COMPOSITE0088=(signed_MOM60 + signed_RVOL20 + signed_LIQ30)/3`.

Higher `COMPOSITE0088` means higher prospectively expected return. Equal one-third factor weights are mandatory. No z-score, clipping, winsorization, neutralization, residualization, volatility scaling, coefficient fitting, factor weighting variant, nonlinear transform, or alternate rank method is allowed.

## Frozen portfolio construction

For each valid week with `n>=21` eligible assets:

- let `k=floor(n/3)`;
- long the `k` highest composite scores;
- short the `k` lowest composite scores;
- ties at a basket boundary use ascending canonical source symbol as the deterministic secondary key;
- long leg gross weight is exactly `+1.0`, equal-weighted within the long basket;
- short leg gross weight is exactly `-1.0`, equal-weighted within the short basket;
- total gross exposure is exactly `2.0` and net dollar exposure is exactly `0.0` at each rebalance;
- no beta hedge, BTC overlay, volatility target, leverage target variant, discretionary name exclusion, stop loss, take profit, or intraperiod rebalance is allowed.

The strategy is evaluated as a research sleeve only. It does not authorize live positions.

## Frozen weekly return and turnover accounting

Price PnL for week `t` is `sum_i w_i,t * simple_return_i(t,t+5)` using decision-time weights.

Weight turnover at decision `t` is `TURNOVER_t = sum_i |w_i,t - w_i,t-1|`; before the first valid portfolio, all prior weights are zero. Delisted or newly ineligible names mechanically receive target weight zero. No terminal liquidation charge is added solely because the historical sample ends.

Cost panels apply to this measured traded-notional turnover:

- `C0`: `0 bps * TURNOVER_t`;
- `C1`: `10 bps * TURNOVER_t`;
- `C2`: `20 bps * TURNOVER_t`.

These are per-unit traded-notional costs, applied once at each weekly rebalance. The panels cannot be changed after controlled exposure.

## Frozen funding accounting

Funding is mandatory and uses source-native Binance USD-M funding rates for each held contract. For every funding event with timestamp strictly after the Monday decision timestamp and at or before the `t+5` exit timestamp, normalized funding contribution is:

`FUNDING_i,event = -w_i,t * funding_rate_i,event`.

Weekly funding PnL is the sum across held assets and included funding events. This is a prospectively fixed entry-notional funding-return convention; no mark-price rescaling, compounding variant, forecasted funding, stale fill, alternate venue, or omission of available events is allowed.

If exact event timestamps and source-native rates cannot be truthfully bound for an otherwise valid held asset/week, that week lacks truthful implementation support and is not imputed.

Net weekly return is `PRICE_PNL + FUNDING_PNL - COST_PANEL`.

## Frozen BTC state and beta diagnostics

`BTC_UP` uses the same BUILD-frozen 0086 rule: BTCUSDT `MOM60_RAW > 0` at the decision session; otherwise the state is `BTC_NONUP`.

For each held asset, estimate trailing-60-completed-session beta to BTCUSDT at the decision session as `cov(asset_return, btc_return)/var(btc_return)` using finite daily simple returns only. Require 60 paired completed returns and nonzero BTC variance. Portfolio decision-time beta is `sum_i w_i,t * beta_i,t`.

Beta is a risk gate only. 0088 may not alter portfolio weights to improve beta after observing controlled values.

## Frozen capacity and concentration accounting

Reference research NAV is exactly `1,000,000 USDT`.

- per-name trade notional at rebalance is `abs(w_i,t-w_i,t-1) * reference_NAV`;
- capacity utilization is trade notional divided by trailing-30-completed-session median daily quote volume available at decision time;
- every traded name must have finite positive capacity denominator;
- maximum absolute target name weight must be `<=0.15`;
- every name-level capacity utilization must be `<=0.01`.

No capital-size optimization or result-dependent resizing is allowed.

## Frozen support minima

0088 is scientifically evaluable only if all apply:

- at least 104 valid weekly portfolio observations overall;
- at least 4 chronological blocks can each be formed with at least 20 valid observations;
- at least 3 calendar years each contain at least 20 valid weekly observations;
- `BTC_UP` and `BTC_NONUP` states each contain at least 30 valid weekly observations;
- every evaluated portfolio week contains at least 21 eligible instruments;
- truthful price-return, funding, turnover, beta, concentration, and capacity accounting exists for every evaluated week.

Weeks failing a frozen support requirement are excluded mechanically. BUILD must prevent selective exclusion based on portfolio return.

## Frozen inference

Primary return series is `C2` stressed-cost weekly net return.

- dependence-aware uncertainty: moving-block bootstrap over weekly C2 returns;
- block length: 8 weeks;
- replicates: 10,000;
- seed: `880088`;
- annualized Sharpe uses `sqrt(52) * mean(C2) / sample_std(C2)` with sample standard deviation `ddof=1`;
- max drawdown compounds weekly C2 returns from unit NAV with no annualization;
- positive-week fraction counts strictly positive C2 returns.

No alternate seed, block length, annualization, risk-free rate, outlier removal, or inference method may replace these rules.

## Frozen PASS gates

0088 PASS requires every gate below to pass in one valid controlled execution:

- `G0_EXECUTION`: all marker, identity, manifest/hash, schema/timestamp, point-in-time, read-count, persistence, finite-statistic, source-interface, network-denial, and exactly-once invariants pass;
- `G1_SUPPORT`: all frozen support minima pass;
- `G2_NET_RETURN`: mean weekly C2 return is `>0` and the moving-block-bootstrap 95% confidence interval lower bound for mean C2 return is `>0`;
- `G3_SHARPE`: annualized C2 Sharpe is `>=0.75`;
- `G4_DRAWDOWN`: maximum C2 drawdown is no worse than `-0.35`;
- `G5_HIT_RATE`: strictly positive C2 weekly return fraction is `>=0.52`;
- `G6_CHRONOLOGY`: at least 3/4 equal-count chronological blocks have positive mean C2 return and no block mean is `<=-0.0025` per week;
- `G7_CALENDAR`: at least three qualifying calendar years have positive mean C2 return;
- `G8_STATE_AND_LOYO`: both qualifying BTC states have positive mean C2 return and every eligible leave-one-calendar-year-out mean C2 return is positive;
- `G9_IMPLEMENTATION`: C0 mean >= C1 mean >= C2 mean; every target portfolio is dollar neutral with gross 2.0; max absolute target name weight `<=0.15`; every capacity utilization `<=0.01`; median absolute portfolio beta `<=0.20`; 90th-percentile absolute portfolio beta `<=0.50`.

No gate may be removed, weakened, or substituted based on controlled results.

## Frozen terminal classifications

- `PASS_VALIDATED_FACTOR_LS`: valid execution and every G0-G9 gate passes.
- `FAIL_FACTOR_LS_GATES`: valid execution with adequate frozen support but at least one mandatory scientific/economic/risk gate fails.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: valid execution but frozen support or truthful implementation accounting is insufficient to evaluate the exact portfolio.
- `INVALID_EXECUTION`: any marker-ordering, manifest/hash, source identity, schema/timestamp, point-in-time membership, funding-event, read-count, non-finite, persistence, network, source-interface, or exactly-once invariant fails.

`INVALID_EXECUTION` answers zero scientific questions. If the common runner causes a new INVALID_EXECUTION, all new controlled science pauses until runner repair and requalification. 0088 creates no replacement retry chain.

## Trial budget and stopping rule

- portfolio candidates: exactly 1;
- factor subsets: exactly 1, containing all three immutable 0086 passing factors;
- factor weights: exactly one equal-weight rule;
- factor signs: immutable from 0086;
- universes: exactly 1;
- holding horizons: exactly 1 (`FWD5`);
- rebalance schedules: exactly 1 (Monday UTC close);
- basket construction: exactly 1 (equal-weight top/bottom terciles);
- controlled attempts: maximum `1/1`, only after separate user authorization;
- RUN must use `ControlledResearchRunnerV1SourceQualified`;
- durable `RUN_ATTEMPT.marker` must precede every controlled payload read;
- scientific engine may execute at most once;
- create-only result persistence and `RUN_ONCE` sealing are mandatory;
- once RUN begins, no same-ID rerun, retune, rescue, source substitution, factor change, sign reinterpretation, coefficient fitting, portfolio-rule change, history extension, threshold change, seed change, or recomputation is allowed.

## BUILD and ARM boundaries

BUILD may use only synthetic/nonhistorical fixtures. It must freeze and test the exact 0086 factor formulas/sign injection, PIT universe, composite rank/tie rules, basket construction, turnover, funding, cost panels, BTC state, beta, capacity, concentration, support accounting, inference, G0-G9 gates, terminal classifier, and source-qualified runner adapter. BUILD must not open controlled historical values.

ARM may inspect only permitted identities/metadata and must bind exact price and funding controlled object identities, declared hashes/sizes, expected source keys, schema contract, source-qualified runner interface, expected controlled read budget, result path, marker path, and engine-call budget. Pre-marker `testzip()`, decompression, CRC traversal, payload parsing, or controlled value reads are forbidden. After ARM, source substitution is forbidden.

## Evidence tier and downstream gate

All controlled history used by 0088 remains researcher-exposed `DEVELOPMENT` evidence, not independent OOS. A valid PASS may unlock only a separately governed multi-sleeve research ID. It grants no production authority.

## What did not change

- `workflow run                         31381953131 / attempt 1` remains immutable.
- CAPTURE-0001 remains sealed/no-retry.
- CAPTURE-0002 remains permanently claimed/no-refetch.
- 0070/0071/0083/0072/0073/0074/0075/0076/0084/0085 terminal states remain immutable.
- 0076 remains sealed at the Stage7 pre-marker read-boundary incident; 0088 is not its replacement or continuation.
- 0085 remains immutable `INVALID_EXECUTION` with attempt 1/1 consumed and no admissible Trend scientific result.
- 0086 remains immutable `PASS_VALIDATED_FACTOR_ATLAS`; its factors/signs cannot be reinterpreted.
- Phase6 PASS closeout remains unchanged.
- R2 common-runner qualification and R3 prospective five-gate lifecycle remain unchanged.
- 0087 remains blocked before controlled science by its qualifying Deribit source-metadata requirement.
- No production, signing, order, withdrawal, or transfer authority is granted.
