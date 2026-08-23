# 0084 Stage 3 PREREGISTRATION — Cross-Sectional Factor Atlas Replacement

Research ID: `BRRK-CRYPTO-CROSS-SECTIONAL-FACTOR-ATLAS-REPLACEMENT-0084`

Lifecycle stage: `3/10 PREREGISTRATION`.

Parent Stage2 merge: `075d8b5b7de97836350314d517ad483d5de67219`.

Controlled attempt: `0/1`; controlled historical/evidence reads: `0`; scientific engine calls: `0`; scientific source-network fetches: `0`.

This document freezes the numerical/data/analysis semantics before implementation and before any controlled 0084 scientific/history read. It mechanically reproduces the frozen 0075 scientific contract under the prospectively authorized replacement ID. No 0075 lifecycle credit, result, attempt consumption, controlled read, or Stage8 authorization transfers to 0084. Researcher-exposed history remains DEVELOPMENT history and must never be described as independent OOS.

## 1. Source families and point-in-time identities

The only admissible market-data families are official Binance public archive objects under `data.binance.vision`, with exact per-object paths, paired `.CHECKSUM` identities and payload SHA256 values to be enumerated and durably staged in Stage6 before Stage7 may PASS:

- SPOT monthly daily klines for eligible `*USDT` symbols;
- USD-M monthly daily perpetual klines for matching perpetual symbols where derivatives features are defined;
- USD-M monthly `fundingRate` archives for matching perpetual symbols.

No Stage8 source-network fetch is permitted. Stage6 must freeze the exact object manifest and hashes; Stage7 may inspect identities and staging metadata only, never payload values. Any missing required source object makes the affected factor observation missing; source substitution is forbidden.

Network/economic-state factors are not instantiated because no separately qualified point-in-time network/economic source family is frozen here. They consume zero trials and may not be added later under the same ID.

## 2. Time range and chronology

Candidate source months are `2021-01` through `2026-07`, inclusive, subject to Stage6 exact-object availability. All timestamps normalize to UTC calendar day. A rebalance decision for day `t` uses only observations whose source timestamp is no later than the close of `t-1`; positions/forward returns begin at close `t`. No same-day close information may affect the return beginning at that same close.

Forward-return horizons are exactly `5` and `20` calendar-observation sessions. A label matures only when the full horizon exists. Unmatured tail rows are excluded, never imputed.

Rebalance cadence is daily on every date with a valid point-in-time universe.

## 3. Point-in-time tradable universe

At each rebalance date, a symbol is eligible only if all rules hold using information available by `t-1`:

1. quote asset is USDT and instrument is ordinary spot crypto, excluding stablecoins, fiat proxies, leveraged tokens, wrapped duplicates where obvious from symbol identity, and migration/redenomination duplicates;
2. listing age is at least `180` calendar days from the first admissible archived daily bar;
3. at least `60` of the previous `60` expected daily closes are present and positive;
4. trailing `30`-day median daily quote-volume proxy is at least `USD 1,000,000`;
5. trailing `30`-day median daily notional volume is finite and positive;
6. current close is not stale: the latest admissible close must be from `t-1`;
7. at least `20` eligible symbols exist cross-sectionally on `t`; otherwise that date produces no atlas observation.

Delisted/dead symbols remain historically eligible until their last valid archived observation if they met the rules then. Future survival may not determine earlier membership.

## 4. Cross-sectional preprocessing

For each factor/date:

- require at least `20` non-missing eligible symbols;
- winsorize raw factor values cross-sectionally at the `2.5th` and `97.5th` percentiles using only that date;
- convert to fractional rank in `[0,1]`, average-ranking ties;
- define quintiles using rank cutoffs `[0,.2), [.2,.4), [.4,.6), [.6,.8), [.8,1]`;
- require at least `4` symbols in both Q1 and Q5; otherwise spread/monotonicity for that date is undefined;
- no forward fill is permitted for factor values.

Residualization is used only by the two explicitly named residual factor definitions below. It is cross-sectional OLS on each date against contemporaneously available controls and requires at least `30` complete symbols. No other factor may be residualized.

## 5. Frozen 16 base factor definitions

Each base factor is evaluated at exactly two forward horizons (`5`,`20`) and exactly two representations (`RAW_RANK`,`RESIDUAL_WHERE_ALLOWED_OR_DUPLICATE_SIGNED_RANK`), giving exactly `16 × 2 × 2 = 64` declared trials. For non-residual factors the second representation is the sign-inverted economic counterpart where the mechanism is directionally ambiguous; both were declared prospectively and both count as separate trials. No candidate may be removed after history exposure.

### Price family

P1 `MOM_20`: log return from close `t-21` to `t-1`.

P2 `MOM_60`: log return from close `t-61` to `t-1`.

P3 `REV_5`: negative log return from close `t-6` to `t-1`.

P4 `DRAWDOWN_60`: `close(t-1)/max(close[t-60:t-1]) - 1`.

P5 `RECOVERY_20_FROM_DD`: 20-session log return multiplied by indicator that prior 60-session drawdown is `<= -20%`.

P6 `RESID_MOM_60`: residual from date-wise cross-sectional OLS of `MOM_60` on `BETA_60`, `RVOL_20`, and log trailing-30d median notional-volume proxy.

### Risk family

R1 `RVOL_20`: sample standard deviation of daily log returns over the previous 20 observations times `sqrt(365)`.

R2 `RVOL_60`: same over 60 observations.

R3 `BETA_60`: OLS beta of asset daily log return on equal-weight eligible-universe daily log return over previous 60 observations, requiring at least 45 paired rows.

R4 `DOWNSIDE_BETA_60`: same beta using only benchmark-negative days, requiring at least 15 negative benchmark days.

R5 `IDIOVOL_60`: annualized sample standard deviation of residuals from the `BETA_60` regression.

### Market-structure family

M1 `VOLUME_SURPRISE_20`: `log(volume_quote(t-1) / median(volume_quote[t-20:t-2]))`, requiring positive values.

M2 `LIQUIDITY_AMIHUD_20`: median over prior 20 observations of `abs(return_d)/quote_volume_d`; lower is more liquid.

M3 `FUNDING_7D`: sum of all admissible archived perpetual funding observations whose timestamps fall in the seven calendar days ending at `t-1`; requires a matching USD-M perpetual symbol and complete available archive coverage for that interval.

M4 `PERP_BASIS_1D`: `perp_close(t-1)/spot_close(t-1)-1` for matching spot/perpetual symbols.

M5 `PERP_MOMENTUM_GAP_20`: 20-session perpetual log return minus 20-session spot log return.

No open-interest factor is instantiated because no exact official archive family is frozen in this preregistration.

## 6. Representation rule and direction

Every base definition yields two declared representations:

- `A`: ascending fractional rank of the raw definition as written;
- `B`: for P6 only, ascending rank of the residual value; for every other factor, `1-A`.

This intentionally counts both prospective directional hypotheses rather than selecting sign from realized history. Total evaluated variants must equal `64` if execution is valid. Missing/undefined rows do not remove a trial.

## 7. Forward-return and factor statistics

For each trial/horizon:

- forward return is `close(t+h)/close(t)-1`;
- daily Q5-Q1 spread is equal-weight mean forward return in Q5 minus Q1;
- monotonicity score is Spearman correlation between quintile index `1..5` and mean quintile forward return on each valid date;
- daily rank IC is Spearman correlation between factor rank and matured forward return across eligible symbols.

Primary inference uses the time series of daily rank IC and Q5-Q1 spread. Overlapping forward horizons are retained and handled with moving-block bootstrap, not treated as IID.

## 8. Regimes and robustness partitions

Prospectively fixed partitions:

- calendar year;
- market trend: 60-session equal-weight universe return `>=0` bull, `<0` bear;
- volatility: equal-weight universe 20-session realized volatility above/below its expanding historical median available by `t-1`;
- liquidity: cross-sectional median trailing-30d notional volume above/below its expanding historical median available by `t-1`;
- size proxy buckets use trailing-30d median notional volume tertiles because no point-in-time market-cap source is frozen;
- theme leave-out is `NOT_EVALUATED` because no point-in-time theme taxonomy is frozen.

Leave-year-out requires at least 3 supported calendar years. Leave-size-bucket-out requires all three size-proxy buckets to be supported.

## 9. Multiplicity and inference

All 64 declared trials belong to three instantiated families: PRICE, RISK, MARKET_STRUCTURE, with P1-P6=24 trials, R1-R5=20 trials, M1-M5=20 trials; NETWORK has zero instantiated trials.

For each family and each primary metric, raw two-sided bootstrap p-values are corrected by Holm at family-wise alpha `0.05`. A factor definition qualifies only if at least one of its two horizons passes multiplicity on both rank-IC and Q5-Q1 evidence with matching economic direction.

Moving-block bootstrap: block length `20` rebalance dates, `4,000` replicates, deterministic seed `750075`. The resampling unit is date, preserving the full cross-section per date.

No DSR or CSCV/PBO is used because 0084 is an atlas of factor associations rather than a selected strategy NAV. Those diagnostics are reserved for strategy-producing 0076.

## 10. Frozen PASS gates

A trial can qualify only if all are true:

G0 execution valid and exactly 64 declared trials persisted;
G1 at least `252` valid rebalance dates and at least `30` eligible symbols on the median valid date;
G2 family-wise Holm-adjusted `p <= 0.05` for mean rank IC;
G3 family-wise Holm-adjusted `p <= 0.05` for mean Q5-Q1 spread;
G4 full-sample mean rank IC and mean Q5-Q1 have consistent declared direction;
G5 at least `60%` of supported calendar years have rank IC with the same sign as full sample;
G6 both bull and bear partitions, where each has at least 63 valid dates, retain the full-sample IC sign;
G7 both high/low-vol partitions, where each has at least 63 valid dates, retain the full-sample IC sign;
G8 both high/low-liquidity partitions, where each has at least 63 valid dates, retain the full-sample IC sign;
G9 leave-year-out IC retains sign in every supported omission and median absolute IC retention is at least `0.50` of full-sample absolute IC;
G10 leave-size-bucket-out IC retains sign in all three omissions;
G11 Q1/Q5 median constituent count is at least `4`, and median one-way constituent replacement fraction between consecutive rebalances is no greater than `0.75`.

0084 `PASS` requires valid execution and at least one trial satisfying G0-G11. `FAIL_NO_QUALIFIED_FACTOR` means valid execution and zero qualifying trials. `INCONCLUSIVE_INSUFFICIENT_SUPPORT` applies only if G1 support is impossible for every trial or required inference is mathematically undefined despite valid identities/accounting. `INVALID_EXECUTION` applies to identity/hash/read-count/lookahead/maturity/universe/candidate-count/source/persistence/exactly-once drift.

PASS only qualifies immutable factor definitions as possible 0076 inputs. It does not imply deployable long/short alpha. Only immutable 0084 PASS closeout may unlock 0076 under governance resolution #381.

## 11. Stage4 synthetic qualification obligations

Stage4 must implement the complete end-to-end scientific execution interface before Stage5 qualification, including deterministic staged-payload parsing and read accounting, every frozen factor calculation, exact 64-trial orchestration, primary statistics, bootstrap and Holm inference, every frozen robustness partition, G0-G11 evaluation, exact counters, and create-only result persistence.

Implementation must support synthetic fixtures for: known positive/negative monotonic factor; null factor; ties; insufficient universe; stale/missing rows; delisting survival; maturity exclusion; winsor/rank determinism; residualization; missing perpetual/funding; Holm family accounting; leave-year/size robustness; turnover/replacement accounting; every terminal classification; identity mismatch -> INVALID_EXECUTION.

Synthetic qualification may read zero controlled historical payloads.

## 12. Exactly-once execution budget

Stage8 budget is exactly one controlled attempt. Before any controlled content read, Stage7 must have PASSed on exact merged boundary and contemporaneous user authorization specific to 0084 must be recorded. Stage8 must:

1. rerun identity-only zero-result preflight;
2. create and remotely verify durable `RUN_ATTEMPT.marker` before first payload content read;
3. read each authorized staged payload object at most once;
4. invoke the scientific engine exactly once;
5. perform scientific source-network fetches exactly zero times;
6. persist result bundle create-only;
7. finalize marker-only with zero scientific reread;
8. create `RUN_ONCE.marker`.

After marker durability, attempt `1/1` is consumed regardless of PASS/FAIL/INCONCLUSIVE/INVALID. Same-ID rerun, retune, rescue, source substitution, candidate replacement, history extension and recomputation are forbidden.

## 13. Immutable anchors and authority

0070 remains immutable PASS closeout. 0071 remains permanently blocked at 6/10. 0083 remains immutable FAIL closeout 10/10 with attempt 1/1 consumed. 0072 remains immutable `INCONCLUSIVE_INSUFFICIENT_SUPPORT` 10/10 with attempt 1/1 consumed, controlled reads 6, scientific engine 1/1, source-network fetches 0, and no same-ID rerun/retune/rescue/recompute. 0075 remains permanently `7/10 BLOCKED_PRE_ATTEMPT_FROZEN_IMPLEMENTATION_INCOMPLETE`, attempt `0/1`, reads `0`, engine `0/1`, network `0`, values exposed false, no marker/result, and no same-ID continuation.

CAPTURE-0001 remains sealed failed HTTP 451 with no retry. CAPTURE-0002 remains permanently claimed with no refetch. The exact historical CURRENT_STATE line `workflow run                         31381953131 / attempt 1` remains immutable.

`production_authorized=false`

`signature_authorized=false`

`order_submission_authorized=false`
