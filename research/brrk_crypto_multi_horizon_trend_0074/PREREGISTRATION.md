# BRRK-CRYPTO-MULTI-HORIZON-TREND-0074 — PREREGISTRATION

Status: STAGE 3 / PROSPECTIVE PREREGISTRATION

This contract freezes the complete numerical/data/analysis semantics before any 0074 controlled scientific/history content read. Stage-3 controlled reads remain 0 and controlled attempt remains 0/1.

## Immutable lineage

- Roadmap: `research/governance/CRYPTO_MULTI_STRATEGY_RESEARCH_PROGRAM_0071_0082.md`.
- OWNER-FIRST merge: `2af445a26e2a1d08b38a1cc9f6c853b29c828cde`.
- DESIGN merge: `08eafc22c3772bd021bc7e3c201c5dc63ac81e64`.
- Universe: exactly BTC, ETH and SOL.
- Selectable candidate count: exactly 3.
- Evidence tier: DEVELOPMENT history, never independent OOS.

No observed 0074 result may alter anything below.

## Frozen historical source set and window

Official source host: `https://data.binance.vision` only.

Instruments: Binance USD-M perpetual contracts `BTCUSDT`, `ETHUSDT`, `SOLUSDT`.

Decision window: UTC daily observations from `2021-01-01T00:00:00Z` through `2026-07-31T23:59:59.999999Z` inclusive.

Required archive families, for every asset and every calendar month from `2021-01` through `2026-07` inclusive:

1. USD-M perpetual monthly 1d klines:
   `data/futures/um/monthly/klines/{SYMBOL}/1d/{SYMBOL}-1d-{YYYY}-{MM}.zip`
2. USD-M monthly funding-rate history:
   `data/futures/um/monthly/fundingRate/{SYMBOL}/{SYMBOL}-fundingRate-{YYYY}-{MM}.zip`

Every authorized object must later be prospectively enumerated with its exact object path, paired official `.CHECKSUM`, SHA-256 identity and one-read budget before Stage-6 merge. Stage 7 may PASS only if every required Stage-8 payload is already durably staged, hash-bound and offline-readable with Stage-8 scientific source-network fetch budget 0.

No API substitute, alternate venue, alternate symbol, spot series, mark/index series, later history extension or source-family replacement is permitted under this ID.

## Frozen chronology

- Daily bars use exchange UTC timestamps.
- Signal for day `t` may use only values timestamped at or before the close of day `t`.
- Exposure decided at close `t` first applies to the `t -> t+1` return interval.
- Same-bar return may never size or determine exposure for that same interval.
- Funding is applied only at its archived exchange timestamp and with the position that was already executable immediately before that funding event.
- Missing or malformed required values cause that asset-day to be ineligible; no forward filling of returns, prices or funding is allowed.

## Common portfolio construction

Each candidate produces an asset signal in `{-1, 0, +1}`. Signals are combined across the frozen FAST/MEDIUM/SLOW family by equal-weight vote: `sign(v_fast + v_medium + v_slow)`; exact zero sum means flat.

Lagged realized volatility is the sample standard deviation of the previous 20 executable daily log returns, annualized by `sqrt(365)`. Volatility target is exactly 20% annualized.

Per-asset risk scale is `min(1.0, 0.20 / max(lagged_20d_ann_vol, 0.05))`.

Portfolio target weight is `signal * risk_scale / 3` for each eligible asset. Absolute per-asset weight cap is `1/3`; portfolio gross exposure cap is `1.0`; net exposure therefore lies in `[-1, +1]`. No leverage above gross 1.0 is permitted.

Rebalance cadence: every UTC daily close. Turnover is `sum(abs(w_t - w_{t-1}))` using executable target weights.

## Candidate 1 — PAST_RETURN_SIGN_TREND

Frozen horizon lookbacks:

- FAST = 20 calendar-trading observations;
- MEDIUM = 60 observations;
- SLOW = 180 observations.

For horizon `L`, vote at close `t` is `sign(log(close_t / close_{t-L}))`. Zero return gives vote 0. The three votes combine by the common equal-vote rule.

## Candidate 2 — MOVING_AVERAGE_SPREAD_TREND

Simple arithmetic moving averages only; no EMA or adaptive smoothing.

Frozen FAST/MEDIUM/SLOW pairs:

- FAST = SMA(10) versus SMA(40);
- MEDIUM = SMA(20) versus SMA(80);
- SLOW = SMA(60) versus SMA(240).

Vote is +1 when short SMA > long SMA, -1 when short SMA < long SMA, otherwise 0. The three votes combine by the common equal-vote rule.

## Candidate 3 — BREAKOUT_TREND_NORMALIZED_BY_LAGGED_VOL_OR_ATR

Frozen channel lookbacks:

- FAST = 20 observations;
- MEDIUM = 60 observations;
- SLOW = 180 observations.

For each horizon `L`, compare `close_t` only with the prior `L` completed closes excluding `t`: vote +1 if `close_t` exceeds the prior-L maximum, vote -1 if below the prior-L minimum, otherwise 0. The three votes combine by the common equal-vote rule. The common 20-day lagged realized-volatility scaler is the only normalization used; ATR is not used in 0074.

## Funding and return accounting

Underlying price return for an executable interval is the log return of the frozen USD-M perpetual 1d close series.

Funding cash flow uses the archived funding-rate event value. Positive funding means long pays short. Portfolio funding contribution is therefore `- position_notional * funding_rate` for a long position and the same signed formula naturally credits a short position.

Funding events are accumulated in their actual chronological order inside each daily interval before daily portfolio NAV is finalized.

## Cost regimes

Costs apply to absolute turnover before the interval NAV update.

- `C0_THEORETICAL`: 0 bps per unit one-way turnover.
- `C1_REALISTIC`: 10 bps per unit one-way turnover, representing fee + spread/slippage combined.
- `C2_STRESSED`: 30 bps per unit one-way turnover.

No post-result fee reduction, maker rebate assumption, spread omission or funding omission is allowed.

## Support minima

A candidate is decision-eligible only if:

- portfolio common-support window contains at least 1,095 executable daily observations;
- each of BTC, ETH and SOL contributes at least 900 eligible daily observations;
- at least 80% of calendar days after the 240-day warm-up retain at least two eligible assets;
- at least 30 non-flat portfolio exposure days exist in each of the three calendar regimes defined below.

Failure of these support minima yields `INCONCLUSIVE_INSUFFICIENT_SUPPORT`, not economic FAIL.

## Frozen regime diagnostics

Regimes are descriptive robustness partitions, not selectable variants:

- BULL: BTC trailing 90-day return > +10%;
- BEAR: BTC trailing 90-day return < -10%;
- SIDEWAYS: otherwise.

High-volatility diagnostic: BTC lagged 20-day annualized realized volatility >= 80%; low-volatility otherwise.

Whipsaw diagnostic: candidate portfolio signal changes sign or crosses through flat at least 4 times in any rolling 20-day window.

Trend-crash diagnostic: candidate portfolio prior-day net exposure sign is opposite the next 5-day BTC cumulative return sign and absolute BTC 5-day return is >= 15%.

Gap/high-volatility stress days: absolute BTC daily return >= 8% or BTC lagged 20-day annualized volatility >= 100%.

## Primary economic and robustness gates

A selectable candidate PASSes only if all gates below PASS under valid exactly-once execution:

G0 Identity/chronology/execution validity PASS.

G1 Support minima PASS.

G2 `C1_REALISTIC` annualized arithmetic return > 0 and terminal wealth > 1.0.

G3 `C1_REALISTIC` annualized Sharpe >= 0.50.

G4 `C1_REALISTIC` maximum drawdown >= -50%.

G5 `C2_STRESSED` annualized arithmetic return > 0 and terminal wealth > 1.0.

G6 Moving-block-bootstrap lower 95% confidence bound for mean daily `C1` log return > 0.

G7 Deflated Sharpe Ratio probability >= 0.95 using exactly 3 selectable trials.

G8 Leave-one-asset-out `C1` annualized return is positive in at least 2 of 3 exclusions and none is below -10% annualized.

G9 BULL, BEAR and SIDEWAYS partitions each have nonnegative `C1` mean daily return; at least 2 of 3 are strictly positive.

G10 No single asset contributes more than 70% of absolute gross portfolio PnL and no single calendar year contributes more than 70% of positive gross PnL.

G11 Median monthly turnover <= 2.0 times gross NAV and 95th-percentile monthly turnover <= 6.0 times gross NAV.

Raw Sharpe alone can never establish PASS.

## Inference

Moving-block bootstrap:

- block length = 20 daily observations;
- replicates = 4,000;
- random seed = 740074;
- bootstrap statistic = mean daily `C1` log return;
- percentile two-sided interval, with PASS gate using the lower 2.5% endpoint > 0.

Deflated Sharpe Ratio:

- selectable trial count = exactly 3;
- annualization = 365;
- observed skewness and kurtosis from each candidate `C1` daily return series;
- PASS threshold probability = 0.95.

CSCV/PBO:

- exactly 8 chronological slices and all 70 half-split combinations when common support after warm-up is at least 1,008 observations;
- diagnostic only; if mathematically undefined it is recorded as `NOT_EVALUATED` and cannot rescue another failed gate.

## Horizon-neighborhood robustness

These are nonselectable stress diagnostics and may not become replacement candidates.

For return-sign and breakout candidates, rerender the frozen logic only at proportional horizon sets `(15,45,135)` and `(25,75,225)`. For moving-average spread, rerender pairs `(8,30)/(15,60)/(45,180)` and `(12,50)/(25,100)/(75,300)`.

A candidate satisfies neighborhood robustness only if its `C1` annualized return is positive in both stress renditions. These diagnostics do not alter the DSR selectable-trial count of 3 and cannot replace the primary candidate settings.

## Terminal classification

- `PASS`: valid execution and at least one of the exactly three primary candidates passes G0-G11 plus both neighborhood stress renditions.
- `FAIL`: valid execution with sufficient support but no primary candidate passes all frozen gates.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: any prospectively defined support condition prevents a scientifically complete decision.
- `INVALID_EXECUTION`: any source identity, checksum, chronology, lookahead, controlled-read count, candidate-count, cost/funding accounting, persistence or exactly-once violation.

Representative candidate, if more than one PASSes, is chosen without final-performance optimization in fixed priority order: `PAST_RETURN_SIGN_TREND`, then `MOVING_AVERAGE_SPREAD_TREND`, then `BREAKOUT_TREND_NORMALIZED_BY_LAGGED_VOL_OR_ATR`.

## Exactly-once execution budget

Before Stage 8:

- Stage 4 implementation uses synthetic fixtures only;
- Stage 5 qualification uses synthetic fixtures only;
- Stage 6 must enumerate exact authorized object identities and prove payload staging contract;
- Stage 7 must PASS zero-result identity/durability/offline-readability preflight with no scientific payload values opened.

Stage 8 requires contemporaneous explicit user authorization, then durable remote `RUN_ATTEMPT.marker` before the first controlled content read.

Frozen Stage-8 budgets:

- controlled attempt: exactly 1/1;
- each authorized historical payload object: at most one scientific content read;
- scientific engine: exactly 1 call;
- scientific source-network fetches: exactly 0;
- result persistence: create-only `RUN_ATTEMPT.marker` -> `PRIMARY_RESULT.json` -> `EVIDENCE.json` -> `EXECUTION.json` -> `RUN_ONCE.marker`.

After durable marker creation: no rerun, retune, rescue, source substitution, history extension, horizon alteration, candidate replacement, threshold relaxation or recomputation.

## Stage-3 accounting

- controlled scientific/history reads: 0;
- scientific engine calls: 0;
- scientific source-network fetches: 0;
- controlled attempt: 0/1;
- production_authorized=false;
- signature_authorized=false;
- order_submission_authorized=false.
