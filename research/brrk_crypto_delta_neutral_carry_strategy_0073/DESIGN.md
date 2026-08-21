# BRRK-CRYPTO-DELTA-NEUTRAL-CARRY-STRATEGY-0073 — Stage 2 DESIGN

Status: `PROSPECTIVE DESIGN / ZERO CONTROLLED HISTORY READS / ATTEMPT 0/1`

Date: 2026-08-21

## Lifecycle anchors

- Program roadmap merge: `169d9adf6531dc099a43541df413fef079322adf`.
- 0072 immutable Stage-10 closeout: `e7571fd592c1a8074d487f27f8dbe9af6e33927f` = `INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED TO SAME-ID RERUN`.
- Prospective 0073 launch-gate amendment: `5b8153476aa63eb0c30d870a73e3bf14b4239ac8`.
- Guarded OWNER-FIRST tooling merge: `88d0daab5a3d35f215f331bba04424149900f570`.
- 0073 Stage-1 OWNER-FIRST merge: `dc287210212a827181501779482c976ac01995c8`.
- 0073 controlled scientific/history reads before and during this DESIGN: `0`.
- 0073 controlled attempt consumed: `0/1`.
- Production/signature/order authority: `false/false/false`.

This DESIGN is prospective. It does not inspect 0073 controlled history and does not use 0072 observed effects, p-values, support failure or any other 0072 result to select a structure, venue, threshold, horizon or parameter.

## Research question

Can a bounded, prospectively frozen set of delta-neutral BTC/ETH/SOL carry portfolios produce robust positive net economic value after complete two-leg implementation accounting, realistic and stressed costs, residual-directional-beta control, margin/liquidation constraints, venue stress, concentration and capacity tests?

0072 contributes **launch eligibility only** under the merged prospective governance amendment. It contributes no scientific PASS, no structure ranking and no parameter-selection evidence to 0073.

## Initial universe

The research universe is exactly:

- BTC
- ETH
- SOL

Each hedge must use the same underlying on both economic legs. Cross-asset hedging is out of scope for 0073. Asset eligibility, venue eligibility and exact instrument identities must be frozen point-in-time in Stage 3 before controlled history.

## Candidate-family ceiling

The candidate-family ceiling is exactly the three structure families already present in the pre-existing roadmap and Stage-1 owner record:

1. `LONG_SPOT_SHORT_PERPETUAL`
2. `LONG_SPOT_SHORT_DATED_FUTURE`
3. `PROSPECTIVELY_FIXED_CROSS_VENUE_HEDGE_WITH_CUSTODY_TRANSFER_MODEL`

The three families are a fixed research ceiling, not three opportunities to choose among many observed variants. Stage 3 must define exactly one candidate construction rule per family. Asset aggregation, venue selection, contract selection, hedge sizing, rebalance, roll and weighting rules must be deterministic and prospectively frozen so that the controlled attempt evaluates exactly three declared candidates.

If a family cannot satisfy prospectively frozen point-in-time data, custody, transfer, borrow, margin or instrument-support requirements, it must persist as a preregistered unavailable/insufficient-support candidate under the Stage-3 terminal rules. It may not be replaced by a newly invented family after history is observed.

## Delta-neutral semantics

Each candidate is one complete hedge portfolio, not two independently scored legs.

- The long and short legs reference the same underlying asset.
- Hedge sizing targets zero directional delta at the prospectively defined decision/rebalance boundary.
- A hard residual directional-beta/delta tolerance must be numerically frozen in Stage 3.
- Breach of the frozen tolerance is a candidate gate failure; it cannot be relabeled as market-neutral alpha.
- No unbounded leverage is permitted. Gross exposure, margin reserve and liquidation-buffer rules must be numerically frozen in Stage 3.
- Any cash, collateral or stablecoin balance must be included in complete portfolio economics and separately exposed to the preregistered collateral/stablecoin stress treatment.

## Ordered economic accounting

Stage 3 must convert this DESIGN into an exact temporal accounting contract that preserves the roadmap order:

1. freeze point-in-time venue, instrument, contract multiplier, maturity and margin metadata;
2. form the deterministic hedge ratio and delta-neutral target using information available at the decision boundary only;
3. apply venue-specific multiplier, collateral and margin rules;
4. apply fees, bid/ask spread and slippage to both legs;
5. apply perpetual funding receipts/payments only at the venue-defined funding timestamps and using information known by then;
6. apply dated-futures convergence and prospectively frozen roll mechanics without using future contract availability;
7. apply borrow, collateral yield/opportunity cost and hedge-rebalance cost in temporal order;
8. reserve margin and enforce a conservative prospectively frozen liquidation buffer;
9. compute net portfolio PnL, return, exposure and residual directional beta/delta;
10. reject candidate-period states that violate the frozen market-neutral tolerance according to the preregistered rule;
11. compute complete C1 realistic-cost and C2 stressed-cost economics plus cost break-even;
12. apply the frozen stress suite;
13. compute asset/venue concentration and remove-largest-venue sensitivity;
14. apply the frozen inference and trial-accounting rules;
15. classify the attempt only from the preregistered terminal gates.

No component may be omitted because it is unfavorable after observation.

## Required performance and economic outputs

Where mathematically defined, Stage 3 must freeze exact formulas for at least:

- CAGR / annualized return;
- annualized volatility;
- Sharpe;
- Sortino;
- maximum drawdown;
- Calmar;
- terminal wealth;
- turnover;
- gross carry;
- funding receipts/payments;
- basis convergence;
- roll contribution and roll cost;
- borrow cost;
- collateral yield/opportunity cost;
- fees, spread, slippage and total cost drag;
- cost break-even;
- gross and net exposure;
- residual directional beta/delta;
- margin reserve and liquidation buffer;
- asset and venue concentration;
- capacity proxies/limits;
- bootstrap or lower-confidence-bound outputs;
- DSR and trial count;
- PBO where mathematically supported.

No metric may be introduced post-result to rescue a candidate.

## Cost regimes

At least two nonzero economic regimes are mandatory:

- `C1_REALISTIC`
- `C2_STRESSED`

Stage 3 must freeze all numerical fees, spreads, slippage, borrow, funding treatment, roll costs, collateral costs/yields, transfer/custody frictions and rebalance-cost assumptions before controlled history. If an assumption cannot be supported prospectively, the affected candidate must fail closed or be unavailable under a preregistered rule rather than receive a favorable post-result estimate.

## Point-in-time and anti-lookahead contract

Stage 3 must freeze exact event time, exchange time, calculation time, as-of join, instrument-listing, maturity, funding, borrow and venue-availability semantics.

At minimum:

- no future venue or contract inclusion;
- no revised-history substitution unless explicitly classified and frozen prospectively;
- information observed at time `t` may influence only the first legally tradable state after `t` under the frozen execution convention;
- funding and settlement cash flows occur only at their actual prospectively defined timestamps;
- dated-future rolls cannot use contracts not yet eligible at the roll decision time;
- custody/withdrawal/transfer state for cross-venue structures must be modeled without hindsight.

## Mandatory stress suite

Stage 3 must freeze deterministic magnitudes and mechanics for all of the following roadmap stress families:

1. funding flip / adverse funding shock;
2. basis compression or adverse convergence;
3. volatility spike;
4. cross-venue spread/slippage blowout;
5. venue closure or withdrawal freeze / transfer impairment;
6. borrow and collateral deterioration;
7. collateral haircut;
8. stablecoin depeg where stablecoin collateral or cash is economically relevant;
9. margin stress and reduced liquidation buffer.

Stress parameters may not be weakened after result exposure.

## Concentration and capacity

Stage 3 must preregister asset concentration, venue concentration and remove-largest-venue sensitivity. It must also define capacity diagnostics appropriate to the selected spot/perpetual/futures instruments, using prospectively available liquidity/open-interest/depth or other point-in-time inputs where qualified.

No candidate may PASS solely because one asset, one venue or one short period supplies the result if the frozen concentration gates fail.

## Inference and multiplicity

The controlled family contains exactly three declared candidate constructions. Stage 3 must freeze:

- the exact trial count used by DSR;
- bootstrap/block-bootstrap method, block length or data-dependent rule frozen without result exposure, replicate count and seed;
- lower-confidence-bound or equivalent robust inference gate;
- PBO configuration where sample support makes it mathematically admissible, with a prospectively defined `NOT_EVALUATED` rule otherwise;
- complete-candidate persistence, including failed/unavailable candidates;
- any representative-candidate or Pareto/non-inferiority tie-break rule before history.

No trial may disappear from multiplicity accounting because it performs poorly.

## Terminal classification design

Stage 3 must freeze exact machine-checkable gates implementing these meanings:

- `PASS`: valid exactly-once execution and at least one prospectively frozen candidate passes every required net, C1/C2, residual-beta/delta, margin/liquidation, stress, concentration, capacity and statistical gate under the frozen representative-selection rule.
- `FAIL`: execution is valid and support is sufficient, but no declared candidate passes all required frozen gates.
- `INCONCLUSIVE`: only a prospectively enumerated insufficient-support or mathematically undefined inference condition prevents the required scientific/economic decision.
- `INVALID_EXECUTION`: identity/hash/read-count/lookahead/accounting/candidate-count/source/persistence/exactly-once drift invalidates the attempt.

A PASS is development-history research evidence only. It is not independent OOS and grants no production, signing or order-submission authority.

## Stage-3 freeze obligations

Before any 0073 controlled-history read, PREREGISTRATION must freeze at minimum:

- exact venue and instrument universe and point-in-time identities;
- exact candidate construction for all three families;
- same-underlying asset aggregation and portfolio-weighting rule;
- exact holding/rebalance/roll horizons;
- hedge-ratio calculation and rebalance convention;
- hard residual directional-beta/delta tolerance;
- gross exposure/leverage, margin reserve and liquidation-buffer limits;
- complete ordered PnL/accounting formulas;
- C1/C2 numerical costs and cost break-even formula;
- funding, borrow, collateral and settlement timing;
- cross-venue custody/transfer assumptions and fail-closed availability rule;
- all stress magnitudes/mechanics;
- concentration and capacity formulas/gates;
- bootstrap/LCB, DSR and PBO rules, seeds/replicates/trial count where applicable;
- candidate persistence and representative/tie-break rule;
- exact source/data identities, hashes or capture boundaries and controlled-read budgets;
- create-only result schema and marker-before-read / exactly-once execution contract;
- exact PASS/FAIL/INCONCLUSIVE/INVALID_EXECUTION gates.

## No-result-informed-rescue boundary

0072 observed H01-H06 effects, p-values, support counts and terminal INCONCLUSIVE classification may not be used to choose any 0073 structure, asset weighting, venue, horizon, threshold, cost assumption, beta tolerance, stress magnitude or statistical rule.

After 0073 Stage 8 attempt consumption, same-ID rerun, retune, rescue, recomputation, history extension, candidate substitution, venue substitution, threshold relaxation or post-result stress deletion are forbidden.

## Stage-2 completion condition

Stage 2 DESIGN is complete only after this file and the mandatory CURRENT_STATE handoff merge with all standing CI SUCCESS on the exact PR head. Until merge, formal completion remains `1/10`. Controlled scientific/history reads remain `0`, controlled attempt remains `0/1`, and scientific engine calls remain `0`.