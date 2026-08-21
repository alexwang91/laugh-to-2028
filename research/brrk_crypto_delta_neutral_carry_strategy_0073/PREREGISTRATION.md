# BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073 — Stage 3 PREREGISTRATION

Status: `PROSPECTIVE FROZEN / ZERO CONTROLLED HISTORY READS / ATTEMPT 0/1`

Date: 2026-08-22

## Lifecycle anchors

- Program roadmap merge: `169d9adf6531dc099a43541df413fef079322adf`.
- 0072 immutable closeout: `e7571fd592c1a8074d487f27f8dbe9af6e33927f` = `INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED TO SAME-ID RERUN`.
- Prospective 0073 launch-gate amendment: `5b8153476aa63eb0c30d870a73e3bf14b4239ac8`.
- 0073 OWNER-FIRST merge: `dc287210212a827181501779482c976ac01995c8`.
- 0073 Stage-2 DESIGN merge: `8cfe10ed7c031c6e46edb1d58e30bc5eb8cc7878`.
- Controlled scientific/history reads: `0`.
- Controlled attempt: `0/1`.
- Scientific engine calls: `0`.
- Production/signature/order authority: `false/false/false`.

This preregistration is prospective and uses no 0073 controlled historical result and no 0072 observed effect, support count, p-value or classification to choose parameters.

## Fixed universe and declared candidates

Assets are exactly `BTC`, `ETH`, `SOL`. Candidate accounting is exactly three declared structures and all three remain in multiplicity accounting even when unavailable:

1. `C1_LONG_SPOT_SHORT_PERPETUAL`.
2. `C2_LONG_SPOT_SHORT_DATED_FUTURE`.
3. `C3_CROSS_VENUE_SAME_UNDERLYING_HEDGE`.

Each candidate is same-underlying only. Cross-asset hedge substitution is forbidden. A candidate that cannot satisfy the frozen point-in-time identity/support contract is persisted as `UNAVAILABLE_INSUFFICIENT_SUPPORT`, never replaced.

## Point-in-time source boundary

Stage 3 freezes source acquisition before any controlled-history read:

- primary archive host: official Binance public archive `data.binance.vision` only where exact spot / USD-M perpetual / eligible dated-futures archive objects can be prospectively enumerated;
- cross-venue candidate requires a separately prospectively qualified second official venue before any history read; absent that qualification, C3 is `UNAVAILABLE_INSUFFICIENT_SUPPORT`;
- present-day instrument metadata may not be projected backward;
- exact archive object path, checksum and SHA256 must be persisted before the object becomes an authorized scientific input;
- automatic retry, result-informed refetch, source substitution and family substitution are forbidden;
- `premiumIndexKlines` is not funding and may not be relabeled as funding;
- funding requires an official historical funding object with event timestamps; if such an object is not prospectively qualified, C1 cannot claim funding carry and must fail closed as unavailable for the intended economic test.

No source object content may be opened merely to decide whether its realized result looks favorable.

## Study window and temporal convention

The controlled study window is fixed to the latest continuous 730 UTC calendar days ending at the prospectively frozen capture cutoff, subject to each candidate having at least 365 eligible daily portfolio observations after all point-in-time joins and warmups. The cutoff itself must be committed before capture.

Decision frequency is daily at `00:00 UTC`. Information timestamped at or before decision time `t` may first affect the portfolio established after `t`. No cash flow may be shifted to an earlier state. Perpetual funding is booked only at its official event timestamp. Dated-future settlement and roll use contracts already eligible at the roll decision timestamp.

## Candidate construction

### C1 LONG_SPOT_SHORT_PERPETUAL

For each eligible asset, long spot notional = `+0.50 NAV` and short perpetual delta notional = `-0.50 NAV`, before margin reserve. Asset sleeves are equal-weighted across currently eligible BTC/ETH/SOL. If fewer than two assets are eligible on a day, the candidate holds cash for that day.

### C2 LONG_SPOT_SHORT_DATED_FUTURE

Same gross sleeve construction as C1. The short leg is the nearest eligible dated future with between 21 and 120 calendar days to maturity. Roll occurs when time-to-maturity first becomes `<= 14` days, into the nearest already-listed contract satisfying 21–120 days. If no contract qualifies, that asset sleeve is cash.

### C3 CROSS_VENUE SAME-UNDERLYING HEDGE

Same gross sleeve construction as C1, but the long and short legs must reside on two prospectively frozen official venues. A second venue must be qualified and exact historical identities frozen before controlled history. Otherwise the complete candidate remains persisted as unavailable.

## Hedge neutrality and leverage gates

Target net delta is `0.000 NAV`. Absolute residual same-underlying delta after each rebalance must be `<= 0.02 NAV`; any observation above this tolerance is a neutrality breach. A candidate FAILs the neutrality gate if more than 1% of otherwise eligible observations breach it.

Gross economic exposure is capped at `1.00 NAV`; no leverage above 1.00 gross is permitted. At least `20% NAV` must remain unencumbered margin/liquidation reserve. If venue margin mechanics imply less than a 20% reserve under the frozen mark-to-market rule, the affected sleeve is reduced pro rata until the reserve is restored; if impossible, it is cash.

## Rebalance and weighting

Rebalance daily only when post-price-move residual delta exceeds `0.01 NAV` for an asset sleeve, when a dated-future roll rule fires, or when eligibility changes. Otherwise positions are held. Asset sleeves use equal target risk capital, not historical-return ranking. No volatility-ranked asset selection is permitted.

## Economic accounting order

For every candidate/day, accounting order is fixed:

1. carry forward prior holdings and collateral;
2. apply spot/futures/perpetual mark-to-market using legally available prices;
3. book funding/settlement/borrow/collateral cash flows at their event timestamps;
4. determine eligibility and target hedge from information available at the decision boundary;
5. compute trades required by rebalance/roll/eligibility rules;
6. apply fees, spread and slippage to both legs;
7. apply transfer/custody cost where relevant;
8. reserve margin and enforce liquidation buffer;
9. compute net NAV, returns, gross/net exposure and residual delta;
10. persist all cost components separately before aggregate metrics.

## Frozen cost regimes

All costs are one-way per traded notional unless stated otherwise.

`C1_REALISTIC`:
- spot fee: 6 bps;
- derivative fee: 5 bps;
- spot half-spread + slippage: 4 bps;
- derivative half-spread + slippage: 3 bps;
- dated-future roll extra friction: 4 bps per rolled derivative notional;
- cross-venue transfer/custody friction: 5 bps monthly equivalent applied pro rata daily when C3 is active;
- borrow cost for short spot is out of scope because all declared candidates are long spot / short derivative;
- collateral opportunity cost: 0 unless an official prospectively frozen collateral yield series is qualified; no favorable yield may be imputed.

`C2_STRESSED` multiplies all fee/spread/slippage/roll/transfer friction above by `2.0`. Funding and basis cash flows are not multiplied; they use realized official event cash flows and receive separate adverse stresses below.

## Stress suite

Each candidate is re-evaluated under deterministic stresses without re-optimization:

1. `FUNDING_FLIP`: each favorable funding receipt is reduced by 50%; each adverse funding payment is increased by 50%.
2. `BASIS_COMPRESSION`: positive convergence contribution reduced by 50%; negative convergence unchanged.
3. `VOL_SPIKE`: trading frictions multiplied by 3.0 on the worst realized 5% volatility days as defined prospectively by trailing 20-day same-asset close-to-close volatility.
4. `SPREAD_BLOWOUT`: all spread/slippage components multiplied by 4.0 for a contiguous 7-day block centered on each candidate's worst C1 drawdown day; this is a deterministic stress diagnostic, not a new selection trial.
5. `VENUE_OUTAGE`: remove the largest contributing venue for 7 consecutive days around its highest absolute gross exposure date; positions are frozen except risk-reducing trades, and no favorable transfer is assumed.
6. `COLLATERAL_HAIRCUT`: collateral value haircut 10% for 7 days around the worst drawdown date.
7. `STABLECOIN_DEPEG`: where stablecoin collateral is used, apply a 5% instantaneous collateral haircut and no immediate recovery credit for 7 days.
8. `MARGIN_STRESS`: required reserve increases from 20% to 35% NAV; exposure is reduced mechanically, never increased.

## Performance outputs

For every complete candidate and cost regime compute, where defined: annualized return, CAGR, annualized volatility, Sharpe, Sortino, maximum drawdown, Calmar, terminal wealth, turnover, gross carry, funding, basis convergence, roll contribution/cost, fees, spread/slippage, transfer/custody cost, total cost drag, cost break-even, gross exposure, net exposure, residual delta, reserve utilization, asset concentration, venue concentration and stress outcomes.

Risk-free rate is fixed to zero for Sharpe/Sortino to avoid introducing an additional unfrozen macro series.

## Concentration and capacity gates

A candidate cannot PASS if any asset contributes more than 70% of absolute cumulative pre-cost PnL or any venue contributes more than 80%. Remove-largest-asset and remove-largest-venue annualized-return estimates must remain positive where mathematically supported.

Capacity is diagnostic unless point-in-time depth/open-interest data are prospectively qualified. If such data are absent, classification cannot be rescued by an assumed capacity number. Any candidate claiming PASS must at minimum keep median daily traded notional below 1% of the exact point-in-time daily quote-volume proxy when that proxy is qualified; otherwise it is `INCONCLUSIVE_INSUFFICIENT_CAPACITY_SUPPORT`.

## Inference and multiplicity

Declared trial count is exactly `3`, including unavailable candidates.

For each supported candidate use synchronized moving-block bootstrap on daily net returns with block length `20`, `4000` replicates and PCG64 seed `730073`. Primary robust statistic is the bootstrap 5th percentile of annualized C1 net return. Candidate statistical PASS requires that lower bound `> 0`.

DSR trial count is fixed at 3 and DSR must be `>= 0.95` where defined. PBO uses CSCV with 8 contiguous slices and all admissible symmetric train/test combinations only when at least 504 eligible daily observations exist; otherwise PBO = `NOT_EVALUATED_INSUFFICIENT_SUPPORT` and cannot by itself create FAIL if every other prerequisite is satisfied.

No candidate may be deleted from trial accounting after poor performance.

## Candidate PASS gates

A candidate passes only if all are true:

- execution identity and accounting valid;
- at least 365 eligible daily observations;
- C1 CAGR > 0;
- C2 CAGR > 0;
- C1 Sharpe > 0.50;
- C2 Sharpe > 0.25;
- C1 maximum drawdown > -0.35;
- bootstrap 5th-percentile annualized C1 return > 0;
- DSR >= 0.95 where defined;
- cost break-even >= 20 bps one-way equivalent;
- neutrality breach rate <= 1%;
- gross exposure and margin-reserve rules pass;
- every mandatory stress has terminal wealth > initial wealth;
- asset and venue concentration gates pass;
- capacity gate passes where capacity input is qualified.

Representative candidate is the passing candidate with highest C2 CAGR; ties within 10 bps annualized are broken by lower C2 maximum drawdown, then fixed order `C1`, `C2`, `C3`.

## Terminal classification

- `PASS`: valid exactly-once execution and at least one declared candidate passes every frozen gate.
- `FAIL`: execution valid, support sufficient for every decision-critical gate, and no candidate passes.
- `INCONCLUSIVE_INSUFFICIENT_SUPPORT`: execution valid but one or more decision-critical source/support/inference/capacity conditions prevent a complete PASS/FAIL determination under the frozen rules.
- `INVALID_EXECUTION`: any identity/hash/read-budget/lookahead/accounting/candidate-count/persistence/exactly-once violation.

A PASS remains DEVELOPMENT-history evidence and is not independent OOS.

## Exactly-once and read budget

Stage 8 receives one and only one controlled attempt. A durable remote `RUN_ATTEMPT.marker` must exist before the first authorized historical object content read. Stage 6 must enumerate the exact authorized objects and per-object read budget. Each authorized object may be read at most once by the scientific attempt. Source-network fetches during Stage 8 are fixed at zero. Scientific engine call budget is exactly 1/1. Result persistence is create-only and ends with `RUN_ONCE.marker`.

After attempt-marker creation, same-ID rerun, retune, rescue, recomputation, history extension, candidate replacement, source replacement, venue replacement, threshold relaxation, stress deletion and additional scientific-engine calls are forbidden.

## Stage-3 completion condition

Stage 3 is complete only after this preregistration, exact source/capture identity boundary needed by the above contract, and mandatory `docs/CURRENT_STATE.md` handoff merge with every standing CI SUCCESS. Until merge, formal completion remains `2/10`; controlled reads remain `0`; attempt remains `0/1`; scientific engine calls remain `0`.
